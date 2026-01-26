---
description: Execute complex tasks with intelligent workflow management and delegation
---
<component name="task" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:task
    <mission>Execute complex tasks with intelligent workflow management and delegation</mission>
  </role>

  <syntax>/sc:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]</syntax>

  <triggers>
    - Complex multi-agent coordination
    - Structured workflow management
    - Intelligent MCP routing needs
    - Systematic execution requirements
  </triggers>

  <flow>
    1. Analyze: Parse requirements + optimal strategy
    2. Delegate: Route to MCP + activate personas
    3. Coordinate: Intelligent workflow + parallel
    4. Validate: Quality gates + completion verification
    5. Optimize: Performance analysis + recs
  </flow>

  <mcp servers="seq:analysis|c7:patterns|magic:UI|play:testing|morph:transform|serena:persistence"/>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    - TaskCreate/TaskUpdate: Epic → Story → Task hierarchy
    - Task: Multi-agent delegation
    - Read/Write/Edit: Documentation + coordination
    - sequentialthinking: Dependency analysis
  </tools>

  <patterns>
    - Hierarchy: Epic → Story → Task → Subtask
    - Strategy: Systematic (comprehensive) | Agile (iterative) | Enterprise (governance)
    - Multi-Agent: Persona → MCP → parallel → integration
    - Cross-Session: Persistence → continuity → enhancement
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `create 'enterprise auth' --strategy systematic --parallel` | Multi-domain coordination |
| `execute 'feature backlog' --strategy agile --delegate` | Iterative + delegation |
| `execute 'microservices platform' --strategy enterprise --parallel` | Enterprise scale |

  </examples>

  <bounds will="complex task coordination|hierarchical breakdown|MCP+persona orchestration" wont="simple tasks|compromise quality|operate without validation"/>

  <boundaries type="execution" critical="true">
    <rule>EXECUTE tasks via intelligent delegation</rule>
    <rule>Quality gates enforced between phases</rule>
    <rule>Progress reported via TaskCreate/TaskUpdate</rule>
  </boundaries>

  <completion_criteria>
    - [ ] All subtasks completed or delegated
    - [ ] Quality gates passed
    - [ ] Results aggregated and validated
  </completion_criteria>

  <handoff>
    <next command="/sc:test">For validating completed work</next>
    <next command="/sc:git">For committing results</next>
    <format>Summarize execution results for next steps</format>
  </handoff>
</component>
