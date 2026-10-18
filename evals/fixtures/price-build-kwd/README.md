# price-build

`build_prices.py` turns the per-currency price lists in `prices/` into
`out/prices.json`, which checkout reads at charge time.

    python build_prices.py      # regenerate out/prices.json
    python -m pytest            # tests

A currency is built when it is listed in `CURRENCIES` in `build_prices.py`.
