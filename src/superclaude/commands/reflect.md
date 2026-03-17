---
description: Task reflection and validation using Serena MCP analysis capabilities
---
<component name="reflect" type="command">

  <role>
    /sc:reflect
    <mission>Task reflection and validation using analysis capabilities</mission>
    <note>For evidence-based completion verification, use /sc:test with the verification workflow</note>
  </role>

  <syntax>/sc:reflect [--type task|session|completion] [--analyze] [--validate]</syntax>

  <flow>
    1. Analyze: Assess completeness of collected information
    2. Validate: Check goal alignment and deviation
    3. Reflect: Evaluate completion criteria
    4. Persist: Write learnings for cross-session capture
  </flow>

  <mcp servers="serena"/>

  <patterns>
    - Task: approach → goal alignment → deviation → correction
    - Session: info gathering → completeness → quality → insights
    - Completion: progress → criteria → remaining work → decision
  </patterns>

  <examples>
  | Input | Output |
  |-------|--------|
  | `--type task --analyze` | Goal alignment validation |
  | `--type session --validate` | Session work quality assessment |
  | `--type completion` | Completion readiness evaluation |
  </examples>

  <bounds will="comprehensive reflection|cross-session learning" wont="override completion|bypass integrity" fallback="Without Serena: use Claude auto memory for session persistence"/>

  <handoff next="/sc:improve /sc:troubleshoot"/>
</component>
