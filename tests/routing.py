import unittest
import weatherrouting
import random
import datetime
import os
import math

from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter

class mockGrib:
    def __init__(self,starttws,starttwd, fuzziness ):
        self.starttws = starttws
        self.starttwd = starttwd
        self.fuzziness = fuzziness
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
        return ( math.radians(self.twd_var(t)), self.tws_var(t), )

def mock_point_validity(y,x):
    return True

polar_obj = weatherrouting.Polar(os.path.join(os.path.dirname(__file__),'Bavaria38.pol'))

track = [(5,38),(5.2,38.2)]

class TestRouting(unittest.TestCase):

    def setUp(self):
        grib = mockGrib(2,180,0.1)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            track,
            grib,
            mock_point_validity,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00')
        )
        
    def test_step(self):
        res = None 
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            # print ("isocrones",res.isochrones)
            # print("path",res.path)
            # print("position",res.position)
            i += 1
        
        self.assertEqual(i, 4)
        self.assertEqual(not res.path, False)
