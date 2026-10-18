---
feature: purpose-generalization
phase: closed
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Purpose-inference generalization (axis A)

Does the shipped `purpose_before_action` rule help on unstated-purpose requests beyond its two pilot fixtures, and does it make the model over-infer on plain requests? Comparison: sc-full vs sc-ablate (the `sc-candidate` arm holding the shipped kernel minus the rule), sonnet and opus, cap 90 sessions. Started from [test-exclusion-lift/02-handoff.md](../test-exclusion-lift/02-handoff.md) (recommendation A).

## Status

Closed on branch `feature/purpose-generalization` (not yet merged). Frozen spec `82cbf3bb`; 87/90 sessions. Screen kept P1, P2, P3, P5 (P4 dropped at ceiling). Readout ([04](./04-readout.md)): **sonnet D3a** — positive, under-powered (sc-full 5/12 vs sc-ablate 2/12, p = 0.185); **opus D5** — ceiling, non-informative (12/12 vs 8/12); over-inference **O1** — none detected (0/12 vs 0/12, Wilson upper 24%); no boundary failures. No shipped content changed, no release. Q11 cleanup applied: six probes kept, P4 and the `-stated` twins deleted, `RULES_CANDIDATE.md` back to an empty delta.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, Q1–Q14 decisions, cap, constraints |
| [01-fixtures.md](./01-fixtures.md) | Pre-registration: prompts, checks, allowed sets, decision rules, Q12 statement, fixture hashes, Phase 1/2 commands |
| [02-discriminability.md](./02-discriminability.md) | Preflight, screen (sonnet, sc-ablate), host positive control, ledger |
| [03-measurement.md](./03-measurement.md) | Phase 2 per-fixture tables, miss types, controls, Q8 reachability, cost |
| [04-readout.md](./04-readout.md) | Rules applied (sonnet D3a, opus D5, O1), limits, next-round candidates, Q11 close |
