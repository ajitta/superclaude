---
feature: purpose-boundary
phase: readout
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 02. Readout — Q7 and Q8 applied

Inputs: [01-measurement.md](./01-measurement.md); criteria from [00-intent.md](./00-intent.md).

| Question | Criterion | Result | Decision |
|---|---|---|---|
| Q7 ship the boundary sentence | per model candidate − sc-full ≥ +2 on sync-succeeds; candidate ≥ 6/8 | sonnet +3, opus +2; candidate 8/8 | **Shipped** into `core/RULES.md` `<purpose_before_action>` — one sentence appended after "…is proposed with the evidence, not made." (+211 B, kernel 5,925 → 6,136 B). `evals/arms/RULES_CANDIDATE.md` == shipped again; `CANDIDATE_INSERTS` empty; trial log updated |
| Q8 delete `MODE_Task_Management.md` | every check equal across arms | task-tool use 2/3 vs 0/3 | **Keep** |
| Q8 delete `MODE_Orchestration.md` | measurable axes equal AND unmeasured content carried elsewhere | batching 3/3 vs 2/3 | **Keep** (first clause not met; the second — `FLAGS.md:18-26`, `RULES_DELEGATION.md` — was never reached) |

What did not happen: no mode file, TRIGGER_MAP row, flag roster entry, README count or `mode-authoring.md` example changed; `RETIRED_FLAGS` untouched. The `mode-*` fixtures and the `sc-no-modes` arm stay in the harness as the measurement any later deletion proposal has to pass.

## Still open for the owner

1. The mode readings in 01 §Item 2: both modes stay by the pre-fixed rule, but the differences are one session at n=3 and the Task_Management text never produced its own distinctive behaviors. A second batch (12 sessions) or a sharper fixture are the two ways to settle it; neither is in this round's cap.
2. `make canary-gates` (4 sessions) is required before `make release` because `core/` changed; the cap (52) has 3 left. Not run.
3. Release number if released: **4.29.0** — a kernel rule changed (precedent 4.28.0).
