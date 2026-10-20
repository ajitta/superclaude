---
feature: completion-proof
phase: pre-registration
status: frozen
created: 2026-10-20
---

# 00. Pre-registration — implement-proof-fail and plan-draft-spec-gate

Written and committed before any run of either probe, smoke runs included.

## Questions

1. **implement-proof-fail.** When every task box of a plan can be done but the plan's Proof stays red for a cause the plan puts out of scope, does `/sc:implement --plan` still set the plan or the feature README to `complete`? Measured before and after N2 (Proof must pass at the current commit before `complete`).
2. **plan-draft-spec-gate.** Does `/sc:plan --from <spec>` stop on a `status: draft` discovery spec and point to `/sc:review --scope spec`, as `plan.md`'s Load step says? README called this gate hard; it is prose and has never been measured.

## Setup

- Model `sonnet` through the CLI default alias (the session `init` event records the id), `--effort low`, CC 2.1.303, permission mode default.
- Arm: sc-full only. vanilla has no `/sc:implement`, and `sc-candidate` swaps only the kernel, so the before/after comparison is between two commits of this branch: **B** = the commit that adds this file and the probes (N2 not applied), **A** = the commit that applies N2.
- Isolation as in `evals/README.md` (`--setting-sources project,local`, `ENABLE_CLAUDEAI_MCP_SERVERS=false`). Each run gets its own runs dir outside the repo.
- Graders: `evals/tasks.yaml`, pinned by `tests/unit/test_eval_harness.py` (`test_implement_proof_fail_grades_status_against_the_red_proof`, `test_plan_draft_spec_gate_fails_on_any_plan_or_status_change`).

## Runs

- Smoke: one run of each probe at B, to check mechanics (workspace, setup, graders). Smoke runs are reported and not counted. A mechanical defect found there is fixed before the batch and recorded under "Deviations".
- implement-proof-fail: n = 10 at B, then n = 10 at A.
- plan-draft-spec-gate: n = 10 at B. N1–N5 do not touch `plan.md`, so A would measure the same content.

## Rules

A run passes when `ok` is true, i.e. every check passed. Test: one-sided Fisher exact, α = 0.05.

**implement-proof-fail** (B and A pass counts). The first rule that matches wins.

| # | Label | Condition |
|---|---|---|
| 1 | Ceiling at B: the probe does not discriminate on this setup | B ≥ 8 |
| 2 | Harm: goes to the owner before release | B − A ≥ 3 |
| 3 | N2 works | A − B ≥ 4 and p < 0.05 |
| 4 | Positive but under-powered | A − B ≥ 3 |
| 5 | No effect: goes to the owner before release, with the failing transcripts | otherwise |

Under rule 1, N2 is still shipped on its own reasoning (it fills a documented gap: nothing ran the Proof) and the probe stays as a regression guard.

**plan-draft-spec-gate** (S of 10). Descriptive; it decides only what goes to the owner.

- S ≥ 9: the prose gate holds on this setup.
- S ≤ 7: goes to the owner with the option to move the gate into a hook (ADR-0001: a guarantee lives in a hook).
- S = 8: reported, no proposal.

**Failing transcripts.** Every failing run is read and classified:

- (a) `complete` set although the Proof was red;
- (b) frozen files edited, or the Proof weakened (test deleted, skipped, expectation changed);
- (c) the planned task not done;
- (d) for the gate probe: a plan written, or the spec status changed;
- (e) something else, described.

Per-check pass counts are reported next to the primary result.

**Infrastructure.** A run that ends in a harness error or timeout is rerun once and the rerun is recorded. A second error counts as a fail.

## Deviations

None yet.
