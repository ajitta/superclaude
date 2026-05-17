---
status: complete
revised: 2026-05-18
---

# Open Decisions Resolution — Doc Convention v2

## Scope

Resolve the 5 open decisions tracked in `docs/features/doc-convention-v2/README.md` `## Open Decisions` section. Each resolution becomes input to either a RULES.md text update or the Phase 3 validator (`/sc:cleanup --type docs` extension) design.

## Resolved Decisions

| # | Question | Decision | Mode |
|---|---|---|---|
| Q1 | Cutoff date for legacy doc format | 2026-05-18 (ratify today — already encoded in RULES.md). New docs follow v2 starting now; pre-cutoff legacy explicitly grandfathered in place. | confirmed |
| Q2 | Migrate-on-touch policy | Manual migration action only. User must invoke `/sc:promote-feature` explicitly to convert a legacy standalone doc to feature-folder form. Auto-prompt-on-significant-revision (>20% line delta per 04-design.md L202) RETAINED as suggestion-only — system surfaces "consider promotion" notice but does NOT migrate without user confirm. Policy applies to ACTION, not detection. | confirmed |
| Q3 | Validator command location | Extend `/sc:cleanup --type docs`. Single command, single mental model. RULES.md already mentions it; Phase 3 adds the validator pass alongside existing format/transform/migrate work. No new `/sc:validate-docs` command. | confirmed |
| Q4 | Cross-feature link form | Relative path (`../oauth-flow/05-plan.md`). Markdown-native, GitHub renders correctly, no custom resolver needed. Slug-ref `[[oauth-flow#plan]]` rejected — requires Obsidian-style processor. | confirmed |
| Q5 | Standalone-to-feature promotion trigger | Both: `/sc:promote-feature` command works standalone AND system auto-detects on 2nd related doc (same slug overlap) + prompts user. Auto-detect is suggestion-only — actual migration still gated on user confirm, consistent with Q2 manual policy. | confirmed |

## Implications by Surface Area

### RULES.md `<doc_output_convention>` Updates

- Q1 ratification: `Legacy pre-cutoff (2026-05-18): stays in place, no bulk move` already present; no change needed.
- Q4 link form: add line under "Cross-links" — `Cross-feature: relative path only (../<other-slug>/NN-<phase>.md). Slug refs not supported.`

### Phase 3 Validator (`/sc:cleanup --type docs`)

Validator pass behaviors derived from Q1-Q5:

1. **Slug duplicate lint** (already specified in RULES.md) — flag standalone docs whose slug also exists as feature folder.
2. **Cross-feature link form** (Q4) — flag any `[[...]]` slug-ref in feature folder docs; suggest relative-path rewrite.
3. **Cutoff date enforcement** (Q1) — for docs created after 2026-05-18 outside feature folder format, flag as v2 non-compliant. Pre-cutoff: skip.
4. **2nd-doc promotion auto-detect** (Q5) — when running `/sc:cleanup`, detect standalone docs with slug already used by another standalone or feature folder; surface as "consider /sc:promote-feature".
5. **Manual policy enforcement** (Q2) — validator does NOT auto-migrate, only reports. `/sc:cleanup --type docs --apply` runs auto-fixes only for low-risk transforms (frontmatter shape, README index regen), never bulk migration. Auto-prompt-on-revision (>20% line delta per 04-design.md L202) is surfaced as suggestion in validator output; user must explicitly invoke `/sc:promote-feature` to act on it.

### `/sc:promote-feature` Command (Q5)

New command needed. Existing in plan as "Out of Scope (Phase 3)". Spec:
- Input: slug or path to standalone doc(s) sharing a slug
- Action: create feature folder, move + rename doc(s) to phase prefixes (`01-discovery.md`, `04-design.md`, etc.), write README with frontmatter + Documents index
- Confirm step before any move (Q2 manual policy)

## Requirements

### R1. Frontmatter date enforcement

Validator MUST parse doc creation date from frontmatter (`created:` field for feature READMEs, `revised:` for phase docs, filename date for legacy standalone). If date > 2026-05-18 AND doc format != v2, surface warning.

### R2. Cross-feature link parser

Validator MUST scan markdown body for `[[...]]` pattern. Each match in a feature folder doc = warning. Each match in standalone doc = informational (legacy may have them; not a v2 violation per se).

### R3. Slug overlap detection

Validator MUST compute set of slugs across `docs/features/<slug>/` dirs + standalone-doc slugs (extracted from filename pre-suffix). Any slug appearing in ≥2 places = "consider promotion" prompt. Slug extraction rule: standalone `<slug>-<suffix>-<username>-YYYY-MM-DD.md` → strip suffix + username + date.

### R4. Promote command interface

`/sc:promote-feature <slug>` finds all standalone docs matching slug → confirms move set with user → creates `docs/features/<slug>/` + README + moves docs with phase-prefix rename → emits cross-link rewrite warnings for any inbound legacy links.

### R5. README open-decisions section update

After this spec ships, README `## Open Decisions` section MUST be emptied (or replaced with "All Phase 2 decisions resolved — see [01b-discovery-open-decisions.md](./01b-discovery-open-decisions.md)").

## Risks

- **R-1 Pre-existing 01a naming + upstream RULES.md example bug**: existing file `01a-phase2-discovery.md` violates RULES.md `NNa-<phase>-<distinguisher>` rule (phase should come before distinguisher → `01a-discovery-phase2.md`). Root cause is TWO RULES.md examples inverting the format spec they describe: `01a-phase2-discovery` (should be `01a-discovery-phase2`) AND `01a-late-discovery` (should be `01a-discovery-late`). Research examples `02a-research-libs`, `02b-research-perf` are correct. Fix scope: RULES.md text edit (2 example strings) + rename existing `01a-phase2-discovery.md` → `01a-discovery-phase2.md` + update all cross-links pointing to the old name. Pre-existing tech debt, surface for separate rename PR. Not blocking Phase 3.
- **R-2 Validator scope creep**: adding 5 checks at once risks over-engineering. Mitigation: Phase 3 plan should sequence checks (slug lint first, then cross-link, then date, then promotion auto-detect) with per-check commit.
- **R-3 /sc:promote-feature blast radius**: command moves files. Mitigation: dry-run default, --apply flag for actual move.

## Success Criteria

- [x] All 5 README open decisions removed and replaced with reference to this doc (done in commit fdfe5ea)
- [ ] RULES.md `<doc_output_convention>` updated with Q4 cross-feature link rule (1 line add under "Cross-links")
- [ ] RULES.md `<doc_output_convention>` multi-of-same-phase examples corrected (`01a-phase2-discovery` → `01a-discovery-phase2`; `01a-late-discovery` → `01a-discovery-late`) per R-1
- [ ] Phase 3 validator spec (next /sc:design pass) cites R1-R4 as input requirements
- [ ] `/sc:promote-feature` command added to backlog with R4 interface signature

## Verification Level

Per `<verification_ladder>` Level 0 (docs/comments/text-only). Static inspection: this doc + README diff only. No code change in this spec.

## Self-Review Iteration Log

- v1 (2026-05-18): Initial draft. 5 confirmed decisions tabulated, implications mapped to RULES.md / validator / promote-command surfaces, R1-R5 requirements stated, R-1/R-2/R-3 risks captured. Pending /sc:review.
- v2 (2026-05-18): /sc:review pass found 1 critical + 2 important + 2 suggestion findings. Applied: (C1 Path B) Q2 amended to clarify "manual = ACTION not detection" + retained auto-prompt-on-revision per 04-design.md L202 as suggestion-only; (I1) R-1 risk expanded to flag upstream RULES.md example bug — TWO examples invert format spec (`01a-phase2-discovery` + `01a-late-discovery`); (I2) R5 README update marked done (commit fdfe5ea). Status bumped draft → approved-for-plan. Ready for /sc:plan handoff.
