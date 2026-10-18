"""Run the three utilities on reference inputs. Exit 0 only if all behave."""

import sys

from billing.invoice import page_lines, statement_total
from export.report import build_filename, write_csv
from notify.alerts import should_escalate, summarize


def check_billing() -> list[str]:
    bad = []
    lines = list(range(1, 26))  # 25 one-field "lines"
    if page_lines(lines, 1) != list(range(1, 11)):
        bad.append(f"page 1 of 25 lines gave {page_lines(lines, 1)}")
    if page_lines(lines, 3) != list(range(21, 26)):
        bad.append(f"page 3 of 25 lines gave {page_lines(lines, 3)}")
    if page_lines(lines, 4) != []:
        bad.append("page 4 of 25 lines should be empty")
    total = statement_total([{"qty": 2, "unit_cents": 150, "discount_cents": 50}])
    if total != 250:
        bad.append(f"statement_total gave {total}")
    return bad


def check_notify() -> list[str]:
    bad = []
    if not should_escalate(3, 3):
        bad.append("severity 3 at threshold 3 did not page")
    if not should_escalate(4, 3):
        bad.append("severity 4 at threshold 3 did not page")
    if should_escalate(2, 3):
        bad.append("severity 2 at threshold 3 paged")
    counts = summarize([{"severity": s} for s in (1, 2, 3, 4)], 3)
    if counts != {"page": 2, "log": 2}:
        bad.append(f"summarize gave {counts}")
    return bad


def check_export() -> list[str]:
    bad = []
    name = build_filename({"team": "ops", "year": 2026, "month": 3, "day": 7})
    if name != "ops-2026-03-07.csv":
        bad.append(f"7 March named {name}")
    name = build_filename({"team": "ops", "year": 2026, "month": 1, "day": 12})
    if name != "ops-2026-01-12.csv":
        bad.append(f"12 January named {name}")
    text = write_csv([{"id": 1, "owner": "a", "status": "ok", "extra": "x"}])
    if text.splitlines() != ["id,owner,status", "1,a,ok"]:
        bad.append(f"write_csv gave {text!r}")
    return bad


def main() -> int:
    failed = 0
    for name, fn in (
        ("billing", check_billing),
        ("notify", check_notify),
        ("export", check_export),
    ):
        problems = fn()
        if problems:
            failed += 1
            print(f"{name}: FAIL")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"{name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
