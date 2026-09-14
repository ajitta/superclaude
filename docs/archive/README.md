# docs/archive

Finished or no-longer-valid docs, moved here so the active `docs/` folders show in-flight work and current reference only. Subfolders mirror where each doc lived: `features/<slug>/`, `specs/`, `plans/`, `analysis/`, `research/`, `reports/`, `guides/`, `codex/`, plus `legacy-userdocs/` below.

## Archive gate

A doc is archived when its frontmatter `status` is terminal:

- `complete` (incl. legacy `done`, `implemented`, `closed`)
- `deprecated` (incl. legacy `superseded`)

A feature folder is archived when its README `phase` is `complete` or `abandoned`.

Pre-convention files with no frontmatter (the `YYYY-MM-DD-` prefix batch, March 2026) are archived as historically shipped.

Active statuses — `draft`, `review`, `approved-for-plan`, `reviewed`, `implementing` — stay in place.

## Content gate

Frontmatter lags reality: many `draft` plans shipped without their status ever being updated. A doc is also archived, whatever its status says, when git history or the current source shows one of:

- the work shipped, or was abandoned;
- a newer doc or feature folder replaced it;
- the files, flags or model versions it describes no longer exist;
- it is sample output rather than a project doc.

The 2026-09-15 pass applied this gate across `docs/`. The evidence for each move is in the commit that moved the file (`git log --follow <path>`). Moved docs keep their original frontmatter.

## legacy-userdocs/

`legacy-userdocs/` holds upstream-SuperClaude user documentation — `user-guide/`, `reference/`, `getting-started/`, `developer-guide/`, and the old `docs/README.md`. Archived 2026-05-15.

These were not status-gated — they were retired because the fork diverged far enough that the prose actively contradicted the live SSOT (wrong command/agent counts, flags that no longer exist, `pipx install` paths the fork doesn't use). The SSOT is the framework content under `src/superclaude/` and its per-directory `README.md` files. Kept for historical reference, not maintained.

`docs/troubleshooting/serena-installation.md` was **not** archived — it tracks current fork practice and is referenced from the repo-root README.

## Notes

- Moves use `git mv` — full history preserved, files stay greppable.
- Archiving is status- or content-driven for project docs (see the two gates above), divergence-driven for `legacy-userdocs/`. `legacy-userdocs/testing/procedures.md` joined it on 2026-09-15 for the same reason.
- This is not `/sc:cleanup --type docs` — that command only fixes naming convention. Archiving is a separate manual pass.
