<component name="brainstorm" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

  <role>
    /sc:brainstorm
    <mission>Interactive requirements discovery through Socratic dialogue and systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]</syntax>

  <triggers>
    <t>Ambiguous project ideas</t>
    <t>Requirements discovery needs</t>
    <t>Concept validation requests</t>
    <t>Cross-session refinement</t>
  </triggers>

  <flow>
    <s n="1">Explore: Socratic dialogue + systematic questioning</s>
    <s n="2">Analyze: Multi-persona coordination + domain expertise</s>
    <s n="3">Validate: Feasibility assessment + requirement validation</s>
    <s n="4">Specify: Concrete specs + cross-session persistence</s>
    <s n="5">Handoff: Actionable briefs for implementation</s>
  </flow>

  <mcp servers="seq:reasoning|c7:patterns|magic:UI|play:UX|morph:analysis|serena:persistence"/>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    <t n="Read/Write/Edit">Requirements docs + spec generation</t>
    <t n="TodoWrite">Multi-phase exploration tracking</t>
    <t n="Task">Parallel exploration + multi-agent</t>
    <t n="WebSearch">Market research + tech validation</t>
    <t n="sequentialthinking">Requirements analysis</t>
  </tools>

  <patterns>
    <p n="Socratic">Question-driven → systematic discovery</p>
    <p n="Multi-Domain">Cross-functional → comprehensive feasibility</p>
    <p n="Progressive">Systematic → iterative refinement</p>
    <p n="Specification">Concrete requirements → actionable briefs</p>
  </patterns>

  <examples>
    <ex i="'AI project management tool' --strategy systematic --depth deep" o="Multi-persona deep analysis"/>
    <ex i="'real-time collaboration' --strategy agile --parallel" o="Parallel FE/BE/Sec exploration"/>
    <ex i="'enterprise data analytics' --strategy enterprise --validate" o="Compliance + validation"/>
    <ex i="'mobile monetization' --depth normal" o="Cross-session with Serena"/>
  </examples>

  <bounds will="ambiguous→concrete|multi-persona+MCP|cross-session persistence" wont="impl without discovery|override user vision|bypass systematic exploration"/>
</component>
