<component name="task" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="high"/>

  <role>
    /sc:task
    <mission>Execute complex tasks with intelligent workflow management and delegation</mission>
  </role>

  <syntax>/sc:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]</syntax>

  <triggers>
    <t>Complex multi-agent coordination</t>
    <t>Structured workflow management</t>
    <t>Intelligent MCP routing needs</t>
    <t>Systematic execution requirements</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Parse requirements + optimal strategy</s>
    <s n="2">Delegate: Route to MCP + activate personas</s>
    <s n="3">Coordinate: Intelligent workflow + parallel</s>
    <s n="4">Validate: Quality gates + completion verification</s>
    <s n="5">Optimize: Performance analysis + recs</s>
  </flow>

  <mcp servers="seq:analysis|c7:patterns|magic:UI|play:testing|morph:transform|serena:persistence"/>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    <t n="TodoWrite">Epic → Story → Task hierarchy</t>
    <t n="Task">Multi-agent delegation</t>
    <t n="Read/Write/Edit">Documentation + coordination</t>
    <t n="sequentialthinking">Dependency analysis</t>
  </tools>

  <patterns>
    <p n="Hierarchy">Epic → Story → Task → Subtask</p>
    <p n="Strategy">Systematic (comprehensive) | Agile (iterative) | Enterprise (governance)</p>
    <p n="Multi-Agent">Persona → MCP → parallel → integration</p>
    <p n="Cross-Session">Persistence → continuity → enhancement</p>
  </patterns>

  <examples>
    <ex i="create 'enterprise auth' --strategy systematic --parallel" o="Multi-domain coordination"/>
    <ex i="execute 'feature backlog' --strategy agile --delegate" o="Iterative + delegation"/>
    <ex i="execute 'microservices platform' --strategy enterprise --parallel" o="Enterprise scale"/>
  </examples>

  <bounds will="complex task coordination|hierarchical breakdown|MCP+persona orchestration" wont="simple tasks|compromise quality|operate without validation"/>
</component>
