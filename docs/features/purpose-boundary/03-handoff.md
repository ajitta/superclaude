---
feature: purpose-boundary
phase: handoff
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 03. Handoff — what the next round starts from

State at handoff: `master` = `stable` = `v4.29.0` (`4c133ff7`), CI green, local-scope install synced with no drift. This round is closed: plan `.hermes/plans/2026-10-18_211158-handoff-round.md` (v3, local to the machine), measurement in [01-measurement.md](./01-measurement.md), readout in [02-readout.md](./02-readout.md). Headless sessions used: 65 (cap 52 raised in chat). A new round needs its own cap.

## Candidates, each with its evidence already written

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | `MODE_Task_Management.md`, `MODE_Orchestration.md` deletion | public routing change (two flags retire) | [01 §Item 2](./01-measurement.md): n=6 sonnet, sc-full vs sc-no-modes — task-tool use 2/6 vs 0/6, batching 6/6 vs 5/6, every other check 0/6 in both arms; no sc-full run produced a phase-structured report, a `/sc:save` suggestion or a stated parallel plan | a **decision**, not a measurement: (a) read "the mode's own behaviors appear 0/6 even with the text" as the lean rule's measurement and delete; (b) write a sharper fixture (what would it check that these did not?). Recommendation recorded at the first readout: (a) |
| 2 | `<finding_policy>` ×3 → one place | delivery to native subagents unproven | [lean-round 03 §4](../lean-round/03-deferred-evidence.md) | the harness collects Bash/PowerShell inputs and tool names, not Agent-tool prompt text — a `delegate_packet` trace needs a new collector. Without it the only closure is "keep", recorded |
| 3 | `RULES_QUALITY.md` vs the 8K budget on `/sc:analyze --delegate` | rule removal or budget default change | [lean-round 03 §7](../lean-round/03-deferred-evidence.md) | whether ~280 tokens of `RULES_INTERACTION` change a `--delegate` analysis — low discriminability; the alternative is a code change to the default budget |
| 4 | Mode fixtures' unused evidence checks | harness hygiene | [01 §Item 2](./01-measurement.md): phase/checkpoint, `/sc:save` and concurrency-rationale regexes are 0/12 across both arms | drop or keep as floor probes; a check that never passes measures nothing. Decide together with item 1 |

## Item 1 cascade, if (a) is chosen (session cost 0; patch release)

Verified on `4c133ff7`:

| Site | Change |
|---|---|
| `src/superclaude/modes/MODE_Task_Management.md`, `MODE_Orchestration.md` | delete |
| `src/superclaude/scripts/context_loader.py:157` (`--task-manage`), `:163` (`--orchestrate\|tool.?select\|/sc:select-tool`) | remove the TRIGGER_MAP rows — `tests/unit/test_content_usage.py:5-7` pins both directions |
| `context_loader.py:351-352` `VALID_FLAGS` | remove `task-manage`, `orchestrate` |
| `context_loader.py:391` `RETIRED_FLAGS` | add both with a redirect (D5: retired flags answer with a notice, never silence), e.g. "Task Management mode removed — in-session task tools and /sc:save cover it", "Orchestration mode removed — /sc:select-tool and core/FLAGS.md mcp section cover it"; two tests in the `tests/unit/test_context_loader.py:642` pattern |
| `src/superclaude/core/FLAGS.md:7,12,13` | drop the two rows and the names in the "read it from modes/" list |
| `README.md:27` (`**8**`), `:32` ("8 behavioral modes"), `:407` ("8 adaptive modes"), `:411`, `:413` | 8 → 6; two bullets out — `tests/unit/test_version_consistency.py:223` count pattern |
| `src/superclaude/modes/README.md:19-20` | two rows out |
| `.claude/rules/mode-authoring.md:85` | naming example uses `MODE_Task_Management.md` — swap for a surviving mode |
| `evals/run_eval.py` `NO_MODES_FILES`, `sc-no-modes` arm, `evals/fixtures/mode-*`, `tests/unit/test_eval_harness.py::test_no_modes_arm_removes_exactly_the_two_deferred_modes` | retire the arm (the files it deletes no longer exist) or keep the fixtures as plain canaries without the arm; decide, do not leave a dangling `unlink` |
| `CHANGELOG.md` `[Unreleased]` Removed | "retired with redirect notice", name both flags and where their work went |

`/sc:select-tool` keeps working: its trigger reached the mode only through the loader regex at `:163`; the command file does not name it.

## Small leftovers deliberately not done

The lean round's list stands (`frozenset` rewrites, Makefile help from `##` comments, CI `curl | sh` → `setup-uv`, `tests/unit/scripts` exclusion, in-function test imports). New this round: `tests/unit/test_command_structure.py` passes on a frontmatter `description` whose `: ` breaks YAML (only `superclaude author-check` catches it — F1); a test that parses every command's frontmatter with `yaml.safe_load` would close it.

## How a new session starts a round

1. `git fetch`, confirm `master` = `origin/master` (= `stable` after a release), `git status` clean except untracked `.hermes/`, `.ignore`.
2. Read this file; read the evidence sections only for the items the owner picks. A request written as "후보 중 [번호]" wants the candidate table and a recommendation first, then a split (measure / cleanup / decide-only / defer) and a session cap, before any plan.
3. Plan per the maintenance skill's `references/audit-planning.md`: numbered decisions in chat (never a form), one independent reviewer pass (terminal/read_file only — `execute_code` in a child blocks on a consent prompt), then v2.
4. Kickoff on the owner's word: branch (`feature/` when a rule or arm is added, `fix/` otherwise), `docs/features/<slug>/00-intent.md` in the owner's words, decisions as a table at the top.
5. Eval runs: one background process per model or item with its own `--runs-dir` prefix, never one loop over everything; keep 2–4 spare sessions for `Not logged in` reruns; aggregate `results.json` per (task, arm, check) and list changed files per workspace. The insight request is already off in the harness.
6. Commit per batch by explicit path; merge, push and release only on request.

## Lessons recorded this round (in the Hermes skill `superclaude-repo-maintenance`)

Parallel eval loops and the credential-copy hazard; the Stop hook's `INSIGHT:` line replacing the final report in headless runs; `parallel_tool_calls_min` summed per `message.id`; `grep $'\r'` false positives in git-bash; `: ` in an unquoted description; the `[번호]` request shape.
