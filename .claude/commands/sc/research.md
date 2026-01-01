---
description: Deep web research with adaptive planning and intelligent search
---
<component name="research" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

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

  <flow>
    <step n="1" effort="5-10%">Understand: Complexity + ambiguity | Info types needed | Resource reqs | Success criteria</step>
    <step n="2" effort="10-15%">Plan: Strategy selection | Parallelization opportunities | Question decomposition | Investigation milestones</step>
    <step n="3" effort="5%">TodoWrite: Adaptive hierarchy (3-15 tasks) | Dependencies | Progress tracking</step>
    <step n="4" effort="50-60%">Execute: Parallel search | Multi-hop exploration | Evidence collection | Source tracking</step>
    <step n="5" effort="continuous">Track: Progress monitoring | Confidence updates | Pattern logging | Gap identification</step>
    <step n="6" effort="10-15%">Validate: Evidence chains | Credibility verification | Contradiction resolution | Completeness check</step>
  </flow>

  <mcp servers="tavily:search|seq:reasoning|play:extraction|serena:persistence"/>
  <personas p="deep-research-agent"/>

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
| Input | Output |
|-------|--------|
| `'quantum computing 2024'` | Standard depth research |
| `'AI coding assistants' --depth deep` | Competitive analysis |
| `'distributed systems' --strategy unified` | Best practices research |
  </examples>

  <bounds will="current info|intelligent search|evidence-based" wont="claims without sources|skip validation|restricted content"/>
</component>
