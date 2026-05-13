---
description: Deep web research with adaptive planning + smart search. Use when user type `/sc:research` or ask multi-source corroboration, version-specific evidence, or contradiction resolve across sources. Do NOT auto-trigger on single doc lookup, library API question, or "fetch this URL" — use Tavily/WebFetch/Context7 direct.
---
<component name="research" type="command">

  <role command="/sc:research">
    <mission>Deep web research w/ adaptive plan + smart search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <flow>
  1. Understand: Complexity + ambiguity check | Success criteria | Prior research check
  2. Plan: Strategy + depth + hop pattern + query decompose + parallel map
  3. Execute: Multi-hop search w/ parallel batch | Evidence collect | Adaptive replan on confidence&lt;0.6 or contradictions&gt;30%
  4. Validate: Cross-source verify | Credibility score | Contradiction resolve | Gap check
  5. Synthesize: Credibility-weighted merge | Structured report → docs/research/[topic]-[username]-YYYY-MM-DD.md
  </flow>

  <depth note="See modes/RESEARCH_CONFIG.md for full profiles, hop config, thresholds">
    quick: 1 hop, auto plan, summary | standard: 2-3 hops, full plan, report
    deep: 3-4 hops, mid-checkpoints | exhaustive: 5+ hops, subagent delegate
  </depth>


  <tools note="Routing in modes/RESEARCH_CONFIG.md tool_routing">
    - Tavily: tavily_search, tavily_extract, tavily_research, tavily_crawl, tavily_map
    - Native: WebSearch/WebFetch (fallback)
    - Sequential: Multi-step reason + replan decide
    - Read/Write: Report gen
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
  - single-source: No conclude from 1 source. Cross-verify ≥2 sources
  - source-quality: No Wikipedia/Reddit as primary. Cross-check w/ primary sources
  </gotchas>

  <bounds>
    <does>current info, smart search, evidence-based, adaptive replan.</does>
    <never>claims w/o sources, skip validate, restricted content, carry raw payloads between hops.</never>
    <fallback>Ask user guide when unsure.</fallback>
  </bounds>

  <handoff next="/sc:design /sc:implement /sc:brainstorm"/>
</component>