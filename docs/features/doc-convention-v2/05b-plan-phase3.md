---
status: complete
revised: 2026-05-18
---

# Phase 3 Implementation Plan — Validator + Promote-Feature Command

**Goal:** Land the doc-convention-v2 validator (extend `/sc:cleanup --type docs`) + new `/sc:promote-feature` command per R1-R4 in 01b spec, plus RULES.md text fixes (Q4 cross-link rule + I1 example bug + 01a rename).

**Architecture:** Pure markdown-command additions. Validator behavior expressed as prompt instructions in `cleanup.md` flow — Claude executes checks via Grep/Glob/Read tools at runtime. `/sc:promote-feature` is new command file with confirm-before-move semantics (Q2 manual policy). RULES.md text edits resolve upstream example bug (I1) and add Q4 cross-link rule. No Python code.

**Tech Stack:** Markdown only. Verification = `uv run pytest tests/unit/test_command_structure.py` per command + `make test` baseline + `make sync-user` deploy + smoke runs on this very repo's docs/ tree.

**Source spec:** `docs/features/doc-convention-v2/01b-discovery-open-decisions.md` v2 (status: approved-for-plan)

## Files Map

| File | Action | Job |
|---|---|---|
| `src/superclaude/core/RULES.md` | Modify (3 edits) | Q4 cross-link rule add (L172 area) + I1 example fix L146 + example fix L179 |
| `docs/features/doc-convention-v2/01a-phase2-discovery.md` | Rename → `01a-discovery-phase2.md` | R-1 rename per format spec |
| `docs/features/doc-convention-v2/README.md` | Modify | Update doc index entry pointing to renamed file + entry 6 add for this plan |
| `src/superclaude/commands/cleanup.md` | Modify | Extend `<flow>` + `<outputs>` with R1-R3 validator behaviors |
| `src/superclaude/commands/promote-feature.md` | Create | New command file per R4 interface (~60-80 lines, command-authoring template) |
| `src/superclaude/commands/README.md` | Modify | Add promote-feature to command table |
| `docs/features/doc-convention-v2/05b-plan-phase3.md` | Create | This plan |

## Branch + Commit Strategy

Single branch `feature/phase3-validator-plan` (already created). Per-phase commits, single PR.

Commit count target: 5 (1 RULES + 1 rename + 1 promote-feature + 1 cleanup validator + 1 plan + readme bump). All conventional-commit format.

## Phases

### Phase 1 — RULES.md text fixes (Q4 + I1)

**Files:** Modify: `src/superclaude/core/RULES.md` (3 spots: L146 multi-of-same-phase examples, L172 cross-links line, L179 examples block)

- [ ] 1.1 Edit L146 examples: `01a-phase2-discovery` → `01a-discovery-phase2`; `01a-late-discovery` → `01a-discovery-late`. Preserve sentence structure.
- [ ] 1.2 Edit L172 cross-links: add sentence after relative-path line: "Cross-feature: relative path only (`../<other-slug>/NN-<phase>.md`). Slug refs (`[[...]]`) not supported."
- [ ] 1.3 Edit L179 example: `01a-phase2-discovery.md` → `01a-discovery-phase2.md` (matches renamed file from Phase 2)
- [ ] 1.4 Verify structural test: `uv run pytest tests/unit/test_core_files.py -v -k rules` (or equivalent SSOT test)
- [ ] 1.5 Commit: `docs(rules): fix multi-of-same-phase examples + add cross-feature link rule`

### Phase 2 — Rename 01a-phase2-discovery.md → 01a-discovery-phase2.md (R-1)

**Files:** Rename: `docs/features/doc-convention-v2/01a-phase2-discovery.md` → `01a-discovery-phase2.md`; Modify: `docs/features/doc-convention-v2/README.md` entry 3 link target; Grep for cross-refs in other docs

- [ ] 2.1 `git mv docs/features/doc-convention-v2/01a-phase2-discovery.md docs/features/doc-convention-v2/01a-discovery-phase2.md`
- [ ] 2.2 Grep repo for `01a-phase2-discovery` references: `grep -r "01a-phase2-discovery" docs/ src/`. Expected hits: README entry 3 link, 05a-plan-phase2.md source-spec mention, maybe README narrative paragraph.
- [ ] 2.3 Update each hit to new name.
- [ ] 2.4 Verify no broken links: re-grep `01a-phase2-discovery`, expect 0 hits.
- [ ] 2.5 Commit: `docs(convention): rename 01a-phase2-discovery to 01a-discovery-phase2 per NNa rule`

### Phase 3 — New /sc:promote-feature command (R4)

**Files:** Create: `src/superclaude/commands/promote-feature.md`; Modify: `src/superclaude/commands/README.md` add row

- [ ] 3.1 Create promote-feature.md per command-authoring template. Required sections: `<role>`, `<syntax>`, `<flow>`, `<outputs>`, `<tools>`, `<examples>`, `<gotchas>`, `<bounds>`, `<handoff>`.
- [ ] 3.2 Flow steps (R4 interface): (1) Scan docs/ for standalone files matching `<slug>` (extract slug from filename pre-suffix); (2) Show match set + confirm with user (Q2 manual gate, --dry-run default); (3) On confirm + --apply: create `docs/features/<slug>/`, move + rename each match to phase prefix per RULES.md mapping (`-discovery` → `01-discovery.md`, `-design` → `04-design.md`, etc.); (4) Generate README with frontmatter + Documents index; (5) Grep repo for inbound legacy paths, emit warning list (do NOT auto-rewrite cross-links — user fixes manually to avoid silent breakage).
- [ ] 3.3 `<outputs>` table: new feature folder + moved files + README + warning report on inbound links.
- [ ] 3.4 `<gotchas>`: slug collision (folder exists), partial slug match ambiguity, cross-link rewrite blast radius.
- [ ] 3.5 Add row to `src/superclaude/commands/README.md` table.
- [ ] 3.6 Verify structural test: `uv run pytest tests/unit/test_command_structure.py -v -k promote-feature` (14/14 pass).
- [ ] 3.7 Commit: `feat(commands): add /sc:promote-feature command per doc-convention-v2 R4`

### Phase 4 — Extend /sc:cleanup --type docs validator (R1-R3)

**Files:** Modify: `src/superclaude/commands/cleanup.md` (flow + outputs + new <validator_checks> section)

- [ ] 4.1 Expand `<flow>` step 3 for `--type docs`: list validator checks invoked sequentially (slug-duplicate, cross-link form, post-cutoff non-v2, slug-overlap promotion-suggest).
- [ ] 4.2 Add new `<validator_checks>` section after `<patterns>` documenting each check: R1 (post-cutoff non-v2 frontmatter check), R2 (cross-feature `[[...]]` pattern flag), R3 (slug-overlap detection across features/ + standalone dirs).
- [ ] 4.3 Update `<outputs>` --type docs row: "Validate (R1-R3 checks) + transform doc naming + suggest promotions; Console: violations + promotion candidates".
- [ ] 4.4 Add R1-R3 gotcha entries (date-parsing edge cases for filename dates, false-positive on intentional `[[...]]` in code blocks).
- [ ] 4.5 Verify structural test: `uv run pytest tests/unit/test_command_structure.py -v -k cleanup` (14/14 pass).
- [ ] 4.6 Verify body size: `(Get-Content src/superclaude/commands/cleanup.md | Measure-Object -Line).Lines` ≤200.
- [ ] 4.7 Commit: `feat(commands): extend /sc:cleanup --type docs with R1-R3 validator checks`

### Phase 5 — Plan dogfood + README + sync + verify + PR

- [ ] 5.1 Add this plan to `docs/features/doc-convention-v2/README.md` Documents (entry 6) + bump `updated:` if not today.
- [ ] 5.2 `make sync-user` — deploy 95+ components including 2 modified + 1 new command.
- [ ] 5.3 `make test` — expect baseline 1964 pass, 0 regression (markdown-only).
- [ ] 5.4 Manual smoke: invoke `/sc:cleanup --type docs --dry-run` on this repo. Expect output: slug-overlap candidates for legacy docs/specs/ + docs/plans/ entries.
- [ ] 5.5 Manual smoke: invoke `/sc:promote-feature <some-slug> --dry-run` on a real legacy slug (e.g., one from docs/specs/). Expect match set + confirm prompt.
- [ ] 5.6 Spec status bump: `01b-discovery-open-decisions.md` status `approved-for-plan` → `complete`; bump 05b status `draft` → `complete`.
- [ ] 5.7 Commit: `chore(docs): bump phase3 spec + plan to complete + dogfood README index`
- [ ] 5.8 Open PR: `feat(commands): Phase 3 — doc-convention-v2 validator + promote-feature command`

## Verification Per Phase

Per `<verification_ladder>`:

| Phase | Level | Required check |
|---|---|---|
| 1 | Level 0 | static inspection (RULES.md is doc/text) |
| 2 | Level 0 | static inspection (file rename + cross-link grep proves no breakage) |
| 3 | Level 1 | typecheck N/A (markdown); structural test per command |
| 4 | Level 1 | structural test per command + size check |
| 5 | Level 2 | full `make test` + manual smoke for 2 commands |

## Rollback Plan

Per-commit revert. Each Phase 1-5 commit is independent revert unit.
- Phase 1 RULES.md fix: revert if it breaks downstream context_loader.py parsing.
- Phase 2 rename: revert via `git mv` reverse + restore cross-link edits.
- Phase 3 promote-feature add: delete the new file via `git rm`.
- Phase 4 cleanup extension: revert single commit.
- Phase 5 README + status bumps: revert single commit.

## Risks (carry-over from 01b spec + new)

- **R-1 RULES.md SSOT change blast radius** (01b R-1 expanded): RULES.md is always-loaded by CLAUDE_SC.md import chain. Format spec change ripples to every command invocation. Mitigation: edits are pure text fixes (example strings, 1 added sentence under Cross-links), no semantic flow change.
- **R-2 Validator over-engineering** (01b R-2): 4 checks in one command pass risks scope creep. Mitigation: per-check section in `<validator_checks>` clearly labels which check fired; user can isolate. Per-check commit is overkill for one command, keep all 4 in single 4.7 commit.
- **R-3 /sc:promote-feature blast radius** (01b R-3): command moves files. Mitigation: `--dry-run` default per 3.2 step (2); `--apply` required for actual move; cross-link rewrite NOT automatic — user-facing warnings only.
- **R-4 Cross-link rewrite gap** (new): Phase 2 grep-based cross-link update for the 01a rename may miss links in commit messages, PR descriptions, archived chats. Accept as known limitation — convention-v2 cross-links policy is forward-looking; legacy mentions outside repo not in scope.
- **R-5 Smoke false-positive** (new): /sc:cleanup --type docs may surface slug-overlap candidates that are legitimately separate features sharing a kebab prefix. Mitigation: validator emits as "suggestion" not "violation"; user decides per case.

## Done Criteria

All Phase 5 boxes ticked + PR opened + 01b spec status `complete` + 05b spec status `complete`. Plan retires when PR merges to master.

## Out of Scope (carry-over from 01b spec)

- Bulk legacy migration (Phase N backlog)
- Cross-feature dependency graph generator
- Worktree-aware routing
- Auto-rewrite of cross-links during `/sc:promote-feature` (left manual per R-3 mitigation)

## Handoff

→ `/sc:implement --plan docs/features/doc-convention-v2/05b-plan-phase3.md` (Phase 1 first — small isolated text fix)
