---
feature: author-check-multiline
phase: intent
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Author-check multiline consumers + release 4.29.2

Close candidate 1 from the [context-budget-restore handoff](../context-budget-restore/02-handoff.md) (carried from harness-checker-hygiene): `superclaude author-check`'s automatic format inference and N4 sentence extraction work one line at a time, so a multiline opener yields a silent clean result. Both consumers adopt the structural scan's placement rule. Then release 4.29.2 with the accumulated fixes.

## Status

Intent approved in chat on 2026-10-19 (candidates 1 + 5, 0 sessions, patch 4.29.2 without canary). Implementation on fix/author-check-multiline from master 02f31d7b.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Original request, decisions, scope and limits |
