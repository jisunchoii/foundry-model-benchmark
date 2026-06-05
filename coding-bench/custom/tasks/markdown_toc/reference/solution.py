import re


def _anchor(title, seen):
    base = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    base = re.sub(r"[\s-]+", "-", base).strip("-")
    count = seen.get(base, 0)
    seen[base] = count + 1
    return base if count == 0 else f"{base}-{count}"


def build_toc(markdown):
    seen = {}
    lines = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        indent = "  " if level == 3 else ""
        lines.append(f"{indent}- [{title}](#{_anchor(title, seen)})")
    return "\n".join(lines)
