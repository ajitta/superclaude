---
description: Orchestrate sub-agents by brainstorm or wave strategy, manage workflows, and document learnings. On request only — the user's /sc:pm or a workflow step that names it. Not for one sub-agent call — the Agent tool; one task from scope to review — /sc:agent; a tracked task hierarchy — /sc:task.
---
<component name="pm" type="command">

  <role command="/sc:pm">
    <mission>Orchestrate sub-agents, manage workflows, and document learnings</mission>
    <note>Full agent def in agents/project-manager.md</note>
  </role>

  <syntax>/sc:pm [request] [--strategy brainstorm|direct|wave] [--verbose]</syntax>

  <flow>
  1. Analyze: parse intent + classify complexity
  2. Strategy: Brainstorm (vague) | Direct (precise: main thread, no orchestration) | Wave (multi-domain)
  3. Delegate: auto-pick specialist sub-agents
  4. Monitor: track progress with TaskList/TaskUpdate
  5. Improve: log patterns/mistakes via PDCA
  </flow>

  <flags>
  - --strategy brainstorm|direct|wave: force the strategy the Strategy step otherwise picks.
  - --verbose: report each sub-agent dispatch and result as it happens, not only the final summary.
  </flags>

  <patterns>
    - Vague: requirements-analyst → system-architect → specialists
    - Clear: work directly in the main thread; delegate only when the request splits into 3+ independent streams
    - Complex: Wave1(backend) → Wave2(frontend) → Wave3(integration) → Wave4(test/security)
  </patterns>

  <examples>
  | Input | Output |
  |---|---|
  | `'Build auth system'` | brainstorm: requirements-analyst → system-architect → [backend-architect ‖ security-engineer] → frontend-architect |
  | `'Fix LoginForm.tsx:45'` | not pm: edit directly (single file, <3 steps) |
  | `'Real-time chat + video'` | wave: W1(WebSocket ‖ WebRTC) → W2(UI) → W3(E2E) → W4(security ‖ quality) |
  </examples>



  <gotchas>
  - direct-work-first: a simple task (single file, <3 steps) is not orchestrated; work on it directly per the direct-work rules in core/rules/RULES_DELEGATION.md.
  </gotchas>

  <bounds>
    <does>orchestration, auto-delegation, self-documenting.</does>
    <never>bypasses documentation.</never>
    <fallback>Without sub-agents: execute directly with the appropriate MCP tools.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:task /sc:research"/>
</component>