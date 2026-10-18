"""Build out/prices.json from the price lists in prices/<currency>.csv."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CURRENCIES = ("USD", "EUR", "GBP")


def load(currency: str) -> dict[str, str]:
    path = ROOT / "prices" / f"{currency.lower()}.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return {row["sku"]: row["price"] for row in csv.DictReader(f)}


def build() -> dict:
    out: dict = {}
    for currency in CURRENCIES:
        for sku, price in load(currency).items():
            out.setdefault(sku, {})[currency] = {"amount_minor": round(float(price) * 100)}
    return out


def main() -> None:
    target = ROOT / "out" / "prices.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
