# -*- coding: utf-8 -*-
# Copyright (C) 2017-2021 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For detail about GNU see <http://www.gnu.org/licenses/>.
'''

import unittest
import weatherrouting
import datetime
import os
import json
import datetime
import hashlib

from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter
from .mock_grib import mock_grib
from .mock_point_validity import mock_point_validity

polar_obj = weatherrouting.Polar(os.path.join(os.path.dirname(__file__),'Bavaria38.pol'))

class TestRouting_lowWind_noIsland(unittest.TestCase):
    def setUp(self):
        grib = mock_grib(2,180,0.1)
        self.track = [(5,38),(5.2,38.2)]
        island_route = mock_point_validity(self.track)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            pointValidity = island_route.point_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0
        
        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 8)
        self.assertEqual(not res.path, False)

        path_to_end = res.path + [[*self.track[-1],'']]
        self.assertEqual( res.time, datetime.datetime.fromisoformat('2021-04-02 19:00:00'))

        gjs = json.dumps(weatherrouting.utils.pathAsGeojson(path_to_end))
        self.assertEqual(len(gjs), 2843)
        self.assertEqual(hashlib.sha256(gjs.encode()).hexdigest(), 'd11127f9228c704c47ccfdcac2cc1b8e97ecae5e6212637aa5e1ccc49c6e396a')


class TestRouting_lowWind_mockIsland_5(unittest.TestCase):
    def setUp(self):
        grib = mock_grib(2,180,0.1)
        self.track = [(5,38),(5.2,38.2)]
        island_route = mock_point_validity(self.track, factor=5)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            pointValidity = island_route.point_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0
        
        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)


class checkRoute_mediumWind_mockIsland_8(unittest.TestCase):
    def setUp(self):
        grib = mock_grib(5,45,0.5) 
        self.track = [(5,38),(4.6,37.6)]
        island_route = mock_point_validity(self.track, factor=8)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            lineValidity = island_route.line_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1
        
        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)

class checkRoute_highWind_mockIsland_3(unittest.TestCase):
    def setUp(self):
        grib = mock_grib(10,270,0.5) 
        self.track = [(5,38),(5.5,38.5)]
        island_route = mock_point_validity(self.track, factor=3)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            lineValidity = island_route.line_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1
        
        self.assertEqual(i, 6)
        self.assertEqual(not res.path, False)

class checkRoute_out_of_scope(unittest.TestCase):
    def setUp(self):
        grib = mock_grib(10,270,0.5,out_of_scope=datetime.datetime.fromisoformat('2021-04-02T15:00:00')) 
        self.track = [(5,38),(5.5,38.5)]
        island_route = mock_point_validity(self.track, factor=3)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            lineValidity = island_route.line_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1
        
        self.assertEqual(i, 4)
        self.assertEqual(not res.path, False)
        