from shop.data import fetch_rows


def summary():
    return {table: len(fetch_rows(table)) for table in ("orders", "stock")}
