# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
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
from typing import Any, Dict, NamedTuple, Optional, Tuple

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


class RoutingNoWindError(Exception):
    pass


class RoutingResult:
    def __init__(self, time, path=[], isochrones=[], position=None, progress=0):
        self.time = time
        self.path = path
        self.isochrones = isochrones
        self.position = position
        self.progress = progress

    def __str__(self):
        sp = list(map(lambda x: x.to_list(True), self.path))
        return f"RoutingResult(time={self.time}, path={sp}, progress={self.progress})"
        # position=%s, self.position,


class IsoPoint(NamedTuple):
    pos: Tuple[float, float]
    prev_idx: int = -1
    time: Optional[float] = None
    twd: float = 0
    tws: float = 0
    speed: float = 0
    brg: float = 0
    next_wp_dist: float = 0
    start_wp_los: Tuple[float, float] = (0, 0)

    def to_list(self, only_pos=False):
        if only_pos:
            return [self.pos[0], self.pos[1]]
        return [
            self.pos[0],
            self.pos[1],
            self.prev_idx,
            self.time,
            self.twd,
            self.tws,
            self.speed,
            self.brg,
            self.next_wp_dist,
            self.start_wp_los,
        ]

    @staticmethod
    def from_list(lst):
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

    def point_distance(self, to):
        return utils.point_distance(to[0], to[1], self.pos[0], self.pos[1])


class Router:
    PARAMS: Dict[str, Any] = {}

    def __init__(
        self,
        polar,
        grib,
        point_validity=None,
        line_validity=None,
        points_validity=None,
        lines_validity=None,
    ):
        self.polar = polar
        self.grib = grib
        self.point_validity = point_validity
        self.line_validity = line_validity
        self.points_validity = points_validity
        self.lines_validity = lines_validity

        if self.points_validity:
            self.point_validity = None
        if self.lines_validity:
            self.line_validity = None

    def set_param_value(self, code, value):
        self.PARAMS[code] = value

    def get_param_value(self, code):
        return self.PARAMS[code].value

    def calculate_shortest_path_isochrones(self, fixed_speed, t, dt, isocrone, nextwp):
        """Calculates isochrones based on shortest path at fixed speed in knots (motoring);
        the speed considers reductions / increases derived from leeway"""

        def point_f(p, tws, twa, dt, brg):
            # TODO: add current factor
            speed = fixed_speed
            return (
                utils.routage_point_distance(
                    p[0], p[1], speed * dt * utils.NAUTICAL_MILE_IN_KM, brg
                ),
                speed,
            )

        return self._calculate_isochrones(t, dt, isocrone, nextwp, point_f)

    def calculate_isochrones(self, t, dt, isocrone, nextwp):
        """Calculate isochrones depending on routageSpeed from polar"""

        def point_f(p, tws, twa, dt, brg):
            speed = self.polar.get_speed(tws, math.copysign(twa, 1))
            # Issue 19 : for routage_point_distance defaut distance unit is nm
            #  speed*dt is nm  (don't convert in km)
            rpd = (
                utils.routage_point_distance(p[0], p[1], speed * dt, brg),
                speed,
            )
            # print ('tws', tws, 'sog', speed, 'twa', math.degrees(twa), 'brg',
            # math.degrees(brg), 'rpd', rpd)
            return rpd

        return self._calculate_isochrones(t, dt, isocrone, nextwp, point_f)

    def _filter_validity(self, isonew, last):  # noqa: C901
        def valid_point(a):
            if not self.point_validity(a.pos[0], a.pos[1]):
                return False
            return True

        def valid_line(a):
            if not self.line_validity(
                a.pos[0], a.pos[1], last[a.prev_idx].pos[0], last[a.prev_idx].pos[1]
            ):
                return False
            return True

        if self.point_validity:
            isonew = list(filter(valid_point, isonew))
        if self.line_validity:
            isonew = list(filter(valid_line, isonew))
        if self.points_validity:
            pp = list(map(lambda a: a.pos, isonew))
            pv = self.points_validity(pp)

            for x in range(len(isonew)):
                if not pv[x]:
                    isonew[x] = None
            isonew = list(filter(lambda a: a is not None, isonew))
        if self.lines_validity:
            pp = list(
                map(
                    lambda a: [
                        a.pos[0],
                        a.pos[1],
                        last[a.prev_idx].pos[0],
                        last[a.prev_idx].pos[1],
                    ],
                    isonew,
                )
            )
            pv = self.lines_validity(pp)

            for x in range(len(isonew)):
                if not pv[x]:
                    isonew[x] = None
            isonew = list(filter(lambda a: a is not None, isonew))

        return isonew

    def _calculate_isochrones_concurrent(self, t, dt, isocrone, nextwp, point_f):
        """Calcuates isochrones based on point_f next point calculation"""
        last = isocrone[-1]

        newisopoints = []

        # foreach point of the iso
        def cisopoints(i):
            cisos = []
            p = last[i]

            try:
                (twd, tws) = self.grib.get_wind_at(t, p.pos[0], p.pos[1])
            except Exception as e:
                raise RoutingNoWindError() from e

            twd = math.radians(twd)
            tws = utils.ms_to_knots(tws)

            for twa in range(-180, 180, 5):
                twa = math.radians(twa)
                brg = utils.reduce360(twd + twa)

                # Calculate next point
                ptoiso, speed = point_f(p.pos, tws, twa, dt, brg)

                nextwpdist = utils.point_distance(
                    ptoiso[0], ptoiso[1], nextwp[0], nextwp[1]
                )
                startwplos = isocrone[0][0].lossodromic((ptoiso[0], ptoiso[1]))

                if nextwpdist > p.next_wp_dist:
                    continue

                # if self.point_validity:
                # 	if not self.point_validity (ptoiso[0], ptoiso[1]):
                # 		continue
                # if self.line_validity:
                # 	if not self.line_validity (ptoiso[0], ptoiso[1], p.pos[0], p.pos[1]):
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

        executor = ThreadPoolExecutor()
        for x in executor.map(cisopoints, range(0, len(last))):
            newisopoints.extend(x)

        executor.shutdown()

        newisopoints = sorted(newisopoints, key=(lambda a: a.start_wp_los[1]))

        # Remove slow isopoints inside
        bearing = {}
        for x in newisopoints:
            k = str(int(math.degrees(x.start_wp_los[1])))

            if k in bearing:
                if x.next_wp_dist < bearing[k].next_wp_dist:
                    bearing[k] = x
            else:
                bearing[k] = x

        isonew = self._filter_validity(list(bearing.values()), last)
        isonew = sorted(isonew, key=(lambda a: a.start_wp_los[1]))
        isocrone.append(isonew)

        return isocrone

    def _calculate_isochrones(self, t, dt, isocrone, nextwp, point_f):
        """Calcuates isochrones based on point_f next point calculation"""
        last = isocrone[-1]

        newisopoints = []

        # foreach point of the iso
        for i in range(0, len(last)):
            p = last[i]

            try:
                (twd, tws) = self.grib.get_wind_at(t, p.pos[0], p.pos[1])
            except Exception as e:
                raise RoutingNoWindError() from e

            twd = math.radians(twd)
            tws = utils.ms_to_knots(tws)

            for twa in range(-180, 180, 5):
                twa = math.radians(twa)
                brg = utils.reduce360(twd + twa)

                # Calculate next point
                ptoiso, speed = point_f(p.pos, tws, twa, dt, brg)

                nextwpdist = utils.point_distance(
                    ptoiso[0], ptoiso[1], nextwp[0], nextwp[1]
                )
                startwplos = isocrone[0][0].lossodromic((ptoiso[0], ptoiso[1]))

                if nextwpdist > p.next_wp_dist:
                    continue

                # if self.point_validity:
                # 	if not self.point_validity (ptoiso[0], ptoiso[1]):
                # 		continue
                # if self.line_validity:
                # 	if not self.line_validity (ptoiso[0], ptoiso[1], p.pos[0], p.pos[1]):
                # 		continue

                newisopoints.append(
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

        newisopoints = sorted(newisopoints, key=(lambda a: a.start_wp_los[1]))

        # Remove slow isopoints inside
        bearing = {}
        for x in newisopoints:
            k = str(int(math.degrees(x.start_wp_los[1])))

            if k in bearing:
                if x.next_wp_dist < bearing[k].next_wp_dist:
                    bearing[k] = x
            else:
                bearing[k] = x

        isonew = self._filter_validity(list(bearing.values()), last)
        isonew = sorted(isonew, key=(lambda a: a.start_wp_los[1]))
        isocrone.append(isonew)

        return isocrone

    def calculate_vmg(self, speed, angle, start, end) -> float:
        """Calculates the Velocity-Made-Good of a boat sailing from start to end
        at current speed / angle"""
        return speed * math.cos(angle)

    def route(self, lastlog, t, timedelta, start, end) -> RoutingResult:
        raise Exception("Not implemented")
