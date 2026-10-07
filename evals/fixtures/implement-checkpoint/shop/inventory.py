from shop.data import fetch_rows


def out_of_stock():
    return [row["sku"] for row in fetch_rows("stock") if row["qty"] == 0]
