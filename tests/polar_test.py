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
import math
import os
import unittest

import weatherrouting


class TestPolar(unittest.TestCase):
    def setUp(self):
        self.polar_obj = weatherrouting.Polar(
            os.path.join(os.path.dirname(__file__), "data/bavaria38.pol")
        )

    def test_to_string(self):
        f = open(os.path.join(os.path.dirname(__file__), "data/bavaria38.pol"), "r")
        d = f.read()
        f.close()
        self.assertEqual(self.polar_obj.to_string(), d)

    def test_get_speed(self):
        self.assertAlmostEqual(
            self.polar_obj.get_speed(8, math.radians(60)), 6.1, delta=0.001
        )
        self.assertAlmostEqual(
            self.polar_obj.get_speed(8.3, math.radians(60)), 6.205, delta=0.001
        )
        self.assertAlmostEqual(
            self.polar_obj.get_speed(8.3, math.radians(64)), 6.279, delta=0.001
        )
        self.assertAlmostEqual(
            self.polar_obj.get_speed(2.2, math.radians(170)), 1.1, delta=0.001
        )

    def test_routage(self):
        self.assertAlmostEqual(
            self.polar_obj.get_routage_speed(2.2, math.radians(170)),
            1.2406897519211786,
            delta=0.001,
        )
        self.assertAlmostEqual(
            self.polar_obj.get_twa_routage(2.2, math.radians(170)),
            2.4434609527920568,
            delta=0.001,
        )

    def test_reaching(self):
        self.assertAlmostEqual(
            self.polar_obj.get_reaching(6.1)[0], 5.3549999999999995, delta=0.001
        )
        self.assertAlmostEqual(
            self.polar_obj.get_reaching(6.1)[1], 1.3962634015954636, delta=0.001
        )
