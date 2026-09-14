---
feature: auto-improve
phase: complete
owner: ajitta
created: 2026-04-27
updated: 2026-05-18
---

# Auto-Improve

## Purpose

Autonomous overnight code improvement loop driven by an objective metric (Karpathy AutoResearch pattern). Implementation shipped 2026-05-03 as `src/superclaude/scripts/auto_improve/` (28 files, 2765 lines) + `/sc:auto-improve` command. This folder holds the original discovery → design → plan trio.

## Documents

1. [Discovery](./01-discovery.md) — 2026-04-27, status: approved-for-plan — autonomous loop requirements + 6 design questions resolved
2. [Design](./04-design.md) — 2026-04-27, status: approved-for-plan — system architecture, agent SDK integration, metric definitions
3. [Plan](./05-plan.md) — 2026-04-27, status: draft — 5-phase TDD task list implemented to shipped state

## Status

Phase: **complete**. Plan executed across phases 1-5; script merged into master on 2026-05-03. Smoke tests pass on superclaude 4.5.1+ajitta / Python 3.13.7. See `src/superclaude/scripts/auto_improve/` for runtime code; `/sc:auto-improve` command for invocation.

## Migration Note

Promoted from standalone via `/sc:promote-feature auto-improve` on 2026-05-18 per doc-convention-v2 R4. Pre-promotion paths: `docs/specs/auto-improve-{discovery,design}-ajitta-2026-04-27.md`, `docs/plans/auto-improve-ajitta-2026-04-27.md`. Statuses preserved as-of original revision date.

External link warning: `src/superclaude/scripts/auto_improve/__init__.py:3` references the old design-spec path in a module docstring. Pre-existing comment, broken after migration — surface for separate fix.
