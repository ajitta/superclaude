---
feature: purpose-opus
phase: closed
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Purpose inference on opus (opus-hard fixtures)

On opus only, does the shipped `purpose_before_action` rule raise the purpose-served rate on unstated-purpose fixtures that opus misses without it, and does it raise over-inference on plain requests? Comparison: sc-full vs sc-ablate (the `sc-candidate` arm restored from `82cbf3bb`), default effort, cap 110 sessions. Follows [purpose-generalization](../purpose-generalization/README.md) (opus D5 ceiling there).

## Status

Closed on branch `feature/purpose-opus` (not yet merged). Frozen spec `976ce0ef`; 79/110 sessions, $23.24 API-equivalent. Screen kept N2, N5, N7 of seven candidates (all reachable when stated) + app02 → k = 4. Readout ([04](./04-readout.md)): **D3a — positive, under-powered** (sc-full 13/20 vs sc-ablate 8/20, p = 0.103; without app02 8/15 vs 3/15, p = 0.064, same label); over-inference **O1** — none detected (0/10 vs 0/10, Wilson upper 28%); no boundary failures. No shipped content changed. Q10 close applied: N2, N5, N7, K3 kept as probes; screen failures and `-stated` twins deleted; `RULES_CANDIDATE.md` back to an empty delta.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, Q1–Q13 decisions, cap, constraints |
| [01-fixtures.md](./01-fixtures.md) | Pre-registration: arms, prompts, evidence and levers, checks, allowed sets, planted tests, leak guard, app02 reuse, task-spec hash, Phase 1/2 commands |
| [01a-rules.md](./01a-rules.md) | Decision and phase rules, verbatim from plan v2 |
| [01b-hashes.md](./01b-hashes.md) | sha256 per fixture file |
| [02-screen.md](./02-screen.md) | Preflight, screen (sc-ablate, opus), reachability, ledger |
| [03-measurement.md](./03-measurement.md) | Phase 2 per-fixture table with `opened`, miss types, controls, overhead, reserve run, cost |
| [04-readout.md](./04-readout.md) | Rules applied (D3a, sensitivity D3a, O1), limits, what stays open, Q10 close |
