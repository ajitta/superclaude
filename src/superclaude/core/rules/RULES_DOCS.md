<component name="rules-docs" type="core-module">
  <role>
    <mission>Doc naming/location convention + workflow gates — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on doc-producing contexts (/sc:document, /sc:plan, /sc:design, plan/spec writing, writing into CLAUDE.md / AGENTS.md / `.claude/rules/`); Read explicitly before creating docs outside those triggers</loading>
  </role>

  <doc_output_convention note="Unified naming for all file-producing commands.">

Long documents: settle the structure and the hard decisions before writing, then write the document once; drafting it in full while reasoning and again as output doubles the turn without improving it.

Size: each feature, plan or standalone doc file targets under 25KB, leaving headroom below the size guard so the next stage reads it whole; living docs and ADRs are exempt. Units follow the guard: 25KB = 25,000 bytes, and the guard blocks a Read at 30,000 bytes (`file_size_guard.py`). Decide the split with the structure: a feature doc expected over the target is written as split files from the start, and measuring after writing is the check. Measure after writing with `wc -c <file>` (bytes, not characters; non-ASCII text such as Korean takes 3 bytes per character). 25,000–29,999 bytes: report the size and split at the next sizable addition. 30,000 or more: split now. Existing content the request did not touch is never cut or reworded to meet the target. Over the target, the split by doc type:
  Feature doc: split by topic into `NNa-` siblings (Multi-of-same-phase below); the primary file keeps the summary and a link to each; the README lists every file.
  Plan (05 slot, /sc:plan and /sc:roadmap output): re-read mid-exec, so split by phase. The plan file becomes the index (header, shared rules, phase order with one checkbox per phase linking its file, footer); each phase goes to `05<letter>-plan-<phase-name>.md` (distinguisher rules apply) with its own frontmatter {status, revised} and a header line linking back to the index. A phase file still over the target means the phase is too big for one commit: split the phase.
  Standalone doc: one file by definition, never split. Expected over the target → recommend `[f]` at slug resolution (below); declined, written to an explicit path, or already over → it stays one file.

Default (multi-doc work): docs/features/<feature-slug>/
  Required: README.md (frontmatter + index) + numbered phase files
  Phase prefixes: 00-intent (intent) | 01-discovery (brainstorm) | 02-research | 03-analysis | 04-design | 05-plan (plan, roadmap) | 06+-<custom> (impl notes, retrospective)
  Multi-of-same-phase: `NNa-<phase>-<distinguisher>.md` (letter = first one not yet used for that NN in the folder, `archive/` included, so files written earlier keep theirs; distinguisher kebab-case ≤20 chars). Primary slot `NN-<phase>.md` optional — letters start at 'a' even when primary skipped. Use for parallel streams (02a-research-libs, 02b-research-perf), phase-specific sub-discovery within multi-phase feature (01a-discovery-phase2), mid-implementation discovery (01a-discovery-late), or a size split (Size above).
  Superseded versions: move to <feature>/archive/ subdir
  Feature-slug: kebab-case, ≤40 chars, no dates/usernames, locked at dir creation

Standalone (single-doc one-off): docs/<type>/<slug>-<suffix?>-<username>-YYYY-MM-DD.md
  Type→dir: analyze→analysis/ | research→research/ | design→specs/ | brainstorm→specs/ | plan→plans/ | roadmap→plans/
  Suffix (shared dirs): brainstorm→-discovery | design→-design | roadmap→-workflow
  Standalone criteria: 1 doc total, no follow-on phases, lifespan <1 week. When a second related doc is about to be written, tell the user both docs can move into a feature folder with /sc:promote-feature <slug>; move nothing unless the user runs it.
  Docs written before the project adopted this convention stay in place; no bulk move.

Slug resolution (file-producing commands): derive a kebab-case slug from the command's topic and compare it with the directory names under docs/features/. One name equals the slug → write there without asking. Names that contain the slug or are contained in it → ask the user to pick. No match → ask `[f]` new feature folder / `[s]` standalone, pre-selecting the command default: `[f]` for brainstorm, design, plan, roadmap; `[s]` for analyze, research. When asking is not possible (sub-agent, headless run), use the default and state the chosen path in the reply.
README update on feature-path write: `updated:` bump + append doc entry to `## Documents` + set `phase:` from the phase mapping below. Standalone path: no README update.
Phase mapping (README `phase:` = the furthest stage the folder has reached; it never moves back, so a late `01a-discovery` during implementation leaves `implementing`):
  00-intent written → intent | 01-discovery written → discovery | 04-design written → design | 05-plan written → planning
  first plan box checked (plan `status: implementing`) → implementing | plan (index) `status: complete` → complete
  02-research, 03-analysis, 06+ docs and `deprecated` docs never move it; a folder they create starts at discovery
  abandoned: only when the user says the feature is dropped

Living docs (UPPER_SNAKE, no date/username): docs/reports/{PROJECT_INDEX,...}.md (sc:index, sc:index-repo, sc:document --type api)
ADRs (sequence, unchanged): docs/adr/NNNN-<slug>.md (4-digit, per-dir counter)
Archive: docs/archive/features/<slug>/ (completed features) | docs/archive/{plans,specs}/ (pre-existing legacy)
Inline only (no file output): test, build, cleanup — console + tool artifacts (coverage/, the build output dir)

Durability routing (writing INTO a doc the session always loads: CLAUDE.md, AGENTS.md, `.claude/rules/**`, any file the start-of-session import chain pulls in)
  Admissible: invariants — true until someone deliberately changes the system — plus frozen evidence for them (past-tense measurement, version floor, citation). A date is fine; an expiring truth value is not.
  Expiry test: name the routine event that falsifies the sentence (file added, version shipped, upstream fix, a week passing). Nothing in the project notices that event → not an invariant. Route it:
    task state, to-do, next step → TodoWrite | docs/features/<slug>/
    progress log, "what's new", migration narrative → commit body | CHANGELOG | features/ retrospective
    dated observation, open upstream bug → `.claude/rules/gotchas/<domain>.md` ([R19 Project Gotcha Capture], and /sc:reflect ages it) | the tracker link alone
    cross-session learning → /sc:insight (`.claude/insights.jsonl`) | `.claude/memories/` (/sc:save) | auto memory
    derived count, inventory, version → delete the value; name the command that computes it, or pin it in a test that counts the source
  Pin a derived value to its source, never to another doc copy — copies go stale together and stay green. If the project already tests or lints that value, the check must cover every occurrence, not only the first; do not add new lint infrastructure unasked.

Username: `git config user.name` (lowercase, no spaces) — fallback OS username

Frontmatter rules:
  Feature README: {feature, phase, owner, created, updated, related?}. Phase enum: intent | discovery | design | planning | implementing | complete | abandoned
  Phase doc (inside feature folder): {status, revised} — new docs start `status: draft` (00-intent: `approved-for-plan`, written only after its Approve step or a `/sc:intent --through` request), `revised: <today>`
  Standalone specs/+plans/: {status, revised}
  Plan docs (feature or standalone): `status: complete` only when every task checkbox is checked (a task dropped by decision: `- [x] ~~task~~`) and, for the plan (index), its `## Proof` footer carries a `Result:` line naming the last commit that changed code, from a green run or with the user's recorded acceptance (/sc:implement Integrate step); departures from the plan, drops included, go under `## Deviations` in the same commit as the code that departed
  Standalone research/+analysis/: optional {status, revised}
  Reports/ADRs: none
Status enum (per-doc): draft | review | approved-for-plan | implementing | complete | deprecated
Status migration (legacy → enum): approved/reviewed → approved-for-plan | done/implemented/closed → complete | superseded → deprecated

Cross-links: relative path within feature (./04-design.md) or across (../oauth-flow/05-plan.md). Stable because slugs are locked at dir creation, until the folder is archived. Cross-feature: relative path only (`../<other-slug>/NN-<phase>.md`). Slug refs (`[[...]]`) not supported.

Formatter: /sc:cleanup --type docs reports violations (including duplicate slugs); with --apply it fixes frontmatter shape and regenerates README `## Documents`

Examples:
  docs/features/auth-refactor/README.md
  docs/features/auth-refactor/04-design.md
  docs/features/auth-refactor/01a-discovery-phase2.md (additional same-phase doc)
  docs/specs/selection-protocol-design-jdoe-2026-03-20.md (standalone or legacy)
  docs/adr/0001-event-sourced-orders.md
  </doc_output_convention>

  <workflow_gates>
    "Committed" names a precondition: when it is unmet, tell the user or offer to commit; do not commit unasked.
    /sc:intent -> /sc:brainstorm | /sc:plan: User approves the intent text in their own words (a `--through` request is that approval); file committed before analysis starts
    /sc:brainstorm -> /sc:design: User approves discovery spec before designing (a `/sc:intent --through` request is that approval; with `--ask`, the user answers the Checkpoint questions)
    /sc:brainstorm -> /sc:review: Spec self-review mandatory before /sc:plan handoff, because approved specs can still carry reversed decisions (see the /sc:brainstorm Self-review step)
    /sc:design -> /sc:plan: Design spec committed (components pass [R18 Necessity Test] necessity test, deferred items marked, Areas of concern resolved by the owner, or planned past by the owner at the /sc:plan Load step)
    /sc:design -> /sc:roadmap: Alternative path when input is a PRD/feature doc rather than a design spec
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:roadmap -> /sc:implement: Roadmap tasks defined; implementation proceeds per task list
    /sc:implement -> /sc:review --scope branch (Large; optional for Medium) | /sc:test: plan doc checkboxes and its Deviations section match the code; the Proof ran on the last code commit (`Result:` line)
    /sc:review -> fix -> /sc:review: a fix to a Critical or Important review finding that changes reviewed code or shipped content is reviewed again, with the earlier findings as acceptance criteria (the review packet in RULES.md Intent Propagation); rounds stop when a review round finds no Critical or Important finding, or the user has accepted the ones it found unfixed or waived the review of their fix; leftover Suggestions are reported, not reviewed again. A `/sc:intent --through` run keeps its single fix round; its /sc:test step names the fix that went unreviewed
    /sc:test -> /sc:reflect | done: Test pass evidence required (actual output, not claims). Work run from a plan document (a feature folder's `05-plan.md` or a `docs/plans/` plan) goes to /sc:reflect; other work is done here
    /sc:reflect -> done: every gap /sc:reflect names is fixed (a fix that changes reviewed code or shipped content goes back to review, above) or accepted by the user
  </workflow_gates>
</component>
