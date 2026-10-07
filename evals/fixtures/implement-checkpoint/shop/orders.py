from shop.data import fetch_rows


def order_ids():
    return [row["id"] for row in fetch_rows("orders")]
