# -*- coding: utf-8 -*-
# Copyright (C) 2017-2021 Davide Gessa
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

from .routers import linearbestisorouter, RoutingResult

def listRoutingAlgorithms():
	""" Return a list of routing algorithms along with their names"""

	return [
		{
			'name': 'LinearBestIsoRouter',
			'class': linearbestisorouter.LinearBestIsoRouter
		}
	]

class Routing:
	"""
	"""

	def __init__ (self, algorithm, polar, track, grib, startDatetime, startPosition = None, pointValidity = None, lineValidity = None):
		"""
		Parameters
		----------
		algorithm : Router
			The routing algorithm class
		polar : Polar
			Polar object of the boat we want to route
		track : list
			A list of track points (lat, lon)
		grib : Grib
			Grib object that abstract our wind / wave / wathever queries
		startDateTime : datetime
			Start time
		startPosition : (float, float)
			Optional, default to None
			A pair containing initial position (or None if we want to start from the first track point)
		pointValidity : function(lat, lon)
			Optional, default to None
			A functions that receives lat and lon and returns True if the point is valid (ie: in the sea)
		lineValidity : function(lat1, lon1, lat2, lon2)
			Optional, default to None
			A functions that receives a vector defined by lat1, lon1, lat2, lon2 and returns True if the line is valid (ie: completely in the sea)
		"""

		self.end = False
		self.algorithm = algorithm(polar, grib, pointValidity, lineValidity)
		self.track = track
		self.steps = 0
		self.path = []
		self.time = startDatetime
		self.grib = grib
		self.log = []   

		if startPosition:
			self.wp = 0
			self.position = startPosition
		else:
			self.wp = 1
			self.position = self.track[0]


	def step (self) -> RoutingResult:
		""" Execute a single routing step """

		self.steps += 1
		
		if self.wp >= len (self.track):
			self.end = True
			res = self.log[-1]
			return self.log[-1]

		# Next waypoint
		nextwp = self.track[self.wp]

		if len (self.log) > 0:
			res = self.algorithm.route (self.log[-1], self.time, self.position, nextwp)
		else:
			res = self.algorithm.route (None, self.time, self.position, nextwp)


		#self.time += 0.2
		progress = len (self.log) * 5

		if len (res.path) != 0:
			self.position = res.position
			self.path = self.path + res.path
			self.wp += 1
			res.isochrones = []

		np = []
		ptime = None 
		for x in self.path:
			if len(x) > 3: nt = x[4]
			else: nt = x[2]

			if ptime:
				if ptime < nt:
					np.append(x)
					ptime = nt
			else:
				np.append(x)
				ptime = nt

		self.path = np
		self.time = res.time
		nlog = RoutingResult(progress=progress, time=res.time, path=self.path, isochrones=res.isochrones)

		self.log.append (nlog)
		return nlog
		