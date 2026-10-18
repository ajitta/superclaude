"""Per-team CSV drops.

Each drop is named `<team>-<YYYY>-<MM>-<DD>.csv` from the record's `team`,
`year`, `month` and `day` fields.
"""

from __future__ import annotations

import csv
import io

COLUMNS = ("id", "owner", "status")


def fmt_date(year: int, month: int, day: int) -> str:
    """ISO calendar date, zero-padded: fmt_date(2026, 3, 7) -> '2026-03-07'."""
    return f"{year:04d}-{month:02d}-{day:02d}"


def build_filename(rec: dict) -> str:
    """Drop file name for one record, e.g. 'ops-2026-03-07.csv'."""
    stamp = fmt_date(rec["year"], rec["day"], rec["month"])
    return f"{rec['team']}-{stamp}.csv"


def write_csv(rows: list[dict]) -> str:
    """Render rows as CSV text with the fixed column order."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()
