---
status: draft
revised: 2026-04-02
subject: Claude Code Source-Level Alignment — SuperClaude Improvement Discovery
source: docs/analysis/claude-code-prompt-format-ajitta-2026-04-02.md (CC source analysis)
method: sequential-thinking + verbalized-sampling (k=5, tau=0.10)
---

# CC Source-Level Alignment: SuperClaude Improvement Discovery

CC 소스 코드 분석에서 도출된 SuperClaude 개선안. 문서화 기반이 아닌 **실제 TypeScript 인터페이스** 기반 gap 분석.

---

## Executive Summary

CC source analysis reveals **12 unused native fields** across agents and skills that SuperClaude doesn't leverage. The highest-impact improvements are:

1. **Agent-Skill Composition** (`skills` preload) — automatic safety mesh
2. **Effort Tiering** (`effort` field) — 20-30% token savings for light agents
3. **Allow-List Security** (`tools` field) — stronger least-privilege than deny-list
4. **Turn Safety Net** (`maxTurns`) — prevents runaway agents
5. **when-to-use Split** — better auto-invocation accuracy for skills

---

## VS Landscape (Verbalized Sampling)

| # | Perspective | p | Focus | Key Recommendation |
|---|-----------|-----|-------|-------------------|
| 1 | Pragmatic Incrementalist | 0.30 | Fields that work TODAY, no code changes | effort, maxTurns, when-to-use |
| 2 | Security-First Hardener | 0.25 | Least privilege enforcement | tools allow-list, Bash() patterns |
| 3 | Composition Architect | 0.20 | Agent-skill composition + dynamic context | skills preload matrix, utility skills |
| 4 | Token Economist | 0.15 | Aggressive context reduction | effort tiers, omitClaudeMd |
| 5 | Format Purist | 0.10 | XML tag alignment with CC internals | \<instructions\>, \<rules\>, \<reasoning\> |

**Consensus:** Perspectives 1+2+4 capture 70% probability mass — low-risk, high-certainty. Perspective 3 is highest upside. Perspective 5 is lowest priority.

---

## Gap Analysis: Unused CC-Native Fields

### Agent Fields (BaseAgentDefinition)

| Field | CC Type | SuperClaude Status | Impact | Priority |
|-------|---------|-------------------|--------|----------|
| `tools` | `string[]` (allow-list) | Not used (deny-list only) | HIGH | Tier 2 |
| `skills` | `string[]` (preload) | Not used | HIGH | Tier 2 |
| `effort` | `1-5 \| EffortValue` | Not used | MEDIUM-HIGH | Tier 1 |
| `maxTurns` | `number` | Not used | MEDIUM | Tier 1 |
| `omitClaudeMd` | `boolean` | Not used | MEDIUM | Tier 2 |
| `background` | `boolean` | Not used | LOW | Skip |
| `initialPrompt` | `string` | Not used | LOW | Skip |
| `isolation` | `worktree \| remote` | Not used | MEDIUM | Tier 4 |

### Skill Fields (SKILL.md frontmatter)

| Field | CC Type | SuperClaude Status | Impact | Priority |
|-------|---------|-------------------|--------|----------|
| `when-to-use` | `string` | Packed into description | HIGH | Tier 1 |
| `effort` | `low\|medium\|high\|max` | Not used | MEDIUM | Tier 1 |
| `shell` | `bash \| powershell` | Not used | LOW | Future |
| `paths` | `string[]` | Not used | LOW | Skip (global framework) |
| `!` backtick execution | inline shell | Not used | HIGH | Tier 3 |
| `${CLAUDE_SKILL_DIR}` | built-in variable | Not used | MEDIUM | Tier 3 |

### Tool Pattern Format (allowedTools)

| Pattern | Example | SuperClaude Status |
|---------|---------|-------------------|
| Fine-grained Bash | `Bash(git commit:*)` | Not used |
| Multi-pattern | `Bash(git add:*), Bash(git status:*)` | Not used |
| Coarse tool name | `Read, Grep, Glob` | Used (current approach) |

---

## Tiered Improvement Plan

### Tier 1: IMMEDIATE (frontmatter-only, zero code changes)

#### 1.1 effort Field Adoption

Add reasoning depth control to all 24 agents:

| Tier | effort | Agents | Rationale |
|------|--------|--------|-----------|
| Light | 2 | repo-index, git-workflow, technical-writer | Mechanical/structured tasks |
| Standard | 3 (or omit) | frontend/backend-architect, quality-engineer, refactoring-expert, learning-guide, project-manager | Standard design + analysis |
| Deep | 4 | system-architect, security-engineer, performance-engineer, root-cause-analyst, requirements-analyst | Complex reasoning needed |
| Maximum | 5 | deep-researcher, business-panel-experts | Multi-perspective synthesis |

**Expected savings:** 20-30% token reduction for Light tier agents.

#### 1.2 maxTurns Safety Net

| Category | maxTurns | Agents | Rationale |
|----------|----------|--------|-----------|
| Quick | 10 | repo-index, git-workflow | Should complete fast |
| Standard | 20 | Most architects + engineers | Analysis + output |
| Extended | 30 | deep-researcher, root-cause-analyst | Need exploration |
| Unlimited | (omit) | project-manager | Orchestrators need flexibility |

**Note:** Agent tool's maxTurns parameter overrides definition default. This is a safety net.

#### 1.3 when-to-use Split for Skills

Current (packed):
```yaml
description: >
  Pre-implementation confidence assessment (>=90% to proceed).
  Use when user mentions 'confidence', 'before implementing', 'validate first',
  'check before building', or wants validation before starting implementation work.
```

Proposed (split):
```yaml
description: Pre-implementation confidence assessment (>=90% to proceed).
when-to-use: >
  Use when user mentions 'confidence', 'before implementing', 'validate first',
  'check before building', or wants validation before starting implementation work.
```

**Rationale:** CC loads `name + description` at startup for all skills. `when-to-use` provides model-facing scenario guidance separately. Splitting reduces startup context while improving trigger accuracy.

---

### Tier 2: HIGH-VALUE (frontmatter + authoring rule updates)

#### 2.1 tools Allow-List for Read-Only Agents

Convert deny-list to allow-list for restrictive agents:

| Agent | Current (deny-list) | Proposed (allow-list) |
|-------|--------------------|-----------------------|
| system-architect | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` |
| self-review | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` |
| deep-researcher | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` |
| simplicity-guide | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent` |
| business-panel-experts | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` |
| requirements-analyst | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent, WebSearch, WebFetch` |
| socratic-mentor | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Read, Grep, Glob, Agent` |

**Security benefit:** Allow-list prevents implicit access to any new tool CC adds in future updates. Deny-list fails open.

**Authoring rule update needed:** agent-authoring.md should add `tools` as an alternative to `disallowedTools` with guidance on when to use which.

#### 2.2 skills Preload Matrix

| Agent | Preloaded Skills | Why |
|-------|-----------------|-----|
| system-architect | confidence-check | Validate before proposing architecture |
| backend-architect | confidence-check | Validate before API design |
| frontend-architect | confidence-check | Validate before UI decisions |
| quality-engineer | confidence-check, simplicity-coach | Check confidence + prevent over-engineering |
| refactoring-expert | simplicity-coach | Prevent over-refactoring |
| performance-engineer | confidence-check | Validate perf hypotheses |
| root-cause-analyst | confidence-check | Validate root cause before fixing |
| security-engineer | confidence-check | Validate security assessment |

**Token cost:** ~500 tokens per preloaded skill. Acceptable for the safety improvement.

**Format:**
```yaml
skills:
  - confidence-check
  - simplicity-coach
```

#### 2.3 omitClaudeMd for Pure-Research Agents

| Agent | omitClaudeMd | Rationale |
|-------|-------------|-----------|
| deep-researcher | `true` | Web-only research, doesn't read project code |
| business-panel-experts | `true` | Business analysis, not code-dependent |

**Token savings:** ~2-5K tokens per agent session (project CLAUDE.md not loaded).

**Risk:** Agent loses project-specific rules. Only viable for agents that never touch project files.

---

### Tier 3: ARCHITECTURAL (new skills + verification needed)

#### 3.1 Dynamic Context Skills (inline shell)

New utility skills using `!` backtick execution:

**git-context skill:**
```yaml
---
name: git-context
description: Injects fresh git context (recent commits, branch, diff stats) into agent sessions.
when-to-use: Preloaded by code-aware agents for automatic project state awareness.
user-invocable: false
---
```
```markdown
# Git Context

!`git log --oneline -10`
!`git diff --stat`
!`git branch --show-current`
```

**test-baseline skill:**
```yaml
---
name: test-baseline
description: Injects test suite baseline (collection count, recent failures) into agent sessions.
when-to-use: Preloaded by quality and implementation agents for test awareness.
user-invocable: false
---
```
```markdown
# Test Baseline

!`uv run pytest --co -q 2>/dev/null | tail -1`
```

**Preload via agents:**
```yaml
# quality-engineer frontmatter
skills:
  - confidence-check
  - test-baseline
  - git-context
```

**Risk:** Need to verify `!` backtick execution works in user-defined skills (analysis confirms CC supports it, but testing needed).

#### 3.2 Fine-Grained Bash Patterns

| Agent/Skill | Current | Proposed |
|-------------|---------|----------|
| git-workflow | `disallowedTools: Edit, Write, NotebookEdit` | `tools: Bash(git:*), Read, Grep, Glob` |
| ship skill | `allowed-tools: Bash, Read` | `allowed-tools: Bash(git push:*), Bash(gh pr:*), Read` |
| quality-engineer | `disallowedTools: NotebookEdit` | `tools: Read, Grep, Glob, Edit, Bash(uv run pytest:*), Bash(uv run ruff:*)` |

**Verification needed:** Does `parseSlashCommandToolsFromFrontmatter()` run for custom `.md` agent/skill definitions? The analysis confirms the parser exists but need to verify it applies to user definitions.

---

### Tier 4: DEFERRED (evaluate later)

| Item | Reason to Defer |
|------|----------------|
| XML tag alignment (\<instructions\>, \<rules\>) | Uncertain behavioral impact. Current custom tags work. High change cost (all files + tests) |
| `isolation: worktree` for destructive agents | Operational complexity. Defer until user reports need |
| `${CLAUDE_SKILL_DIR}` variable migration | Current `{{SKILLS_PATH}}` works. Low priority optimization |
| `shell: bash\|powershell` | Low priority — current skills use Python scripts |
| `background: true` default | User/orchestrator controls this, not agent definition |

---

## Authoring Rule Updates Required

### agent-authoring.md

1. Add `effort` to Field Reference (optional, tiered defaults)
2. Add `maxTurns` to Field Reference (optional, safety net)
3. Add `tools` as alternative to `disallowedTools` (allow-list pattern)
4. Add `skills` to Field Reference (preload list)
5. Add `omitClaudeMd` to Field Reference (pure-research agents only)
6. Update disallowedTools table with allow-list alternative row

### skill-authoring.md

1. Add `when-to-use` as recommended field (split from description)
2. Add `effort` to Field Reference
3. Document `!` backtick shell execution in body
4. Document `${CLAUDE_SKILL_DIR}` / `${CLAUDE_SESSION_ID}` variables

### Tests (test_agent_structure.py)

1. Validate `effort` is 1-5 if present
2. Validate `maxTurns` is positive integer if present
3. Validate `tools` and `disallowedTools` are mutually exclusive
4. Validate `skills` references existing skill directories

---

## Verification Gate

Before rolling out across all agents/skills:

1. **Create test-agent.md** with all new fields (`effort`, `maxTurns`, `tools`, `skills`, `omitClaudeMd`)
2. **Deploy:** `make deploy`
3. **Verify:**
   - `effort` affects reasoning depth (compare output quality at effort:2 vs effort:5)
   - `maxTurns` terminates agent at limit
   - `tools` allow-list actually restricts (try disallowed tool)
   - `skills` preload actually loads skill body
   - `omitClaudeMd` actually skips CLAUDE.md
4. **If all pass:** Roll out Tier 1 → Tier 2 → Tier 3 incrementally

---

## Risk Summary

| Tier | Risk | Mitigation |
|------|------|-----------|
| 1 | Zero — pure frontmatter additions | Graceful degradation if CC ignores |
| 2 | Low — needs authoring rule updates | Test agent verification first |
| 3 | Medium — new skills + shell execution | Verify `!` backtick in user skills |
| 4 | N/A — deferred | Evaluate when evidence emerges |
