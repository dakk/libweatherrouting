# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
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
import unittest

import weatherrouting


class TestUtils(unittest.TestCase):
    def test_point_distance(self):
        self.assertEqual(
            round(weatherrouting.utils.point_distance(0.0, 0.0, 1 / 60, 0.0)), 1
        )

    def test_max_dist_reaching(self):
        p1 = (5, 38)
        maxd = weatherrouting.utils.max_reach_distance(p1, 5)
        self.assertAlmostEqual(maxd, 5.000000000000199, delta=0.001)
