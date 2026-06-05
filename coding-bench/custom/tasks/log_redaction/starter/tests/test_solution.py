import unittest

from solution import redact


class RedactionTests(unittest.TestCase):
    def test_masks_common_secret_shapes(self):
        text = "user ada@example.com token Bearer abc.def.ghi key sk-1234567890abcdef card 4242424242424242"
        redacted = redact(text)
        self.assertNotIn("ada@example.com", redacted)
        self.assertNotIn("abc.def.ghi", redacted)
        self.assertNotIn("sk-1234567890abcdef", redacted)
        self.assertNotIn("4242424242424242", redacted)
        self.assertIn("a***@example.com", redacted)
        self.assertIn("Bearer [REDACTED]", redacted)
        self.assertIn("sk-...cdef", redacted)
        self.assertIn("4242********4242", redacted)


if __name__ == "__main__":
    unittest.main()
