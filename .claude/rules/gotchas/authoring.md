---
paths: ["src/superclaude/**", ".claude/rules/**", "scripts/**"]
---

# Project Gotchas — Authoring
# Last reviewed: 2026-05-06
# Content-framework authoring traps (agents/commands/skills/modes/core).

- install-tree-boundary: Files outside `src/superclaude/` (e.g., `.claude/rules/schemas.yaml`, `tests/`, repo-root docs) NOT shipped to `~/.claude/` at install. Installed content link to them → break on user machine. Keep installed content self-contained or copy needed refs into `src/superclaude/`.
- dynamic-vs-static-load: `core/BUSINESS_SYMBOLS.md` NOT always-loaded — injected on-demand by `src/superclaude/scripts/context_loader.py` TRIGGER_MAP. Always-loaded core files = three in `CLAUDE_SC.md` @import chain (FLAGS/PRINCIPLES/RULES). Check `context_loader.py` before assert load mode.
- agent-desc-halluc-trigger: agent description wording implying prior practice (`following X practices`, `deep production experience`, `pragmatic tradeoff judgment`) primes context-hallucination on long-output tasks — measured 5/5 and 3/3 hallucination rates on pytest-writing (claim preexisting files, prior fixes, even narrate self-edits). Forward-looking phrasing (`learning`, `applying`, `grounded in`) no trigger. Source: `docs/research/2026-05-06-agent-naming-findings/`.
- description-as-overeng-lever: add Zen-of-Python clause ("simple is better than complex; values minimal solutions; code that any junior can read") to agent description cut over-engineering signals 25–73% with same name and body. Lower-cost than renaming agent. Caveat: `hypothesis`-style advanced patterns only drop ~20% — soft directive no fully suppress. Source: same as above.