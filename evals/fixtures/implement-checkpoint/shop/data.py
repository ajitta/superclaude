ROWS = {
    "orders": [{"id": 1, "total": 30}, {"id": 2, "total": 12}],
    "stock": [{"sku": "A1", "qty": 4}, {"sku": "B2", "qty": 0}],
}


def fetch_rows(table):
    return list(ROWS.get(table, []))
