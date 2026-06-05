def build_toc(markdown):
    return "\n".join(line for line in markdown.splitlines() if line.startswith("#"))
