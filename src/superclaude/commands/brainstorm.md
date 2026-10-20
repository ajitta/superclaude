---
description: Interactive requirements discovery through Socratic dialogue + systematic exploration that writes feature docs. On request only — the user's /sc:brainstorm or a workflow step that names it. Not for routine questions or casual "what should we do about X" — answer directly.
---
<component name="brainstorm" type="command">

  <role command="/sc:brainstorm">
    <mission>Interactive requirements discovery through Socratic dialogue + systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--vs [standard|cot|multi]] [--delegate]</syntax>

  <flow>
  1. Explore: Socratic dialogue + systematic questioning. When the slug folder holds `00-intent.md`, read it first and keep its wording as the anchor; 01-discovery records an "Intent coverage" table mapping each of its five fields to how discovery made it concrete.
  2. Analyze: weigh the idea from each relevant domain angle in turn. With --vs, generate k perspectives with probabilities and a landscape synthesis; --depth tunes detail (shallow→brief, normal→balanced, deep→detailed).
  3. Validate: Feasibility check + requirement validation.
  4. Specify: feature path `docs/features/<slug>/01-discovery.md`, standalone `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` — slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`.
  5. Approve: Show spec for user review — no proceed without confirm.
  6. Self-review (hard gate): the spec stays `status: draft`; emit "Run /sc:review --scope spec <path> before /sc:plan." Claude does not review the spec itself in place of /sc:review. Rules in the self-review section below.
  7. Decision-mode tag: tag each Resolved Decision as confirmed or delegated. Heuristic below.
  8. Handoff: Route to /sc:review --scope spec (mandatory); /sc:plan follows once /sc:review has set `status: approved-for-plan`. With delegated decisions, add --audit-delegated to the /sc:review call.
  </flow>

  <flags>
  - --strategy systematic|agile|enterprise: systematic works through every requirement area in order; agile splits the work into parallel streams (e.g. frontend, backend, security) and iterates; enterprise adds compliance and validation requirements throughout.
  - --depth shallow|normal|deep: detail level set in the Analyze step.
  </flags>

  <self_review>
  Required hard gate before /sc:plan handoff, because a spec the user approved can still carry reversed decisions that only an independent review catches; the gate is not advisory.

  A direct route to /sc:plan from the Approve step is forbidden. /sc:review records each round in the spec's "Self-Review Iteration Log" section (v1→vN delta) and sets `status: approved-for-plan` when the gate passes; brainstorm writes neither.
  </self_review>

  <decision_modes>
  For each user-decided question Qi, record mode in spec's "Resolved Decisions" table as confirmed or delegated.

  - confirmed: user response has literal option letter (`[a]`/`[b]`/`[c]`, or `a`/`b`/`c` as standalone token), OR ≥2 contiguous words from chosen option label text.
  - delegated: bare "yes", "proceed", "looks good", or silent accept of ★.

  When ≥1 decision delegated, /sc:review handoff (the Handoff step) adds the literal phrase "mandatory: N delegated decisions need independent audit" (N = count of delegated decisions).
  </decision_modes>

  <outputs>
| Artifact | Purpose |
|---|---|
| Feature path: `docs/features/<slug>/01-discovery.md` | Phase doc when slug resolves to existing/new feature folder |
| Standalone path: `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` | One-off discovery, no related work expected |
| Conversation output | Socratic dialogue + validated requirements |
  </outputs>

  <tools>
  - WebSearch / Tavily search skill: Market research + tech validation
  </tools>

  <examples>
| Input | Output |
|---|---|
| `'AI project management tool' --strategy systematic --depth deep` | Multi-agent deep analysis |
| `'real-time collaboration' --strategy agile --delegate` | Parallel frontend/backend/security exploration |
| `'enterprise data analytics' --strategy enterprise --depth deep` | Compliance + validation |
| `'mobile monetization' --depth normal` | Cross-session via /sc:save |
| `'API design' --vs cot [k:3] [tau:0.20]` | 3 focused API design perspectives via VS-CoT |
| `'product ideas' --vs multi [tau:0.01]` | Exhaustive brainstorm: 15 wild ideas (5×3 turns) |
| `'migration strategy' --vs --depth deep` | Auto-detect VS-CoT, detailed depth, 5 perspectives |
  <example name="brainstorm-then-implement" type="error-path">
    - Input: /sc:brainstorm 'auth system' (then immediately start coding without user confirm)
    - Why wrong: Brainstorm = discovery-only. Implementing before the user confirms the direction violates the exploration contract.
    - Correct: Finish brainstorm → user confirms direction → /sc:review on the spec → /sc:design or /sc:plan
  </example>
  </examples>

  <gotchas>
  - evidence-fabrication: Do not construct hypothetical failure scenarios to justify a recommendation already made. Evidence (code, config, measurements) must precede proposals.
  - analysis-loop: If reasoning hit same conclusion twice on same question, kill that line of analysis + move to next topic.
  - skip-review: do not route to /sc:plan while the spec is `status: draft` or its Self-Review Iteration Log has no /sc:review round. The gate is hard, not advisory.
  </gotchas>

  <bounds>
    <does>turns ambiguous requests into concrete requirements, uses multi-agent and MCP analysis, persists across sessions, and routes the spec to /sc:review before the plan handoff.</does>
    <never>implements without discovery, overrides the user's vision, bypasses systematic exploration, or routes directly to /sc:plan without /sc:review.</never>
  </bounds>

  <handoff next="/sc:review /sc:plan /sc:design /sc:research"/>
</component>