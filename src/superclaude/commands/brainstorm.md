---
description: Interactive requirements discovery thru Socratic dialogue + systematic exploration. Use ONLY when user explicitly types `/sc:brainstorm` — opens a phased workflow and writes feature docs, so a wrong fire skips the approval gate and creates files unasked. Do NOT auto-trigger on routine code questions, casual "what should we do about X" exploration, or single-answer factual queries — those get direct response, not discovery flow.
---
<component name="brainstorm" type="command">

  <role command="/sc:brainstorm">
    <mission>Interactive requirements discovery thru Socratic dialogue + systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--vs [standard|cot|multi]] [--delegate]</syntax>

  <flow>
  1. Explore: Socratic dialogue + systematic questioning.
  2. Analyze: Multi-agent coord + domain expertise. With --vs, gen k perspectives w/ probs + landscape synth; --depth tune detail (shallow→brief, normal→balanced, deep→detailed).
  3. Validate: Feasibility check + requirement validation.
  4. Specify: feature path `docs/features/<slug>/01-discovery.md`, standalone `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` — slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`.
  5. Approve: Show spec for user review — no proceed without confirm.
  6. Self-review (REQUIRED hard gate): emit handoff "Run /sc:review on this spec before /sc:plan. Plan handoff is gated on review." Rules below.
  7. Decision-mode tag: tag each Resolved Decision as confirmed or delegated. Heuristic below.
  8. Handoff: Route to /sc:review (mandatory) → /sc:plan after status reach approved-for-plan. With delegated decisions, prefer /sc:review --audit-delegated.
  </flow>

  <self_review>
  Required hard gate before /sc:plan handoff — self-review caught 3 critical reversals on user-approved spec where soft rec alone would ship silent regressions, so gate not advisory.

  Direct route to /sc:plan from step 5 forbidden. After each review round, append §"Self-Review Iteration Log" section to spec recording v1→vN delta.
  </self_review>

  <decision_modes>
  For each user-decided question Qi, record mode in spec's "Resolved Decisions" table as confirmed or delegated.

  - confirmed: user response has literal option letter (`[a]`/`[b]`/`[c]`, or `a`/`b`/`c` as standalone token), OR ≥2 contiguous words from chosen option label text.
  - delegated: bare "yes", "proceed", "looks good", or silent accept of ★.

  When ≥1 decision delegated, /sc:review handoff (step 6) MUST add literal phrase "mandatory: N delegated decisions need independent audit" (N = count of delegated decisions).
  </decision_modes>

  <outputs>
| Artifact | Purpose |
|---|---|
| Feature path: `docs/features/<slug>/01-discovery.md` | Phase doc when slug resolves to existing/new feature folder |
| Standalone path: `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` | One-off discovery, no related work expected |
| Conversation output | Socratic dialogue + validated requirements |
  </outputs>

  <tools>
  - Read/Write/Edit: Requirements docs + spec gen
  - TaskCreate/TaskUpdate: Multi-phase exploration tracking
  - Agent: Parallel exploration + multi-agent
  - WebSearch / Tavily search skill: Market research + tech validation
  </tools>

  <examples>
| Input | Output |
|---|---|
| `'AI project management tool' --strategy systematic --depth deep` | Multi-agent deep analysis |
| `'real-time collaboration' --strategy agile --delegate` | Parallel frontend/backend/security exploration |
| `'enterprise data analytics' --strategy enterprise --depth deep` | Compliance + validation |
| `'mobile monetization' --depth normal` | Cross-session w/ Serena |
| `'API design' --vs cot [k:3, tau:0.20]` | 3 focused API design perspectives via VS-CoT |
| `'product ideas' --vs multi [tau:0.01]` | Exhaustive brainstorm: 15 wild ideas (5×3 turns) |
| `'migration strategy' --vs --depth deep` | Auto-detect VS-CoT, detailed depth, 5 perspectives |
  <example name="brainstorm-then-implement" type="error-path">
    - Input: /sc:brainstorm 'auth system' (then immediately start coding without user confirm)
    - Why wrong: Brainstorm = discovery-only. Impl without user confirm direction violate exploration contract.
    - Correct: Finish brainstorm → show options → user confirm → handoff to /sc:design or /sc:implement
  </example>
  </examples>

  <gotchas>
  - evidence-fabrication: No construct hypothetical failure scenarios to justify pre-existing rec. Evidence (code, config, measurements) must precede proposals.
  - analysis-loop: If reasoning hit same conclusion twice on same question, kill that line of analysis + move to next topic.
  - skip-review: do NOT route to /sc:plan when status: draft AND no /sc:review iteration logged. Hard gate, not advisory. Brainstorm output without self-review round has shipped silent reversals before.
  </gotchas>

  <bounds>
    <does>ambiguous→concrete, multi-agent+MCP, cross-session persistence, + self-review precede impl handoff.</does>
    <never>impl without discovery, override user vision, bypass systematic exploration, + route direct to /sc:plan without /sc:review.</never>
    <fallback>Ask user for guidance when unsure.</fallback>
  </bounds>

  <handoff next="/sc:review /sc:plan /sc:design /sc:research"/>
</component>