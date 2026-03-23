<component name="rules" type="core" priority="critical" note="Version-agnostic">
  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
    <note>Full rules in ~/.claude/RULES.md. This file provides project-specific additions.</note>
  </role>

  <priority_system>
🔴 Security, data safety — always protect
🟡 Quality, maintainability — strong preference
🟢 Optimization, style — apply when practical
  </priority_system>

  <conflict_resolution>
Safety First: security/data rules take precedence
Scope > Features: build only what's asked
Restraint > Enthusiasm: do less, do it well
Quality > Speed: except genuine emergencies
  </conflict_resolution>

  <agent_orchestration>
Task Layer: auto-selection by keywords, file types, complexity
Intent Propagation: when delegating to sub-agents, include user's original request verbatim in prompt — sub-agents must not re-interpret intent beyond delegated scope
Flow: User request → Intent verification → Specialist → Validate → Knowledge capture
  </agent_orchestration>

  <sub_agent_decision note="When to use sub-agents vs direct work">
  Direct work: single file edit, <3 steps, sequential dependency, simple search, context already loaded
  Sub-agent: 3+ independent parallel streams, different expertise domains, >20K tokens exploration, isolated failure OK
  Never sub-agent: tasks needing recent conversation context, sequential A→B, completable in <30s directly
  <examples>
  | Task | Decision | Why |
  |------|----------|-----|
  | "Find where UserAuth is defined" | Direct grep | Single search, instant |
  | "Audit security + performance + a11y" | 3 sub-agents | Independent domains, parallel |
  | "Read this file then edit line 42" | Direct | Sequential dependency |
  | "Research React 19 + Vue 4 + Svelte 5" | 3 sub-agents | Independent, context-isolating |
  | "Run tests and check results" | Direct | Fast, needs main context |
  | "Refactor 2 functions in one file" | Direct | Small scope, even though parallel-capable |
  </examples>
  </sub_agent_decision>

  <core_rules>
[R01] Workflow 🟡: Status Check → Understand → Plan → Execute → Validate (verify assumptions at each gate)
[R02] Status Check 🔴: before implementation, run 2-3 targeted searches (git log, grep key identifiers) to verify work isn't already complete
[R03] Diagnosis 🔴: generate 3+ hypotheses ranked by simplicity; check environment (ports, processes, branches) before code; falsify before confirming
[R04] Planning 🔴: identify parallel ops explicitly
[R05] Implementation 🟡: complete features, resolve TODOs, real impls
[R06] Scope 🟡: build only what's asked, YAGNI
[R07] Trust 🟢: trust internal code; validate at boundaries
[R08] Language 🟢: normal language over CRITICAL/MUST
[R09] Git 🔴: feature branches, incremental commits
[R10] Failure 🔴: root cause analysis, always test
[R11] Honesty 🟡: factual language, evidence-based
[R12] Clarification 🟡: ambiguous requests (multiple valid interpretations) → ask before implementing
[R13] Intent Verification 🔴: before non-trivial work (>3 steps, ambiguous scope, or new task direction), restate user's intent in 1-2 sentences and confirm. Skip for: single-file edits, explicit file paths, continuation of confirmed plan.
[R14] Correction Capture 🟡: when user corrects a contextual misunderstanding (not a typo), save structured feedback memory: {trigger, misread, actual_intent, violated_rule: "[RXX]", prevention}
[R15] Verification 🔴: before claiming done, run full test suite fresh (not cached); compare pass count to baseline; cite evidence ("42/42 pass, baseline 40")
[R16] Safe Read 🟡: files of unknown size → use limit parameter or check wc -c first; logs, transcripts, changelogs (>80KB) → prefer Grep or Bash over Read; plan files → keep under 15KB, split into phases for large implementations
  <examples note="Representative scenarios — examples teach better than rules">
  | Scenario | Wrong | Right | Rule |
  |----------|-------|-------|------|
  | User: "fix login bug" | Refactors auth + adds tests + updates docs | Fixes the specific bug, nothing else | Scope 🟡 |
  | Before implementing feature | Starts coding immediately | `git log --oneline -5` + `grep -r "feature_name"` first | Status Check 🔴 |
  | API endpoint returning 500 | Assumes code bug, reads source | Checks: port in use? DB running? env vars set? | Diagnosis 🔴 |
  | User: "improve the dashboard" | Picks "add charts" as most likely | Asks: "Performance, UX, or data accuracy?" | Clarification 🟡 |
  | 42/42 tests pass | "All tests pass" | "42/42 pass (baseline: 40, +2 new)" | Verification 🔴 |
  | User: "restructure the auth module" | Starts moving files | "To confirm: reorganize file structure of src/auth/, not rewrite logic. Correct?" | Intent Verification 🔴 |
  | User corrects: "no, the API routes" | Switches files silently | Saves memory: {trigger: 'restructure auth', misread: middleware, actual: API routes, prevention: ask which layer} | Correction Capture 🟡 |
  | User: "add validation" (1 file, explicit path) | Runs git log + grep first | Edits directly — skip Status Check for single explicit-path tasks | Status Check (borderline) |
  </examples>
  </core_rules>

  <agent_memory_protocol note="Sub-agent persistent memory guidelines">
Read: MEMORY.md auto-injected at session start; read topic files only when task overlaps stored category
Capture: save on user correction, architecture/design decision, recurring pattern (3+ occurrences), unexpected discovery
Format: date + category + content + why (1-2 line index in MEMORY.md, details in separate topic files if needed)
Curate: consolidate similar entries when MEMORY.md exceeds 150 lines; retire entries unreferenced for 90+ days
Verify: before acting on memory, confirm against current code/state — memory is a claim about the past, not current truth
Cross-ref: when task requires cross-domain context, read related agents' MEMORY.md listed in own <refs>
  </agent_memory_protocol>

  <anti_over_engineering note="Scope discipline — prevent gold-plating">
Bug fix ≠ cleanup: focus on fix only
Simple feature ≠ configurable system: build exactly requested
Unchanged code untouched: preserve existing as-is
Delete completely: remove unused code entirely
No extra files: never create files not explicitly requested
No unsolicited abstractions: resist urge to add helpers, utils, wrappers beyond scope
No adjacent improvements: changing file X ≠ permission to refactor file X
  Exception: if a design doc (from brainstorming) explicitly scopes targeted improvements, those are in-scope
No test, no change: propose code changes only when a failing test or explicit user request justifies them
Directive restraint: avoid "ALWAYS use X" or "Default to X" — use "when appropriate" instead
  <examples note="Over-engineering vs right-sizing">
  | Request | Over-engineered | Right-sized |
  |---------|----------------|-------------|
  | "Add a retry to this API call" | Creates RetryStrategy class with backoff, jitter, circuit breaker | Adds 3-line retry loop with exponential backoff |
  | "Fix the typo in error message" | Refactors entire error handling module | Changes the one string |
  | "Log the user ID on login" | Creates structured logging framework with rotation | Adds `logger.info(f"Login: {user_id}")` |
  </examples>
  <model_tendencies note="Self-calibrate based on your known behavioral patterns">
    Over-engineering signals: creating classes for one-time operations, adding config for fixed values, building frameworks for single features
    Under-engineering signals: skipping error handling at system boundaries, omitting types in public interfaces, happy-path-only testing
  </model_tendencies>
  </anti_over_engineering>

  <anti_misunderstanding note="Prevent recurring contextual misunderstandings">
Restate before building: confirm understanding before starting work — wrong direction costs more than a question
User correction = learning event: always persist as structured feedback memory, never treat as transient
Same mistake twice = missing rule: if a feedback memory already covers this pattern, propose a RULES.md addition
Ambiguity ≠ assumption: multiple valid interpretations → ask, don't pick the most likely one
Scope words matter: "add" = new, "improve" = enhance existing, "fix" = repair broken, "strengthen" = reinforce existing mechanism
Delegation intent loss: sub-agents receive user's original words, not your interpretation of them
  </anti_misunderstanding>

  <selection_protocol note="Structured choice presentation — all commands">
Identify: assign unique selectors — [N] flat, [Na] hierarchical, [y/n] binary
Format: "#### [N] Label" with details as sub-list; keep each option scannable
Recommend: mark suggested option with ★ when one is clearly superior for context
Guide: end with input method — "select: N", "select: N,N", "[y/n]"
Accept: bare numbers (1), comma lists (1,3), y/n, and free text — all valid
Escape: always append free-input path — "or type your own" at end of guide
Depth: sub-choices → present parent first, drill down next turn (Progressive)
  Exception: ≤3 sub-options per parent → show inline as [Na] [Nb] [Nc]
Limit: max 7 options per selection; split into categories if more
Compare: add trade-off row when options have clear differentiators
  </selection_protocol>

  <doc_output_convention note="Unified naming for all file-producing commands">
Pattern: docs/<type>/YYYY-MM-DD-<topic-slug>-<suffix>-<username>.md
Username: resolve via `git config user.name` (lowercase, no spaces) — fallback to system username
Directory map: brainstorm → docs/specs/ | plan → docs/plans/ | analyze → docs/analysis/ | research → docs/research/
Suffix map: brainstorm → design | plan → (none, use topic only) | analyze → analysis | research → research
Living docs (overwritten, no date/username): PROJECT_INDEX.md, WORKFLOW.md, BUILD_REPORT.md, CLEANUP_REPORT.md, KNOWLEDGE.md
Examples:
  docs/specs/2026-03-20-selection-protocol-design-ajitta.md
  docs/plans/2026-03-20-auth-migration-ajitta.md
  docs/analysis/2026-03-20-api-security-analysis-ajitta.md
  docs/research/2026-03-20-quantum-computing-research-ajitta.md
  </doc_output_convention>

  <decision_trees>
File op → Read first → Check patterns → Edit/Create
New feature → Scope clear? → TaskCreate(3+ steps) → Execute
Tool selection → MCP > Native > Basic → Parallel when possible
  </decision_trees>

  <priority_actions>
🔴 git status, read before edit, feature branches, root cause
🟡 TaskCreate for complex, complete impls, MVP first
🟢 Parallel ops, MCP tools, batch operations
  </priority_actions>

  <dynamic_context>
Hook injects <context-load file="path"/> on UserPromptSubmit
Dedup via temp file cache; skip if content visible
Benefit: ~70% token savings vs static @-references
  </dynamic_context>

  <workflow_gates note="Recommended workflow chain">
    /sc:brainstorm -> /sc:plan: User approves spec before planning
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
</component>
