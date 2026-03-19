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
    1. Understand: Complexity + ambiguity assessment | Info types needed | Success criteria | Prior research check (Serena)
    2. Plan: Strategy selection (planning-only|intent|unified) | Depth determination | Hop pattern (entity|temporal|conceptual|causal) | Query decomposition | Parallelization map
    3. Execute: Multi-hop search with parallel batching | Evidence collection + source tracking | Inline progress monitoring | Adaptive replan on: confidence<0.6, contradictions>30%, dead ends
    4. Validate: Cross-source verification | Credibility scoring (1-5) | Per-claim confidence | Contradiction resolution | Completeness + gap check
    5. Synthesize: Cross-source correlation | Credibility-weighted integration | Structured report | Conclusions + recommendations | Uncertainties + next steps
  </flow>

  <depth_flow>
    quick:       Understand(brief) → Plan(auto: 1-hop, no decomposition) → Execute(1 hop) → Validate(light) → Synthesize(summary)
    standard:    Full 5-phase, 2-3 hops
    deep:        Full 5-phase + mid-Execute validation checkpoint, 3-4 hops
    exhaustive:  Full 5-phase + multiple checkpoints + subagent delegation, 5+ hops
  </depth_flow>

  <depth_levels>
    quick:      1 hop | auto plan | light validation | summary output
    standard:   2-3 hops | full plan | full validation | structured report
    deep:       3-4 hops | full plan + mid-checkpoints | thorough validation | detailed analysis
    exhaustive: 5+ hops | full plan + subagent delegation | multi-checkpoint validation | complete investigation
  </depth_levels>

  <mcp servers="tavily|seq|c7|serena"/>
  <mcp_routing>
    1. Sequential: query decomposition, contradiction analysis, multi-step reasoning, replan decisions
    2. Tavily: broad search (tavily_search), deep extraction (tavily_extract), synthesis (tavily_research), site crawling (tavily_crawl), URL discovery (tavily_map)
    3. Context7: framework/library documentation, API patterns, version-specific info
    4. Serena: prior research recall, cross-session persistence, pattern storage
  </mcp_routing>
  <personas p="research"/>

  <tools>
    - Tavily: tavily_search, tavily_extract, tavily_research, tavily_crawl, tavily_map
    - Native: WebSearch/WebFetch (fallback when Tavily unavailable)
    - Sequential: Multi-step reasoning + replan decisions
    - Read/Write: Report generation to docs/research/
    - Serena: Cross-session research memory
  </tools>

  <parallel_strategy>
    Parallel: Independent sub-queries | Cross-validation after collection | Multi-entity deep dives
    Sequential: Same-source extraction chains | Dependent hop sequences | Rate-limited APIs
    Batch: Similar query variants | Related entity lookups
  </parallel_strategy>

  <patterns>
    - Multi-Hop: entity→affiliations→related | temporal→changes→history | conceptual→details→edge cases | causal→proximate→root
    - Adaptive: confidence&lt;0.6→broaden query | contradictions&gt;30%→add sources | dead end→change hop pattern | sparse results→escalate depth
    - Credibility: 5=Official/standards | 4=Peer-reviewed | 3=Industry reports | 2=Expert blogs | 1=Community posts
    - Parallel: Batch independent | concurrent extractions | post-collection cross-validate
    - Evidence: Source-linked claims | dated access | uncertainty flagged
    - Output: docs/research/YYYY-MM-DD-<topic>-research-<username>.md
  </patterns>

  <token_efficiency>
    - quick/standard: inline execution (single context)
    - deep/exhaustive: delegate to deep-researcher subagent (context isolation)
    - Between hops: summarize intermediate results, discard raw payloads
    - Source deduplication before synthesis
    - Use --uc at 60%+ context
  </token_efficiency>

  <examples>

  <example name="standard-depth" type="happy-path">
    <input>/sc:research 'quantum computing breakthroughs 2025'</input>
    <reasoning>Factual query, current events → standard depth, 2-3 hops</reasoning>
    <output>
      Depth: standard (auto-detected)
      Hop 1: tavily_search ('quantum computing 2025 breakthroughs') → 5 sources
      Hop 2: tavily_extract (top 3 URLs) → detailed content
      Hop 3: Cross-validate claims across sources
      Output: docs/research/2025-08-15-quantum-computing-research-ajitta.md (structured report, 8 citations)
    </output>
  </example>

  <example name="exhaustive-depth" type="happy-path">
    <input>/sc:research 'AI coding assistants market comparison' --depth exhaustive</input>
    <reasoning>Comparative analysis, multiple entities → exhaustive, 5 hops, parallel search, subagent delegation</reasoning>
    <output>
      Depth: exhaustive → delegate to deep-researcher subagent
      Hop 1: tavily_search (3 parallel queries: market share, features, pricing) → 15 sources
      Hop 2: tavily_extract (top 8 URLs) → feature matrices
      Hop 3: Validate checkpoint — confidence 0.7, proceed
      Hop 4: Entity-specific deep dives (Cursor, Copilot, Claude Code, Windsurf)
      Hop 5: Cross-source contradiction resolution + credibility weighting
      Output: Full report with comparison tables, citations, per-claim confidence scores
    </output>
  </example>

  <example name="adaptive-replan" type="happy-path">
    <input>/sc:research 'internal company API migration patterns' --depth standard</input>
    <reasoning>Niche topic → standard search yields sparse results → adaptive replan triggers</reasoning>
    <output>
      Depth: standard
      Hop 1: tavily_search → 1 weak source (confidence: 0.3)
      Replan: confidence&lt;0.6 → broaden query to 'API migration best practices enterprise'
      Hop 2: tavily_search (broadened) → 6 sources (confidence: 0.7)
      Hop 3: Filter for enterprise-relevant patterns
      Output: Report with confidence gap noted — "Limited data on internal patterns; general best practices provided."
    </output>
  </example>

  <example name="quick-depth" type="comparison">
    <input>/sc:research 'React server components' --depth quick</input>
    <reasoning>Same topic at quick depth → reduced plan, single hop, summary only</reasoning>
    <output>
      Depth: quick
      Plan: auto (1-hop, no decomposition)
      Hop 1: tavily_search → top 3 results summarized
      Validate: light (source titles + dates only)
      Output: 5-sentence summary with 3 links
      Contrast: At --depth deep, would produce 3-hop investigation with code examples, migration guide, and performance benchmarks
    </output>
  </example>

  </examples>

  <token_note>High consumption — multi-hop research uses significant context; use --uc at 60%+ or delegate to subagent for deep/exhaustive</token_note>

  <bounds will="current info|intelligent search|evidence-based|adaptive replan" wont="claims without sources|skip validation|restricted content|carry raw payloads between hops" fallback="Ask user for guidance when uncertain" type="document-only">

    Produce research report, then complete | Defer implementation to /sc:implement | Preserve codebase unchanged | Research and documentation only → Output: Research report with citations and findings

  </bounds>

  <handoff next="/sc:design /sc:implement /sc:brainstorm"/>
</component>
