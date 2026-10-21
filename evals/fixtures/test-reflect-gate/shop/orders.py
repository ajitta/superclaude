ORDERS = [
    {"id": 1, "customer": "acme", "total": 9.5},
    {"id": 2, "customer": "globex", "total": 20.0},
]


def all_orders():
    return [dict(row) for row in ORDERS]
