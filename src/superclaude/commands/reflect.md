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
    2.5. Misunderstanding-Audit: Identify moments where user intent was misread during this session. For each: what triggered the misread, what was the actual intent, what rule would prevent it. Save as feedback memory if not already stored.
    3. Reflect: Evaluate completion criteria
    3.5. Gotchas-Gardening: If `.claude/rules/gotchas/` exists, check: (a) files with `# Last reviewed:` older than 90 days → warn, (b) `paths:` glob patterns that match zero files in current project → warn stale pattern, (c) gotcha entries referencing identifiers not found in codebase → warn potential staleness.
    4. Persist: Write learnings for cross-session capture
  </flow>


  <patterns>
    - Task: approach → goal alignment → deviation → correction
    - Session: info gathering → completeness → quality → insights
    - Completion: progress → criteria → remaining work → decision
    - Gotchas: staleness check → paths: validation → content relevance → prune recommendation
  </patterns>

  <examples>
  | Input | Output |
  |-------|--------|
  | `--type task --analyze` | Goal alignment validation |
  | `--type session --validate` | Session work quality assessment |
  | `--type completion` | Completion readiness evaluation |
  </examples>

  <bounds should="comprehensive reflection|cross-session learning" avoid="override completion|bypass integrity" fallback="Without Serena: use Claude auto memory for session persistence"/>

  <handoff next="/sc:improve /sc:troubleshoot"/>
</component>
