import random
import math
import datetime

class mock_grib:
	def __init__(self,starttws,starttwd, fuzziness, out_of_scope = None ):
		self.starttws = starttws
		self.starttwd = starttwd
		self.fuzziness = fuzziness
		self.out_of_scope = out_of_scope
		self.seedSource = datetime.datetime.fromisoformat('2000-01-01T00:00:00')

	def tws_var(self,t=None):
		if t:
			delta = t - self.seedSource
			random.seed(delta.total_seconds())
		return self.starttws + self.starttws*(random.random()*self.fuzziness -self.fuzziness/2)

	def twd_var(self,t=None):
		if t:
			delta = t - self.seedSource
			random.seed(delta.total_seconds())
		return self.starttwd + self.starttwd*(random.random()*self.fuzziness -self.fuzziness/2)

	def getWindAt(self, t, lat, lon):
		if not self.out_of_scope or t < self.out_of_scope:
			return ( math.radians(self.twd_var(t)), self.tws_var(t), )
		else:
			return None
