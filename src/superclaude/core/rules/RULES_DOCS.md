<component name="rules-docs" type="core-module">
  <role>
    <mission>Doc naming/location convention + workflow gates — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on doc-producing contexts (/sc:document, /sc:plan, /sc:design, plan/spec writing); Read explicitly before creating docs outside those triggers</loading>
  </role>

  <doc_output_convention note="Unified naming for all file-producing commands.">

Default (multi-doc work): docs/features/<feature-slug>/
  Required: README.md (frontmatter + index) + numbered phase files
  Phase prefixes: 01-discovery (brainstorm) | 02-research | 03-analysis | 04-design | 05-plan (plan, roadmap) | 06+-<custom> (impl notes, retrospective)
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
    /sc:design -> /sc:roadmap: Alternative path when input is a PRD/feature doc rather than a design spec
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:roadmap -> /sc:implement: Roadmap tasks defined; implementation proceeds per task list
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
</component>
