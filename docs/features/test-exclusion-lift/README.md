---
feature: test-exclusion-lift
phase: closed
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Lift the tests/unit/scripts exclusion; Dependabot

Decide on evidence whether `tests/unit/scripts/` rejoins the default `pytest` run (a Windows native-abort workaround from c97705c0), and add Dependabot for the pinned GitHub Actions. The `frozenset` cosmetic item is dropped from the carried list.

## Status

Lifted on fix/test-exclusion-lift from master fe3195c1: intent b54f21fb, Dependabot 10697cd1, lift 3e64dc82. Rule: eight full runs with the directory included (six sequential, two concurrent) all exit 0 — 8/8 clean, 3870 passed each. Default `uv run pytest` now runs 3870 tests (+140); CI run 39153742114 green with the isolated step removed. Sessions: 0. Merged into master at 09ea2e74 and pushed (post-merge full suite 3870 passed). No release: test/CI config only; the CHANGELOG contributor note ships with the next release.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, lift rule, scope |
| [01-verification.md](./01-verification.md) | Reproduction record, every wiring site, checks, Dependabot, dropped item |
| [02-handoff.md](./02-handoff.md) | Carried import item (no guard), recurrence watch, Dependabot confirmation |
