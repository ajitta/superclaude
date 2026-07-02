"""Pricing helpers."""


def apply_discount(price, pct):
    """Return the price after applying a pct discount."""
    return price * pct / 100


def add_tax(price, rate=0.1):
    return round(price * (1 + rate), 2)
