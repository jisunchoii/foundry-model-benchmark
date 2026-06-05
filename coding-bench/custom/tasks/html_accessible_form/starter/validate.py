from html.parser import HTMLParser
from pathlib import Path


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = {}
        self.inputs = {}
        self.buttons = []
        self.external = []
        self._label_for = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "label":
            self._label_for = attrs.get("for")
        if tag == "input":
            self.inputs[attrs.get("id")] = attrs
        if tag == "button":
            self.buttons.append(attrs)
        if tag in {"script", "link"}:
            src = attrs.get("src") or attrs.get("href")
            if src and (src.startswith("http") or src.startswith("//")):
                self.external.append(src)

    def handle_data(self, data):
        if self._label_for and data.strip():
            self.labels[self._label_for] = data.strip()

    def handle_endtag(self, tag):
        if tag == "label":
            self._label_for = None


parser = Parser()
parser.feed(Path("index.html").read_text(encoding="utf-8"))
assert not parser.external, "external assets are not allowed"
assert any(attrs.get("type") == "submit" for attrs in parser.buttons), "submit button missing"
for input_id, expected_type, autocomplete in [
    ("email", "email", "email"),
    ("password", "password", "current-password"),
]:
    attrs = parser.inputs.get(input_id)
    assert attrs, f"missing input id {input_id}"
    assert attrs.get("type") == expected_type, f"wrong type for {input_id}"
    assert "required" in attrs, f"{input_id} must be required"
    assert attrs.get("autocomplete") == autocomplete, f"wrong autocomplete for {input_id}"
    assert input_id in parser.labels, f"label for {input_id} missing"
