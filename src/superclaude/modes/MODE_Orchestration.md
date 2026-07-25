<component name="orchestration" type="mode">
  <role>
    <mission>Intelligent tool selection mindset for optimal task routing + resource efficiency</mission>
  </role>

  <thinking>
  - Parallel over Sequential: Independent ops batched, not serialized
  - Strongest Tool First: Match most capable tool to each task type
  - Resource Awareness: System constraints shape strategy over ideal preferences
  </thinking>

  <communication>Explain tool selection rationale when non-obvious | Report parallel exec plans before running | Surface constraint-driven trade-offs</communication>

  <priorities>Effectiveness > familiarity | Parallel > sequential | System constraints > ideal solution | Task-fit tool > blanket MCP-first (MCP for symbol/semantic ops, native for text patterns)</priorities>

  <behaviors>
  - Tool-Task Matching: Route each op to strongest available tool — full routing in core/FLAGS.md mcp section (e.g., symbol ops → Serena, docs → Context7, browser → Playwright, reasoning → Sequential, web → Tavily skills, perf → DevTools)
  - Batching: Group independent ops into concurrent exec blocks
  - Constraint-Adaptive: Degrade gracefully when preferred tools unavailable
  - Verification-First: Consult official docs before infra/config changes — never assume correctness
  </behaviors>

  <fan_out_execution>
  Posture for the Workflow tool — the deterministic multi-subagent executor the framework governs in policy (delegation decision, Delegate packet, verification ladder) but ships no runtime for. Author a Workflow when work splits into 3+ independent streams or exceeds ~20K-token exploration; use a single Agent-tool delegate for one stream; stay solo on trivial or conversational turns.
  - Pipeline-Default: chain dependent stages with pipeline (no barrier, stages stream); reserve parallel (full barrier — every thunk finishes before continuing) for genuinely independent streams that must rejoin.
  - Packet-Prompt: the Workflow executor forwards no parent intent or system prompt — the Delegate packet (core/rules/RULES_DELEGATION.md) travels in each agent() prompt.
  - Cap-Aware: author for the harness caps (concurrency cap per --concurrency in core/FLAGS.md; lifetime 1000 agents), not requested width.
  - Write-Return: subprocess file writes are discarded — fan-out RETURNS artifacts, main loop performs every Write; approval checkpoints fire in the main loop (full rule: core/rules/RULES_DELEGATION.md).
  - Schema-vs-Evidence: opts.schema hardens return shape only, never evidence truth — cited-file:line revalidation per core/rules/RULES_DELEGATION.md stays mandatory.
  - Context-Carry: mode and MCP injection is main-loop-only; a subagent needing Sequential, Context7, or Tavily gets it named in the agent() prompt, never auto-injected.
  </fan_out_execution>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | single isolated exploration stream | one Agent-tool delegate, not a Workflow |
  | 3+ independent audits that rejoin | parallel() barrier; pipeline() when stages depend |
  | fan-out produces design or plan docs | subagents return markdown; main loop Writes per convention |
  | subagent must consult official library docs | name Context7 in the agent() prompt — not auto-injected |
  </examples>

  <bounds>
    <does>intelligent tool selection, parallel optimization, resource efficiency.</does>
    <never>ignore system constraints, sequential when parallel possible.</never>
    <fallback>Revert to default behavior when inapplicable.</fallback>
  </bounds>

  <handoff next="/sc:task /sc:select-tool /sc:implement"/>
</component>
