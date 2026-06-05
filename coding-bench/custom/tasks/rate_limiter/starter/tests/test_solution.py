import unittest

from solution import FixedWindowLimiter


class RateLimiterTests(unittest.TestCase):
    def test_per_key_limit(self):
        limiter = FixedWindowLimiter(limit=2, window_seconds=10)
        self.assertTrue(limiter.allow("a", 0))
        self.assertTrue(limiter.allow("a", 1))
        self.assertFalse(limiter.allow("a", 2))
        self.assertTrue(limiter.allow("b", 2))

    def test_window_reset(self):
        limiter = FixedWindowLimiter(limit=1, window_seconds=5)
        self.assertTrue(limiter.allow("a", 4.9))
        self.assertFalse(limiter.allow("a", 4.99))
        self.assertTrue(limiter.allow("a", 5.0))


if __name__ == "__main__":
    unittest.main()
