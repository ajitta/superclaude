---
name: requesting-code-review
description: |
  Dispatch a subagent reviewer with the context needed to review completed work.
  Use when completing tasks, implementing features, or before merging.
context: fork
---

## Purpose

Request a structured code review by dispatching a reviewer subagent with the right context about what changed and why.

## When to Use

- After completing a discrete task or feature
- Before merging any branch into `integration` or `master`
- After resolving a complex bug touching multiple files
- Optionally: when stuck on a design decision or working in unfamiliar code

## Workflow

1. **Get the diff range**: Identify BASE_SHA and HEAD_SHA covering your work. Use `git log --oneline BASE_SHA..HEAD_SHA` to confirm the range is correct.
2. **Gather context**: Collect changed files, their purpose, the original requirements or plan, and current test results.
3. **Dispatch reviewer**: Send a `self-review` subagent (or use `/sc:review`) with: what was implemented, the plan/requirements, the commit range, and a brief description.
4. **Keep context clean**: The reviewer should receive the final result and requirements — not your false starts or abandoned approaches.
5. **Triage feedback by severity**:
   - **Critical**: Fix immediately before any other work.
   - **Important**: Address before moving to the next task.
   - **Minor**: Note for later, batch with related work.
   - **Style**: Apply if you agree, skip if subjective.
6. **Fix and re-request if needed**: After addressing Critical or Important items, request another review pass if the changes were substantial.

## Constraints

- Do not skip review because "it's a small change" — small changes in critical paths cause outages.
- Do not request review before the work compiles and tests pass.
- Do not ignore Critical feedback — if you disagree, respond with evidence.

## Completion

Reviewer feedback is received, triaged, and addressed. Critical and Important items are resolved.

## Next

After receiving feedback, follow the `receiving-code-review` skill to process and act on comments.
