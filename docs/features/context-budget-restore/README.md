---
feature: context-budget-restore
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Context budget restore

Close candidate 1 from the [harness-checker-hygiene handoff](../harness-checker-hygiene/02-handoff.md): `/sc:analyze --delegate` drops `core/rules/RULES_DOCS.md` because the three priority-1 rule modules (8,015 estimated tokens) exceed the loader's 8,000-token default — a regression shipped in v4.29.1. The default rises to 12,000 from one shared constant and two deterministic tests pin the headroom. No instruction content changes.

## Status

Implemented on fix/context-budget-default from master d995aa1a: intent a60b8d17, fix 9f0f6ce3. Red→green evidence, the before/after `context explain` table and the integration checks are in [01-verification.md](./01-verification.md). Headless sessions used: 0 (owner cap 0). **Unmerged, unreleased**; stable and v4.29.1 unchanged. The installed local-scope copy runs the fix through the editable uv tool without an install sync; `verify-drift --scope local` is clean because no content file changed. `src/superclaude/core/` untouched — no canary gate. Remaining candidates: [02-handoff.md](./02-handoff.md).

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, scope and limits |
| [01-verification.md](./01-verification.md) | Before/after measurement, red→green evidence, integration checks |
| [02-handoff.md](./02-handoff.md) | Carried author-check candidate, the stacked-mode residual, delivery status |
