---
description: Task reflection and validation using Serena MCP analysis capabilities
---
<component name="reflect" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5"/>

  <role>
    /sc:reflect
    <mission>Task reflection and validation using Serena MCP analysis capabilities</mission>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <triggers>
    - Task completion validation
    - Session progress analysis
    - Cross-session learning capture
    - Quality gate verification
  </triggers>

  <flow>
    1. Analyze: Task state + session progress (Serena)
    2. Validate: Adherence + completion quality
    3. Reflect: Deep analysis + session insights
    4. Document: Update metadata + capture learnings
    5. Optimize: Process improvement recs
  </flow>

  <mcp servers="serena:reflection|serena:memory"/>

  <tools>
    - think_about_task_adherence: Goal alignment + deviation ID
    - think_about_collected_information: Completeness assessment
    - think_about_whether_you_are_done: Completion criteria eval
    - write_memory/read_memory: Cross-session persistence
  </tools>

  <patterns>
    - Task: Approach → goal alignment → deviation → correction
    - Session: Info gathering → completeness → quality → insights
    - Completion: Progress → criteria → remaining work → decision
    - Learning: Insights → persistence → enhanced understanding
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `--type task --analyze` | Goal alignment validation |
| `--type session --validate` | Session work quality |
| `--type completion` | Completion readiness eval |

  </examples>

  <bounds will="comprehensive reflection|TodoWrite bridge|cross-session learning" wont="operate without Serena|override completion|bypass integrity"/>
</component>
