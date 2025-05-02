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

import datetime

from .. import utils
from .router import IsoPoint, Router, RouterParam, RoutingResult


class LinearBestIsoRouter(Router):
    PARAMS = {
        "min_increase": RouterParam(
            "min_increase",
            "Minimum increase (nm)",
            "float",
            "Set the minimum value for selecting a new valid point",
            default=10.0,
            lower=1.0,
            upper=100.0,
            step=0.1,
            digits=1,
        )
    }

    def _route(self, lastlog, time, timedelta, start, end, iso_f):  # noqa: C901
        position = start
        path = []

        def generate_path(p):
            nonlocal path
            nonlocal isoc  # noqa: F824
            nonlocal position
            path.append(p)
            for iso in isoc[::-1][1::]:
                path.append(iso[path[-1].prev_idx])
            path = path[::-1]
            position = path[-1].pos

        if self.grib.get_wind_at(
            time + datetime.timedelta(hours=timedelta), end[0], end[1]
        ):
            if lastlog is not None and len(lastlog.isochrones) > 0:
                isoc = iso_f(
                    time + datetime.timedelta(hours=timedelta),
                    timedelta,
                    lastlog.isochrones,
                    end,
                )
            else:
                nwdist = utils.point_distance(end[0], end[1], start[0], start[1])
                isoc = iso_f(
                    time + datetime.timedelta(hours=timedelta),
                    timedelta,
                    [[IsoPoint((start[0], start[1]), time=time, next_wp_dist=nwdist)]],
                    end,
                )

            nearest_dist = self.get_param_value("min_increase")
            nearest_solution = None
            for p in isoc[-1]:
                distance_to_end_point = p.point_distance(end)
                if distance_to_end_point < self.get_param_value("min_increase"):
                    # (twd,tws) = self.grib.get_wind_at (time + datetime.timedelta(hours=timedelta),
                    # p.pos[0], p.pos[1])
                    max_reach_distance = utils.max_reach_distance(p.pos, p.speed)
                    if distance_to_end_point < abs(max_reach_distance * 1.1):
                        if (
                            not self.point_validity
                            or self.point_validity(end[0], end[1])
                        ) and (
                            not self.line_validity
                            or self.line_validity(end[0], end[1], p.pos[0], p.pos[1])
                        ):
                            if distance_to_end_point < nearest_dist:
                                nearest_dist = distance_to_end_point
                                nearest_solution = p
            if nearest_solution:
                generate_path(nearest_solution)

        # out of grib scope
        else:
            min_dist = 1000000
            isoc = lastlog.isochrones
            for p in isoc[-1]:
                check_dist = p.point_distance(end)
                if check_dist < min_dist:
                    min_dist = check_dist
                    min_p = p
            generate_path(min_p)

        return RoutingResult(
            time=time + datetime.timedelta(hours=timedelta),
            path=path,
            position=position,
            isochrones=isoc,
        )

    def route(self, lastlog, t, timedelta, start, end) -> RoutingResult:
        return self._route(lastlog, t, timedelta, start, end, self.calculate_isochrones)
