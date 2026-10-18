---
feature: purpose-generalization
phase: screen
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Purpose-inference generalization (axis A)

Does the shipped `purpose_before_action` rule help on unstated-purpose requests beyond its two pilot fixtures, and does it make the model over-infer on plain requests? Comparison: sc-full vs sc-ablate (the `sc-candidate` arm holding the shipped kernel minus the rule), sonnet and opus, cap 90 sessions. Started from [test-exclusion-lift/02-handoff.md](../test-exclusion-lift/02-handoff.md) (recommendation A).

## Status

Phase 0 built and frozen by its commit (task ids made neutral before the freeze — see 01 Tasks). Branch `feature/purpose-generalization` from master `b50a1820`. Built: 6 fixture dirs, 12 canary-only tasks, the ablation arm (`evals/arms/RULES_CANDIDATE.md`, byte-equal to `123c6a22^:src/superclaude/core/RULES.md`), and `tests/unit/test_eval_purpose_fixtures.py`. Sessions: 0. The pre-registration in [01-fixtures.md](./01-fixtures.md) is frozen by the Phase 0 commit; nothing in it changes after Phase 1 starts.

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, Q1–Q14 decisions, cap, constraints |
| [01-fixtures.md](./01-fixtures.md) | Pre-registration: prompts, checks, allowed sets, decision rules, Q12 statement, fixture hashes, Phase 1/2 commands |
