# Amounts

Every amount field is an integer in the minor unit of the charge currency.
Payrail charges the integer as sent; it does not rescale amounts.

| exponent | currencies |
|---|---|
| 0 | JPY, KRW, VND, CLP, ISK |
| 2 | USD, EUR, GBP, CAD, AUD, CHF, SEK, and most others |
| 3 | KWD, BHD, JOD, OMR, TND |

The amount is the price × 10^exponent: 10.00 USD is `1000`, 10.000 KWD is `10000`.
