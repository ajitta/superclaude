---
feature: ultracode-sc-integration
phase: complete
owner: ajitta
created: 2026-06-27
updated: 2026-06-27
---

# Ultracode / Workflow / Goal-Driven Integration

Make `src/superclaude/` content compatible and integrated with the newly-added Claude Code harness execution features: the **ultracode** effort level (`xhigh` + dynamic workflow orchestration), the deterministic multi-subagent **Workflow** tool, and **goal-driven** loop/budget execution.

Thesis (from the upstream research): harness execution and SuperClaude governance are **orthogonal layers that compose** — SC content decides *whether and with what intent* to fan out; the Workflow tool *executes* the fan-out SC ships no runtime for. Integration encodes that split into the always-loaded core, the orchestration/token modes, and the doc-producing commands, and removes the `/sc:workflow` ↔ harness `Workflow` name collision by renaming the command to `/sc:roadmap`.

## Documents

- [02-research.md](./02-research.md) — compatibility research (orthogonal-layers thesis, conflict reconciliation, integration recipes a–f, recommendation 1–5). Generated 2026-06-05 by a 35-agent ultracode Workflow.
- [05-plan.md](./05-plan.md) — integration plan + applied-edit record (32 edits across 16 files; rename `/sc:workflow` → `/sc:roadmap`).
