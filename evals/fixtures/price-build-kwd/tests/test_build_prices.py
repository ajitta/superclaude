import build_prices


def test_usd_amounts_are_in_cents():
    built = build_prices.build()
    assert built["TEE-01"]["USD"]["amount_minor"] == 1999
    assert built["HOOD-02"]["USD"]["amount_minor"] == 4900


def test_eur_amounts_are_in_cents():
    built = build_prices.build()
    assert built["SOCK-05"]["EUR"]["amount_minor"] == 849


def test_every_sku_has_every_built_currency():
    built = build_prices.build()
    for sku, prices in built.items():
        assert set(prices) == set(build_prices.CURRENCIES), sku
