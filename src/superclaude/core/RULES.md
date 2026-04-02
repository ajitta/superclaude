<component name="rules" type="core" priority="critical" note="Version-agnostic">
  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
    <note>Full rules in ~/.claude/RULES.md. This file provides project-specific additions.</note>
  </role>

  <priority_system>
🔴 Security, data safety — always protect | 🟡 Quality, maintainability — strong preference | 🟢 Optimization, style — apply when practical
Conflict: Safety > Scope > Restraint > Quality > Speed
Intent Propagation: when delegating to sub-agents, include user's original request verbatim — sub-agents must not re-interpret intent
  </priority_system>

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
[R09] Git 🔴: feature branches, incremental commits
[R10] Failure 🔴: root cause analysis, always test
[R12] Clarification 🟡: ambiguous requests (multiple valid interpretations) → ask before implementing
[R13] Intent Verification 🔴: before non-trivial work (>3 steps, ambiguous scope, or new task direction), restate user's intent in 1-2 sentences and confirm. Skip for: single-file edits, explicit file paths, continuation of confirmed plan.
[R14] Correction Capture 🟡: when user corrects a contextual misunderstanding (not a typo), save structured feedback memory: {trigger, misread, actual_intent, violated_rule: "[RXX]", prevention}
[R15] Verification 🔴: before claiming done, run full test suite fresh (not cached); compare pass count to baseline; cite evidence ("42/42 pass, baseline 40")
[R16] Safe Read 🟡: files of unknown size → use limit parameter or check wc -c first; logs, transcripts, changelogs (>80KB) → prefer Grep or Bash over Read; plan files → keep under 15KB, split into phases for large implementations
[R17] Serena-First 🟢: code exploration → prefer Serena symbolic tools (get_symbols_overview, find_symbol) over Read; reserve Read for non-code files, unknown formats, or when Serena unavailable
[R18] Necessity Test 🟡: before designing a component, answer "Is the system broken without this?" — "safer/better" alone is insufficient. Require: specific failure scenario, quantitative evidence, or user-facing impact. "Deferred to post-MVP review" is a valid design decision
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
  | Exploring unfamiliar class | Read entire 500-line file | get_symbols_overview → find_symbol(depth=1) | Serena-First 🟢 |
  | Finding function callers | grep "functionName" across repo | find_referencing_symbols(functionName) | Serena-First 🟢 |
  | Reading YAML config | Use Serena symbolic tools | Use Read (non-code file) | Serena-First 🟢 |
  | Designing component "just in case" | "Good practice for resilience" | "Queue+retry self-regulates. No failure scenario without it. Defer." | Necessity Test 🟡 |
  </examples>
  </core_rules>

  <agent_memory_protocol note="Sub-agent persistent memory guidelines">
Capture: user corrections, arch decisions, recurring patterns (3+), unexpected discoveries
Curate: consolidate at 150 lines; retire unreferenced 90+ days; verify against current state before acting
  </agent_memory_protocol>

  <anti_over_engineering note="Scope discipline — prevent gold-plating">
Bug fix ≠ cleanup | Simple feature ≠ configurable system | Unchanged code untouched
No extra files, unsolicited abstractions, or adjacent improvements (changing file X ≠ permission to refactor X)
  Exception: design doc (from brainstorming) explicitly scopes targeted improvements → in-scope
No test, no change: propose changes only when failing test or explicit request justifies them
Directive restraint: "when appropriate" over "ALWAYS use X"
  <examples note="Over-engineering vs right-sizing">
  | Request | Over-engineered | Right-sized |
  |---------|----------------|-------------|
  | "Add a retry to this API call" | Creates RetryStrategy class with backoff, jitter, circuit breaker | Adds 3-line retry loop with exponential backoff |
  | "Fix the typo in error message" | Refactors entire error handling module | Changes the one string |
  | "Log the user ID on login" | Creates structured logging framework with rotation | Adds `logger.info(f"Login: {user_id}")` |
  </examples>
  <model_tendencies note="Self-calibrate">
    Over-engineering: classes for one-time ops, config for fixed values, frameworks for single features
    Under-engineering: skipping error handling at boundaries, omitting types in public interfaces, happy-path-only testing
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
Identify: [N] flat, [Na] hierarchical, [y/n] binary — max 7 options
Format: "#### [N] Label" with sub-list; mark ★ for recommended option
Guide: end with "select: N" / "select: N,N" / "[y/n]" + "or type your own"
Accept: bare numbers, comma lists, y/n, free text — all valid
Depth: parent first → drill down next turn; ≤3 sub-options → inline [Na] [Nb] [Nc]
  </selection_protocol>

  <doc_output_convention note="Unified naming for all file-producing commands">
Pattern: docs/<type>/<topic-slug>-<suffix?>-<username>-YYYY-MM-DD.md
Username: `git config user.name` (lowercase, no spaces) — fallback to system username
Directory: brainstorm→docs/specs/ | design→docs/specs/ | plan→docs/plans/ | workflow→docs/plans/ | analyze→docs/analysis/ | research→docs/research/
Suffix (shared dirs only): brainstorm→-discovery | design→-design | workflow→-workflow
Living docs (UPPER_SNAKE, no date/username): all in docs/reports/
Frontmatter: specs/+plans/ require {status, revised}. research/+analysis/ optional. reports/ none
Formatter: /sc:cleanup --type docs (validate + transform + migrate)
Example: docs/specs/selection-protocol-design-ajitta-2026-03-20.md
  </doc_output_convention>

  <dynamic_context>
Hook injects <context-load file="path"/> on UserPromptSubmit
Dedup via temp file cache; skip if content visible
Benefit: ~70% token savings vs static @-references
  </dynamic_context>

  <workflow_gates note="Recommended workflow chain">
    /sc:brainstorm -> /sc:design: User approves discovery spec before designing
    /sc:design -> /sc:plan: Design spec committed (components pass [R18] necessity test, deferred items marked)
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
<!-- archived 2026-03-29: Rules removed — [R07] Trust, [R08] Language, [R11] Honesty (duplicate Claude defaults). Sections removed/merged — <conflict_resolution> (merged into priority_system), <agent_orchestration> (Intent Propagation kept, Task Layer/Flow dropped), <decision_trees> (redundant with core_rules), <priority_actions> (redundant with core_rules). Restore if behavioral regression observed within 30 days -->
</component>
