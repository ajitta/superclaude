<component name="sequential" type="mcp">
  <role>
    <mission>Multi-step reasoning engine for complex analysis and systematic problem solving</mission>
  </role>

  ## Thinking Model
  Each thought is a step in an evolving chain. The chain can branch, revise, and adapt.

  **Core parameters:**
  - `thought` — current reasoning step (analysis, hypothesis, revision, or verification)
  - `thoughtNumber` / `totalThoughts` — position and estimated total (adjustable mid-chain)
  - `nextThoughtNeeded` — true until a satisfactory answer is reached
  - `isRevision` + `revisesThought` — mark when reconsidering a previous step
  - `branchFromThought` + `branchId` — explore alternative paths without losing the main chain

  <choose>
  Use:
  - Multi-component problems: 3+ interconnected systems or concerns
  - Root cause analysis: systematic hypothesis generation and falsification
  - Architecture decisions: trade-off evaluation with multiple dimensions
  - Security threat modeling: attack surface enumeration and risk assessment
  - Planning: multi-phase implementation with dependencies

  Avoid:
  - Single-step answers: simple lookups, explanations, one-file fixes
  - Code generation: writing code is not thinking — use native Claude
  - Documentation: writing docs doesn't need structured reasoning
  </choose>

  ## Thought Strategies
  - **Linear**: step 1 → 2 → 3 → conclusion (simple decomposition)
  - **Hypothesis-test**: hypothesis → evidence → verify → accept/reject → next hypothesis
  - **Branch-compare**: thought N → branch A → branch B → compare → select best
  - **Revision**: realize error at step 5 → revise step 3 → continue from corrected base

  ## When to Adjust
  - `totalThoughts` too low? Increase mid-chain — don't force premature conclusions
  - Dead end? Set `isRevision: true` and reconsider the problematic step
  - Two valid paths? Branch from the decision point, explore both, then compare
  - `needsMoreThoughts: true` — signals the chain needs extension even at planned end

  ## Integration Patterns
  - **Troubleshooting**: Sequential:hypotheses → test each → Sequential:synthesize → /sc:troubleshoot
  - **Architecture**: Sequential:requirements → trade-offs → constraints → recommendation → /sc:design
  - **Research**: Tavily:gather → Sequential:analyze → gaps → Tavily:targeted → Sequential:conclude
  - **Review**: Read code → Sequential:security-analysis → Sequential:perf-analysis → /sc:review

  <examples>
| Input | Thoughts | Strategy |
|-------|----------|----------|
| why is API slow under load | 6-8 | Hypothesis-test: connection pool → query plan → serialization → GC |
| design auth microservice | 8-12 | Linear: requirements → protocols → token strategy → session → failure modes |
| debug intermittent test failure | 5-7 | Branch-compare: timing issue vs state leak vs resource contention |
| evaluate React vs Vue for project | 6-8 | Branch-compare: branch per framework → score on criteria → recommend |
  </examples>

  <bounds will="multi-step reasoning|systematic analysis|hypothesis testing|trade-off evaluation" wont="code generation|simple explanations|documentation writing" fallback="Use native Claude reasoning for single-step tasks, Adaptive Thinking for moderate complexity"/>

  <handoff next="/sc:analyze /sc:troubleshoot /sc:research /sc:design"/>
</component>
