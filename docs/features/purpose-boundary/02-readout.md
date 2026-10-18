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
| Q8 delete `MODE_Task_Management.md` | every check equal across arms | task-tool use 2/6 vs 0/6 (n=6, two batches; the second batch was equal on every check) | **Keep** |
| Q8 delete `MODE_Orchestration.md` | measurable axes equal AND unmeasured content carried elsewhere | batching 6/6 vs 5/6 | **Keep** (first clause not met by one run; the second — `FLAGS.md:18-26`, `RULES_DELEGATION.md` — was never reached) |

What did not happen: no mode file, TRIGGER_MAP row, flag roster entry, README count or `mode-authoring.md` example changed; `RETIRED_FLAGS` untouched. The `mode-*` fixtures and the `sc-no-modes` arm stay in the harness as the measurement any later deletion proposal has to pass.

## Closed after the first readout (owner's answers)

1. Cap raised; `make canary-gates` run: **7/7 hard-gate checks passed**, 4 sessions, sonnet (`C:/tmp/sc-evals/gate-pb-20261018-220855/`).
2. Second mode batch run (12 sessions): no difference on any check; the combined n=6 result keeps both modes by the pre-fixed rule (01 §Item 2 has the reading).
3. Released as **4.29.0** — a kernel rule changed (precedent 4.28.0).

## Left for a later round

- Modes: a sharper fixture, or a decision on whether "no distinctive behavior in 6/6 sc-full runs" counts as the measurement the lean rule asks for.
- Lean-handoff items 4 (`<finding_policy>` copies) and 6 (`RULES_QUALITY` budget), unchanged.
