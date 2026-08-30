# Architecture

This project's architecture doc is **not** here. The taxonomy SSOT lives with the
code it describes:

**→ [`src/superclaude/ARCHITECTURE.md`](../src/superclaude/ARCHITECTURE.md)**

It covers directory roles, delivery pipelines, and content types for the
`superclaude` package.

## Why this file is a pointer

`/sc:init i` scaffolds `docs/ARCHITECTURE.md` by default. Copying the template
here would have produced a second architecture document describing the same
system — two copies that drift apart, with nothing in the project noticing when
they disagree. `CLAUDE.md` already routes readers to the in-package file, so
that one stays authoritative and this one only forwards.

## Related

- [`CONTEXT.md` / `docs/adr/`](./adr/) — the *why* behind structural decisions
- [`docs/PRD.md`](./PRD.md) — the *what* and *for whom*
- `CLAUDE.md` (repo root) — working agreements for Claude Code in this repo
