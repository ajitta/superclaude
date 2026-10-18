---
feature: mode-retire
phase: handoff
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 02. Handoff — what the next round starts from

State at handoff: branch `fix/mode-retire` on base `40746786` (`master` = `stable` = `v4.29.0` + one docs commit), three commits, full suite green. Headless sessions used: **0** (cap 0). Not merged, not released: `core/FLAGS.md` and `core/rules/RULES_DELEGATION.md` changed, so `make release` demands `make canary-gates` (4 sessions) first — the round ends at the merge the owner requests; the release goes with the next round that has a cap. At release the `CHANGELOG.md` `[Unreleased]` block becomes `[4.29.1] - <date>` (Q7).

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

Same as [purpose-boundary 03-handoff](../purpose-boundary/03-handoff.md) §"How a new session starts a round": state check → read this file → candidate table and a recommendation → split (measure / cleanup / decide-only / defer) and a session cap → plan per the maintenance skill → kickoff on the owner's word. If this branch is still unmerged, merge it first (full suite, `--no-ff`), then run the post-merge local-scope reinstall (`superclaude install --force --scope local`, `superclaude verify-drift --scope local`) so the two retired modes stop injecting in in-repo sessions.
