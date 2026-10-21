from shop.export import to_csv
from shop.orders import all_orders


def test_header():
    assert to_csv(all_orders()).splitlines()[0] == "id,customer,total"


def test_one_line_per_order():
    assert len(to_csv(all_orders()).splitlines()) == 1 + len(all_orders())
