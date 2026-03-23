# Model-Agnostic Compatibility — Implementation Plan

**Goal:** Remove all 17 hardcoded "Opus 4.6" assumptions from SuperClaude so the framework works correctly on any Claude model (Opus, Sonnet, Haiku) via inheritance.
**Architecture:** Content-only changes to markdown files. No Python code changes. Agents inherit parent model by removing `model:` frontmatter field. Core rules generalized with `model_tendencies` self-calibration.
**Tech Stack:** Markdown editing, pytest validation
**Spec:** `docs/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md`
**Baseline:** 1,694 tests pass, 22 agents with `model:` field, 6 files with Opus hardcoding

---

## Sprint 1: Agent Frontmatter — Remove `model:` (22 files)

### Task 1.1: Remove `model:` from all 22 agent frontmatters

**Files:** Modify: `src/superclaude/agents/*.md` (22 files, line 4 each)

All agents have `model: opus` on line 4 except repo-index (`model: sonnet`). Remove the line from every agent.

- [ ] Remove `model: opus` from: system-architect, security-engineer, root-cause-analyst, self-review, requirements-analyst, business-panel-experts, deep-researcher, project-initializer, project-manager, simplicity-guide, backend-architect, frontend-architect, devops-architect, performance-engineer, quality-engineer, refactoring-expert, python-expert, technical-writer, learning-guide, socratic-mentor, git-workflow
- [ ] Remove `model: sonnet` from: repo-index
- [ ] Verify: `grep -c "^model:" src/superclaude/agents/*.md` → 0 matches

### Task 1.2: Update agent-authoring.md

**Files:** Modify: `.claude/rules/agent-authoring.md`

- [ ] Line 11: `model: opus|sonnet|haiku  # required` → `model: opus|sonnet|haiku  # optional | omit to inherit parent model (recommended)`
- [ ] Lines 33-36: Replace model routing heuristic with inherit-first guidance:
  ```
  - Default: omit `model:` field — agent inherits parent session's model (recommended)
  - Override: set `model:` explicitly only when a specific model is required regardless of user's session choice
  - Use sparingly — explicit `model:` overrides the user's cost/speed preference
  ```
- [ ] Verify: read file, confirm changes

### Task 1.3: Update agents/README.md

**Files:** Modify: `src/superclaude/agents/README.md`

- [ ] Remove `Model` column from all 8 agent tables (lines 13-71)
- [ ] Remove line 81: `Model routing: opus for architecture/security/judgment | sonnet for...`
- [ ] Add new `## Model Routing` section after Permission Framework:
  ```
  ## Model Routing

  All agents inherit the parent session's model by default — no `model:` field in frontmatter.
  To pin a specific model, add `model: opus|sonnet|haiku` to frontmatter (not recommended — overrides user's choice).
  ```
- [ ] Verify: read file, confirm no `Model` column remains

### Task 1.4: Sprint 1 verification

- [ ] Run: `uv run pytest tests/unit/test_agent_structure.py -v`
- [ ] Expected: all pass (tests don't validate `model:` field)

---

## Sprint 2: Core Files — Remove Opus Hardcoding (3 files)

### Task 2.1: RULES.md — generalize notes + add model_tendencies

**Files:** Modify: `src/superclaude/core/RULES.md`

- [ ] Line 59: `note="Representative scenarios — examples teach better than rules for Opus 4.6"` → `note="Representative scenarios — examples teach better than rules"`
- [ ] Line 82: `note="Opus 4.6 tends to over-engineer — these rules are critical guardrails"` → `note="Scope discipline — prevent gold-plating"`
- [ ] Insert before `</anti_over_engineering>` (after examples closing tag, line ~100):
  ```xml
  <model_tendencies note="Self-calibrate based on your known behavioral patterns">
    Over-engineering signals: creating classes for one-time operations, adding config for fixed values, building frameworks for single features
    Under-engineering signals: skipping error handling at system boundaries, omitting types in public interfaces, happy-path-only testing
  </model_tendencies>
  ```
- [ ] Verify: no "Opus" or "4.6" remains in file

### Task 2.2: PRINCIPLES.md — generalize thinking_strategy + multimodal

**Files:** Modify: `src/superclaude/core/PRINCIPLES.md`

- [ ] Lines 24-28: Replace thinking_strategy block:
  ```xml
  <thinking_strategy note="Adaptive by complexity">
  Complex reasoning (debug, arch): extended thinking when available
  Task planning: structured thinking block
  Simple tasks: direct response
  Anti-pattern: Extended + Manual = redundant; choose one by complexity
  </thinking_strategy>
  ```
- [ ] Line 52: `<multimodal note="Opus 4.6">` → `<multimodal note="Vision-capable models">`
- [ ] Verify: no "Opus" or "4.6" remains in file

### Task 2.3: FLAGS.md — generalize execution section

**Files:** Modify: `src/superclaude/core/FLAGS.md`

- [ ] Lines 39-41: Replace 3 lines with:
  ```
  Default: sub-agents inherit parent model (no agent declares model: by default)
  Override: add model: to agent frontmatter to pin a specific model (overrides user's session choice)
  ```
- [ ] Line 48: `--fast: same Opus 4.6 model, faster output (v2.1.36+)` → `--fast: same model, faster output (v2.1.36+)`
- [ ] Lines 51-52: Replace 2 notes:
  ```
  Note: see RULES.md anti_over_engineering for scope discipline guardrails
  Note: token consumption varies by model — monitor context usage, use --uc at 60%+
  ```
- [ ] Verify: no "Opus" or "4.6" remains in file

### Task 2.4: Sprint 2 verification

- [ ] Run: `uv run pytest tests/unit/ -v`
- [ ] Grep: confirm zero "Opus 4.6" in core/ files: `grep -r "Opus" src/superclaude/core/`

---

## Sprint 3: Mode & Agent Content (2 files)

### Task 3.1: MODE_Token_Efficiency.md

**Files:** Modify: `src/superclaude/modes/MODE_Token_Efficiency.md`

- [ ] Line 27: `Opus 4.6 uses 25-50% more tokens — trigger efficiency earlier` → `Token consumption varies by model — monitor context usage proactively`

### Task 3.2: simplicity-guide.md

**Files:** Modify: `src/superclaude/agents/simplicity-guide.md`

- [ ] Line 36: `note="Opus tendencies to resist"` → `note="Common over-engineering tendencies"`

### Task 3.3: Sprint 3 verification

- [ ] Run: `uv run pytest tests/unit/test_mode_structure.py tests/unit/test_agent_structure.py -v`

---

## Sprint 4: Final Verification & Deploy

### Task 4.1: Full audit — no "Opus 4.6" remains

- [ ] Run: `grep -r "Opus" src/superclaude/core/ src/superclaude/agents/ src/superclaude/modes/` → 0 matches
- [ ] Run: `grep -r "4\.6" src/superclaude/core/` → 0 matches

### Task 4.2: Full test suite

- [ ] Run: `uv run pytest`
- [ ] Expected: 1,694+ pass (baseline), 0 new failures
- [ ] Record: exact pass count for verification evidence

### Task 4.3: Deploy

- [ ] Run: `make deploy`
- [ ] Verify: installed correctly

### Task 4.4: Update spec status

- [ ] Change spec Status from "Draft — pending user approval" to "Delivered"

### Task 4.5: Update MEMORY.md

- [ ] Add model-agnostic transition entry to project memory
