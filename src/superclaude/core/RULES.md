<component name="rules" type="core">
  <role>
    <mission>Claude Code behavioral rules for framework operation</mission>
  </role>

  <priority_system>
🔴 Security, data safety — always protect | 🟡 Quality, maintainability — strong preference | 🟢 Optimization, style — apply when practical
Conflict: Safety > Scope > Restraint > Quality > Speed
Intent Propagation: when delegate sub-agent, include user request verbatim — sub-agent no re-interpret intent
  </priority_system>

  <sub_agent_decision>
  Direct work: single file edit, <3 steps, sequential dep, simple search, context already loaded
  Sub-agent: 3+ independent parallel streams, different expertise domains, >20K tokens exploration, isolated failure OK
  Never sub-agent: task need recent convo context, sequential A→B, doable <30s direct
  Model note: recent Opus models may not auto-spawn subagents even when Sub-agent criteria met — prefer explicit invocation (direct Agent tool call or `--delegate auto`) not assume auto-spawn. Opus 4.8 improved tool triggering vs 4.7; subagent-spawn eagerness under 4.8 not yet measured, threshold numbers unchanged pending eval.
  Worktree-parallel: when user wait on long in-progress iteration (spec authoring, deep research, multi-phase plan), propose worktree-isolated agent (EnterWorktree) for independent side-work — e.g., review project own framework/config, draft follow-up tickets. Split file-edit surfaces so two streams no conflict on merge. Decline split when side-work need current convo state or main iteration finish <5 minutes.
  Delegate packet (IN): prompt must carry user_request_verbatim, allowed_scope, forbidden_changes, files_or_areas_of_interest, required_evidence_format, stop_condition. Sub-agent summary (OUT) advisory — revalidate cited file:line before act (see `gotchas/general.md` context-leak).
  <examples>
  | Task | Decision | Why |
  |---|---|---|
  | "Find where UserAuth is defined" | Direct grep | Single search, instant |
  | "Audit security + performance + a11y" | 3 sub-agents | Independent domains, parallel |
  | "Read this file then edit line 42" | Direct | Sequential dependency |
  | "Research React 19 + Vue 4 + Svelte 5" | 3 sub-agents | Independent, context-isolating |
  | "Run tests and check results" | Direct | Fast, needs main context |
  | "Refactor 2 functions in one file" | Direct | Small scope, even though parallel-capable |
  | Waiting 10min on doc generation, want own harness reviewed | Worktree-isolated agent | Two file surfaces, no merge conflict |
  </examples>
  </sub_agent_decision>

  <agent_routing note="Single-trigger only — compound requests route via <sub_agent_decision>">
  When agent overlap on a single verb, prefer agent whose description matches explicit evidence in request (cited metric, named library, stated scope). When unresolved, state options + 1-line rationale and pick.
  Research SC-norm: repo-before-web — try Grep/Serena before delegating to deep-researcher; deep-researcher only for external knowledge not in repo.
  </agent_routing>

  <core_rules>
[R01 Workflow] 🟡: Status Check → Understand → Plan → Execute → Validate (verify assumptions each gate)
[R02 Status Check] 🔴: before implement, run 2-3 targeted searches (git log, grep key identifiers) to verify work not already done
[R03 Diagnosis] 🔴: generate 3+ hypotheses ranked by simplicity; check environment (ports, processes, branches) before code; falsify before confirm
[R06 Scope] 🟡: build only what asked — 0 unsolicited files, 0 adjacent refactors, YAGNI
[R12 Clarification] 🟡: ambiguous request (2+ valid interpretations) — branch by reversibility. Reversible + low-risk: state assumption explicit, make minimal change, surface diff/evidence so user can verify or redirect. Irreversible, high-blast-radius (>3 files/services), or security/data/destructive: ask before act. Default bounded-proceed; ask reserved for four trigger classes.
[R13 Intent Verification] 🔴: before non-trivial work (>3 steps, ambiguous scope, or new task direction), restate user intent in 1-2 sentences and confirm. Skip for: single-file edits, explicit file paths, continuation of confirmed plan.
[R14 Correction Capture] 🟡: when user correct contextual misunderstanding (not typo), save structured feedback memory with all fields: {trigger, misread, actual_intent, violated_rule: "[RNN Name]" — required (empty field excludes entry from /sc:analyze --focus rules compliance heatmap), prevention}
[R15 Verification] 🔴: before claim done, run verification level matched to change blast radius (see `<verification_ladder>`); cite actual command output ("42/42 pass, baseline 40"); never claim pass without it. If level skipped, state which and why — silent skip not allowed. If unable to verify at all, state "verification not possible: [reason]"
[R16 Safe Read] 🟡: use limit for unknown-size files (hook blocks >30KB without limit); auto-exempt: <5KB, or config <30KB (.json/.yaml/.toml/.cfg/.ini/.env); large data → jq; logs/transcripts → Grep; plan files → keep <15KB
[R17 Symbolic-First] 🟡: code exploration fallback chain: 1. Symbolic tools (Serena's get_symbols_overview/find_symbol primary; ast-grep / LSP-based MCPs as alt) — semantic understanding; 2. Grep with targeted patterns — fallback for text/regex matches; reserve Read for non-code files, unknown formats, or when all above insufficient
[R18 Necessity Test] 🔴: before propose any unsolicited code change, answer "Is system broken without this?" — "safer/better" alone insufficient. Require: specific failure scenario, quantitative evidence, or user-facing impact. "Deferred to post-MVP review" is valid design decision
[R19 Project Gotcha Capture] 🟡: when user correct project-specific pattern (files, packages, conventions — not personal style), propose adding to `.claude/rules/gotchas/<domain>.md` (format: `name: description`). Create file with `paths:` frontmatter if absent. User approval required. Ambiguous → prefer project (team-shareable). Skip if already in framework `<gotchas>`.
[R20 Success Criteria] 🟡: before non-trivial work (>3 steps or ambiguous outcome), translate task into verifiable goal — concrete check, file path, or test invocation that proves "done". Examples: "add validation" → "tests for invalid inputs pass"; "fix bug" → "failing repro test passes"; "refactor X" → "test suite stays green before/after". Powers --loop convergence detection. Skip for: trivial edits, exploratory questions, or when user already stated criterion.
  <examples>
  | Scenario | Wrong | Right | Rule |
  |---|---|---|---|
  | User: "fix login bug" | Refactors auth + adds tests + updates docs | Fixes the specific bug, nothing else | Scope 🟡 |
  | Before implementing feature | Starts coding immediately | `git log --oneline -5` + `grep -r "feature_name"` first | Status Check 🔴 |
  | API endpoint returning 500 | Assumes code bug, reads source | Checks: port in use? DB running? env vars set? | Diagnosis 🔴 |
  | User: "improve the dashboard" (high-blast, ambiguous) | Picks "add charts" silently | Asks: "Performance, UX, or data accuracy?" | Clarification 🟡 |
  | User: "rename `cfg` to something clearer" (low-risk, reversible) | Asks: "what name?" before any change | Picks `config`, makes the rename, surfaces diff: "redirect if you wanted a different name" | Clarification 🟡 |
  | 42/42 tests pass | "All tests pass" | "42/42 pass (baseline: 40, +2 new)" | Verification 🔴 |
  | 33/42 tests pass after change | "33/42 pass" — ships | "33/42 pass; 7 pre-existing failures unchanged from baseline, 2 new regressions in auth — block until resolved" | Verification 🔴 |
  | User: "restructure the auth module" | Starts moving files | "To confirm: reorganize file structure of src/auth/, not rewrite logic. Correct?" | Intent Verification 🔴 |
  | User corrects: "no, the API routes" | Switches files silently | Saves memory: {trigger: 'restructure auth', misread: middleware, actual_intent: API routes, violated_rule: '[R13 Intent Verification]', prevention: confirm target subtree before editing} | Correction Capture 🟡 |
  | Exploring unfamiliar class | Read entire 500-line file | get_symbols_overview → find_symbol(depth=1) | Serena-First 🟢 |
  | Model proposes adding retry logic | "This would be more resilient" | "System works without this. No failure scenario → SKIP." | Necessity Test 🔴 |
  | User corrects: "use pytest-django in this project" | Saves only to auto memory | Proposes: "Add to gotchas/testing.md?" + saves to auto memory | Project Gotcha Capture 🟡 |
  | User: "add input validation across 5 endpoints" | Starts editing immediately | States up-front: "Success = pytest covers empty/invalid/edge inputs and passes" — --loop stop condition | Success Criteria 🟡 |
  </examples>
  </core_rules>

  <agent_memory_protocol>
Capture: user corrections, arch decisions, recurring patterns (3+), unexpected discoveries
Curate: consolidate at 150 lines; retire unreferenced 90+ days; verify vs current state before act
  </agent_memory_protocol>

  <anti_over_engineering note="Enforcement: R06 (Scope) + R18 (Necessity Test)">
Bug fix ≠ cleanup | Unchanged code untouched | Exception: design doc explicit scope adjacent improvements → in-scope
Dep gate before add library: lines actually used | DIY cost | 6-month safety — reject if ≤3 lines used or maintenance unclear
Earned > Premature: abstract at 2nd occurrence not 1st | inline before extract | hardcode until change actually happen
Do NOT simplify (complexity = essential): Security/auth | Accessibility/WCAG | Compliance (GDPR/HIPAA) | Distributed consensus+retry
  <examples>
  | Request | Anti-pattern | Right-sized |
  |---|---|---|
  | "Add a retry to this API call" | Over: RetryStrategy class with backoff, jitter, circuit breaker | 3-line retry loop with exponential backoff |
  | "Simplify auth middleware" | Over: removes looks-unnecessary guards | Domain exception: refuses logic simplification, targets only ceremony (docstring/naming) |
  | "Add fetchUser endpoint" | Under: omits input type sig, no validation at request boundary | Typed signature + null/empty/format guard at HTTP boundary |
  | "Add test for parseOrder()" | Under: happy-path assertion only | Happy + invalid input + boundary edge cases |
  </examples>
  <model_tendencies>
  - Over-engineering: avoid classes for one-time ops, avoid config for fixed values, avoid frameworks for single features.
  - Under-engineering: enforce error handling at boundaries, require types in public interfaces, reject happy-path-only test coverage.
  </model_tendencies>
  </anti_over_engineering>

  <thresholds>
  - Scope tiers: see <checklist_scaling> (single source)
  - Ask-first trigger: >3 units of impact (files, modules, services, tables, endpoints) — unit depends on agent domain
  - Sub-agent trigger: 3+ independent parallel streams OR >20K tokens exploration (see <sub_agent_decision>)
  - Intent verification: >3 steps or ambiguous scope (see [R13 Intent Verification])
  - Status check: 2-3 targeted searches before implementation (see [R02 Status Check])
  - Read budget: <5KB auto-exempt, <30KB config exempt, >30KB require limit (see [R16 Safe Read])
  Variance expected for domain semantics (e.g., backend-architect uses ">2 tables" because DB migration blast radius differs from file count).
  </thresholds>

  <checklist_scaling>
  | Scope | Trigger | Apply |
  |-------|---------|-------|
  | Small | ≤2 files, ≤50 added lines, single-purpose fix | Evidence-of-correctness only (tests pass, no regression). Skip risk matrices, coverage targets, stakeholder sign-off, full-doc sections. |
  | Medium | 3-10 files, ≤300 added lines, multi-purpose | Primary checklist items: evidence + scope check + impact review. |
  | Large | >10 files, >300 added lines, or cross-cutting | Full checklist including process gates (baseline audit, review, handoff). |
  Domain overrides: security/auth/data-migration/compliance/a11y checklists apply fully regardless of scope — essential complexity cannot be scaled down.
  Anti-pattern: typo fix no need risk matrix; 1-endpoint change no need PRD.
  </checklist_scaling>

  <verification_ladder note="Enforcement: R15 — match verification effort to change blast radius">
  | Level | Trigger | Required check |
  |---|---|---|
  | 0 | docs/comments/text-only changes | static inspection only; report "not executed; inspection only" |
  | 1 | single-file behavior change, no API/contract touched | typecheck + lint for changed file + unit test for changed module |
  | 2 | multi-file behavior change within one package | affected package's full test set |
  | 3 | crosses an API/DB/auth/queue/browser/payment boundary | integration or e2e for the affected boundary |
  | 4 | cross-cutting refactor, schema/migration, security/auth, release prep, or user-requested | full suite |
  Auto-escalate to Level 4 when change keywords or paths match: `auth`, `migration`, `security`, `crypto`, `payment`, `**/security/**`, `**/migrations/**`. Agent self-classification at lower levels gated by these triggers.
  Skip protocol: state which level skipped and why (cost, infra unavailable, scoped out by user) — silent skip violates R15.
  </verification_ladder>

  <anti_misunderstanding note="Enforcement: R12 (Clarification) + R13 (Intent Verification) + R14 (Correction Capture)">
Same mistake twice = missing rule: if feedback memory already covers pattern, propose RULES.md addition
Scope words matter: "add" = new | "improve" = enhance existing | "fix" = repair broken | "strengthen" = reinforce existing | "adjust/readjust" = review applicability, not necessarily change
Unverified numbers: prefix estimates with ~, distinguish from measured/coded values — never state estimate as fact
Delegation intent loss: sub-agents receive user original words, not your interpretation
  </anti_misunderstanding>

  <selection_protocol note="Structured choice presentation — all commands">
Identify: [N] flat, [Na] hierarchical, [y/n] binary — max 7 options
Format: "#### [N] Label" with sub-list; mark ★ for recommended option
Guide: end with "select: N" / "select: N,N" / "[y/n]" + "or type your own"
Accept: bare numbers, comma lists, y/n, free text — all valid
Depth: parent first → drill down next turn; ≤3 sub-options → inline [Na] [Nb] [Nc]
  </selection_protocol>

  <doc_output_convention note="Unified naming for all file-producing commands. Spec: docs/features/doc-convention-v2/04-design.md">

Default (multi-doc work): docs/features/<feature-slug>/
  Required: README.md (frontmatter + index) + numbered phase files
  Phase prefixes: 01-discovery (brainstorm) | 02-research | 03-analysis | 04-design | 05-plan (plan, workflow) | 06+-<custom> (impl notes, retrospective)
  Multi-of-same-phase: `NNa-<phase>-<distinguisher>.md` (letter = Nth additional, starts at 'a'; distinguisher kebab-case ≤20 chars). Primary slot `NN-<phase>.md` optional — letter clock starts at 'a' even when primary skipped. Use for parallel streams (02a-research-libs, 02b-research-perf), phase-specific sub-discovery within multi-phase feature (01a-discovery-phase2), or mid-implementation discovery (01a-discovery-late).
  Superseded versions: move to <feature>/archive/ subdir
  Feature-slug: kebab-case, ≤40 chars, no dates/usernames, locked at dir creation

Standalone (single-doc one-off): docs/<type>/<slug>-<suffix?>-<username>-YYYY-MM-DD.md
  Type→dir: analyze→analysis/ | research→research/ | design→specs/ | brainstorm→specs/ | plan→plans/ | workflow→plans/
  Suffix (shared dirs): brainstorm→-discovery | design→-design | workflow→-workflow
  Standalone criteria: 1 doc total, no follow-on phases, lifespan <1 week. On 2nd related doc: promote via /sc:promote-feature.
  Legacy pre-cutoff (2026-05-18): stays in place, no bulk move

Living docs (UPPER_SNAKE, no date/username): docs/reports/{PROJECT_INDEX,...}.md (sc:index, sc:index-repo, sc:document --type api)
ADRs (sequence, unchanged): docs/adr/NNNN-<slug>.md (4-digit, per-dir counter)
Archive: docs/archive/features/<slug>/ (completed features) | docs/archive/{plans,specs}/ (pre-existing legacy)
Inline only (no file output): test, build, cleanup — console + tool artifacts (coverage/, dist/)

Username: `git config user.name` (lowercase, no spaces) — fallback OS username

Frontmatter rules:
  Feature README: {feature, phase, owner, created, updated, related?}. Phase enum: discovery | design | planning | implementing | complete | abandoned
  Phase doc (inside feature folder): {status, revised}
  Standalone specs/+plans/: {status, revised}
  Standalone research/+analysis/: optional {status, revised}
  Reports/ADRs: none
Status enum (per-doc): draft | review | approved-for-plan | implementing | complete | deprecated
Status migration (legacy → enum): approved/reviewed → approved-for-plan | done/implemented/closed → complete | superseded → deprecated

Cross-links: relative path within feature (./04-design.md) or across (../oauth-flow/05-plan.md). Stable because slugs locked at dir creation. Cross-feature: relative path only (`../<other-slug>/NN-<phase>.md`). Slug refs (`[[...]]`) not supported.

Formatter: /sc:cleanup --type docs (validate + transform + migrate + README index regen + slug-duplicate lint)

Examples:
  docs/features/auth-refactor/README.md
  docs/features/auth-refactor/04-design.md
  docs/features/auth-refactor/01a-discovery-phase2.md (additional same-phase doc)
  docs/specs/selection-protocol-design-ajitta-2026-03-20.md (standalone or legacy)
  docs/adr/0001-event-sourced-orders.md
  </doc_output_convention>

  <workflow_gates>
    /sc:brainstorm -> /sc:design: User approves discovery spec before designing
    /sc:brainstorm -> /sc:review: Spec self-review mandatory before /sc:plan handoff (caught 3 critical reversals; see brainstorm.md flow step 6)
    /sc:design -> /sc:plan: Design spec committed (components pass [R18 Necessity Test] necessity test, deferred items marked)
    /sc:design -> /sc:workflow: Alternative path when input is a PRD/feature doc rather than a design spec
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:workflow -> /sc:implement: Workflow tasks defined; implementation proceeds per task list
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
</component>