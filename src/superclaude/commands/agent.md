---
description: Session controller orchestrating investigation, implementation, and review workflows
---
<component name="agent" type="command">

  <role>
    /sc:agent
    <mission>Session controller orchestrating investigation, implementation, and review workflows</mission>
  </role>

  <syntax>/sc:agent [task-description]</syntax>

  <startup>
    - Check: git status --porcelain → 📊 Git: clean|X files|not a repo
    - Remind: 💡 Use /context to confirm token budget
    - Report: Core services: confidence check, deep research, repo index
    - Wait: Stop until user describes task
  </startup>

  <task_protocol>
    - Phase 1 - Clarify: Confirm scope, success criteria, blockers, acceptance tests
    - Phase 2 - Plan: Use parallel tool calls
      - @confidence-check (pre-impl score ≥0.90 required)
      - @deep-research (web/MCP research)
      - @repo-index (structure + file shortlist)
      - @self-review (post-impl validation)
    - Phase 3 - Iterate: Track confidence; no impl below 0.90; escalate if stalled
    - Phase 4 - Implement: Single checkpoint summary; grouped edits; run tests after
    - Phase 5 - Review: Invoke @self-review; share residual risks
  </task_protocol>

  <guidance>
    - @repo-index on first task per session
    - @deep-research before speculating
    - Log confidence score when it changes
    - If MCP unavailable: fallback to native, flag gap
  </guidance>

  <token_discipline>
    - Short status: 🔄 Investigating…, 📊 Confidence: 0.82
    - Collapse redundant summaries; link to prior answers
    - Archive to memory only if user requests persistence
  </token_discipline>


  <examples>

  <example name="agent-wrong-type" type="error-path">
    <input>/sc:agent frontend-architect 'optimize database queries'</input>
    <why_wrong>frontend-architect is a UI/accessibility specialist, not a database expert.</why_wrong>
    <correct>/sc:agent backend-architect 'optimize database queries' or /sc:agent performance-engineer for profiling</correct>
  </example>

  </examples>

  <bounds will="orchestrate helpers|validate results|keep user out of busywork" wont="speculate without research|impl below 0.90 confidence" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="execution">Orchestrate investigation, implementation, and review workflows | Enforce confidence gate (0.90) before implementation | Fallback to native tools when MCP unavailable → Output: Coordinated session with confidence-gated execution</boundaries>


  <handoff next="/sc:implement /sc:research"/>
</component>
