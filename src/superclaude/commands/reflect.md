---
description: Task reflection and validation using Serena MCP analysis capabilities
---
<component name="reflect" type="command">

  <role>
    /sc:reflect
    <mission>Task reflection and validation using Serena MCP analysis capabilities</mission>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <triggers>task completion validation|session progress|cross-session learning|quality gate</triggers>

  <flow>
    1. Analyze: think_about_collected_information() → assess completeness
    2. Validate: think_about_task_adherence() → check goal alignment
    3. Reflect: think_about_whether_you_are_done() → evaluate completion
    4. Persist: write_memory("learnings_[topic]", insights) → cross-session capture
    5. Optimize: Process improvement recs
    Fallback (no Serena): Use native reasoning for steps 1-3, Write for step 4
  </flow>

  <mcp servers="serena"/>
  <personas p="review"/>

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

  <example name="reflect-before-work" type="error-path">
    <input>/sc:reflect --type session --validate (at session start, no work done yet)</input>
    <why_wrong>Reflecting on an empty session produces no useful validation. Nothing to reflect on.</why_wrong>
    <correct>Do meaningful work first, then /sc:reflect --type session to validate progress and quality.</correct>
  </example>
  </examples>

  <bounds will="comprehensive reflection|TaskList bridge|cross-session learning" wont="override completion|bypass integrity" fallback="Without Serena: use native reasoning for reflection, Grep/Read for code analysis. Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Produce reflection report, then complete | Preserve code unchanged during reflection | Report issues with recommendations; defer fixes to /sc:improve → Output: Reflection analysis with recommendations</boundaries>


  <handoff next="/sc:improve /sc:troubleshoot /sc:save"/>
</component>
