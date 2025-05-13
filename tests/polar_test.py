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
import tempfile

import weatherrouting


class TestPolar(unittest.TestCase):
    def setUp(self):
        self.polar_obj = weatherrouting.Polar(
            os.path.join(os.path.dirname(__file__), "data/bavaria38.pol")
        )
        self.valid_polar_file_path = os.path.join(os.path.dirname(__file__), "data/bavaria38.pol")
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            self.valid_polar_content_lines = f.readlines()

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
    
    # --- Tests for Polar.validate_polar_file ---
    def _create_temp_file_with_content(self, content: str) -> str:
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pol", encoding="utf-8")
        temp_file.write(content)
        temp_file.close()
        self.addCleanup(os.remove, temp_file.name)
        return temp_file.name

    def test_validate_polar_file_succeeds_on_valid_file(self):
        # This should not raise an error for a known valid file
        try:
            weatherrouting.Polar.validate_polar_file(self.valid_polar_file_path)
        except weatherrouting.PolarError as e:
            self.fail(f"validate_polar_file raised PolarError unexpectedly for a valid file: {e}")

    def test_validate_polar_file_empty_file(self):
        temp_file_path = self._create_temp_file_with_content("")
        with self.assertRaisesRegex(weatherrouting.PolarError, "EMPTY_FILE"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_wind_numeric(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('30','a')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "WIND_SPEED_NOT_NUMERIC"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_wind_incresing(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('50','100')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "WIND_SPEEDS_NOT_INCREASING"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_empty_line(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('\n','\n\n')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "EMPTY_LINE"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_column_count_mismatch(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('60','60 70')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "COLUMN_COUNT_MISMATCH"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_twa_out_of_range(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('100','181')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "TWA_OUT_OF_RANGE"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_twa_not_numeric(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('100','a')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "TWA_NOT_NUMERIC"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)


    def test_validate_empty_value(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('7.7','-')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "EMPTY_VALUE"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)

    def test_validate_negative_speed(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('7.7','-1')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "NEGATIVE_SPEED"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)
    
    def test_validate_speed_not_numeric(self):
        with open(self.valid_polar_file_path, "r", encoding="utf-8") as f:
            valid_content = f.read()
        corrupt_content = valid_content.replace('7.7','a')
        temp_file_path = self._create_temp_file_with_content(corrupt_content)
        with self.assertRaisesRegex(weatherrouting.PolarError, "SPEED_NOT_NUMERIC"):
            weatherrouting.Polar.validate_polar_file(temp_file_path)


            
