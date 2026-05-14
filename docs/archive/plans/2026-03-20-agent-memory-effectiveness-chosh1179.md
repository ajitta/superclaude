# Agent Memory Effectiveness — Implementation Plan

**Goal:** Enable all 22 SuperClaude agents to effectively use persistent memory by adding a common protocol (RULES.md), per-agent memory guides (22 agent files), authoring rules, and test validation.
**Architecture:** Markdown-only changes across 25 files. No Python source changes except 1 test file. Layers: Protocol (RULES.md) → Schema (agent `<memory_guide>`) → Authoring rules → Tests.
**Tech Stack:** Markdown (agents, rules), Python (pytest validation)
**Spec:** `docs/specs/2026-03-20-agent-memory-effectiveness-design-chosh1179.md`

---

## Sprint 1: Foundation

### Task 1: Add `<agent_memory_protocol>` to RULES.md

**Files:** Modify: `src/superclaude/core/RULES.md:44` (between `</core_rules>` line 43 and `<anti_over_engineering>` line 45)

- [ ] Insert after `</core_rules>` (line 43), before blank line + `<anti_over_engineering>` (line 45):

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

- [ ] Verify: `grep "agent_memory_protocol" src/superclaude/core/RULES.md`

### Task 2: Add Memory Guide rules to agent-authoring.md

**Files:** Modify: `.claude/rules/agent-authoring.md` (append after "Checklist for New Agents" section, before end of file)

- [ ] Add the following section:

```markdown
## Memory Guide (required)

Every agent must include a `<memory_guide>` section in the XML body.

**Placement:** After `<checklist>`, before `<examples>`.

**Format:**
```xml
<memory_guide>
- CategoryName: what to remember (1-line, max 80 chars)
  <refs agents="related-agent1,related-agent2"/>
</memory_guide>
```

**Rules:**
- 3-5 memory categories per agent, specific to the agent's domain
- Category names: PascalCase-Hyphenated (e.g., `Debug-Patterns`, `API-Decisions`)
- `<refs>`: list agents whose memory may be relevant (max 3)
- All agents use `memory: project` scope

**Validation:** `test_agent_structure.py` checks:
- `<memory_guide>` section exists
- Contains at least 2 category entries (lines starting with `- `)
- Contains `<refs agents="..."/>` with valid agent names
```

- [ ] Verify: file reads correctly, no markdown syntax errors

---

## Sprint 2: Agent Memory Guides (22 files)

Each task adds a `<memory_guide>` section after `<checklist>...</checklist>` and before `<examples>`.

### Task 3: Architecture group (5 agents)

**Files:** Modify:
- `src/superclaude/agents/system-architect.md` (after checklist ~line 89, before examples line 90)
- `src/superclaude/agents/frontend-architect.md` (after checklist ~line 52, before examples line 53)
- `src/superclaude/agents/backend-architect.md` (after checklist ~line 87, before examples line 88)
- `src/superclaude/agents/devops-architect.md` (after checklist ~line 54, before examples line 55)
- `src/superclaude/agents/project-initializer.md` (after checklist ~line 123, before examples line 124)

Insert for each:

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

- [ ] Insert each block between `</checklist>` and `<examples>` in the corresponding file
- [ ] Verify: `grep -c "memory_guide" src/superclaude/agents/{system-architect,frontend-architect,backend-architect,devops-architect,project-initializer}.md` → each returns 2

### Task 4: Engineering group (6 agents)

**Files:** Modify:
- `src/superclaude/agents/security-engineer.md`
- `src/superclaude/agents/quality-engineer.md`
- `src/superclaude/agents/performance-engineer.md`
- `src/superclaude/agents/refactoring-expert.md`
- `src/superclaude/agents/python-expert.md`
- `src/superclaude/agents/git-workflow.md`

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

- [ ] Insert each block between `</checklist>` and `<examples>`
- [ ] Verify: `grep -c "memory_guide" src/superclaude/agents/{security-engineer,quality-engineer,performance-engineer,refactoring-expert,python-expert,git-workflow}.md` → each returns 2

### Task 5: Research group (3 agents)

**Files:** Modify:
- `src/superclaude/agents/deep-researcher.md`
- `src/superclaude/agents/requirements-analyst.md`
- `src/superclaude/agents/root-cause-analyst.md`

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

- [ ] Insert each block between `</checklist>` and `<examples>`
- [ ] Verify: `grep -c "memory_guide" src/superclaude/agents/{deep-researcher,requirements-analyst,root-cause-analyst}.md` → each returns 2

### Task 6: Documentation group (3 agents)

**Files:** Modify:
- `src/superclaude/agents/technical-writer.md`
- `src/superclaude/agents/learning-guide.md`
- `src/superclaude/agents/socratic-mentor.md`

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

- [ ] Insert each block between `</checklist>` and `<examples>`
- [ ] Verify: `grep -c "memory_guide" src/superclaude/agents/{technical-writer,learning-guide,socratic-mentor}.md` → each returns 2

### Task 7: Management group (4 agents)

**Files:** Modify:
- `src/superclaude/agents/project-manager.md`
- `src/superclaude/agents/self-review.md`
- `src/superclaude/agents/simplicity-guide.md`
- `src/superclaude/agents/business-panel-experts.md`

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

- [ ] Insert each block between `</checklist>` and `<examples>`
- [ ] Verify: `grep -c "memory_guide" src/superclaude/agents/{project-manager,self-review,simplicity-guide,business-panel-experts}.md` → each returns 2

### Task 8: Indexing group (1 agent)

**Files:** Modify: `src/superclaude/agents/repo-index.md`

**repo-index:**
```xml
  <memory_guide>
  - Structure-Evolution: major project layout changes and reorganizations
  - Hot-Zones: frequently changing directories and files
  - Entry-Points: key service boundaries and documentation locations
    <refs agents="system-architect,project-initializer"/>
  </memory_guide>
```

- [ ] Insert between `</checklist>` and `<examples>`
- [ ] Verify: `grep -c "memory_guide" src/superclaude/agents/repo-index.md` → returns 2

---

## Sprint 3: Test Validation

### Task 9: Add memory_guide tests to test_agent_structure.py

**Files:** Modify: `tests/unit/test_agent_structure.py` (append new class after `TestAgentMinimumContent`)

- [ ] Add `TestAgentMemoryGuide` class after line 230 (after `TestAgentMinimumContent`):

```python
class TestAgentMemoryGuide:
    """Validate <memory_guide> section in every agent file."""

    def test_has_memory_guide(self, agent):
        stem, content, _ = agent
        assert "<memory_guide>" in content, (
            f"{stem}: missing <memory_guide> section"
        )

    def test_memory_guide_has_categories(self, agent):
        stem, content, _ = agent
        mg = extract_xml_content(content, "memory_guide")
        assert mg, f"{stem}: <memory_guide> is empty"
        categories = [line.strip() for line in mg.splitlines()
                      if line.strip().startswith("- ")]
        assert len(categories) >= 2, (
            f"{stem}: memory_guide has {len(categories)} categories, need >= 2"
        )

    def test_memory_guide_has_refs(self, agent):
        stem, content, _ = agent
        mg = extract_xml_content(content, "memory_guide") or ""
        assert '<refs agents="' in mg, (
            f"{stem}: memory_guide missing <refs agents=\"...\"/>"
        )

    def test_memory_guide_refs_valid(self, agent):
        stem, content, _ = agent
        mg = extract_xml_content(content, "memory_guide") or ""
        match = re.search(r'<refs agents="([^"]+)"', mg)
        if match:
            refs = [r.strip() for r in match.group(1).split(",")]
            for ref in refs:
                assert ref in AGENT_IDS, (
                    f"{stem}: memory_guide refs unknown agent '{ref}'"
                )
```

- [ ] Run: `uv run pytest tests/unit/test_agent_structure.py -v`
- [ ] Verify: all tests pass (existing + 4 new × 22 agents = 88 new test cases)

---

## Sprint 4: Deploy & Verify

### Task 10: Deploy and full test

- [ ] Run full test suite: `uv run pytest tests/unit/ -v`
- [ ] Verify agent structure tests: `uv run pytest tests/unit/test_agent_structure.py -v` — all pass
- [ ] Verify content structure tests: `uv run pytest tests/unit/test_content_structure.py -v` — all pass
- [ ] Deploy: `make deploy`
- [ ] Verify deployment: `grep "memory_guide" ~/.claude/agents/system-architect.md`
- [ ] Verify RULES.md deployed: `grep "agent_memory_protocol" ~/.claude/superclaude/core/RULES.md`
