---
feature: purpose-opus
phase: pre-registration
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Purpose inference on opus (opus-hard fixtures)

On opus only, does the shipped `purpose_before_action` rule raise the purpose-served rate on unstated-purpose fixtures that opus misses without it, and does it raise over-inference on plain requests? Comparison: sc-full vs sc-ablate (the `sc-candidate` arm restored from `82cbf3bb`), default effort, cap 110 sessions. Follows [purpose-generalization](../purpose-generalization/README.md) (opus D5 ceiling there).

## Status

Phase 0 built and frozen by its commit on branch `feature/purpose-opus`: 7 new fixtures (N1–N7) with `-stated` twins, control K3, `app02-disk-alert` and K2 reused; ablation arm restored; an independent fixture review (FREEZE WITH FIXES) applied to the checks, the N6 service and the K3 proxy. No model session run yet (0/110). Next: Phase 1a (screen, sc-ablate only).

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, Q1–Q13 decisions, cap, constraints |
| [01-fixtures.md](./01-fixtures.md) | Pre-registration: arms, prompts, evidence and levers, checks, allowed sets, planted tests, leak guard, app02 reuse, task-spec hash, Phase 1/2 commands |
| [01a-rules.md](./01a-rules.md) | Decision and phase rules, verbatim from plan v2 |
| [01b-hashes.md](./01b-hashes.md) | sha256 per fixture file |
