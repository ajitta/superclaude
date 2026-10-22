---
status: complete
revised: 2026-10-22
---

# 명령 핸드오프 그래프 — 5차 독립 검증

대상: `verify/roadmap-proof-handoff-5` @ 95d5f73b(4차 반영 커밋). 비교 기준: `git diff 0aa1daea 95d5f73b`. 적용 표는 믿지 않고 각 항목을 파일과 실행으로 다시 확인했다.

**판정: 통과.** README `phase:`를 "plan (index)가 `complete`가 되면 `complete`"로 되돌린 뒤에는 나갈 길이 없는 상태가 남지 않았다. `reflect.md`, `implement.md`, `RULES_DOCS.md`, CHANGELOG는 서로 맞고, 되돌린 규칙의 문장은 남아 있지 않다. Critical과 Important는 없고 Suggestion이 둘 있다. 하나는 가드 빈틈이고, 하나는 2·3차 적용 표에 "되돌림" 표시가 없는 것이다.

## 실행한 검사

- `uv run pytest -q`: 3866 passed, 3 skipped, exit 0. `make lint`: All checks passed. `make typecheck`: Success, 54 source files.
- `test_roadmap_and_review_handoffs_follow_the_chain` 변이 13개(한 번에 하나씩 되돌리고 `git checkout HEAD -- <file>`로 복구, 끝난 뒤 `git status` 깨끗함):
  - red 12개: roadmap Proof 문장, roadmap 핸드오프에 `/sc:task` 추가, review 핸드오프에서 `/sc:design` 제거, plan 문서 정의 세 곳(RULES_DOCS, reflect, test) 각각, RULES_DOCS roadmap 관문, phase 매핑을 3차 문장으로, phase 매핑을 2차 문장으로, test.md "the plan doc the work ran from", "pass it that path", implement "when it is not already further".
  - green 1개: `reflect.md` Plan-Close의 "in a feature folder, the README `phase: complete`"를 3차 문장("whose other plan documents with task boxes are all `complete` or `deprecated`")으로 되돌림. 이 변이로는 전체 suite도 3866 passed였다(제안 1).
- probe check(`evals/tasks.yaml:579-591`의 `proof()`)를 스크래치에서 사례 7개로 돌렸다. 첫 칸 펜스 안 제목은 무시하고, 들여쓴 펜스, 목록 안 펜스, `~~~` 펜스 안 제목은 통과시킨다. `**Result:**` 줄은 명령으로 치고, `Result:`만 있으면 실패하고, `### Proof`는 실패한다.

## G1–G5

| 기준 | 판정 | 근거 |
|---|---|---|
| G1 나갈 길 없는 상태 없음 | 충족 | plan 하나: Plan-Close가 plan과 README를 함께 `complete`로 쓴다(`reflect.md:19`, `RULES_DOCS.md:33`). plan 둘, 어느 순서로 닫든: 먼저 닫힌 plan이 README를 `complete`로 만든다. 두 번째 plan의 첫 박스는 "when it is not already further"라서 README를 되돌리지 않고(`implement.md:19`), 두 번째 Plan-Close는 이미 `complete`인 값을 다시 쓸 뿐이다. 다른 plan을 닫기 전이나 후에 버려도 README는 그 plan을 세지 않으므로 막히지 않는다. 박스 없는 05 슬롯 파일(`runtime-behavior-audit/05a-plan-trigger-tiers.md`, 박스 0개): README 조건에서 빠졌고, 그 파일에서 작업이 돌지 않으면 Plan-Close 대상도 아니다. 분할 plan: 단계 파일의 `complete`는 README를 움직이지 않고, index의 Plan-Close만 움직인다. 다시 연 `complete` plan: implement와 reflect 모두 "README `phase:` unchanged / never moves back"이고, 다시 닫으면 같은 Plan-Close를 쓴다. `--through`: `intent.md:22`는 "setting the plan `complete`"를 사용자에게 남기므로 아무것도 `complete`로 쓰지 않는다. plan이 하나뿐이고 그 plan을 버리면 README가 `implementing`에 머문다. 이것은 이 브랜치 전부터 있던 상태이고, 새 plan을 쓰거나 `abandoned`로 바꾸면 빠져나온다. 남은 문장 grep(`with task boxes`, `` `archive/` aside ``, `both are`, `other plan`, `every plan`)은 src/·CHANGELOG에서 하나도 나오지 않았다. 가드가 "with task boxes"를 금지할 때만 나오고, `author_check.py`와 `run_eval.py`의 "both are"는 이 주제와 상관없다 |
| G2 되돌린 이유가 맞는가, 기록이 참인가 | 충족(제안 2) | `RULES_DOCS.md:31`은 "README `phase:` = the furthest stage the folder has reached; it never moves back"이라고 쓴다. 되돌린 이유는 이 정의와 같다. 2차 제안 4도 처음부터 "규칙과 모순되지 않고 막힌 상태도 아니다"라고 적었으므로(`verify2:60-62`) 받지 않는 것과 맞는다. 문서 전체로 보면 4차 절이 되돌림을 적고, "남는 것" 줄이 지금 유효한 규칙을 적는다. 다만 2차 표 4번 행과 3차 표 1번 행은 되돌린 규칙을 현재형("바꾼다", "…이다")으로 적고 표시가 없다 |
| G3 probe 한계 목록에 들여쓴 펜스와 목록 안 펜스 | 참 | 적용 표 4번 행에 "들여쓴 펜스나 목록 안 펜스(`- ```md`) 안의 제목은 무시하지 않는다. 줄 첫 칸에서 여는 ` ``` ` 펜스만 본다"가 있다. 실행 결과도 같다(위) |
| G4 verifier 문장과 가드 | 충족 | `test.md:40`은 "compares with the plan doc the work ran from (its Proof section and task list; pass it that path), and reports every mismatch without fixing"이다. 두 구절 모두 가드가 지키고, 하나씩 되돌리면 가드가 red가 된다 |
| G5 앞 차수의 해결 유지 | 충족 | 역할 기준 정의가 reflect·test·RULES_DOCS에 같은 문장으로 하나씩 있다(grep -o 각 1). `roadmap.md:17`에 Proof 꼬리말이 있다. 핸드오프는 roadmap → `/sc:implement`(`roadmap.md:68`), review는 `/sc:design`을 포함한다(`review.md:76`). `RULES_DOCS.md:84` roadmap → implement --plan 관문, `implement.md:19` "when it is not already further"가 그대로이고, 모두 변이 시 red다 |

## 새 발견

1. **Suggestion — `reflect.md` Plan-Close의 README 문장을 지키는 가드가 없다.**
   근거: 4차 반영 때 가드에서 reflect 단언이 빠졌다. "with task boxes" 금지도 `rules`(RULES_DOCS)에만 건다. reflect에 3차 문장을 다시 넣어도 전체 suite가 통과했다(변이 M7). 기록(4차 절)은 "reflect.md Plan-Close와 RULES_DOCS 매핑을 원래 문장으로 돌렸다. 가드는 원래 문장을 고정하고…"라고 써서, 두 곳을 다 지키는 것처럼 읽힌다. 지금 문장은 맞으므로 Suggestion이다.
   수정: 가드에 `assert "and, in a feature folder, the README \`phase: complete\`" in reflect`와 `assert "with task boxes" not in reflect`를 더한다. 아니면 기록에 "가드는 RULES_DOCS만 본다"고 적는다.

2. **Suggestion — 2·3차 적용 표에 되돌림 표시가 없다.**
   근거: 2차 표 4번 행("Plan-Close는 '폴더의 다른 plan 문서가 모두 `complete`일 때'만 README를 `complete`로 바꾼다")과 3차 표 1번 행("RULES_DOCS 매핑은 'every plan (index) with task boxes …'이다. 둘 다 가드에 넣었다")은 지금 없는 규칙과 가드를 현재형으로 적는다. 같은 문서의 1차 표 4번 행은 고친 내용에 "(2차 검증 반영으로 정정)"을 붙였다. 1차 표의 "이 브랜치 밖" 행("a roadmap's `05<letter>-plan-workflow.md`"를 넣고, 가드가 그 이름을 본다)도 2차에서 역할 기준으로 바뀌었는데 표시가 없다. 시간순 기록이고 바로 아래 4차 절이 되돌림을 적으므로 거짓 기록까지는 아니라고 보았다.
   수정: 두 행 끝에 "(4차 검증 반영에서 되돌림)"을, 1차 행 끝에 "(2차 검증 반영에서 역할 기준으로 바뀜)"을 붙인다.

## 이 브랜치 밖

없음. 2차 제안 4가 지적한 경로(roadmap plan이 먼저 닫히면 주 plan이 진행 중인데 README가 `complete`)는 정의대로의 동작이다. CHANGELOG는 이 경로를 따로 적지 않지만, 거짓 문장은 없다.
