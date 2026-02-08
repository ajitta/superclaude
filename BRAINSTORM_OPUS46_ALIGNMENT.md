# SuperClaude Opus 4.6 Alignment — Requirements Specification

> Generated: 2026-02-08 | Research: 4 parallel streams + codebase analysis
> Scope: `src/superclaude/[agents,commands,modes,mcp,scripts,skills,hooks,core]`
> Boundary: Specification only — no implementation

---

## Executive Summary

Research across 5 streams (Opus 4.6 official docs, Claude Code v2.1.33-37 changelog, community forums/blogs, Context7 docs, codebase gap analysis) reveals a **paradigm shift**: Opus 4.6 flips the behavioral challenge from **laziness → overeagerness**. SuperClaude's content framework, optimized for earlier models where "push harder" was needed, must rebalance toward **"exercise restraint."**

### Key Findings

| Stream | Top Insight |
|--------|------------|
| Opus 4.6 Official | Adaptive thinking replaces budget_tokens; effort parameter GA; prefill removal is BREAKING |
| Claude Code v2.1.33-37 | Agent Teams experimental; TeammateIdle/TaskCompleted hooks; Fast Mode; async hooks |
| Community Forums | 25-50% higher token consumption; overeagerness complaints; CLAUDE.md <300 lines best practice |
| Context7 Docs | Tool Search Tool with defer_loading (85% token reduction); context engineering "right altitude" |
| Codebase Analysis | 2 deprecated MCPs; duplicate research agents; missing handoffs; version refs stale |

### Dominant Theme

**Anti-overeagerness calibration.** Opus 4.6 tends to over-engineer, create extra files, add unnecessary abstractions, and overtrigger on directive language ("ALWAYS use X", "Default to using"). The framework must counterbalance this tendency, not amplify it.

---

## Requirements by Directory

### 1. `core/` — FLAGS.md, PRINCIPLES.md, RULES.md, RESEARCH_CONFIG.md

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| C1 | HIGH | Update FLAGS.md version note `2.1.33+` → `2.1.37+` | Accuracy |
| C2 | **CRITICAL** | Add anti-overeagerness guidance to FLAGS.md execution section | Opus 4.6 overengineers by default |
| C3 | MEDIUM | Add `--fast` flag documentation (v2.1.36+, same model, faster output) | New feature undocumented |
| C4 | MEDIUM | Document Tool Search Tool / `defer_loading` in MCP auto mode section | 85% token reduction opportunity |
| C5 | LOW | Note 25-50% higher token consumption for Opus 4.6 in effort section | User awareness |
| C6 | MEDIUM | Document `disable-model-invocation` skill field | New v2.1.37 feature |
| C7 | **HIGH** | Add restraint principle to PRINCIPLES.md: "Restraint > Enthusiasm" | Core behavioral calibration |
| C8 | LOW | Add context engineering principle: "Right altitude" guidance | Best practice from research |
| C9 | **CRITICAL** | Strengthen RULES.md `anti_over_engineering` for Opus 4.6 | Model needs MORE restraint, not less |
| C10 | MEDIUM | Anti-laziness dial-back rule — avoid "ALWAYS use X" patterns | Causes Opus 4.6 overtriggering |
| C11 | LOW | Clarify FLAGS.md effort section: "Claude 4 models" → "Opus 4.6" specificity | Ambiguous reference |
| C12 | MEDIUM | Add experimental feature flag docs for Agent Teams in FLAGS.md | TeammateIdle/TaskCompleted undocumented |
| C13 | LOW | Review RESEARCH_CONFIG.md for undefined/aspirational config keys | Lines 10, 34, 89 reference unimplemented features |

### 2. `agents/` — 20+ Agent Definitions

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| A1 | **CRITICAL** | Consolidate duplicate research agents: `deep-research.md` + `deep-research-agent.md` | >80% overlap, user confusion, maintenance burden |
| A2 | HIGH | Audit all agents for anti-laziness trigger words causing Opus 4.6 overtriggering | "Default to using", "ALWAYS prefer" patterns |
| A3 | MEDIUM | Review `whenToUse` sections — guide without mandating | Prevent Opus 4.6 overactivation |
| A4 | LOW | Add `color` field to agent frontmatter (v2.1.37 visual support) | New platform feature |
| A5 | LOW | Add negative examples (when NOT to use) for Opus 4.6 restraint | Behavioral calibration |
| A6 | LOW | Add explicit `autonomy` level to all 20 agents | Only some have it; framework defined in README but not applied |
| A7 | LOW | Add cross-references to related commands (e.g., system-architect ↔ /sc:design) | Discoverability |

### 3. `commands/` — 30 Slash Commands

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| CMD1 | **HIGH** | Add missing `<handoff>` section to `sc.md` and `select-tool.md` | Breaks workflow continuity (28/30 have it) |
| CMD2 | MEDIUM | Update version refs in task.md, git.md → `2.1.37+` | Stale references |
| CMD3 | LOW | Audit commands for anti-laziness trigger patterns | Opus 4.6 overtriggering prevention |
| CMD4 | LOW | Add token efficiency notes to high-consumption commands | Opus 4.6 uses 25-50% more tokens |
| CMD5 | LOW | Clarify `index-repo.md` vs `index.md` relationship | Two index commands create confusion |
| CMD6 | LOW | Standardize internal section ordering across all commands | Some follow different order patterns |

### 4. `modes/` — 7 Behavioral Modes

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| M1 | MEDIUM | Update MODE_Token_Efficiency.md for Opus 4.6 consumption patterns | 25-50% higher usage makes this mode more critical |
| M2 | LOW | Review/remove deprecated symbol mappings (v="5.1" deprecation) | Timeline unclear, version mismatch |
| M3 | LOW | Add Opus 4.6 overeagerness awareness to relevant modes | Behavioral calibration |
| M4 | LOW | Create modes/README.md overview file | Missing (agents, commands, skills, hooks all have READMEs) |

### 5. `mcp/` — MCP Server Docs

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| MCP1 | **HIGH** | Remove or clearly deprecate MCP_Mindbase.md and MCP_Airis-Agent.md | Known deprecated servers |
| MCP2 | **HIGH** | Add deprecation warnings in FLAGS.md `<mcp>` section with migration paths | Users can still reference deprecated servers via flags |
| MCP3 | MEDIUM | Add Tool Search Tool documentation (defer_loading, 85% token reduction) | Major optimization opportunity |
| MCP4 | MEDIUM | Add `<fallback_chains>` to all MCP docs (Primary → Fallback1 → Native) | Currently only show single fallback |
| MCP5 | LOW | Review all MCP docs for version accuracy | General maintenance |
| MCP6 | LOW | Standardize MCP reference format: YAML in skills vs XML in agents/commands | Inconsistency across component types |
| MCP7 | LOW | Create mcp/README.md overview file | Missing |

### 6. `scripts/` — Shell/Python Utilities

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| S1 | LOW | Evaluate session-end learning script | No SessionEnd hook in Claude Code yet; future-prep |
| S2 | LOW | Review context_reset.py for v2.1.37 compatibility | Maintenance |

### 7. `skills/` — Skill Implementations

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| SK1 | MEDIUM | Update confidence-check skill — resolve `@deprecated` annotation | Unclear status |
| SK2 | MEDIUM | Document `disable-model-invocation` field support in SKILL.md manifests | New v2.1.37 capability |
| SK3 | LOW | Consider continuous learning skill for cross-session pattern capture | Enhancement opportunity |

### 8. `hooks/` — Hook System

| ID | Pri | Requirement | Rationale |
|----|-----|-------------|-----------|
| H1 | MEDIUM | Add TeammateIdle and TaskCompleted hook events (experimental) | Requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 |
| H2 | MEDIUM | Update hooks.json schema version `2.1.33` → `2.1.37` | Version alignment |
| H3 | LOW | Document async hook support (v2.1.34+) | New capability |
| H4 | LOW | Add PreCompact and PermissionRequest hook events if available | New event types |

---

## Feasibility Assessment

| Category | Risk | Test Impact | Breaking Changes |
|----------|------|-------------|------------------|
| All changes | **LOW** | **NONE** (225 tests unaffected) | **NONE** (docs/content only) |
| Deployment | Standard `make deploy` | — | — |
| Rollback | Git revert | — | — |

### Multi-Persona Validation

| Persona | Assessment |
|---------|------------|
| **Architect** | Anti-overeagerness is #1 priority. Opus 4.6's tendency to over-engineer directly conflicts with YAGNI. Strengthen core config files first. |
| **QA** | All docs-only — zero code risk. Content quality is the concern, not regression. |
| **Performance** | 25-50% token increase + Tool Search Tool's 85% reduction = high-impact optimizations. Token efficiency mode update is important. |
| **Security** | No security implications. All documentation/configuration changes. |
| **DevOps** | Standard maintenance. hooks.json schema update backward compatible. |

---

## Implementation Waves

| Wave | Theme | Requirements | Effort | Dependencies |
|------|-------|-------------|--------|--------------|
| **1** | Anti-overeagerness core | C2, C7, C9, C10 | Medium | None — highest impact |
| **2** | Structural fixes | A1, CMD1, MCP1, MCP2 | Medium | None — cleanup debt |
| **3** | Version alignment | C1, C11, C12, CMD2, H2 | Low | None — quick wins |
| **4** | Token & MCP optimization | C3, C4, C5, M1, MCP3, MCP4 | Medium | Wave 1 (anti-overeagerness context) |
| **5** | Systematic audit | A2, A3, CMD3 | High | Wave 1 (audit criteria from anti-overeagerness) |
| **6** | Feature additions | C6, SK1, SK2, H1, H3 | Medium | Wave 3 (version alignment) |
| **7** | Polish & consistency | A4-A7, CMD4-CMD6, M2-M4, MCP5-MCP7, S1-S2, SK3, H4, C8, C13 | Low | All prior waves |

### Wave Execution Strategy

- **Waves 1-3**: Can run in parallel (no dependencies between them)
- **Wave 4**: After Wave 1 (needs anti-overeagerness context established)
- **Wave 5**: After Wave 1 (audit criteria depend on anti-overeagerness principles)
- **Wave 6**: After Wave 3 (version alignment needed first)
- **Wave 7**: After all (polish pass)

---

## Priority Summary

### CRITICAL (do first)
1. **C2 + C9**: Anti-overeagerness in FLAGS.md and RULES.md
2. **A1**: Consolidate duplicate research agents

### HIGH (do soon)
3. **C7**: Restraint principle in PRINCIPLES.md
4. **CMD1**: Missing handoff sections
5. **MCP1 + MCP2**: Deprecated MCP cleanup + warnings
6. **C1**: Version alignment

### MEDIUM (important but not urgent)
7. Token efficiency updates (C3, C4, M1, MCP3)
8. Agent audit for overtriggering (A2, A3)
9. Hooks & skills updates (H1, H2, SK1, SK2, C6, C12)

### LOW (polish)
10. Everything in Wave 7

---

## Handoff Options

| Next Command | When to Use |
|-------------|-------------|
| `/sc:workflow` | Break waves into implementation plan with task dependencies |
| `/sc:implement --delegate` | Execute waves in parallel with sub-agents |
| `/sc:design` | If architectural decisions needed (e.g., research agent consolidation strategy) |
| `/sc:task` | Execute individual waves sequentially |

---

## Appendix: Research Sources

| Source Type | Details |
|------------|---------|
| Official Docs | Anthropic API docs, Claude Code changelog, model card |
| Community | Forums, blog posts, GitHub discussions on Opus 4.6 behavior |
| Context7 | Claude platform docs, Claude Code repo, Everything Claude Code community |
| Codebase | Full analysis of all 150+ files across 8 directories |

**Total requirements: 42** (7 CRITICAL/HIGH, 13 MEDIUM, 22 LOW)
