# Content Framework Upgrade Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port 12 process skills from obra/superpowers into superclaude, making skills the process backbone while commands/agents serve as tools.

**Architecture:** Each skill is a `SKILL.md` file in `src/superclaude/skills/<name>/` with superclaude YAML frontmatter + superpowers-compatible plain markdown body. Skills install to `~/.claude/skills/` via `superclaude install`. Workflow chain (brainstorm -> plan -> execute -> verify) enforced via rules in `core/RULES.md`.

**Tech Stack:** Markdown (YAML frontmatter), Python (pytest, click CLI), UV package manager

**Spec:** `docs/superpowers/specs/2026-03-15-superclaude-content-framework-upgrade-design.md`

---

## Task 0: Branch Setup

- [ ] **Create feature branch**

```bash
git checkout -b feature/content-framework-upgrade
```

---

## File Structure

### New Files (12 skills)
```
src/superclaude/skills/brainstorming/SKILL.md
src/superclaude/skills/writing-plans/SKILL.md
src/superclaude/skills/verification-before-completion/SKILL.md
src/superclaude/skills/executing-plans/SKILL.md
src/superclaude/skills/test-driven-development/SKILL.md
src/superclaude/skills/systematic-debugging/SKILL.md
src/superclaude/skills/requesting-code-review/SKILL.md
src/superclaude/skills/receiving-code-review/SKILL.md
src/superclaude/skills/finishing-a-development-branch/SKILL.md
src/superclaude/skills/dispatching-parallel-agents/SKILL.md
src/superclaude/skills/using-git-worktrees/SKILL.md
src/superclaude/skills/using-superclaude/SKILL.md
```

### New Command (Phase 3 prerequisite)
```
src/superclaude/commands/review.md
```

### Modified Files
```
src/superclaude/core/RULES.md           ← workflow gates + skill priority rules
src/superclaude/execution/parallel.py   ← deprecation header
src/superclaude/execution/reflection.py ← deprecation header
src/superclaude/execution/self_correction.py ← deprecation header
CLAUDE.md                               ← update skill count (3 → 15)
```

### Deleted Files (Phase 5)
```
src/superclaude/commands/git.md         ← Claude Code native duplicate
```

### Compressed Files (Phase 5)
```
src/superclaude/commands/recommend.md   ← 8,428 → ~3,000 tokens
src/superclaude/commands/pm.md          ← 5,106 → ~1,100 tokens (brief reference)
src/superclaude/commands/improve.md     ← merge into skills
src/superclaude/commands/reflect.md     ← absorbed by verification skill
```

---

## Chunk 1: Phase 1 — Foundation (3 skills + rules)

### Task 1: Create brainstorming skill

**Files:**
- Create: `src/superclaude/skills/brainstorming/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/brainstorming/SKILL.md` (superpowers source)
- Reference: `src/superclaude/skills/confidence-check/SKILL.md` (existing skill for frontmatter pattern)
- Reference: `.claude/rules/skill-authoring.md` (authoring rules)

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p src/superclaude/skills/brainstorming
```

- [ ] **Step 2: Write SKILL.md**

Create `src/superclaude/skills/brainstorming/SKILL.md` with:

**Frontmatter** (superclaude convention):
```yaml
---
name: brainstorming
description: |
  Design-first exploration before any implementation. Use before creating features,
  building components, adding functionality, or modifying behavior. Explores user intent,
  requirements and design through collaborative dialogue before writing code.
---
```

**Body**: Port the superpowers brainstorming skill content. Key elements to include:
- Hard gate: NO implementation until design approved
- Checklist: explore context -> ask questions -> propose approaches -> present design -> write spec -> review loop
- Process flow (text description, not graphviz)
- One question at a time rule
- YAGNI ruthlessly
- Design for isolation and clarity
- After design: write spec to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Terminal state: invoke writing-plans skill

**Superclaude additions** (clearly marked):
- Reference `/sc:brainstorm` command for context exploration
- Reference `requirements-analyst` agent for spec validation
- Handoff: `writing-plans` skill

Keep body under 500 lines. Target ~800-1000 tokens.

- [ ] **Step 3: Validate frontmatter**

Verify: `name` matches directory, `description` > 10 chars with task keywords, no forbidden fields (`context`, `agent` not needed for inline skill).

- [ ] **Step 4: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

Expected: all existing tests pass, new skill detected and validated.

---

### Task 2: Create writing-plans skill

**Files:**
- Create: `src/superclaude/skills/writing-plans/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/writing-plans/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p src/superclaude/skills/writing-plans
```

- [ ] **Step 2: Write SKILL.md**

**Frontmatter**:
```yaml
---
name: writing-plans
description: |
  Create detailed implementation plans with zero-context assumption. Use when you have
  a spec or requirements for a multi-step task, before touching code. Produces bite-sized
  TDD tasks with exact file paths, code, and verification commands.
---
```

**Body**: Port the superpowers writing-plans skill. Key elements:
- Zero-context assumption (engineer knows nothing about codebase)
- File structure mapping before tasks
- Bite-sized tasks (2-5 min each step)
- Plan document header template
- Task structure template (Files, Steps with checkboxes, Run commands, Expected output)
- DRY, YAGNI, TDD, frequent commits
- Save plans to `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- Execution handoff: invoke executing-plans skill

**Superclaude additions**:
- Reference `/sc:workflow` and `/sc:task` commands
- Handoff: `executing-plans` skill

Target ~800-1000 tokens.

- [ ] **Step 3: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 3: Create verification-before-completion skill

**Files:**
- Create: `src/superclaude/skills/verification-before-completion/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/verification-before-completion/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p src/superclaude/skills/verification-before-completion
```

- [ ] **Step 2: Write SKILL.md**

**Frontmatter**:
```yaml
---
name: verification-before-completion
description: |
  Evidence-first verification before any completion claims. Use before committing,
  creating PRs, or claiming work is done. Requires running verification commands and
  confirming output before making success claims. No shortcuts for verification.
---
```

**Body**: Port the superpowers verification-before-completion skill. Key elements:
- The Iron Law: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
- The Gate Function (5 steps: identify, run, read, verify, claim)
- Common failures table (claim -> requires -> not sufficient)
- Red flags (should, probably, expressing satisfaction before verification)
- Rationalization prevention table
- Key patterns (tests, regression, build, requirements, agent delegation)

**Superclaude additions**:
- Reference `self-review` agent for post-implementation validation
- Reference `/sc:analyze` for comprehensive verification

Target ~800-1000 tokens.

- [ ] **Step 3: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 4: Update core/RULES.md with workflow gates

**Files:**
- Modify: `src/superclaude/core/RULES.md`

- [ ] **Step 1: Read current RULES.md**

```bash
cat src/superclaude/core/RULES.md
```

- [ ] **Step 2: Add workflow gates section**

Add before `</component>` closing tag:

```xml
  <workflow_gates note="Process skill chain — enforce progression">
    brainstorming -> writing-plans: User must approve spec before planning
    writing-plans -> executing-plans: Plan document must be committed to repo
    executing-plans -> verification: All plan tasks must be marked complete
    verification -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>

  <skill_priority note="Process skills activate BEFORE implementation">
    1. brainstorming (any creative/feature work)
    2. systematic-debugging (any bug/failure)
    3. test-driven-development (any implementation)
    4. verification-before-completion (any completion claim)
  </skill_priority>
```

- [ ] **Step 3: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v
```

---

### Task 5: Verify install_paths.py handles new skills

**Files:**
- Read: `src/superclaude/cli/install_paths.py`
- Read: `src/superclaude/cli/install_components.py`

- [ ] **Step 1: Check if skills component auto-discovers subdirectories**

Read `install_paths.py` and `install_components.py` to verify the `"skills"` COMPONENTS entry copies all subdirectories (not a hardcoded list).

The current COMPONENTS entry is:
```python
"skills": ("skills", "skills", "Skills"),
```

This maps `src/superclaude/skills/` -> `~/.claude/skills/`. If the install logic copies the entire directory tree (not specific files), new skill directories will be auto-discovered. Verify this by reading `install_components.py`.

- [ ] **Step 2: Test installation**

```bash
superclaude install --list-all
```

Verify new skills appear in the listing.

- [ ] **Step 3: Test actual install**

```bash
superclaude install --scope user --force
```

Verify `~/.claude/skills/brainstorming/SKILL.md` exists.

---

### Task 6: Phase 1 commit

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

Expected: all existing tests pass + new skills detected.

- [ ] **Step 2: Commit**

```bash
git add src/superclaude/skills/brainstorming/ src/superclaude/skills/writing-plans/ src/superclaude/skills/verification-before-completion/ src/superclaude/core/RULES.md
git commit -m "feat: add Phase 1 process skills (brainstorming, writing-plans, verification)"
```

---

## Chunk 2: Phase 2 — Execution Skills (3 skills)

### Task 7: Create executing-plans skill

**Files:**
- Create: `src/superclaude/skills/executing-plans/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/executing-plans/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p src/superclaude/skills/executing-plans
```

- [ ] **Step 2: Write SKILL.md**

**Frontmatter**:
```yaml
---
name: executing-plans
description: |
  Execute implementation plans with review checkpoints. Use when you have a written
  plan to implement. Follows plan tasks sequentially, runs verification at checkpoints,
  and delegates to subagents when available.
context: fork
---
```

**Body**: Port superpowers executing-plans skill. Key elements:
- Read plan document first
- Execute tasks in order (checkbox tracking)
- Review checkpoints between chunks
- Verification at each checkpoint (run tests, check output)
- Subagent delegation when available

**Superclaude additions**:
- Reference `/sc:agent` and `/sc:spawn` commands for delegation
- Handoff: `verification-before-completion` skill

- [ ] **Step 3: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 8: Create test-driven-development skill

**Files:**
- Create: `src/superclaude/skills/test-driven-development/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/test-driven-development/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p src/superclaude/skills/test-driven-development
```

- [ ] **Step 2: Write SKILL.md**

**Frontmatter**:
```yaml
---
name: test-driven-development
description: |
  Enforce RED-GREEN-REFACTOR cycle for all feature and bugfix implementation.
  Use before writing any implementation code. Write failing test first, then
  minimal code to pass. No production code without a failing test.
---
```

**Body**: Port superpowers TDD skill. Key elements:
- The Iron Law: NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
- Red-Green-Refactor cycle (text description)
- RED: write one minimal failing test
- Verify RED: run and confirm correct failure
- GREEN: minimal code to pass
- Verify GREEN: run and confirm pass
- REFACTOR: clean up while staying green
- Good vs Bad test examples (use Python since superclaude is Python-focused)
- Common rationalizations table
- Red flags list
- Verification checklist

**Superclaude additions**:
- Reference `/sc:test` command and `quality-engineer` agent
- Use `uv run pytest` instead of `npm test` in examples
- Handoff: `verification-before-completion` skill

- [ ] **Step 3: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 9: Create systematic-debugging skill

**Files:**
- Create: `src/superclaude/skills/systematic-debugging/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/systematic-debugging/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p src/superclaude/skills/systematic-debugging
```

- [ ] **Step 2: Write SKILL.md**

**Frontmatter**:
```yaml
---
name: systematic-debugging
description: |
  Four-phase root cause investigation before proposing any fix. Use when encountering
  bugs, test failures, or unexpected behavior. Requires hypothesis generation, evidence
  gathering, and verification before implementing fixes.
---
```

**Body**: Port superpowers systematic-debugging skill. Key elements:
- Four phases: Observe, Hypothesize, Test, Fix
- Phase 1 (Observe): gather symptoms, reproduce, collect evidence
- Phase 2 (Hypothesize): generate 3+ hypotheses ranked by simplicity
- Phase 3 (Test): falsify hypotheses systematically
- Phase 4 (Fix): implement fix with regression test (invoke TDD skill)
- Common debugging rationalizations
- Red flags (fixing symptoms, not root cause)

**Superclaude additions**:
- Reference `/sc:troubleshoot` command and `root-cause-analyst` agent
- Handoff: `test-driven-development` skill for the fix

- [ ] **Step 3: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 10: Phase 2 commit

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

- [ ] **Step 2: Commit**

```bash
git add src/superclaude/skills/executing-plans/ src/superclaude/skills/test-driven-development/ src/superclaude/skills/systematic-debugging/
git commit -m "feat: add Phase 2 execution skills (executing-plans, TDD, debugging)"
```

---

## Chunk 3: Phase 3 — Review + Branch Skills (3 skills + 1 command)

### Task 11: Create /sc:review command

**Files:**
- Create: `src/superclaude/commands/review.md`
- Reference: `.claude/rules/command-authoring.md` (command format rules)
- Reference: `src/superclaude/commands/analyze.md` (existing command for pattern)

- [ ] **Step 1: Write review.md**

**Frontmatter**:
```yaml
---
description: Review code changes for quality, security, and correctness with structured feedback
---
```

**Body**: Follow command-authoring rules. XML component structure:
```xml
<component name="review" type="command">
  <role>
    /sc:review
    <mission>Review code changes for quality, security, and correctness</mission>
  </role>
  <syntax>/sc:review [target] [--scope pr|diff|file]</syntax>
  <flow>
    1. Identify: determine review scope (PR, diff, files)
    2. Analyze: read changes, check patterns, security, edge cases
    3. Feedback: structured findings (critical, important, suggestion)
    4. Verify: run tests and linting on changed code
  </flow>
  <outputs note="Per execution">
  | Artifact | Purpose |
  |----------|---------|
  | Review summary | Categorized findings |
  | Action items | Required changes before merge |
  </outputs>
  <bounds will="code review, quality analysis, security check" wont="auto-merge, auto-approve, modify code without permission"/>
  <handoff next="/sc:implement /sc:test"/>
</component>
```

- [ ] **Step 2: Run command structure tests**

```bash
uv run pytest tests/unit/test_command_structure.py -v
```

---

### Task 12: Create requesting-code-review skill

**Files:**
- Create: `src/superclaude/skills/requesting-code-review/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/requesting-code-review/SKILL.md`

- [ ] **Step 1: Create skill directory and write SKILL.md**

```bash
mkdir -p src/superclaude/skills/requesting-code-review
```

**Frontmatter**:
```yaml
---
name: requesting-code-review
description: |
  Dispatch a subagent reviewer with precisely crafted context to review completed work.
  Use when completing tasks, implementing features, or before merging. Provides the
  reviewer exactly the context needed without session history leakage.
context: fork
---
```

**Body**: Port superpowers requesting-code-review. Key elements:
- Craft review context (what changed, why, what to check)
- Dispatch subagent reviewer (not session history)
- Review scope: diff, spec compliance, test coverage
- Handle review feedback: fix issues, re-dispatch if needed

**Superclaude additions**:
- Reference `/sc:review` command and `self-review` agent
- Handoff: `receiving-code-review` skill

- [ ] **Step 2: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 13: Create receiving-code-review skill

**Files:**
- Create: `src/superclaude/skills/receiving-code-review/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/receiving-code-review/SKILL.md`

- [ ] **Step 1: Create skill directory and write SKILL.md**

```bash
mkdir -p src/superclaude/skills/receiving-code-review
```

**Frontmatter**:
```yaml
---
name: receiving-code-review
description: |
  Handle code review feedback with technical rigor, not performative agreement.
  Use when receiving review comments. Verify suggestions before implementing,
  push back on incorrect feedback with evidence.
---
```

**Body**: Port superpowers receiving-code-review. Key elements:
- Technical rigor over performative agreement
- Verify reviewer suggestions before implementing
- Push back with evidence when feedback is incorrect
- Don't blindly implement all suggestions
- Understand the "why" behind feedback

- [ ] **Step 2: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 14: Create finishing-a-development-branch skill

**Files:**
- Create: `src/superclaude/skills/finishing-a-development-branch/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/finishing-a-development-branch/SKILL.md`

- [ ] **Step 1: Create skill directory and write SKILL.md**

```bash
mkdir -p src/superclaude/skills/finishing-a-development-branch
```

**Frontmatter**:
```yaml
---
name: finishing-a-development-branch
description: |
  Complete development work with structured options for merge, PR, or cleanup.
  Use when implementation is complete and all tests pass. Presents options and
  guides branch completion. Involves git operations.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---
```

**Body**: Port superpowers finishing-a-development-branch. Key elements:
- 4 options: merge to main, create PR, save for later, cleanup
- Verification before any option (tests pass, linting clean)
- PR creation with structured description
- Cleanup of worktree if applicable

**Superclaude additions**:
- Git operations handled natively (no `/sc:git` reference — command deleted in Phase 5)
- Handoff: none (terminal skill)

- [ ] **Step 2: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 15: Phase 3 commit

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

- [ ] **Step 2: Commit**

```bash
git add src/superclaude/skills/requesting-code-review/ src/superclaude/skills/receiving-code-review/ src/superclaude/skills/finishing-a-development-branch/ src/superclaude/commands/review.md
git commit -m "feat: add Phase 3 review skills + /sc:review command"
```

---

## Chunk 4: Phase 4 — Utility Skills + Python Cleanup (3 skills)

### Task 16: Create dispatching-parallel-agents skill

**Files:**
- Create: `src/superclaude/skills/dispatching-parallel-agents/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/dispatching-parallel-agents/SKILL.md`

- [ ] **Step 1: Create skill directory and write SKILL.md**

```bash
mkdir -p src/superclaude/skills/dispatching-parallel-agents
```

**Frontmatter**:
```yaml
---
name: dispatching-parallel-agents
description: |
  Dispatch multiple subagents concurrently for independent tasks. Use when facing
  2+ tasks that can be worked on without shared state or sequential dependencies.
  Manages context isolation between agents.
disable-model-invocation: true
---
```

**Body**: Port superpowers dispatching-parallel-agents. Key elements:
- When to dispatch (2+ independent tasks, no shared state)
- Context isolation: each agent gets only what it needs
- Parallel execution: launch all at once, gather results
- Result integration: merge outputs, resolve conflicts
- Error handling: partial failure recovery

**Superclaude additions**:
- Reference `/sc:spawn` command

- [ ] **Step 2: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 17: Create using-git-worktrees skill

**Files:**
- Create: `src/superclaude/skills/using-git-worktrees/SKILL.md`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/using-git-worktrees/SKILL.md`

- [ ] **Step 1: Create skill directory and write SKILL.md**

```bash
mkdir -p src/superclaude/skills/using-git-worktrees
```

**Frontmatter**:
```yaml
---
name: using-git-worktrees
description: |
  Create isolated git worktrees for feature work and plan execution. Use when
  starting work that needs isolation from current workspace. Sets up worktree
  with smart directory selection and safety verification.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---
```

**Body**: Port superpowers using-git-worktrees. Key elements:
- When to use worktrees (feature isolation, plan execution)
- Worktree creation commands
- Safety verification (check clean state, no conflicts)
- Directory selection (adjacent to repo, named by feature)
- Cleanup after completion

- [ ] **Step 2: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 18: Create using-superclaude meta-skill

**Files:**
- Create: `src/superclaude/skills/using-superclaude/SKILL.md`

- [ ] **Step 1: Create skill directory and write SKILL.md**

```bash
mkdir -p src/superclaude/skills/using-superclaude
```

**Frontmatter**:
```yaml
---
name: using-superclaude
description: |
  Meta-skill establishing how to find and use superclaude skills. Loaded at session
  start. Defines skill invocation rules, priority order, and the mandatory check
  before any response. Even 1% chance a skill applies means invoke it.
---
```

**Body**: Adapted from superpowers using-superpowers. Key elements:
- Skill invocation rule: check before ANY response
- Skill priority: process skills first, then implementation
- Red flags table (rationalizations for skipping skills)
- Available skills list (all 15)
- Skill types: rigid (TDD, debugging) vs flexible (patterns)

**Superclaude additions**:
- Reference `/sc:help` for full command listing
- List all 15 skills with their trigger conditions
- Reference superclaude commands and agents as tools available within skills

- [ ] **Step 2: Run structure tests**

```bash
uv run pytest tests/unit/test_content_structure.py -v -k skill
```

---

### Task 19: Add deprecation notices to execution/ Python files

**Files:**
- Modify: `src/superclaude/execution/parallel.py` (line 1)
- Modify: `src/superclaude/execution/reflection.py` (line 1)
- Modify: `src/superclaude/execution/self_correction.py` (line 1)

- [ ] **Step 1: Add deprecation header to each file**

Add at the top of each file's module docstring:

```python
"""
DEPRECATED: This module is superseded by Claude Code's native Agent tool
and the superclaude process skills (executing-plans, systematic-debugging).
Kept for backward compatibility with existing pytest fixtures and tests.

[original docstring continues...]
"""
```

- [ ] **Step 2: Run full test suite to verify nothing breaks**

```bash
uv run pytest -v
```

Expected: all tests pass unchanged.

---

### Task 20: Phase 4 commit

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

- [ ] **Step 2: Commit**

```bash
git add src/superclaude/skills/dispatching-parallel-agents/ src/superclaude/skills/using-git-worktrees/ src/superclaude/skills/using-superclaude/ src/superclaude/execution/parallel.py src/superclaude/execution/reflection.py src/superclaude/execution/self_correction.py
git commit -m "feat: add Phase 4 utility skills + deprecate execution/ modules"
```

---

## Chunk 5: Phase 5 — Token Optimization + Integration

### Task 21: Remove git.md command

**Files:**
- Delete: `src/superclaude/commands/git.md`

- [ ] **Step 1: Verify git.md is a Claude Code native duplicate**

Read `src/superclaude/commands/git.md` to confirm it duplicates Claude Code's native git functionality.

- [ ] **Step 2: Delete the file**

```bash
rm src/superclaude/commands/git.md
```

- [ ] **Step 3: Run command structure tests**

```bash
uv run pytest tests/unit/test_command_structure.py -v
```

---

### Task 22: Compress recommend.md

**Files:**
- Modify: `src/superclaude/commands/recommend.md`

- [ ] **Step 1: Read current recommend.md**

Note the current token count (~8,428 tokens).

- [ ] **Step 2: Compress to ~3,000 tokens**

- Reduce 9 examples to 3 essential examples
- Remove "Comprehensive Final Example" (duplicates earlier content)
- Consolidate redundant YAML mappings
- Compress verbose explanations to bullet points

- [ ] **Step 3: Run command structure tests**

```bash
uv run pytest tests/unit/test_command_structure.py -v
```

---

### Task 23: Compress pm.md

**Files:**
- Modify: `src/superclaude/commands/pm.md`

- [ ] **Step 1: Read current pm.md and pm-agent agent**

Note overlap between `commands/pm.md` (~5,106 tokens) and `agents/pm-agent.md` (~4,993 tokens).

- [ ] **Step 2: Reduce pm.md to brief command reference (~1,100 tokens)**

Keep: syntax, basic description, handoff to pm-agent.
Remove: all detailed PM Agent logic (lives in the agent file).

- [ ] **Step 3: Run command structure tests**

```bash
uv run pytest tests/unit/test_command_structure.py -v
```

---

### Task 24: Compress improve.md and reflect.md

**Files:**
- Modify: `src/superclaude/commands/improve.md`
- Modify: `src/superclaude/commands/reflect.md`

- [ ] **Step 1: Trim improve.md (target: save ~1,500 tokens)**

Remove content that overlaps with skills (TDD, verification). Keep the command-specific improvement workflow.

- [ ] **Step 2: Trim reflect.md (target: save ~1,200 tokens)**

Remove content absorbed by `verification-before-completion` skill. Keep as brief pointer to the skill.

- [ ] **Step 3: Run command structure tests**

```bash
uv run pytest tests/unit/test_command_structure.py -v
```

---

### Task 25: Update project documentation with new counts

**Files:**
- Modify: `CLAUDE.md`
- Modify: `PLANNING.md`
- Modify: `TASK.md`

- [ ] **Step 1: Update CLAUDE.md skill count**

Change skills count from 3 to 15 in the Content Installation Flow section and Package Structure section.

- [ ] **Step 2: Update CLAUDE.md command count**

Command count should be 30 (29 after git.md removal + 1 review.md addition).

- [ ] **Step 3: Update PLANNING.md**

Update the architecture diagram to reflect 15 skills. Update roadmap to mark process skills as complete.

- [ ] **Step 4: Update TASK.md**

Mark the content framework upgrade as completed.

---

### Task 26: Phase 5 commit + final verification

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

- [ ] **Step 2: Test installation**

```bash
superclaude install --scope user --force
```

Verify all 15 skills deployed to `~/.claude/skills/`.

- [ ] **Step 3: Verify token count**

Use token estimation to verify total is moving toward 60,000 target.

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/commands/recommend.md src/superclaude/commands/pm.md src/superclaude/commands/improve.md src/superclaude/commands/reflect.md CLAUDE.md PLANNING.md TASK.md
git rm src/superclaude/commands/git.md
git commit -m "feat: Phase 5 token optimization + doc updates"
```

- [ ] **Step 5: Final deploy**

```bash
make deploy
```

---

## Verification Checklist (All Phases)

- [ ] 15 skills exist in `src/superclaude/skills/` (12 new + 3 existing)
- [ ] All skill names match superpowers exactly (except using-superclaude)
- [ ] Workflow gates documented in `core/RULES.md`
- [ ] `/sc:review` command created and validated
- [ ] All tests pass: `uv run pytest -v`
- [ ] `superclaude install` deploys all 15 skills
- [ ] Deprecation notices on `execution/` modules
- [ ] Token count reduced from ~85K toward 60K target
- [ ] CLAUDE.md updated with correct counts
