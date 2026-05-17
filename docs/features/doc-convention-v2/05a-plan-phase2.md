---
status: draft
revised: 2026-05-18
---

# Phase 2 Implementation Plan — Command Output Routing Updates

**Goal:** Update 6 SuperClaude file-producing commands so their output routes to feature-folder layout (per RULES.md `<doc_output_convention>` shipped Phase 1) with standalone hybrid retained.

**Architecture:** Cite-only routing (no per-command `<output_routing>` section duplication). Each command body gets (a) 1-line cite header prepended to `<outputs>` table, (b) conditional write-path prose in flow step, (c) R3 table row showing both feature + standalone paths. RULES.md remains SSOT.

**Tech Stack:** Markdown edits only. No Python/test code. Verification = `/sc:brainstorm` smoke run + `make test` (baseline ~1,904) + `make sync-user` deploy.

**Source spec:** `docs/features/doc-convention-v2/01a-phase2-discovery.md` v2 (status: approved-for-plan)

## Files Map

| File | Action | Job |
|---|---|---|
| `src/superclaude/commands/brainstorm.md` | Modify | Phase 1 canary — full pattern (R1+R2+R3) |
| `src/superclaude/commands/design.md` | Modify | Phase 3 replication |
| `src/superclaude/commands/plan.md` | Modify | Phase 3 replication |
| `src/superclaude/commands/workflow.md` | Modify | Phase 3 replication |
| `src/superclaude/commands/research.md` | Modify | Phase 3 replication |
| `src/superclaude/commands/analyze.md` | Modify | Phase 3 replication |
| `docs/features/test-feature-folder-temp/` | Create then delete | Smoke test artifact (Phase 2), cleaned in Phase 4 |
| `docs/features/doc-convention-v2/README.md` | Modify | Add this plan to `## Documents` index (R4 dogfood) |

## Branch + Commit Strategy

Single branch `feature/phase2-command-routing` off master. Per Q5 checkpoint-gated single PR — commit brainstorm.md first, smoke test, only-if-green replicate 5 more commits, then cleanup commit.

Commit count target: 7 (1 canary + 5 replications + 1 cleanup+sync). All conventional-commit format.

## Phases

### Phase 1 — Brainstorm.md canary edit

**Files:** Modify: `src/superclaude/commands/brainstorm.md` (lines ~12-43 — `<flow>` + `<outputs>`)

- [ ] 1.1 Re-read current brainstorm.md `<flow>` step 4 (L16) + `<outputs>` table (L38-43)
- [ ] 1.2 Edit `<flow>` step 4 per R2 — path-conditional prose + threaded R4 README update inline. Exact prose: "Specify (routing per RULES.md `<doc_output_convention>`): on feature path, write spec to `docs/features/<slug>/01-discovery.md` (frontmatter: `status: draft, revised: <today>`) AND update `docs/features/<slug>/README.md` (`updated:` bump + append entry to `## Documents`, advance `phase:` if status enum moved). On standalone path, write to `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` — no README update needed."
- [ ] 1.3 Prepend R1 cite line to `<outputs>` table body (before `| Artifact | Purpose |` row): "Routing: per RULES.md `<doc_output_convention>` — feature path `docs/features/<slug>/01-discovery.md` (existing folder OR user picks `[f]`) | standalone path `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` (user picks `[s]` or no related work expected). Slug resolution: exact-match silent / multi partial-match prompt / zero match → `[f]/[s]` w/ default `[f]`."
- [ ] 1.4 Replace `<outputs>` first table row w/ R3 dual-path shape: `| Feature path | docs/features/<slug>/01-discovery.md | Phase doc, when slug resolves to existing/new feature folder |` + `| Standalone path | docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md | One-off discovery, no related work expected |`
- [ ] 1.5 Verify file still passes structural test: `uv run pytest tests/unit/test_command_structure.py -v -k brainstorm`
- [ ] 1.6 Verify body size still ≤200-line target per xml-prose-format: `Get-Content src/superclaude/commands/brainstorm.md | Measure-Object -Line`
- [ ] 1.7 `make sync-user` to deploy to `~/.claude/superclaude/commands/brainstorm.md` (smoke needs deployed copy)
- [ ] 1.8 Commit: `feat(commands): route brainstorm output to feature-folder per doc-convention-v2`

### Phase 2 — Smoke test gate (Q5 checkpoint, BLOCKING)

**Files:** Create: `docs/features/test-feature-folder-temp/` (via /sc:brainstorm invocation)

- [ ] 2.1 Invoke `/sc:brainstorm 'phase2 routing smoke check' --feature test-feature-folder-temp` (new session or current — both fine since brainstorm.md deployed)
- [ ] 2.2 Verify output: `Test-Path docs/features/test-feature-folder-temp/01-discovery.md` returns `True`
- [ ] 2.3 Verify README created: `Test-Path docs/features/test-feature-folder-temp/README.md` returns `True`
- [ ] 2.4 Verify README index entry: grep for `01-discovery.md` in `docs/features/test-feature-folder-temp/README.md` `## Documents` section
- [ ] 2.5 Verify README `updated:` frontmatter = 2026-05-18
- [ ] 2.6 Verify 01-discovery.md frontmatter = `{status: draft, revised: 2026-05-18}`
- [ ] 2.7 **GATE**: if any of 2.2-2.6 fail → ABORT Phase 3. Diagnose brainstorm.md edit, revert Phase 1 commit if structural error, re-do Phase 1. Do NOT proceed to replication.
- [ ] 2.8 If all green → log smoke pass in spec self-review log (v3 entry) + proceed to Phase 3

### Phase 3 — Replicate to 5 commands (gated on Phase 2 green)

Per-command edit pattern identical to Phase 1 (R1 cite + R2 flow step + R3 dual-path table). Each command gets own commit so review history shows replication clearly.

Per-command path/phase prefix mapping (from R3 table):

| Command | Phase prefix | Standalone dir |
|---|---|---|
| design.md | `04-design.md` | `docs/specs/` |
| plan.md | `05-plan.md` | `docs/plans/` |
| workflow.md | `05-plan.md` (variant) | `docs/plans/` (w/ `-workflow` suffix) |
| research.md | `02-research.md` | `docs/research/` |
| analyze.md | `03-analysis.md` | `docs/analysis/` |

Per-command default for slug-resolution zero-match prompt (per Q3 v2):

| Command | Default |
|---|---|
| design.md | `[f]` |
| plan.md | `[f]` |
| workflow.md | `[f]` |
| research.md | `[s]` |
| analyze.md | `[s]` |

- [ ] 3.1 Edit `design.md` — apply R1+R2+R3 w/ `04-design.md` phase prefix + `[f]` default. Commit: `feat(commands): route design output to feature-folder per doc-convention-v2`
- [ ] 3.2 Edit `plan.md` — apply pattern w/ `05-plan.md` + `[f]` default. Commit: `feat(commands): route plan output to feature-folder per doc-convention-v2`
- [ ] 3.3 Edit `workflow.md` — apply pattern w/ `05-plan.md` (workflow variant; standalone uses `-workflow` suffix) + `[f]` default. Commit: `feat(commands): route workflow output to feature-folder per doc-convention-v2`
- [ ] 3.4 Edit `research.md` — apply pattern w/ `02-research.md` + `[s]` default. Commit: `feat(commands): route research output to feature-folder per doc-convention-v2`
- [ ] 3.5 Edit `analyze.md` — apply pattern w/ `03-analysis.md` + `[s]` default. Commit: `feat(commands): route analyze output to feature-folder per doc-convention-v2`
- [ ] 3.6 After each per-command commit: `uv run pytest tests/unit/test_command_structure.py -v -k <command-name>` — structural test pass before next replication
- [ ] 3.7 After all 5: `make sync-user` to deploy all updated commands

### Phase 4 — Cleanup + sync + final verification

- [ ] 4.1 Delete smoke artifact: `Remove-Item -Recurse -Force docs/features/test-feature-folder-temp/`
- [ ] 4.2 Update `docs/features/doc-convention-v2/README.md` — add this plan entry to `## Documents`, bump `updated:` to today, advance `phase:` from `design` → `planning` (per phase enum)
- [ ] 4.3 Full test: `make test` — expect baseline ~1,904 pass, 0 regression (markdown-only)
- [ ] 4.4 Lint: `make lint`
- [ ] 4.5 Final `make sync-user` to confirm clean deploy
- [ ] 4.6 Spec status bump: `01a-phase2-discovery.md` status `approved-for-plan` → `implementing` → `complete` after Phase 3 ships
- [ ] 4.7 Commit: `chore(docs): clean phase2 smoke artifact + bump feature phase to planning`
- [ ] 4.8 Open PR titled `feat(commands): Phase 2 — route 6 file-producing commands to feature-folder layout`

## Verification Per Phase

Per `<verification_ladder>`:

| Phase | Level | Required check |
|---|---|---|
| 1 | Level 1 | typecheck + lint + unit `test_command_structure.py -k brainstorm` + size check |
| 2 | Level 2 | manual smoke: `/sc:brainstorm` run + 5 file/frontmatter assertions |
| 3 | Level 1 (per command) | structural test per command after each edit |
| 4 | Level 2 | full `make test` + `make lint` + clean sync-user |

## Rollback Plan

Per-commit revert. Each Phase 1 + Phase 3.* commit is independent revert unit. Phase 2 smoke artifact = `Remove-Item -Recurse` if needed. Phase 4 README dogfood revert via git revert.

If Phase 2 smoke fails: revert Phase 1 commit, fix root cause (likely brainstorm.md flow misedit or R1 cite typo breaking parse), re-do Phase 1, re-smoke.

If Phase 3 mid-replication breaks (e.g., commit 3.3 fails structural test): revert that single commit, fix the per-command edit, recommit. Other Phase 3 commits stay.

## Risks (carry-over from spec)

- **R-1 Self-edit risk** (brainstorm.md): Phase 1 ↔ Phase 2 sequencing covers this — smoke test re-invokes the edited command on throwaway slug before replication.
- **R-2 Drift** (RULES.md SSOT vs commands): cite-only design minimizes drift surface; Phase 3 validator catches future regression.
- **R-3 Blast radius**: Q5 checkpoint gate (Phase 2 BLOCKING) limits damage to 1 commit if pattern broken.
- **R-4 README malformed**: handled by brainstorm.md edit — README update should fail loud on missing `## Documents` section (verify in 2.4).

## Done Criteria

All Phase 4 boxes ticked + PR opened + spec status `complete`. Plan retires when PR merges to master.

## Out of Scope (carry-over from spec)

Phase 3 validator (`/sc:promote-feature`, `/sc:cleanup --type docs` extension), bulk legacy migration, cross-feature dependency graph, worktree-aware routing.

## Handoff

→ `/sc:implement --plan docs/features/doc-convention-v2/05a-plan-phase2.md` (Phase 1 only first — checkpoint gate)
