# SuperClaude Core

Framework DNA — always-on principles + rules define SuperClaude identity.

## Content Delivery

Core files load via `CLAUDE_SC.md` `@import` at session start. Present in **every** Claude Code session where SuperClaude installed.

**Exceptions (on-demand, injected by `context_loader.py`):** `rules/` modules load when their domain triggers (implement/review work, delegation, doc production, /sc: commands); BUSINESS_SYMBOLS.md loads when business-symbol / panel-example / `--structured` patterns match.

## Files

| File | Role | Delivery |
|------|------|----------|
| FLAGS.md | Behavioral flags, mode triggers, MCP routing, execution + output flags | Always loaded |
| PRINCIPLES.md | Software engineering principles and decision frameworks | Always loaded |
| RULES.md | ~0.9k-token behavioral kernel (scope, verification, destructive-op, project-rules-priority) + on-demand module map | Always loaded |
| rules/RULES_QUALITY.md | R01–R21 detail + examples, verification_ladder, anti_over_engineering, checklist_scaling, thresholds | On-demand |
| rules/RULES_DELEGATION.md | sub_agent_decision, delegate packet, agent_routing, workflow fan-out rules | On-demand |
| rules/RULES_DOCS.md | doc_output_convention, workflow_gates | On-demand |
| rules/RULES_INTERACTION.md | selection_protocol | On-demand |
| BUSINESS_SYMBOLS.md | Symbol system for business strategy multi-expert panel | On-demand |

The kernel/module split (roadmap Phase 2-1) is measurement-gated: the evals/ 4×7 matrix showed kernel-only parity with the full monolith before any prose moved.

## Authoring

Framework devs only maintain core files. Edits to always-loaded files hit context budget every session — keep terse.

- `CLAUDE_SC.md` chains: `@core/FLAGS.md` → `@core/PRINCIPLES.md` → `@core/RULES.md`
- `rules/` modules + BUSINESS_SYMBOLS.md fire via `context_loader.py` TRIGGER_MAP; drift guards in `tests/unit/test_context_loader.py` (`TestCoreLiteSplit`) enforce kernel token budget and module↔routing sync

## Related

- `CLAUDE_SC.md` — Import chain entry
- `modes/` — On-demand cognitive overlays (pair with core rules)
- `scripts/context_loader.py` — On-demand delivery mechanism
