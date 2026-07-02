from calc import apply_discount


def test_apply_discount():
    assert apply_discount(100, 10) == 90


def test_apply_discount_zero():
    assert apply_discount(50, 0) == 50
