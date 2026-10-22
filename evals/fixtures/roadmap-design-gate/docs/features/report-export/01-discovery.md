---
status: draft
revised: 2026-10-20
---

# Report export: discovery spec

## Problem

`report.py` prints its summary to the terminal only. Finance wants the summary as a file they can attach to the monthly close.

## Requirements

1. `report.py --out <path>` writes the summary to `<path>` as CSV.
2. Without `--out`, behavior is unchanged.
3. An existing file at `<path>` is overwritten only with `--force`.

## Resolved Decisions

| # | Question | Decision | mode |
|---|---|---|---|
| Q1 | CSV or XLSX | CSV, no new dependency | confirmed |
| Q2 | Overwrite policy | refuse unless `--force` | delegated |

## Out of scope

Scheduling, email delivery.
