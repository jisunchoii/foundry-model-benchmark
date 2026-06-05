import copy


def _parts(path):
    if not path.startswith("/"):
        raise ValueError("path must start with /")
    return [p.replace("~1", "/").replace("~0", "~") for p in path[1:].split("/") if p != ""]


def _resolve(root, path):
    parts = _parts(path)
    current = root
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current, parts[-1]


def apply_patch(document, operations):
    result = copy.deepcopy(document)
    for operation in operations:
        parent, key = _resolve(result, operation["path"])
        if operation["op"] == "remove":
            if isinstance(parent, list):
                parent.pop(int(key))
            else:
                del parent[key]
        elif operation["op"] in {"add", "replace"}:
            value = copy.deepcopy(operation.get("value"))
            if isinstance(parent, list):
                if key == "-":
                    parent.append(value)
                elif operation["op"] == "add":
                    parent.insert(int(key), value)
                else:
                    parent[int(key)] = value
            else:
                parent[key] = value
        else:
            raise ValueError(f"unsupported op: {operation['op']}")
    return result
