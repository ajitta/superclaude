---
name: requesting-code-review
description: |
  Dispatch a subagent reviewer with precisely crafted context to review completed work.
  Use when completing tasks, implementing features, or before merging. Provides the
  reviewer exactly the context needed without session history leakage.
context: fork
---

# Requesting Code Review

## Overview

When work is complete, dispatch a reviewer subagent with a purpose-built context payload. The reviewer should receive only the information it needs to evaluate the changes — not your entire session history. Craft the review request so the reviewer can operate independently, with clear boundaries around what changed and why.

## When to Request Review

### Mandatory

- After completing each discrete task or user story
- After implementing a major feature or architectural change
- Before merging any branch into `integration` or `master`
- After resolving a complex bug where the fix touches multiple files

### Optional

- When stuck on a design decision and want a second perspective
- Before starting a large refactor, to validate the approach
- When making changes in unfamiliar areas of the codebase
- After performance-sensitive changes

## How to Request

### Step 1: Gather Change Boundaries

Identify the exact commit range that covers your work:

```
BASE_SHA = commit before your first change
HEAD_SHA = your latest commit (usually HEAD)
```

Use `git log --oneline BASE_SHA..HEAD_SHA` to confirm the range captures all relevant commits and nothing extraneous.

### Step 2: Dispatch the Reviewer Subagent

Provide these four pieces of context — no more, no less:

| Field | Content |
|-------|---------|
| **WHAT_WAS_IMPLEMENTED** | Concrete summary of changes made. List files touched and the purpose of each change. |
| **PLAN_OR_REQUIREMENTS** | The original task description, acceptance criteria, or plan that drove the work. |
| **BASE_SHA** | The commit SHA before your first change. |
| **HEAD_SHA** | The commit SHA of your final change. |

The reviewer uses `git diff BASE_SHA..HEAD_SHA` to inspect the actual changes. Your summary in WHAT_WAS_IMPLEMENTED helps the reviewer orient quickly, but the diff is the source of truth.

### Step 3: Do Not Leak Session Context

The reviewer should not inherit your reasoning, false starts, or abandoned approaches. If you tried three implementations before settling on one, the reviewer only needs to see the final result plus the requirements it should satisfy.

## Acting on Feedback

### Severity-Based Response

| Severity | Action | Timing |
|----------|--------|--------|
| **Critical** | Fix immediately, do not proceed with other work | Before any other changes |
| **Important** | Address before moving to next task | Before proceeding |
| **Minor** | Note for later, batch with related work | Next convenient opportunity |
| **Style** | Apply if you agree, skip if subjective | At your discretion |

### Disagreeing with Feedback

If feedback is incorrect or missing context, push back with evidence. Show the reviewer what they missed — a test that covers the case, a constraint they were not aware of, or a deliberate tradeoff documented in the plan. Do not silently ignore feedback.

## Integration with Workflows

**Subagent-driven development**: After each implementation subagent completes its work, the orchestrator dispatches a review subagent before accepting the result.

**Executing plans**: Review at each milestone boundary, not only at the end. Catching issues early in a multi-step plan prevents cascading rework.

**Ad-hoc work**: Even single-file fixes benefit from review when they touch critical paths (auth, payments, data migration).

## Red Flags

- Never skip review because "it's a small change" — small changes in critical paths cause outages
- Never ignore Critical severity feedback — if you disagree, respond with evidence, but do not proceed without resolution
- Never request review before the work compiles and tests pass — the reviewer's job is correctness and design, not catching syntax errors
- Never dump your entire session as context — curate what the reviewer needs

## SuperClaude Integration

Use `/sc:review` to initiate a structured review workflow. The `self-review` agent can serve as the reviewer subagent for automated review passes.

Handoff: after receiving reviewer feedback, follow the `receiving-code-review` skill for how to process and act on comments.
