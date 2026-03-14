---
name: writing-plans
description: |
  Create detailed implementation plans with zero-context assumption. Use when you have
  a spec or requirements for a multi-step task, before touching code. Produces bite-sized
  TDD tasks with exact file paths, code, and verification commands.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming zero codebase context. Every plan must be self-contained: a developer with no prior knowledge should be able to execute it start to finish.

Principles:
- **Zero-context assumption** -- document every file path, every import, every command
- **Bite-sized tasks** -- each step is one discrete action (2-5 minutes)
- **TDD always** -- write the test first, watch it fail, implement, watch it pass
- **DRY / YAGNI** -- no speculative abstractions, no duplicated logic
- **Frequent commits** -- commit after each passing test or logical unit

## Announcement

> I'm using the writing-plans skill to create the implementation plan.

## Output Location

Save plans to: `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

Create the directory if it does not exist.

## Scope Check

Before writing, assess the spec:
- If the spec covers **multiple independent subsystems**, suggest breaking into separate plans
- Each plan should target one cohesive feature or subsystem
- Ask the user before splitting: "This spec spans X and Y. Separate plans recommended. Proceed?"

## Step 1: Map the File Structure

Before writing any tasks, map every file that will be created or modified.

- List each file with its purpose and responsibility
- One responsibility per file -- no god-files
- Follow existing project patterns (naming, directory structure, imports)
- Mark files as `[new]` or `[modify]`

Example:
```
src/auth/token.py       [new]    -- JWT token generation and validation
src/auth/middleware.py   [modify] -- Add token verification to request pipeline
tests/unit/test_token.py [new]   -- Token generation/validation unit tests
```

## Step 2: Write Bite-Sized Tasks

Each task is one action a developer can complete in 2-5 minutes.

Granularity pattern:
1. Write test for behavior X
2. Run test -- confirm it fails
3. Implement behavior X
4. Run test -- confirm it passes
5. Commit: `test: add X` / `feat: implement X`

Never combine "implement + test" into a single step. Never say "add appropriate tests." Be explicit.

## Plan Document Template

Every plan starts with this header:

```markdown
# Plan: <Feature Name>

**Date**: YYYY-MM-DD
**Status**: Draft | In Progress | Complete

## Goal
One sentence describing what this plan delivers.

## Architecture Decisions
- Key decision 1 and rationale
- Key decision 2 and rationale

## Tech Stack
- Language/framework versions
- Dependencies to add (with exact versions)

## File Map
| File | Action | Responsibility |
|------|--------|----------------|
| path/to/file.py | new | What it does |
```

## Task Structure Template

Each task follows this format:

```markdown
### Task N: <Short Description>

**Files**: `path/to/file.py`

**Steps**:
- [ ] Step 1: Write/modify specific code
- [ ] Step 2: Run verification command
- [ ] Step 3: Commit with message

**Run**:
\`\`\`bash
uv run pytest tests/unit/test_feature.py::test_name -v
\`\`\`

**Expected**: Test passes (green) / Output matches X
```

## Key Rules

- **Exact file paths** -- always absolute or project-relative, never "the auth file"
- **Complete code** -- show the full function/class, not "add validation here"
- **Exact commands** -- `uv run pytest tests/unit/test_token.py -v`, not "run the tests"
- **DRY** -- if two tasks share logic, extract it first in a prior task
- **YAGNI** -- only plan what the spec requires, nothing speculative
- **TDD** -- every implementation step has a preceding test step
- **Commit points** -- mark explicit commit boundaries with conventional messages

## Plan Review Loop

After drafting the full plan:

1. Re-read each task for completeness (paths, code, commands all present?)
2. Check ordering -- does each task only depend on previously completed tasks?
3. Verify no missing steps between "write test" and "implement"
4. Confirm commit messages follow conventional format
5. If issues found, fix and re-review (max 5 iterations)

## Execution Handoff

When the plan is complete and saved:

> Plan complete and saved to `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`. Ready to execute?

If the user confirms, invoke the **executing-plans** skill to begin implementation.

## SuperClaude Integration

- Use `/sc:workflow` to coordinate multi-phase execution
- Use `/sc:task` for individual task tracking
- Handoff: **executing-plans** skill for implementation phase
