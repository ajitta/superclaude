---
description: Deep web research with adaptive planning and intelligent search
---
<component name="research" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:research
    <mission>Deep web research with adaptive planning and intelligent search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <triggers>
    - Research beyond knowledge cutoff
    - Complex research questions
    - Current events + real-time info
    - Academic/technical research
    - Market analysis + competitive intel
  </triggers>

  <flow total_effort="100%">
    <step n="1" effort="5%">Understand: Complexity + ambiguity | Info types needed | Resource reqs | Success criteria</step>
    <step n="2" effort="10%">Plan: Strategy selection | Parallelization opportunities | Question decomposition | Confidence threshold | Investigation milestones</step>
    <step n="3" effort="5%">TaskCreate: Adaptive hierarchy (3-15 tasks) | Dependencies | Progress tracking</step>
    <step n="4" effort="55%" parallel="track">Execute: Parallel search | Multi-hop exploration | Evidence collection | Source tracking | Fallback strategies</step>
    <step n="5" effort="0%" type="parallel">Track: Progress monitoring | Confidence updates | Pattern logging | Gap identification</step>
    <step n="6" effort="10%">Validate: Evidence chains | Credibility verification | Contradiction resolution | Completeness check</step>
    <step n="7" effort="15%">Synthesize: Integration | Cross-source correlation | Report generation | Conclusions + recommendations</step>
  </flow>

  <mcp servers="tavily:search|seq:reasoning|play:extraction|serena:persistence"/>
  <personas p="deep-research-agent"/>

  <depth_levels>
    - quick: 1 hop | summary output
    - standard: 2-3 hops | structured report
    - deep: 3-4 hops | detailed analysis
    - exhaustive: 5 hops | complete investigation
  </depth_levels>

  <defaults effort="high" tokens="2500">
| Depth | Effort | Token Budget | Rationale |
|-------|--------|--------------|-----------|
| quick | low | 500 | Single-hop, summary only |
| standard | medium | 1000 | Multi-source validation |
| deep | high | 2000 | Cross-checking, synthesis |
| exhaustive | high | 2500 | Full investigation, citations |
  </defaults>

  <patterns>
    - Parallel: Batch independent searches | concurrent extractions
    - Evidence: Track results | citations | note uncertainties
    - Output: claudedocs/research_[topic]_[timestamp].md
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `'quantum computing 2024'` | Standard depth research |
| `'AI coding assistants' --depth deep` | Competitive analysis |
| `'distributed systems' --strategy unified` | Best practices research |
  </examples>

  <bounds will="current info|intelligent search|evidence-based" wont="claims without sources|skip validation|restricted content"/>

  <boundaries type="document-only" critical="true">
    <rule>STOP after producing research report</rule>
    <rule>DO NOT implement based on research findings</rule>
    <rule>DO NOT modify codebase</rule>
    <rule>Research and documentation only</rule>
    <output>Research report with citations and findings</output>
  </boundaries>

  <handoff>
    <next command="/sc:design">For architecture based on research</next>
    <next command="/sc:implement">For implementation of researched solutions</next>
    <next command="/sc:brainstorm">For requirements refinement</next>
    <format>Provide research context for implementation decisions</format>
  </handoff>
</component>
