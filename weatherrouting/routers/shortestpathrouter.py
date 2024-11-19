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
from .linearbestisorouter import LinearBestIsoRouter, RouterParam, RoutingResult


class ShortestPathRouter(LinearBestIsoRouter):
    PARAMS = LinearBestIsoRouter.PARAMS | {
        "fixedSpeed": RouterParam(
            "fixedSpeed",
            "Fixed speed (kn)",
            "float",
            "Set the fixed speed",
            default=5.0,
            lower=1.0,
            upper=60.0,
            step=0.1,
            digits=1,
        ),
    }

    def route(self, lastlog, t, start, end) -> RoutingResult:
        return self._route(
            lastlog,
            t,
            start,
            end,
            lambda t, isoc, end: self.calculateShortestPathIsochrones(
                self.getParamValue("fixedSpeed"), t, isoc, end
            ),
        )
