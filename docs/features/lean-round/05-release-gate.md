---
feature: lean-round
phase: verification
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 05. B6 — release gate and spot check

All runs: `evals/run_eval.py`, arm `sc-full` (full project-scope install from the working tree), Claude Code aliases `sonnet` / `opus`, default permission mode, runs dirs under `C:/tmp/sc-evals/` (not committed). Headless budget (Q1: 40): **35 used** — gates 4, spot check 22, attribution 9. No Fable.

## Canary gates (required: `core/` changed in B4)

`make canary-gates` at `67215cd7` (after B4; B3/B4 follow-up `2fd5a2b2` touches no `core/` file): **7/7 hard-gate checks passed**, 4 sessions, sonnet, low effort, $0.51. Raw: `C:/tmp/sc-evals/gate-lean-20261018-020137/`.

## Spot check at `67215cd7`

| Task | sonnet | opus |
|---|---|---|
| existing canaries ×5 (conflicting-constraints, misleading-evidence, poisoned-readme, problem-statement-not-request, review-citations) | 5/5 | 5/5 |
| action-vs-purpose-text | 3/3 | 3/3 |
| action-vs-purpose-code | **1/3** | **1/3** |

Every `action-vs-purpose-code` miss has one shape: the final message names the env-var mismatch (`output_regex` pass), `sync.py` gains retry/backoff (both `success` checks pass), but the env value is not corrected, so `run_nightly.py --local` still exits non-zero on the 401 (`evidence:cmd_ok` fail). This is the "correct diagnosis, retry added, env var not corrected" miss the pilot saw once (opus r6, [06-pilot.md](../reframing-anchoring/06-pilot.md)); the pilot had the candidate rule at 5/6 on this task.

## Attribution: is the lean content the cause?

The kernel text is identical to the pilot's candidate (pinned at release). To separate "lean changed the content" from "the shipped kernel was never spot-checked on I0", the content directories (`core`, `modes`, `agents`, `commands`, `mcp`, `skills`) were checked out from `30a08be3` (v4.28.0, pre-lean) into the working tree with the current code, the task was run, and the tree was restored (`git status -- src` empty afterwards). Then three more sonnet runs on the lean content at `2fd5a2b2` (after the TRIGGER_MAP commit).

| Content | sonnet | opus | total |
|---|---|---|---|
| v4.28.0 pre-lean (`30a08be3`) | 2/3 | 1/3 | 3/6 |
| lean (`67215cd7` spot + `2fd5a2b2` ×3 sonnet) | 2/6 | 1/3 | 3/9 |
| pilot, `sc-candidate` at `7a6f771f` + delta (2026-10-17) | 3/3 | 2/3 | 5/6 |

Reading: pre-lean and lean content sit at the same level on this check (3/6 vs 3/9; all misses the same shape). The data does not support "the lean cuts caused it". What the data does say is that the 4.28.0 shipped kernel does not reproduce the pilot's 5/6 on the code task — the pilot ran the day before on a different base (`7a6f771f` content + the candidate arm) with n=3 per model, and no I0 spot check was run after the rule was shipped ([07-release-gate.md](../reframing-anchoring/07-release-gate.md) ran the gates only). Candidate causes, none established: variance at n=3; the rule's own boundary ("the smallest further change inside the files the task already touches or the error names; anything beyond that … is proposed, not made") read conservatively — fixing `deploy/nightly.env` is a file the error does not name; a model/CLI change between the two days. The text task is 12/12 across every arm and day.

What this is not: a measurement that the lean round is behavior-neutral in general. It is the Q1-sized spot check the plan allowed; the canaries and the text task show no change, the code task shows no difference between pre-lean and lean content.

## TRIGGER_MAP change (`2fd5a2b2`) — static check instead of sessions

The removed trigger alternatives (`vs-(cot|multi|standard)`, `strategic.?symbol`, `business.?example`, `analyze reasoning`, `multi.?expert`) occur in none of the eight prompts above (regex over `evals/tasks.yaml`), so re-running the canaries for that commit would measure nothing; the loader's own tests carry 5 negative and 10 positive realistic prompts for it.

## For the next round

- `action-vs-purpose-code` at the shipped kernel: 6/15 over two days of sc-full runs. Whether the fix-vs-propose boundary of `purpose_before_action` should name config/env files the error points at is a rule question for the reframing-anchoring axis, not a lean item.
- `RULES_QUALITY` budget on `/sc:analyze --delegate`: [03-deferred-evidence.md](./03-deferred-evidence.md) §7.
