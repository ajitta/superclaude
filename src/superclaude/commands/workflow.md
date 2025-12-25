<component name="workflow" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

  <role>
    /sc:workflow
    <mission>Generate structured implementation workflows from PRDs and feature requirements</mission>
  </role>

  <syntax>/sc:workflow [prd-file|feature] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]</syntax>

  <triggers>
    <t>PRD + spec analysis</t>
    <t>Implementation workflow generation</t>
    <t>Multi-persona coordination</t>
    <t>Cross-session workflow management</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Parse PRD + understand requirements</s>
    <s n="2">Plan: Workflow structure + dependency mapping</s>
    <s n="3">Coordinate: Multi-persona + domain expertise</s>
    <s n="4">Execute: Step-by-step workflows + task coordination</s>
    <s n="5">Validate: Quality gates + workflow completeness</s>
  </flow>

  <mcp servers="seq:analysis|c7:patterns|magic:UI|play:testing|morph:transform|serena:persistence"/>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    <t n="Read/Write/Edit">PRD analysis + workflow docs</t>
    <t n="TodoWrite">Multi-phase progress tracking</t>
    <t n="Task">Parallel workflow + multi-agent</t>
    <t n="WebSearch">Tech research + framework validation</t>
    <t n="sequentialthinking">Dependency analysis</t>
  </tools>

  <patterns>
    <p n="PRD">Document parsing → requirement extraction → strategy</p>
    <p n="Generation">Task decomposition → dependency → planning</p>
    <p n="Multi-Domain">Cross-functional → comprehensive strategies</p>
    <p n="Quality">Validation → testing → deployment planning</p>
  </patterns>

  <examples>
    <ex i="Claudedocs/PRD/feature.md --strategy systematic --depth deep" o="Comprehensive PRD workflow"/>
    <ex i="'user auth system' --strategy agile --parallel" o="Agile + parallel coordination"/>
    <ex i="enterprise-prd.md --strategy enterprise --validate" o="Enterprise + compliance"/>
    <ex i="project-brief.md --depth normal" o="Cross-session with Serena"/>
  </examples>

  <bounds will="comprehensive workflows|multi-persona+MCP|cross-session management" wont="execute impl beyond planning|override dev process|generate without analysis"/>
</component>
