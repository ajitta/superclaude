---
feature: test-exclusion-lift
phase: intent
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Lift the tests/unit/scripts exclusion; Dependabot

Decide on evidence whether `tests/unit/scripts/` rejoins the default `pytest` run (a Windows native-abort workaround from c97705c0), and add Dependabot for the pinned GitHub Actions. The `frozenset` cosmetic item is dropped from the carried list.

## Status

Intent approved in chat on 2026-10-19 (rows 1 + 3 + 6, 0 sessions, no release). Reproduction runs in progress on fix/test-exclusion-lift from master fe3195c1.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, lift rule, scope |
