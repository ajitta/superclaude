---
status: approved-for-plan
revised: 2026-10-18
---

# Intent: retire the two measured modes, close the harness and finding-policy rows without sessions

Author: ajitta. Decisions were taken in chat on 2026-10-18.

## Problem

Original request:

> superclaude 다음 라운드 시작 — docs/features/purpose-boundary/03-handoff.md 읽고 후보 1(a)·2·4로 계획 구성·리뷰 후 제시. 세션 상한 0.

followed by "권고 대로" on every decision (Q1–Q7).

The purpose-boundary round measured `MODE_Task_Management.md` and `MODE_Orchestration.md` by ablation ([01-measurement.md §Item 2](../purpose-boundary/01-measurement.md)): n=6 sonnet, sc-full vs sc-no-modes — task-tool use 2/6 vs 0/6, batching 6/6 vs 5/6, every other check 0/6 in both arms. No sc-full run produced the mode's distinctive behavior (a phase-structured report, a `/sc:save` suggestion, a stated parallel plan). The readout kept both by its pre-fixed rule and handed the reading to the owner ([03-handoff.md item 1](../purpose-boundary/03-handoff.md)); the owner chose (a).

The owner's ultimate purpose, unchanged from [the reframing-anchoring intent](../reframing-anchoring/00-intent.md):

> 이게 나의 궁극적이며 최종적인 목적이다 '의도를 어떻게 인공지능이 인식하게 만드냐'

Content that does not produce its own behavior even when present is a cut on that axis.

## Proposed outcome

- Delete both modes with the full cascade; `--task-manage` and `--orchestrate` answer with a redirect notice (`RETIRED_FLAGS`, D5), never silence.
- Carry the one `MODE_Orchestration` bullet with no other home (Pipeline-Default) into `RULES_DELEGATION.md` `<workflow_delegation>`; every other bullet is already stated elsewhere (table in [01-decisions.md](./01-decisions.md)).
- Retire the `sc-no-modes` arm, the `mode-*` fixtures and tasks, and their test: the measurement they existed for is recorded and done.
- Close the `<finding_policy>` ×3 row as "keep, recorded" — delivery to subagents is unproven and cannot be proven under cap 0.
- Zero headless sessions. The round ends at merge-to-master; release (which needs `make canary-gates`, 4 sessions, because `core/` changes) waits for a round with a cap.

## Affected users and systems

- Users typing `--task-manage` / `--orchestrate`: one-line notice per prompt naming where the work went. The `tool.?select` keyword trigger disappears with the mode; `/sc:select-tool` is unaffected.
- `core/FLAGS.md` (two rows, two names), `core/rules/RULES_DELEGATION.md` (one bullet), `scripts/context_loader.py` (TRIGGER_MAP, VALID_FLAGS, RETIRED_FLAGS), README counts (8 → 6 modes), codex component map.
- Eval harness: one arm, two tasks, two fixture dirs, one test removed; `tool_called` / `parallel_tool_calls_min` check types stay (unused after this round).
- Installed copies: `find_unshipped` prunes `superclaude/modes/*.md` the source no longer ships on the next install.

## Constraints and decisions

| Question | Accepted decision |
|---|---|
| Q1 reading of "세션 상한 0" | R1 — zero headless sessions of any kind; no `make canary-gates`, so no release this round |
| Q2 item 4 (harness) | 4-A — delete arm, `NO_MODES_FILES`, fixtures, tasks, test, README row |
| Q3 item 2 (`<finding_policy>` ×3) | 2-A — keep, recorded; no `src/` change |
| Q4 branch / docs | `fix/mode-retire`, `docs/features/mode-retire/` |
| Q5 Pipeline-Default bullet | carry into `RULES_DELEGATION.md` `<workflow_delegation>` |
| Q6 redirect wording | "Task Management mode removed — in-session task tools and /sc:save cover it; /sc:task for a tracked hierarchy." / "Orchestration mode removed — /sc:select-tool and the core/FLAGS.md mcp section cover tool routing; --delegate / --concurrency for fan-out." |
| Q7 version at release | 4.29.1 (patch: the flags still answer; no command, hook or CLI surface changes) |

Reading adopted for the lean rule ("no deletion on 'the model already does this' without a measurement", [lean-round/00-intent.md](../lean-round/00-intent.md)): an ablation in which the mode's own instructed behaviors appear in 0/6 sc-full runs is the measurement. This overturns the purpose-boundary readout's Q8 `Keep` rows on the owner's reading, not on new data.

## Open questions

None at kickoff. Plan: `.hermes/plans/2026-10-18_233018-mode-retire-round.md` (v3; v1 and the reviewed v2 beside it, local to the machine).
