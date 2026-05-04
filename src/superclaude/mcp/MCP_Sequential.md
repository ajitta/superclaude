<component name="sequential" type="mcp">
  <role>
    <mission>Multi-step reasoning engine for complex analysis and systematic problem solving</mission>
  </role>

  <choose>
  <use>multi-component problem decomposition (3+ interconnected systems or concerns), root-cause analysis with systematic hypothesis generation and falsification, architecture trade-off evaluation across multiple dimensions, security threat modeling with attack-surface enumeration and risk assessment, and multi-phase implementation planning with dependency chains.</use>
  <never>single-step answers (simple lookups, explanations, one-file fixes), code generation (writing code is not thinking — native Claude is faster), and documentation writing (no structured-reasoning value).</never>
  </choose>

  <thought_strategies>
  - Linear: step 1 → 2 → 3 → conclusion (simple decomposition).
  - Hypothesis-Test: hypothesis → evidence → verify → accept/reject → next hypothesis.
  - Branch-Compare: thought N → branch A → branch B → compare → select best.
  - Revision: realize error at step 5 → revise step 3 → continue from corrected base.
  </thought_strategies>

  <when_to_adjust>
  - `totalThoughts` too low? Increase mid-chain — don't force premature conclusions.
  - Dead end? Set `isRevision: true` and reconsider the problematic step.
  - Two valid paths? Branch from the decision point, explore both, then compare.
  - `needsMoreThoughts: true` — signals the chain needs extension even at planned end.
  </when_to_adjust>

  <integration_patterns>
  - Troubleshooting: Sequential:hypotheses → test each → Sequential:synthesize → `/sc:troubleshoot`.
  - Architecture: Sequential:requirements → trade-offs → constraints → recommendation → `/sc:design`.
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
    <does>multi-step reasoning, systematic analysis, hypothesis testing, and trade-off evaluation.</does>
    <never>code generation, simple explanations, and documentation writing.</never>
    <fallback>Use native Claude reasoning for single-step tasks, Adaptive Thinking for moderate complexity.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:troubleshoot /sc:research /sc:design"/>
</component>
