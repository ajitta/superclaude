<component name="implement" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:implement
    <mission>Feature and code implementation with intelligent persona activation and MCP integration</mission>
  </role>

  <syntax>/sc:implement [feature] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>

  <triggers>
    <t>Feature development requests</t>
    <t>Code implementation with framework reqs</t>
    <t>Multi-domain development</t>
    <t>Implementation with testing</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Requirements + tech context</s>
    <s n="2">Plan: Approach + activate personas</s>
    <s n="3">Generate: Code + framework best practices</s>
    <s n="4">Validate: Security + quality checks</s>
    <s n="5">Integrate: Docs + testing recs</s>
  </flow>

  <mcp servers="c7:patterns|seq:analysis|magic:UI|play:testing"/>
  <personas p="arch|fe|be|sec|qa"/>

  <tools>
    <t n="Write/Edit/MultiEdit">Code generation</t>
    <t n="Read/Grep/Glob">Project analysis</t>
    <t n="TodoWrite">Multi-file progress</t>
    <t n="Task">Large-scale delegation</t>
  </tools>

  <patterns>
    <p n="Context">Framework detect → persona + MCP activation</p>
    <p n="Flow">Requirements → code → validation → integration</p>
    <p n="Multi-Persona">FE + BE + Sec → comprehensive solutions</p>
    <p n="Quality">Impl → testing → docs → validation</p>
  </patterns>

  <examples>
    <ex i="user profile --type component --framework react" o="Magic UI + FE best practices"/>
    <ex i="auth API --type api --safe --with-tests" o="BE + Sec personas"/>
    <ex i="payment system --type feature --with-tests" o="Multi-persona coordination"/>
    <ex i="dashboard widget --framework vue" o="C7 Vue patterns"/>
  </examples>

  <bounds will="intelligent impl|framework best practices|comprehensive testing" wont="arch decisions without consultation|conflict with security|override safety"/>
</component>
