---
description: Session controller orchestrating investigation, implementation, and review workflows. Use ONLY when user explicitly types `/sc:agent` — drives multi-phase orchestration. Do NOT auto-trigger when single sub-agent invocation suffices; use Agent tool directly for one-off delegations.
---
<component name="agent" type="command">

  <role command="/sc:agent">
    <mission>Session controller orchestrate investigate, implement, review workflows</mission>
  </role>

  <syntax>/sc:agent [task-description]</syntax>
  <flow>
  1. Parse: ID task type, complexity, required expertise from request
  2. Delegate: Pick agent(s) by domain triggers + complexity
  3. Monitor: Track progress, handle fails, consolidate outputs
  4. Deliver: Present synth results with evidence citations
  </flow>


  <startup>
    - Check: git status --porcelain → 📊 Git: clean|X files|not a repo
    - Remind: 💡 Use /context to confirm token budget
    - Report: Core services: confidence check, deep research, repo index
    - Wait: Stop until user describe task
  </startup>

  <task_protocol>
    - Phase 1 - Clarify: Confirm scope, success criteria, blockers, acceptance tests
    - Phase 2 - Plan: Use parallel tool calls
      - @confidence-check (pre-impl score ≥0.90 required)
      - @deep-researcher (web/MCP research)
      - @repo-index (structure + file shortlist)
      - @self-review (post-impl validation)
    - Phase 3 - Iterate: Track confidence; no impl below 0.90; escalate if stalled
    - Phase 4 - Implement: Single checkpoint summary; grouped edits; run tests after
    - Phase 5 - Review: Invoke @self-review; share residual risks
  </task_protocol>

  <guidance>
    - @repo-index on first task per session
    - @deep-researcher before speculate
    - Log confidence score when change
    - If MCP unavailable: fallback to native, flag gap
  </guidance>

  <token_discipline>
    - Short status: 🔄 Investigating…, 📊 Confidence: 0.82
    - Collapse redundant summaries; link to prior answers
    - Archive to memory only if user request persistence
  </token_discipline>

  <examples>

  <example name="agent-wrong-type" type="error-path">
    - Input: /sc:agent frontend-architect 'optimize database queries'
    - Why wrong: frontend-architect is UI/a11y specialist, not DB expert.
    - Correct: /sc:agent backend-architect 'optimize database queries' or /sc:agent performance-engineer for profiling
  </example>

  </examples>


  <gotchas>
  - scope-leak: No let sub-agents expand scope past original request. Pass user words verbatim
  - context-pollution: No read sub-agent output files (pollute main context with tool noise). Treat returned summary as advisory, not authoritative — require cite {files inspected, commands run, exact evidence, assumptions, residual risks}, then revalidate cited file:line before edit or report
  </gotchas>

  <bounds>
    <does>orchestrate helpers, validate results, keep user out of busywork.</does>
    <never>speculate without research and impl below 0.90 confidence.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:research"/>
</component>