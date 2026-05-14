# Agent Memory Effectiveness System — Design Specification

**Date:** 2026-03-20
**Author:** chosh1179
**Status:** Draft — Pending /sc:plan
**Scope:** SuperClaude agent memory optimization across 22 agents

---

## 1. Problem Statement

SuperClaude has 22 agents (excluding README.md), all declaring `memory: project` in frontmatter. Claude Code v2.1.33+ provides robust infrastructure:

- `.claude/agent-memory/<name>/MEMORY.md` auto-created per agent
- First 200 lines of MEMORY.md auto-injected into system prompt
- Read/Write/Edit tools auto-enabled (even if in disallowedTools)

**Current utilization: 6 out of 22 agents (27%) actually write to memory.**

The gap is not infrastructure — it's guidance. Agents don't know **what** to remember, **when** to capture, or **how** to maintain quality.

### Industry Context

| Tool | Memory System | Dynamic Learning | Agent Isolation |
|------|-------------|-----------------|----------------|
| Claude Code | file-based, 200-line auto-inject | Yes | Yes |
| Windsurf | Automatic + User Memories | Yes | No (workspace) |
| Cline | Memory Bank (5 fixed files) | No (manual) | No |
| Cursor | .cursor/rules/ (static) | No | No |
| Copilot | copilot-instructions.md | No | No |

Claude Code's architecture is the most advanced. SuperClaude needs to leverage it.

---

## 2. Design Overview

Five integrated layers forming a unified system:

```
Layer 4: Cross-Agent Sharing ── <refs agents="..."/> reference paths
Layer 3: Quality Lifecycle ──── Capture → Consolidate → Validate → Retire
Layer 2: Scope ─────────────── All agents: memory: project (unchanged)
Layer 1: Memory Schema ──────── <memory_guide> per-agent categories
Layer 0: Memory Protocol ────── RULES.md common behavioral rules
```

### Design Principles

- **Markdown-only**: No Python code changes, no new files beyond this spec
- **Minimal footprint**: 4-6 lines per agent, ~12 lines in RULES.md
- **Leverage existing infra**: Claude Code's `memory: project` does the heavy lifting
- **Anti-over-engineering**: No custom lifecycle hooks, skills, or automation

---

## 3. Layer 0: Memory Protocol (RULES.md)

Add `<agent_memory_protocol>` section to `src/superclaude/core/RULES.md`:

```xml
<agent_memory_protocol note="Sub-agent persistent memory guidelines">
Read: MEMORY.md auto-injected at session start; read topic files only when task overlaps stored category
Capture: save on user correction, architecture/design decision, recurring pattern (3+ occurrences), unexpected discovery
Format: date + category + content + why (1-2 line index in MEMORY.md, details in separate topic files if needed)
Curate: consolidate similar entries when MEMORY.md exceeds 150 lines; retire entries unreferenced for 90+ days
Verify: before acting on memory, confirm against current code/state — memory is a claim about the past, not current truth
Cross-ref: when task requires cross-domain context, read related agents' MEMORY.md listed in own <refs>
</agent_memory_protocol>
```

**Placement:** After `<core_rules>` section, before `<anti_over_engineering>`.

---

## 4. Layer 1: Memory Schema (per-agent `<memory_guide>`)

### 4.1 XML Format

```xml
<memory_guide>
- CategoryName: what to remember in this category (1-line)
  <refs agents="related-agent1,related-agent2"/>
</memory_guide>
```

**Placement in agent .md:** After `<checklist>`, before `<examples>`.

### 4.2 All 22 Agent Memory Guides

#### Architecture Group (blue)

**system-architect:**
```xml
<memory_guide>
- Decisions: architecture choices with rationale and rejected alternatives
- Constraints: technical and business constraints discovered during analysis
- Patterns: chosen design patterns and why alternatives were rejected
  <refs agents="frontend-architect,backend-architect,devops-architect"/>
</memory_guide>
```

**frontend-architect:**
```xml
<memory_guide>
- Components: design system decisions, component API patterns, token conventions
- A11y-Issues: recurring accessibility failures and proven resolutions
- Perf-Baselines: Core Web Vitals baselines and optimization history
  <refs agents="system-architect,performance-engineer"/>
</memory_guide>
```

**backend-architect:**
```xml
<memory_guide>
- API-Decisions: endpoint design choices, versioning strategy, auth patterns
- Data-Models: schema evolution rationale and migration lessons
- Reliability: failure modes encountered, retry and circuit-breaker configurations
  <refs agents="system-architect,security-engineer"/>
</memory_guide>
```

**devops-architect:**
```xml
<memory_guide>
- Infra-Decisions: IaC choices, cloud service selections, cost trade-offs
- Pipeline-Issues: CI/CD failures, deployment gotchas, and resolutions
- Runbook-Learnings: incident patterns and monitoring gap discoveries
  <refs agents="system-architect,performance-engineer"/>
</memory_guide>
```

**project-initializer:**
```xml
<memory_guide>
- Setup-Patterns: project type detection heuristics that worked or failed
- Convention-Defaults: effective default conventions by framework and language
- Onboarding-Gaps: common missing setup steps discovered during initialization
  <refs agents="repo-index"/>
</memory_guide>
```

#### Engineering Group (green)

**security-engineer:**
```xml
<memory_guide>
- Vulnerabilities: discovered vulnerability patterns with CWE references
- Auth-Patterns: authentication and authorization decisions, threat models
- Compliance: regulatory requirements and how they were satisfied
  <refs agents="backend-architect,quality-engineer"/>
</memory_guide>
```

**quality-engineer:**
```xml
<memory_guide>
- Coverage-Gaps: areas with insufficient test coverage and reasons
- Flaky-Tests: unreliable tests, root causes, and fixes applied
- Edge-Cases: boundary conditions that caught real bugs
  <refs agents="root-cause-analyst,performance-engineer"/>
</memory_guide>
```

**performance-engineer:**
```xml
<memory_guide>
- Baselines: benchmark measurements (before/after) for critical paths
- Bottlenecks: identified performance bottleneck locations and resolutions
- Regressions: performance regressions caught and their root causes
  <refs agents="frontend-architect,backend-architect"/>
</memory_guide>
```

**refactoring-expert:**
```xml
<memory_guide>
- Debt-Map: known technical debt locations, severity, and priority
- Refactor-History: completed refactorings with outcomes and lessons
- Anti-Patterns: recurring code smells specific to this project
  <refs agents="quality-engineer,simplicity-guide"/>
</memory_guide>
```

**python-expert:**
```xml
<memory_guide>
- Conventions: project-specific Python patterns and style decisions
- Dependency-Issues: package conflicts, version pinning lessons
- Testing-Patterns: effective test patterns for this project domain
  <refs agents="quality-engineer,backend-architect"/>
</memory_guide>
```

**git-workflow:**
```xml
<memory_guide>
- Branch-Strategy: branching model, naming conventions, protection rules
- Merge-Issues: recurring merge conflict patterns and resolution strategies
- CI-Integration: commit hooks behavior, CI pipeline expectations and gotchas
  <refs agents="devops-architect"/>
</memory_guide>
```

#### Research Group (purple)

**deep-researcher:**
```xml
<memory_guide>
- Search-Strategies: effective query patterns and source combinations
- Source-Reliability: domain-specific trusted and unreliable sources
- Research-Gaps: topics where information was scarce or conflicting
  <refs agents="requirements-analyst"/>
</memory_guide>
```

**requirements-analyst:**
```xml
<memory_guide>
- Stakeholder-Map: key decision-makers, their priorities, and influence
- Scope-Changes: requirement changes, their drivers, and impact
- Ambiguity-Resolutions: how unclear requirements were clarified
  <refs agents="project-manager,system-architect"/>
</memory_guide>
```

**root-cause-analyst:**
```xml
<memory_guide>
- Debug-Patterns: recurring failure modes with proven root causes
- Environment-Gotchas: platform, version, and config-specific traps
- False-Leads: commonly suspected but incorrect hypotheses
  <refs agents="quality-engineer,performance-engineer"/>
</memory_guide>
```

#### Documentation Group (yellow)

**technical-writer:**
```xml
<memory_guide>
- Style-Decisions: documentation style choices and terminology conventions
- Audience-Profiles: target reader characteristics and knowledge levels
- Structure-Patterns: effective information architecture for this project
  <refs agents="learning-guide"/>
</memory_guide>
```

**learning-guide:**
```xml
<memory_guide>
- Effective-Explanations: explanation patterns that resonated with users
- Prerequisite-Maps: concept dependency chains by domain area
- Difficulty-Calibration: concepts users found unexpectedly easy or hard
  <refs agents="socratic-mentor,technical-writer"/>
</memory_guide>
```

**socratic-mentor:**
```xml
<memory_guide>
- Mastery-Tracking: learner progress on concepts (discovered/applied/mastered)
- Effective-Questions: question patterns that led to discovery breakthroughs
- Misconceptions: common misunderstandings and effective corrections
  <refs agents="learning-guide"/>
</memory_guide>
```

#### Management Group (orange)

**project-manager:**
```xml
<memory_guide>
- Session-Context: project state, active milestones, current blockers
- Decision-Log: key project decisions with rationale and stakeholders
- Workflow-Patterns: successful delegation and coordination approaches
- Mistake-Prevention: past mistakes with root cause and prevention checklist
  <refs agents="requirements-analyst,system-architect"/>
</memory_guide>
```

**self-review:**
```xml
<memory_guide>
- Review-Patterns: recurring quality issues found during post-implementation review
- Missed-Cases: edge cases that were missed and later discovered
- Validation-Criteria: effective acceptance criteria patterns for this project
  <refs agents="quality-engineer"/>
</memory_guide>
```

**simplicity-guide:**
```xml
<memory_guide>
- Complexity-Signals: patterns that indicated over-engineering in this project
- Simplification-Wins: successful complexity reductions and measurable impact
- Dependency-Audit: unnecessary dependencies identified and removed
  <refs agents="refactoring-expert,system-architect"/>
</memory_guide>
```

**business-panel-experts:**
```xml
<memory_guide>
- Market-Context: industry and competitive landscape facts relevant to project
- Strategy-Decisions: business strategy choices and framework analyses applied
- Stakeholder-Concerns: key business stakeholder priorities and constraints
  <refs agents="requirements-analyst,project-manager"/>
</memory_guide>
```

#### Indexing Group (cyan)

**repo-index:**
```xml
<memory_guide>
- Structure-Evolution: major project layout changes and reorganizations
- Hot-Zones: frequently changing directories and files
- Entry-Points: key service boundaries and documentation locations
  <refs agents="system-architect,project-initializer"/>
</memory_guide>
```

---

## 5. Layer 3: Quality Lifecycle

Encoded in the RULES.md `<agent_memory_protocol>` (Layer 0). Four phases:

| Phase | Trigger | Action |
|-------|---------|--------|
| **Capture** | User correction, architecture decision, pattern (3+ occurrences), unexpected discovery | Write date + category + content + why |
| **Consolidate** | MEMORY.md > 150 lines | Merge similar entries, extract patterns, generalize |
| **Validate** | Before acting on a memory | Confirm against current code/state |
| **Retire** | Entry unreferenced for 90+ days | Remove from MEMORY.md; delete topic files |

**Exception:** Architecture decisions (ADR) are never auto-retired. Mark as `[archived]` instead.

---

## 6. Layer 4: Cross-Agent Sharing

Implemented via `<refs agents="..."/>` in each `<memory_guide>`.

**Mechanism:** When an agent's task overlaps another agent's domain, it reads the referenced agent's MEMORY.md at `.claude/agent-memory/<referenced-agent>/MEMORY.md`.

**Example flow:**
1. backend-architect is designing an API
2. Sees `<refs agents="system-architect,security-engineer"/>`
3. Reads `.claude/agent-memory/system-architect/MEMORY.md` for architecture constraints
4. Reads `.claude/agent-memory/security-engineer/MEMORY.md` for security requirements

**Constraints:**
- Read-only cross-reference (never write to another agent's memory)
- Best-effort — if referenced memory doesn't exist, proceed without it
- Maximum 2 cross-references per task to avoid context bloat

---

## 7. Changes to agent-authoring.md

Add to `.claude/rules/agent-authoring.md` after the "Checklist for New Agents" section:

```markdown
## Memory Guide (required)

Every agent must include a `<memory_guide>` section in the XML body:

### Placement
After `<checklist>`, before `<examples>`.

### Format
```xml
<memory_guide>
- CategoryName: what to remember (1-line description)
- CategoryName: what to remember
  <refs agents="related-agent1,related-agent2"/>
</memory_guide>
```

### Rules
- 3-5 memory categories per agent, specific to the agent's domain
- Category names: PascalCase-Hyphenated (e.g., `Debug-Patterns`, `API-Decisions`)
- Each category: noun phrase + colon + what to remember (max 80 chars)
- `<refs>`: list agents whose memory may be relevant (max 3)
- All agents use `memory: project` scope
```

### Validation Addition
Add to `test_agent_structure.py`:
- `<memory_guide>` section exists
- Contains at least 2 category entries (lines starting with `- `)
- Contains `<refs agents="..."/>` with valid agent names

---

## 8. File Change Summary

| File | Change | Lines |
|------|--------|-------|
| `src/superclaude/core/RULES.md` | Add `<agent_memory_protocol>` section | +8 |
| `.claude/rules/agent-authoring.md` | Add Memory Guide rules + validation | +25 |
| 22 agent `.md` files | Add `<memory_guide>` section each | +4-6 each |
| `tests/unit/test_agent_structure.py` | Add memory_guide validation | +15 |
| **Total** | 25 files modified | ~150 lines |

### NOT Changed
- No new files created (except this spec)
- No Python source code in `src/superclaude/` modified
- No `memory:` scope changes (all remain `project`)
- No skills, hooks, or automation added
- No sc:save/sc:load modifications

---

## 9. Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Agents with memory guidance | 6/22 (27%) | 22/22 (100%) |
| Memory categories defined | 0 | ~70 across 22 agents |
| Cross-agent references | 0 | ~40 directional refs |
| Common protocol | None | RULES.md shared protocol |
| Authoring standard | None | agent-authoring.md rules |
| Test validation | None | Structural test for memory_guide |

---

## 10. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Agent .md files grow too large | Token cost +10% | Medium | memory_guide is 4-6 lines, negligible |
| Agents over-memorize (noise) | 200-line limit hit fast | Medium | Capture threshold in protocol (correction, decision, pattern 3+) |
| Cross-refs create context bloat | Slow agent startup | Low | Max 2 cross-refs per task, best-effort |
| Categories don't match actual usage | Guides ignored | Medium | Review after 1 month of usage, iterate |

---

## 11. Handoff

This spec is ready for `/sc:plan` to generate implementation tasks.

**Suggested sprint structure:**
1. RULES.md + agent-authoring.md (foundation)
2. Agent memory_guide additions (22 files, can be parallelized)
3. Test validation additions
4. Deploy + verify

**Verification command:**
```bash
uv run pytest tests/unit/test_agent_structure.py -v
```
