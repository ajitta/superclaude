---
description: Orchestrate sub-agents, manage workflows, and document learnings for continuous improvement
---
<component name="pm" type="command">

  <role>
    /sc:pm
    <mission>Orchestrate sub-agents, manage workflows, and document learnings for continuous improvement</mission>
    <note>Always-active foundation: runs at session start, orchestrates transparently. Persona defined in agents/pm-agent.md</note>
  </role>

  <syntax>/sc:pm [request] [--strategy brainstorm|direct|wave] [--verbose]</syntax>

  <flow>
    1. Analyze: Parse intent + classify complexity
    2. Strategy: Brainstorm | Direct | Wave
    3. Delegate: Auto-select specialist sub-agents
    4. Orchestrate: Dynamic MCP loading
    5. Monitor: TaskList/TaskUpdate tracking
    6. Improve: Document patterns/mistakes
    7. Evaluate: PDCA continuous improvement
  </flow>

  <mcp servers="seq|c7|magic|play|morph|serena|tavily"/>
  <personas p="pm"/>

  <mcp_phases>
    - Discovery: seq|c7
    - Design: seq|magic
    - Implementation: c7|magic|morph
    - Testing: play|seq
  </mcp_phases>

  <patterns>
    - Vague: Discovery → requirements-analyst → system-architect → specialists
    - Clear: c7 → refactoring-expert → quality-engineer
    - Complex: Wave1(BE‖) → Wave2(FE‖) → Wave3(integration) → Wave4(test/sec‖)
  </patterns>


  <self_correction note="Defined in agents/pm-agent.md; inherited at invocation">
    Rule: Never retry without understanding WHY it failed
    1. STOP → 2. Investigate → 3. Hypothesis → 4. New Approach → 5. Execute → 6. Learn (write_memory)
  </self_correction>

  <examples>

  <example name="brainstorm-strategy" type="happy-path">
    <input>/sc:pm 'Build auth system'</input>
    <reasoning>Vague scope, multi-domain (DB + API + UI + security) → brainstorm strategy</reasoning>
    <output>
      Strategy: brainstorm
      Flow: requirements-analyst → system-architect → [backend-architect ‖ security-engineer] → frontend-architect
      MCP: seq (decomposition) → c7 (auth patterns) → magic (login UI)
      Tasks: 4 stories, 12 subtasks across 3 waves
    </output>
  </example>

  <example name="direct-strategy" type="happy-path">
    <input>/sc:pm 'Fix LoginForm.tsx:45 — button disabled state not updating'</input>
    <reasoning>Precise file:line, single-domain (FE), clear symptom → direct strategy</reasoning>
    <output>
      Strategy: direct
      Flow: c7 (React state patterns) → refactoring-expert → quality-engineer
      MCP: c7 (useEffect/useState docs)
      Tasks: 1 story, 2 subtasks
    </output>
  </example>

  <example name="wave-strategy" type="happy-path">
    <input>/sc:pm 'Real-time chat with video calling'</input>
    <reasoning>Multi-domain (WebSocket + WebRTC + UI + infra), parallelizable → wave strategy</reasoning>
    <output>
      Strategy: wave
      Wave1: backend-architect (WebSocket server ‖ WebRTC signaling)
      Wave2: frontend-architect (chat UI ‖ video UI) using Wave1 APIs
      Wave3: integration testing (E2E flows)
      Wave4: security-engineer (auth) ‖ quality-engineer (load testing)
    </output>
  </example>

  <example name="missing-prerequisites" type="error-path">
    <input>/sc:pm 'Deploy to production'</input>
    <reasoning>No test results in context, no CI config detected → self-correction triggers</reasoning>
    <output>
      Strategy: direct (blocked)
      Self-correction: STOP → Investigate (no test evidence) → Hypothesis (untested code)
      Recovery: "No test results found. Run /sc:test --coverage first?"
      Handoff: /sc:test → then retry /sc:pm 'Deploy to production'
    </output>
  </example>

  <example name="cross-command-handoff" type="handoff">
    <input>/sc:pm 'Optimize API response times'</input>
    <reasoning>Performance domain → needs profiling before action</reasoning>
    <output>
      Strategy: direct
      Handoff chain: /sc:analyze --focus perf → bottleneck report → /sc:improve --type performance → /sc:test --type e2e
      MCP: devtools (profiling) → seq (bottleneck reasoning) → c7 (optimization patterns)
    </output>
  </example>

  </examples>

  <token_note>High consumption — orchestrates multiple sub-agents; consider --strategy direct for simple tasks</token_note>

  <bounds will="seamless orchestration|auto-delegation|zero-token MCP|self-documenting" wont="expose internal complexity to user|skip specialist delegation|bypass documentation" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="execution">Orchestrate sub-agents and manage workflows | Delegate to specialists based on complexity analysis | Document patterns and mistakes for continuous improvement → Output: Coordinated task execution with progress tracking</boundaries>


  <handoff next="/sc:implement /sc:task /sc:research"/>
</component>
