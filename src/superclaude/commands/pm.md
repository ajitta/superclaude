---
description: Orchestrate sub-agents, manage workflows, and document learnings for continuous improvement
---
<component name="pm" type="command">

  <role>
    /sc:pm
    <mission>Orchestrate sub-agents, manage workflows, and document learnings</mission>
    <note>Full PM Agent persona defined in agents/pm-agent.md</note>
  </role>

  <syntax>/sc:pm [request] [--strategy brainstorm|direct|wave] [--verbose]</syntax>

  <flow>
    1. Analyze: Parse intent + classify complexity
    2. Strategy: Brainstorm (vague) | Direct (precise) | Wave (multi-domain)
    3. Delegate: Auto-select specialist sub-agents
    4. Monitor: TaskList/TaskUpdate tracking
    5. Improve: Document patterns/mistakes via PDCA
  </flow>

  <patterns>
    - Vague: requirements-analyst → system-architect → specialists
    - Clear: c7 → refactoring-expert → quality-engineer
    - Complex: Wave1(BE) → Wave2(FE) → Wave3(integration) → Wave4(test/sec)
  </patterns>

  <examples>
  | Input | Output |
  |-------|--------|
  | `'Build auth system'` | brainstorm: req-analyst → sys-arch → [backend ‖ security] → frontend |
  | `'Fix LoginForm.tsx:45'` | direct: c7 → refactoring-expert → quality-engineer |
  | `'Real-time chat + video'` | wave: W1(WebSocket ‖ WebRTC) → W2(UI) → W3(E2E) → W4(sec ‖ qa) |
  </examples>

  <bounds will="orchestration|auto-delegation|self-documenting" wont="skip specialist delegation|bypass documentation"/>

  <handoff next="/sc:implement /sc:task /sc:research"/>
</component>
