# SuperClaude Framework Improvement — Design Specification

> **Source**: `docs/research/claude-code-skills-design-guide.md` (Anthropic internal design principles, cross-verified with official sources)
> **Scope**: Full framework — skills, agents, commands, modes, core, mcp
> **Method**: VS (k=5, tau=0.08) + 3-agent parallel audit + 3-agent self-review
> **Date**: 2026-03-29
> **Rev**: 3 (Tier 1+2 implemented, English translation, final metrics)
> **Status**: Tier 1+2 IMPLEMENTED | Tier 3 NOT STARTED

---

## Scope Boundary

The guide's 6 principles were written **specifically for Skills**. Extensions to agents/commands/core in this spec are **independent reasoning**, not direct guide recommendations.

| Scope | Authority Level |
|---|---|
| Skill improvements | Guide direct recommendation |
| Agent/Command `<gotchas>` | Independent extension (logical extrapolation of guide principles) |
| Core file trimming | Independent judgment (general token efficiency) |

---

## Format Convention

SuperClaude uses XML tags + simple markdown. Guide's pure Markdown recommendations are mapped to SC's `<component>` structure. **Note**: This is format mapping only. Content strategy is discussed in Gap Analysis.

| Guide (Markdown) | SC Format (XML) | Note |
|---|---|---|
| `## Gotchas` | `<gotchas>` | New XML tag (skills/agents/commands) |
| `## Available Files` | `<references>` | New XML tag (skills only) |
| `## Core Rules` | Existing `<flow>`, `<tool_guidance>` | Dedup only |
| `## Overview` | Existing `<role><mission>` | No change |

---

## Gap Analysis (Pre-Implementation)

| Guide Principle | SC State Before | Gap | Scope |
|---|---|---|---|
| P1: Skills are folders | Compliant (5/5 have folders) | Low | Skills |
| P2: Don't repeat model knowledge | Skills embed general instructions | **Medium** | Skills (guide) |
| P3: Gotchas = highest value | 3/5 skills had equivalent content under non-standard tags | **Medium** | Skills (guide) |
| P4: Progressive disclosure | 2/5 used references/ | **Medium** | Skills (guide) |
| P5: Description = trigger | 1/5 excellent (verbalized-sampling) | **Medium** | Skills (guide) |
| P6: Hooks for safety | 2/5 destructive skills lacked hooks | **Medium** | Skills (guide) |

### Skill Type Coverage (Reference)

| Anthropic Skill Type (9) | SC Coverage | Note |
|---|---|---|
| CI/CD | ship, finishing-a-development-branch | Skills |
| Code Review/Quality | confidence-check, simplicity-coach | Skills |
| Library/API Reference | verbalized-sampling | Skill |
| Product Verification | quality-engineer agent, /sc:test | Not a skill gap |
| Business Automation | /sc:business-panel | Not a skill gap |
| Code Scaffolding | Authoring rules exist, not as skill | Potential |
| Runbook | root-cause-analyst agent, /sc:troubleshoot | Not a skill gap |
| Infrastructure Operations | devops-architect agent | Not a skill gap |

> The 9 types are a skill classification system. Domains already covered by agents/commands are not skill gaps.

---

## Implementation Results (Tier 1 + 2)

### Final Metrics

| Metric | Before | After | Status |
|---|---|---|---|
| `<gotchas>` in skills | 0/5 standard tag | **5/5** | DONE |
| `<gotchas>` in agents | 0/3 target | **3/3** | DONE |
| Safety hooks (destructive skills) | 0/2 | **2/2** | DONE |
| RULES.md | 169 lines | **124 lines** (-27%) | DONE |
| research.md | 140 lines | **70 lines** (-50%) | DONE |
| ship SKILL.md | 87 lines | **63 lines** (-28%) | DONE |
| confidence-check SKILL.md | 61 lines | **51 lines** (-16%) | DONE |
| verbalized-sampling SKILL.md | 158 lines | **80 lines** (-49%) | DONE |
| Tests | 1,673 passed | **1,673 passed** | NO REGRESSION |
| Net lines | | **-175** (151 added, 326 deleted) | |
| Korean in modified files | N/A | **0 occurrences** | CLEAN |

### Files Changed (15 modified + 3 created)

**Skills** (5 modified + 3 new):
- ship/SKILL.md — gotchas, triggers, hooks, $ARGUMENTS, progressive disclosure
- confidence-check/SKILL.md — gotchas, triggers, progressive disclosure
- finishing-a-dev-branch/SKILL.md — gotchas, triggers, hooks
- simplicity-coach/SKILL.md — gotchas
- verbalized-sampling/SKILL.md — gotchas (from critical_rules), progressive disclosure
- NEW: ship/references/conventions.md
- NEW: confidence-check/references/checks-detail.md
- NEW: verbalized-sampling/references/paper-methodology.md

**Agents** (4 modified):
- security-engineer.md — gotchas + 6 trigger keywords
- frontend-architect.md — gotchas
- backend-architect.md — gotchas
- performance-engineer.md — 4 trigger keywords

**Core** (1 modified): RULES.md (169→124, -27%)
**Commands** (1 modified): research.md (140→70, -50%)
**Rules** (3 modified): agent-authoring.md, command-authoring.md, skill-authoring.md

---

## VS Distribution: 5 Perspectives (Design Phase Record)

### [1] Gotchas Standardization + Gap-Fill — p=0.32 ★ IMPLEMENTED

**Status correction**: Not "zero gotchas" but "non-standard tags scattered":
- ship: `<safety>` (equivalent) → renamed to `<gotchas>`
- finishing-a-dev-branch: `<constraints>` (kept) + `<gotchas>` added separately
- verbalized-sampling: `<critical_rules>` → replaced with `<gotchas>`
- confidence-check: gap → `<gotchas>` added
- simplicity-coach: gap → `<gotchas>` added

**Tag preservation**: `<self_checks>` (deep-researcher) and `<exploration_budget>` (root-cause-analyst) are NOT gotchas — they are runtime self-evaluation protocols and resource constraints respectively. Kept as-is.

**Growth mechanism**: R14 Correction Capture writes to MEMORY.md, not content files. Gotchas growth is **manual**: developers add entries when repeated failures are observed.

### [2] Skill Progressive Disclosure — p=0.27 ★ IMPLEMENTED

Skills-only (3-level loading). Commands use **content externalization** pattern instead (not the same mechanism).

### [3] Code Scaffolding Skill (new-content) — p=0.20 — NOT IMPLEMENTED (Tier 3)

**YAGNI note**: Authoring rules already exist in `.claude/rules/`. Build only when actual demand arises.

### [4] Safety Hooks for Destructive Skills — p=0.13 ★ PARTIALLY IMPLEMENTED

- ship hooks: DONE
- finishing-a-dev-branch hooks: DONE
- /careful skill: NOT IMPLEMENTED (Tier 3)
- Commands cannot have hooks (command-authoring.md: forbidden fields)

### [5] Description Trigger Optimization — p=0.08 ★ IMPLEMENTED

- Skill descriptions: "pushy" strategy (undertrigger prevention)
- Agent descriptions: "precise" strategy (routing accuracy) — different from skills

---

## Part 2: Full Framework Audit

> 3-agent parallel audit → 3-agent self-review verified

### P2: Repeated Model Knowledge

> **Methodology note**: "Repeated %" values are subjective estimates, not precise measurements. Directional signal (which files are more generic) is meaningful; specific numbers have ~15pp margin of error.

| Content Type | Files | Avg Repeated % (est.) | Worst Offender | Note |
|---|---|---|---|---|
| **Core** | 3 | ~30% | RULES.md (35%, was 169 lines) | Always loaded |
| **Agents** | 8 sampled / 22 total | ~35% | security-engineer (~45%) | On delegation |
| **Commands** | 10 sampled / 33 total | ~22% | troubleshoot.md (~40%) | On invocation |
| **Skills** | 5 | ~20% | ship | On activation |
| **Modes** | 7 | ~10% | Business_Panel (~20%) | On-demand |
| **MCP** | 8 | ~8% | Context7 (~10%) | On-demand |

### Modes & MCP

| Category | Verdict | Action |
|---|---|---|
| **Modes** (7 files, 36-63 lines) | HEALTHY | No changes needed |
| **MCP** (8 files, 57-118 lines) | EXCELLENT | No changes needed |

### P3: Gotchas Coverage (Post-Implementation)

| Content Type | Standard `<gotchas>` tag | Coverage |
|---|---|---|
| Skills (5) | **5/5** | **100%** |
| Agents (3 target) | **3/3** | **100% of target** |
| Commands (1 target) | **1/1** (research.md) | **100% of target** |

### P5: Description Trigger Quality (Post-Implementation)

Skills: 3/5 with explicit trigger keywords (ship, confidence-check, finishing-a-dev-branch)
Agents: security-engineer and performance-engineer triggers expanded

---

## Remaining Work (Tier 3 — Not Started)

| # | Task | Target | Effort | Priority |
|---|---|---|---|---|
| **T9** | /careful safety skill (new) | skills/ (new) | ~1h | Low-Medium |
| **T10** | new-content scaffolding skill — build only when demand arises | skills/ (new) | ~3h | Low |

---

## Token Savings (Actual)

| Change | Lines Saved | Loading |
|---|---|---|
| RULES.md trim (169→124) | 45 lines (~180 tokens) | **Every session** |
| research.md trim (140→70) | 70 lines (~280 tokens) | On invocation |
| ship SKILL.md (87→63) | 24 lines (~96 tokens) | On activation |
| confidence-check (61→51) | 10 lines (~40 tokens) | On activation |
| verbalized-sampling (158→80) | 78 lines (~312 tokens) | On activation |
| **Net deleted** | **175 lines** | |

> Per-session savings (always-loaded): ~180 tokens from RULES.md
> Per-activation savings: variable, up to ~450 tokens per skill invocation

---

## Validation

| Metric | Baseline | Result | Command |
|---|---|---|---|
| Test suite | 1,673 pass | **1,673 pass** | `python -m pytest tests/unit/ -v` |
| Korean in files | N/A | **0** | `grep -rn '[가-힣]' src/superclaude/...` |
| `<gotchas>` skills | 0/5 | **5/5** | `grep -l gotchas skills/*/SKILL.md` |
| Safety hooks | 0/2 | **2/2** | `grep -l 'hooks:' skills/*/SKILL.md` |

### Regression Detection

- Removed RULES.md rules archived as `<!-- archived 2026-03-29 -->` comment for 30-day observation
- Archive lists: [R07] Trust, [R08] Language, [R11] Honesty, plus merged/removed sections
- Restore if behavioral regression observed

### `<gotchas>` Test Policy

- **Optional** (requiring it would break 40+ files immediately)
- Added as "recommended" in authoring rules
- Consider making required when coverage reaches 80%+

---

## Self-Review Findings Log

> 10 findings from Rev 1 → Rev 2 correction

| # | Finding | Severity | Resolution |
|---|---|---|---|
| C1 | Command hooks architecture violation | Critical | Removed. Commands cannot have hooks |
| C2 | "Zero gotchas" overstated | High | 3/5 had equivalent content; reframed as "standardize + gap-fill" |
| C3 | `<self_checks>`/`<exploration_budget>` are not gotchas | High | Migration withdrawn. Existing tags preserved |
| C4 | Token savings 1,190 inflated | Medium | Split: always-loaded ~180 vs on-demand variable |
| C5 | No validation methodology | Medium | Validation section added |
| I1 | Guide scope inflation | Medium | Scope Boundary section added |
| I2 | Progressive disclosure does not apply to commands | Medium | Renamed to "content externalization" for commands |
| I3 | R14 does not feed into gotchas | Medium | Manual growth mechanism specified |
| I4 | Description strategy differs: skill vs agent | Medium | Pushy (skills) vs Precise (agents) separated |
| I5 | security-engineer 60% overestimate | Low | Corrected to ~45% |

### Post-Implementation Review Findings

| # | Finding | Severity | Resolution |
|---|---|---|---|
| P1 | Korean strings in 8 modified files | High | All translated to English |
| P2 | Duplicate `<references>` in verbalized-sampling | Medium | Consolidated to single block |
| P3 | `<gotchas>` placement mismatch (template vs agents) | Low | Template updated to match implementation |
| P4 | RULES.md archive comment incomplete | Low | Expanded to list all removed sections |
