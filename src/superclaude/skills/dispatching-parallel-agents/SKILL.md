---
name: dispatching-parallel-agents
description: |
  Dispatch multiple subagents concurrently for independent tasks. Use when facing
  2+ tasks that can be worked on without shared state or sequential dependencies.
  Manages context isolation between agents.
disable-model-invocation: true
---

# Dispatching Parallel Agents

Delegate tasks to specialized agents with isolated context. Each agent receives only the information it needs to complete its assignment. Craft instructions precisely --- never inherit session history. Agents cannot see each other's work until you integrate their results.

## When to Use

Parallel dispatch is the right choice when all of the following hold:

- There are **2 or more independent tasks** that do not depend on each other's output.
- Each task can be **understood in isolation** without requiring the full session context.
- There is **no shared mutable state** between the tasks (no overlapping files, no shared database rows being written).
- The combined work would take significantly longer if done sequentially.

**Do NOT use parallel dispatch when:**

- Failures across tasks are **causally related** --- fix the root cause first.
- You need **full system state** to reason about the problem (e.g., tracing a request across layers).
- Agents would **modify the same files** or compete for the same resources.
- The task is **exploratory** and the next step depends on what you discover in the current one.

## The Pattern

### Step 1: Identify Independent Domains

Before dispatching, decompose the work into non-overlapping units. Group by what is broken, what is needed, or what area of the codebase is involved.

Ask yourself for each pair of tasks: "If one agent fails completely, can the other still succeed?" If the answer is no, they are not independent.

Examples of good splits:
- Fix a CSS layout bug **and** add a new API endpoint
- Write unit tests for module A **and** write unit tests for module B
- Update documentation **and** refactor a utility function

Examples of bad splits:
- Fix the database schema **and** fix the queries that use that schema
- Refactor a shared utility **and** update all callers of that utility

### Step 2: Create Focused Agent Tasks

Each agent prompt must be self-contained. Write it as if the agent has never seen your conversation. Include:

1. **Scope** --- exactly which files, functions, or modules to touch. Be explicit about boundaries.
2. **Goal** --- what "done" looks like. State the acceptance criteria in concrete terms.
3. **Constraints** --- what the agent must not do. Prevent scope creep by naming the boundaries.
4. **Context** --- any relevant code snippets, error messages, or design decisions the agent needs. Copy them in; do not reference "the error we saw earlier."
5. **Expected output** --- what artifact the agent should produce (a commit, a diff, a test file, a summary).

### Step 3: Dispatch in Parallel

Launch all agents concurrently. Each runs in its own isolated context with no visibility into sibling agents.

Key principles during dispatch:

- Give each agent a **distinct working area** to avoid merge conflicts.
- If agents share read access to common files but write to different ones, that is acceptable.
- Set appropriate scope limits so agents do not wander beyond their assignment.
- Prefer smaller, well-defined tasks over large ambiguous ones.

### Step 4: Review and Integrate

Once all agents complete:

1. **Read each agent's summary** --- confirm the stated goal was achieved.
2. **Check for conflicts** --- look for overlapping file edits, incompatible changes, or divergent assumptions.
3. **Run the full test suite** --- individual agents may have passed their local tests but introduced cross-cutting regressions.
4. **Integrate deliberately** --- apply changes in a logical order. If conflicts exist, resolve them before proceeding.
5. **Validate the whole** --- the integrated result must be tested as a unit, not just as the sum of parts.

## Agent Prompt Structure

A well-crafted agent prompt has three qualities:

**Focused** --- It addresses exactly one problem. If you find yourself writing "also" or "and then," split into two agents.

**Self-contained** --- It includes every piece of information the agent needs. File paths are absolute. Error messages are quoted verbatim. Design decisions are stated, not implied.

**Specific about output** --- It names the deliverable. "Fix the bug" is vague. "Modify `src/auth/token.py` so that expired tokens return a 401 instead of a 500, and add a test in `tests/test_token.py` that verifies this behavior" is specific.

Template:

```
Task: [one-sentence summary]
Files: [list of files to read and/or modify]
Goal: [concrete acceptance criteria]
Constraints: [what not to touch, what not to change]
Context: [relevant code, errors, or decisions --- copied in full]
Output: [what to produce when done]
```

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Task scope too broad | Agent wanders, touches unrelated code, burns context | Narrow to one module or one bug |
| Missing context | Agent makes wrong assumptions, hallucinates file paths | Copy in all relevant snippets and paths |
| No constraints stated | Agent refactors beyond scope, breaks unrelated tests | Explicitly list what must not change |
| Vague expected output | Cannot tell if agent succeeded; integration is guesswork | Name the exact files and behaviors expected |
| Overlapping file writes | Merge conflicts, lost work, inconsistent state | Ensure each agent writes to distinct files |

## When NOT to Use

- **Related failures** --- If fixing bug A reveals that bug B has the same root cause, dispatch will produce two partial fixes instead of one correct one. Investigate first, then dispatch if the fixes truly diverge.
- **Exploratory debugging** --- When you do not yet know what is wrong, parallel agents will explore blindly. Use a single focused investigation first, then dispatch targeted fixes.
- **Shared mutable state** --- If two agents need to edit the same configuration file, the same database migration, or the same API contract, serialize them. Run one first, then dispatch the other with the updated state.
- **Small tasks** --- If the total work takes less than a few minutes sequentially, the overhead of crafting isolated prompts and integrating results outweighs the time saved.

## Verification Checklist

After integrating parallel agent results:

- [ ] Each agent's summary confirms its goal was met
- [ ] No file was modified by more than one agent
- [ ] Full test suite passes (not just individual agent tests)
- [ ] No unintended cross-cutting changes (imports, shared configs, package versions)
- [ ] Spot-check at least one agent's work in detail to verify quality
- [ ] Changes are committed in a logical grouping, not as disconnected patches

## SuperClaude Integration

Use the `/sc:spawn` command to dispatch parallel agents within SuperClaude. It handles context isolation and concurrent execution automatically.
