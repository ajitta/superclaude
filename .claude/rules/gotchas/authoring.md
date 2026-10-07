---
paths: ["src/superclaude/**", ".claude/rules/**", "scripts/**"]
---

# Project Gotchas — Authoring
# Last reviewed: 2026-10-07
# Content-framework authoring traps (agents/commands/modes/core).

- install-tree-boundary: Files outside `src/superclaude/` (`.claude/rules/schemas.yaml`, `tests/`, repo-root docs) are not shipped to `~/.claude/`; installed content that links them breaks on user machines. Keep installed content self-contained or copy the ref into `src/superclaude/`.
- dynamic-vs-static-load: `core/BUSINESS_SYMBOLS.md` + `core/rules/RULES_*.md` load on-demand via `src/superclaude/scripts/context_loader.py` TRIGGER_MAP. Always-loaded = FLAGS/PRINCIPLES/RULES (`CLAUDE_SC.md` chain); RULES.md is the kernel, R01-R21 detail lives in the modules. Check it before asserting load mode.
- agent-desc-halluc-trigger: Wording implying prior practice (`following X practices`, `deep production experience`) primes hallucination on long-output tasks (5/5 on pytest-writing). Forward-looking (`learning`, `applying`, `grounded in`) does not. Source: `docs/research/2026-05-06-agent-naming-findings/`.
- description-as-overeng-lever: Zen-of-Python clause in the description ("simple is better than complex; values minimal solutions; code that any junior can read") cuts over-engineering 25–73% with same name and body — cheaper than renaming. Soft: `hypothesis`-style patterns drop only ~20%. Source: same as above.
- rule-before-recommend: Read the `*-authoring.md` BEFORE recommending a content change, not at execution: a decorative-looking tag may be a spec'd slot (`<outcomes>`, mode-authoring.md), the obvious new home forbidden (mcp-authoring.md: no setup blocks in `MCP_*.md`). 2026-07-25: 2 of 5 recommendations misplaced.
- probe-observer-effect: `claude -p` probed in-repo reads spec/plan docs and complies, so an uninstalled rule looks live; probe from home dir for A/B. Passive rules (R21) fire conditionally; user-invoked markers (`--introspect`) fire 100%. Source: `docs/research/agent-native-design-ajitta-2026-05-31.md` § P-R21.
- demand-capability-mismatch: A section demanding facts `<tools>` cannot read leaves memory as source → confabulation, a spec defect (2026-09-09 `/sc:prompt`: 4 fabricated repo facts). Fix: grant the read tool + read-or-`[FILL:]`, no third source, or drop the demand. Audit each tool's consumer and each demand's tool.
