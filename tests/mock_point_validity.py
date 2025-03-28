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

# For detail about GNU see <http://www.gnu.org/licenses/>.
import weatherrouting


class MockPointValidity:
    def __init__(self, track, factor=4):
        self.mean_point = (
            (track[0][1] + track[1][1]) / 2,
            (track[0][0] + track[1][0]) / 2,
        )
        self.mean_island = (
            weatherrouting.utils.pointDistance(*(track[0] + track[1])) / factor
        )

    def point_validity(self, y, x):
        if (
            weatherrouting.utils.pointDistance(x, y, *(self.mean_point))
            < self.mean_island
        ):
            return False
        else:
            return True

    def line_validity(self, y1, x1, y2, x2):
        if (
            weatherrouting.utils.pointDistance(x1, y2, *(self.mean_point))
            < self.mean_island
        ):
            return False
        else:
            return True
