import unittest
import weatherrouting
import os

class TestPolar(unittest.TestCase):
    def setUp(self):
        self.polar_obj = weatherrouting.Polar(os.path.join(os.path.dirname(__file__),'Bavaria38.pol'))

    def test_pointDistance(self):
        self.assertEqual(self.polar_obj.getSpeed(8,60),6.48, 0.01)  
