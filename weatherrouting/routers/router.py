# -*- coding: utf-8 -*-
# Copyright (C) 2017-2024 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
# Copyright (C) 2012 Riccardo Apolloni
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# For detail about GNU see <http://www.gnu.org/licenses/>.

import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .. import utils

# http://www.tecepe.com.br/nav/vrtool/routing.htm

# Le isocrone saranno un albero; deve essere semplice:
# - accedere alla lista delle isocrone dell'ultimo albero
# - aggiungere un layer per il nuovo t
# - fare pruning di foglie

# [[level1], [level2,level2], [level3,level3,level3,level3]]


class RouterParam:
    def __init__(
        self,
        code,
        name,
        ttype,
        tooltip,
        default,
        lower=None,
        upper=None,
        step=None,
        digits=None,
    ):
        self.code = code
        self.name = name
        self.ttype = ttype
        self.tooltip = tooltip
        self.default = default
        self.value = default

        self.lower = lower
        self.upper = upper
        self.digits = digits
        self.step = step


class RoutingNoWindException(Exception):
    pass


class RoutingResult:
    def __init__(self, time, path=[], isochrones=[], position=None, progress=0):
        self.time = time
        self.path = path
        self.isochrones = isochrones
        self.position = position
        self.progress = progress

    def __str__(self):
        sp = list(map(lambda x: x.toList(True), self.path))
        return f"RoutingResult(time={self.time}, path={sp}, progress={self.progress})"
        # position=%s, self.position,


@dataclass
class IsoPoint:
    pos: Tuple[float, float]
    prevIdx: int = -1
    time: Optional[float] = None
    twd: float = 0
    tws: float = 0
    speed: float = 0
    brg: float = 0
    nextWPDist: float = 0
    startWPLos: Tuple[float, float] = (0, 0)

    def toList(self, onlyPos=False):
        if onlyPos:
            return [self.pos[0], self.pos[1]]
        return [
            self.pos[0],
            self.pos[1],
            self.prevIdx,
            self.time,
            self.twd,
            self.tws,
            self.speed,
            self.brg,
            self.nextWPDist,
            self.startWPLos,
        ]

    @staticmethod
    def fromList(lst):
        return IsoPoint(
            (lst[0], lst[1]),
            lst[2],
            lst[3],
            lst[4],
            lst[5],
            lst[6],
            lst[7],
            lst[8],
            lst[9],
        )

    def lossodromic(self, to):
        return utils.lossodromic(self.pos[0], self.pos[1], to[0], to[1])

    def pointDistance(self, to):
        return utils.pointDistance(to[0], to[1], self.pos[0], self.pos[1])


class Router:
    PARAMS: Dict[str, Any] = {
        "subdiv": RouterParam(
            "subdiv",
            "Filtering subdivision of isopoint resolution",
            "int",
            "Set the filtering subdivision of isopoint resolution",
            default=1,
            lower=1,
            upper=30,
            step=1,
            digits=0,
        ),
        "concurrent": RouterParam(
            "concurrent",
            "Calculation concurrency",
            "bool",
            "Enable isochrones calculation concurrency",
            default=False,
            lower=False,
            upper=True,
        ),
    }

    def __init__(
        self,
        polar,
        grib,
        pointValidity=None,
        lineValidity=None,
        pointsValidity=None,
        linesValidity=None,
    ):
        self.polar = polar
        self.grib = grib
        self.pointValidity = pointValidity
        self.lineValidity = lineValidity
        self.pointsValidity = pointsValidity
        self.linesValidity = linesValidity

        if self.pointsValidity:
            self.pointValidity = None
        if self.linesValidity:
            self.lineValidity = None

    def setParamValue(self, code, value):
        if code not in self.PARAMS:
            raise Exception(f"Invalid param: {code}")
        self.PARAMS[code].value = value

    def getParamValue(self, code):
        if code not in self.PARAMS:
            raise Exception(f"Invalid param: {code}")
        return self.PARAMS[code].value

    def calculateShortestPathIsochrones(self, fixedSpeed, t, dt, isocrone, nextwp):
        """Calculates isochrones based on shortest path at fixed speed (motoring);
        the speed considers reductions / increases derived from leeway"""

        def pointF(p, tws, twa, dt, brg):
            # TODO: add current factor
            speed = fixedSpeed
            return (
                utils.routagePointDistance(
                    p[0], p[1], speed * dt * utils.NAUTICAL_MILE_IN_KM, brg
                ),
                speed,
            )

        return self._calculateIsochrones(
            t, dt, isocrone, nextwp, pointF, self.getParamValue("subdiv")
        )

    def calculateIsochrones(self, t, dt, isocrone, nextwp):
        """Calculate isochrones depending on routageSpeed from polar"""

        def pointF(p, tws, twa, dt, brg):
            speed = self.polar.getSpeed(tws, math.copysign(twa, 1))
            rpd = (
                utils.routagePointDistance(
                    p[0], p[1], speed * dt * utils.NAUTICAL_MILE_IN_KM, brg
                ),
                speed,
            )
            # print ('tws', tws, 'sog', speed, 'twa', math.degrees(twa), 'brg',
            # math.degrees(brg), 'rpd', rpd)tox

            return rpd

        return self._calculateIsochrones(
            t, dt, isocrone, nextwp, pointF, self.getParamValue("subdiv")
        )

    def _filterValidity(self, isonew, last):  # noqa: C901
        def validPoint(a):
            if not self.pointValidity(a.pos[0], a.pos[1]):
                return False
            return True

        def validLine(a):
            if not self.lineValidity(
                a.pos[0], a.pos[1], last[a.prevIdx].pos[0], last[a.prevIdx].pos[1]
            ):
                return False
            return True

        if self.pointValidity:
            isonew = list(filter(validPoint, isonew))
        if self.lineValidity:
            isonew = list(filter(validLine, isonew))
        if self.pointsValidity:
            pp = list(map(lambda a: a.pos, isonew))
            pv = self.pointsValidity(pp)

            for x in range(len(isonew)):
                if not pv[x]:
                    isonew[x] = None
            isonew = list(filter(lambda a: a is not None, isonew))
        if self.linesValidity:
            pp = list(
                map(
                    lambda a: [
                        a.pos[0],
                        a.pos[1],
                        last[a.prevIdx].pos[0],
                        last[a.prevIdx].pos[1],
                    ],
                    isonew,
                )
            )
            pv = self.linesValidity(pp)

            for x in range(len(isonew)):
                if not pv[x]:
                    isonew[x] = None
            isonew = list(filter(lambda a: a is not None, isonew))

        return isonew

    def _calculateIsochrones(  # noqa: C901
        self, t, dt, isocrone, nextwp, pointF, subdiv
    ):
        """Calcuates isochrones based on pointF next point calculation"""
        last = isocrone[-1]

        newisopoints = []

        def _calculateIsoPoints(i):
            last = isocrone[-1]
            cisos = []
            p = last[i]

            try:
                (twd, tws) = self.grib.get_wind_at(t, p.pos[0], p.pos[1])
            except Exception as e:
                raise RoutingNoWindException() from e

            for twa in range(-180, 180, 5):
                twa = math.radians(twa)
                twd = math.radians(twd)
                brg = utils.reduce360(twd + twa)

                # Calculate next point
                ptoiso, speed = pointF(p.pos, tws, twa, dt, brg)

                nextwpdist = utils.pointDistance(
                    ptoiso[0], ptoiso[1], nextwp[0], nextwp[1]
                )
                startwplos = isocrone[0][0].lossodromic((ptoiso[0], ptoiso[1]))

                if nextwpdist > p.nextWPDist:
                    continue

                # if self.pointValidity:
                # 	if not self.pointValidity (ptoiso[0], ptoiso[1]):
                # 		continue
                # if self.lineValidity:
                # 	if not self.lineValidity (ptoiso[0], ptoiso[1], p.pos[0], p.pos[1]):
                # 		continue

                cisos.append(
                    IsoPoint(
                        (ptoiso[0], ptoiso[1]),
                        i,
                        t,
                        twd,
                        tws,
                        speed,
                        math.degrees(brg),
                        nextwpdist,
                        startwplos,
                    )
                )

            return cisos

        # foreach point of the iso

        if self.getParamValue("concurrent"):
            executor = ThreadPoolExecutor()
            for x in executor.map(_calculateIsoPoints, range(0, len(last))):
                newisopoints.extend(x)

            executor.shutdown()
        else:
            for i in range(0, len(last)):
                newisopoints += _calculateIsoPoints(i)

        newisopoints = sorted(newisopoints, key=(lambda a: a.startWPLos[1]))

        # Remove slow isopoints inside
        bearing = {}
        for x in newisopoints:
            k = str(int(math.degrees(x.startWPLos[1]) / subdiv))

            if k in bearing:
                if x.nextWPDist < bearing[k].nextWPDist:
                    bearing[k] = x
            else:
                bearing[k] = x

        isonew = self._filterValidity(list(bearing.values()), last)
        isonew = sorted(isonew, key=(lambda a: a.startWPLos[1]))
        isocrone.append(isonew)

        # print(f"Before filtre: {len(newisopoints)}\tAfter filter: {len(isonew)}")

        return isocrone

    def calculateVMG(self, speed, angle, start, end) -> float:
        """Calculates the Velocity-Made-Good of a boat sailing from start to end
        at current speed / angle"""
        return speed * math.cos(angle)

    def route(self, lastlog, t, timedelta, start, end) -> RoutingResult:
        raise Exception("Not implemented")
