<component name="sequential" type="mcp">
  <role>
    <mission>Multi-step reason engine for complex analyze + systematic problem solve</mission>
  </role>

  <choose>
  <use>multi-component problem decomp (3+ interconnect systems/concerns), root-cause analyze w/ systematic hypothesis gen + falsify, architecture trade-off eval cross multi dimension, security threat model w/ attack-surface enum + risk assess, multi-phase impl plan w/ dependency chain.</use>
  <never>single-step answer (simple lookup, explain, one-file fix), code gen (write code not think — native Claude faster), doc write (no structured-reason value).</never>
  </choose>

  <thought_strategies>
  - Linear: step 1 → 2 → 3 → conclude (simple decomp).
  - Hypothesis-Test: hypothesis → evidence → verify → accept/reject → next hypothesis.
  - Branch-Compare: thought N → branch A → branch B → compare → pick best.
  - Revision: spot error step 5 → revise step 3 → continue from fix base.
  </thought_strategies>

  <when_to_adjust>
  - `totalThoughts` too low? Bump mid-chain — no force premature conclude.
  - Dead end? Set `isRevision: true`, redo bad step.
  - Two valid path? Branch from decision point, explore both, compare.
  - `needsMoreThoughts: true` — signal chain need extend past planned end.
  </when_to_adjust>

  <integration_patterns>
  - Troubleshoot: Sequential:hypotheses → test each → Sequential:synthesize → `/sc:troubleshoot`.
  - Architecture: Sequential:requirements → trade-offs → constraints → recommend → `/sc:design`.
  - Research: Tavily:gather → Sequential:analyze → gaps → Tavily:targeted → Sequential:conclude.
  - Review: Read code → Sequential:security-analysis → Sequential:perf-analysis → `/sc:review`.
  </integration_patterns>

  <examples>
| Input | Thoughts | Strategy |
|---|---|---|
| why is API slow under load | 6-8 | Hypothesis-test: connection pool → query plan → serialization → GC |
| design auth microservice | 8-12 | Linear: requirements → protocols → token strategy → session → failure modes |
| debug intermittent test failure | 5-7 | Branch-compare: timing issue vs state leak vs resource contention |
| evaluate React vs Vue for project | 6-8 | Branch-compare: branch per framework → score on criteria → recommend |
  </examples>

  <bounds>
    <does>multi-step reason, systematic analyze, hypothesis test, trade-off eval.</does>
    <never>code gen, simple explain, doc write.</never>
    <fallback>Use native Claude reason for single-step task, Adaptive Thinking for moderate complex.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:troubleshoot /sc:research /sc:design"/>
</component>