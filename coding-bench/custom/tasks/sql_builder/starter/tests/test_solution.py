import unittest

from solution import build_select


class SqlBuilderTests(unittest.TestCase):
    def test_parameterized_query(self):
        sql, params = build_select("users", {"status": "active", "team_id": 7}, order_by="created_at", limit=10)
        self.assertEqual(sql, "SELECT * FROM users WHERE status = ? AND team_id = ? ORDER BY created_at LIMIT ?")
        self.assertEqual(params, ["active", 7, 10])

    def test_no_filters(self):
        self.assertEqual(build_select("events", {}, limit=5), ("SELECT * FROM events LIMIT ?", [5]))

    def test_rejects_bad_identifier(self):
        with self.assertRaises(ValueError):
            build_select("users; DROP TABLE users", {})


if __name__ == "__main__":
    unittest.main()
