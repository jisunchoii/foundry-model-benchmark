import unittest

from solution import slugify


class SlugifyTests(unittest.TestCase):
    def test_punctuation_and_spaces(self):
        self.assertEqual(slugify(" Hello,   World!! "), "hello-world")

    def test_underscores_and_repeated_separators(self):
        self.assertEqual(slugify("API__Gateway   v2"), "api-gateway-v2")

    def test_empty_result(self):
        self.assertEqual(slugify(" !? "), "")


if __name__ == "__main__":
    unittest.main()
