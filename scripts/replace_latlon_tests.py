# -*- coding: utf-8 -*-
# Copyright (C) 2017-2024 Davide Gessa
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

# import numpy
import math
import time

import latlon
from geographiclib.geodesic import Geodesic

# def get_bearing(lat1, long1, lat2, long2):
#     dLon = (long2 - long1)
#     x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
#     y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
#     brng = numpy.arctan2(x,y)
#     brng = numpy.degrees(brng)

#     return brng

# from turfpy import measurement
# from geojson import Point, Feature
# start = Feature(geometry=Point((-75.343, 39.984)))
# end = Feature(geometry=Point((-75.534, 39.123)))
# measurement.bearing(start,end)


def routagePointDistance(latA: float, lonA: float, distance: float, hdg: float):
    """Returns the point from (latA, lonA) to the given (distance, hdg)"""
    d = distance

    p = latlon.LatLon(latlon.Latitude(latA), latlon.Longitude(lonA))
    of = p.offset(math.degrees(hdg), d).to_string("D")
    return (float(of[0]), float(of[1]))


def ortodromic(latA: float, lonA: float, latB: float, lonB: float):
    p1 = latlon.LatLon(latlon.Latitude(latA), latlon.Longitude(lonA))
    p2 = latlon.LatLon(latlon.Latitude(latB), latlon.Longitude(lonB))

    return (p1.distance(p2), math.radians(p1.heading_initial(p2)))


def lossodromic(latA: float, lonA: float, latB: float, lonB: float):
    p1 = latlon.LatLon(latlon.Latitude(latA), latlon.Longitude(lonA))
    p2 = latlon.LatLon(latlon.Latitude(latB), latlon.Longitude(lonB))

    return (p1.distance(p2, ellipse="sphere"), math.radians(p1.heading_initial(p2)))


T = [-32.06, 115.74, 32.11195529143165, -63.95925278363717]

geod = Geodesic.WGS84

t = time.time()
g = geod.Inverse(T[0], T[1], T[2], T[3])
print(g, g["s12"] * 1e-3, math.radians(g["azi1"]))
print(time.time() - t, "\n\n")

t = time.time()
gg = lossodromic(T[0], T[1], T[2], T[3])
print(gg, math.degrees(gg[1]))
print(time.time() - t, "\n\n")


gg = ortodromic(T[0], T[1], T[2], T[3])
print(gg, math.degrees(gg[1]))


g = geod.Direct(-32.06, 115.74, 225, 20000e3)
print(g)

g = routagePointDistance(-32.06, 115.74, 20000, math.radians(225))
print(g)
