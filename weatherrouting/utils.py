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
from typing import Tuple

import latlon

# from geographiclib.geodesic import Geodesic
# geod = Geodesic.WGS84

EARTH_RADIUS = 60.0 * 360 / (2 * math.pi)  # nm
NAUTICAL_MILE_IN_KM = 1.852
# Speed conversion m/s to kt
MS2KT = 1.94384


def ms_to_knots(v: float) -> float:
    return v * MS2KT


def cfbinomiale(n: int, i: int) -> float:
    # TODO: remove
    return math.factorial(n) / (math.factorial(n - i) * math.factorial(i))


def ortodromic2(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> Tuple[float, float]:
    # TODO: remove
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dp2 = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) * math.sin(dp2 / 2) + math.cos(p1) * math.cos(p2) * math.sin(
        dp2 / 2
    ) * math.sin(dp2 / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return (EARTH_RADIUS * c, a)


def ortodromic(
    lat_a: float, lon_a: float, lat_b: float, lon_b: float
) -> Tuple[float, float]:
    """Returns the ortodromic distance in km between A and B"""
    # g = geod.Inverse(lat_a, lon_a, lat_b, lon_b)
    # return (g['s12'] * 1e-3, math.radians (g['azi1']))

    p1 = latlon.LatLon(latlon.Latitude(lat_a), latlon.Longitude(lon_a))
    p2 = latlon.LatLon(latlon.Latitude(lat_b), latlon.Longitude(lon_b))
    return (p1.distance(p2), math.radians(p1.heading_initial(p2)))


def lossodromic(
    lat_a: float, lon_a: float, lat_b: float, lon_b: float
) -> Tuple[float, float]:
    """Returns the lossodromic distance in km between A and B"""
    # g = geod.Inverse(lat_a, lon_a, lat_b, lon_b)
    # return (g['s12'] * 1e-3, math.radians (g['azi1']))

    p1 = latlon.LatLon(latlon.Latitude(lat_a), latlon.Longitude(lon_a))
    p2 = latlon.LatLon(latlon.Latitude(lat_b), latlon.Longitude(lon_b))
    return (p1.distance(p2, ellipse="sphere"), math.radians(p1.heading_initial(p2)))


def km2nm(d: float) -> float:
    return d * 0.539957


def nm2km(d: float) -> float:
    return d / 0.539957


def point_distance(
    lat_a: float, lon_a: float, lat_b: float, lon_b: float, unit: str = "nm"
) -> float:
    """Returns the distance between two geo points"""
    p1 = latlon.LatLon(latlon.Latitude(lat_a), latlon.Longitude(lon_a))
    p2 = latlon.LatLon(latlon.Latitude(lat_b), latlon.Longitude(lon_b))
    d = p1.distance(p2)

    # d = ortodromic(lat_a, lon_a, lat_b, lon_b)[0]

    if unit == "nm":
        return km2nm(d)
    else:  # if unit == "km":
        return d


def routage_point_distance(
    lat_a: float, lon_a: float, distance: float, hdg: float, unit: str = "nm"
) -> Tuple[float, float]:
    """Returns the point from (lat_a, lon_a) to the given (distance, hdg)"""
    if unit == "nm":
        d = nm2km(distance)
    elif unit == "km":
        d = distance

    # g = geod.Direct(lat_a, lon_a, math.degrees(hdg), d * 1e3)
    # return (g['lat2'], g['lon2'])

    p = latlon.LatLon(latlon.Latitude(lat_a), latlon.Longitude(lon_a))
    of = p.offset(math.degrees(hdg), d).to_string("D")
    return (float(of[0]), float(of[1]))


def max_reach_distance(p, speed: float, dt: float = (1.0 / 60.0 * 60.0)) -> float:
    maxp = routage_point_distance(p[0], p[1], speed * dt, 1)
    return point_distance(p[0], p[1], maxp[0], maxp[1])


def reduce360(alfa: float) -> float:
    if math.isnan(alfa):
        return 0.0

    n_ = int(alfa * 0.5 / math.pi)
    n = math.copysign(n_, 1)
    if alfa > 2.0 * math.pi:
        alfa = alfa - n * 2.0 * math.pi
    if alfa < 0:
        alfa = (n + 1) * 2.0 * math.pi + alfa
    if alfa > 2.0 * math.pi or alfa < 0:
        return 0.0
    return alfa


def reduce180(alfa: float) -> float:
    if alfa > math.pi:
        alfa = alfa - 2 * math.pi
    if alfa < -math.pi:
        alfa = 2 * math.pi + alfa
    if alfa > math.pi or alfa < -math.pi:
        return 0.0
    return alfa


def path_as_geojson(path) -> object:
    feats = []
    route = []

    for order, wayp in enumerate(path):
        feat = {
            "type": "Feature",
            "id": order,
            "geometry": {
                "type": "Point",
                "coordinates": [wayp.pos[1], wayp.pos[0]],  # longitude, latitude
            },
            "properties": {
                "timestamp": str(wayp.time),
                "twd": math.degrees(wayp.twd),
                "tws": wayp.tws,
                "knots": wayp.speed,
                "heading": wayp.brg,
            },
        }
        feats.append(feat)
        route.append([wayp.pos[1], wayp.pos[0]])  # longitude, latitude

    feats.append(
        {
            "type": "Feature",
            "id": 999,
            "geometry": {"type": "LineString", "coordinates": route},
            "properties": {
                "start-timestamp": str(path[0].time),
                "end-timestamp": str(path[-1].time),
            },
        }
    )

    return {"type": "FeatureCollection", "features": feats}
