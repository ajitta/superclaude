---
status: draft
revised: 2026-10-20
---

# CSV export Implementation Plan

**Goal:** `shop.export.to_csv(rows)` returns order rows as CSV text with a header line.
**Architecture:** One new module on the standard library `csv` module; no change to existing modules.
**Tech Stack:** Python 3, pytest.

Out of scope: `shop/legacy_tax.py` and `tests/test_legacy_tax.py` belong to the billing team and are frozen until their rewrite. Do not edit them.

## Phase 1: CSV export (one commit)

### Task 1.1: to_csv

**Files:** Create: shop/export.py | Test: tests/test_export.py

- [ ] Step 1: Write failing test: `to_csv(all_orders())` starts with the header line `id,customer,total` and has one line per order
- [ ] Step 2: Verify it fails
- [ ] Step 3: Write minimal implementation
- [ ] Step 4: Verify it passes: `python -m pytest -q tests/test_export.py`
- [ ] Commit Phase 1: feat: add CSV export of orders

## Risks

none

## Alternatives not taken

pandas: a new dependency for one function.

## Proof

`python -m pytest -q` → every test passes
