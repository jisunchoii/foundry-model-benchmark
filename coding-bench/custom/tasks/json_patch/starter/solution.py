def apply_patch(document, operations):
    for operation in operations:
        document[operation["path"]] = operation.get("value")
    return document
