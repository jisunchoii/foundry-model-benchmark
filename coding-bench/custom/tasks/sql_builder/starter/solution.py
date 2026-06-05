def build_select(table, filters, order_by=None, limit=None):
    sql = "SELECT * FROM " + table
    if filters:
        sql += " WHERE " + " AND ".join(f"{key} = '{value}'" for key, value in filters.items())
    return sql, []
