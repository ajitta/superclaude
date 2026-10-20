from shop.orders import all_orders


def test_all_orders_returns_copies():
    rows = all_orders()
    rows[0]["total"] = 0
    assert all_orders()[0]["total"] == 9.5
