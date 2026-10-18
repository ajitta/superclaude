---
feature: harness-checker-hygiene
phase: handoff
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Handoff — what remains after harness/checker hygiene

This round implements mode-retire handoff candidates 2 and 3 on fix/harness-checker-hygiene from master 19a17705. Integration tests and deterministic red-to-green evidence are in [01-verification.md](./01-verification.md). Independent code review passed, with its optional combined-attribute coverage suggestion incorporated. Implementation commits: 73d41ecb (harness retirement) and 4c0a2c24 (quoted attributes); intent: 5bff3e86. Headless behavioral sessions used: **0**; the owner imposed no ceiling. Merged into master at 0986f600. Development delivery targets origin/master; the existing local-scope install was synchronized, with no drift and doctor healthy. The installed RULES_DELEGATION.md also passes author-check with zero errors/warnings. No release was requested: stable and tag v4.29.1 remain at 96619c64. Remaining work is explicitly for a new session.

Post-merge audit (Fable 5.1, same day): one Low finding fixed and merged at ce0d148e — an opener with an unbalanced attribute quote is now reported on its own line through a second structural-scan alternative, `_STRUCT_RE` in author_check.py (`TAG_RE` unchanged); see [01-verification.md](./01-verification.md) §Candidate 3. The audit also found that candidate 1 below had gone stale; its row is updated to the current measurement. Master is at that audit commit plus this handoff update; still unreleased.

## Candidates

| # | Item | Kind of decision | Evidence | What it needs |
|---|---|---|---|---|
| 1 | `/sc:analyze --delegate` overflows the 8K budget and now drops RULES_DOCS.md — **regression shipped in v4.29.1** | Budget default change, injection order, or a ≥15-token wording trim (not a rule removal) | [mode-retire handoff](../mode-retire/02-handoff.md), item 1; [lean-round deferred evidence](../lean-round/03-deferred-evidence.md), section 7 (measured at 67215cd7, stale); current: `SUPERCLAUDE_PATH=src/superclaude superclaude context explain "/sc:analyze --delegate"` | The lean-round measurement (QUALITY 3,245 + DELEGATION 2,180 + DOCS 2,534 = 7,959 ≤ 8,000; INTERACTION ~282 dropped) no longer holds: mode-retire moved the Orchestration `pipeline()`/`parallel()` rule into RULES_DELEGATION.md (9f27b82d, +56 tokens), so the set is 8,015 and the loader drops RULES_DOCS.md (~2,534) instead, injecting RULES_INTERACTION. The old question ("do ~280 INTERACTION tokens matter?") is moot; the live question is which of the three options restores RULES_DOCS on a delegated analysis. Decide the option in chat first; a behavioral session is needed only if the owner wants the RULES_DOCS effect measured rather than restored. Not recorded in the mode-retire docs. |
| 2 | Multiline-first-root auto-format inference and multiline-tag N4 stripping | Bounded checker follow-up, not a regression from this round | src/superclaude/cli/author_check.py, infer_format and _sentences still process one line at a time; [verification](./01-verification.md) | Decide whether to expand support; reproduce both limits, preserve offsets and HTML-led Markdown handling, then add consumer-specific regressions. Note that the structural scan now iterates `_STRUCT_RE` (TAG_RE plus the unbalanced-quote opener alternative), while infer_format, the `closed` set and _sentences still use TAG_RE — any change to the tag grammar touches both. Model sessions not required. |

The prior finding_policy decision remains **keep, recorded**. This round's unlimited ceiling did not authorize reopening it; see [mode-retire decisions](../mode-retire/01-decisions.md), item 2.

## Compatibility note

New eval results omit tools_called and max_parallel_tool_calls; old results remain intact. Skill/shell checks and all seven hard gates remain. Consumers outside the repository that require the retired JSON fields must adjust; none are claimed verified here.

## Other leftovers

The prior lean-round small-leftover list and purpose-boundary frontmatter-yaml.safe_load test idea remain outside this round. See [mode-retire handoff](../mode-retire/02-handoff.md), small leftovers.

## Next-round start

Check git state and delivery status before relying on this branch. Read the candidates, select numbers and a session policy in chat, then compose and independently review the next plan. A new session does not inherit execution authorization from this round.
