---
feature: mode-retire
phase: decisions
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 01. Decisions applied — carry-over, finding policy, harness

No headless session was used in this round. Line numbers are from `40746786` (the base) unless marked.

## Item 1(a) — `MODE_Orchestration` carry-over (the readout's unreached clause)

`02-readout.md:17` kept Orchestration because its second deletion clause — "unmeasured content carried elsewhere" — was never checked. Checked here, bullet by bullet, before the file was deleted:

| Mode content | Carried at | Action |
|---|---|---|
| `<behaviors>` Tool-Task Matching, Constraint-Adaptive | `core/FLAGS.md` `<mcp>` (routing per server; `--no-mcp` native fallback); `commands/select-tool.md` | none |
| `<behaviors>` Batching; `<thinking>` Parallel over Sequential | `core/FLAGS.md` `--concurrency`; measured at ceiling (batching 6/6 vs 5/6) | none |
| `<fan_out_execution>` Packet-Prompt | `core/rules/RULES_DELEGATION.md` `<delegate_packet>` | none |
| `<fan_out_execution>` Cap-Aware | `core/FLAGS.md` `--concurrency` ("does not change the harness's own limits on parallel subagents") | none |
| `<fan_out_execution>` Write-Return, Schema-vs-Evidence | `RULES_DELEGATION.md` `<workflow_delegation>` (the mode cited it) | none |
| `<fan_out_execution>` Context-Carry | `RULES_DELEGATION.md` `<delegate_packet>` ("sub-agents never receive context_loader/UserPromptSubmit injections… travels only if copied") | none |
| `<fan_out_execution>` Pipeline-Default | nowhere | **carried** as one bullet into `RULES_DELEGATION.md` `<workflow_delegation>` (Q5; +~200 B on an on-demand module, Workflow-tool-only block) |
| `<communication>` explain rationale / report parallel plan; `<examples>` | measured 0/6 in sc-full | dropped |

`MODE_Task_Management`: the task tools, `/sc:save` and `/sc:task` are commands and native tools; the hierarchy and checkpoint prose measured 0/6 (phase-structured report, `/sc:save` suggestion). Nothing to carry.

Fuzzy mis-route check for the two new `RETIRED_FLAGS` entries: highest difflib ratio of any surviving `VALID_FLAGS` name to `task-manage` is 0.40 (`safe-mode`), to `orchestrate` 0.42 (`delegate`); `RETIRED_FUZZY_CUTOFF` is 0.8.

Upgrade path: `install_paths.py` `find_unshipped` returns installed `superclaude/modes/*.md` the source no longer ships and `install_components.py` removes them — no retired-name list is needed (unlike `agents/`, which is shared with the user's own files). The repo's own local-scope install keeps the two files until `superclaude install --force --scope local` runs after the merge.

## Item 2 — `<finding_policy>` ×3: keep, recorded (2-A)

| Fact | Evidence |
|---|---|
| Three identical copies | `agents/self-review.md`, `security-engineer.md`, `quality-engineer.md` — [lean-round 03 §4](../lean-round/03-deferred-evidence.md) |
| No other path carries the text into a subagent | same §4: no hook, no `delegate_packet` field, `RULES_DELEGATION.md` only reaches the main loop |
| The text was load-bearing on an earlier model | `.claude/insights.jsonl:94` (2026-04-18, Opus 4.7): two sub-agents on identical buggy input, "only important" → 10 findings vs "report every" → 38; severity mix 2C/3H/3M/2L → 5C/7H/11M/9L/6 nits |
| Not measured on current models | no eval collects Agent-tool prompt text; a `delegate_packet` trace needs a new collector and sessions |

Closure: **keep the three copies**. Consolidating to one place changes delivery (a file the agent must `Read`, or a packet field the main loop must copy) and cannot be measured under cap 0; deleting needs a current-model measurement the repo rule requires. The item leaves the candidate list; it reopens only with a session budget for a delivery trace.

Not taken: a canonical copy in `.claude/rules/agent-authoring.md` plus a byte-identity test (2-B) — the copies have not drifted since April; a pin for drift that has not happened is code without a failure behind it.

## Item 4 — harness hygiene (4-A)

Removed: `sc-no-modes` from `ARMS`, `NO_MODES_FILES`, the arm branch in `_build_workspace`, the `mode-task-manage` / `mode-orchestrate` tasks, `evals/fixtures/mode-task-manage/`, `evals/fixtures/mode-orchestrate/`, `test_no_modes_arm_removes_exactly_the_two_deferred_modes`, the arm row in `evals/README.md` (a "retired arms" line records it). Kept: the `tool_called` and `parallel_tool_calls_min` check types and their unit tests — zero tasks use them now; a later round may remove them if still unused. Every full `--canary` run is 2 sessions shorter; `make canary-gates` names four other tasks and is unchanged.

Not taken: keeping the fixtures as plain canaries (4-B) — both sat at ceiling on success checks in both arms, and a canary without a recorded failure behind it guards nothing.

## Verification

Full `uv run pytest`, `tests/unit/scripts` run, `ruff format --check` / `ruff check` on `src tests evals`, `superclaude author-check` on `core/FLAGS.md` with `RULES.md` and `PRINCIPLES.md` (clean), CRLF check (clean), loader probe without a session (`superclaude hook context_loader` on `--task-manage` / `--orchestrate` prints one retired-flag notice each, no `<context-inject>`), red→green for the two new retired-flag tests. Pre-existing and not this round's: `author-check` reports X2 on `RULES_DELEGATION.md:63` (`</agent_routing>` "has no opening tag") at the base commit too — the opening tag's `note="… via <sub_agent_decision>"` attribute confuses the checker.
