# Context Engineering Improvements for superclaude

**Date:** 2026-03-22
**Author:** chosh1179
**Source:** Cross-reference analysis of `opus-practical-guide.md` (Anthropic context engineering principles) against superclaude framework v4.3.0+ajitta
**Status:** Delivered — all 4 sprints complete

---

## Executive Summary

Systematic cross-reference of 9 Opus practical guide principles against 74 superclaude content items reveals **5 high-impact** and **3 medium-impact** improvement opportunities. The framework already excels at structured prompts (XML components), strong-language avoidance (0 violations), hybrid delivery (context_loader.py), and model tiering (agent frontmatter). The primary gaps are in **token efficiency of injected content**, **examples-over-rules balance**, and **progressive disclosure**.

**Estimated total token savings:** 5,600-8,000 tokens per multi-flag session (30-50% of context budget).

### Delivery Results (measured 2026-03-22)

| Scenario | Before | After | Reduction |
|----------|--------|-------|-----------|
| brainstorm+serena+tavily | ~2,998 tokens | ~926 tokens | **-69%** |
| --all-mcp (8 MCPs) | ~7,365 tokens | ~513 tokens | **-93%** |
| research+seq | ~1,455 tokens | ~612 tokens | **-58%** |
| Test suite | 1,687 passed | 1,694 passed | +7 new, 0 regressions |

---

## Methodology

### 3-Iteration Brainstorm Process

| Iteration | Focus | Output |
|-----------|-------|--------|
| 1 | Guide principle → implementation gap mapping | 8 gaps with severity ratings |
| 2 | Top gaps → concrete improvement proposals with implementation sketches | 8 proposals with token savings estimates |
| 3 | Prioritization, trade-off resolution, design specification | This document |

### Data Sources
- `opus-practical-guide.md` — 9-part Anthropic context engineering guide
- Architecture exploration — 74 content items, 6 content types
- **Token efficiency audit** — quantified always-loaded baseline at 4,002 tokens (50% of 8K budget)
- **Example coverage audit** — 106 rule lines with 0 examples in RULES.md; overall 6:1 ratio framework-wide
- **Context engineering research** — industry trends (Google ADK, Letta, Stanford ACE, LangChain) confirm progressive disclosure as consensus best practice
- Strong-language audit — 0 violations across agents/commands/modes
- Rules-to-examples ratio — RULES.md 106:8 (13:1), PRINCIPLES.md 26:0
- INSTRUCTION_MAP audit — only 1 of 9 entries populated (BUSINESS_SYMBOLS.md)
- Command scope analysis — 6 overlap clusters across 33 commands

---

## Token Budget Quantification (from audit)

### Always-Loaded Baseline (via CLAUDE_SC.md @import)

| File | Characters | Tokens | % of 8K Budget |
|------|-----------|--------|----------------|
| FLAGS.md | 5,733 | 1,433 | 18% |
| RULES.md | 8,023 | 2,005 | 25% |
| PRINCIPLES.md | 2,259 | 564 | 7% |
| **Total Baseline** | **16,015** | **4,002** | **50%** |

**Remaining budget for on-demand context: ~4,000 tokens.**

### Context Pressure Scenarios

| Scenario | Baseline | Additional | Total | Budget % |
|----------|----------|-----------|-------|----------|
| Plain prompt | 4,002 | — | 4,002 | 50% |
| +1 mode (--brainstorm) | 4,002 | ~500 | 4,502 | 56% |
| +research mode + agent | 4,002 | ~2,000 | 6,002 | 75% |
| +--frontend-verify (3 MCPs) | 4,002 | ~2,500 | 6,502 | 81% |
| +--all-mcp (8 MCPs) | 4,002 | ~4,500 | 8,502 | **>100% overflow** |

### Example Coverage Audit

| Content Type | Rule Lines | Example Lines | Ratio | Example Quality |
|-------------|-----------|---------------|-------|-----------------|
| RULES.md (core) | 106 | 8 | **13:1** | Minimal (path patterns only) |
| PRINCIPLES.md | 26 | 0 | **∞** | Zero examples |
| FLAGS.md | 84 | 0 | **∞** | Zero examples |
| Agents (avg of 5) | 19 | 6 | 3:1 | Template-level (artifact names, not demonstrations) |
| Commands (avg of 5) | 23 | 9 | 3:1 | Better (error-paths exist) but abstract outputs |
| Modes (avg of 3) | 24 | 4 | 6:1 | Weakest despite needing most |

### Industry Validation (from research)

| Pattern | Adopted By | Relevance to superclaude |
|---------|-----------|-------------------------|
| 3-tier progressive disclosure | Google ADK, Letta, agentskills.io, Anthropic | Validates Improvement #1 (tiered system) |
| Handle Pattern (lightweight refs) | Google ADK | Validates Improvement #3 (INSTRUCTION_MAP) |
| Self-improving context (ACE) | Stanford/SambaNova | Informs Improvement #7 (rule effectiveness) |
| Write/Select/Compress/Isolate | LangChain | Framework for evaluating context operations |
| Context rot in 1M+ windows | Anthropic, Google | Confirms need for curation even with large context |

**Key industry quote (Anthropic, Sep 2025):** "Context rot is real even with 1M tokens. For the foreseeable future, context windows of all sizes will be subject to context pollution."

---

## Gap Analysis Summary

| # | Gap | Guide § | Severity | Current State |
|---|-----|---------|----------|---------------|
| G1 | No progressive context disclosure | §4.3 | **High** | Modes inject full .md or nothing |
| G2 | INSTRUCTION_MAP underutilized | §4.2 | **High** | 1 of 9 entries populated; MCP docs inject full markdown |
| G3 | Low examples-to-rules ratio | §6.1-6.2 | **High** | PRINCIPLES.md: 0 examples; RULES.md: 6:1 ratio |
| G4 | No prompt effectiveness feedback loop | §2.3 | **High** | No way to measure if rules improve behavior |
| G5 | Command scope overlap | §3.2 | **Medium** | 6 potential overlap clusters in 33 commands |
| G6 | Sub-agent criteria scattered | §1.3, §5.3 | **Medium** | Criteria in FLAGS.md, RULES.md, and implicit in agents |
| G7 | No session goal framing | §7.1, §7.3 | **Medium** | /sc:load doesn't set session-level objectives |
| G8 | No explicit compaction strategy | §5.1 | **Medium** | /sc:save captures state but doesn't optimize preservation |

### What's Already Strong (No Action Needed)

| Principle | Guide § | superclaude Status |
|-----------|---------|-------------------|
| Strong language avoidance | §1.4 | 0 violations across 74 files |
| Over-engineering guardrails | §1.2 | 9 rules in `anti_over_engineering` section |
| Structured XML prompts | §2.2 | Consistent `<component>` pattern everywhere |
| Hybrid context retrieval | §4.1-4.2 | context_loader.py: pre-load + JIT |
| Agentic note-taking | §5.2 | claude-mem + MEMORY.md + /sc:save |
| Model tiering | §8.1 | Agent frontmatter: opus/sonnet/haiku |
| Extended thinking control | §7.4 | --seq flag → Sequential MCP |

---

## Improvement Proposals

### Improvement 1: Tiered Context Disclosure System

**Priority:** P0 (highest impact, addresses G1 + G2)
**Effort:** Medium (context_loader.py changes)
**Token savings:** 75% per injection; ~5,600 tokens total for multi-MCP sessions

#### Problem

When 3+ flags activate, 2-4K tokens are consumed by injecting full .md files for modes/MCPs. The token audit confirms: always-loaded baseline is already 4,002 tokens (50% of budget), leaving only ~4K for on-demand context. `--all-mcp` overflows at 8,500+ tokens.

The Opus guide's core principle: "원하는 결과의 가능성을 최대화하는 가장 작은 고신호 토큰 세트를 찾아라."

INSTRUCTION_MAP currently has only 1 entry (BUSINESS_SYMBOLS.md). All 8 MCP docs inject full markdown (~750 tokens each).

**Industry validation:** Google ADK (Feb 2026) formalized the same 3-tier architecture: Storage → Processor Pipeline → Compiled Working Context. Letta implements self-managed progressive disclosure via git-based memory with frontmatter metadata. The agentskills.io standard (arXiv, Zhang et al., Feb 2026) measures 70-90% token reduction with this pattern.

#### Design

**3-tier injection model:**

| Tier | Content Level | When Used | Token Cost |
|------|---------------|-----------|------------|
| **Tier 0** | 1-line summary | Default for MCPs (Claude already has tool descriptions) | ~15 tokens |
| **Tier 1** | Compact reference (operational essentials) | Default for modes; on-demand for MCPs | ~100 tokens |
| **Tier 2** | Full .md file | Explicit `--verbose-context` flag or auto-escalation | ~400-800 tokens |

**Auto-escalation rule:** If the same mode/MCP triggers in 2+ consecutive prompts within a session, escalate from Tier 0/1 → Tier 2.

#### Implementation

```python
# context_loader.py additions

TIER_0_MAP = {
    # MCP — 1-line summaries (Claude has tool descriptions already)
    "mcp/MCP_Serena.md": "Serena: symbol-level code ops. Use get_symbols_overview before reading files.",
    "mcp/MCP_Tavily.md": "Tavily: web search (tavily_search), extraction (tavily_extract), research (tavily_research).",
    "mcp/MCP_Context7.md": "Context7: resolve-library-id first, then query-docs. Never skip step 1.",
    "mcp/MCP_Sequential.md": "Sequential: multi-step reasoning chain. Use for 3+ component problems.",
    "mcp/MCP_Playwright.md": "Playwright: browser E2E automation. navigate→interact→assert.",
    "mcp/MCP_Chrome-DevTools.md": "DevTools: performance profiling. trace→reproduce→analyze Core Web Vitals.",
    "mcp/MCP_Magic.md": "Magic 21st.dev: UI component search→customize→integrate.",
    "mcp/MCP_Morphllm.md": "Morphllm: bulk pattern-based multi-file transforms.",
    # Core
    "core/BUSINESS_SYMBOLS.md": "Business symbols + expert selection. 🎯📈💰⚖️🏆🌊 domain mapping.",
}

TIER_1_MAP = {
    # Modes — compact 4-axis reference
    "modes/MODE_Brainstorming.md": (
        "<sc-mode name='brainstorm'>"
        "Think: diverge→converge, quantity→quality | "
        "Communicate: questions over answers, 'what if' framing | "
        "Prioritize: exploration>efficiency, understanding>solution | "
        "Behave: Socratic probing, non-presumptive, brief-generation"
        "</sc-mode>"
    ),
    # ... (one per mode, ~100 tokens each)

    # MCP — operational essentials
    "mcp/MCP_Serena.md": (
        "<sc-mcp name='serena'>"
        "Symbol ops: find_symbol(name_path, include_body), get_symbols_overview, replace_symbol_body. "
        "Workflow: overview→find→read body→edit. Use search_for_pattern for unknown locations. "
        "Priority: symbolic tools > file reads. Memory: list_memories for cross-session context."
        "</sc-mcp>"
    ),
    # ... (one per MCP, ~80 tokens each)
}

# Injection logic update
def get_injection_tier(context_file: str, session_count: int) -> int:
    """Determine injection tier based on file type and session usage count."""
    if session_count >= 2:
        return 2  # Auto-escalate after repeated use
    if context_file.startswith("mcp/"):
        return 0  # MCPs default to minimal
    if context_file.startswith("modes/"):
        return 1  # Modes need behavioral context
    return 1  # Core files default to compact
```

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/scripts/context_loader.py` | Add TIER_0_MAP, TIER_1_MAP, tier selection logic |
| `src/superclaude/core/FLAGS.md` | Add `--verbose-context` flag documentation |

---

### Improvement 2: Examples-First Core Content

**Priority:** P0 (addresses G3 — guide §6.1-6.2)
**Effort:** Medium (content authoring)
**Impact:** Better rule compliance with fewer repeated violations

#### Problem

Detailed audit reveals the imbalance is worse than initially estimated:
- **RULES.md**: 106 rule lines with only 8 examples (13:1 ratio). Zero examples for Status Check, Diagnosis, Intent Verification, Correction Capture — the most violated rules.
- **PRINCIPLES.md**: 26 principles with 0 examples (∞ ratio).
- **FLAGS.md**: 84 flag definitions with 0 usage examples.
- **Agents**: All 22 use identical 6-line example blocks (3 rows) with template-level quality ("Component diagram + API contracts" — tells what exists, not how).
- **Modes**: Weakest examples (4 lines avg) despite being cognitive overlays where example IS the teaching.

The guide emphasizes: "다양하고 대표적인 소수의 예시가 장황한 규칙 목록보다 효과적이다."
Anthropic (Sep 2025): "Curate a set of diverse, canonical examples. For an LLM, examples are the 'pictures' worth a thousand words."

#### Design

Add `<examples>` sections to both core files with curated before/after demonstrations.

**RULES.md — Add after `<core_rules>`:**

```xml
<core_rules>
  ...existing rules unchanged...
  <examples note="Representative scenarios — examples teach better than rules">
  | Scenario | Wrong (❌) | Right (✅) | Rule |
  |----------|-----------|-----------|------|
  | User: "fix login bug" | Refactors auth + adds tests + updates docs | Fixes the specific bug, nothing else | Scope 🟡 |
  | Before implementing feature | Starts coding immediately | `git log --oneline -5` + `grep -r "feature_name"` first | Status Check 🔴 |
  | API endpoint returning 500 | Assumes code bug, reads source | Checks: port in use? DB running? env vars set? | Diagnosis 🔴 |
  | User: "improve the dashboard" | Picks "add charts" as most likely | Asks: "Performance, UX, or data accuracy?" | Clarification 🟡 |
  | 42/42 tests pass | "All tests pass" | "42/42 pass (baseline: 40, +2 new)" | Verification 🔴 |
  </examples>
</core_rules>
```

**RULES.md — Add after `<anti_over_engineering>`:**

```xml
<anti_over_engineering>
  ...existing rules unchanged...
  <examples note="Over-engineering vs right-sizing">
  | Request | Over-engineered (❌) | Right-sized (✅) |
  |---------|---------------------|-----------------|
  | "Add a retry to this API call" | Creates RetryStrategy class with backoff, jitter, circuit breaker | Adds 3-line retry loop with exponential backoff |
  | "Fix the typo in error message" | Refactors entire error handling module | Changes the one string |
  | "Log the user ID on login" | Creates structured logging framework with rotation | Adds `logger.info(f"Login: {user_id}")` |
  </examples>
</anti_over_engineering>
```

**PRINCIPLES.md — Add after `<philosophy>`:**

```xml
<philosophy>
  ...existing principles unchanged...
  <examples note="Principles in action">
  | Principle | Before | After |
  |-----------|--------|-------|
  | Restraint-First | "I also cleaned up the utils while I was in there" | "Fixed the bug. Utils cleanup is separate scope." |
  | Right-Altitude | "ALWAYS use Serena for ALL symbol operations" | "Use Serena for symbol operations when exploring unfamiliar code" |
  | Evidence-Based | "This should work now" | "Tests pass: 42/42 (baseline 40). Deploy verified locally." |
  | Parallel-Thinking | Runs 5 sequential grep calls | Runs 5 grep calls in single parallel message |
  </examples>
</philosophy>
```

#### Token Cost

~200 additional tokens per file. Net positive: LLMs learn more from 3 examples than 10 rules.

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/core/RULES.md` | Add 2 `<examples>` blocks (~10 rows total) |
| `src/superclaude/core/PRINCIPLES.md` | Add 1 `<examples>` block (~4 rows) |

---

### Improvement 3: INSTRUCTION_MAP Expansion

**Priority:** P1 (quick win, addresses G2)
**Effort:** Low (data entry only)
**Token savings:** ~5,600 tokens when multiple MCPs active

#### Problem

Only `core/BUSINESS_SYMBOLS.md` has an instruction. All 8 MCP docs inject full .md.

#### Design

Populate INSTRUCTION_MAP for all 8 MCPs. These instructions serve as Tier 1 content for the tiered system (Improvement 1), but can be implemented independently.

```python
INSTRUCTION_MAP = {
    # Core
    "core/BUSINESS_SYMBOLS.md": (
        "Business symbols + expert selection: 🎯target 📈growth 💰financial ⚖️tradeoffs 🏆competitive 🌊blue-ocean. "
        "Includes expert domain mapping, discussion templates, and abbreviations."
    ),
    # MCP operational instructions
    "mcp/MCP_Serena.md": (
        "Serena: symbol-level code operations (find_symbol, replace_symbol_body, get_symbols_overview, "
        "insert_before/after_symbol, find_referencing_symbols, rename_symbol). "
        "Workflow: overview → find symbol → read body → edit. Use search_for_pattern for unknown locations. "
        "Prioritize symbolic tools over full file reads. Use list_memories/read_memory for cross-session context."
    ),
    "mcp/MCP_Tavily.md": (
        "Tavily MCP: tavily_search (web search with domain/time filtering), tavily_extract (full-text from URLs), "
        "tavily_research (multi-source synthesis), tavily_crawl (site-wide extraction), tavily_map (URL discovery). "
        "Use for current info, multi-source research. Fallback: native WebSearch for simple queries."
    ),
    "mcp/MCP_Context7.md": (
        "Context7: 2-step library documentation lookup. "
        "Step 1: resolve-library-id (name → Context7 ID). Step 2: query-docs (ID + query → docs). "
        "Never skip step 1. Default 10K tokens per query. Pin version with /org/project/version format."
    ),
    "mcp/MCP_Sequential.md": (
        "Sequential: multi-step reasoning chain. Parameters: thought, thoughtNumber, totalThoughts, "
        "nextThoughtNeeded, isRevision+revisesThought, branchFromThought+branchId. "
        "Use for: 3+ component problems, root cause analysis, trade-off evaluation, hypothesis testing."
    ),
    "mcp/MCP_Playwright.md": (
        "Playwright: browser automation for E2E testing. Pattern: navigate → interact → assert. "
        "Prefer CSS selectors. Handle async with waitForSelector. Screenshot on failure. "
        "Integration: combine with DevTools for performance + visual testing."
    ),
    "mcp/MCP_Chrome-DevTools.md": (
        "Chrome DevTools: performance profiling and Core Web Vitals. "
        "Workflow: start trace → reproduce issue → stop trace → analyze insights. "
        "Key metrics: CLS, LCP, FID/INP. Use lighthouse_audit for overall scores. "
        "take_screenshot for visual validation."
    ),
    "mcp/MCP_Magic.md": (
        "Magic 21st.dev: UI component library. Search components → preview → customize → integrate. "
        "Focus on React components, design system tokens, responsive patterns."
    ),
    "mcp/MCP_Morphllm.md": (
        "Morphllm: bulk code transforms via pattern matching. Multi-file edits for: "
        "rename across codebase, pattern migration, API signature updates, bulk formatting changes."
    ),
}
```

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/scripts/context_loader.py` | Expand INSTRUCTION_MAP from 1 to 9 entries |

---

### Improvement 4: Unified Sub-Agent Decision Framework

**Priority:** P1 (addresses G6)
**Effort:** Low (content consolidation)

#### Problem

Sub-agent criteria are scattered across:
- FLAGS.md `--delegate` section (heuristics)
- RULES.md `agent_orchestration` (flow)
- Agent frontmatter `permissionMode` (implicit)

The guide (§1.3): "서브에이전트 사용 기준을 명시"

#### Design

Add a consolidated `<sub_agent_decision>` section to RULES.md with clear criteria and examples.

```xml
<sub_agent_decision note="Unified sub-agent vs direct work criteria (Guide §1.3, §5.3)">
  Direct work:
  - Single file edit, <3 steps, sequential dependency
  - Simple search (grep/glob for known pattern)
  - Context already loaded in conversation

  Sub-agent:
  - 3+ independent work streams (parallelizable)
  - Different expertise domains needed simultaneously
  - Exploration would consume >20K tokens of main context
  - Isolated failure acceptable (exploratory research)

  Never sub-agent:
  - Tasks needing main conversation's recent context
  - Sequential A→B dependencies
  - Tasks completable in <30 seconds directly

  <examples>
  | Task | Decision | Why |
  |------|----------|-----|
  | "Find where UserAuth is defined" | Direct grep | Single search, instant |
  | "Audit security + performance + a11y" | 3 sub-agents | Independent domains, parallel |
  | "Read this file then edit line 42" | Direct | Sequential dependency |
  | "Research React 19 + Vue 4 + Svelte 5 features" | 3 sub-agents | Independent, context-isolating |
  | "Run tests and check results" | Direct | Fast, needs main context |
  </examples>
</sub_agent_decision>
```

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/core/RULES.md` | Add `<sub_agent_decision>` section |

---

### Improvement 5: Command Scope Map

**Priority:** P2 (addresses G5)
**Effort:** Low (documentation only)

#### Problem

33 commands with 6 overlap clusters may confuse Claude's auto-delegation. The guide (§3.1): "인간이 '어떤 도구를 쓸지' 즉시 판단할 수 없으면 모델도 못한다"

#### Design

Add a `<scope_map>` to help.md that explicitly differentiates overlapping commands.

```xml
<scope_map note="Disambiguation for overlapping commands">
  Analysis cluster:
  - analyze: Static code quality assessment (metrics, patterns, smells)
  - review:  Change-level review (PRs, diffs, specific commits)
  - reflect: Post-implementation self-validation ("did I do this correctly?")

  Project management cluster:
  - task:  Single-session work breakdown and progress tracking
  - pm:    Multi-session orchestration, delegation, learning capture
  - spawn: One-shot parallel sub-agent launch for independent tasks

  Implementation cluster:
  - implement: Write/modify code for features and fixes
  - build:     Compile, package, deploy artifacts (post-implementation)

  Documentation cluster:
  - document:   Prose documentation for human readers
  - index:      Structured knowledge base generation
  - index-repo: Repository structure catalog (token-efficient)

  Discovery cluster:
  - brainstorm: Interactive requirements discovery (Socratic, exploratory)
  - research:   Systematic evidence-based investigation (web search, citations)

  Advisory cluster:
  - business-panel: Business strategy analysis (market, competitive, financial)
  - spec-panel:     Technical specification review (architecture, API, correctness)
</scope_map>
```

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/commands/help.md` | Add `<scope_map>` section |

---

### Improvement 6: Session Goal Framing

**Priority:** P2 (addresses G7)
**Effort:** Low

#### Problem

No session-level goal tracking. Guide (§7.1): "한 세션에 하나의 명확한 목표."

#### Design

Extend /sc:load to include optional session goal capture.

```xml
<!-- Addition to load.md flow -->
<flow>
  ...existing steps...
  N. Session Goal (optional): If user provides a goal, record it.
     Display as reminder when context exceeds 60%.
     At /sc:save, evaluate goal completion status.
</flow>
```

Implementation: Store goal in session cache file (already exists at `~/.claude/.superclaude_hooks/claude_context_{SESSION_ID}.txt`). Emit as `<sc-directive>` when context pressure rises.

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/commands/load.md` | Add session goal step to flow |
| `src/superclaude/commands/save.md` | Add goal completion evaluation |
| `src/superclaude/scripts/context_loader.py` | Read/emit goal from session cache |

---

### Improvement 7: Rule Effectiveness Tracking

**Priority:** P2 (addresses G4 — lightweight version)
**Effort:** Medium

#### Problem

No way to know if rules improve behavior. Guide (§2.3): "최소 프롬프트로 시작 → 실패 모드 관찰 → 실패 모드별 지시 추가 → 반복"

#### Design

**Lightweight approach using existing correction capture:**

1. Add `rule_id` tags to each rule in RULES.md (e.g., `[R01]`, `[R02]`)
2. Extend correction capture format to include violated rule_id
3. Add `/sc:analyze --focus rules` mode that scans feedback memories for patterns
4. Quarterly audit: which rules get violated most? Which are never triggered?

**Industry reference:** Stanford ACE Framework (Oct 2025) uses `helpful_count`/`harmful_count` per context rule — the most advanced implementation of context signal quality measurement. Our lightweight version (rule_id + correction capture) is a pragmatic step toward this pattern without automated scoring.

```xml
<core_rules>
  [R01] Workflow 🟡: Status Check → Understand → Plan → Execute → Validate
  [R02] Status Check 🔴: before implementation, run 2-3 targeted searches
  [R03] Diagnosis 🔴: generate 3+ hypotheses ranked by simplicity
  ...
</core_rules>

<!-- Correction capture format update -->
<correction_capture>
  Format: {trigger, misread, actual_intent, violated_rule: "[R01]", prevention}
</correction_capture>
```

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/core/RULES.md` | Add rule_id prefixes, update correction format |
| `src/superclaude/commands/analyze.md` | Add `--focus rules` option |

---

### Improvement 8: Compaction Strategy for /sc:save

**Priority:** P3 (addresses G8)
**Effort:** Low

#### Problem

/sc:save captures session state but lacks explicit guidance on what to preserve vs discard for optimal future session loading.

#### Design

Add `<compaction_strategy>` to save.md:

```xml
<compaction_strategy note="Guide §5.1 — what to preserve across sessions">
  Preserve (high signal):
  - Architecture decisions and their rationale
  - Unresolved issues and blockers
  - Key implementation patterns discovered
  - Session goal and completion status

  Discard (low signal):
  - Verbatim tool output (file contents, grep results)
  - Intermediate search results that led nowhere
  - Already-committed code diffs (git has these)
  - Duplicate context from previous sessions

  Format:
  - Structured summary (decisions, todo, context pointers)
  - Not narrative prose
  - Reference file paths and line numbers, not full content
</compaction_strategy>
```

#### Files Changed

| File | Change |
|------|--------|
| `src/superclaude/commands/save.md` | Add `<compaction_strategy>` section |

---

## Implementation Priority Matrix

| Priority | Improvement | Effort | Token Impact | Files |
|----------|------------|--------|--------------|-------|
| **P0** | #1 Tiered Context Disclosure | Medium | -5,600 tokens/session | context_loader.py, FLAGS.md |
| **P0** | #2 Examples-First Core Content | Medium | +400 tokens (net positive) | RULES.md, PRINCIPLES.md |
| **P1** | #3 INSTRUCTION_MAP Expansion | **Low** | -5,600 tokens (can deploy alone) | context_loader.py |
| **P1** | #4 Sub-Agent Decision Framework | **Low** | Clarity, no token change | RULES.md |
| **P2** | #5 Command Scope Map | **Low** | Clarity, ~200 tokens | help.md |
| **P2** | #6 Session Goal Framing | Low | ~50 tokens | load.md, save.md, context_loader.py |
| **P2** | #7 Rule Effectiveness Tracking | Medium | ~100 tokens | RULES.md, analyze.md |
| **P3** | #8 Compaction Strategy | **Low** | Clarity, ~100 tokens | save.md |

### Recommended Sprint Plan

**Sprint 1 (Quick wins — P1 low-effort):**
- [ ] #3 Expand INSTRUCTION_MAP (9 entries)
- [ ] #4 Add sub-agent decision section to RULES.md

**Sprint 2 (High-impact — P0):**
- [ ] #2 Add examples to RULES.md and PRINCIPLES.md
- [ ] #1 Implement tiered context disclosure in context_loader.py

**Sprint 3 (Documentation — P2):**
- [ ] #5 Command scope map in help.md
- [ ] #6 Session goal framing in load/save
- [ ] #8 Compaction strategy in save.md

**Sprint 4 (Feedback loop — P2 medium-effort):**
- [ ] #7 Rule effectiveness tracking (IDs + analyze mode)

---

## Trade-Off Analysis

| Decision | Option A | Option B | Chosen | Why |
|----------|----------|----------|--------|-----|
| Tier default for MCPs | Tier 0 (1-line) | Tier 1 (compact) | **Tier 0** | Claude already has MCP tool descriptions in system prompt |
| Tier default for modes | Tier 0 (1-line) | Tier 1 (compact) | **Tier 1** | Modes define behavioral shifts that need more context |
| Examples format | Narrative paragraphs | Table format | **Table** | Scannable, token-efficient, pattern-matching friendly |
| Rule IDs | Auto-generated | Manual `[R01]` tags | **Manual** | More memorable, allows semantic grouping |
| Scope map location | Separate file | Inside help.md | **help.md** | Single source, always accessible via /sc:help |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tier 0/1 too terse → Claude misuses MCP | Medium | Auto-escalation to Tier 2 on repeated use; --verbose-context escape hatch |
| Examples become stale | Low | Examples reference behavioral patterns, not specific code |
| INSTRUCTION_MAP instructions diverge from full .md | Medium | Generate from .md programmatically (future enhancement) |
| Rule IDs create maintenance burden | Low | Only 17 core_rules + 9 anti_over_engineering = 26 IDs |
| Session goal feels intrusive | Low | Made optional in /sc:load; never auto-prompted |

---

## Verification Plan

| Improvement | Verification Method |
|-------------|-------------------|
| #1 Tiered disclosure | `python context_loader.py` with 3+ flags → measure output token count before/after |
| #2 Examples | `uv run pytest tests/unit/test_content_structure.py` — verify XML valid |
| #3 INSTRUCTION_MAP | `python context_loader.py` with each MCP flag → verify short instruction emitted |
| #4 Sub-agent decision | Qualitative: test in 3 sessions, verify sub-agent usage matches criteria |
| #5 Scope map | `uv run pytest tests/unit/test_command_structure.py` |
| #6 Session goal | Manual test: `/sc:load` → set goal → work → `/sc:save` → check goal captured |
| #7 Rule tracking | Qualitative: after 10 sessions, check feedback memories for rule_id patterns |
| #8 Compaction | Qualitative: compare /sc:save output before/after |

---

## Out of Scope

- Automated telemetry / metrics dashboard for rule compliance
- Command merging or deletion (all 33 commands have distinct roles)
- Agent restructuring (22 agents are well-differentiated)
- Changes to the @import chain (CLAUDE_SC.md structure is stable)
- Token counting with actual tokenizer (char/4 estimate is sufficient for budgeting)

---

## Appendix: Guide Principle Coverage

| Guide Part | Title | superclaude Coverage | Gap? |
|------------|-------|---------------------|------|
| 1.1 | Literal instruction following | anti_over_engineering | No |
| 1.2 | Over-engineering tendency | 9 guardrail rules | No |
| 1.3 | Sub-agent abuse | FLAGS --delegate + this spec #4 | **Improved** |
| 1.4 | Prompt sensitivity | 0 strong-language violations | No |
| 2.1 | Right-altitude design | PRINCIPLES.md states principle | No |
| 2.2 | Structured prompts | XML components everywhere | No |
| 2.3 | Prompt iteration process | This spec #7 | **Improved** |
| 3.1 | Self-contained tools | This spec #5 scope map | **Improved** |
| 3.2 | Minimum viable tool set | 33 commands, all differentiated | No |
| 4.1 | Hybrid retrieval | context_loader.py | No |
| 4.2 | Lightweight identifiers | This spec #1 + #3 | **Improved** |
| 4.3 | Progressive disclosure | This spec #1 tiered system | **Improved** |
| 5.1 | Compaction strategy | This spec #8 | **Improved** |
| 5.2 | Structured note-taking | claude-mem + MEMORY.md | No |
| 5.3 | Sub-agent architecture | --delegate + this spec #4 | **Improved** |
| 6.1 | Anti-pattern: edge-case listing | This spec #2 examples | **Improved** |
| 6.2 | Few-shot examples | This spec #2 examples | **Improved** |
| 7.1 | Session start structure | This spec #6 goal framing | **Improved** |
| 7.3 | Long session management | This spec #6 + #8 | **Improved** |
| 7.4 | Extended thinking | --seq flag | No |
| 8.1 | Model tiering | Agent frontmatter | No |
| 8.2 | Token cost consciousness | --uc flag + this spec #1 | **Improved** |

**Coverage: 22/22 principles addressed (12 already covered + 10 improved by this spec)**
