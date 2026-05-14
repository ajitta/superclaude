# docs/archive

Terminal-status plans, specs, and analysis. Moved here so active `docs/plans/` and `docs/specs/` show in-flight work only.

## Archive gate

A doc is archived when its frontmatter `status` is terminal:

- `complete` (incl. legacy `done`, `implemented`, `closed`)
- `deprecated` (incl. legacy `superseded`)

Pre-convention files with no frontmatter (the `YYYY-MM-DD-` prefix batch, March 2026) are archived as historically shipped.

Active statuses — `draft`, `review`, `approved-for-plan`, `reviewed`, `implementing` — stay in `docs/plans/` and `docs/specs/`.

## Notes

- Moves use `git mv` — full history preserved, files stay greppable.
- Archiving is status-driven, not date-driven. A recent doc with `status: deprecated` archives; an old `draft` does not.
- This is not `/sc:cleanup --type docs` — that command only fixes naming convention. Archiving is a separate manual pass.
