---
name: executing-plans
description: |
  Execute implementation plans with review checkpoints. Use when you have a written
  plan to implement. Follows plan tasks sequentially, runs verification at checkpoints,
  and delegates to subagents when available.
context: fork
---

# Executing Plans

Load the plan, review it critically, execute every task in order, and report when complete.

> I'm using the executing-plans skill to implement this plan.

When subagents are available, delegate discrete tasks via `/sc:agent` or `/sc:spawn` to improve quality and parallelism.

## The Process

### Step 1: Load and Review Plan

- Read the full plan document before touching any code.
- Review each task critically: are the steps clear, the dependencies correct, the scope reasonable?
- If the plan has gaps, contradictions, or risky assumptions, raise concerns with the user before proceeding.
- If the plan is sound, confirm readiness and move to execution.

### Step 2: Execute Tasks

For each task in the plan, in order:

1. Mark the task **in_progress**.
2. Follow the documented steps exactly as written.
3. Run any verification commands or checks specified for that task.
4. If verification passes, mark the task **completed** and move to the next.
5. If verification fails, diagnose the issue and retry. After two consecutive failures on the same verification, stop and ask.

Do not reorder tasks unless a dependency explicitly requires it.

### Step 3: Complete Development

- Announce that all plan tasks are finished.
- Hand off to the **verification-before-completion** skill for a final check.
- Summarize what was implemented, any deviations from the plan, and outstanding items.

## When to Stop and Ask

Pause execution and consult the user when:

- A blocker prevents progress (missing dependency, permission issue, environment problem).
- The plan has a critical gap that cannot be resolved by reading surrounding context.
- Instructions are ambiguous and choosing wrong could cause significant rework.
- The same verification step fails more than twice consecutively.

## When to Revisit Earlier Steps

- A later task reveals that a previous task was implemented incorrectly.
- Verification output shows a regression in previously completed work.
- New information changes the assumptions an earlier task was built on.

## Key Rules

1. **Review critically first** -- never start executing a plan you haven't fully read.
2. **Follow steps exactly** -- the plan author chose that order for a reason.
3. **Don't skip verifications** -- they exist to catch problems early.
4. **Stop when blocked** -- guessing through ambiguity wastes more time than asking.
5. **Never start work on main/master** without explicit user consent. If the current branch is main or master, confirm before making any changes.

## SuperClaude Integration

- Use `/sc:agent` and `/sc:spawn` commands to delegate independent subtasks to specialized agents.
- After all tasks are complete, hand off to the **verification-before-completion** skill for final validation.
