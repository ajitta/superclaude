---
description: Interactive requirements discovery through Socratic dialogue and systematic exploration
---
<component name="brainstorm" type="command">

  <role>
    /sc:brainstorm
    <mission>Interactive requirements discovery through Socratic dialogue and systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--vs [standard|cot|multi]] [--parallel]</syntax>

  <flow>
    1. Explore: Socratic dialogue + systematic questioning
    2. Analyze: Multi-agent coordination + domain expertise
       (--vs): VS distribution generation — k perspectives with probabilities + landscape synthesis.
               Multi-agent insights inform post-hoc labeling. --depth maps: shallow→brief, normal→balanced, deep→detailed.
    3. Validate: Feasibility assessment + requirement validation
    4. Specify: Write spec to docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>)
    5. Approve: Present spec for user review — do not proceed without confirmation
    6. Handoff: Route to /sc:plan for implementation planning
  </flow>

  <outputs>
| Artifact | Purpose |
|----------|---------|
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
|-------|--------|
| `'AI project management tool' --strategy systematic --depth deep` | Multi-agent deep analysis |
| `'real-time collaboration' --strategy agile --parallel` | Parallel frontend/backend/security exploration |
| `'enterprise data analytics' --strategy enterprise --depth deep` | Compliance + validation |
| `'mobile monetization' --depth normal` | Cross-session with Serena |
| `'API design' --vs cot [k:3, tau:0.20]` | 3 focused API design perspectives via VS-CoT |
| `'product ideas' --vs multi [tau:0.01]` | Exhaustive brainstorm: 15 wild ideas (5×3 turns) |
| `'migration strategy' --vs --depth deep` | Auto-detect VS-CoT, detailed depth, 5 perspectives |
  <example name="brainstorm-then-implement" type="error-path">
    <input>/sc:brainstorm 'auth system' (then immediately starts coding without user confirmation)</input>
    <why_wrong>Brainstorm is discovery-only. Implementation without user confirming direction violates the exploration contract.</why_wrong>
    <correct>Complete brainstorm → present options → user confirms → handoff to /sc:design or /sc:implement</correct>
  </example>
  </examples>

  <gotchas>
  - evidence-fabrication: Do not construct hypothetical failure scenarios to justify a pre-existing recommendation. Evidence (code, config, measurements) must precede proposals.
  - seq-loop: If sequential thinking reaches the same conclusion twice on the same question, terminate that analysis branch and move to next topic.
  </gotchas>

  <bounds will="ambiguous→concrete|multi-agent+MCP|cross-session persistence" wont="impl without discovery|override user vision|bypass systematic exploration" fallback="Ask user for guidance when uncertain">

    Produce requirements specification, then complete | Focus on requirements; defer architecture to /sc:design | Defer implementation to /sc:implement | Defer scaffolding to /sc:implement → Output: Requirements specification document only

  </bounds>

  <handoff next="/sc:plan /sc:design /sc:research"/>
</component>
