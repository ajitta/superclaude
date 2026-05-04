---
description: Deep web research with adaptive planning and intelligent search
---
<component name="research" type="command">

  <role command="/sc:research">
    <mission>Deep web research with adaptive planning and intelligent search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <flow>
  1. Understand: Complexity + ambiguity assessment | Success criteria | Prior research check
  2. Plan: Strategy + depth + hop pattern + query decomposition + parallelization map
  3. Execute: Multi-hop search with parallel batching | Evidence collection | Adaptive replan on confidence&lt;0.6 or contradictions&gt;30%
  4. Validate: Cross-source verification | Credibility scoring | Contradiction resolution | Gap check
  5. Synthesize: Credibility-weighted integration | Structured report → docs/research/[topic]-[username]-YYYY-MM-DD.md
  </flow>

  <depth note="See modes/RESEARCH_CONFIG.md for full profiles, hop config, and thresholds">
    quick: 1 hop, auto plan, summary | standard: 2-3 hops, full plan, report
    deep: 3-4 hops, mid-checkpoints | exhaustive: 5+ hops, subagent delegation
  </depth>


  <tools note="Routing details in modes/RESEARCH_CONFIG.md tool_routing">
    - Tavily: tavily_search, tavily_extract, tavily_research, tavily_crawl, tavily_map
    - Native: WebSearch/WebFetch (fallback)
    - Sequential: Multi-step reasoning + replan decisions
    - Read/Write: Report generation
    - Serena: Cross-session research memory
  </tools>

  <examples>

  <example name="standard-depth" type="happy-path">
    - Input: /sc:research 'quantum computing breakthroughs 2025'
  </example>

  <example name="adaptive-replan" type="happy-path">
    - Input: /sc:research 'internal company API migration patterns'
  </example>

  </examples>

  <gotchas>
  - single-source: Do not conclude from a single source. Cross-verify with at least 2 sources
  - source-quality: Do not use Wikipedia/Reddit as primary source. Cross-check with primary sources
  </gotchas>

  <bounds>
    <does>current info, intelligent search, evidence-based, and adaptive replan.</does>
    <never>claims without sources, skip validation, restricted content, and carry raw payloads between hops.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:design /sc:implement /sc:brainstorm"/>
</component>
