<component name="research" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

  <role>
    /sc:research
    <mission>Deep web research with adaptive planning and intelligent search</mission>
  </role>

  <syntax>/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]</syntax>

  <triggers>
    <t>Research beyond knowledge cutoff</t>
    <t>Complex research questions</t>
    <t>Current events + real-time info</t>
    <t>Academic/technical research</t>
    <t>Market analysis + competitive intel</t>
  </triggers>

  <flow>
    <s n="1">Understand (5-10%): Complexity + success criteria</s>
    <s n="2">Plan (10-15%): Strategy + parallelization</s>
    <s n="3">TodoWrite (5%): Adaptive hierarchy (3-15 tasks)</s>
    <s n="4">Execute (50-60%): Parallel search + multi-hop + evidence</s>
    <s n="5">Track: Progress + confidence + gaps</s>
    <s n="6">Validate (10-15%): Evidence chains + credibility + contradictions</s>
  </flow>

  <mcp servers="tavily:search|seq:reasoning|play:extraction|serena:persistence"/>
  <personas p="deep-research-agent"/>

  <depth_levels>
    <level n="quick">1 hop | summary output</level>
    <level n="standard">2-3 hops | structured report</level>
    <level n="deep">3-4 hops | detailed analysis</level>
    <level n="exhaustive">5 hops | complete investigation</level>
  </depth_levels>

  <patterns>
    <p n="Parallel">Batch independent searches | concurrent extractions</p>
    <p n="Evidence">Track results | citations | note uncertainties</p>
    <p n="Output">claudedocs/research_[topic]_[timestamp].md</p>
  </patterns>

  <examples>
    <ex i="'quantum computing 2024'" o="Standard depth research"/>
    <ex i="'AI coding assistants' --depth deep" o="Competitive analysis"/>
    <ex i="'distributed systems' --strategy unified" o="Best practices research"/>
  </examples>

  <bounds will="current info|intelligent search|evidence-based" wont="claims without sources|skip validation|restricted content"/>
</component>
