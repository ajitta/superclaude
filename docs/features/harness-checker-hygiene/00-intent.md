---
feature: harness-checker-hygiene
phase: intent
status: approved-for-plan
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — harness and checker hygiene

## Original request

> superclaude 다음 라운드 시작 — docs/features/mode-retire/02-handoff.md 읽고 후보 중 [번호]로 계획 구성·리뷰 후 제시. 세션 상한 [N].

Selection:

> Q1. 2.3번,
> Q2. 세션 상한을 두지 않는다. 가능한한 병렬 처리.

Approval of the reviewed implementation plan, branch, documentation location and per-batch commits:

> Q1. 권고대로 승인

## Problem

The mode-retire round left two eval check types with no current task consumer, and recorded an author-check X2 false positive when a quoted attribute contains an angle-bracket reference. The latter reproduces on RULES_DELEGATION.md without any defect in that document.

## Desired outcome

Close handoff candidates 2 and 3 with deterministic regression evidence: remove the unused checks and their exclusive support; recognize quoted attribute contents as opaque while preserving true structure errors. Keep purpose-inference instructions and delivered content unchanged.

## Affected users and systems

- Eval harness maintainers: two check types and two fields in newly generated results.json retire.
- author-check users: quoted angle brackets no longer cause false X2 reports.
- Existing result files, behavioral measurements, task definitions, hard gates and user installations remain untouched.

## Constraints and decisions

| Topic | Approved decision |
|---|---|
| Scope | mode-retire candidates 2 and 3 only; candidate 1 remains deferred |
| Branch | fix/harness-checker-hygiene, from master 19a17705; origin/master ahead/behind 0/0 at kickoff |
| Parallelism | Separate harness and checker workers on disjoint allowlists; parent owns shared docs, review, staging and commits |
| Sessions | No ceiling; deterministic tests are the oracle, so no headless behavioral sessions planned |
| Compatibility | New results omit tools_called and max_parallel_tool_calls; disclose the change rather than emitting misleading empty measurements |
| Checker boundary | Preserve four TAG_RE capture groups, placeholders, code/comment masking and real mismatch line numbers; no strict XML parser or new dependency |
| Existing limits | Multiline-first-root automatic format inference and multiline-tag N4 normalization remain deferred; multiline whole-body structural checking is in scope |
| Delivery | Per-batch commits on the feature branch; merge, push, release and install sync require separate instructions |

## Open questions

No implementation-blocking decision remains. External result readers outside this repository are unknown. Stop and report any new live consumer or overlapping concurrent edit rather than broadening the approved scope.

## Plan and review

The local working plan is .hermes/plans/2026-10-19_003153-harness-checker-hygiene.md (reviewed v2, approval recorded). Its review required explicit multiline limits, report-write/readback schema coverage and an automatic regression for the actual triggering document. This committed intent preserves those decisions independently of the local plan.
