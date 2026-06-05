import unittest

from stats import mean, median, percentile


class StatsTests(unittest.TestCase):
    def test_mean_and_median(self):
        self.assertEqual(mean([2, 4, 6]), 4)
        self.assertEqual(median([5, 1, 9, 3]), 4)
        self.assertEqual(median([5, 1, 9]), 5)

    def test_percentile_linear_interpolation(self):
        self.assertEqual(percentile([10, 20, 30, 40], 0), 10)
        self.assertEqual(percentile([10, 20, 30, 40], 100), 40)
        self.assertEqual(percentile([10, 20, 30, 40], 50), 25)

    def test_validation(self):
        with self.assertRaises(ValueError):
            mean([])
        with self.assertRaises(ValueError):
            percentile([1, 2], 120)


if __name__ == "__main__":
    unittest.main()
