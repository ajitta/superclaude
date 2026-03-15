# Opus 4.6 Alignment — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite 12 SP-ported skills to Opus 4.6-native format (WHAT-only, no HOW prescriptions) and simplify core file additions.

**Architecture:** Strip thinking prescriptions and aggressive language from skills, revert SP deference from core files, keep install-time dedup unchanged. Skills use plain markdown template (Purpose/Workflow/Constraints/Completion/Next).

**Tech Stack:** Markdown (skill files), Python (tests), Git

**Spec:** `docs/superpowers/specs/2026-03-15-opus46-alignment-design.md`

---

## Chunk 1: Core File Fixes

Revert/simplify the uncommitted SP coexistence changes in the 3 always-loaded core files.

### Task 1: Fix RULES.md — Simplify workflow_gates, remove skill_scope and skill_priority

**Files:**
- Modify: `src/superclaude/core/RULES.md`

- [ ] **Step 1: Revert workflow_gates to simple 4-stage chain**

Replace the current expanded workflow_gates (7-stage with `|` choices and `[]` optional stages) with:

```xml
  <workflow_gates note="Recommended workflow chain">
    brainstorming -> writing-plans: User approves spec before planning
    writing-plans -> executing-plans: Plan document committed to repo
    executing-plans -> verification: Plan tasks completed
    verification -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
```

- [ ] **Step 2: Remove skill_scope section entirely**

Delete the `<skill_scope>` block (lines about "invoke eagerly" vs "implement with restraint"). The Right-Altitude principle in PRINCIPLES.md already covers this.

- [ ] **Step 3: Remove skill_priority numbered list**

Delete the `<skill_priority>` block. Opus 4.6 can determine which skill applies without a numbered priority list.

- [ ] **Step 4: Verify RULES.md is valid XML-in-markdown**

Read the file and confirm no broken tags or dangling references.

- [ ] **Step 5: Commit**

```bash
git add src/superclaude/core/RULES.md
git commit -m "refactor: simplify RULES.md — remove SP coexistence complexity"
```

---

### Task 2: Fix PRINCIPLES.md — Remove Invoke-Eagerly

**Files:**
- Modify: `src/superclaude/core/PRINCIPLES.md`

- [ ] **Step 1: Remove the Invoke-Eagerly line**

Delete: `Invoke-Eagerly: check skills aggressively (even 1% match), but implement with restraint`

This conflicts with both Right-Altitude and Restraint-First which are already present.

- [ ] **Step 2: Commit**

```bash
git add src/superclaude/core/PRINCIPLES.md
git commit -m "refactor: remove Invoke-Eagerly from PRINCIPLES.md"
```

---

### Task 3: Fix FLAGS.md — Remove SP deference in model_routing

**Files:**
- Modify: `src/superclaude/core/FLAGS.md`

- [ ] **Step 1: Remove the SP conditional block**

Delete these lines from `<model_routing>`:
```
  When superpowers workflow active (subagent-driven-development skill):
    Defer to superpowers' dynamic model routing (by task complexity, not by role)
    SC model_routing applies only to /sc: commands and SC-specific agents

  When SC-only (no superpowers):
```

Keep only the SC-native routing table (opus/sonnet/haiku assignments) without any conditional wrapper.

- [ ] **Step 2: Commit**

```bash
git add src/superclaude/core/FLAGS.md
git commit -m "refactor: remove SP deference from FLAGS.md model_routing"
```

---

## Chunk 2: Skill Rewrites — Process Skills (Skills 1-4)

Each skill is rewritten from scratch. Read the current file, apply the 3-bucket test, write the new version. Frontmatter `name` and `description` fields are preserved (descriptions may be tightened).

### Task 4: Rewrite brainstorming/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/brainstorming/SKILL.md` (142 → ~60 lines)

- [ ] **Step 1: Read current file**

Read `src/superclaude/skills/brainstorming/SKILL.md` fully.

- [ ] **Step 2: Write new version**

Keep:
- Frontmatter (name, description — tighten description if needed)
- Checklist: explore context → ask questions one at a time → propose 2-3 approaches → present design → write spec → spec review loop → user review → handoff to writing-plans
- Visual companion offer (as optional step)
- Spec save path: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- "One question at a time" and "multiple choice preferred" principles (these are WHAT)

Remove:
- 9 thinking prescriptions (scope assessment methodology, complexity scaling rules, design thinking method, "Can someone understand what a unit does without reading its internals?")
- "HARD-GATE" block and anti-pattern section
- "You MUST create a task for each" mandate
- Process flow graphviz diagram

Target: ~60 lines, Purpose/Workflow/Constraints/Completion/Next template.

- [ ] **Step 3: Verify no aggressive language remains**

Search the file for: MUST, IRON LAW, NOT NEGOTIABLE, ABSOLUTELY, EXTREMELY, VIOLATING, HARD.GATE

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/brainstorming/SKILL.md
git commit -m "refactor: rewrite brainstorming skill — Opus 4.6 native"
```

---

### Task 5: Rewrite writing-plans/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/writing-plans/SKILL.md` (156 → ~50 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- File structure mapping requirement
- Bite-sized task granularity (2-5 min per step)
- Plan document header template
- Task structure with checkbox syntax
- Plan review loop (dispatch reviewer)
- Save path: `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`
- DRY, YAGNI, TDD, frequent commits
- Execution handoff (subagent-driven or executing-plans)

Remove:
- Decomposition thinking, architectural reasoning, capacity reasoning, cohesion thinking
- "assume engineer has zero context and questionable taste"
- "You reason best about code you can hold in context at once"

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/writing-plans/SKILL.md
git commit -m "refactor: rewrite writing-plans skill — Opus 4.6 native"
```

---

### Task 6: Rewrite executing-plans/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/executing-plans/SKILL.md` (80 → ~40 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Load plan → review → mark progress → follow steps → stop on blocker → handoff
- Finishing handoff to finishing-a-development-branch skill
- Worktree awareness

Remove:
- Critical analysis stance prescription
- Escalation judgment prescription
- Detailed decision framework for blockers (simplify to "stop and ask")

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/executing-plans/SKILL.md
git commit -m "refactor: rewrite executing-plans skill — Opus 4.6 native"
```

---

### Task 7: Rewrite test-driven-development/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/test-driven-development/SKILL.md` (379 → ~60 lines)

- [ ] **Step 1: Read current file**

This is the largest skill (379 lines). Read carefully to identify all WHAT vs HOW content.

- [ ] **Step 2: Write new version**

Keep:
- RED → GREEN → REFACTOR cycle (core workflow)
- 3 exception categories: refactoring (always TDD), legacy (test boundaries), config (judgment)
- Test verification: watch it fail, then watch it pass
- Refactoring under green tests only

Remove:
- 8 thinking prescriptions
- Rationalization prevention table (~30 lines of "if you catch yourself thinking X, stop")
- Cognitive bias framing ("sunk cost fallacy", "tests-after are biased")
- "Delete it. Start over." mandatory reset
- "VIOLATING LETTER = VIOLATING SPIRIT"
- "THE IRON LAW" framing
- Graphviz process diagram
- Red flags table

Soften:
- "NO PRODUCTION CODE WITHOUT FAILING TEST" → "Write a failing test before implementation"

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/test-driven-development/SKILL.md
git commit -m "refactor: rewrite TDD skill — Opus 4.6 native (379→~60 lines)"
```

---

## Chunk 3: Skill Rewrites — Quality Skills (Skills 5-8)

### Task 8: Rewrite systematic-debugging/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/systematic-debugging/SKILL.md` (223 → ~50 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Reproduce → investigate → fix → verify cycle
- "After 3+ failed fixes, reconsider your approach" (WHAT-NOT)
- Create a failing test to lock the fix

Remove:
- 10 thinking prescriptions (4-phase investigation framework, backward tracing, hypothesis formulation, pattern analysis, meta-reasoning)
- "THE IRON LAW: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION"
- Red flag thought patterns list
- "VIOLATING THE LETTER OF THIS PROCESS" language
- Architecture escalation framework

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/systematic-debugging/SKILL.md
git commit -m "refactor: rewrite debugging skill — Opus 4.6 native (223→~50 lines)"
```

---

### Task 9: Rewrite verification-before-completion/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/verification-before-completion/SKILL.md` (167 → ~35 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Run verification command → read full output → confirm before claiming
- Revert-verify cycle for regression (simplified)
- Evidence before claims principle

Remove:
- 5-step cognitive gate function (IDENTIFY/RUN/READ/VERIFY/ONLY THEN)
- Red flag thought patterns (using "should", "probably")
- "If you lie, you'll be replaced"
- "non-negotiable" and "VIOLATING LETTER" language
- Extensive regression verification 7-step cycle (simplify to: revert, verify old behavior, re-apply, verify new behavior)

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/verification-before-completion/SKILL.md
git commit -m "refactor: rewrite verification skill — Opus 4.6 native (167→~35 lines)"
```

---

### Task 10: Rewrite requesting-code-review/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/requesting-code-review/SKILL.md` (125 → ~40 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Get diff (git SHAs, changed files)
- Dispatch code-reviewer subagent with context
- Triage by severity (Critical → fix immediately, Important → address, Minor → optional)
- context: fork in frontmatter (if present)

Remove:
- Context crafting reasoning prescription
- Mental separation prescription ("keep reviewer focused on work product, not thought process")

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/requesting-code-review/SKILL.md
git commit -m "refactor: rewrite requesting-code-review — Opus 4.6 native"
```

---

### Task 11: Rewrite receiving-code-review/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/receiving-code-review/SKILL.md` (179 → ~50 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Understand feedback → verify technically → implement or push back → test
- "Evaluate feedback technically before implementing" (WHAT-NOT)
- One item at a time, test each
- GitHub threading workflow

Remove:
- 6 thinking prescriptions (cognitive verification, pushback reasoning, inquiry methodology)
- Forbidden phrases list ("You're absolutely right!", "Great point!", etc.)
- "Technical correctness over social comfort" framing
- "No performative agreement" mandate
- "Actions speak. Just fix it." behavioral mandate

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/receiving-code-review/SKILL.md
git commit -m "refactor: rewrite receiving-code-review — Opus 4.6 native"
```

---

## Chunk 4: Skill Rewrites — Workflow Skills (Skills 9-12)

### Task 12: Rewrite finishing-a-development-branch/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/finishing-a-development-branch/SKILL.md` (149 → ~50 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Run test suite → present 4 options (merge, PR, keep working, discard) → execute chosen → cleanup
- Test gate: tests must pass before presenting options
- Worktree cleanup if applicable
- Base branch detection

Remove:
- Branch topology reasoning prescription
- Detailed option presentation format (trust Opus 4.6 to present options clearly)

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/finishing-a-development-branch/SKILL.md
git commit -m "refactor: rewrite finishing-branch skill — Opus 4.6 native"
```

---

### Task 13: Rewrite dispatching-parallel-agents/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/dispatching-parallel-agents/SKILL.md` (178 → ~45 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Identify independent tasks → dispatch one agent per domain → review & integrate
- Agent prompt template (focused, self-contained)
- Failure handling (retry with different model, escalate if stuck)

Remove:
- Categorization method prescription
- Independence reasoning prescription
- Debugging philosophy ("Do NOT just increase timeouts")
- Detailed failure analysis framework

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/dispatching-parallel-agents/SKILL.md
git commit -m "refactor: rewrite dispatching-parallel-agents — Opus 4.6 native"
```

---

### Task 14: Rewrite using-git-worktrees/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/using-git-worktrees/SKILL.md` (169 → ~45 lines)

- [ ] **Step 1: Read current file**

- [ ] **Step 2: Write new version**

Keep:
- Check candidate dirs → verify .gitignore → create worktree → setup dependencies → run baseline tests
- Directory candidates priority (../worktrees, /tmp, etc.)
- Worktree cleanup on completion

Remove:
- Directory selection reasoning method
- Safety reasoning prescription
- "Fix broken things immediately" behavioral mandate

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/using-git-worktrees/SKILL.md
git commit -m "refactor: rewrite using-git-worktrees — Opus 4.6 native"
```

---

### Task 15: Rewrite using-superclaude/SKILL.md

**Files:**
- Modify: `src/superclaude/skills/using-superclaude/SKILL.md` (142 → ~50 lines)

- [ ] **Step 1: Read current file**

This is the meta-skill. Needs special attention — it sets the tone for all other skills.

- [ ] **Step 2: Write new version**

Keep:
- SC features overview: commands (/sc:*), agents, skills, core config
- How to invoke skills (Skill tool in Claude Code)
- Instruction priority: User > Superpowers > SuperClaude > Default (WHAT, not HOW)
- Platform adaptation note

Remove:
- 11 forbidden thought patterns table
- "1% threshold" for skill invocation
- "NOT NEGOTIABLE. NOT OPTIONAL. You cannot rationalize your way out of this."
- "ABSOLUTELY MUST invoke" language
- SP deference logic (coexistence handled at install-time)
- Red flags table
- Graphviz skill flow diagram
- "EXTREMELY_IMPORTANT" wrapper tags

Add:
- Brief note: "When Superpowers plugin is also installed, SP skills take precedence for overlapping skill names (handled automatically at install time)."

- [ ] **Step 3: Verify no aggressive language**

- [ ] **Step 4: Commit**

```bash
git add src/superclaude/skills/using-superclaude/SKILL.md
git commit -m "refactor: rewrite using-superclaude as SC-native meta-skill"
```

---

## Chunk 5: Test Updates and Validation

### Task 16: Update test_skill_structure.py

**Files:**
- Modify: `tests/unit/test_skill_structure.py`

- [ ] **Step 1: Read current test file**

Read `tests/unit/test_skill_structure.py` fully to understand all assertions.

- [ ] **Step 2: Remove test_rules_has_skill_priority**

Delete the `test_rules_has_skill_priority` method (asserts `<skill_priority` in RULES.md — this section was removed in Task 1).

- [ ] **Step 3: Update test_rules_has_workflow_gates**

Keep the assertion that `<workflow_gates` exists, but update any content checks to match the simplified 4-stage gates.

- [ ] **Step 4: Update test_workflow_gates_mention_key_skills**

Update the list of skills that must appear in workflow_gates. The simplified version references: `brainstorming`, `writing-plans`, `executing-plans`, `verification`.

- [ ] **Step 5: Add aggressive language absence test**

Add a new test class:

```python
class TestNoAggressiveLanguage:
    """Validate skills do not contain aggressive enforcement language."""

    FORBIDDEN_PATTERNS = [
        "ABSOLUTELY MUST",
        "IRON LAW",
        "NOT NEGOTIABLE",
        "VIOLATING LETTER",
        "EXTREMELY_IMPORTANT",
        "EXTREMELY-IMPORTANT",
    ]

    def test_no_aggressive_language(self, skill):
        dirname, content, fm = skill
        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in content, (
                f"{dirname}: contains aggressive language '{pattern}'"
            )
```

- [ ] **Step 6: Run full test suite**

```bash
python -m pytest tests/unit/test_skill_structure.py -v
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add tests/unit/test_skill_structure.py
git commit -m "test: update skill structure tests for Opus 4.6 alignment"
```

---

### Task 17: Run full test suite and validate

**Files:**
- None (validation only)

- [ ] **Step 1: Run complete test suite**

```bash
python -m pytest --tb=short -q
```

Expected: All 1523+ tests pass. New aggressive-language test passes.

- [ ] **Step 2: Verify skill line counts**

```bash
for f in brainstorming writing-plans executing-plans test-driven-development systematic-debugging verification-before-completion requesting-code-review receiving-code-review finishing-a-development-branch dispatching-parallel-agents using-git-worktrees using-superclaude; do wc -l "src/superclaude/skills/$f/SKILL.md"; done
```

Expected: Each skill is 30-80 lines. Total should be ~575 (±100).

- [ ] **Step 3: Verify no aggressive language across all skills**

```bash
grep -rn "ABSOLUTELY MUST\|IRON LAW\|NOT NEGOTIABLE\|VIOLATING LETTER\|EXTREMELY_IMPORTANT" src/superclaude/skills/
```

Expected: No matches.

- [ ] **Step 4: Verify core files are clean**

```bash
grep -n "Invoke-Eagerly\|skill_scope\|skill_priority\|superpowers workflow active" src/superclaude/core/*.md
```

Expected: No matches.

---

### Task 18: Update project memory

**Files:**
- Modify: `~/.claude/projects/C--Users-ajitta-Repos-ajitta-superclaude/memory/project_superpowers-coexistence.md`
- Modify: `~/.claude/projects/C--Users-ajitta-Repos-ajitta-superclaude/memory/project_content-framework-upgrade.md`

- [ ] **Step 1: Rewrite project_superpowers-coexistence.md**

Update from 3-layer to 1-layer model:
- Layer 1 (install-time dedup): unchanged
- Layers 2-3 (content-time, skill sync): removed — SC owns its behavior
- Reference the design spec for rationale

- [ ] **Step 2: Update project_content-framework-upgrade.md**

Add Phase 1 Opus 4.6 alignment work:
- 12 skills rewritten to Opus 4.6-native format
- Core files simplified (no SP deference)
- Token savings achieved

- [ ] **Step 3: Commit memory updates (if in repo)**

These are project-scoped memory files, not tracked in git. No commit needed.

---

## Summary

| Chunk | Tasks | Files Modified | Key Action |
|-------|-------|---------------|------------|
| 1: Core Files | 1-3 | 3 core .md files | Revert SP deference, simplify gates |
| 2: Process Skills | 4-7 | 4 skill SKILL.md files | Clean rewrite (brainstorming, plans, TDD) |
| 3: Quality Skills | 8-11 | 4 skill SKILL.md files | Clean rewrite (debug, verify, review) |
| 4: Workflow Skills | 12-15 | 4 skill SKILL.md files | Clean rewrite (branch, parallel, worktrees, meta) |
| 5: Tests & Validation | 16-18 | 1 test file + 2 memory files | Update tests, validate, update memory |

**Total: 18 tasks, 16 files modified, ~1,500 lines removed**
