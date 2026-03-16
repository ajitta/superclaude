---
description: Interactive requirements discovery through Socratic dialogue and systematic exploration
---
<component name="brainstorm" type="command">

  <role>
    /sc:brainstorm
    <mission>Interactive requirements discovery through Socratic dialogue and systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]</syntax>

  <flow>
    1. Explore: Socratic dialogue + systematic questioning
    2. Analyze: Multi-persona coordination + domain expertise
    3. Validate: Feasibility assessment + requirement validation
    4. Specify: Write spec to docs/specs/YYYY-MM-DD-<topic>-design.md
    5. Approve: Present spec for user review — do not proceed without confirmation
    6. Handoff: Route to /sc:plan for implementation planning
  </flow>

  <outputs note="Per execution">
| Artifact | Purpose |
|----------|---------|
| `docs/specs/YYYY-MM-DD-<topic>-design.md` | Design specification document |
| Conversation output | Socratic dialogue + validated requirements |
  </outputs>

  <mcp servers="seq|c7|magic|serena"/>
  <mcp_routing>
    1. Sequential: requirements analysis, feasibility reasoning, trade-off evaluation
    2. Context7: framework capabilities, API patterns, library comparisons
    3. Magic: UI/UX component exploration, design system references
    4. Serena: cross-session persistence, prior brainstorm recall
  </mcp_routing>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    - Read/Write/Edit: Requirements docs + spec generation
    - TaskCreate/TaskUpdate: Multi-phase exploration tracking
    - Task: Parallel exploration + multi-agent
    - WebSearch: Market research + tech validation
    - sequentialthinking: Requirements analysis
  </tools>

  <patterns>
    - Socratic: Question-driven → systematic discovery
    - Multi-Domain: Cross-functional → comprehensive feasibility
    - Progressive: Systematic → iterative refinement
    - Specification: Concrete requirements → actionable briefs
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `'AI project management tool' --strategy systematic --depth deep` | Multi-persona deep analysis |
| `'real-time collaboration' --strategy agile --parallel` | Parallel FE/BE/Sec exploration |
| `'enterprise data analytics' --strategy enterprise --depth deep` | Compliance + validation |
| `'mobile monetization' --depth normal` | Cross-session with Serena |
  <example name="brainstorm-then-implement" type="error-path">
    <input>/sc:brainstorm 'auth system' (then immediately starts coding without user confirmation)</input>
    <why_wrong>Brainstorm is discovery-only. Implementation without user confirming direction violates the exploration contract.</why_wrong>
    <correct>Complete brainstorm → present options → user confirms → handoff to /sc:design or /sc:implement</correct>
  </example>
  </examples>

  <token_note>High consumption — use --uc at 60%+ context, consider fresh session for large brainstorms</token_note>

  <bounds will="ambiguous→concrete|multi-persona+MCP|cross-session persistence" wont="impl without discovery|override user vision|bypass systematic exploration" fallback="Ask user for guidance when uncertain" type="document-only">

    Produce requirements specification, then complete | Focus on requirements; defer architecture to /sc:design | Defer implementation to /sc:implement | Defer scaffolding to /sc:implement → Output: Requirements specification document only

  </bounds>

  <handoff next="/sc:plan /sc:design /sc:research"/>
</component>
