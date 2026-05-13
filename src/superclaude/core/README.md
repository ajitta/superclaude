# SuperClaude Core

Framework DNA — always-on principles + rules define SuperClaude identity.

## Content Delivery

Core files load via `CLAUDE_SC.md` `@import` at session start. Present in **every** Claude Code session where SuperClaude installed.

**Exception:** BUSINESS_SYMBOLS.md load on-demand by `context_loader.py` when business-panel mode/agent fire.

## Files

| File | Role | Delivery |
|------|------|----------|
| FLAGS.md | Behavioral flags, mode triggers, MCP routing, model assignments | Always loaded |
| PRINCIPLES.md | Software engineering principles and decision frameworks | Always loaded |
| RULES.md | Behavioral guardrails, priority system, anti-over-engineering rules | Always loaded |
| BUSINESS_SYMBOLS.md | Symbol system for business strategy multi-expert panel | On-demand |

## Authoring

Framework devs only maintain core files. Edits to always-loaded files hit context budget every session — keep terse.

- `CLAUDE_SC.md` chains: `@core/FLAGS.md` → `@core/PRINCIPLES.md` → `@core/RULES.md`
- BUSINESS_SYMBOLS.md fire via `context_loader.py` TRIGGER_MAP

## Related

- `CLAUDE_SC.md` — Import chain entry
- `modes/` — On-demand cognitive overlays (pair with core rules)
- `scripts/context_loader.py` — On-demand delivery mechanism