---
description: Orchestrate sub-agents, manage workflows, and document learnings for continuous improvement. Use when the user types `/sc:pm` or asks for project-manager-style orchestration of multiple parallel work streams with learnings capture. Do NOT auto-trigger on a single sub-agent delegation, small workflow, or one-off task tracking — use direct Agent tool calls instead.
---
<component name="pm" type="command">

  <role command="/sc:pm">
    <mission>Orchestrate sub-agents, manage workflows, and document learnings</mission>
    <note>Full agent def in agents/project-manager.md</note>
  </role>

  <syntax>/sc:pm [request] [--strategy brainstorm|direct|wave] [--verbose]</syntax>

  <flow>
  1. Analyze: parse intent + classify complexity
  2. Strategy: Brainstorm (vague) | Direct (precise) | Wave (multi-domain)
  3. Delegate: auto-pick specialist sub-agents
  4. Monitor: TaskList/TaskUpdate track
  5. Improve: log patterns/mistakes via PDCA
  </flow>

  <patterns>
    - Vague: requirements-analyst → system-architect → specialists
    - Clear: c7 → refactoring-expert → quality-engineer
    - Complex: Wave1(backend) → Wave2(frontend) → Wave3(integration) → Wave4(test/security)
  </patterns>

  <examples>
  | Input | Output |
  |---|---|
  | `'Build auth system'` | brainstorm: req-analyst → sys-arch → [backend ‖ security] → frontend |
  | `'Fix LoginForm.tsx:45'` | direct: c7 → refactoring-expert → quality-engineer |
  | `'Real-time chat + video'` | wave: W1(WebSocket ‖ WebRTC) → W2(UI) → W3(E2E) → W4(security ‖ quality) |
  </examples>



  <gotchas>
  - direct-work-first: no orchestrate simple task (<3 steps). Do direct per sub_agent_decision rules
  - intent-propagation: pass user original request verbatim to sub-agents, not your interpretation
  </gotchas>

  <bounds>
    <does>orchestration, auto-delegation, self-documenting.</does>
    <never>skip specialist delegation, bypass documentation.</never>
    <fallback>No sub-agents: execute direct with proper MCP tools.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:task /sc:research"/>
</component>