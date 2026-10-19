"""Payout helpers."""


def split_cents(total, n):
    """Split total cents into n shares (see README for the rules)."""
    share = total // n
    return [share] * n
