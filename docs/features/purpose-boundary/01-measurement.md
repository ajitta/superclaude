---
feature: purpose-boundary
phase: measurement
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 01. Phase 1 measurement

All runs: `evals/run_eval.py`, Claude Code 2.1.302, default permission mode, runs dirs `C:/tmp/sc-evals/pb-20261018-220855-*` (not committed). Headless budget (cap 52): **49 used** — item 7: 32 + 1 rerun; item 2: 12 + 12 rerun. No Fable. Aggregation script: `.hermes/scratch/agg.py` (local), reading `results.json` `checks[].{tag,passed,detail}` per (task, arm, run).

## Item 7 — `purpose_before_action` fix-vs-propose boundary

Task `action-vs-purpose-code`, sc-full vs sc-candidate (shipped `RULES.md` + one sentence, 211 B, `tests/unit/test_eval_harness.py` `CANDIDATE_INSERTS` at `75afc784`), both arms in the same batch, 4 runs per model.

| check | sonnet sc-full | sonnet sc-candidate | opus sc-full | opus sc-candidate |
|---|---|---|---|---|
| changed something (success) | 4/4 | 4/4 | 4/4 | 4/4 |
| retry added in `sync.py` (success) | 4/4 | 4/4 | 4/4 | 4/4 |
| final text names the cause (evidence) | 4/4 | 4/4 | 4/4 | 4/4 |
| **`run_nightly.py --local` exits 0 (evidence)** | **1/4** | **4/4** | **2/4** | **4/4** |
| all checks | 1/4 | 4/4 | 2/4 | 4/4 |
| turns | 15, 18, 15, 13 | 16, 16, 18, 16 | 7, 9, 9, 11 | 14, 10, 12, 13 |

Files changed per session (from `git status` in each workspace):

| run | sonnet sc-full | sonnet sc-candidate | opus sc-full | opus sc-candidate |
|---|---|---|---|---|
| r1 | `sync.py` | `settings.json` `sync.py` | `sync.py` (rerun r1b; the first r1 ended `Not logged in` after 9 turns, `sync.py` only, excluded as an error) | `deploy/nightly.env` `sync.py` |
| r2 | `settings.json` `sync.py` | `settings.json` `sync.py` | `settings.json` `sync.py` | `settings.json` `sync.py` |
| r3 | `sync.py` | `settings.json` `sync.py` | `deploy/nightly.env` `sync.py` | `deploy/nightly.env` `sync.py` |
| r4 | `sync.py` | `deploy/nightly.env` `sync.py` | `sync.py` | `deploy/nightly.env` `sync.py` |

Miss type: every sc-full miss (5/8) changed `sync.py` only while its final text named the env-var mismatch — "knew the file, did not fix it", never "did not find it". The candidate sentence closed it 8/8; it never produced an edit outside `settings.json` / `deploy/nightly.env` / `sync.py`.

**Q7 applied**: per model candidate − sc-full on the sync-succeeds check = +3 (sonnet), +2 (opus) — both ≥ +2; candidate total 8/8 ≥ 6/8. **Ship.** Same-day sc-full sits at 3/8, consistent with the two-day 6/15 in `lean-round/05-release-gate.md`, so the day/base hypothesis there does not explain the earlier gap; the wording does.

Caveat on the "names the cause" check: on sc-* arms up to this batch, the Stop hook's `INSIGHT:` request made the insight line the result text (see §Harness below), and the insight restated the cause every time. The check passed 16/16 for that reason as much as for the report; the ship decision rests on the `cmd_ok` check, which the hook cannot touch.

## Item 2 — modes ablation (sc-full vs sc-no-modes, sonnet, n=3)

Prompts carry `--task-manage` / `--orchestrate`; `sc-no-modes` deletes the two mode files from the workspace install, so the loader injects nothing for the flag (verified: `superclaude hook context_loader` rc 0, empty output, in the dry-run workspace). First batch of 12 ran with the insight request on and is discarded for the `output_regex` checks (they read the insight line); the table is the rerun with it off.

`mode-task-manage` (3-layer feature; task tools granted via per-task `allowed_tools`):

| check | sc-full | sc-no-modes |
|---|---|---|
| suite passes + 3 files changed (success ×4) | 3/3 | 3/3 |
| task tool called (`TodoWrite|TaskCreate|TaskUpdate`) | **2/3** | **0/3** (first batch 1/3 vs 0/3; six runs: 3/6 vs 0/6) |
| final report organised by phase/checkpoint/milestone | 0/3 | 0/3 |
| suggests `/sc:save` | 0/3 | 0/3 |
| turns | 15, 21, 20 | 17, 5, 8 |

`mode-orchestrate` (three independent defects, one merged report):

| check | sc-full | sc-no-modes |
|---|---|---|
| names each defect site (success ×3) + `check_all.py` exits 0 | 3/3 | 3/3 |
| ≥3 tool calls in one message (`parallel_tool_calls_min: 3`) | 3/3 | **2/3** (r1: max 1, 4 turns; first batch 3/3 vs 3/3; six runs: 6/6 vs 5/6) |
| final report states the streams were run concurrently | 0/3 | 0/3 |
| turns | 11, 11, 11 | 4, 11, 11 |

**Q8 applied mechanically**: Task_Management — one check differs (task-tool use, 2/3 vs 0/3): **keep**. Orchestration — one measurable check differs by one run (3/3 vs 2/3): **keep**. Readings the owner may weigh: the Task_Management text produces task-list use but neither of its distinctive behaviors (phase-structured report, `/sc:save` suggestion) appeared in any of six sc-full runs; the Orchestration difference is one session at n=3 and absent in the first batch. Both are below what n=3 can separate from noise; the criterion was fixed in advance, so the mechanical result stands and the reading goes to the owner.

## Harness findings this phase

- **Insight request skews `output_regex`** (fixed, `evals/run_eval.py` `SUPERCLAUDE_INSIGHT_PROMPT=0` for every arm; pinned by `test_insight_request_is_off_for_every_arm`). On any sc-* arm the Stop hook asked for an `INSIGHT:` line after the first code change, and headless that reply is the `result` event's text — every final-message regex read the insight, not the report; vanilla had no hook. Before the fix the mode fixtures scored 0–2/3 on diagnosis checks in both arms; after it 3/3. Earlier rounds' `output_regex` passes on sc arms carry the same caveat; they were not re-scored.
- **Parallel runs and copied credentials**: one session (opus r1 sc-full) ended `Not logged in · Please run /login` at turn 9 right after a second and third loop started; the harness copies `~/.claude/.credentials.json` per run, and a token refresh in one process can invalidate the copies. 1 of 24 parallel sessions; rerun from the spare budget. Sequential loops showed none.
- **Sequential by default**: one loop over 44 sessions would have taken ~40 min at ~50 s a session; split per model and per item, three processes finished in ~15 min.
