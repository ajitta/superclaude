branch: master @20d19dbb (v4.34.4 released; stable == 20d19dbb)

# Session 2026-11-08 — claude-box — socratic plugin removed, 4.34.4

## Start here (next session)
1. `git fetch origin && git switch master && git pull --ff-only`, then read this file and `docs/plans/remaining-work-ajitta-2026-10-20.md`.
2. v4.34.4 is released; nothing unreleased on master.

## What was done
- Owner: the socratic plugin is no longer used; remove it and update the docs.
- Removed `portable-skills/` entirely (two skill sources, generated plugin, `socratic.zip`, `package.py`), `tests/unit/test_portable_skills.py`, the Pages `#plugins` section and nav link, and the `.gitignore` lines for it.
- Owner chose (a): `.claude-plugin/marketplace.json` stays as the empty `ajitta-socratic` marketplace — `plugins: []`, `renames` keeps `socratic-brainstorm`/`socratic-elenchus` → `socratic` and adds `socratic: null`, `forceRemoveDeletedPlugins: true`. `claude plugin validate .` passes (warning: no plugins). Verified in scratch `CLAUDE_CONFIG_DIR`s with Claude Code 2.1.314 (directory marketplace source): after `marketplace update`, the next session start uninstalled `socratic` and both earlier plugins and flagged them; `marketplace remove` also uninstalls. A GitHub-source marketplace was not exercised.
- New guard `tests/unit/test_marketplace.py` (name, retired names unlisted, renames chain, forceRemove, listed sources exist); mutation-checked (v4.34.3 file → 4 red; dropping `socratic: null` or `forceRemoveDeletedPlugins` → 1 red each).
- Docs: `socratic-brainstorm-skill` and `portable-skills-single-plugin` moved to `docs/archive/features/` with a removal note and links to tag v4.34.3; `plugin-install/05-plan.md` (held, draft) updated for the empty marketplace and the new test; CHANGELOG 4.34.4 `### Removed` with the upgrade steps. Completed plans/reviews that mention portable-skills were left as records.
- Owner chose: release 4.34.4 right after merge; no pointer to ajitta/dialectic-skills in the CHANGELOG.
- Full suite 3837 passed, 3 skipped (branch, bump branch, merge); format, lint, typecheck clean.

## Decisions
- The empty marketplace file and its `renames` entries are permanent history (Claude Code follows the chain from the oldest name); do not rename the marketplace, or the removal stops reaching machines that still have the plugin.

## Next actions
- [x] Release 4.34.4 (2026-11-08): CI green on 20d19dbb; `make release` (no canary: only `__init__.py` changed under src/) → tag v4.34.4, stable → 20d19dbb; stable's marketplace.json is the empty one, `portable-skills/` 404s there; this VM installed (`--scope user`), no drift.
- [ ] Owner, Windows: `superclaude install --force --scope user` for 4.34.3/4.34.4; if the socratic plugin is installed there, `/plugin marketplace remove ajitta-socratic`.
