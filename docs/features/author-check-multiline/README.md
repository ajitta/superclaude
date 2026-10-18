---
feature: author-check-multiline
phase: closed
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Author-check multiline consumers + release 4.29.2

Close candidate 1 from the [context-budget-restore handoff](../context-budget-restore/02-handoff.md) (carried from harness-checker-hygiene): `superclaude author-check`'s automatic format inference and N4 sentence extraction worked one line at a time, so a multiline opener yielded a silent clean result. Both consumers now apply the structural scan's placement rule. Then release 4.29.2 with the accumulated fixes.

## Status

Implemented on fix/author-check-multiline from master 02f31d7b: intent 252d37b7, fix a1d6ca7a. Red→green evidence, before/after reproductions and the 559-file whole-tree diff (0 differences) are in [01-verification.md](./01-verification.md). Headless sessions used: 0. Merged into master at 37a6501b and pushed; version bump merged at 1f57aa62; **released as v4.29.2** (`make release`: Tests run 39150331450 green, GitHub release created, `stable` → 1f57aa62 — master, stable and the tag share one SHA). Local-scope install re-synced (83 files, `verify-drift` clean, `superclaude --version` 4.29.2). No canary gate was due (`core/` and `hooks.json` unchanged since v4.29.1) and none was run — an explicit decision recorded in 00-intent.md; the release carries the loader-budget change measured deterministically in context-budget-restore.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, scope and limits |
| [01-verification.md](./01-verification.md) | Before/after reproductions, red→green evidence, whole-tree diff, integration checks |
| [02-handoff.md](./02-handoff.md) | Carried leftovers, recorded limits, delivery status pointer |
