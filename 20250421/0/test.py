from kv import sqroots
import unittest

class Test(unittest.TestCase):
    
    def test_0_zero_x(self):
        self.assertEqual(sqroots('1 2 3'), None)

    def test_1_one_x(self):
        self.assertEqual(sqroots('2 4 2'), -1.0)

    def test_2_two_x(self):
        self.assertEqual(sqroots('1 -3 2'), (2.0, 1.0))

    def test_3_errors(self):
        with self.assertRaises(ValueError):
            sqroots('1 2')