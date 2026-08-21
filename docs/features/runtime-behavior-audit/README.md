---
feature: runtime-behavior-audit
phase: planning
owner: chosh1179
created: 2026-08-21
updated: 2026-08-22
---

# Runtime Behavior Audit

An evidence-based review of how SuperClaude actually behaves in daily use, derived from
the Claude Code logs and history under `~/.claude/`, plus live probes of every installed
hook. The audit was requested to find improvement targets; it produced one structural
finding (adoption collapsed to near zero in May 2026) and nine supporting defects.

## Scope of evidence

| Source | Volume | Window |
|---|---|---|
| `~/.claude/history.jsonl` (typed prompts) | 14,596 entries | 2025-10-15 → 2026-08-21 |
| `~/.claude/projects/**/*.jsonl` (session transcripts) | 1,331 files, 1.1 GB | 2026-07-22 → 2026-08-21 |
| `~/.claude/.superclaude_hooks/`, `./.claude/.superclaude_hooks/` | runtime state | 2026-03-21 → 2026-08-21 |
| Live hook probes | 11 installed hook commands | 2026-08-21 |

Claude Code rotates transcripts, so anything derived from them covers the last 30 days
only. Prompt history covers the full 10 months.

## Documents

- [03-analysis.md](./03-analysis.md) — findings A1–A12 with evidence and reproduction
- [05-plan.md](./05-plan.md) — prioritized remediation plan with verification commands
- [05a-plan-trigger-tiers.md](./05a-plan-trigger-tiers.md) — Task 8 detail: per-command auto-trigger classification
- [06-diagnostics.md](./06-diagnostics.md) — Phase 1 results: why commands and agents never fire, with live probes

## Headline

`/sc:` commands were 30–47% of all typed prompts from October 2025 through March 2026.
They fell to 10.4% in April, 0% in May, and have totalled **9 invocations since June 1**
against 2,469 prompts. In the same window user-scope plugin tooling (claude-mem, caveman,
karpathy-skills) and native Claude Code controls (`/goal`, `/effort`) took over the roles
SuperClaude was built for. The framework is currently installed in two repositories and
in neither user scope nor as a plugin.

The plan therefore opens with a distribution decision, because every other fix is only
worth doing on the assumption the framework is meant to keep being used.

## Decisions

Taken 2026-08-21.

| # | Decision | Effect on this plan |
|---|---|---|
| D1 | **Ship it** — package as a Claude Code plugin, keep the CLI | All six phases apply; Phase 6 is the destination |
| D2 | The May 2026 collapse happened **because auto-trigger never worked** | Phase 1 is now the root-cause diagnostic, not a gate for subtraction |
| D3 | The insight pipeline is **repaired, not retired** | Task 11 gives `INSIGHT:` a real producer instead of deleting the subsystem |
| D4 | Orphan state in `~/.claude/.superclaude_hooks/` may be deleted | Done — 32 files removed 2026-08-21, backup kept |
| D5 | `--parallel` is **not** restored | Task 7 takes the notice route; the one-canonical-name rule stands |
| D6 | Caveman mode stays as-is | Out of scope for this plan |

D2 is the user's answer, not a measurement — the logs show 22 commands carry auto-triggerable
wording and none fired in thirty days (A12), but cannot say why the user stopped typing. Recording
it as a decision keeps the provenance clear and makes Phase 1 the item everything depends on.
