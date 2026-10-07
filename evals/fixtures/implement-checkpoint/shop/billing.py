from shop.data import fetch_rows


def revenue():
    return sum(row["total"] for row in fetch_rows("orders"))
