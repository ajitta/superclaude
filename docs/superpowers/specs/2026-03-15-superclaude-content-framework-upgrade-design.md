# Superclaude Content Framework Upgrade Design

**Date**: 2026-03-15
**Status**: Approved
**Approach**: Cherry-Pick & Independent Enhancement (superpowers-compatible)

## Problem Statement

Comparative analysis of obra/superpowers (v5.0.2, 40K+ stars) vs superclaude (v4.3.0+ajitta) reveals:

1. **Superclaude lacks process workflow chain** — 30 commands and 20 agents exist as independent silos with no enforced progression (brainstorm -> plan -> execute -> verify)
2. **Skills system is underutilized** — only 3 skills vs superpowers' 14 process-enforcing skills
3. **PM Agent Python code doesn't work** — confidence.py, self_check.py, reflexion.py exist as Python functions but have zero integration with the markdown-based Claude Code workflow. No command or agent calls them.
4. **No hard gates** — users can skip brainstorming and jump straight to implementation
5. **No verification enforcement** — no evidence-first completion gate

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Independence | Keep superclaude independent | Unique domain breadth (30 commands, 20 agents, 8 modes) |
| Focus | Content framework only | PM Agent Python doesn't connect to CC workflow |
| Porting style | Superpowers-compatible | Easier adoption for superpowers users |
| PM Agent Python | Keep pytest fixtures, minimize rest | 1,321 tests depend on fixtures |

## Architecture Change

### Current State
```
superclaude content:
├── commands/ (30) ← independent silos, no workflow chain
├── agents/ (20)   ← independent silos, no orchestration
├── skills/ (3)    ← underutilized (confidence-check, ship, simplicity-coach)
├── modes/ (8)     ← behavioral config, working well
├── core/ (4)      ← FLAGS, PRINCIPLES, RULES, BUSINESS_SYMBOLS
├── mcp/ (9)       ← MCP server docs, working well
└── pm_agent/ (Python) ← not connected to CC workflow
```

### Target State
```
superclaude content:
├── commands/ (25-28) ← trimmed, connected to skills
├── agents/ (18-20)   ← trimmed, roles clarified for skill delegation
├── skills/ (12-15)   ← PROCESS BACKBONE (ported from superpowers)
├── modes/ (8)        ← unchanged
├── core/ (4)         ← workflow chain rules added to RULES.md
├── mcp/ (9)          ← unchanged
└── pm_agent/ (Python) ← pytest fixtures only, rest minimized
```

**Key shift**: Skills become the process backbone. Commands/agents become tools invoked BY skills, not standalone entry points.

## Skills Porting Plan

### 12 Skills to Port (from superpowers 14)

| # | Skill | Source (superpowers) | Superclaude Integration | Priority |
|---|-------|---------------------|------------------------|----------|
| 1 | brainstorming | brainstorming SKILL.md | `/sc:brainstorm` + `requirements-analyst` agent | P1 |
| 2 | writing-plans | writing-plans SKILL.md | `/sc:workflow` + `/sc:task` commands | P1 |
| 3 | verification-before-completion | verification-before-completion SKILL.md | NEW (no equivalent exists) | P1 |
| 4 | executing-plans | executing-plans SKILL.md | `/sc:agent` + `/sc:spawn` commands | P2 |
| 5 | test-driven-development | test-driven-development SKILL.md | `/sc:test` + `quality-engineer` agent | P2 |
| 6 | systematic-debugging | systematic-debugging SKILL.md | `/sc:troubleshoot` + `root-cause-analyst` agent | P2 |
| 7 | requesting-code-review | requesting-code-review SKILL.md | `self-review` agent (NOTE: `/sc:review` command must be created) | P3 |
| 8 | receiving-code-review | receiving-code-review SKILL.md | NEW | P3 |
| 9 | finishing-a-development-branch | finishing-a-development-branch SKILL.md | `/sc:git` command (NOTE: `/sc:commit` command must be created or merged into git) | P3 |
| 10 | dispatching-parallel-agents | dispatching-parallel-agents SKILL.md | `/sc:spawn` command | P4 |
| 11 | using-git-worktrees | using-git-worktrees SKILL.md | NEW | P4 |
| 12 | using-superclaude | using-superpowers SKILL.md (renamed) | `/sc:help` command | P4 |

### Excluded
- **writing-skills** — meta-tool for skill authoring, add later
- **subagent-driven-development** — absorbed into executing-plans

### Skill File Structure

Each skill follows superclaude's existing skill-authoring rules (`.claude/rules/skill-authoring.md`):

```
src/superclaude/skills/
├── brainstorming/
│   └── SKILL.md          ← superpowers-compatible content, superclaude frontmatter
├── writing-plans/
│   └── SKILL.md
├── verification-before-completion/
│   └── SKILL.md
├── executing-plans/
│   └── SKILL.md
├── test-driven-development/
│   └── SKILL.md
├── systematic-debugging/
│   └── SKILL.md
├── requesting-code-review/
│   └── SKILL.md
├── receiving-code-review/
│   └── SKILL.md
├── finishing-a-development-branch/
│   └── SKILL.md
├── dispatching-parallel-agents/
│   └── SKILL.md
├── using-git-worktrees/
│   └── SKILL.md
├── using-superclaude/
│   └── SKILL.md
├── confidence-check/          ← existing, keep
│   └── SKILL.md
├── ship/                      ← existing, keep
│   └── SKILL.md
└── simplicity-coach/          ← existing, keep
    └── SKILL.md
```

Total: 15 skills (12 new + 3 existing)

### Frontmatter Policy for Ported Skills

| Skill | disable-model-invocation | context | allowed-tools | Rationale |
|-------|--------------------------|---------|---------------|-----------|
| brainstorming | — | — (inline) | — (all) | Auto-invoke on creative/feature work |
| writing-plans | — | — (inline) | — (all) | Auto-invoke after brainstorming |
| verification-before-completion | — | — (inline) | — (all) | Auto-invoke on completion claims |
| executing-plans | — | fork | — (all) | Subagent isolation for plan tasks |
| test-driven-development | — | — (inline) | — (all) | Auto-invoke on implementation |
| systematic-debugging | — | — (inline) | — (all) | Auto-invoke on bugs/failures |
| requesting-code-review | — | fork | — (all) | Subagent reviewer needs isolation |
| receiving-code-review | — | — (inline) | — (all) | Guidance for receiving feedback |
| finishing-a-development-branch | `true` | — (inline) | Bash, Read, Grep, Glob | Side effects (git push, PR) |
| dispatching-parallel-agents | `true` | — (inline) | — (all) | Spawns multiple agents (side effect) |
| using-git-worktrees | `true` | — (inline) | Bash, Read, Grep, Glob | Creates worktrees (filesystem side effect) |
| using-superclaude | — | — (inline) | — (all) | Meta-skill, auto-invoke at session start |

### Commands to Create (Prerequisites)

| Command | Phase | Connected Skills |
|---------|-------|-----------------|
| `/sc:review` | Phase 3 | requesting-code-review, receiving-code-review |

## Workflow Chain + Hard Gates

### Chain Definition

```
brainstorming ──gate──> writing-plans ──gate──> executing-plans ──gate──> verification
     │                       │                       │                       │
     v                       v                       v                       v
  /sc:brainstorm         /sc:workflow             /sc:agent              self-review agent
  requirements-analyst   /sc:task                 /sc:spawn              /sc:analyze
                                                  quality-engineer
```

### Gate Rules (to add to core/RULES.md)

```markdown
## Workflow Gates

1. brainstorming -> writing-plans: User must approve spec before planning
2. writing-plans -> executing-plans: Plan document must be committed to repo
3. executing-plans -> verification: All plan tasks must be marked complete
4. verification -> done: Test pass evidence required (actual output, not claims)

## Skill Priority (from superpowers)

Process skills activate BEFORE implementation:
1. brainstorming (any creative/feature work)
2. systematic-debugging (any bug/failure)
3. test-driven-development (any implementation)
4. verification-before-completion (any completion claim)
```

### Superpowers Compatibility

Skills maintain superpowers' core patterns:
- Same checklist structure (numbered items, same order)
- Same hard gate semantics (MUST complete before proceeding)
- Same skill invocation rule ("even 1% chance a skill applies -> invoke it")
- Superclaude-specific additions clearly marked (e.g., agent references, MCP connections)

## PM Agent Python Cleanup

### Keep (pytest fixtures depend on these)
| File | What to keep | Reason |
|------|-------------|--------|
| `pytest_plugin.py` | Full file | 1,321 tests depend on fixtures |
| `pm_agent/confidence.py` | `CheckResult`, `ConfidenceResult` dataclasses, `ConfidenceCheck` protocol, `ConfidenceChecker.assess()` | Fixtures use them |
| `pm_agent/token_budget.py` | Full file | Simple, useful, fixtures use it |
| `pm_agent/self_check.py` | `SelfCheckProtocol.validate()` | Fixtures use it |
| `pm_agent/reflexion.py` | `ReflexionPattern` class (JSONL storage) | Fixtures use it |
| `pm_agent/task_cleanup.py` | Full file | Used by self_check |

### Minimize / Deprecate
| File | Action | Reason |
|------|--------|--------|
| `execution/parallel.py` | Add deprecation notice | Claude Code Agent tool supersedes |
| `execution/reflection.py` | Add deprecation notice | Skills handle this now |
| `execution/self_correction.py` | Add deprecation notice | Skills handle this now |

### No Deletion
All files stay for backward compatibility. Add `# DEPRECATED: ...` headers where appropriate. Tests keep passing.

## Token Optimization (Integrated)

### Budget
- Current: ~85,108 tokens
- Skills addition: +12,000 tokens (12 skills x ~1,000 avg)
- RULES.md growth + doc updates: +1,500 tokens
- Commands cleanup: -16,328 tokens (trim duplicates, compress)
- Verbose compression across all files: -3,000 tokens
- **Target: ~60,000 tokens** (aligned with PLANNING.md goal)

### Commands to Trim
| Command | Action | Token Savings |
|---------|--------|---------------|
| `recommend.md` (8,428t) | Compress examples 9->3 | -5,428 |
| `pm.md` (5,106t) | Merge into pm-agent, keep brief reference | -4,000 |
| `git.md` | Remove (Claude Code native) | -1,200 |
| `improve.md` | Merge improvement logic into relevant skills | -1,500 |
| `reflect.md` | Absorbed by verification-before-completion skill | -1,200 |
| Verbose explanations (all files) | Compress to bullets | -3,000 |

Net change: +13,500 - 16,328 - 3,000 = **-5,828 tokens** (improvement despite adding 12 skills)
Target: 85,108 - 5,828 = ~79,280. Remaining gap to 60,000 requires Phase 5 aggressive compression.

## Implementation Phases

### Phase 1: Foundation (Skills infra + core 3 skills)
- Port `brainstorming` skill (connect to `/sc:brainstorm` + `requirements-analyst`)
- Port `writing-plans` skill (connect to `/sc:workflow` + `/sc:task`)
- Port `verification-before-completion` skill (new)
- Update `core/RULES.md` with workflow gate rules
- Verify `install_paths.py` COMPONENTS dict auto-discovers new skill directories (update if not)
- Run structure tests: `uv run pytest tests/unit/test_content_structure.py -v`

### Phase 2: Execution skills (3 skills)
- Port `executing-plans` skill (connect to `/sc:agent` + `/sc:spawn`)
- Port `test-driven-development` skill (connect to `/sc:test` + `quality-engineer`)
- Port `systematic-debugging` skill (connect to `/sc:troubleshoot` + `root-cause-analyst`)
- Run structure tests

### Phase 3: Review + branch skills (3 skills)
- Create `/sc:review` command (prerequisite for code-review skills)
- Port `requesting-code-review` skill (connect to `/sc:review` + `self-review`)
- Port `receiving-code-review` skill (new)
- Port `finishing-a-development-branch` skill (connect to `/sc:git`)
- Run structure tests

### Phase 4: Utility + meta skills + cleanup (3 skills + Python)
- Port `dispatching-parallel-agents` skill (connect to `/sc:spawn`)
- Port `using-git-worktrees` skill (new)
- Port `using-superclaude` meta-skill (session-start invocation, skill priority rules)
- PM Agent Python cleanup (deprecation notices)
- Run full test suite: `uv run pytest -v`

### Phase 5: Token optimization + integration
- Compress `recommend.md`, merge `pm.md`
- Remove `git.md`
- Compress verbose explanations across all content files
- Validate token count targeting 60,000 (PLANNING.md goal)
- Update CLAUDE.md, PLANNING.md, TASK.md
- Run full test suite + `make deploy`

## Success Criteria

1. 15 skills installed and validated (structure tests pass)
2. Workflow chain documented in core/RULES.md
3. All existing 1,321 tests still pass
4. Token count <= 60,000 (from 85,108, aligned with PLANNING.md)
5. `superclaude install` deploys all 15 skills to `~/.claude/skills/`
6. Skill names match superpowers exactly (except `using-superpowers` -> `using-superclaude`)

## Branch Strategy

- Single feature branch: `feature/content-framework-upgrade`
- Commit per phase completion (Phase 1 commit, Phase 2 commit, etc.)
- Each phase must pass `uv run pytest -v` before committing
- Rollback: if a phase breaks tests, revert the phase commit and fix before re-attempting
- Merge to `master` after Phase 5 completion + full test pass

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token budget exceeded by skill additions | Context window pressure | Aggressive command trimming in Phase 5 |
| Superpowers skill content is copyrighted | Legal | Write superclaude-native content inspired by patterns, not copied verbatim |
| Existing tests break during Python cleanup | Regression | No deletions, only deprecation notices |
| Skills conflict with existing commands | User confusion | Clear documentation: skills = process, commands = tools |
