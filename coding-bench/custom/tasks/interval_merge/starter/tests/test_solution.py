import unittest

from solution import merge_intervals


class IntervalMergeTests(unittest.TestCase):
    def test_merges_overlapping_and_touching(self):
        self.assertEqual(merge_intervals([(5, 8), (1, 3), (3, 4), (10, 12), (11, 20)]), [(1, 4), (5, 8), (10, 20)])

    def test_empty(self):
        self.assertEqual(merge_intervals([]), [])

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            merge_intervals([(2, 1)])


if __name__ == "__main__":
    unittest.main()
