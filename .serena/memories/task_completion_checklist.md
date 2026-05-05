# Task Completion Checklist

## After any Python code change
1. `make format` — ruff format (fix style)
2. `uv run pytest` — verify baseline (1,628 pass / 1,807 collected, do not regress)
3. `make lint` — ruff check (no new warnings)

## After markdown/content changes
- No test run needed (markdown-only changes carry no test risk)
- Verify XML prose format compliance (`.claude/rules/xml-prose-format.md`)
- Check `make verify` if content was installed

## Before committing
- `make format` — ruff format
- Stage specific files (not `git add .`)
- Commit with conventional prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## After install changes
- `make deploy` + `make sync-user` to test locally
- `make verify` — full installation check

## Notes
- Do NOT regress test count below 1,628 passing
- Markdown-only changes: skip tests, just commit
