import unittest
from helpertools import elegant_time


class MyTestCase(unittest.TestCase):
    def test1(self):
        self.assertEqual(elegant_time(2.5), "2:30")  # add assertion here

    def test2(self):
        self.assertEqual(elegant_time(3.0), "3")

    def test3(self):
        self.assertEqual(elegant_time(3), "3")


if __name__ == '__main__':
    unittest.main()
