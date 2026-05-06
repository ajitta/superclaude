---
paths: ["src/superclaude/**", ".claude/rules/**", "scripts/**"]
---

# Project Gotchas — Authoring
# Last reviewed: 2026-05-06
# Content-framework authoring traps (agents/commands/skills/modes/core).

- install-tree-boundary: Files outside `src/superclaude/` (e.g., `.claude/rules/schemas.yaml`, `tests/`, repo-root docs) are NOT shipped to `~/.claude/` at install. If installed content links to them, it breaks on user machines. Keep installed content self-contained or copy needed refs into `src/superclaude/`.
- dynamic-vs-static-load: `core/BUSINESS_SYMBOLS.md` is NOT always-loaded — it is injected on-demand by `src/superclaude/scripts/context_loader.py` TRIGGER_MAP. Always-loaded core files are the three in `CLAUDE_SC.md` @import chain (FLAGS/PRINCIPLES/RULES). Check `context_loader.py` before asserting load mode.
- agent-desc-halluc-trigger: agent description wording that implies prior practice (`following X practices`, `deep production experience`, `pragmatic tradeoff judgment`) primes context-hallucination on long-output tasks — measured 5/5 and 3/3 hallucination rates on pytest-writing (claims of preexisting files, prior fixes, even narrating self-edits). Forward-looking phrasing (`learning`, `applying`, `grounded in`) did not trigger it. Source: `docs/research/2026-05-06-agent-naming-findings/`.
- description-as-overeng-lever: adding a Zen-of-Python clause ("simple is better than complex; values minimal solutions; code that any junior can read") to an agent description reduced over-engineering signals 25–73% with the same name and body. Lower-cost intervention than renaming an agent. Caveat: `hypothesis`-style advanced patterns only dropped ~20% — soft directives don't fully suppress them. Source: same as above.
