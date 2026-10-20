---
feature: agent-roster-audit
phase: implemented
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
---

# Agent roster audit

The owner asked which subagents had lost their reason to exist, given that agents defined by an identity ("python expert", "system architect") are going out of use, and how Anthropic builds them now. The audit kept 5 of 24 agents and retired 19. Owner ruling: every ★ option (1-a, 2-a, 3-a, 4-a), 2026-10-20.

## Status

Implemented on branch `feature/agent-roster-audit` (base `f467012c`). Next: independent verification, merge, minor release with `make canary-gates` (`core/rules/RULES_QUALITY.md` changed).

## Documents

| File | Content |
|---|---|
| [00-intent.md](./00-intent.md) | Request, Anthropic's current guidance, the test applied, the per-agent verdicts, decisions |
| [01-carry-over.md](./01-carry-over.md) | For each retired agent: what was still load-bearing and where it lives now; what changed in commands, rules, tests and the upgrade path |
