"""Charge a cart line through Payrail at the built price."""

import json
from pathlib import Path

from vendor.payrail.client import Payrail

PRICES = Path(__file__).resolve().parents[1] / "out" / "prices.json"


def charge(sku: str, currency: str, card: str, client: Payrail) -> dict:
    prices = json.loads(PRICES.read_text(encoding="utf-8"))
    amount = prices[sku][currency]["amount_minor"]
    return client.create_charge(amount=amount, currency=currency, source=card)
