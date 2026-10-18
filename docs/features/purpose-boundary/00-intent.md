---
status: approved-for-plan
revised: 2026-10-18
---

# Intent: close the measured purpose-boundary gap, then settle the lean leftovers

Author: ajitta. Decisions were taken in chat on 2026-10-18.

## Problem

Original request:

> superclaude 다음 라운드 시작 — docs/features/lean-round/06-handoff.md 읽고 후보 중 [번호]로 계획 구성·리뷰 후 제시

followed by "모두 진행하려고 하는데, 너의 권고는?" and, on the recommended split, "52로 올려" (session cap).

The lean round closed with [nine candidates](../lean-round/06-handoff.md). One of them sits on the owner's own axis and has a measured gap behind it: on the shipped kernel, `action-vs-purpose-code` passes 6/15 while the pilot's candidate arm passed 5/6 ([05-release-gate.md](../lean-round/05-release-gate.md)). Every miss has one shape — the cause (env-var mismatch) is named, retry is added, the env value is not corrected. The rest of the list is deletions and consolidations the lean round refused to make without measurement, plus cleanup that needs none.

The owner's ultimate purpose, unchanged from [the reframing-anchoring intent](../reframing-anchoring/00-intent.md):

> 이게 나의 궁극적이며 최종적인 목적이다 '의도를 어떻게 인공지능이 인식하게 만드냐'

## Proposed outcome

- Re-measure the `purpose_before_action` fix-vs-propose boundary with one candidate sentence, sc-full vs sc-candidate on the same day, and ship it into `core/RULES.md` only when the pre-fixed criterion is met.
- Measure the two deferred modes by ablation (`sc-full` vs `sc-no-modes`) on fixtures whose checks the mode text could actually change, and delete per the pre-fixed criterion.
- Apply the no-measurement cleanup: `.gitignore` duplicates, MCP body trim per the authoring rule, init-pair cross-links, `commands/sc.md` removal.
- Record every decision here; report measured results, not estimated savings.

## Affected users and systems

- `core/RULES.md` (every session) if the rule ships; `modes/` and the loader's flag roster if a mode is deleted; `commands/` roster and README counts for the dispatcher removal.
- The eval harness (`evals/run_eval.py`, `tasks.yaml`, `tests/unit/test_eval_harness.py`): one new arm, two check types, two fixtures.
- Users of `--verbose-context` (MCP body trim is visible only there) and of `--task-manage` / `--orchestrate` (retired with a redirect notice if deleted).

## Constraints and decisions

| Question | Accepted decision |
|---|---|
| Scope | Measure items 7 and 2; clean up 9, 3 (MCP bodies only), 5; decide 1 and 8; defer 4, 6 and `RESEARCH_CONFIG.md` deletion. |
| Session cap | 52 headless sessions (32 item 7 + 12 item 2 + 4 canary-gates + 4 spare). Sonnet and Opus only; no headless Fable. |
| Q1 branch | `feature/purpose-boundary` from `master` `a0b7fc9a`. |
| Q2 candidate wording | A — one sentence appended after the boundary sentence: a value the failing call read belongs to the files the error names wherever it is defined; correcting it there is inside the boundary when the edit is reversible. Insertion only; no existing sentence changes. |
| Q3 item 7 cells | `action-vs-purpose-code` × {sc-full, sc-candidate} × {sonnet, opus} × 4 runs = 32, both arms in the same batch. |
| Q4 harness | Add `parallel_tool_calls_min` (tool_use blocks summed per `message.id` — stream-json emits one `assistant` event per block), `tool_called`, and tool-name collection in `_parse_stream`; each red→green. |
| Q5 `commands/sc.md` | Delete. The owner used `/sc:sc` to look up a command's flags; `/sc:help <command-name>` already returns the command's syntax, flags and "Not for" line, and `/sc:help --flags` the FLAGS.md list. CHANGELOG names the replacement. |
| Q6 `memory_guide` header, `<role>`/`<does>` overlap | No change. Both are pinned by tests and authoring rules; no saving is at stake. Closed. |
| Q7 ship criterion | Per model, sc-candidate minus sc-full on the `sync succeeds` check ≥ +2 (each /4), and sc-candidate total ≥ 6/8. Not a statistical test; an accepted threshold at n=4. |
| Q8 mode deletion | Sonnet, n=3 per cell. Task_Management: delete when every check is equal across arms. Orchestration: delete when the measurable axes (batching, selection rationale) show no difference AND the unmeasured content is carried by always-loaded files (`core/FLAGS.md` mcp section; `RULES_DELEGATION.md`). Flags move to `RETIRED_FLAGS` with a redirect, never silently vanish. |

Additional constraints:

- The lean round's rule stands: no deletion on "the model already does this" without a measurement whose checks the content could have changed. The ablation fixtures therefore grant the task tools (`TodoWrite`, `TaskCreate`, `TaskUpdate`) and count parallel tool calls per message; the Orchestration routing and `<fan_out_execution>` sections cannot be reached in a headless eval (no MCP servers, no Workflow tool — the latter condition was added by the prompt-content audit, `03b-analysis-modes.md:26`, already applied at `MODE_Orchestration.md:24`).
- The miss mechanism ("the boundary sentence is read as a file-name test") is a hypothesis among the three candidate causes in `05-release-gate.md:37`; the same-day sc-full control is its test. The measurement report separates misses that mention `nightly.env` and still do not fix it from misses that never find it.
- Commit per batch by explicit path; `.gitignore` is in scope this round (item 9) and is committed on its own.
- Merge, push, canary-gates and release are separate instructions. If the rule ships the next version is 4.29.0 (kernel change, precedent 4.28.0); otherwise 4.28.3.

## Open questions

None at kickoff. The readout (`02-readout.md`) applies Q7 and Q8 mechanically; a result that fits neither branch (e.g. the candidate improves one model and regresses the other) comes back as a question.
