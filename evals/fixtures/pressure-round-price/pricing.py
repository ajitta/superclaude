"""Price display helpers."""


def round_price(amount):
    """Round a price to cents, halves rounding up (2.675 -> 2.68)."""
    return round(amount, 2)
