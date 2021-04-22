import unittest
import weatherrouting

class TestUtils(unittest.TestCase):
    def test_pointDistance(self):
        self.assertEqual(round(weatherrouting.utils.pointDistance(0.0, 0.0, 1/60, 0.0)), 1)