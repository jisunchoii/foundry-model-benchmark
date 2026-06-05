import re


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value):
    if not IDENTIFIER.match(value):
        raise ValueError(f"invalid identifier: {value}")
    return value


def build_select(table, filters, order_by=None, limit=None):
    sql = f"SELECT * FROM {_identifier(table)}"
    params = []
    if filters:
        clauses = []
        for key, value in filters.items():
            clauses.append(f"{_identifier(key)} = ?")
            params.append(value)
        sql += " WHERE " + " AND ".join(clauses)
    if order_by is not None:
        sql += f" ORDER BY {_identifier(order_by)}"
    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a non-negative integer")
        sql += " LIMIT ?"
        params.append(limit)
    return sql, params
