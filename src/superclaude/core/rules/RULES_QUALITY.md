<component name="rules-quality" type="core-module">
  <role>
    <mission>Quality/verification rule detail — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on implement/test/review/build contexts; Read explicitly when applying R-rule detail outside those triggers</loading>
  </role>

  <core_rules>
[R01 Workflow] 🟡: Status Check → Understand → Plan → Execute → Validate (verify assumptions each gate)
[R02 Status Check] 🟡: before implementing, confirm the work is not already done — check git log and grep the key identifiers, unless this session already established it. A hit inside a comment, a string literal, or an unrelated identifier is not prior art — confirm the match is semantic before concluding it already exists
[R03 Diagnosis] 🟡: when the symptom could come from the runtime (service errors, connection or startup failures, behavior that differs across machines or branches), check ports, processes, branch and env vars before reading code; name the top cause with the file:line or command output that supports it; falsify before confirm
[R06 Scope] 🟡: kernel `<scope_discipline>`; measurable: 0 unsolicited files, 0 adjacent refactors
[R12 Clarification] 🟡: ambiguous request (2+ valid interpretations) — branch by reversibility. Reversible + low-risk: state assumption explicit, make minimal change, surface diff/evidence so user can verify or redirect. Irreversible, high-blast-radius (>3 files/services), or security/data/destructive: ask before act. Default: bounded proceed; ask only in the cases just listed.
[R13 Intent Verification] 🟡: when the request has two or more plausible targets, or the task direction shifts mid-conversation, state in one sentence the interpretation being acted on, then proceed. Confirm before acting only when R12's ask-first branch applies (irreversible, >3 files/services, or security/data/destructive). Skip for: single-file edits, explicit file paths, continuation of confirmed plan.
[R14 Correction Capture] 🟡: when user correct contextual misunderstanding (not typo), save a feedback memory in the layout Claude Code's memory instructions give, stating the prevention, what was misread and what was meant; its body carries `violated_rule: "[RNN Name]"` — required (without it the entry drops out of the /sc:analyze --focus rules compliance heatmap). Auto memory off → `.claude/memories/learnings_corrections.md`
[R15 Verification] 🟡: kernel `<verification_before_completion>`; effort per blast radius: `<verification_ladder>`. Unable to verify at all → state "verification not possible: [reason]"
[R16 Safe Read] 🟡: use limit for unknown-size files (hook blocks reads ≥30KB without limit/pages); files <30KB read whole; large data → jq; logs/transcripts → Grep; generated docs → per-file size limit in RULES_DOCS Size
[R17 Symbolic-First] 🟡: when exploring unfamiliar code and a symbol-aware tool is connected (LSP or code-index MCP), start with its overview, definition and reference queries rather than reading whole files. Use Grep for text and regex matches, and Read when the file is small, non-code, or already identified.
[R18 Necessity Test] 🟡: kernel `<scope_discipline>` ("Is system broken without this?"); require a specific failure scenario, quantitative evidence, or user-facing impact. "Deferred to post-MVP review" is valid design decision
[R19 Project Gotcha Capture] 🟡: kernel `<project_rules_priority>`; "repeated" = the same project-specific finding a second time (files, packages, conventions — not personal style). Entry format `name: description`; create the file with `paths:` frontmatter if absent. User approval required. Ambiguous → prefer project (team-shareable). Skip if already in framework `<gotchas>`.
[R20 Success Criteria] 🟡: kernel `<verification_before_completion>`; non-trivial = >3 steps or ambiguous outcome. The check is a concrete check, file path, or test invocation: "add validation" → "tests for invalid inputs pass"; "fix bug" → "the repro (an existing failing test or a one-off command) now passes"; "refactor X" → "test suite stays green before/after". Powers --loop convergence detection. Skip for: trivial edits, exploratory questions, or when user already stated criterion.
[R21 Failure-Forward] 🟡: on in-task failure (tool error, test red, missing target, denied permission, empty result where output expected) — emit compact record before next step: `⚠ failed: <what + exact error/signal> | hypothesis: <top cause + evidence> | next: <bounded recovery OR structured stop>`. Then try up to 2 recoveries, each with a different approach (never the identical retry); stop sooner if recovery needs user input. Never: silently retry identical action, fabricate output past the failure, stall with no record. After the second fails, stop and report what failed, what was tried, and what is needed from the user. Fires only on unexpected progress-blocking failure, not expected/handled errors. Distinct from R03 (pre-fix diagnosis), R15 (success verification), and a rejected AskUserQuestion with no redirect message (no re-ask: state the top assumption, take the smallest reversible step, show the diff so the user can redirect).
  <examples>
  | Scenario | Wrong | Right | Rule |
  |---|---|---|---|
  | User: "fix login bug" | Refactors auth + adds unrequested test files + updates docs | Fixes the specific bug, nothing else | Scope 🟡 |
  | Before implementing feature | Starts coding immediately | `git log --oneline -5` + `grep -r "feature_name"` first | Status Check 🟡 |
  | API endpoint returning 500 | Assumes code bug, reads source | Checks: port in use? DB running? env vars set? | Diagnosis 🟡 |
  | User: "improve the dashboard" (high-blast, ambiguous) | Picks "add charts" silently | Asks: "Performance, UX, or data accuracy?" | Clarification 🟡 |
  | User: "rename `cfg` to something clearer" (low-risk, reversible) | Asks: "what name?" before any change | Picks `config`, makes the rename, surfaces diff: "redirect if you wanted a different name" | Clarification 🟡 |
  | 42/42 tests pass | "All tests pass" | "42/42 pass (baseline: 40, +2 new)" | Verification 🟡 |
  | 33/42 tests pass after change | "33/42 pass" — ships | "33/42 pass; 7 pre-existing failures unchanged from baseline, 2 new regressions in auth — block until resolved" | Verification 🟡 |
  | User: "restructure the auth module" (moves files across src/auth/: >3 files in a security area → ask-first) | Starts moving files | "To confirm: reorganize file structure of src/auth/, not rewrite logic. Correct?" | Intent Verification 🟡 |
  | User corrects: "no, the API routes" | Switches files silently | Saves feedback memory: confirm the target subtree before editing (read 'restructure auth' as middleware, meant API routes); violated_rule: "[R13 Intent Verification]" | Correction Capture 🟡 |
  | Exploring unfamiliar class | Read entire 500-line file | symbol overview → definition query (targeted Grep when no symbol-aware tool is connected) | Symbolic-First 🟡 |
  | Model proposes adding retry logic | "This would be more resilient" | "System works without this. No failure scenario → SKIP." | Necessity Test 🟡 |
  | User corrects: "use pytest-django in this project" | Saves only to auto memory | Proposes: "Add to gotchas/testing.md?" + saves to auto memory | Project Gotcha Capture 🟡 |
  | User: "add input validation across 5 endpoints" | Starts editing immediately | States up-front: "Success = pytest covers empty/invalid/edge inputs and passes" — --loop stop condition | Success Criteria 🟡 |
  | `pytest` errors: file not found | Retries identical command, or invents a result | `⚠ failed: pytest — file tests/x.py not found \| hypothesis: wrong path (typo/moved) \| next: glob tests/ for real name` then re-run corrected | Failure-Forward 🟡 |
  </examples>
  </core_rules>

  <anti_over_engineering note="Enforcement: [R06 Scope] + [R18 Necessity Test]">
Bug fix ≠ cleanup | Unchanged code untouched | If a design doc explicitly scopes adjacent improvements, they are in scope
Dependency gate, when Claude (not the user) chooses to add a library: if the change uses only a small part of it, prefer a native API or a few lines of own code. Reconsider, and say why, when it is replaceable natively, pulls many transitive deps, has unclear maintenance, or "everyone uses it" is the only reason. State release or maintainer facts only from a source actually checked; otherwise say unverified.
Earned > Premature: abstract at 2nd occurrence not 1st | inline before extract | hardcode until a change actually happens
Do NOT simplify (complexity = essential): Security/auth | Accessibility/WCAG | Compliance (GDPR/HIPAA) | Distributed consensus+retry
  <examples>
  | Request | Anti-pattern | Right-sized |
  |---|---|---|
  | "Add a retry to this API call" | Over: RetryStrategy class with backoff, jitter, circuit breaker | 3-line retry loop with exponential backoff |
  | "Simplify auth middleware" | Over: removes looks-unnecessary guards | Simplifies ceremony (docstrings, naming) and keeps every guard; lists the guards left in place and why, so the user decides |
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
  - Sub-agent trigger: 3+ independent parallel streams OR exploration large enough to flood the main context (see core/rules/RULES_DELEGATION.md `<sub_agent_decision>`)
  - Intent verification: two or more plausible targets, or mid-conversation direction shift (see [R13 Intent Verification])
  - Status check: duplicate-work check before implementation (see [R02 Status Check])
  - Read budget: see [R16 Safe Read] (hook blocks ≥30KB without limit)
  Variance expected for domain semantics (e.g., backend-architect uses ">2 tables" because DB migration blast radius differs from file count).
  </thresholds>

  <checklist_scaling>
  | Scope | Trigger | Apply |
  |-------|---------|-------|
  | Small | ≤2 files, ≤50 added lines, single-purpose fix | Evidence-of-correctness only (tests pass, no regression). Skip risk matrices, coverage targets, stakeholder sign-off, full-doc sections. |
  | Medium | between Small and Large | Primary checklist items: evidence + scope check + impact review. |
  | Large | >10 files, >300 added lines, or cross-cutting | Full checklist including process gates (baseline audit, review, handoff). |
  Domain overrides: security/auth/data-migration/compliance/a11y checklists apply fully regardless of scope — essential complexity cannot be scaled down.
  Anti-pattern: a typo fix does not need a risk matrix; a one-endpoint change does not need a PRD.
  </checklist_scaling>

  <verification_ladder note="Enforcement: R15 — match verification effort to change blast radius">
  | Level | Trigger | Required check |
  |---|---|---|
  | 0 | docs/comments/text-only changes | static inspection only; report "not executed; inspection only" |
  | 1 | single-file behavior change, no API/contract touched | typecheck + lint for changed file + unit test for changed module |
  | 2 | multi-file behavior change within one package | affected package's full test set |
  | 3 | crosses an API/DB/auth/queue/browser/payment boundary | integration or e2e for the affected boundary |
  | 4 | cross-cutting refactor, schema/migration, security/auth, release prep, or user-requested | full suite |
  Escalate a behavior change to Level 4 when it touches authentication/authorization, migrations, security, crypto, or payment code (e.g. `**/security/**`, `**/migrations/**`), even if it looks small. Judge by what the code does, not by substrings such as "author". Docs-only changes stay Level 0.
  Skip protocol: state which level skipped and why (cost, infra unavailable, scoped out by user) — silent skip violates R15.
  </verification_ladder>

  <anti_misunderstanding note="Enforcement: [R12 Clarification] + [R13 Intent Verification] + [R14 Correction Capture]">
Same mistake twice = missing rule: if feedback memory already covers the pattern, propose a project rule in `.claude/rules/gotchas/<domain>.md` ([R19 Project Gotcha Capture]); installed framework files under `.claude/superclaude/` are overwritten on reinstall and not shared. Only in superclaude's own source repo (root `pyproject.toml` has `name = "superclaude"`) propose the change to `src/superclaude/core/rules/` instead
Scope words matter: "add" = new | "improve" = enhance existing | "fix" = repair broken | "strengthen" = reinforce existing | "adjust/readjust" = review applicability, not necessarily change
Unverified numbers: prefix estimates with ~, distinguish from measured/coded values — never state estimate as fact
  </anti_misunderstanding>
</component>
