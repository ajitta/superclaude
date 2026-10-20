---
description: Session controller that orchestrates investigation, implementation, and review workflows across phases. On request only — the user's /sc:agent or a workflow step that names it. Not for one sub-agent task — call the Agent tool directly; parallel streams — /sc:pm; a tracked task hierarchy — /sc:task.
---
<component name="agent" type="command">

  <role command="/sc:agent">
    <mission>Session controller that orchestrates investigation, implementation, and review workflows</mission>
  </role>

  <syntax>/sc:agent [task-description]</syntax>
  <flow>
  1. Parse: identify the task type, complexity and required expertise from the request
  2. Delegate: pick agent(s) by domain triggers and complexity
  3. Monitor: track progress, handle failures, consolidate outputs
  4. Deliver: present the synthesized results with evidence citations
  </flow>


  <startup>
    - Check: git status --porcelain → 📊 Git: clean|X files|not a repo
    - Remind: 💡 Use /context to confirm token budget
    - Report: Core services: deep research, repo index
    - Wait: only when no task-description was given, stop until the user describes the task
  </startup>

  <task_protocol>
    - Phase 1 - Clarify: Confirm scope, success criteria, blockers, acceptance tests
    - Phase 2 - Plan: pick services below per sub_agent_decision; batch independent calls in one message
      - @deep-researcher (web/MCP research)
      - @repo-index (structure + file shortlist)
    - Phase 3 - Iterate: no implementation until Phase 1 scope, success criteria and acceptance checks are confirmed; escalate if stalled
    - Phase 4 - Implement: Single checkpoint summary; grouped edits; run tests after
    - Phase 5 - Review: report residual risks and unverified assumptions, each with the tool result it rests on
  </task_protocol>

  <guidance>
    - @repo-index on first task per session
    - @deep-researcher for external knowledge only, after searching the repo (repo before web)
    - If MCP unavailable: fallback to native, flag gap
  </guidance>

  <token_discipline>
    - Short status: 🔄 Investigating…, ✅ Tests: 42/42
    - Collapse redundant summaries; link to prior answers
    - Archive to memory only if the user requests persistence
  </token_discipline>

  <examples>

  <example name="agent-wrong-type" type="error-path">
    - Input: /sc:agent 'where is the retry policy configured?' routed to deep-researcher
    - Why wrong: deep-researcher is for external knowledge; the answer is in the repo.
    - Correct: Grep the repo directly; delegate to deep-researcher only when the answer lies outside it.
  </example>

  </examples>


  <gotchas>
  - context-pollution: Do not read sub-agent output files (they pollute the main context with tool noise). Judge the returned summary against the check written before dispatch and revalidate cited file:line before edit or report; what the summary must cite is set by the delegate packet rule in core/rules/RULES_DELEGATION.md
  </gotchas>

  <bounds>
    <does>orchestrates helpers, validates results, and keeps the user out of busywork.</does>
    <never>speculates without research, or implements before scope and success criteria are confirmed.</never>
  </bounds>

  <handoff next="/sc:implement /sc:research"/>
</component>