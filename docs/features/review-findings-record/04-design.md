---
status: draft
revised: 2026-10-22
---

# 리뷰 발견과 그 수락의 기록 위치

출처: [review-reflect-gate-gap](../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md) 항목 E, [plan-complete-order 06e](../plan-complete-order/06e-verify-round6.md) "이 브랜치 밖". 이 문서는 설계안이다. 소유자가 안을 고른 뒤에 계획을 쓴다. 이 round에서는 `src/`를 바꾸지 않는다.

## 결론

`/sc:reflect` Plan-Close 조건 (3)은 리뷰 발견과 그 처리 상태를 근거로 삼는다. 그런데 계획으로 진행한 코드 리뷰는 그 근거를 어디에도 남기지 않는다. 기록이 없으면 지금의 reflect가 잘못 닫지는 않는다. 기준선 5/5에서 "조건 (3)을 확인할 수 없다"고 말하고 사용자에게 물었다. 남은 문제는 다른 세션에서 Plan-Close를 할 때마다 사용자가 리뷰 내용을 기억해서 답하거나 이미 끝난 리뷰를 다시 돌려야 한다는 점이다. 또 프로브 fixture는 shipped 명령이 쓰지 않는 `06-review.md`를 근거로 쓴다. 권고는 ★B다. 스펙 게이트가 이미 하는 것처럼, `/sc:review`가 계획 파일의 `## Review Log` 절에 round마다 몇 줄을 남긴다.

## 문제: 무엇이 쓰고 무엇이 읽나

조건 (3)(`src/superclaude/commands/reflect.md:19`)은 "every Critical or Important review finding is fixed or accepted by the user, and every fix to one that changed reviewed code or shipped content has had a /sc:review round after it, or the user waived that round"다. 판단하려면 다음 네 가지가 필요하다.

1. 리뷰가 낸 발견과 그 등급
2. 각 발견이 고쳐졌는지
3. 사용자가 고치지 않고 수락했는지
4. 수정의 재리뷰를 사용자가 면제했는지

### 쓰는 쪽 (writers)

- `/sc:review`: `<outputs>`는 대화 안의 요약, 조치 항목, 근거뿐이다(`review.md:31-37`). 예외는 스펙 게이트 하나다. `status: draft` 스펙을 리뷰하면 사용자가 발견을 처리한 뒤 그 round를 스펙의 "Self-Review Iteration Log"에 덧붙인다(`review.md:22`). bounds의 `<never>`도 이 기록만 예외로 둔다(`review.md:72`).
- `self-review` 에이전트: 도구가 `Read, Grep, Glob`뿐이다(`agents/self-review.md:5`). 쓸 수 없고, 등급 체계도 `critical|high|medium|low|nit`로 다르다(`:36`). 등급은 `/sc:review` Categorize 단계에서 Critical/Important/Suggestion으로 다시 묶는다(`review.md:18`).
- `/sc:implement`: `Result:` 줄, Proof의 사용자 수락(`(accepted by user)`), Deviations를 계획에 쓴다(`implement.md:19`). 리뷰 발견을 쓰지는 않는다.
- `/sc:intent --through`: "commit what each command writes"(`intent.md:20`). reflect 결과만 `06-reflect.md`로 따로 남긴다. 리뷰 결과는 Report의 "(5) the branch review's Critical count"(`intent.md:22`)로 대화에만 남는다.
- 사용자의 수락과 면제: 기록할 자리가 없다.

### 읽는 쪽 (readers)

- `/sc:reflect` 3.6 Plan-Close: "from the plan file, the review findings and `git log`"(`reflect.md:19`). "the review findings"가 어디 있는지는 정하지 않았다.
- `/sc:test` Report: 마지막 리뷰 round 뒤의 수정을 재리뷰 대상으로 말한다(`test.md:17`). 마지막 round가 언제였는지 알아야 한다.
- `/sc:implement` Integrate의 되돌림: "a Critical or Important finding in a `complete` plan's work, sets it back to `implementing`"(`implement.md:19`). RULES_DOCS 계획 규칙(`RULES_DOCS.md:58`)과 게이트(`:86`, `:88`)도 같은 상태를 말한다.
- 프로브: `test-reflect-gate`·`test-reflect-gate-complete`·`reflect-plan-close`·`reflect-plan-close-review-due`가 fixture의 `docs/features/csv-export/06-review.md`(round 절, 발견 ID, 등급, 판정)를 근거로 쓴다(`evals/tasks.yaml:514-728`). 이 파일을 쓰는 shipped 명령은 없다. 그래서 프로브는 사용자가 실제로 갖지 않는 상태를 잰다.
- 이 저장소의 관행: 리뷰 기록은 `06x-verify-*.md`로 남는다. 검증자 프롬프트에 그렇게 쓰라고 시켰기 때문이다. 명령이 쓴 것은 아니다.
- 로딩 범위: `context_loader.py:191`은 RULES_DOCS를 `/sc:review`, `/sc:reflect`, `/sc:implement`, `/sc:test`에서 주입하지 않는다(그 네 명령은 `:181`의 RULES_QUALITY만 받는다). 그래서 쓰는 규칙과 읽는 규칙은 각 명령 본문에 있어야 한다.

### 이미 막힌 것 (기준선)

`reflect-plan-close-no-record` 프로브를 이 브랜치에 먼저 커밋하고(9bf0bdac) 돌렸다. fixture에서 `06-review.md`를 지우고, 리뷰가 있었다는 흔적은 수정 커밋 제목과 계획 Deviations 한 줄만 남겼다. Linux, sonnet, low, 5회 결과는 다음과 같다.

- 5/5 통과. 계획과 README는 그대로였고, 어떤 run도 "모든 조건이 성립한다"고 하지 않았다.
- 다섯 run 모두 조건 (3)을 "확인할 수 없다"고 했다. 다음 셋 중 하나를 사용자에게 요청했다: F-1의 등급을 알려 달라, 수정에 `/sc:review`를 돌려라, 그 round를 면제해 달라.
- run 3은 Persist 단계에서 "리뷰 발견을 feature 폴더에 등급과 함께 기록하라"는 학습을 제안했다.

즉 잘못 닫는 위험은 지금도 막혀 있다. 남은 비용은 셋이다.

1. 세션이 바뀐 뒤의 Plan-Close는 근거로 통과할 수 없다. 사용자의 기억으로 통과하거나, 이미 끝난 리뷰를 한 번 더 돌려서 통과한다. 소유자는 여러 세션, 두 컴퓨터에서 일한다(`.claude/memories/` 세션 기록은 컴퓨터별로 남는다).
2. `--through` 뒤의 Plan-Close는 항상 다음 단계에서 사용자가 한다(`intent.md:22`). 그때 리뷰 결과는 이전 대화의 Report에만 있다.
3. 프로브 fixture가 shipped 명령이 만들지 않는 상태를 쓴다. 기록 위치를 정하면 fixture와 shipped 동작이 같은 모양을 갖는다.

## 지켜야 할 앞선 결정

- 리뷰는 대상을 고치지 않는다(`review.md:72` `<never>`, gotcha `no-unsolicited-fixes`, `:67`). 예외의 선례는 이미 있다. prompt-content-audit 03i(`docs/features/prompt-content-audit/03i-analysis-commands.md:31,42`)는 "게이트에 주인이 없다. review는 수정 금지라 상태를 바꿀 수 없다"는 문제를 Spec gate 단계와 `<never>` 예외로 풀었다. 이 문제도 같은 모양이다. 게이트(조건 (3))는 있는데, 그 근거를 쓰는 명령이 없다. 이 이유는 그대로 성립하지만, 같은 예외를 하나 더 두는 것으로 풀 수 있다.
- 상태나 증거 표를 늘리지 않는다. 10-20 약점 감사는 `implemented → verified → complete` 상태와 "수용 기준 증거표"를 기각했다. 이유는 절차 운영 비용(약점 4)과 "이미 있는 자리를 쓰는 것이 낫다"였다(`docs/research/superclaude-weakness-audit-ajitta-2026-10-20.md:14,33`). 그 감사가 고른 것이 계획의 `Result:` 줄이다. 이 이유는 지금도 성립한다. 새 상태, 새 파일 종류, 손으로 맞춰야 하는 표를 만드는 안은 불리하다.
- 관찰된 실패 없이 문구를 더하지 않는다(`.claude/rules/content-quality.md`). 기준선은 잘못 닫는 실패를 보여 주지 않았다. 남는 근거는 "근거를 만드는 단계가 없는 조건"과 "fixture와 shipped 동작의 불일치"다. proposal-audit의 구분으로는 문구 추가가 아니라 기본값이 없는 규칙을 고치는 일이다. 이 판단은 검증에서 다시 본다(아래 "검증에 맡길 주장" 2).
- 규칙 하나는 한 곳에 쓴다(누더기 감사, `docs/analysis/patchwork-audit-ajitta-2026-10-22.md`). 쓰는 규칙은 `review.md`에, 읽는 규칙은 `reflect.md`에 둔다. 같은 말을 RULES_DOCS나 README에 한 번 더 쓰지 않는다. README에는 행 하나를 맞춘다.
- `--through`와 충돌하지 않는다(소유자 결정, 2026-10-22). Run 단계의 수정 round는 하나다. `/sc:review` 호출은 두 번이다(`intent-through-*`의 `skill_called max: 2`). 계획을 `complete`로 만들지 않는다(`through_left_open`).
- `complete`는 사용자가 정한다(plan-complete-order B′). 기록은 판단의 근거일 뿐이다. 어떤 안도 명령이 스스로 `complete`를 쓰게 하지 않는다.

## 안

### ★B. 계획의 `## Review Log` 절 (스펙 게이트와 같은 모양)

`/sc:review`가 계획으로 진행한 작업을 리뷰하면, round마다 그 계획(분할 계획이면 index)에 몇 줄을 덧붙인다. 스펙 리뷰가 스펙의 Iteration Log에 하는 일과 같다.

- `review.md` 새 flow 단계, Process 단계 뒤(문구 초안):
  "Review Log: when the reviewed work ran from a plan document (a feature folder's `05-plan.md` or a `docs/plans/` plan), append this round under the plan (index)'s `## Review Log` heading, created after `## Proof` when absent: the reviewed commit's short sha, one line per Critical or Important finding with its id and state (open, fixed — an earlier finding this round found fixed — or accepted by the user), and any re-review the user waived. Write it in a docs-only commit once the user has resolved the findings; a run that cannot ask (headless, `/sc:intent --through`) writes them open."
- `review.md:72` `<never>`의 예외를 "the log entries in the Spec gate and Review Log steps"로 넓힌다.
- `reflect.md:19` 3.6: "the review findings"를 "the plan's `## Review Log` and any review in this session"으로 바꾼다. 사용자가 Plan-Close에서 말한 수락이나 면제는, 사용자가 yes 한 그 docs 전용 커밋에 Review Log 줄로 함께 쓴다.
- 바꾸지 않는 것:
  - `implement.md`: 재리뷰 문장은 그대로 둔다.
  - `test.md`: Report는 마지막 round를 Review Log에서 찾게 되고, 문구는 그대로다.
  - `intent.md`: Run 단계의 "commit what each command writes"가 이 쓰기를 이미 덮는다. Report (5)는 그대로다.
  - `plan.md` 템플릿: 첫 round에서 절을 만든다.
  - RULES_DOCS: 이 네 명령에서는 로드되지 않으므로 같은 말을 더하지 않는다. 그래서 `core/`는 바뀌지 않는다.
- `--through`에서의 동작: 브랜치 리뷰가 round 1을 발견 open으로 남긴다. 한 번의 수정 round 뒤 재리뷰는 없다. 나중의 Plan-Close는 "F-1 open, 그 뒤 수정 커밋, round 없음"을 파일에서 읽는다. 그리고 `/sc:review`를 이름으로 댄다. 이것이 지금 Report가 사용자에게 남기는 단계와 같다.
- 세션이 바뀐 경우: 다음 세션의 reflect는 계획 파일만 읽어도 조건 (3)을 판단한다. 계획 파일은 이미 읽는 파일이다.
- 분할 계획과 단독 계획(`docs/plans/`): Plan-Close는 index를 보므로 기록도 index에 둔다. 단독 계획에도 같은 자리가 있다. 안 A에는 이 자리가 없다.
- 크기: 발견 하나에 한 줄, round 하나에 2–5줄이다. 계획 25 KB 목표(`RULES_DOCS.md` Size)에 비해 작다.
- 프로브:
  - fixture의 `06-review.md` 내용을 계획의 `## Review Log`로 옮긴다. 대상은 test-reflect-gate 계열 두 개와 reflect-plan-close 계열 두 개다. `review_untouched` check는 계획의 Review Log 절이 그대로인지를 본다.
  - 새 `review-log-branch` 프로브: 결함을 심은 fixture에 headless로 `/sc:review --scope branch`를 부른다. 채점은 셋이다. 계획에 `## Review Log`, 리뷰한 sha, 발견 줄이 생긴다. 코드는 바뀌지 않는다. `status`는 그대로다.
  - `reflect-plan-close-no-record`는 기록 이전 계획(업그레이드 전)의 회귀 가드로 남긴다.
  - `intent-through-branch`에는 브랜치에 Review Log가 커밋됐는지 보는 check를 더한다.
- 릴리스: 명령 본문 두 개(`review.md`, `reflect.md`)가 바뀐다. 그래서 `make canary-commands`가 필요하다. `core/`는 바뀌지 않아 `canary-gates`는 필요 없다. 4.34.2의 Plan-Close 변경과 같은 워크플로 계약 변경이므로 patch, `### Changed`, `Upgrade:` 줄로 낸다. 업그레이드 줄 내용: 이미 진행 중인 계획에는 Review Log가 없으니 Plan-Close가 조건 (3)을 묻는다(기준선과 같은 동작).
- 남는 것: 사용자가 대화 중에, 그것도 review나 reflect 밖에서 한 수락은 기록되지 않는다. 다음 리뷰 round나 Plan-Close에서 다시 말해야 한다.

### A. feature 폴더의 `06-review.md`

`/sc:review`가 feature 폴더에 `06-review.md`를 만들고 round마다 절을 덧붙인다. fixture가 이미 이 모양이다.

- 바뀌는 것:
  - `review.md`에 단계 하나가 생긴다(파일 이름, 절 모양, 발견 상태).
  - `review.md`가 README `## Documents`도 갱신해야 한다. RULES_DOCS가 로드되지 않으므로 그 규칙(`RULES_DOCS.md:30`)을 본문에 다시 쓴다.
  - `<never>` 예외를 넓힌다.
  - `reflect.md` 3.6이 `06-review.md`를 읽는다.
  - 이름 충돌이 있다. `--through`는 `06-reflect.md`를 쓰고, 사용자가 이미 `06-…`을 쓴 폴더도 있다. 그래서 `06<letter>-review` 규칙이 필요하다(`RULES_DOCS.md:19`).
- 단독 계획: feature 폴더가 없으므로 기록할 곳이 없다. 대체 경로를 따로 정하든지 B로 떨어지든지 해야 한다.
- 장점: 계획이 커지지 않는다. 이 저장소의 관행, fixture와 같은 모양이다. 발견 본문 전체를 남길 수 있다.
- 단점:
  - 새 파일 종류와 README 쓰기가 생긴다. 약점 감사가 기각한 "새 표/문서를 늘리는 쪽"에 가깝다.
  - 리뷰 본문 전체를 쓰면 리뷰 하나가 문서 하나가 된다. Medium 작업에서 운영 비용이 크다.
- 릴리스: B와 같다(canary-commands, patch).

### C. 쓰지 않는다: 지금 동작을 문구로 굳힌다

`reflect.md` 3.6에 다음 한 문장을 더한다. "with no review record in the files or this session, condition (3) is unverified: name it and ask the user."

- 근거: 기준선 5/5가 이미 이렇게 한다.
- 장점: 가장 작고, 쓰는 명령이 늘지 않는다.
- 단점:
  - 위 비용 1–3이 그대로다. 조건 (3)은 세션이 바뀌면 "사용자에게 묻는다"가 된다.
  - 사용자의 답도 Plan-Close의 yes 커밋 밖에서는 남지 않는다.
  - 관찰된 실패가 없는 곳에 문구를 더하는 것이라 content-quality와 맞지 않는다. 그래서 C를 고른다면 문구 없이("변경 없음") 두는 편이 낫다.
- 릴리스: 문구를 더하면 canary-commands, patch. 변경 없음이면 릴리스할 것이 없다.

### 비교

- 세션이 바뀐 뒤 근거로 닫기: B 가능, A 가능(단독 계획 제외), C 불가(질문)
- 새 파일 종류: B 없음, A 있음, C 없음
- 바뀌는 shipped 파일: B 2개, A 2개와 README 규칙 중복, C 0–1개
- `--through`: B와 A는 Run이 커밋한다. C는 그대로다.
- fixture와 shipped 동작: B와 A는 일치한다(B는 fixture를 옮겨야 한다). C는 불일치가 남는다.
- canary: A·B·C 모두 `canary-commands`. 셋 다 `core/`를 바꾸지 않는다.

권고 ★B. 스펙 게이트가 이미 쓰는 모양이고(앞선 예외의 선례), Plan-Close가 이미 읽는 파일에 기록이 남는다. 단독 계획과 분할 계획도 덮고, 새 파일 종류와 README 쓰기가 없다.

## 검증에 맡길 주장

독립 검증이 다시 재 볼 주장이다. 틀렸을 가능성이 높은 순서로 적었다.

1. 읽는 쪽과 쓰는 쪽 목록이 완전하다. promote-feature, archive, cleanup `--type docs`, `/sc:load`·`/sc:save`, README 표, Pages, 테스트(`test_docs_ssot_guards.py` `_GATE_ANCHORS`, `test_plan_checklist.py`, `test_command_structure.py`)가 `## Review Log` 같은 새 절이나 계획 구조를 읽는지.
2. 기준선이 잘못 닫는 실패를 보여 주지 않았는데도 B가 content-quality의 "관찰된 실패" 요건을 넘는다. 더 작은 안(변경 없음, 또는 fixture만 바꾸기)이 맞을 수도 있다.
3. B의 headless 쓰기("a run that cannot ask writes them open")가 `review.md:72` `<never>`와 "no-unsolicited-fixes", 그리고 `--through` 계약(리뷰 두 번, 브랜치에 complete 없음, 작업 트리 깨끗함)과 충돌하지 않는다.
4. B에서 "fixed"를 다음 round만 쓰게 한 것이 조건 (3)의 문구와 맞는다. 조건 (3)은 "fixed or accepted"와 "round after the fix or waived"를 따로 묻는다.
5. RULES_DOCS를 바꾸지 않아도 된다. 계획 규칙(`RULES_DOCS.md:58`)이 계획 문서의 절을 열거하는지, 그리고 `--through`의 doc 작성 단계에서 RULES_DOCS가 로드되는지.

## 소유자 결정

1. 안: ★B 계획 `## Review Log` / A `06-review.md` / C 변경 없음
2. 기준선 프로브 `reflect-plan-close-no-record`(이 브랜치에서 추가, 5/5): ★회귀 가드로 남긴다 / 지운다
3. 빌드 뒤 경로: ★계획 → 빌드 → 독립 검증(opus high) round → 누더기 감사 → 병합. 릴리스는 따로 묻는다.
