---
feature: mode-retire
phase: handoff
owner: ajitta
created: 2026-10-18
updated: 2026-10-19
---

# 02. Handoff — what the next round starts from

State at handoff: `master` = `stable` = `v4.29.1` (`96619c64`), CI green, local-scope install synced with no drift (the two retired mode files pruned). Headless sessions used: **4** — cap 0 for the work itself, then `make canary-gates` (7/7) when the owner asked for merge + push + release in chat. A new round needs its own cap.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | `RULES_QUALITY.md` vs the 8K budget on `/sc:analyze --delegate` | rule removal or budget default change | [lean-round 03 §7](../lean-round/03-deferred-evidence.md) | whether ~280 tokens of `RULES_INTERACTION` change a `--delegate` analysis — low discriminability; the alternative is a code change to the default budget (no session) |
| 2 | `tool_called` / `parallel_tool_calls_min` check types | harness hygiene | [01 §Item 4](./01-decisions.md) | zero tasks use them after this round; remove when a round touches the harness and they are still unused |
| 3 | `author-check` X2 false positive on an attribute that contains `<…>` | checker fix | [01 §Verification](./01-decisions.md): `RULES_DELEGATION.md:63` at `40746786` | a regression test with a `note="… <tag>"` attribute; code-only |

Closed this round, not to reopen without a session budget: `<finding_policy>` ×3 (keep, [01 §Item 2](./01-decisions.md)).

## Small leftovers deliberately not done

The lean round's list stands (`frozenset` rewrites, Makefile help from `##` comments, CI `curl | sh` → `setup-uv`, `tests/unit/scripts` exclusion, in-function test imports) plus the purpose-boundary round's frontmatter-`yaml.safe_load` test idea.

## How a new session starts a round

Same as [purpose-boundary 03-handoff](../purpose-boundary/03-handoff.md) §"How a new session starts a round": state check → read this file → candidate table and a recommendation → split (measure / cleanup / decide-only / defer) and a session cap → plan per the maintenance skill → kickoff on the owner's word.
