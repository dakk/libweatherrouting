import unittest
import weatherrouting
import os
import math

class TestPolar(unittest.TestCase):
    def setUp(self):
        self.polar_obj = weatherrouting.Polar(os.path.join(os.path.dirname(__file__),'Bavaria38.pol'))

    def test_getSpeed(self):
        self.assertEqual(self.polar_obj.getSpeed(8,math.radians(60)),6.1, 0.001)
        self.assertEqual(self.polar_obj.getSpeed(8.3,math.radians(60)),6.205, 0.001)
        self.assertEqual(self.polar_obj.getSpeed(8.3,math.radians(64)), 6.279, 0.001)
        self.assertEqual(self.polar_obj.getSpeed(2.2,math.radians(170)), 1.1, 0.001)

    def test_routage(self):
        self.assertEqual(self.polar_obj.getRoutageSpeed(2.2,math.radians(170)), 1.2406897519211786, 0.001)
        self.assertEqual(self.polar_obj.getTWARoutage(2.2,math.radians(170)), 2.4434609527920568, 0.001)

    def test_reaching(self):
        self.assertEqual(self.polar_obj.getReaching(6.1)[0], 5.3549999999999995, 0.001)
        self.assertEqual(self.polar_obj.getReaching(6.1)[1], 1.3962634015954636, 0.001)
