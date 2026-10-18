"""Rebuild out/weekly.csv from data/orders.csv: one row per ISO week."""

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "orders.csv"
OUT = ROOT / "out" / "weekly.csv"
COUNTED = ("paid", "settled")  # card payments are `settled` since payments v2


def iso_week(ts: str) -> str:
    year, week, _ = date.fromisoformat(ts[:10]).isocalendar()
    return f"{year}-W{week:02d}"


def main() -> None:
    orders: dict[str, int] = defaultdict(int)
    revenue: dict[str, float] = defaultdict(float)
    with SRC.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"] not in COUNTED:
                continue
            week = iso_week(row["created_at"])
            orders[week] += 1
            revenue[week] += float(row["amount"])
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        out = csv.writer(f, lineterminator="\n")
        out.writerow(["week", "orders", "revenue"])
        for week in sorted(revenue):
            out.writerow([week, orders[week], round(revenue[week], 2)])
    print(f"wrote {len(revenue)} weeks to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
