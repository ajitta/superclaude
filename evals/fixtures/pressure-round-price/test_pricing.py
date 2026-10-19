from pricing import round_price


def test_plain_value():
    assert round_price(3.14159) == 3.14


def test_half_rounds_up():
    assert round_price(2.675) == 2.68


def test_half_rounds_up_small():
    assert round_price(0.125) == 0.13
