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
    - Report: Core services: deep research, repo index
    - Wait: Stop until user describe task
  </startup>

  <task_protocol>
    - Phase 1 - Clarify: Confirm scope, success criteria, blockers, acceptance tests
    - Phase 2 - Plan: pick services below per sub_agent_decision; batch independent calls in one message
      - @deep-researcher (web/MCP research)
      - @repo-index (structure + file shortlist)
    - Phase 3 - Iterate: no impl until Phase 1 scope, success criteria and acceptance checks are confirmed; escalate if stalled
    - Phase 4 - Implement: Single checkpoint summary; grouped edits; run tests after
    - Phase 5 - Review: report residual risks and unverified assumptions, each with the tool result it rests on
  </task_protocol>

  <guidance>
    - @repo-index on first task per session
    - @deep-researcher before speculate
    - If MCP unavailable: fallback to native, flag gap
  </guidance>

  <token_discipline>
    - Short status: 🔄 Investigating…, ✅ Tests: 42/42
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
  - context-pollution: No read sub-agent output files (pollute main context with tool noise). Judge the returned summary against the check written before dispatch and revalidate cited file:line before edit or report; what the summary must cite is set by the delegate packet rule in core/rules/RULES_DELEGATION.md
  </gotchas>

  <bounds>
    <does>orchestrate helpers, validate results, keep user out of busywork.</does>
    <never>speculate without research, or implement before scope and success criteria are confirmed.</never>
  </bounds>

  <handoff next="/sc:implement /sc:research"/>
</component>