---
feature: harness-checker-hygiene
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Handoff — what remains after harness/checker hygiene

This round implements mode-retire handoff candidates 2 and 3 on fix/harness-checker-hygiene from master 19a17705. Integration tests and deterministic red-to-green evidence are in [01-verification.md](./01-verification.md). Independent code review passed, with its optional combined-attribute coverage suggestion incorporated. Implementation commits: 73d41ecb (harness retirement) and 4c0a2c24 (quoted attributes); intent: 5bff3e86. Headless behavioral sessions used: **0**; the owner imposed no ceiling. Not merged, pushed or released; no installation changed.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | RULES_QUALITY.md vs the 8K budget on /sc:analyze --delegate | Rule removal or budget default change | [mode-retire handoff](../mode-retire/02-handoff.md), item 1; [lean-round deferred evidence](../lean-round/03-deferred-evidence.md), section 7 | Whether approximately 280 tokens of RULES_INTERACTION affect delegated analysis; low discriminability. The alternative is a code change to the default budget. No rule deletion without measurement. |
| 2 | Multiline-first-root auto-format inference and multiline-tag N4 stripping | Bounded checker follow-up, not a regression from this round | src/superclaude/cli/author_check.py, infer_format and _sentences still process one line at a time; [verification](./01-verification.md) | Decide whether to expand support; reproduce both limits, preserve offsets and HTML-led Markdown handling, then add consumer-specific regressions. Model sessions not required. |

The prior finding_policy decision remains **keep, recorded**. This round's unlimited ceiling did not authorize reopening it; see [mode-retire decisions](../mode-retire/01-decisions.md), item 2.

## Compatibility note

New eval results omit tools_called and max_parallel_tool_calls; old results remain intact. Skill/shell checks and all seven hard gates remain. Consumers outside the repository that require the retired JSON fields must adjust; none are claimed verified here.

## Other leftovers

The prior lean-round small-leftover list and purpose-boundary frontmatter-yaml.safe_load test idea remain outside this round. See [mode-retire handoff](../mode-retire/02-handoff.md), small leftovers.

## Next-round start

Check git state and delivery status before relying on this branch. Read the candidates, select numbers and a session policy in chat, then compose and independently review the next plan. A new session does not inherit execution authorization from this round.
