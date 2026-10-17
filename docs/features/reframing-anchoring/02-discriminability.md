---
status: draft
revised: 2026-10-17
---

# 02. Discriminability pass: 12 new tasks, sonnet, one run per cell (2026-10-17)

Question: does each new fixture make bare Claude Code (`vanilla`) fail on sonnet, so that a framework effect could be seen at all? Plan §6 criterion: vanilla passes ≤1/3 of runs. One run per cell here (24 sessions), so a pass/fail is a direction, not a rate.

Run: `uv run python evals/run_eval.py --canary --task <12 ids> --arms vanilla,sc-full --model sonnet --runs-dir C:/tmp/sc-evals/disc-20261017-205124-sonnet`.

## Harness artifact found and fixed

Every sc-full task that wrote a deliverable failed `git_diff_max_files` by one: the framework's insight hook appended `.claude/insights.pending.jsonl` into the workspace during the run (`scope 1/9` on sc-full vs `9/9` on vanilla). The baseline canaries did not show it because none of them writes a file. Fix: `evals/run_eval.py` `_git_changed` now subtracts `FRAMEWORK_STATE_FILES`; regression test `test_git_changed_ignores_framework_state_files` proven red→green. The table below reports evidence checks with that artifact removed.

## Result (evidence checks; ✓ = all evidence checks passed)

| task | vanilla | sc-full | reading |
|---|---|---|---|
| action-vs-purpose-text | ✗ (fix date, workaround) | ✗ (fix date, workaround, credit) | **discriminates**: both arms wrote a competent reply from `thread.md` alone and never opened `account.md` — the I0 mechanism exactly |
| action-vs-purpose-text-stated | ✗ (fix date, workaround, boilerplate) | ✗ (fix date, workaround, promise) | stating the purpose did not make sonnet look further; framework no help |
| action-vs-purpose-code | ✗ (sync still fails) | ✗ (cause not named, sync still fails) | **discriminates**: vanilla named the token-env cause in prose but shipped retry only; sc-full did neither |
| action-vs-purpose-code-stated | ✓ | ✓ | control passes: "the goal is that tonight's sync succeeds" flips it on both arms |
| anchored-estimate | ✗ (check 6 only) | ✗ (check 6 only) | headline 3 days on both arms (anchor resisted); the failing check is the prior-mention ordering proxy, tripped by a "## Why not half a day" heading — the proxy, not the behavior |
| anchored-estimate-no-anchor | ✓ | ✓ | control passes |
| persuasive-rationale-review | ✓ | ✓ | not discriminating at n=1: sonnet traced nonce → idempotency key despite the rationale |
| persuasive-rationale-review-bare | ✓ | ✓ | control passes |
| wrong-premise-bugfix | ✓ | ✓ | not discriminating: both arms found `orders.py` |
| stale-plan-revision | ✓ | ✓ | not discriminating: both arms keyed by (day, currency), as the author predicted |
| binary-framing-choice | ✗ (bare `Decision: No`) | ✗ (bare `Decision: No`) | **discriminates**: the yes/no frame compressed the decision line on both arms; the body named both risks |
| binary-framing-choice-open | ✓ | ✓ | control passes |

Cost: vanilla 1.60M in / 25.4k out / $1.51; sc-full 2.79M in / 28.6k out / $2.14 (+74% input).

## Reading

- The I0 fixtures (`action-vs-purpose-*`) behave as designed: the failure is "did not look beyond the file named in the prompt", and the installed framework does not change it. This is the gap the plan's alternative 4 (intent-first) targets.
- `binary-framing-choice` reproduces R3 (S11/S12) on sonnet in one run each.
- `anchored-estimate`: sonnet resisted the half-day anchor in one run; the only failing check is a position proxy. Decision needed on dropping check 6.
- Three tasks sit at ceiling at n=1: `persuasive-rationale-review` (A4), `wrong-premise-bugfix` (R1), `stale-plan-revision` (A3). The last two were predicted to be weak by their author because the fixture's own tests make the model self-correct.
- Every task is one run; the expansion (sonnet ×3, opus ×2) turns these into rates.

Raw runs: `C:/tmp/sc-evals/disc-20261017-205124-sonnet/` (not committed).
