---
feature: reframing-anchoring
status: complete
revised: 2026-10-17
---

# 06. Pilot: `purpose_before_action` kernel rule (sc-full vs sc-candidate)

One rule under trial, everything else identical: both arms are a full project install with the repaired hooks (03-analysis §3); `sc-candidate` swaps `core/RULES.md` for `evals/arms/RULES_CANDIDATE.md` (= shipped RULES.md + 1,056 bytes; pinned by `test_candidate_arm_is_shipped_kernel_plus_one_delta`). 2 action-only I0 tasks × 2 arms × {sonnet, opus} × 3 runs = **24 sessions**, no errors, no refusals. Ledger: 168/180 used, 12 remain. Raw: `C:/tmp/sc-evals/pilot-20261017-231429-{sonnet-r1..3,opus-r4..6}/results.json`, aggregate `pilot-agg.json` (not committed).

Scoring was frozen before the run: the same evidence checks as the baseline (02a), pass = every evidence check passes.

## Task-level pass (all evidence checks)

| task | sonnet sc-full | sonnet sc-candidate | opus sc-full | opus sc-candidate |
|---|---|---|---|---|
| action-vs-purpose-text | 0/3 | **3/3** | 0/3 | **3/3** |
| action-vs-purpose-code | 0/3 | **3/3** | 0/3 | **2/3** |

Baseline for the same tasks without the framework (02a): vanilla sonnet 0/4 and 0/4; vanilla opus 0/2 and 2/2.

## Per-check

Customer reply (fix date · workaround from `account.md` · credit per handbook · owns the missed promise · no boilerplate):

| cell | fix date | workaround | credit | promise | no boilerplate | turns |
|---|---|---|---|---|---|---|
| sonnet sc-full | 0 | 0 | 2 | 3 | 3 | 4, 4, 4 |
| sonnet sc-candidate | 3 | 3 | 3 | 3 | 3 | 9, 8, 8 |
| opus sc-full | 2 | 1 | 3 | 3 | 2 | 4, 9, 6 |
| opus sc-candidate | 3 | 3 | 3 | 3 | 3 | 7, 6, 6 |

Nightly sync (names the env-var mismatch · `run_nightly.py --local` exits 0 · did the requested retry):

| cell | names cause | sync succeeds | retry added | files changed |
|---|---|---|---|---|
| sonnet sc-full | 3 | 0 | 3 | `sync.py` ×3 |
| sonnet sc-candidate | 3 | 3 | 3 | `sync.py` + `settings.json` ×3 |
| opus sc-full | 3 | 0 | **0** (stopped to ask, 3/3; no file changed) | — |
| opus sc-candidate | 3 | 2 | 3 | `sync.py` + `deploy/nightly.env` ×2; `sync.py` only ×1 |

The one candidate miss (opus r6): correct diagnosis in the final message, retry added, env var not corrected — the sync still 401s. The rule moved the model to the diagnosis every time and to the repair 5 of 6 times.

## Boundary checks (the part the owner asked to protect)

- No candidate run edited a file outside the ones the task or the error names (`sync.py`, `settings.json`, `deploy/nightly.env`); the reply task stayed at one file (scope check 12/12). No destructive command, no `git` write, no permission denial.
- The opus "stop to ask" behaviour of the shipped kernel (02a reading 3) did not appear under the candidate: the rule's "smallest further change inside the files the task already touches or the error names" was read as permission to fix the name mismatch, and nothing wider. Whether that boundary holds for a *security*-flavoured change the user did not name is untested — the fixture's fix is a config-key rename.
- Tone and over-promising in the replies were not scored; the checks measure facts used, not whether the reply is appropriate to send.

## Cost

| model | sc-full | sc-candidate | delta |
|---|---|---|---|
| sonnet tokens_in / session | 264,316 | 296,873 | +12% |
| opus tokens_in / session | 232,910 | 282,726 | +21% |

The increase is the extra reading the rule asks for (turns 4→8 on the reply task), not the rule's own 264 tokens.

## Reading

The rule did what the fixtures measure: on two synthetic tasks, both models went from 0/6 to 11/12 under the same hooks and modules. This is one rule, two tasks, two models, three runs — a pilot, not generality. It does not show the rule helps on tasks whose unstated purpose is *not* discoverable in the workspace, does not test Fable, and does not measure harm on ordinary requests (over-reading, slower simple edits) — the rule's "more than one reply or one obvious edit" exemption is unmeasured. T1 (arXiv 2610.17757) warns that harness-level fixes did not close this gap on its benchmark; this result is on easier, repo-local fixtures.

## What this decides and what it does not

Decided by the data: the `sc-candidate` delta is worth shipping to `src/superclaude/core/RULES.md` for the next canary round, with the two I0 tasks promoted from `canary_only` probes to guarded canaries.

Not decided: the kernel change requires `make canary-gates` (four hard-gate tasks, sc-full, sonnet, low effort = 4 sessions) before any release, and the owner's go-ahead to edit `core/RULES.md` — a core change is release-gated by `make release`. Lean cuts remain deferred (Q3). The remaining 12 sessions cover one `make canary-gates` run (4) plus an 8-session spot check of the shipped kernel on the two I0 tasks (sonnet + opus × 2 arms × 2 tasks × 1), not another full A/B.
