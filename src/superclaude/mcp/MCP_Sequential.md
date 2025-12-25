<component name="sequential" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>think|think-hard|ultrathink|debug|architecture|analysis|reasoning|sequential</triggers>

  <role>
    <mission>Multi-step reasoning engine for complex analysis and systematic problem solving</mission>
  </role>

  <choose>
    <use context="complex problems">3+ interconnected components</use>
    <use context="systematic analysis">Root cause, architecture review, security assessment</use>
    <use context="structured approach">Decomposition, evidence gathering</use>
    <use context="cross-domain">Frontend + backend + database + infrastructure</use>
    <avoid context="simple tasks">Basic explanations, single-file, straightforward fixes</avoid>
  </choose>

  <synergy>
    <with n="Context7">Sequential coordinates → Context7 provides patterns</with>
    <with n="Magic">Sequential analyzes UI logic → Magic implements</with>
    <with n="Playwright">Sequential identifies test strategy → Playwright executes</with>
  </synergy>

  <examples>
    <ex i="why is API slow" o="Sequential" r="systematic perf analysis"/>
    <ex i="design microservices" o="Sequential" r="structured system design"/>
    <ex i="debug auth flow" o="Sequential" r="multi-component investigation"/>
    <ex i="security vulnerabilities" o="Sequential" r="comprehensive threat modeling"/>
    <ex i="explain this function" o="Native Claude" r="simple explanation"/>
  </examples>
</component>
