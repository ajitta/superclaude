from shop.legacy_tax import tax


def test_tax_rate_is_ten_percent():
    assert tax(100) == 10.0
