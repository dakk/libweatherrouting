import unittest
import weatherrouting

class TestUtils(unittest.TestCase):
    def test_pointDistance(self):
        self.assertEqual(weatherrouting.utils.pointDistance(0.0, 0.0, 0.1, 0.0), 6)