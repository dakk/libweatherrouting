# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from abc import ABC, abstractmethod

# For detail about GNU see <http://www.gnu.org/licenses/>.
from typing import Tuple


class Grib(ABC):
    """
    Grib class is an abstract class that should be implement for providing grib data to routers
    """

    @abstractmethod
    def get_wind_at(self, t: float, lat: float, lon: float) -> Tuple[float, float]:
        """
        Returns (twd: degree, tws: m/s) for the given point (lat, lon) at time t
        or None if running out of temporal/geographic grib scope
        """
        raise Exception("Not implemented")
