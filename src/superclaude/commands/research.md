---
description: Deep web research with adaptive planning and smart search. Use when asked for multi-source corroboration, version-specific evidence or resolving contradictions between sources. Not for one doc lookup or fetching a URL — use WebFetch or Context7 directly.
---
<component name="research" type="command">

  <role command="/sc:research">
    <mission>Deep web research with adaptive planning and smart search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <flow>
  1. Understand: Complexity + ambiguity check | Success criteria | Prior research check
  2. Plan: Strategy + depth + hop pattern + query decompose + parallel map; ask or wait as the strategy says
  3. Execute: Multi-hop search with parallel batch | Evidence collect | Adaptive replan when sources conflict, run thin, or leave the core question unanswered
  4. Validate: Cross-source verify | Credibility tier | Contradiction resolve | Gap check
  5. Synthesize: credibility-weighted merge; feature path `docs/features/<slug>/02-research.md`, standalone `docs/research/<topic>-<username>-YYYY-MM-DD.md` — slug resolution (zero-match default `[s]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`.
  </flow>

  <flags>
  - --depth quick|standard|deep|exhaustive: hops and validation per the depth section; --depth quick always runs without asking, whatever the --strategy.
  - --strategy planning|intent|unified: planning runs the plan without asking; intent asks up to 3 clarifying questions before planning; unified shows the plan and waits for the user's go-ahead. Without --strategy, pick by the query: clear and scoped → planning, ambiguous or broad → intent, complex where the user should shape the plan → unified.
  </flags>

  <depth note="Full profiles and thresholds: .claude/superclaude/modes/RESEARCH_CONFIG.md (user-scope install: ~/.claude/superclaude/modes/)">
    quick: 1 hop, runs without asking, summary | standard: 2-3 hops, full plan, report
    deep: 3-4 hops, mid-checkpoints | exhaustive: 5+ hops, subagent delegate
  </depth>

  <outputs>
| Artifact | Purpose |
|---|---|
| Feature path: `docs/features/<slug>/02-research.md` | Phase doc when slug resolves to existing/new feature folder |
| Standalone path: `docs/research/<topic>-<username>-YYYY-MM-DD.md` | One-off research, no related work expected (default) |
  </outputs>


  <tools note="Routing: tool_routing in the RESEARCH_CONFIG.md named in the depth note">
    - Tavily: tavily-search, tavily-extract, tavily-research, tavily-crawl, tavily-map (Agent Skills — auto/slash; MCP path exposes the same five as tools)
    - Native: WebSearch/WebFetch (fallback)
    - Read/Write: Report gen
    - /sc:save (suggest to the user; on request): cross-session research memory (`.claude/memories/`)
  </tools>

  <examples>
| Input | Expected behavior |
|---|---|
| `/sc:research 'quantum computing breakthroughs 2025'` | standard depth: 2-3 hops, full report |
| `/sc:research 'internal company API migration patterns'` | low-confidence sources → adaptive replan |
  </examples>

  <gotchas>
  - single-source: each load-bearing claim needs ≥2 independent sources; label a claim with only one as single-source.
  - source-quality: never use Wikipedia or Reddit as a primary source; cross-check them against primary sources.
  </gotchas>

  <bounds>
    <does>finds current information, searches across sources, grounds claims in evidence, replans adaptively.</does>
    <never>makes claims without sources, skips validation, accesses restricted content, or carries raw payloads between hops.</never>
  </bounds>

  <handoff next="/sc:design /sc:implement /sc:brainstorm"/>
</component>