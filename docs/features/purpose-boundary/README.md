---
feature: purpose-boundary
phase: readout
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# Purpose-boundary round

Re-measure the `purpose_before_action` fix-vs-propose boundary with one candidate sentence (sc-full vs sc-candidate), measure the two deferred modes by ablation (sc-full vs sc-no-modes), and apply the lean leftovers that need no measurement. Started from the lean round's [handoff](../lean-round/06-handoff.md).

## Status

Phases 0–3 done on branch `feature/purpose-boundary` (base `a0b7fc9a`). Decisions Q1–Q8 in [00-intent.md](./00-intent.md); measurement in [01-measurement.md](./01-measurement.md) (49 of 52 sessions); readout in [02-readout.md](./02-readout.md): the boundary sentence shipped into `core/RULES.md` (sc-full 3/8 → sc-candidate 8/8), both modes kept by the pre-fixed rule, `/sc:sc` removed, MCP docs trimmed, init pair cross-linked. Not run: canary-gates (4 sessions, cap has 3). Not done: merge, push, release.

Working plan: `.hermes/plans/2026-10-18_211158-handoff-round.md` (v3; v1 and the reviewed v2 preserved alongside it).

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, purpose, decision table |
| [01-measurement.md](./01-measurement.md) | Phase 1 results: item 7 per-check table with miss types, item 2 ablation per check, harness findings |
| [02-readout.md](./02-readout.md) | Q7/Q8 applied, what shipped, what stays open |
