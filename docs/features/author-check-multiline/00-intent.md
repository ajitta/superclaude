---
feature: author-check-multiline
phase: intent
status: approved-for-plan
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — author-check multiline consumers and release 4.29.2

## Original request

After the context-budget-restore round was merged, pushed and synced:

> 머지 푸시 설치동기화하고 , 다음라운드 준비해줘

Candidate table presented in chat (1 author-check multiline consumers, 2 stacked-mode budget residual, 3 lean-round small leftovers, 4 frontmatter yaml.safe_load test idea, 5 release 4.29.2); recommendation 1 + 5, session cap 0:

> 권고대로 진행

Reviewed plan v2 (release scope/version and start):

> Q1. 권고대로, q2 시작

## Problem

`superclaude author-check` tokenizes tags with a quote-aware, multiline-capable grammar (`TAG_RE`, widened in harness-checker-hygiene) for its structural scan, but two consumers still work one line at a time: automatic format inference matches only the first content *line*, and N4 sentence extraction strips tags per line. A file whose first root opener spans lines is checked as Markdown and its unclosed tags go unreported; prose after a multiline opener is read with the opener's tail glued on, so duplicate sentences are missed. Both are silent clean results. The shipped corpus has no multiline openers; the defect reaches users of the CLI on their own files. Separately, `[Unreleased]` holds the harness retirement, the author-check quote fix and the context-budget regression fix, none released.

## Desired outcome

Both consumers agree with the structural scan: a multiline span is a tag when it starts a line and its continuation lines are attributes, and otherwise is prose — so Markdown angle-bracket terms are not swallowed. Deterministic tests pin the four fixed cases and three controls, the corpus test asserts the auto-inferred format, and a whole-tree before/after diff over every tracked `*.md` is empty. Then 4.29.2 ships the accumulated fixes.

## Affected users and systems

- `superclaude author-check` users with multiline openers in their own instruction files: unclosed tags and duplicate sentences are now reported.
- Shipped content: no finding changes (0 multiline openers; whole-tree diff gate).
- Release 4.29.2: GitHub release, `stable` moves, local-scope install re-synced. It carries the loader default budget change (8,000 → 12,000) measured deterministically in context-budget-restore; no canary gate is triggered (`core/`, `hooks.json` unchanged since v4.29.1) and none is run — an explicit decision at 0 sessions.

## Constraints and decisions

| Topic | Approved decision |
|---|---|
| Scope | Candidates 1 and 5 only; lean-round small leftovers and the yaml.safe_load test idea stay separate; the stacked-mode budget residual is deferred |
| Checker boundary | `TAG_RE`, `_STRUCT_RE`, the X1/X2 scan, `is_placeholder`, capture groups and line offsets unchanged; one helper plus the two consumers; no strict XML parser, no new rule codes |
| Placement rule | A multiline match is a tag only when it begins a line and every continuation line is attribute-shaped or a bare closer — the structural scan's block-element rule applied to both consumers |
| Branch | fix/author-check-multiline from master 02f31d7b; release via chore/version-4.29.2 |
| Sessions | 0; deterministic tests and the whole-tree diff are the oracle |
| Version | 4.29.2 (patch) by the 4.29.1 precedent (a patch that carried a Removed section); `[Unreleased]` holds Removed (dev-only eval checks) + Fixed ×3 |
| Delivery | One commit per phase; merge + push (Phase 3) and release (Phase 4) authorized by the plan's acceptance, each gated on a green full suite |

## Open questions

None blocking. Stop and report any concurrent edit to author_check.py or its tests, or a stray `.gitignore` edit before `make release`.

## Plan and review

Local working plan: .hermes/plans/2026-10-19_022000-author-check-multiline.md (reviewed v2; v1 beside it). The review added the placement rule, the Markdown-prose control, the corpus auto-format assertion, the whole-tree diff gate and the explicit no-canary decision; this committed intent preserves those decisions independently of the local plan.
