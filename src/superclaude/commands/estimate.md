<component name="estimate" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:estimate
    <mission>Provide development estimates for tasks, features, or projects with intelligent analysis</mission>
  </role>

  <syntax>/sc:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]</syntax>

  <triggers>
    <t>Development time/effort estimates</t>
    <t>Project scoping + resource allocation</t>
    <t>Feature breakdown estimation</t>
    <t>Risk assessment + confidence intervals</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Scope, complexity, deps, patterns</s>
    <s n="2">Calculate: Methodology + benchmarks</s>
    <s n="3">Validate: Cross-reference + domain expertise</s>
    <s n="4">Present: Breakdown + confidence + risk</s>
    <s n="5">Track: Accuracy for improvement</s>
  </flow>

  <mcp servers="seq:analysis|c7:benchmarks"/>
  <personas p="arch|perf|pm"/>

  <tools>
    <t n="Read/Grep/Glob">Codebase complexity analysis</t>
    <t n="TodoWrite">Estimation breakdown tracking</t>
    <t n="Task">Multi-domain estimation delegation</t>
    <t n="Bash">Project + dependency analysis</t>
  </tools>

  <patterns>
    <p n="Scope">Requirements → complexity → patterns → risk</p>
    <p n="Method">Time|Effort|Complexity|Cost approaches</p>
    <p n="Multi-Domain">Arch + Perf + Timeline assessment</p>
    <p n="Validation">Benchmarks → cross-check → confidence</p>
  </patterns>

  <examples>
    <ex i="'auth system' --type time --unit days --breakdown" o="8 days, 85% confidence"/>
    <ex i="'monolith to microservices' --type complexity --breakdown" o="Risk + dependency map"/>
    <ex i="'optimize performance' --type effort --unit hours" o="Effort by category"/>
  </examples>

  <bounds will="systematic estimates|confidence intervals|multi-persona analysis" wont="guarantee accuracy|estimate without analysis|override benchmarks"/>
</component>
