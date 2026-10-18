---
feature: context-budget-restore
phase: intent
status: approved-for-plan
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — context budget restore

## Original request

> superclaude 다음 라운드 시작 — docs/features/harness-checker-hygiene/02-handoff.md 읽고 후보 중 [번호]로 계획 구성·리뷰 후 제시. 세션 상한 [N].
>
> 시작 전 확인: git 상태(master == origin/master d995aa1a, 작업 트리 clean), 핸드오프의 후보 1 측정치를 `SUPERCLAUDE_PATH=src/superclaude uv run superclaude context explain "/sc:analyze --delegate"` 로 현재 트리와 다시 대조. 후보 1은 v4.29.1에 배포된 회귀(RULES_DOCS 탈락, 초과 15토큰)이므로 복구 방식(예산 기본값 / 주입 순서 / ≥15토큰 문구 압축, 규칙 삭제 아님)을 Q1로 채팅에서 먼저 결정하고, 행동 세션은 RULES_DOCS 효과를 "측정"하기로 할 때만 쓴다. … 머지·푸시·릴리스는 별도 지시 전까지 금지.

Selection and decisions, in chat:

> Q1. 권고대로 진행한다. (budget default raise + regression test; injection-order change rejected; no wording trim)
> Q2. 1만, (candidate 1 only)
> Q3. 권고대로 (0 headless sessions)

Budget value, after the multi-flag measurement in the plan was shown:

> 12,000이면 테스트한 모든 조합이 ≥1,500 여유로 들어감 이러면 12000으로 하자

Start of the reviewed plan:

> 시작

## Problem

`/sc:analyze --delegate` matches three priority-1 rule modules whose estimated size is 8,015 tokens against the loader's 8,000-token default budget, so `core/rules/RULES_DOCS.md` is dropped and `RULES_INTERACTION.md` (282 tokens, priority 2) fills the remainder. The overflow was introduced by mode-retire `9f27b82d` (+56 tokens in `RULES_DELEGATION.md`) and shipped in v4.29.1. The default was never a measured contract: the only rationale on record is a `# ~8K tokens` comment, and the same number is duplicated as a literal in `superclaude context explain`.

## Desired outcome

Every priority-1 rule module a `/sc:` prompt triggers is injected again, with headroom for ordinary rule edits, and a deterministic test fails before the next edit can silently change which module the budget drops. No rule text is removed or reworded; the behavioral effect of `RULES_DOCS.md` is not measured.

## Affected users and systems

- Every installed SuperClaude prompt hook: the default `CLAUDE_CONTEXT_MAX_TOKENS` becomes 12,000; the env override keeps working.
- `superclaude context explain`: reports the same default from one shared constant.
- Busy prompts inject up to ~4K more tokens once per session per file; the always-loaded kernel is unchanged.
- Installed copies: the hook command resolves through the editable uv tool, so the code fix is live without `superclaude install`; no content file changes.

## Constraints and decisions

| Topic | Approved decision |
|---|---|
| Scope | harness-checker-hygiene handoff candidate 1 only; candidate 2 (author_check multiline) carried untouched |
| Restore option | Default budget raise to 12,000 plus regression and drift-guard tests; injection order unchanged; no wording trim; no rule removal |
| Branch | fix/context-budget-default, from master d995aa1a; origin/master ahead/behind 0/0 at kickoff |
| Sessions | 0 headless sessions; deterministic tests are the oracle; the lean-round §7 "cost of a larger budget" question is closed by decision, not measurement |
| Residual | Prompts stacking three or more mode flags with `--delegate` can still exceed 12,000; they lose `RULES_INTERACTION.md` (priority 2) first, never a priority-1 module; recorded in the handoff |
| Release gate | `src/superclaude/core/` untouched, so no canary gate is triggered; release not requested |
| Delivery | One commit per phase on the feature branch; merge, push, release and install sync require separate instructions |

## Open questions

None blocking. Stop and report any concurrent edit to `context_loader.py`, `cli/main.py` or the two test files rather than merging around it.

## Plan and review

The local working plan is .hermes/plans/2026-10-19_014500-context-budget-restore.md (reviewed v2; v1 kept beside it). The review added the stacked-mode residual, the routed-modes-only drift guard, the `env_unset` helper parameter and the CHANGELOG placement; this committed intent preserves those decisions independently of the local plan.
