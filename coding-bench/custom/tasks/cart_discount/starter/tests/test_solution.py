import unittest

from solution import total_due


class CartDiscountTests(unittest.TestCase):
    def test_quantity_before_discount_and_tax(self):
        items = [{"price": 60, "quantity": 2}]
        self.assertEqual(total_due(items, 0.1), 118.8)

    def test_gift_cards_are_not_discounted(self):
        items = [
            {"price": 80, "quantity": 2, "category": "gift_card"},
            {"price": 30, "quantity": 2, "category": "book"},
        ]
        self.assertEqual(total_due(items, 0), 214.0)

    def test_no_discount_at_exact_threshold(self):
        items = [{"price": 50, "quantity": 2}]
        self.assertEqual(total_due(items, 0.05), 105.0)


if __name__ == "__main__":
    unittest.main()
