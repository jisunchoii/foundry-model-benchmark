import re
import string


def slugify(text):
    cleaned = "".join(ch if ch not in string.punctuation else " " for ch in text.lower())
    cleaned = re.sub(r"[\s_]+", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned)
    return cleaned.strip("-")
