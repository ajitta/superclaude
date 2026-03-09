---
description: Deep web research with adaptive planning and intelligent search
---
<component name="research" type="command">

  <role>
    /sc:research
    <mission>Deep web research with adaptive planning and intelligent search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <flow total_effort="100%">
    <step n="1" effort="5%">Understand: Complexity + ambiguity | Info types needed | Resource reqs | Success criteria</step>
    <step n="2" effort="10%">Plan: Strategy selection | Parallelization opportunities | Question decomposition | Confidence threshold | Investigation milestones</step>
    <step n="3" effort="5%">TaskCreate: Adaptive hierarchy (3-15 tasks) | Dependencies | Progress tracking</step>
    <step n="4" effort="55%" parallel="track">Execute: Parallel search | Multi-hop exploration | Evidence collection | Source tracking | Fallback strategies</step>
    <step n="5" effort="0%" type="parallel">Track: Progress monitoring | Confidence updates | Pattern logging | Gap identification</step>
    <step n="6" effort="10%">Validate: Evidence chains | Credibility verification | Contradiction resolution | Completeness check</step>
    <step n="7" effort="15%">Synthesize: Integration | Cross-source correlation | Report generation | Conclusions + recommendations</step>
  </flow>

  <mcp servers="tavily|seq|play|serena"/>
  <personas p="research"/>

  <depth_levels>
    - quick: 1 hop | summary output
    - standard: 2-3 hops | structured report
    - deep: 3-4 hops | detailed analysis
    - exhaustive: 5 hops | complete investigation
  </depth_levels>

  <patterns>
    - Parallel: Batch independent searches | concurrent extractions
    - Evidence: Track results | citations | note uncertainties
    - Output: claudedocs/research_[topic]_[timestamp].md
  </patterns>


  <examples>

  <example name="standard-depth" type="happy-path">
    <input>/sc:research 'quantum computing breakthroughs 2025'</input>
    <reasoning>Factual query, current events → standard depth, 2-3 hops</reasoning>
    <output>
      Depth: standard (auto-detected)
      Hop 1: tavily_search ('quantum computing 2025 breakthroughs') → 5 sources
      Hop 2: tavily_extract (top 3 URLs) → detailed content
      Hop 3: Cross-validate claims across sources
      Output: claudedocs/research_quantum_computing_20250815.md (structured report, 8 citations)
    </output>
  </example>

  <example name="exhaustive-depth" type="happy-path">
    <input>/sc:research 'AI coding assistants market comparison' --depth exhaustive</input>
    <reasoning>Comparative analysis, multiple entities → exhaustive, 5 hops, parallel search</reasoning>
    <output>
      Depth: exhaustive
      Hop 1: tavily_search (3 parallel queries: market share, features, pricing) → 15 sources
      Hop 2: tavily_extract (top 8 URLs) → feature matrices
      Hop 3: tavily_research (competitive positioning synthesis)
      Hop 4: Entity-specific deep dives (Cursor, Copilot, Claude Code, Windsurf)
      Hop 5: Cross-source contradiction resolution
      Output: Full report with comparison tables, citations, confidence scores per claim
    </output>
  </example>

  <example name="no-sources-found" type="error-path">
    <input>/sc:research 'internal company API migration patterns' --depth standard</input>
    <reasoning>Niche/internal topic → standard search yields sparse results</reasoning>
    <output>
      Depth: standard → auto-escalate to deep
      Hop 1: tavily_search → 1 weak source (confidence: 0.3)
      Recovery: Broaden query to 'API migration best practices enterprise'
      Hop 2: tavily_search (broadened) → 6 sources (confidence: 0.7)
      Hop 3: Filter for enterprise-relevant patterns
      Output: Report with confidence gap noted — "Limited data on internal patterns; general best practices provided. Consider /sc:analyze --scope project for codebase-specific insights."
    </output>
  </example>

  <example name="depth-comparison" type="comparison">
    <input>/sc:research 'React server components' --depth quick</input>
    <reasoning>Same topic at quick depth → single hop, summary only</reasoning>
    <output>
      Depth: quick
      Hop 1: tavily_search → top 3 results summarized
      Output: 5-sentence summary with 3 links
      Contrast: At --depth deep, would produce 3-hop investigation with code examples, migration guide, and performance benchmarks
    </output>
  </example>

  </examples>

  <token_note>High consumption — multi-hop research uses significant context; use --uc at 60%+ or delegate to subagent</token_note>

  <bounds will="current info|intelligent search|evidence-based" wont="claims without sources|skip validation|restricted content" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Produce research report, then complete | Defer implementation to /sc:implement | Preserve codebase unchanged | Research and documentation only → Output: Research report with citations and findings</boundaries>


  <handoff next="/sc:design /sc:implement /sc:brainstorm"/>
</component>
