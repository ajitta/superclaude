# Suggested Commands

Canonical sources: `CLAUDE.md` (Python Environment, Developer Environment) and the `Makefile`
itself — `make help` lists the targets, and they change more often than any copy here would.

Two facts the Makefile does not state:

- CI's lint gate is `ruff check src/ tests/` (both workflows). `make lint` runs `ruff check .`,
  a wider net — passing CI's command is the actual bar.
- `make format` *writes* (`ruff format .`); CI only checks (`ruff format --check src/ tests/`).
