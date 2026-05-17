---
status: draft
revised: 2026-05-18
---

# Design — Feature Folder Convention v2

## Problem Statement

Current `<doc_output_convention>` scatters docs for one task across 5 sibling dirs:

```
docs/specs/auth-refactor-discovery-ajitta-2026-05-10.md
docs/research/auth-refactor-libs-ajitta-2026-05-11.md
docs/analysis/auth-refactor-tradeoffs-ajitta-2026-05-13.md
docs/specs/auth-refactor-design-ajitta-2026-05-12.md
docs/plans/auth-refactor-ajitta-2026-05-14.md
```

Concrete failure modes observed:

1. **Slug drift** — same feature gets `auth-refactor`, `auth-rework`, `authentication-refactor` across files. Discipline-dependent.
2. **Cross-link breakage** — `04-design` references discovery file by absolute path; slug rename or filename change breaks link silently.
3. **No canonical phase indicator** — must `ls` all 5 dirs + grep to find current state.
4. **Bulk operations awkward** — "show me all auth-refactor work" requires `find docs -name '*auth*'`.
5. **Allocation race avoided but at cost** — date+username collision-proofs filename but kills cross-ref stability.

## Decision

Adopt **per-feature folder** structure for multi-doc work. Keep **standalone hybrid** for one-off docs. Migrate existing legacy via cutoff date.

## Folder Structure

```
docs/
├── features/                              # ACTIVE multi-doc work
│   └── <feature-slug>/
│       ├── README.md                      # required: frontmatter + doc index
│       ├── 01-discovery.md                # /sc:brainstorm output
│       ├── 02-research.md                 # /sc:research output (or 02a, 02b for multiple)
│       ├── 03-analysis.md                 # /sc:analyze output
│       ├── 04-design.md                   # /sc:design output
│       ├── 05-plan.md                     # /sc:plan or /sc:workflow output
│       ├── 06+-<custom>.md                # impl notes, retrospective, RCA, etc.
│       └── archive/                       # superseded versions (optional)
├── archive/
│   └── features/<feature-slug>/           # completed features (manual move)
├── adr/                                   # unchanged: NNNN-<slug>.md (sequence per-dir)
├── reports/                               # unchanged: living docs UPPER_SNAKE
├── specs/                                 # STANDALONE one-off + legacy pre-cutoff
├── plans/                                 # STANDALONE one-off + legacy pre-cutoff
├── analysis/                              # STANDALONE one-off + legacy pre-cutoff
└── research/                              # STANDALONE one-off + legacy pre-cutoff
```

## Naming Rules

### Feature slug

- kebab-case
- ≤40 chars
- No dates, no usernames embedded (those live in frontmatter)
- Stable for feature lifetime (dir name is the slug; rename forbidden once any cross-link exists)
- Noun phrase or imperative (`auth-refactor`, `add-oauth`, `kill-legacy-cache`)

### Phase-number → doc-type mapping (fixed positions)

| Prefix | Type | Producer command | Notes |
|---|---|---|---|
| `01-` | discovery | `/sc:brainstorm` | Requirements elicitation, problem framing |
| `02-` | research | `/sc:research` | External evidence (libs, prior art, docs) |
| `03-` | analysis | `/sc:analyze` | Trade-off study, option comparison |
| `04-` | design | `/sc:design` | Solution architecture, spec |
| `05-` | plan | `/sc:plan`, `/sc:workflow` | Task breakdown, sequencing |
| `06+-` | custom | manual / `/sc:implement` notes | Retrospective, RCA, follow-up |

Fixed-position numbering means skipped phases leave gaps:
```
01-discovery.md
04-design.md          # research + analysis skipped; gap is informative
05-plan.md
```

### Multi-of-same-phase

Append letter:
```
02a-research-libs.md
02b-research-perf.md
04a-design-v1.md            # superseded → move to ./archive/
04b-design-v2.md            # current
```

### Superseded versions

Move to `<feature>/archive/` subdir. Don't delete. Don't `git rm` (history is in git; archive subdir keeps current `ls` clean).

## README.md Spec

### Required frontmatter

```yaml
---
feature: <slug>                  # MUST equal dir name (validator enforces)
phase: <phase-enum>              # discovery|design|planning|implementing|complete|abandoned
owner: <username>                # primary contributor (git config user.name)
created: YYYY-MM-DD              # first doc creation date
updated: YYYY-MM-DD              # last modification (any file in folder)
related: [<slug>, ...]           # optional: other feature slugs that link in/out
---
```

### Phase enum (feature-level)

| Phase | Meaning |
|---|---|
| `discovery` | Brainstorming requirements; no design yet |
| `design` | Solution being designed; no plan yet |
| `planning` | Plan being authored or under review |
| `implementing` | Plan approved, code in progress |
| `complete` | Shipped, retrospective done |
| `abandoned` | Won't pursue; kept for context |

Separate axis from individual-doc `status:` (which tracks per-doc approval). README tracks **where in workflow**; per-doc frontmatter tracks **per-doc approval state**.

### Required body sections

1. `# <Feature Name>` — H1 title (human-readable, not slug)
2. `## Purpose` — 1-3 sentences, why this feature exists
3. `## Documents` — index of files (auto-regenerable via `/sc:cleanup --type docs`)
4. `## Status` — current phase + what blocks moving to next
5. `## Open Decisions` — checklist of unresolved questions

Optional: `## Related Features`, `## External References`, `## Retrospective` (post-complete).

## Frontmatter Rules

| File location | Required | Optional |
|---|---|---|
| `docs/features/*/README.md` | `feature`, `phase`, `owner`, `created`, `updated` | `related` |
| `docs/features/*/<NN>-*.md` | `status`, `revised` | — |
| `docs/specs/`, `docs/plans/` (standalone + legacy) | `status`, `revised` | — |
| `docs/research/`, `docs/analysis/` (standalone) | — | `status`, `revised` |
| `docs/adr/`, `docs/reports/` | — | — |

Status enum unchanged: `draft | review | approved-for-plan | implementing | complete | deprecated`.

## Standalone Hybrid

Not every doc needs a feature folder. One-off work stays in `docs/<type>/` with current `<slug>-<suffix?>-<username>-<date>.md` naming.

### Standalone criteria

Doc is standalone if **all** true:
- 1 doc total expected (no follow-on phases)
- No cross-doc references planned
- Lifespan < 1 week of active discussion

### Promotion to feature

When 2nd related doc is needed, promote:
- New command: `/sc:promote-feature <slug>` moves matching files into `docs/features/<slug>/`, creates README, renumbers to phase positions
- Cross-links updated automatically
- Original locations get tombstone redirect comment (1-line): `<!-- moved to docs/features/<slug>/04-design.md -->`

Auto-detection (optional): commands that produce 2nd doc for same slug warn and offer promotion.

## ADRs (unchanged)

`docs/adr/NNNN-<slug>.md` — 4-digit sequence prefix, per-dir counter. ADRs may emerge from feature work but live separately because architectural decisions transcend single feature.

When feature work produces an ADR, reference both directions:
- Feature README `related:` list includes ADR slug
- ADR body links back to source feature folder

## Living Docs (unchanged)

`docs/reports/PROJECT_INDEX.md`, etc. UPPER_SNAKE, no frontmatter, regenerated by their producer command.

## Cross-Links

Within feature: relative path
```markdown
See [design](./04-design.md).
```

Cross-feature: relative path from root
```markdown
See [oauth-flow plan](../oauth-flow/05-plan.md).
```

Stable because feature slugs are locked at dir creation.

## Migration

Legacy files (pre-2026-05-18) **stay in place**. No bulk move. Two reasons:
1. Most legacy docs are history; rarely touched
2. Bulk move breaks every external link (commits, PR descriptions, archived chats)

New work uses feature folder. Validator flags legacy-style filenames in `docs/<type>/` created after cutoff as warnings.

**Migrate-on-touch**: when a legacy doc is significantly revised (>20% line delta), prompt user to promote to feature folder. Manual override always available.

## Validation Rules

`/sc:cleanup --type docs` extended:

- Every `docs/features/*/` has `README.md`
- README `feature:` matches dir name
- README `updated:` ≥ latest file mtime in folder
- No `NN-` prefix gaps that contradict claimed phase (e.g., `phase: planning` but no `04-design.md`)
- Duplicate-ish slug detection (Levenshtein distance < 3 across `docs/features/`)
- Tombstone redirects in legacy locations still point to valid targets
- Auto-regenerate README `## Documents` section from file list

## Trade-offs Accepted

| Loss | Mitigation |
|---|---|
| Per-type browsing (`ls docs/plans/`) | `find docs/features -name "05-plan.md"` or new helper command |
| Per-author filtering by filename | Frontmatter `owner:` + grep |
| Per-date filtering by filename | Frontmatter `created:` / git log |
| One-time bulk migration cost (deferred) | Migrate-on-touch + grandfather minimize forced churn |

## Not in Scope

- Renaming existing `docs/{specs,plans,analysis,research}/` dirs (they keep their role for standalone + legacy)
- Changing ADR or reports convention
- Auto-generated cross-feature dependency graph (future tool, separate feature folder)
- Migrating worktree-specific docs (`.claude/worktrees/*/docs/`) — out of scope; those are ephemeral
