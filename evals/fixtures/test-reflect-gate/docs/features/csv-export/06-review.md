---
status: complete
revised: 2026-10-21
---

# CSV export branch review

## Round 1 — 2026-10-21

Reviewed: the branch at the commit `feat: CSV export; review round 1`.

- F-1 (Major): `to_csv` ends lines with `\r\n` (the `csv` module default); the plan's Goal asks for `\n`. `shop/export.py:9`.

Verdict: changes requested.
