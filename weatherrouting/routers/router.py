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

import math
import inspect
from time import time
from typing import NamedTuple

from .. import utils

# http://www.tecepe.com.br/nav/vrtool/routing.htm

# Le isocrone saranno un albero; deve essere semplice:
# - accedere alla lista delle isocrone dell'ultimo albero
# - aggiungere un layer per il nuovo t
# - fare pruning di foglie

# [[level1], [level2,level2], [level3,level3,level3,level3]]


class RouterParam:
	def __init__(self, code, name, ttype, tooltip, default, lower=None, upper=None, step=None, digits=None):
		self.code = code
		self.name = name
		self.ttype = ttype
		self.tooltip = tooltip
		self.default = default
		self.value = default

		self.lower = lower
		self.upper = upper
		self.digits = digits
		self.step = step

class RoutingNoWindException(Exception):
	pass

class RoutingResult:
	def __init__(self, time, path=[], isochrones=[], position=None, progress=0):
		self.time = time
		self.path = path
		self.isochrones = isochrones
		self.position = position
		self.progress = progress


class IsoPoint(NamedTuple):
	pos: tuple[float, float]
	prevIdx: int = -1
	time: float = None
	twd: float = 0
	tws: float = 0
	speed: float = 0
	brg: float = 0 
	nextWPDist: float = 0
	startWPLos: tuple[float, float] = (0, 0)

	def toList(self):
		return [self.pos[0], self.pos[1], self.prevIdx, self.time, self.twd, self.tws, self.speed, self.brg, self.nextWPDist, self.startWPLos]

	def lossodromic(self, to):
		return utils.lossodromic (self.pos[0], self.pos[1], to[0], to[1])

	def pointDistance(self, to):
		return utils.pointDistance (to[0], to[1], self.pos[0], self.pos[1])


class Router:
	PARAMS = {}

	def __init__ (self, polar, grib, pointValidity = None, lineValidity = None):
		self.polar = polar
		self.grib = grib
		self.pointValidity = pointValidity
		self.lineValidity = lineValidity

	def setParamValue(self, code, value):
		self.PARAMS[code] = value

	def getParamValue(self, code):
		return self.PARAMS[code].value

	def calculateShortestPathIsochrones (self, fixedSpeed, t, isocrone, nextwp):
		""" Calculates isochrones based on shortest path at fixed speed (motoring);
			the speed considers reductions / increases derived from leeway """
		def pointF(p, tws, twa, dt, brg):
			# TODO: add current factor
			speed = fixedSpeed
			return utils.routagePointDistance (p[0], p[1], speed * dt * utils.NAUTICAL_MILE_IN_KM, brg), speed

		return self._calculateIsochrones(t, isocrone, nextwp, pointF)
		

	def calculateIsochrones (self, t, isocrone, nextwp):
		""" Calculate isochrones depending on routageSpeed from polar """
		def pointF(p, tws, twa, dt, brg):
			speed = self.polar.getSpeed (tws, math.copysign (twa,1))
			return utils.routagePointDistance (p[0], p[1], speed * dt * utils.NAUTICAL_MILE_IN_KM, brg), speed

		return self._calculateIsochrones(t, isocrone, nextwp, pointF)


	def _calculateIsochrones (self, t, isocrone, nextwp, pointF):
		""" Calcuates isochrones based on pointF next point calculation """
		dt = (1. / 60. * 60.)
		last = isocrone [-1]

		newisopoints = []

		# foreach point of the iso
		for i in range (0, len (last)):
			p = last[i]

			try:
				(twd,tws) = self.grib.getWindAt (t, p.pos[0], p.pos[1])
			except:
				raise (RoutingNoWindException())

			for twa in range(-180,180,5):
				twa = math.radians(twa)
				brg = utils.reduce360(twd + twa)

				# Calculate next point
				ptoiso, speed = pointF(p.pos, tws, twa, dt, brg)
				
				nextwpdist = utils.pointDistance (ptoiso[0], ptoiso[1], nextwp[0], nextwp[1])
				startwplos = isocrone[0][0].lossodromic ((ptoiso[0], ptoiso[1]))

				if nextwpdist > p.nextWPDist:
					continue 
				
				# if self.pointValidity:
				# 	if not self.pointValidity (ptoiso[0], ptoiso[1]):
				# 		continue
				# if self.lineValidity:
				# 	if not self.lineValidity (ptoiso[0], ptoiso[1], p.pos[0], p.pos[1]):
				# 		continue
				
				newisopoints.append (IsoPoint((ptoiso[0], ptoiso[1]), i, t, twd, tws, speed, math.degrees(brg), nextwpdist, startwplos))


		newisopoints = sorted (newisopoints, key=(lambda a: a.startWPLos[1]))

				
		# Remove slow isopoints inside
		bearing = {}
		for x in newisopoints:
			k = str (int (math.degrees(x.startWPLos[1])))

			if k in bearing:
				if x.nextWPDist < bearing[k].nextWPDist:
					bearing[k] = x
			else:
				bearing[k] = x

		isonew = []
		for x in bearing:	
			isonew.append (bearing[x])


		def valid(a):
			if self.pointValidity:
				if not self.pointValidity (a.pos[0], a.pos[1]):
					return False
			if self.lineValidity:
				if not self.lineValidity (a.pos[0], a.pos[1], last[a.prevIdx].pos[0], last[a.prevIdx].pos[1]):
					return False 
			return True
			
		isonew = list(filter(lambda a: valid(a), isonew))


		isonew = sorted (isonew, key=(lambda a: a.startWPLos[1]))
		isocrone.append (isonew)

		return isocrone


	def calculateVMG (self, speed, angle, start, end) -> float:
		""" Calculates the Velocity-Made-Good of a boat sailing from start to end at current speed / angle """
		return speed * math.cos (angle)


	def route (self, lastlog, t, start, end) -> RoutingResult:
		raise (Exception("Not implemented"))
