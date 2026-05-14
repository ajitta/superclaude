# docs/archive

Terminal-status plans, specs, and analysis. Moved here so active `docs/plans/` and `docs/specs/` show in-flight work only.

## Archive gate

A doc is archived when its frontmatter `status` is terminal:

- `complete` (incl. legacy `done`, `implemented`, `closed`)
- `deprecated` (incl. legacy `superseded`)

Pre-convention files with no frontmatter (the `YYYY-MM-DD-` prefix batch, March 2026) are archived as historically shipped.

Active statuses — `draft`, `review`, `approved-for-plan`, `reviewed`, `implementing` — stay in `docs/plans/` and `docs/specs/`.

## legacy-userdocs/

`legacy-userdocs/` holds upstream-SuperClaude user documentation — `user-guide/`, `reference/`, `getting-started/`, `developer-guide/`, and the old `docs/README.md`. Archived 2026-05-15.

These were not status-gated — they were retired because the fork diverged far enough that the prose actively contradicted the live SSOT (wrong command/agent counts, flags that no longer exist, `pipx install` paths the fork doesn't use). The SSOT is the framework content under `src/superclaude/` and its per-directory `README.md` files. Kept for historical reference, not maintained.

`docs/troubleshooting/serena-installation.md` was **not** archived — it tracks current fork practice and is referenced from the repo-root README.

## Notes

- Moves use `git mv` — full history preserved, files stay greppable.
- Archiving is status-driven for plans/specs/analysis, divergence-driven for `legacy-userdocs/`.
- This is not `/sc:cleanup --type docs` — that command only fixes naming convention. Archiving is a separate manual pass.
