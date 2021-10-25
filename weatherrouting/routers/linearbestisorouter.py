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

import datetime
from .. import utils
from .router import *

class LinearBestIsoRouter (Router):
	PARAMS = {
		'minIncrease': RouterParam('minIncrease', 'Minimum increase (nm)', 'float', 'Set the minimum value for selecting a new valid point', default=10.0, lower=1.0, upper=100.0, step=0.1, digits=1)
	}


	def _route (self, lastlog, time, start, end, isoF):
		position = start
		path = []

		def generate_path(p):
			nonlocal path
			nonlocal isoc
			nonlocal position
			path.append (p)
			for iso in isoc[::-1][1::]:
				path.append (iso[path[-1][2]])
			path = path[::-1]
			position = path[-1]
		
		if self.grib.getWindAt (time + datetime.timedelta(hours=1), end[0],end[1]):
			if lastlog != None and len (lastlog.isochrones) > 0:
				isoc = isoF(time + datetime.timedelta(hours=1), lastlog.isochrones, end)
			else:
				isoc = isoF(time + datetime.timedelta(hours=1), [[(start[0], start[1], time)]], end)

			nearest_dist = self.getParamValue('minIncrease')
			nearest_solution = None
			for p in isoc[-1]:
				distance_to_end_point = utils.pointDistance (end[0],end[1], p[0], p[1])
				if distance_to_end_point < self.getParamValue('minIncrease'):
					(twd,tws) = self.grib.getWindAt (time + datetime.timedelta(hours=1), p[0], p[1])
					maxReachDistance = utils.maxReachDistance(p, p[6])
					if utils.pointDistance (end[0],end[1], p[0], p[1]) < abs(maxReachDistance*1.1):
						if (not self.pointValidity or self.pointValidity(end[0],end[1])) and (not self.lineValidity or self.lineValidity(end[0],end[1], p[0], p[1])):
							if distance_to_end_point < nearest_dist:
								nearest_dist = distance_to_end_point
								nearest_solution = p
			if nearest_solution:
				generate_path(nearest_solution)

		# out of grib scope
		else: 
			minDist = 1000000
			isoc = lastlog.isochrones
			for p in isoc[-1]:
				checkDist = utils.pointDistance (end[0],end[1], p[0], p[1]) 
				if checkDist < minDist:
					minDist = checkDist
					minP = p
			generate_path(minP)

		return RoutingResult(time=time + datetime.timedelta(hours=1), path=path, position=position, isochrones=isoc)


	def route (self, lastlog, time, start, end) -> RoutingResult:
		return self._route(lastlog, time, start, end, self.calculateIsochrones)
