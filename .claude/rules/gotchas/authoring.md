# Project Gotchas — Authoring
# Last reviewed: 2026-04-16
# paths: ["src/superclaude/**", ".claude/rules/**", "scripts/**"]
# Content-framework authoring traps (agents/commands/skills/modes/core).

- install-tree-boundary: Files outside `src/superclaude/` (e.g., `.claude/rules/schemas.yaml`, `tests/`, repo-root docs) are NOT shipped to `~/.claude/` at install. If installed content links to them, it breaks on user machines. Keep installed content self-contained or copy needed refs into `src/superclaude/`.
- dynamic-vs-static-load: `core/BUSINESS_SYMBOLS.md` is NOT always-loaded — it is injected on-demand by `src/superclaude/scripts/context_loader.py` TRIGGER_MAP. Always-loaded core files are the three in `CLAUDE_SC.md` @import chain (FLAGS/PRINCIPLES/RULES). Check `context_loader.py` before asserting load mode.
