<component name="rules-quality" type="core-module">
  <role>
    <mission>Quality/verification rule detail — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on implement/test/review/build contexts; Read explicitly when applying R-rule detail outside those triggers</loading>
  </role>

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
[R21 Failure-Forward] 🟡: on in-task failure (tool error, test red, missing target, denied permission, empty result where output expected) — emit compact record before next step: `⚠ failed: <what + exact error/signal> | hypothesis: <top cause + evidence> | next: <bounded recovery OR structured stop>`. Then take ONE bounded recovery probe (different approach, not identical retry) OR surface a structured stop if recovery needs user input. Never: silently retry identical action, fabricate output past the failure, stall with no record. Cap: 2 recovery attempts on same failure → escalate to structured stop. Fires only on unexpected progress-blocking failure, not expected/handled errors. Distinct from R03 (pre-fix diagnosis), R15 (success verification), askuserquestion-rejection-fallback (AskUserQuestion-only).
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
  | `pytest` errors: file not found | Retries identical command, or invents a result | `⚠ failed: pytest — file tests/x.py not found \| hypothesis: wrong path (typo/moved) \| next: glob tests/ for real name` then re-run corrected | Failure-Forward 🟡 |
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
  - Sub-agent trigger: 3+ independent parallel streams OR >20K tokens exploration (see core/rules/RULES_DELEGATION.md `<sub_agent_decision>`)
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
</component>
