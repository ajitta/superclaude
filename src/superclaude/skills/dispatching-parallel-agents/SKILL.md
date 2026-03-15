---
name: dispatching-parallel-agents
description: |
  Dispatch multiple subagents concurrently for independent tasks. Use when facing
  2+ tasks that can be worked on without shared state or sequential dependencies.
  Manages context isolation between agents.
disable-model-invocation: true
---

## Purpose

Delegate independent tasks to parallel agents with isolated context, then integrate their results.

## Workflow

1. **Identify independent tasks.** Decompose work into non-overlapping units. Two tasks are independent if one agent failing completely would not prevent the other from succeeding.
2. **Craft focused agent prompts.** Each prompt should be self-contained — include scope (specific files/modules), goal (concrete acceptance criteria), constraints (what not to touch), and all relevant context (code snippets, error messages copied verbatim). Do not reference session history.
3. **Dispatch agents in parallel.** Give each agent a distinct working area to avoid merge conflicts. Prefer smaller, well-defined tasks over large ambiguous ones.
4. **Review results.** Confirm each agent met its stated goal. Check for overlapping file edits or incompatible changes.
5. **Integrate and verify.** Apply changes in logical order, resolve any conflicts, then run the full test suite on the integrated result.

## Constraints

- Do not dispatch parallel agents for related failures that likely share a root cause — investigate first.
- Do not dispatch when agents would need to edit the same files.
- Do not skip the integration test suite — individual agent tests passing does not guarantee the combined result works.
- If an agent fails, retry with an adjusted prompt or different model before escalating.

## Completion

All agent results have been integrated, the full test suite passes, and changes are committed in a logical grouping.

## Next

Use `/sc:spawn` to dispatch parallel agents within SuperClaude. Pairs with **using-git-worktrees** when each agent needs its own workspace.
