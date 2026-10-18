---
feature: lean-round
phase: handoff
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 06. Handoff — what the next round starts from

State at handoff: `master` = `stable` = `v4.28.2` (`8cb16daa`), CI green, local-scope install synced with no drift. The lean round is closed: plan `.hermes/plans/2026-10-18_001500-lean-round.md` (v3, local to the machine), batches in [04-batches.md](./04-batches.md), gate and spot check in [05-release-gate.md](./05-release-gate.md). Headless budget of this round: 35/40 used; a new round needs its own cap.

## Candidates, each with its evidence already written

| # | Item | Kind of decision | Evidence | Measurement it would need |
|---|---|---|---|---|
| 1 | `commands/sc.md` deletion | public routing change | [03 §1](./03-deferred-evidence.md) | how often `/sc:sc` or bare `/sc` is typed — no source for it exists in the repo |
| 2 | `MODE_Orchestration.md`, `MODE_Task_Management.md` deletion | public routing change | [03 §2](./03-deferred-evidence.md) | a fixture where `--orchestrate` / `--task-manage` changes behavior; none exists |
| 3 | `mcp/*.md` body shrink, `RESEARCH_CONFIG.md` deletion | documented manual-load paths (5 live references) | [03 §3](./03-deferred-evidence.md) | whether `--verbose-context` and the manual paths are used |
| 4 | `<finding_policy>` ×3 → one place | delivery to native subagents unproven | [03 §4](./03-deferred-evidence.md) | trace what a `delegate_packet` actually carries into an auto-delegated agent |
| 5 | `/sc:init` ↔ `project-initializer` | authorization axes differ (13-axis table done) | [03 §5](./03-deferred-evidence.md) | none — a design decision |
| 6 | `RULES_QUALITY.md` vs the 8K budget on `/sc:analyze --delegate` | rule removal, not dedup | [03 §7](./03-deferred-evidence.md) | does `RULES_INTERACTION` (~280 tokens) change a `--delegate` analysis |
| 7 | `purpose_before_action`: fix-vs-propose boundary | kernel rule wording | [05](./05-release-gate.md) — `action-vs-purpose-code` 6/15 on the shipped kernel, pilot 5/6 | sc-full vs sc-candidate on the code task with a candidate wording that names config/env files the error points at; §10 of the maintenance skill's planning reference has the arm procedure |
| 8 | `memory_guide` header (04b #9), `<role>`/`<does>` overlap (04b #14) | spec change: tests + authoring rules pin both | [04](./04-batches.md) B4 skipped list | none — decide whether the spec changes |
| 9 | `.gitignore` 19 duplicate entries, `.black/` | pure cleanup | 04a #11 (`04-ponytail-audit-1.md`) | none; the other session's edit has landed (shipped in the 4.28.2 bump), so the file is free |

Item 7 belongs to the reframing-anchoring axis (the owner's stated purpose), not to lean; it is the one with a measured gap behind it.

## Small leftovers deliberately not done

`frozenset("…".split())` rewrites (cosmetic); Makefile help generated from `##` comments; CI `curl | sh` → `astral-sh/setup-uv` and the repeated addopts in `test.yml`; `tests/unit/scripts` default exclusion (the native crash was not re-investigated; 140 tests pass in a separate process); 198 in-function `superclaude.*` imports in tests whose module is not imported at the top.

## How a new session starts a round

1. `git fetch`, confirm `master` = `origin/master`, `git status` clean except untracked `.hermes/`, `.ignore`.
2. Read this file, then only the evidence sections for the items the owner picks.
3. Plan per the maintenance skill's `references/audit-planning.md`: readings table if the request is ambiguous, numbered decisions in chat (never a form), a session cap, one independent reviewer pass, then v2.
4. Kickoff only on the owner's word: branch (`feature/<slug>` when a rule or arm is added, `fix/` otherwise), `docs/features/<slug>/00-intent.md` in the owner's words, decisions as a table at the top of the plan.
5. Commit per batch by explicit path; `.gitignore` is now clean, but keep staging by name.

## Lessons recorded this round (in the Hermes skill `superclaude-repo-maintenance`)

Parallel subagents on one tree with disjoint file allowlists; no `sys.platform` faking in tests (CI is Linux); stage by name, never `git add -u`; kernel re-measure in decoded chars/4 with the import stub excluded; Claude Code's project-folder encoder is `[^A-Za-z0-9]` → `-` (verified against the CLI binary).
