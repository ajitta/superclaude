---
description: Execute complex tasks with intelligent workflow management and delegation
---
<component name="task" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:task
    <mission>Execute complex tasks with intelligent workflow management and delegation</mission>
  </role>

  <syntax>/sc:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate] [--cleanup]</syntax>

  <triggers>
    - Complex multi-agent coordination
    - Structured workflow management
    - Intelligent MCP routing needs
    - Systematic execution requirements
    - Task cleanup and maintenance (Claude Code 2.1.20+)
  </triggers>

  <flow>
    1. Analyze: Parse requirements + optimal strategy
    2. Delegate: Route to MCP + activate personas
    3. Coordinate: Intelligent workflow + parallel
    4. Validate: Quality gates + completion verification
    5. Optimize: Performance analysis + recs
    6. Cleanup: Auto-remove stale/completed tasks (--cleanup)
  </flow>

  <task_cleanup note="Claude Code 2.1.20+">
    <description>Automatic task cleanup via TaskUpdate delete feature</description>
    <cleanable_states>
      - completed: Successfully finished tasks
      - cancelled: User-cancelled tasks
      - stale: Pending > 24 hours without progress
      - blocked: Tasks blocked by unresolved dependencies
    </cleanable_states>
    <usage>
      - /sc:task cleanup: Run automatic task cleanup
      - /sc:task cleanup --dry-run: Preview without deletion
      - Auto-integrated with SelfCheckProtocol
    </usage>
  </task_cleanup>

  <mcp servers="seq|c7|magic|play|morph|serena"/>
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
    - Cleanup: Stale detection → auto-delete → report
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `create 'enterprise auth' --strategy systematic --parallel` | Multi-domain coordination |
| `execute 'feature backlog' --strategy agile --delegate` | Iterative + delegation |
| `execute 'microservices platform' --strategy enterprise --parallel` | Enterprise scale |
| `cleanup` | Auto-remove stale/completed tasks |
| `cleanup --dry-run` | Preview cleanup without deletion |

  </examples>

  <bounds will="complex task coordination|hierarchical breakdown|MCP+persona orchestration|auto cleanup" wont="simple tasks|compromise quality|operate without validation"/>

  <boundaries type="execution" critical="true">
    <rule>Execute tasks via intelligent delegation</rule>
    <rule>Quality gates enforced between phases</rule>
    <rule>Progress reported via TaskCreate/TaskUpdate</rule>
    <rule>Cleanup removes only completed/cancelled/stale tasks</rule>
  </boundaries>

  <completion_criteria>
    - [ ] All subtasks completed or delegated
    - [ ] Quality gates passed
    - [ ] Results aggregated and validated
    - [ ] Stale tasks cleaned up (if --cleanup)
  </completion_criteria>

  <handoff>
    <next command="/sc:test">For validating completed work</next>
    <next command="/sc:git">For committing results</next>
    <format>Summarize execution results for next steps</format>
  </handoff>
</component>
