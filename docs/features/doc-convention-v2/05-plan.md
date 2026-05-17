---
status: draft
revised: 2026-05-18
---

# Plan — Feature Folder Convention v2 Rollout

## Goal

Ship feature-folder convention as the default for multi-doc work. Update RULES.md, command outputs, and validator. Preserve legacy docs. Verifiable end state: a new `/sc:brainstorm` run writes to `docs/features/<slug>/01-discovery.md`, not `docs/specs/<slug>-discovery-...md`.

## Success Criteria

- [ ] `<doc_output_convention>` in `src/superclaude/core/RULES.md` describes feature-folder layout + standalone hybrid
- [ ] At least one feature folder exists in `docs/features/` (this folder, doc-convention-v2, counts as canary)
- [ ] `make test` passes (markdown-only changes; baseline ~1,904)
- [ ] `make sync-user` deploys updated RULES.md to `~/.claude/superclaude/core/RULES.md`
- [ ] A follow-up `/sc:design` invocation correctly routes to `docs/features/<slug>/04-design.md`

## Phases

### Phase 1 — Convention spec (this PR) — MUST be sequential

1. Write `docs/features/doc-convention-v2/README.md` ✓ (done in this session)
2. Write `docs/features/doc-convention-v2/04-design.md` ✓ (done in this session)
3. Write `docs/features/doc-convention-v2/05-plan.md` ✓ (this file)
4. Rewrite `<doc_output_convention>` in `src/superclaude/core/RULES.md`
5. Verify RULES.md size stays under 400-line ceiling per xml-prose-format
6. `make test` → expect 0 regression (markdown-only)
7. Commit: `docs(convention): introduce feature-folder layout v2`

### Phase 2 — Command output updates (next session)

Files to touch (one per command):
- `src/superclaude/commands/brainstorm.md` — route output to feature folder
- `src/superclaude/commands/design.md` — same
- `src/superclaude/commands/plan.md` — same
- `src/superclaude/commands/workflow.md` — same
- `src/superclaude/commands/research.md` — feature-or-standalone prompt
- `src/superclaude/commands/analyze.md` — feature-or-standalone prompt

Per-command edit:
- Add path resolution: check `docs/features/<slug>/` exists → use it; else ask "feature or standalone?"
- On feature path: write next phase number; update README index; bump `updated:` date
- On standalone path: existing `docs/<type>/<slug>-...md` convention

Risk: command bodies are user-facing. Test with `/sc:brainstorm` on throwaway slug before commit. Verification level 1 (single-file behavior change, no cross-boundary).

### Phase 3 — Validator + tooling (separate PR, no dependency)

- New `/sc:promote-feature <slug>` command — finds matching legacy files, moves into feature folder, renumbers, leaves tombstone redirect
- Extend `/sc:cleanup --type docs`:
  - Check every feature folder has README
  - Auto-regenerate README `## Documents` index
  - Lint duplicate-ish slugs (Levenshtein < 3)
  - Flag legacy-style filenames created after cutoff
- Auto-detection in `/sc:design`, `/sc:plan`: when 2nd doc for same slug detected in legacy dirs, offer promotion

### Phase 4 — Documentation + onboarding (low priority)

- Update `src/superclaude/ARCHITECTURE.md` if it references doc layout
- Update `CLAUDE.md` if needed (currently doesn't reference doc convention specifics)
- Update `.claude/rules/gotchas/general.md` with new gotcha: "feature-folder slug locked at creation"

## Verification Per Phase

Per `<verification_ladder>`:
- Phase 1: Level 0 (docs/text only) — static inspection + `make test` (markdown safety check)
- Phase 2: Level 1 (single-file behavior, no API boundary) — manual `/sc:brainstorm` smoke test on throwaway slug
- Phase 3: Level 2 (multi-file, validator behavior change) — full `make test` + manual `/sc:cleanup --type docs` run
- Phase 4: Level 0 — static inspection

## Rollback Plan

Each phase is a separate commit. Rollback via `git revert <commit>`. No data destruction; legacy files untouched by Phase 1-2.

## Out of Scope (deferred)

- Bulk migration of existing `docs/{specs,plans,analysis,research}/*.md` to feature folders
- Cross-feature dependency graph visualization
- Worktree-aware doc routing (`.claude/worktrees/*/docs/`)
- Integration with matt-pocock skills `docs/agents/` doctrine (separate concern)

## Open Questions Blocking Plan Execution

1. Cutoff date confirmation: 2026-05-18 (today) acceptable?
2. Phase 2 verification: smoke-test slug name? Resolved per `01a-discovery-phase2.md` Q6 v2 — use `test-feature-folder-temp` (kebab-compliant; `-temp` suffix flags ephemeral). Leading `_` rejected because it violates feature-slug kebab-case rule (04-design.md naming rules).
3. Phase 3 tooling priority: ship validator before or after command updates? Recommend after — commands can write valid output without enforcement, validator catches drift later.
