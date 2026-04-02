---
status: superseded
revised: 2026-04-03
source: docs/specs/cc-source-alignment-discovery-ajitta-2026-04-02.md
---

# CC Source-Level Alignment — Implementation Plan

> **SUPERSEDED (2026-04-03):** Source spec had incorrect field values and harmful recommendations.
> Applied: `when-to-use` split, `skills` preload. Reverted: `effort`, `maxTurns`, `tools`, `permissionMode`.

**Original Goal:** Adopt 5 unused CC-native fields (`effort`, `maxTurns`, `when-to-use`, `tools`, `skills`) across 22 agents and 5 skills to improve token economy, security, and agent quality.

**Architecture:** Frontmatter-only changes (no Python code). Test updates for optional field validation. Authoring rule updates for new field documentation.

**Tech Stack:** YAML frontmatter, pytest, markdown

---

## Phase 1: Verification Gate (test agent)

Verify CC actually honors new fields in custom `.md` definitions before rolling out.

### Task 1: Create Test Agent

**Files:** Create: `src/superclaude/agents/_test-cc-fields.md`

- [ ] Create minimal agent with all new fields:
  ```yaml
  name: _test-cc-fields
  description: Temporary test agent for CC field verification (triggers - test)
  permissionMode: plan
  memory: project
  effort: 3
  maxTurns: 5
  tools: Read, Grep, Glob
  skills:
    - confidence-check
  color: cyan
  ```
- [ ] Deploy: `make deploy`
- [ ] Test manually: spawn agent, verify effort/maxTurns/tools/skills behavior
- [ ] Delete test agent after verification
- [ ] Document results in commit message

---

## Phase 2: Tier 1 — effort + maxTurns (22 agents)

Pure frontmatter additions. Zero risk — CC ignores unknown fields gracefully.

### Task 2: Add effort + maxTurns to all agents

**Files:** Modify: all 22 files in `src/superclaude/agents/*.md`

Field values per agent:

| Agent | effort | maxTurns | Rationale |
|-------|--------|----------|-----------|
| repo-index | 2 | 10 | Scanning, not reasoning |
| git-workflow | 2 | 10 | Mechanical git ops |
| technical-writer | 2 | 15 | Structured writing |
| learning-guide | 3 | 15 | Educational, moderate depth |
| socratic-mentor | 3 | 15 | Guidance, moderate depth |
| project-initializer | 3 | 15 | Setup, moderate depth |
| project-manager | 3 | *(omit)* | Orchestrator needs flexibility |
| frontend-architect | 3 | 20 | Standard design |
| backend-architect | 3 | 20 | Standard design |
| devops-architect | 3 | 20 | Standard design |
| quality-engineer | 3 | 20 | Test analysis |
| refactoring-expert | 3 | 20 | Code transformation |
| python-expert | 3 | 20 | Implementation |
| self-review | 3 | 15 | Validation pass |
| simplicity-guide | 3 | 10 | Quick assessment |
| system-architect | 4 | 20 | Complex design decisions |
| security-engineer | 4 | 20 | Threat analysis |
| performance-engineer | 4 | 20 | Optimization analysis |
| root-cause-analyst | 4 | 25 | Deep debugging |
| requirements-analyst | 4 | 20 | Ambiguity resolution |
| deep-researcher | 5 | 30 | Maximum synthesis depth |
| business-panel-experts | 5 | 25 | Multi-perspective analysis |

- [ ] Edit each agent's frontmatter to add `effort:` and `maxTurns:` after `color:`
- [ ] Verify: `uv run pytest tests/unit/test_agent_structure.py -v` (must still pass — new fields are optional)
- [ ] Commit: `feat: add effort + maxTurns fields to all 22 agents`

### Task 3: Add when-to-use to skills

**Files:** Modify: 5 SKILL.md files

| Skill | Current description length | Split to when-to-use |
|-------|--------------------------|---------------------|
| confidence-check | 3 lines packed | Move trigger keywords to when-to-use |
| simplicity-coach | 1 line | Add when-to-use with trigger scenarios |
| ship | 1 line | Add when-to-use with trigger scenarios |
| finishing-a-development-branch | 1 line | Add when-to-use with trigger scenarios |
| verbalized-sampling | 2 lines packed | Move trigger keywords to when-to-use |

- [ ] For each skill, split `description` into clean one-liner + `when-to-use` with trigger keywords
- [ ] Verify: `uv run pytest tests/unit/test_skill_structure.py -v`
- [ ] Commit: `feat: split skill descriptions into description + when-to-use`

---

## Phase 3: Tier 2 — tools allow-list + skills preload

### Task 4: Convert read-only agents to tools allow-list

**Files:** Modify: 8 agent `.md` files

Convert from `disallowedTools` (deny-list) to `tools` (allow-list):

| Agent | Current | New `tools` | Remove |
|-------|---------|-------------|--------|
| system-architect | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` | disallowedTools line |
| self-review | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` | disallowedTools line |
| deep-researcher | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` | disallowedTools line |
| simplicity-guide | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent` | disallowedTools line |
| business-panel-experts | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` | disallowedTools line |
| requirements-analyst | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` | disallowedTools line |
| socratic-mentor | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent` | disallowedTools line |
| security-engineer | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` | disallowedTools line |

- [ ] Edit each agent: replace `disallowedTools:` line with `tools:` line
- [ ] Verify all tests pass
- [ ] Commit: `feat: convert 8 read-only agents from deny-list to allow-list`

**Note:** Keep `disallowedTools: NotebookEdit` on permissive agents (9 agents) — deny-list is correct for "everything except notebooks". Only convert agents whose intent is "read-only + search".

### Task 5: Add skills preload to analytical agents

**Files:** Modify: 8 agent `.md` files

| Agent | skills | Rationale |
|-------|--------|-----------|
| system-architect | `confidence-check` | Validate before proposing architecture |
| backend-architect | `confidence-check` | Validate before API design |
| frontend-architect | `confidence-check` | Validate before UI decisions |
| quality-engineer | `confidence-check` | Check confidence before test strategy |
| performance-engineer | `confidence-check` | Validate perf hypotheses |
| root-cause-analyst | `confidence-check` | Validate root cause before fixing |
| security-engineer | `confidence-check` | Validate security assessment |
| refactoring-expert | `confidence-check` | Validate before refactoring |

Format to add to frontmatter:
```yaml
skills:
  - confidence-check
```

- [ ] Add `skills:` block to each agent's frontmatter
- [ ] Verify all tests pass
- [ ] Commit: `feat: preload confidence-check skill into 8 analytical agents`

---

## Phase 4: Test + Authoring Rule Updates

### Task 6: Update test_agent_structure.py

**Files:** Modify: `tests/unit/test_agent_structure.py`

Add optional field validation (tests pass if field absent, validate if present):

- [ ] Add `VALID_EFFORT_VALUES = {1, 2, 3, 4, 5}` constant
- [ ] Add test: `test_effort_valid_if_present` — if `effort` in fm, assert value in VALID_EFFORT_VALUES
- [ ] Add test: `test_max_turns_valid_if_present` — if `maxTurns` in fm, assert positive integer
- [ ] Add test: `test_tools_and_disallowed_mutually_exclusive` — assert not both `tools` and `disallowedTools` present
- [ ] Add test: `test_skills_reference_existing_dirs` — if `skills` in fm, each skill name must exist as dir in skills/
- [ ] Run: `uv run pytest tests/unit/test_agent_structure.py -v`
- [ ] Commit: `test: add optional field validation for effort, maxTurns, tools, skills`

### Task 7: Update agent-authoring.md

**Files:** Modify: `.claude/rules/agent-authoring.md`

- [ ] Add `effort`, `maxTurns`, `tools`, `skills` to YAML frontmatter template (as optional)
- [ ] Add `tools` as alternative to `disallowedTools` in "disallowedTools by role pattern" table:
  ```
  | Read-only (plan, review, research) | tools: Read, Grep, Glob, Agent, ... | Agent should only read/search |
  ```
- [ ] Add effort tiering table (Light=2, Standard=3, Deep=4, Maximum=5)
- [ ] Add maxTurns guidance table (Quick=10, Standard=20, Extended=30)
- [ ] Add skills preload guidance
- [ ] Add rule: `tools` and `disallowedTools` are mutually exclusive
- [ ] Commit: `docs: update agent-authoring rules with effort, maxTurns, tools, skills fields`

### Task 8: Update skill-authoring.md

**Files:** Modify: `.claude/rules/skill-authoring.md`

- [ ] Add `when-to-use` to Field Reference table
- [ ] Add `effort` to Field Reference table
- [ ] Add guidance: split `description` (clean one-liner) from `when-to-use` (trigger scenarios)
- [ ] Commit: `docs: update skill-authoring rules with when-to-use, effort fields`

---

## Verification

After all phases:

```bash
# Full test suite
uv run pytest tests/unit/test_agent_structure.py tests/unit/test_skill_structure.py -v

# Deploy and manual verification
make deploy

# Verify field rendering (inspect installed files)
cat ~/.claude/agents/system-architect.md | head -15
cat ~/.claude/skills/confidence-check/SKILL.md | head -15
```

**Success criteria:**
- All existing tests pass (baseline: 1,787 collected)
- New optional field tests pass
- Deployed agents show new fields in frontmatter
- Manual test: spawned agent with `effort: 2` vs `effort: 5` shows behavior difference

---

## Out of Scope (Tier 3-4, separate plan)

- Dynamic context skills (`!` backtick) — needs verification first
- `Bash(pattern:*)` fine-grained tool restrictions — needs verification first
- `omitClaudeMd` — needs careful per-agent evaluation
- XML tag alignment — uncertain benefit
- `isolation: worktree` — defer until need demonstrated
