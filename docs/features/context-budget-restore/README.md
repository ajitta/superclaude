---
feature: context-budget-restore
phase: intent
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Context budget restore

Close candidate 1 from the [harness-checker-hygiene handoff](../harness-checker-hygiene/02-handoff.md): `/sc:analyze --delegate` drops `core/rules/RULES_DOCS.md` because the three priority-1 rule modules (8,015 estimated tokens) exceed the loader's 8,000-token default — a regression shipped in v4.29.1. The default rises to 12,000 from one shared constant and two deterministic tests pin the headroom. No instruction content changes.

## Status

Intent approved in chat on 2026-10-19 (candidate 1 only, 0 headless sessions, budget 12,000). Implementation on fix/context-budget-default from master d995aa1a. Unmerged, unreleased.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, scope and limits |
