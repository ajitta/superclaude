---
name: writing-plans
description: |
  Create detailed implementation plans with bite-sized TDD tasks, exact file paths,
  complete code, and verification commands. Use when you have a spec or requirements
  for a multi-step task, before touching code.
---
<component name="writing-plans" type="skill">

  <role>
    <mission>Write comprehensive implementation plans with bite-sized tasks that include exact file paths, complete code, and verification commands</mission>
  </role>

  <when>
  - When you have a spec or requirements for a multi-step task
  - Before touching code — planning phase
  - After brainstorming has produced an approved spec
  </when>

  <flow>
    1. Announce — "I'm using the writing-plans skill to create the implementation plan."
    2. Map file structure — before defining tasks, list which files will be created or modified and what each is responsible for. In existing codebases, follow established patterns
    3. Write tasks — each step should be a single action (2-5 minutes). Use checkbox (`- [ ]`) syntax. Include exact file paths, complete code (not "add validation"), and exact commands with expected output
    4. Add plan header — every plan starts with the header template (see template below)
    5. Plan review loop — dispatch `plan-document-reviewer` subagent with crafted review context (not session history), providing chunk content and spec path. Fix issues and re-dispatch until approved, max 5 iterations before surfacing to human. Use `## Chunk N: <name>` headings, each chunk <=1000 lines
    6. Save — to `docs/plans/YYYY-MM-DD-<feature-name>.md` (user preferences override)
    7. Execution handoff — if subagents are available, use subagent-driven-development. Otherwise, hand off to executing-plans
  </flow>

  <template note="Plan header">
```markdown
# [Feature Name] Implementation Plan
> **For agentic workers:** REQUIRED: Use subagent-driven-development (if subagents available) or executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.
**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key technologies]
---
```
  </template>

  <template note="Task template">
````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**
````
  </template>

  <constraints>
  - Every step should include exact file paths and complete code
  - Reference relevant docs and skills with @ syntax
  - Reviewers are advisory — explain disagreements if you believe feedback is incorrect
  - If a spec covers multiple independent subsystems, suggest separate plans — one per subsystem
  </constraints>

  <bounds will="plan writing|task decomposition|file structure mapping|review coordination" wont="write implementation code|execute plan tasks|skip review loop"/>

  <handoff next="executing-plans subagent-driven-development"/>
</component>
