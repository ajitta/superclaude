---
description: Deep web research with adaptive planning and intelligent search
---
<component name="research" type="command">

  <role>
    /sc:research
    <mission>Deep web research with adaptive planning and intelligent search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <flow effort="5|10|55|15|15">
    1. Understand: Complexity + ambiguity assessment | Success criteria | Prior research check
    2. Plan: Strategy + depth + hop pattern + query decomposition + parallelization map
    3. Execute: Multi-hop search with parallel batching | Evidence collection | Adaptive replan on confidence&lt;0.6 or contradictions&gt;30%
    4. Validate: Cross-source verification | Credibility scoring | Contradiction resolution | Gap check
    5. Synthesize: Credibility-weighted integration | Structured report → docs/research/YYYY-MM-DD-&lt;topic&gt;-research-&lt;username&gt;.md
  </flow>

  <depth note="See modes/RESEARCH_CONFIG.md for full profiles, hop config, and thresholds">
    quick: 1 hop, auto plan, summary | standard: 2-3 hops, full plan, report
    deep: 3-4 hops, mid-checkpoints | exhaustive: 5+ hops, subagent delegation
  </depth>

  <mcp servers="tavily|seq|c7|serena"/>
  <personas p="research"/>

  <tools note="Routing details in modes/RESEARCH_CONFIG.md tool_routing">
    - Tavily: tavily_search, tavily_extract, tavily_research, tavily_crawl, tavily_map
    - Native: WebSearch/WebFetch (fallback)
    - Sequential: Multi-step reasoning + replan decisions
    - Read/Write: Report generation
    - Serena: Cross-session research memory
  </tools>

  <examples>

  <example name="standard-depth" type="happy-path">
    <input>/sc:research 'quantum computing breakthroughs 2025'</input>
    <output>
      Depth: standard (auto) | Hop 1: tavily_search → 5 sources | Hop 2: tavily_extract top 3 | Hop 3: cross-validate
      Output: docs/research/2025-08-15-quantum-computing-research-ajitta.md (8 citations)
    </output>
  </example>

  <example name="adaptive-replan" type="happy-path">
    <input>/sc:research 'internal company API migration patterns'</input>
    <output>
      Hop 1: tavily_search → 1 weak source (confidence: 0.3) → replan: broaden query
      Hop 2: broadened search → 6 sources (confidence: 0.7) | Hop 3: filter enterprise patterns
      Output: Report with confidence gap noted
    </output>
  </example>

  </examples>

  <token_note>High consumption — use --uc at 60%+; deep/exhaustive auto-delegate to subagent for context isolation</token_note>

  <gotchas>
  - single-source: Do not conclude from a single source. Cross-verify with at least 2 sources
  - source-quality: Do not use Wikipedia/Reddit as primary source. Cross-check with primary sources
  </gotchas>

  <bounds will="current info|intelligent search|evidence-based|adaptive replan" wont="claims without sources|skip validation|restricted content|carry raw payloads between hops" fallback="Ask user for guidance when uncertain">
    Produce research report, then complete | Defer implementation to /sc:implement | Preserve codebase unchanged
  </bounds>

  <handoff next="/sc:design /sc:implement /sc:brainstorm"/>
</component>
