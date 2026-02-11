---
description: Task reflection and validation using Serena MCP analysis capabilities
---
<component name="reflect" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:reflect
    <mission>Task reflection and validation using Serena MCP analysis capabilities</mission>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <triggers>task completion validation|session progress|cross-session learning|quality gate</triggers>

  <flow>
    1. Analyze: Task state + session progress (Serena)
    2. Validate: Adherence + completion quality
    3. Reflect: Deep analysis + session insights
    4. Document: Update metadata + capture learnings
    5. Optimize: Process improvement recs
  </flow>

  <mcp servers="serena"/>

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

  <checklist note="Completion criteria">
    - [ ] Task/session state analyzed via Serena (show memory read)
    - [ ] Adherence validated against goals (list goal vs actual)
    - [ ] Insights captured for cross-session learning (show memory write)
    - [ ] Actionable recommendations provided (specific next steps)
  </checklist>

  <examples>

| Input | Output |
|-------|--------|
| `--type task --analyze` | Goal alignment validation |
| `--type session --validate` | Session work quality |
| `--type completion` | Completion readiness eval |

  </examples>

  <bounds will="comprehensive reflection|TaskList bridge|cross-session learning" wont="operate without Serena|override completion|bypass integrity" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only" critical="true">
    <rule>Produce reflection report, then complete</rule>
    <rule>Preserve code unchanged during reflection</rule>
    <rule>Report issues with recommendations; defer fixes to /sc:improve</rule>
    <output>Reflection analysis with recommendations</output>
  </boundaries>

  <handoff>
    <next command="/sc:improve">For implementing reflection insights</next>
    <next command="/sc:troubleshoot">For addressing identified issues</next>
    <next command="/sc:save">For persisting reflection learnings</next>
    <format>Provide actionable recommendations for follow-up</format>
  </handoff>
</component>
