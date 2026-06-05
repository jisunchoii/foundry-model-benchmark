import unittest

from solution import apply_patch


class JsonPatchTests(unittest.TestCase):
    def test_add_replace_remove_nested_values(self):
        doc = {"users": [{"name": "Ada", "roles": ["dev"]}], "active": True}
        patched = apply_patch(
            doc,
            [
                {"op": "add", "path": "/users/0/roles/1", "value": "admin"},
                {"op": "replace", "path": "/users/0/name", "value": "Ada Lovelace"},
                {"op": "remove", "path": "/active"},
            ],
        )
        self.assertEqual(patched, {"users": [{"name": "Ada Lovelace", "roles": ["dev", "admin"]}]})
        self.assertEqual(doc["users"][0]["name"], "Ada")

    def test_dash_appends_to_list(self):
        self.assertEqual(apply_patch({"a": [1]}, [{"op": "add", "path": "/a/-", "value": 2}]), {"a": [1, 2]})


if __name__ == "__main__":
    unittest.main()
