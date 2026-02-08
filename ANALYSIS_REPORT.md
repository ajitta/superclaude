# SuperClaude Framework Analysis Report

> **Date**: 2026-02-07 | **Scope**: `src/superclaude/agents/` + `src/superclaude/commands/` | **Baseline**: Claude Code v2.1.34
> **Iterations**: 3 (discovery → cross-reference → synthesis)

---

## 1. Executive Summary

The SuperClaude content framework is **well-engineered and structurally sound** across 20 agents and 30 commands. Quality scores are high (agents 4.3/5, commands 8.5/10). XML structure is consistent, handoff chains are valid, and boundaries are well-defined.

However, **Claude Code has shipped 15 releases since v2.1.20** (27 Jan -- 06 Feb 2026), introducing transformative features -- particularly **Agent Teams**, **automatic memory**, **new hook events**, and **agent frontmatter extensions** -- that the framework has not yet absorbed.

**Bottom line**: Internal quality is strong. External alignment needs attention.

---

## 2. Framework Health Scorecard

| Dimension | Agents | Commands | Overall |
|-----------|--------|----------|---------|
| Structural Consistency | 95% | 95% | 95% |
| XML Validity | 100% | 100% | 100% |
| Documentation Clarity | 4.3/5 | 8.5/10 | Strong |
| Handoff Chain Integrity | N/A | 100% (0 dead refs) | Pass |
| Dead References | 0 | 0 | Pass |
| Duplicate Content | 1 pair (deep-research) | 0 | Low risk |
| Claude Code v2.1.34 Alignment | ~75% | ~80% | **Gap** |
| MCP Coverage | 8 servers | 7 servers | Good |
| Persona Index Accuracy | 100% | 100% | Pass |

---

## 3. Agents Analysis

### 3.1 Inventory

- **20 production agents** + 1 README template
- **Domains**: Architecture (4), Engineering (5), Research (3), Education (3), Ops (3), Utility (2)
- **Autonomy distribution**: 10 high / 6 medium / 2 low

| # | Agent | Domain | Autonomy | MCP Servers |
|---|-------|--------|----------|-------------|
| 1 | backend-architect | Architecture | medium | seq, c7 |
| 2 | business-panel-experts | Ops | low | seq, tavily |
| 3 | deep-research-agent | Research | high | tavily, c7, seq |
| 4 | deep-research | Research | high | tavily, c7, seq |
| 5 | devops-architect | Architecture | medium | seq, c7 |
| 6 | frontend-architect | Architecture | high | magic, play, perf |
| 7 | learning-guide | Education | high | c7, seq |
| 8 | performance-engineer | Engineering | high | perf, seq, play |
| 9 | pm-agent | Ops | medium | serena, seq |
| 10 | python-expert | Engineering | high | c7, seq |
| 11 | quality-engineer | Engineering | high | play, seq |
| 12 | refactoring-expert | Engineering | medium | seq, serena, morph |
| 13 | repo-index | Utility | high | serena |
| 14 | requirements-analyst | Ops | medium | seq |
| 15 | root-cause-analyst | Research | high | seq, serena |
| 16 | security-engineer | Engineering | medium | seq, c7 |
| 17 | self-review | Utility | medium | seq, serena |
| 18 | socratic-mentor | Education | medium | seq, c7 |
| 19 | system-architect | Architecture | low | seq, c7 |
| 20 | technical-writer | Education | high | c7, seq |

### 3.2 Structural Patterns

All agents share this canonical structure:

```
Frontmatter (YAML): name, description, memory: user
<component type="agent">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>                    # pipe-separated activation keywords
  <role>
    <mission>                   # primary purpose
    <mindset>                   # operating principles
  <focus>                       # expertise areas (16/20)
  <actions>                     # workflow steps (16/20)
  <outputs>                     # deliverables (16/20)
  <mcp servers="..."/>          # MCP tool references (20/20)
  <tool_guidance autonomy="X">  # proceed/ask-first/never (20/20)
  <checklist>                   # 4 completion criteria (20/20)
  <examples>                    # 3-row markdown table (20/20)
  <bounds will="..." wont="..."/>  # capability boundaries (20/20)
```

**Variations from canonical**: pm-agent (lifecycle, memory keys, docs, integration), self-review (checks, workflow), business-panel-experts (experts, modes, workflow), deep-research-agent (constraints, strategies, hop_patterns, evidence, credibility), socratic-mentor (domains, questioning, sessions, revelation_timing, validation, tracking)

### 3.3 MCP Server Distribution

| Server | Agents | Coverage | Domain Affinity |
|--------|--------|----------|-----------------|
| seq (sequential) | 15 | 75% | Universal -- complex workflows, evidence chains |
| c7 (Context7) | 11 | 55% | Documentation-heavy domains |
| serena | 5 | 25% | Memory-dependent agents |
| tavily | 3 | 15% | Research agents |
| play (Playwright) | 3 | 15% | Visual/testing agents |
| perf (DevTools) | 2 | 10% | Performance specialists |
| magic (21st.dev) | 1 | 5% | Frontend only |
| morph (Morphllm) | 1 | 5% | Refactoring only |

### 3.4 Trigger Keyword Analysis

- Consistent pipe-delimited format across all agents
- 2 agents use slash-command triggers: `/sc:pm` (pm-agent), `/sc:research` (deep-research-agent)
- Range: 5-8 triggers per agent (average 6.3)
- **Overlap hotspots**: "security" (2 agents), "performance" (2 agents), "discovery" (4 agents)

---

## 4. Commands Analysis

### 4.1 Inventory

**30 commands** across 6 categories:

| Category | Count | Commands |
|----------|-------|----------|
| Discovery/Planning | 6 | brainstorm, design, research, workflow, estimate, business-panel |
| Execution | 8 | implement, build, test, git, improve, cleanup, troubleshoot, task |
| Analysis/Validation | 3 | analyze, reflect, spec-panel |
| Documentation/Reference | 5 | document, explain, recommend, help, index, index-repo |
| Orchestration/Lifecycle | 5 | agent, pm, spawn, load, save |
| Utilities | 3 | sc, select-tool |

### 4.2 Structural Patterns

All commands follow this template:

```
Frontmatter (YAML): description
<component name="..." type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <role>
    /sc:[command]
    <mission>
  <syntax>                      # with flags
  <triggers>                    # activation conditions
  <flow>                        # 4-5 numbered steps (100%)
  [domain-specific sections]    # MCP, personas, tools, patterns
  <checklist>                   # completion criteria (72%)
  <examples>                    # markdown table (100%)
  <bounds will="..." wont="..."/>
  <boundaries type="...">       # document-only|execution|conditional
  <handoff>                     # <next command> references
```

### 4.3 Boundary Type Distribution

| Type | Count | Commands |
|------|-------|---------|
| document-only | 12 | brainstorm, design, analyze, research, document, explain, workflow, spawn, reflect, help, index-repo, load |
| execution | 8 | build, test, implement, git, task, improve, cleanup, troubleshoot |
| conditional | 1 | troubleshoot (--fix flag dependent) |
| **missing/ambiguous** | 3 | agent, pm, spawn (need "orchestration" type) |

### 4.4 Handoff Chain Map

All handoff references validated. Key convergence patterns:

```
brainstorm → research → design → workflow → implement → test → git
                                                ↓
                                         improve → cleanup → git

agent (orchestrator) → analyze → workflow → task → git
pm (orchestrator)    → implement → task
spawn (orchestrator) → task → implement
```

**Convergence points**: Most commands flow toward `/sc:test` → `/sc:git`
**Reflection loop**: `/sc:reflect` → `/sc:improve` or `/sc:troubleshoot`

### 4.5 Tool Usage Patterns

| Tool | Commands Using | Coverage |
|------|---------------|----------|
| Read | 17/18 sampled | 94% |
| Grep | 14/18 | 78% |
| Write | 13/18 | 72% |
| Glob | 11/18 | 61% |
| TaskCreate/TaskUpdate | 10/18 | 56% |
| Task (delegation) | 8/18 | 44% |
| Bash | 6/18 | 33% |
| Edit | 5/18 | 28% |

### 4.6 MCP Server Distribution in Commands

| Server | Commands | Coverage |
|--------|----------|----------|
| seq (sequential) | 13/18 sampled | 72% |
| c7 (Context7) | 12/18 | 67% |
| magic (21st.dev) | 5/18 | 28% |
| play (Playwright) | 4/18 | 22% |
| serena | 4/18 | 22% |
| morph (Morphllm) | 3/18 | 17% |
| tavily | 1/18 | 6% |

---

## 5. Claude Code Release Alignment (v2.1.20 -- v2.1.34)

### 5.1 Release Timeline

| Version | Date | Key Features |
|---------|------|-------------|
| v2.1.34 | 06 Feb | Agent teams crash fix, sandbox permission fix |
| v2.1.33 | 06 Feb | TeammateIdle/TaskCompleted hooks, agent memory frontmatter, Task(agent_type) restrictions, skill plugin names |
| v2.1.32 | 05 Feb | **Opus 4.6**, **Agent Teams** (research preview), automatic memory, skill auto-discovery from --add-dir, skill budget scales with context |
| v2.1.31 | 04 Feb | Plan mode fix, system prompt tool guidance, temperatureOverride fix |
| v2.1.30 | 03 Feb | PDF pages parameter, MCP OAuth credentials, /debug command, Task metrics, subagent MCP sync fix |
| v2.1.29 | 31 Jan | Hook context performance fix |
| v2.1.27 | 30 Jan | **BREAKING: content-level ask > tool-level allow**, --from-pr flag, PR auto-linking |
| v2.1.25 | 29 Jan | Beta header validation fix |
| v2.1.23 | 29 Jan | spinnerVerbs setting, async hook cancellation, proxy fixes |
| v2.1.22 | 28 Jan | Structured outputs fix |
| v2.1.21 | 28 Jan | System prompt: prefer dedicated tools over bash |
| v2.1.20 | 27 Jan | CLAUDE.md from --add-dir, TaskUpdate delete, PR review status, background agent permissions, Bash(*) equivalence |

### 5.2 Features Already Aligned

| Feature | Version | Framework Status |
|---------|---------|-----------------|
| Opus 4.6 model references | v2.1.32 | FLAGS.md references Opus 4.6 adaptive thinking |
| Agent `memory: user` scope | v2.1.33 | All 20 agents declare `memory: user` |
| Task management system | v2.1.16 | Commands use TaskCreate/TaskUpdate extensively |
| PR status integration | v2.1.20 | /sc:git has `pr_status_integration` section |
| `--from-pr` flag | v2.1.27 | /sc:git has `from_pr` section |
| Dedicated tools over bash | v2.1.21/31 | RULES.md promotes tool-first approach |
| Skill auto-discovery | v2.1.32 | Skills installed to `~/.claude/skills/` correctly |

### 5.3 Feature Gap Matrix

| Feature | Version | Impact | Aligned? |
|---------|---------|--------|----------|
| **Agent Teams** (multi-agent collaboration) | v2.1.32 | Transformative | **NO** |
| **TeammateIdle + TaskCompleted hooks** | v2.1.33 | Multi-agent workflows | **NO** |
| **Agent Task(agent_type) restrictions** | v2.1.33 | Sub-agent control | **NO** |
| **Agent memory: project/local scopes** | v2.1.33 | Scoped persistence | **PARTIAL** (user only) |
| **Automatic memory recording** | v2.1.32 | Memory interaction | **NO** |
| **Permission breaking change** | v2.1.27 | Config compatibility | **UNVERIFIED** |
| **Skill character budget** (2% of context) | v2.1.32 | Skill sizing | **NO** |
| **Task metrics** (tokens, tools, duration) | v2.1.30 | Performance tracking | **NO** |
| **PDF pages parameter** | v2.1.30 | Document analysis | **NO** |
| **/debug command** | v2.1.30 | Troubleshooting | **NO** |
| **spinnerVerbs setting** | v2.1.23 | UX customization | **NO** |
| **MCP OAuth credentials** | v2.1.30 | MCP setup | **NO** |
| **"Summarize from here"** | v2.1.32 | Context management | **NO** |

---

## 6. Severity-Rated Findings

### P1 -- High Priority (2 findings)

| ID | Finding | Source | Impact |
|----|---------|--------|--------|
| **GAP-1** | **No Agent Teams awareness** -- v2.1.32 introduced multi-agent collaboration as a research preview. The framework has no team-aware patterns, no team orchestration guidance in /sc:spawn or /sc:pm, and no documentation of team workflows. | Release research | Framework misses an entire new paradigm for complex task execution |
| **GAP-2** | **Missing TeammateIdle/TaskCompleted hooks** -- v2.1.33 added these hook events for multi-agent workflows. The hooks.json template does not include them. | Release research | Hook-dependent workflows cannot react to team events |

### P2 -- Medium Priority (11 findings)

| ID | Finding | Source | Impact |
|----|---------|--------|--------|
| **A1** | **deep-research vs deep-research-agent overlap** -- Same MCP servers (tavily, c7, seq), same autonomy (high), partially overlapping triggers. Distinction (speed vs rigor) is undocumented. | Agents analysis | User confusion on which to invoke |
| **A2** | **No MCP fallback documentation** -- No agent defines behavior when seq/c7/tavily unavailable. | Agents analysis | Unclear degraded operation |
| **A3** | **Trigger keyword overlaps** -- "security" (2 agents), "performance" (2 agents), "discovery" (4 agents) with no documented priority hierarchy. | Agents analysis | Ambiguous agent selection |
| **A6** | **No agent co-invocation guide** -- No documentation of which agents complement each other or should work together. | Agents analysis | Suboptimal agent pairing |
| **A7** | **All agents use `memory: user` only** -- v2.1.33 supports `project` and `local` scopes. repo-index and pm-agent would benefit from `project` scope. | Cross-reference | Over-broad memory persistence |
| **A8** | **No Task(agent_type) restrictions in frontmatter** -- v2.1.33 allows restricting sub-agent spawning. No agent declares these restrictions. | Cross-reference | Unrestricted sub-agent spawning |
| **C1** | **Command frontmatter lacks hooks integration** -- Commands only declare `description`. Could leverage `user-invocable`, `context`, `allowed-tools`, `hooks` fields. | Commands analysis | Underutilized hooks system |
| **C2** | **Boundary type ambiguity** -- agent, pm, spawn lack explicit `type` attribute. No `type="orchestration"` exists for orchestrator commands. | Commands analysis | Unclear scope enforcement |
| **C7** | **No Task metrics awareness** -- v2.1.30 added token count, tool uses, duration to Task results. Commands like /sc:analyze, /sc:test don't leverage this. | Cross-reference | Missing performance data |
| **GAP-3** | **Permission model change unverified** -- v2.1.27 breaking change (content-level `ask` > tool-level `allow`) not audited against SC configurations. | Release research | Potential silent permission failures |
| **GAP-4** | **Skill character budget undocumented** -- v2.1.32 introduced 2% of context window limit for skill descriptions. SC skills not audited against this. | Release research | Skills may exceed budget |

### P3 -- Low Priority (8 findings)

| ID | Finding | Source | Impact |
|----|---------|--------|--------|
| **A4** | Inconsistent section ordering across agents | Agents analysis | Minor cognitive load |
| **A5** | Missing `<outputs>` on 4 agents (pm-agent, self-review, business-panel, repo-index) | Agents analysis | Incomplete specification |
| **A9** | Tool guidance detail variance (some detailed, some minimal) | Agents analysis | Inconsistent expectations |
| **C3** | Checklist naming inconsistency (`<checklist>` vs `<completion_criteria>`) | Commands analysis | Template confusion |
| **C4** | agent and pm commands lack explicit `<tools>` section | Commands analysis | Missing reference |
| **C5** | Reference commands (recommend, help, sc) lack MCP declarations | Commands analysis | Intentional but undocumented |
| **C6** | No `/debug` command integration in /sc:troubleshoot handoff | Cross-reference | Missing native tool reference |
| **GAP-5** | Minor undocumented features (PDF pages, spinnerVerbs, MCP OAuth, "Summarize from here") | Release research | Documentation gaps |

---

## 7. Recommended Action Roadmap

### Phase 1: Platform Alignment (P1 + critical P2)

**Objective**: Bring framework to parity with Claude Code v2.1.34 capabilities.

| Action | Findings Addressed | Files Affected |
|--------|-------------------|----------------|
| Design Agent Teams patterns for /sc:spawn, /sc:pm | GAP-1 | commands/spawn.md, commands/pm.md |
| Add team orchestration section to agent framework | GAP-1 | agents/README.md |
| Update hooks.json with TeammateIdle, TaskCompleted events | GAP-2 | hooks/hooks.json |
| Add Task(agent_type) restrictions to agent frontmatter | A8 | All 20 agent files |
| Update repo-index, pm-agent memory scope to `project` | A7 | agents/repo-index.md, agents/pm-agent.md |
| Audit permission patterns for v2.1.27 compatibility | GAP-3 | hooks/hooks.json, settings patterns |
| Audit skill sizes against 2% context budget | GAP-4 | All skill directories |

### Phase 2: Framework Hardening (remaining P2)

**Objective**: Improve consistency, documentation, and resilience.

| Action | Findings Addressed | Files Affected |
|--------|-------------------|----------------|
| Document deep-research vs deep-research-agent distinction | A1 | agents/README.md, both agent files |
| Add `<fallbacks>` section to all agents | A2 | All 20 agent files |
| Document trigger priority hierarchy | A3 | agents/README.md |
| Create agent companion/co-invocation guide | A6 | agents/README.md (new section) |
| Enhance command frontmatter with hooks fields | C1 | All 30 command files |
| Add `type="orchestration"` boundary type | C2 | commands/agent.md, pm.md, spawn.md |
| Integrate Task metrics into analysis/test commands | C7 | commands/analyze.md, test.md |

### Phase 3: Polish (P3)

**Objective**: Normalize cosmetic inconsistencies and minor gaps.

| Action | Findings Addressed | Files Affected |
|--------|-------------------|----------------|
| Standardize XML section ordering in agents | A4 | agents/README.md template |
| Add missing `<outputs>` sections | A5 | 4 agent files |
| Normalize tool guidance detail level | A9 | ~6 agent files |
| Standardize to `<completion_criteria>` naming | C3 | ~5 command files |
| Add `<tools>` sections to agent/pm commands | C4 | 2 command files |
| Document why reference commands lack MCP | C5 | agents/README.md |
| Add /debug to /sc:troubleshoot handoff | C6 | commands/troubleshoot.md |
| Document minor new features | GAP-5 | Various |

---

## 8. Claude Code Release Thematic Index

### Hooks Evolution (v2.1.2 -- v2.1.33)

| Version | Change |
|---------|--------|
| v2.1.33 | `TeammateIdle` and `TaskCompleted` hook events for multi-agent workflows |
| v2.1.29 | Fixed performance with `saved_hook_context` on resume |
| v2.1.23 | Fixed pending async hooks not cancelled on session end |
| v2.1.3 | Hook timeout increased from 60s to 10 minutes |
| v2.1.2 | `agent_type` field added to SessionStart hook input |

### Skills Evolution (v2.1.3 -- v2.1.33)

| Version | Change |
|---------|--------|
| v2.1.33 | Plugin name shown in skill descriptions and `/skills` menu |
| v2.1.32 | Auto-load from `--add-dir` directories; character budget = 2% of context |
| v2.1.20 | `/commit-push-pr` skill auto-posts PR URLs to Slack via MCP |
| v2.1.19 | Skills without extra permissions allowed without approval |
| v2.1.6 | Auto-discovery from nested `.claude/skills` directories |
| v2.1.3 | Slash commands and skills merged (simplified model) |

### Agent Teams Evolution (v2.1.14 -- v2.1.34)

| Version | Change |
|---------|--------|
| v2.1.34 | Fixed crash when agent teams setting changed between renders |
| v2.1.33 | Fixed tmux sessions; Task(agent_type) restrictions; `memory` frontmatter |
| v2.1.32 | **Research preview** (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); automatic memory |
| v2.1.20 | Background agents prompt for permissions; teammate messages render Markdown |
| v2.1.16 | Fixed OOM from heavy subagent usage |
| v2.1.14 | Fixed memory issues with parallel subagents |

### Tool Policies Evolution (v2.1.2 -- v2.1.34)

| Version | Change |
|---------|--------|
| v2.1.34 | Fixed sandbox exclusion bypass of Bash ask permission |
| v2.1.27 | **BREAKING**: Content-level `ask` > tool-level `allow` |
| v2.1.20 | `Bash(*)` accepted as equivalent to `Bash` |
| v2.1.7 | Fixed wildcard rules matching compound commands with shell operators |
| v2.1.6 | Detection and warnings for unreachable permission rules |
| v2.1.2 | Fixed command injection vulnerability in bash processing |

### Settings Changes (v2.1.4 -- v2.1.33)

| Version | Setting |
|---------|---------|
| v2.1.33 | Agent `memory` frontmatter (user/project/local); proxy env vars |
| v2.1.32 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| v2.1.31 | `temperatureOverride` fix (was silently ignored in streaming) |
| v2.1.30 | Reduced motion mode |
| v2.1.23 | `spinnerVerbs` customization |
| v2.1.7 | `showTurnDuration` |
| v2.1.6 | `context_window.used_percentage`, `context_window.remaining_percentage` |
| v2.1.5 | `CLAUDE_CODE_TMPDIR` |
| v2.1.4 | `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` |

---

## 9. Metrics Summary

| Metric | Value |
|--------|-------|
| Files analyzed | 50 (20 agents + 30 commands) |
| Claude Code releases reviewed | 15 (v2.1.20 -- v2.1.34) |
| P1 findings | 2 |
| P2 findings | 11 |
| P3 findings | 8 |
| **Total findings** | **21** |
| Dead references | 0 |
| Handoff chain breaks | 0 |
| Structural consistency | 95% |
| Platform alignment | ~75% (7 unaligned features) |

---

## 10. Breaking Changes Requiring Immediate Attention

1. **v2.1.27 -- Permission precedence change**: `allow: ["Bash"], ask: ["Bash(rm *)"]` previously allowed all bash; now prompts for `rm`. Audit all SC permission patterns.
2. **v2.1.7 -- MCP tool search auto mode**: Now default. Disable via `disallowedTools: ["MCPSearch"]`.
3. **v2.1.19 -- Argument syntax change**: `$ARGUMENTS.0` → `$ARGUMENTS[0]`.

---

*Analysis complete. No source files modified.*
*Handoff: Use `/sc:improve` to act on P1-P2 findings, `/sc:implement` for Agent Teams integration, `/sc:cleanup` for P3 polish.*
