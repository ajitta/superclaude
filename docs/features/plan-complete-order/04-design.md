---
status: approved-for-plan
revised: 2026-10-22
---

# 계획 `complete`의 위치

출처: [review-reflect-gate-gap](../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md) 항목 D, 그리고 [review-reflect-gates 06b](../review-reflect-gates/06b-verify-fixes.md) 발견 5. 이 문서는 설계안이다. 소유자가 고른 뒤에 계획을 쓴다.

## 문제

`/sc:implement` Integrate 단계(`src/superclaude/commands/implement.md:19`)는 마지막 상자를 체크하고 Proof가 마지막 코드 커밋에서 녹색이면, docs 전용 커밋으로 계획을 `status: complete`로 바꾼다. 같은 때 feature README도 `phase: complete`가 된다(`src/superclaude/core/rules/RULES_DOCS.md:33`). 그런데 체인에서는 그 뒤에 branch review(Large), `/sc:test`, `/sc:reflect`가 온다. 리뷰 수정이 다음 round를 거치는 것도 그 뒤다(`RULES_DOCS.md:86`). 그래서 다음 두 가지가 생긴다.

1. 이른 라벨. 리뷰·테스트·reflect 전에 파일은 "끝"이라고 말한다. 이 라벨을 읽는 쪽:
   - README `phase:`와 그 매핑(`RULES_DOCS.md:31-33`). phase는 되돌아가지 않는다.
   - `docs/archive/features/<slug>/`(완료된 feature를 옮기는 곳, `RULES_DOCS.md:39`).
   - 다음 세션의 모델과 사람. 소유자의 릴리스 습관도 여기에 기댄다(auto memory `release-needs-complete-plan`, 다른 컴퓨터; `session_2026-10-21_master.md:30` "No bump or release until the plan is `complete`, the review has passed, fixes are re-reviewed and /sc:reflect …").
2. 되돌림 경로가 하나뿐이다. `complete`를 `implementing`으로 되돌리는 것은 "a red re-run"뿐이다(`implement.md:19`). 2차 리뷰 round가 Critical을 찾아도 계획은 `complete`로 남는다.

이미 막은 것: `/sc:test` 세션의 모델은 `complete`를 보고도 "not done until /sc:reflect"와 재리뷰를 말한다(`test.md:17`). `test-reflect-gate-complete` 프로브가 이 상태를 잰다. Linux, sonnet, low에서 3/3 통과했다([05a](../review-reflect-gates/05a-plan-measurements.md)). 남은 문제는 모델이 `/sc:test`에서 하는 말이 아니라, 파일에 남는 라벨과 그 라벨을 읽는 사람·다음 세션이다.

## 지켜야 할 앞선 결정

- 상태를 늘리지 않는다. 2026-10-20 감사는 `implemented`/`verified`/`complete` 3단계 상태를 기각했다(`docs/research/superclaude-weakness-audit-ajitta-2026-10-20.md` §2). 이유는 셋이다. enum과 마이그레이션 표(`RULES_DOCS.md:61-62`, legacy `implemented` → `complete`)와 충돌한다. README phase가 되돌아가지 않는다는 규칙과 충돌한다. `test_plan_checklist.py`와 상태 전이가 함께 바뀐다.
- `complete`의 진입 조건은 상자 전부와 `Result:` 줄이다(completion-proof N2, `RULES_DOCS.md:58`). 이 조건은 어느 안에서도 그대로 둔다.
- `/sc:reflect`가 상태를 바꾸는 안은 같은 감사가 기각했다(§2 "§6 `reflect --type completion`이 상태 전이"). 이유 ②는 phase가 되돌아가지 않는다는 규칙이다. 이유 ③은 "reflect는 게이트가 없는 선택 단계"다. ③은 review-reflect-gates 이후 바뀌었다. 계획 문서로 진행한 작업은 이제 `/sc:test -> /sc:reflect`를 지난다(`RULES_DOCS.md:87`). ②는 `complete`를 늦추는 쪽에는 해당하지 않는다. 늦추면 phase가 되돌아갈 일이 없다.
- `reflect.md:45` bounds: "never overrides completion status". 아래 B는 이 줄을 바꾼다.

## 안

### A. 위치는 그대로 두고, 뜻과 되돌림 경로를 적는다

- `RULES_DOCS.md:58` 계획 조건 끝에 한 문장을 더한다. "`complete` records that the plan's tasks are done and its Proof is green on the last code commit; it does not pass the review, test and reflect gates (`<workflow_gates>`)".
- `implement.md:19`: 리뷰 round가 그 계획의 작업에서 Critical이나 Important를 찾으면, 그 수정의 첫 커밋이 계획을 `implementing`으로 되돌린다. 수정 뒤 Proof가 녹색이면 다시 `complete`다. README phase는 그대로다.
- 바뀌는 파일: `RULES_DOCS.md`(core, canary-gates), `implement.md`(canary-commands), drift test 한 줄, CHANGELOG `Changed`.
- 남는 것: README `phase: complete`와 archive 기준은 여전히 이르다. 소유자의 릴리스 습관은 `complete` 말고도 리뷰·reflect를 따로 확인해야 한다. 되돌림은 수정 커밋에서 Proof까지의 짧은 구간만 보인다.

### B. `complete`를 마지막 게이트 뒤로 옮긴다 (★)

- `implement.md:19`: Proof가 녹색이어도 계획은 `implementing`이다. `Result:` 줄만 쓴다. 지금의 "set the status"를 "`Result:` 줄을 쓴다"로 바꾼다.
- `/sc:reflect`: 계획 문서로 진행한 작업에서 남은 gap이 없거나 사용자가 남은 gap을 받아들였으면, 계획을 `status: complete`, README를 `phase: complete`로 docs 전용 커밋에서 바꾼다. 조건은 셋이다.
  - `RULES_DOCS.md:58`의 조건(상자 전부, 마지막 코드 커밋의 `Result:`)이 맞는다.
  - 그 `Result:` 뒤에 코드 커밋이 없다.
  - 리뷰가 필요한 수정이 남지 않았다(`RULES_DOCS.md:86`의 종료 조건).
  
  사용자에게 묻고 쓴다(Persist 단계와 같은 방식). `/sc:intent --through`에서는 요청이 승인이다.
- `reflect.md:45` bounds를 "never overrides completion status"에서 "sets a plan `complete` only under the conditions above; never moves it back"으로 바꾼다.
- `RULES_DOCS.md:33` phase 매핑 문구는 그대로 맞다("plan (index) `status: complete` → complete"). `implement.md`를 읽는 다른 곳(README 작업 크기 표 `/sc:implement --plan` 행 `README.md:315`, `/sc:reflect` 행 `:318`)을 같이 고친다.
- red re-run 경로(`implement.md:19` "a red re-run sets the plan back to `implementing`")는 B에서 대부분 쓸 일이 없다. `complete` 뒤의 코드 변경은 다음 feature다. 문장은 남겨 둔다(reflect 뒤에도 코드가 바뀔 수 있다).
- 프로브:
  - `implement-proof-fail`(red Proof면 `complete`가 아니다)은 그대로 통과해야 한다.
  - 녹색 Proof에서 `implementing`으로 남는지 보는 check를 implement 쪽에 더한다.
  - `test-reflect-gate-complete`의 fixture 상태(implement가 남긴 `complete`)는 새 implement가 만들지 않는다. 옛 설치나 손으로 쓴 `complete`를 재는 프로브로 남긴다.
  - reflect가 조건을 갖췄을 때만 `complete`로 바꾸는지 재는 프로브 하나를 더한다. 조건은 둘이다. 남은 재리뷰가 있으면 바꾸지 않는다. 사용자 답 없이 headless면 묻는 말만 한다.
- 바뀌는 파일: `implement.md`, `reflect.md`, `RULES_DOCS.md`(core), README 표 두 행, `evals/tasks.yaml`, 테스트, CHANGELOG. 행동 계약이 바뀌므로 minor 범프 감이고 upgrade note가 필요하다. 이미 `complete`인 계획은 그대로 둔다.
- 남는 것: reflect를 돌리지 않는 사용자의 계획은 `implementing`에 머문다. 이것이 의도다. 게이트를 다 지나지 않은 일은 끝이 아니다.

### C. 아무것도 바꾸지 않는다

- 모델 쪽 위험은 `test.md` Report 줄과 프로브가 막는다. 파일 라벨은 알려진 한계로 둔다.
- 분석 문서 D와 이 문서에 한계로 적는다.

## 권고

B를 권한다. 문제의 뿌리는 "녹색 Proof = 끝"이라는 라벨이다. A는 라벨의 뜻을 다시 적지만, 그 라벨을 읽는 README phase, archive, 릴리스 습관은 그 문장을 읽지 않는다. B는 라벨이 실제 끝에 붙게 한다. 앞선 기각의 이유 ③은 review-reflect-gates로 사라졌다. ②는 늦추는 쪽에 해당하지 않는다. 상태 enum과 진입 조건은 그대로 둔다. 비용은 `reflect.md`의 쓰기 권한 하나와 프로브 두 개다.

## 소유자가 정할 것

1. A / B / C.
2. B라면: reflect가 `complete`를 쓰기 전에 묻는가(★ 묻는다, `--through`만 예외), 아니면 조건이 맞으면 바로 쓰는가.
3. B라면 릴리스 범주: ★ 다음 minor(4.35.0)에 upgrade note와 함께. 4.34.2 릴리스 보류와 묶을지는 릴리스 때 정한다.

## 확인 방법 (B를 고르면 계획의 Proof가 된다)

- 녹색 Proof 뒤 계획 `status`가 `implementing`이고 `Result:`가 있다(implement 프로브 check).
- 재리뷰가 남은 상태의 `/sc:reflect`는 `complete`로 바꾸지 않는다. 조건이 맞고 사용자가 답하면 바꾼다(새 reflect 프로브).
- `implement-proof-fail`, `test-reflect-gate`, `test-reflect-gate-complete`가 그대로 통과한다.
- drift test가 implement.md, reflect.md, RULES_DOCS, README의 `complete` 진입 문장을 고정한다.

## 검증 반영과 확정안 B′ (2026-10-22)

[04a](./04a-design-verify.md)는 "권고 수정"이었다. 소유자는 권고대로 진행하라고 했다. 그래서 B를 04a의 B′로 고쳐 확정한다.

| 04a | 반영 |
|---|---|
| 1 (Important) | reflect는 `complete`를 제안만 한다. 쓰는 것은 사용자가 답했을 때뿐이다. f1c067b9 → 81776c29("completion is the owner's call")가 B 원안이 만들 상태였다 |
| 2 (Important) | `--through`와 headless에서는 쓰지 않는다. `intent.md` Run 단계의 "propose, write nothing"에 이 제안을 넣고, Report 단계의 "steps left to the user"에 계획 `complete`를 더한다. README `--through` 문단도 고친다 |
| 3 (Important) | 되돌림 경로: `complete` 뒤에 그 계획의 작업에서 Critical·Important가 나오거나 red re-run이면, 계획은 `implementing`으로 돌아간다. README phase는 그대로다(`RULES_DOCS.md:31`). 81776c29의 phase 되돌림은 규칙으로 올리지 않는다 |
| 4 (Important) | `implement-proof-fail`에 `Result:` 줄이 실패를 기록하고 "(accepted by user)"가 없는지 보는 check를 더한다. status·phase check는 "implement는 `complete`를 쓰지 않는다"를 재므로 남긴다 |
| 5 (Important) | reflect의 세 조건을 `reflect.md`의 새 단계에 문장 그대로 싣고 `_GATE_PHRASES`로 고정한다 |
| 6 | 리더 목록: `promote-feature.md:18`, R02(`RULES_QUALITY.md:9`), `intent.md:22` Report, `test_plan_checklist.py`. archive는 사람만 읽는다. 감사 §2의 이유는 ①–④다. reflect 기각 행의 "역할 유지"(`reflect.md:8`)에는 이렇게 답한다: reflect는 `Result:`와 `git log`만 읽고 Proof를 다시 돌리지 않는다. `Result:` 뒤에 코드 커밋이 있으면 `/sc:test`로 돌려보낸다 |
| 7 | split plan: phase 파일은 지금처럼 끝나면 `complete`이고, index만 기다린다. `RULES_DOCS.md:58`의 작성자 표기를 바꾼다 |
| 8 | 함께 거짓이 되는 문장(`tasks.yaml` 주석, `test_eval_harness.py` docstring, CHANGELOG `[Unreleased]`)을 고친다. `test-reflect-gate-complete`는 "이미 `complete`인 계획"(옛 설치, 손으로 쓴 값)을 재는 프로브로 남긴다 |
| 9 | 릴리스: 패치 `Changed`와 upgrade note. 릴리스 자체는 보류 중이다 |
| 10 | 안 D(게이트를 계획의 상자로)는 넣지 않는다. 상자를 누가 체크하고 누가 `complete`를 쓰는지는 B′와 같은 문제로 남고, "code backs it"(`implement.md:19`)와 맞지 않는다 |

B′의 내용:

- `/sc:implement`는 녹색 Proof 뒤 `Result:` 줄만 쓰고, 계획(index)은 `implementing`에 둔다. `complete`를 쓰지 않는다.
- `/sc:reflect`의 새 단계 Plan-Close: 계획 문서로 진행한 작업의 계획이 `implementing`이면 세 조건을 본다.
  1. 상자가 전부 체크되었고, 마지막 코드 커밋을 적은 녹색 `Result:`(또는 사용자의 기록된 수용)가 있다.
  2. 그 sha 뒤에 코드 커밋이 없다.
  3. 다음 리뷰 round를 기다리는 Critical·Important 수정이 없다.
  
  셋이 맞으면 계획 `complete`와 README `phase: complete`를 docs 전용 커밋으로 제안하고, 사용자가 답할 때만 쓴다. `Result:` 뒤에 코드 커밋이 있으면 `/sc:test`로 보낸다. 그 밖에는 맞지 않는 조건을 말한다.
- 되돌림: 위 04a 3.
- 바뀌는 shipped 파일: `implement.md`, `reflect.md`, `intent.md`, `RULES_DOCS.md`(core), README(표 두 행, `--through` 문단).
- 프로브: `implement-proof-fail` check 하나, 새 `implement-proof-green`(녹색 Proof 뒤에도 `implementing`, `Result:` 있음), 새 `reflect-plan-close`(조건이 맞으면 제안하고, headless라 쓰지 않는다), 새 `reflect-plan-close-review-due`(재리뷰가 남았으면 그것을 말하고 쓰지 않는다).
