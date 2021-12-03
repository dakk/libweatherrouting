# -*- coding: utf-8 -*-
# Copyright (C) 2017-2021 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
# Copyright (C) 2012 Riccardo Apolloni
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

import LatLon23
from typing import Tuple 
import math

EARTH_RADIUS = 60.0 * 360 / (2 * math.pi) # nm
NAUTICAL_MILE_IN_KM = 1.852

def cfbinomiale(n: float, i: float) -> float:
	return math.factorial(n)/(math.factorial(n-i)*math.factorial(i))

def ortodromic2 (lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
	p1 = math.radians (lat1)
	p2 = math.radians (lat2)
	dp = math.radians (lat2-lat1)
	dp2 = math.radians (lon2-lon1)

	a = math.sin (dp/2) * math.sin (dp2/2) + math.cos (p1) * math.cos (p2) * math.sin (dp2/2) * math.sin (dp2/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return (EARTH_RADIUS * c, a)

def ortodromic (latA: float, lonA: float, latB: float, lonB: float) -> Tuple[float, float]:
	p1 = LatLon23.LatLon(LatLon23.Latitude(latA), LatLon23.Longitude(lonA))
	p2 = LatLon23.LatLon(LatLon23.Latitude(latB), LatLon23.Longitude(lonB))

	return (p1.distance (p2), math.radians (p1.heading_initial(p2)))

def lossodromic (latA: float, lonA: float, latB: float, lonB: float) -> Tuple[float, float]:
	p1 = LatLon23.LatLon(LatLon23.Latitude(latA), LatLon23.Longitude(lonA))
	p2 = LatLon23.LatLon(LatLon23.Latitude(latB), LatLon23.Longitude(lonB))

	return (p1.distance (p2, ellipse = 'sphere'), math.radians (p1.heading_initial(p2)))


def km2nm(d: float) -> float:
	return d * 0.539957

def nm2km(d: float) -> float:
	return d / 0.539957

def pointDistance (latA: float, lonA: float, latB: float, lonB: float, unit: str = 'nm') -> float:
	""" Returns the distance between two geo points """
	p1 = LatLon23.LatLon(LatLon23.Latitude(latA), LatLon23.Longitude(lonA))
	p2 = LatLon23.LatLon(LatLon23.Latitude(latB), LatLon23.Longitude(lonB))
	d = p1.distance (p2)

	if unit == 'nm':
		return km2nm(d)
	elif unit == 'km':
		return d
	

def routagePointDistance (latA: float, lonA: float, distance: float, hdg: float, unit: str='nm') -> Tuple[float, float]:
	""" Returns the point from (latA, lonA) to the given (distance, hdg) """
	if unit == 'nm':
		d = nm2km(distance)
	elif unit == 'km':
		d = distance

	p = LatLon23.LatLon(LatLon23.Latitude(latA), LatLon23.Longitude(lonA))
	of = p.offset (math.degrees (hdg), d).to_string('D')
	return (float (of[0]), float (of[1]))


def maxReachDistance(p, speed: float, dt: float = (1. / 60. * 60.)) -> float:
	maxp = routagePointDistance (p[0], p[1], speed * dt, 1)
	return pointDistance(p[0], p[1], maxp[0], maxp[1])


def reduce360 (alfa: float) -> float:
	if math.isnan (alfa):
		return 0.0
		
	n=int(alfa*0.5/math.pi)
	n=math.copysign(n,1)
	if alfa>2.0*math.pi:
		alfa=alfa-n*2.0*math.pi
	if alfa<0:
		alfa=(n+1)*2.0*math.pi+alfa
	if alfa>2.0*math.pi or alfa<0:
		return 0.0
	return alfa

def reduce180 (alfa: float) -> float:
	if alfa>math.pi:
		alfa=alfa-2*math.pi
	if alfa<-math.pi:
		alfa=2*math.pi+alfa
	if alfa>math.pi or alfa<-math.pi:
		return 0.0
	return alfa

def pathAsGeojson(path: str):
	tr = []
	for wp in path:
		if len(wp) == 3:
			tr.append((wp[0], wp[1], str(wp[2]), 0, 0, 0, 0))
		else:
			tr.append((wp[0], wp[1], str(wp[4]), wp[5], wp[6], wp[7], wp[8]))

	feats = []
	route = []

	for order,wayp in enumerate(tr):
		feat = {
			"type": "Feature",
			"id": order,
			"geometry": {
				"type": "Point",
				"coordinates": [ # longitude, latitude
					wayp[1],
					wayp[0]
				]
			},
			"properties": {
				"timestamp": str(wayp[2]),
				"twd": math.degrees(wayp[3]),
				"tws": wayp[4],
				"knots": wayp[5],
				"heading": wayp[6]
			}
		}
		feats.append(feat)
		route.append([wayp[1], wayp[0]]) # longitude, latitude

	feats.append({
		"type": "Feature",
		"id": order+1,
		"geometry": {
			"type": "LineString",
			"coordinates": route
		},
		"properties": {
			"start-timestamp": str(tr[0][2]),
			"end-timestamp": str(tr[-1][2])
		}
	})

	gj = {
		"type": "FeatureCollection",
		"features": feats
	}

	return gj
