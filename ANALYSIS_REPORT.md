# Core + Modes + MCP Quality Analysis Report

**Target:** `src/superclaude/core/` (4 files) + `src/superclaude/modes/` (8 modes + README) + `src/superclaude/mcp/` (8 MCP docs + README)
**Focus:** Quality
**Date:** 2026-02-26
**Baseline:** v4.3.0+ajitta

---

## Executive Summary

The three supporting directories are **functionally sound with intentional structural variation**. Core files are dense behavioral references. Modes use a uniform `<component type="mode">` schema. MCP docs vary dramatically in depth — Serena/Tavily are comprehensive (78-119 lines) while 5 others are minimal (24-32 lines).

**8 findings** require attention (0 critical, 3 moderate, 5 minor).

| Severity | Count | Category |
|----------|-------|----------|
| 🔴 Critical | 0 | — |
| 🟡 Moderate | 3 | RESEARCH_CONFIG misplaced type, FLAGS.md indentation, MCP depth imbalance |
| 🟢 Minor | 5 | Missing bounds on core files, README description drift, component closing tags, mode README missing RESEARCH_CONFIG, Chrome-DevTools naming |

---

## 1. Core Directory (4 files)

### Schema

| File | Type | Priority | Lines | Component Name |
|------|------|----------|-------|----------------|
| FLAGS.md | core | high | 93 | `flags` |
| PRINCIPLES.md | core | high | 49 | `principles` |
| RULES.md | core | critical | 68 | `rules` |
| BUSINESS_SYMBOLS.md | core | medium | 59 | `business-symbols` |

All 4 files use `<component type="core">` — consistent.

### Section Coverage

| Section | FLAGS | PRINCIPLES | RULES | BUSINESS_SYMBOLS |
|---------|-------|------------|-------|------------------|
| `<role>` + `<mission>` | ✅ | ✅ | ✅ | ✅ |
| `<bounds>` | ❌ | ❌ | ❌ | ❌ |
| Priority attribute | high | high | critical | medium |
| Version-agnostic note | ❌ | ✅ | ✅ | ❌ |

**Notable:** No core file has `<bounds>` — modes and commands all do. This is consistent within core (core files are behavioral references, not executable commands) but creates a cross-directory inconsistency.

### FLAGS.md Structural Issues

1. **`<priority_rules>` indentation** (line 75): This section breaks out of the component's indentation pattern. All other sections are indented 2 spaces inside `<component>`, but `<priority_rules>` starts at column 0:
   ```xml
   </output>        ← line 73, indented

   <priority_rules>  ← line 75, NOT indented (breaks pattern)
   ```

2. **Stray `</output>` closing tag** (line 93): The file ends with `</component>\n</output>` — the `</output>` tag has no matching opening tag in FLAGS.md. This is a vestige from the CLAUDE.md injection chain where it was wrapped in `<output>` context, but it should not be in the source file.

### RULES.md Structural Issues

1. **Stray `</output>` closing tag** (line 69): Same issue as FLAGS.md — ends with `</output>` after `</component>`.

### PRINCIPLES.md — Clean

No issues found. Well-structured, appropriately concise.

### BUSINESS_SYMBOLS.md — Clean

No issues found. Appropriate depth for a symbol reference.

---

## 2. Modes Directory (8 modes + README)

### Schema

| Mode | Lines | Sections |
|------|-------|----------|
| TOKEN_EFFICIENCY | 65 | role, behaviors, context_limits, symbols, abbreviations, examples, compaction, bounds |
| DEEP_RESEARCH | 51 | role, thinking, communication, priorities, process, integration, extended_thinking, quality, output, bounds |
| TASK_MANAGEMENT | 56 | role, hierarchy, memory_ops, execution, tool_select, memory_schema, task_api, bounds |
| BUSINESS_PANEL | 43 | role, activation, experts, modes, selection, synthesis, mcp, bounds |
| ORCHESTRATION | 41 | role, behaviors, tool_matrix, infra_validation, resources, parallel, bounds |
| BRAINSTORMING | 24 | role, behaviors, outcomes, examples, bounds |
| INTROSPECTION | 24 | role, behaviors, outcomes, examples, bounds |
| RESEARCH_CONFIG | 102 | role, defaults, parallel_rules, strategies, hop_config, confidence, reflection, memory, tool_routing, gates, credibility, depth_profiles, output_formats, replanning, optimization, errors, metrics |

### Section Coverage

| Section | Token | Deep | Task | Biz | Orch | Brain | Intro | ResConf |
|---------|-------|------|------|-----|------|-------|-------|---------|
| `<role>` + `<mission>` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `<behaviors>` | ✅ | — | — | — | ✅ | ✅ | ✅ | — |
| `<bounds>` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `<examples>` | ✅ | — | — | — | — | ✅ | ✅ | — |

**Pattern:** Complex modes (Token, Deep, Task, Orchestration) use domain-specific sections. Simple modes (Brainstorming, Introspection) use the `behaviors/outcomes/examples/bounds` template. This is appropriate — each mode's structure serves its complexity.

### RESEARCH_CONFIG Type Mismatch

`RESEARCH_CONFIG.md` declares `type="core"` but lives in `modes/`:
```xml
<component name="research-config" type="core" priority="medium">
```

This creates a type/location mismatch:
- Location says "mode" (in `modes/` directory)
- XML says "core" (in `type` attribute)
- Content is research strategy configuration — neither a behavioral mode nor a core behavioral reference
- Missing `<bounds>` (all 7 actual modes have bounds; core files don't — so it follows core pattern)

### Mode Bounds Consistency

All 7 modes use identical `fallback` phrasing: `"Revert to default behavior when inapplicable"`. This is good consistency.

### README Coverage

The modes README lists 7 modes matching FLAGS.md `<modes>` section. However, RESEARCH_CONFIG.md is not mentioned in the README — it's effectively hidden documentation.

---

## 3. MCP Directory (8 docs + README)

### Schema

| MCP Server | Lines | Depth |
|------------|-------|-------|
| Serena | 119 | Comprehensive: init, tools_active(20), tools_thinking(5), choose, memory_patterns, config, examples |
| Tavily | 78 | Comprehensive: choose, capabilities, tools(5), search_patterns, flows, strategies, errors, examples |
| Token Efficiency* | — | (mode, not MCP) |
| Chrome-DevTools | 32 | Standard: role+flags+note, choose, examples |
| Sequential | 28 | Minimal: role, choose, examples |
| Morphllm | 28 | Minimal: role, choose, examples |
| Playwright | 28 | Minimal: role, choose, examples |
| Magic | 27 | Minimal: role, choose, examples |
| Context7 | 24 | Minimal: role, choose, examples |

### Section Coverage

| Section | Serena | Tavily | DevTools | Seq | Morph | Play | Magic | C7 |
|---------|--------|--------|---------|-----|-------|------|-------|-----|
| `<role>` + `<mission>` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `<choose>` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `<examples>` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `<tools>` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `<errors>` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `<bounds>` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Notable:** No MCP doc has `<bounds>`. This is consistent within the MCP directory (they're reference docs, not executable) but contrasts with modes (all have bounds) and commands (all have bounds).

### Depth Imbalance

The 5 minimal MCP docs (Sequential, Morphllm, Playwright, Magic, Context7) are ~25 lines with only 3 sections each (role, choose, examples). This is intentional for context_loader.py's hybrid injection strategy (these get INSTRUCTION_MAP compact format), but means:

- No error handling guidance for 5/8 MCPs
- No tool listing for 5/8 MCPs (even though all have multiple tools)
- No coordination/flow guidance for 5/8 MCPs (only in README matrix)

Serena (119 lines) and Tavily (78 lines) get full .md injection, so their comprehensive docs are justified. The minimal docs serve their injection context well.

### README Quality

The MCP README is excellent:
- Complete coordination matrix (13 pairings)
- Composite flags documented
- Key distinctions section clarifies overlapping MCPs
- All 8 servers listed with flags and missions

### Chrome-DevTools Naming

The file is named `MCP_Chrome-DevTools.md` but the component is `name="chrome-devtools"`. The FLAGS.md refers to this as `--perf|--devtools`. The README calls it "Chrome DevTools". The component `<role>` includes `<flags>--perf, --devtools</flags>` — this is the only MCP doc that includes a `<flags>` element, which is a positive distinction.

---

## 4. Findings

### F-1: RESEARCH_CONFIG.md Type Mismatch 🟡

`modes/RESEARCH_CONFIG.md` declares `type="core"` but resides in `modes/`. Content is research configuration — supporting the deep-research mode and /sc:research command.

**Options:**
- (a) Change `type="core"` → `type="config"` or `type="mode"` to match location
- (b) Move to `core/` directory to match type
- (c) Accept as-is — it's a config file that augments a mode

**Impact:** Confusing for contributors. Context loader loads it from `modes/` regardless of declared type.

**Recommendation:** Change to `type="config"` — it's neither a behavioral mode nor a core behavioral reference. It's configuration data.

---

### F-2: FLAGS.md `<priority_rules>` Indentation 🟡

Line 75: `<priority_rules>` breaks out of the 2-space indentation pattern used by all other sections:

```xml
  </output>           ← 2-space indent

<priority_rules>      ← 0-space indent (inconsistent)

- Safety First: ...
  </priority_rules>   ← 2-space indent on close
```

**Impact:** Minor readability issue. No functional impact since FLAGS.md is loaded as-is.

**Recommendation:** Indent `<priority_rules>` to match sibling sections.

---

### F-3: MCP Depth Imbalance 🟡

5 of 8 MCP docs (Sequential, Morphllm, Playwright, Magic, Context7) have only ~25 lines with 3 sections. While this aligns with the compact INSTRUCTION_MAP injection strategy, they lack:
- Error handling guidance (only Tavily has `<errors>`)
- Tool enumeration (only Serena and Tavily list tools)

**Impact:** When these MCPs encounter errors, there's no fallback guidance in the docs. The orchestration mode's `tool_matrix` partially compensates.

**Recommendation:** Add a brief `<errors>` section (2-3 lines) to the 5 minimal MCP docs with common failure modes and fallbacks. Low priority — the compact injection doesn't include these sections anyway.

---

### F-4: ~~Stray `</output>` Tags in Core Files~~ FALSE POSITIVE 🟢

Initial analysis flagged `</output>` tags at end of FLAGS.md and RULES.md. Hex inspection confirmed these don't exist in source files — they were Read tool display artifacts from the CLAUDE.md injection context.

**Status:** No action needed.

---

### F-5: No `<bounds>` on Core or MCP Files 🟢

Core files (4/4) and MCP files (8/8) lack `<bounds>`. All 7 modes and 30 commands have bounds. This is consistent within each directory type but creates cross-directory inconsistency.

**Impact:** Minor — core and MCP are reference docs, not executable commands. Bounds are most valuable for execution-boundary files.

**Recommendation:** Accept as intentional — core/MCP files don't execute actions. No change needed.

---

### F-6: Modes README Missing RESEARCH_CONFIG 🟢

The modes README (line 8-15) lists 7 modes but omits RESEARCH_CONFIG.md. Since RESEARCH_CONFIG supports the deep-research mode, it should be mentioned.

**Impact:** Minor — contributors may not discover RESEARCH_CONFIG.md.

**Recommendation:** Add a note to the modes README about RESEARCH_CONFIG as a supporting configuration file.

---

### F-7: README Mission Descriptions Minor Drift 🟢

Modes README missions are close but not identical to source files:

| Mode | README Says | File Says |
|------|------------|-----------|
| Token Efficiency | "Symbol-enhanced communication for compressed clarity" | "Symbol-enhanced communication mindset for compressed clarity and efficient token usage" |
| Deep Research | "Systematic investigation and evidence-based reasoning" | "Research mindset for systematic investigation and evidence-based reasoning" |
| Task Management | "Hierarchical task organization for multi-step operations" | "Hierarchical task organization with persistent memory for complex multi-step operations" |

MCP README missions are very close to source — only minor wording differences (acceptable).

**Impact:** Minor — key concepts preserved. Less severe than the commands README drift.

**Recommendation:** Sync modes README to match exact `<mission>` text. Low priority.

---

### F-8: Chrome-DevTools Unique `<flags>` Element 🟢

`MCP_Chrome-DevTools.md` is the only MCP doc that includes `<flags>--perf, --devtools</flags>` inside `<role>`. Other MCP docs rely on FLAGS.md and the README for flag documentation.

**Impact:** No functional impact. It's actually useful — but inconsistent with other MCP docs.

**Recommendation:** Accept as-is. The flags note adds value. Other MCP docs could benefit from similar additions, but that's optimization not a bug.

---

## 5. Cross-Directory Patterns

### Consistent Patterns (Good)

| Pattern | Core | Modes | MCP |
|---------|------|-------|-----|
| `<component>` wrapper | ✅ 4/4 | ✅ 8/8 | ✅ 8/8 |
| `<role>` + `<mission>` | ✅ 4/4 | ✅ 8/8 | ✅ 8/8 |
| README with table | ❌ (no README) | ✅ | ✅ |
| YAML frontmatter | ❌ | ❌ | ❌ |
| `<bounds>` | ❌ 0/4 | ✅ 7/7* | ❌ 0/8 |

*RESEARCH_CONFIG excluded from mode count (type="core").

### Token Budget

| Directory | Files | Total Lines | Est. Tokens |
|-----------|-------|-------------|-------------|
| core/ | 4 | ~269 | ~3,500 |
| modes/ | 9 (8 + README) | ~439 | ~5,500 |
| mcp/ | 9 (8 + README) | ~414 | ~5,200 |
| **Total** | **22** | **~1,122** | **~14,200** |

In practice, context_loader.py's hybrid injection means only a fraction loads per session.

---

## 6. Quality Score

### Overall: 88/100

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema consistency (within dir) | 95 | Each directory internally consistent |
| Cross-directory consistency | 80 | bounds present on modes but not core/MCP; type mismatch |
| Documentation accuracy | 85 | README descriptions close but not exact; RESEARCH_CONFIG hidden |
| Structural integrity | 82 | Stray `</output>` tags; indentation break |
| Content depth | 90 | Serena/Tavily excellent; minimal MCP docs appropriate for injection |
| Cross-reference integrity | 92 | README coordination matrix accurate; FLAGS ↔ modes ↔ MCP aligned |

---

## 7. Recommended Actions

| Priority | Action | Finding | Effort |
|----------|--------|---------|--------|
| 1 | Change RESEARCH_CONFIG type to "config" | F-1 | Trivial |
| 2 | Fix FLAGS.md `<priority_rules>` indentation | F-2 | Trivial |
| ~~3~~ | ~~Remove stray `</output>`~~ — FALSE POSITIVE | F-4 | None |
| 4 | Add RESEARCH_CONFIG note to modes README | F-6 | Trivial |
| 5 | Sync modes README mission descriptions | F-7 | Low |
| 6 | Add `<errors>` to minimal MCP docs | F-3 | Low-Medium (deferred) |
| 7 | Accept Chrome-DevTools `<flags>` as-is | F-8 | None |
| 8 | Accept no-bounds on core/MCP as intentional | F-5 | None |

---

*Analysis complete. No source files modified.*

*Handoff: `/sc:improve` for F-1 through F-5 (quick wins) | F-3 deferred (MCP depth is by-design for injection)*
