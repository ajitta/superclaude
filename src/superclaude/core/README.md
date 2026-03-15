# SuperClaude Core

Framework DNA — always-applied principles and rules that define SuperClaude's identity.

## Content Delivery

Core files are loaded via `CLAUDE_SC.md` `@import` at session start. They are present in **every** Claude Code session where SuperClaude is installed.

**Exception:** BUSINESS_SYMBOLS.md is loaded on-demand by `context_loader.py` when business-panel mode/agent activates.

## Files

| File | Role | Delivery |
|------|------|----------|
| FLAGS.md | Behavioral flags, mode triggers, MCP routing, model assignments | Always loaded |
| PRINCIPLES.md | Software engineering principles and decision frameworks | Always loaded |
| RULES.md | Behavioral guardrails, priority system, anti-over-engineering rules | Always loaded |
| BUSINESS_SYMBOLS.md | Symbol system for business strategy multi-expert panel | On-demand |

## Authoring

Core files are maintained by framework developers only. Changes to always-loaded files directly impact context budget for every session — keep them concise.

- `CLAUDE_SC.md` chains: `@core/FLAGS.md` → `@core/PRINCIPLES.md` → `@core/RULES.md`
- BUSINESS_SYMBOLS.md is triggered via `context_loader.py` TRIGGER_MAP

## Related

- `CLAUDE_SC.md` — Import chain entry point
- `modes/` — On-demand cognitive overlays (complement core rules)
- `scripts/context_loader.py` — On-demand delivery mechanism
