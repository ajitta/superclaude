---
description: Interactive requirements discovery through Socratic dialogue and systematic exploration. Use when the user types `/sc:brainstorm`, asks to "spec out a feature", "discover requirements", or says an idea is "vague" / "fuzzy". Do NOT auto-trigger on routine code questions, casual "what should we do about X" exploration, or single-answer factual queries — those get a direct response, not a discovery flow.
---
<component name="brainstorm" type="command">

  <role command="/sc:brainstorm">
    <mission>Interactive requirements discovery through Socratic dialogue and systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--vs [standard|cot|multi]] [--parallel]</syntax>

  <flow>
  1. Explore: Socratic dialogue + systematic questioning.
  2. Analyze: Multi-agent coordination + domain expertise. With --vs, generate k perspectives with probabilities and a landscape synthesis; --depth tunes detail (shallow→brief, normal→balanced, deep→detailed).
  3. Validate: Feasibility assessment + requirement validation.
  4. Specify: Write spec to docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md (frontmatter: status: draft, revised: <today>).
  5. Approve: Present spec for user review — do not proceed without confirmation.
  6. Self-review (REQUIRED hard gate): emit handoff "Run /sc:review on this spec before /sc:plan. Plan handoff is gated on review." Detailed rules below.
  7. Decision-mode tagging: tag each Resolved Decision as confirmed or delegated. Heuristic below.
  8. Handoff: Route to /sc:review (mandatory) → /sc:plan after status reaches approved-for-plan. With delegated decisions present, prefer /sc:review --audit-delegated.
  </flow>

  <self_review>
  Required hard gate before /sc:plan handoff — self-review caught 3 critical reversals on a user-approved spec where soft recommendation alone would have shipped silent regressions, so this gate is not advisory.

  Direct routing to /sc:plan from step 5 is prohibited. After each review round, append a §"Self-Review Iteration Log" section to the spec recording v1→vN delta.
  </self_review>

  <decision_modes>
  For each user-decided question Qi, record mode in the spec's "Resolved Decisions" table as confirmed or delegated.

  - confirmed: user response contains a literal option letter (`[a]`/`[b]`/`[c]`, or `a`/`b`/`c` as a standalone token), OR ≥2 contiguous words from the chosen option's label text.
  - delegated: bare "yes", "proceed", "looks good", or silent acceptance of ★.

  When ≥1 decision is delegated, the /sc:review handoff (step 6) MUST add the explicit phrase "mandatory: N delegated decisions need independent audit" (N = count of delegated decisions).
  </decision_modes>

  <outputs>
| Artifact | Purpose |
|---|---|
| `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` | Discovery specification document |
| Conversation output | Socratic dialogue + validated requirements |
  </outputs>

  <tools>
  - Read/Write/Edit: Requirements docs + spec generation
  - TaskCreate/TaskUpdate: Multi-phase exploration tracking
  - Agent: Parallel exploration + multi-agent
  - WebSearch/Tavily: Market research + tech validation
  - sequentialthinking: Requirements analysis, trade-off evaluation
  - sequentialthinking: Requirements analysis
  </tools>

  <patterns>
    - Socratic: Question-driven → systematic discovery
    - Multi-Domain: Cross-functional → comprehensive feasibility
    - Progressive: Systematic → iterative refinement
    - Specification: Concrete requirements → actionable briefs
    - Verbalized-Sampling: --vs → distribution-level diversity (k candidates, τ dial, probability-weighted landscape)
  </patterns>

  <examples>
| Input | Output |
|---|---|
| `'AI project management tool' --strategy systematic --depth deep` | Multi-agent deep analysis |
| `'real-time collaboration' --strategy agile --parallel` | Parallel frontend/backend/security exploration |
| `'enterprise data analytics' --strategy enterprise --depth deep` | Compliance + validation |
| `'mobile monetization' --depth normal` | Cross-session with Serena |
| `'API design' --vs cot [k:3, tau:0.20]` | 3 focused API design perspectives via VS-CoT |
| `'product ideas' --vs multi [tau:0.01]` | Exhaustive brainstorm: 15 wild ideas (5×3 turns) |
| `'migration strategy' --vs --depth deep` | Auto-detect VS-CoT, detailed depth, 5 perspectives |
  <example name="brainstorm-then-implement" type="error-path">
    - Input: /sc:brainstorm 'auth system' (then immediately starts coding without user confirmation)
    - Why wrong: Brainstorm is discovery-only. Implementation without user confirming direction violates the exploration contract.
    - Correct: Complete brainstorm → present options → user confirms → handoff to /sc:design or /sc:implement
  </example>
  </examples>

  <gotchas>
  - evidence-fabrication: Do not construct hypothetical failure scenarios to justify a pre-existing recommendation. Evidence (code, config, measurements) must precede proposals.
  - seq-loop: If sequential thinking reaches the same conclusion twice on the same question, terminate that analysis branch and move to next topic.
  - skip-review: do NOT route to /sc:plan when status: draft AND no /sc:review iteration logged. Hard gate, not advisory. Brainstorm output without a self-review round has historically shipped silent reversals.
  </gotchas>

  <bounds>
    <does>ambiguous→concrete, multi-agent+MCP, cross-session persistence, and self-review precedes implementation handoff.</does>
    <never>impl without discovery, override user vision, bypass systematic exploration, and route directly to /sc:plan without /sc:review.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:review /sc:plan /sc:design /sc:research"/>
</component>
