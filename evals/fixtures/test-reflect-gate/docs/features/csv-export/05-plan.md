---
status: implementing
revised: 2026-10-21
---

# CSV export Implementation Plan

**Goal:** `shop.export.to_csv(rows)` returns order rows as CSV text with a header line and `\n` line endings.
**Architecture:** One new module on the standard library `csv` module; no change to existing modules.
**Tech Stack:** Python 3, pytest.

## Phase 1: CSV export (one commit)

### Task 1.1: to_csv

**Files:** Create: shop/export.py | Test: tests/test_export.py

- [x] Step 1: Write failing test: the header line is `id,customer,total` and there is one line per order
- [x] Step 2: Verify it fails
- [x] Step 3: Write minimal implementation
- [x] Step 4: Verify it passes: `python -m pytest -q tests/test_export.py`
- [x] Commit Phase 1: feat: CSV export

## Deviations

- Review finding F-1 (06-review.md) applied in the commit `fix: apply review F-1`.

## Risks

none

## Alternatives not taken

pandas: a new dependency for one function.

## Proof

`python -m pytest -q` → every test passes
