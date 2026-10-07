# Task Completion Checklist

Canonical source: `AGENTS.md` (Python Environment, Code Style, Git Workflow).

Gist: `make format` → `uv run pytest` (must exit 0) → `ruff check src/ tests/` → commit.

- Markdown changes are **not** exempt: content, counts, cross-refs and doc structure have tests,
  so a docs-only change still runs the suite.
- A green suite says nothing about lint — they are separate gates, and the lint one was red for
  weeks while pytest passed (fixed 2026-09-11, `1fef6eb`).
- Stage specific files, never `git add .`. Conventional prefixes per AGENTS.md Git Workflow.
- Do not restate a test count anywhere; state the invariant and let the suite hold the number.
- Release only: `make release` refuses when `src/superclaude/core` or `hooks.json` changed since the
  last `v*` tag unless `CANARY_OK=1` — run `make canary-gates` (4 hard-gate tasks, local `claude -p`,
  sonnet, low effort) and read `report.md` first (AGENTS.md "Canary before a release", 2026-10-07).
