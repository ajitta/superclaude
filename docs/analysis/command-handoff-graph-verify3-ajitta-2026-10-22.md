---
status: complete
revised: 2026-10-22
---

# 핸드오프 그래프 브랜치 독립 검증 3차

**판정: 조건부 통과.** 2차 Important(적용 표의 거짓 문장)는 고쳐졌다. plan 문서 정의는 세 곳이 글자까지 같다. 남은 조건은 1번 하나다. 새 README `complete` 규칙이 폴더 안의 모든 plan 문서를 세는데, 그중에는 끝내 `complete`가 될 수 없는 문서가 있다. 그런 문서가 있으면 README가 `implementing`에서 나갈 길이 없다.

대상: `verify/roadmap-proof-handoff-3` @ ccdfdc8f(수정 diff `cb97a307..ccdfdc8f`). 모델: Claude Opus. canary는 운영자가 돌린다.

## 실행한 검사

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3866 passed, 3 skipped (exit 0) |
| `make lint` / `make typecheck` | All checks passed / mypy 54 files 이상 없음 |
| 파일 되돌리기(`git show HEAD~1:<f> > <f>`): `reflect.md`, `test.md`, `RULES_DOCS.md` | 셋 다 `test_roadmap_and_review_handoffs_follow_the_chain` red |
| 문장 하나만 되돌리기: reflect README 조건, RULES_DOCS phase 매핑, test Report 정의 | 셋 다 red |
| 문장 하나만 되돌리기: `test.md` verifier 항목 | **green**(4번) |
| 복구 | 매번 `git checkout HEAD -- <f>`, `git status` 깨끗 |

probe check(`roadmap-design-draft`)를 HEAD와 79d26c57 판에서 추출해 직접 만든 문서 20개에 돌렸다(0 = 통과).

| 문서 | 옛 | HEAD | 적용 표와 대조 |
|---|---|---|---|
| 끝 탭 · CRLF | 0 | 0 | 옛 check도 통과. "끝 탭도 인식한다"는 지워졌다 |
| `Result:`만 · ```` ``` ```` 펜스 안 제목 | 0 | 1 | 고쳤다는 주장과 맞음 |
| 한계 ① 기대 출력만 든 ```` ```text ```` 블록 | 0 | 0 | 사실 |
| 한계 ② `~~~` 펜스 안 제목 | 0 | 0 | 사실 |
| 한계 ③ `## Proof` 뒤에 다른 절 | 0 | 0 | 사실 |
| 한계 ④ `` `<command>` `` 자리표시 | 0 | 0 | 사실 |
| 한계 ⑤ `## Proof:` · `### Proof` | 1 | 1 | 사실 |
| 표에 없음: 파일 이름만 백틱(`` `04-design.md` ``) · `**Result:** `…`` · `- Result: `…`` · 들여쓴 펜스 안 제목 | 0 | 0 | 잘못 통과(3번) |
| 표에 없음: `## Proof footer` | 1 | 1 | 잘못 실패(3번) |

## G1–G5

| # | 상태 | 근거 |
|---|---|---|
| G1 적용 표의 거짓 문장 | 해결 | 4번 행에서 탭 문장이 빠졌고, 다섯 한계는 모두 재현된다. 2차 반영 1행의 "옛 check도 탭과 CRLF를 통과"도 사실이다. 거짓 주장은 남지 않았다. 목록이 다 적지 못한 경우는 3번이다 |
| G2 더 조이지 않음 | 수용 | 2차 제안(펜스 안에 빈 줄이 아닌 줄이 있는지 보기)으로도 한계 ①은 남는다. 그래서 "정규식으로 명령과 출력을 가를 수 없다"는 이유는 맞다. 문서가 실패한다고 적은 경우를 check가 통과시키는 일은 없다 |
| G3 역할로 쓴 정의 | 해결, 잔여 2번 | `reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87`이 같은 구절을 쓴다. implement Load·Integrate는 경로와 "plan (index)"만 쓰고, `RULES_DOCS.md:58`은 "Plan docs (feature or standalone)"라고 쓴다. `_GATE_ANCHORS`에는 plan이 하나라는 가정이 없다. 셋 다 모순되지 않는다 |
| G4 README `complete` | **열림(1번)** | 순서는 어느 쪽이든 마지막 Plan-Close가 README를 쓴다. 다시 열린 plan은 README를 바꾸지 않고(never moves back), 다시 닫을 때 README를 쓴다. `--through`는 `complete`를 사용자에게 남긴다(`intent.md:22`). 규칙 전의 폴더(README가 이미 `complete`)에 새 plan이 생겨도 README는 `complete`에 머문다. 막힌 상태는 아니다(이 브랜치 밖 참조). 막히는 경우는 1번이다 |
| G5 verifier 항목 | 해결, 잔여 4번 | `test.md:40`과 `verifier.md:23`(주어진 경로 → `05-plan.md` → `docs/plans/`)이 모순되지 않는다 |

## 새 발견

1. **Important — README `complete` 조건이 끝내 `complete`가 될 수 없는 plan 문서까지 센다.**
   근거: `reflect.md:19`("whose other plan documents are all `complete`")와 `RULES_DOCS.md:33`("every plan (index) in the folder")에는 예외가 없다. 막히는 문서는 두 종류다. (a) 버린 plan이다. `deprecated`가 되고 박스와 `Result:`가 없으니 `RULES_DOCS.md:58`로는 `complete`가 될 수 없다. `archive/`로 옮긴 옛 판이 "in the folder"에 드는지도 정하지 않았다. (b) 05 슬롯에 있지만 박스가 없는 부속 파일이다. 새 정의로는 이것도 plan 문서다. 실례: `runtime-behavior-audit/05a-plan-trigger-tiers.md`("Detail for 05-plan.md Task 8", 박스 0개, `approved-for-plan`). implement는 박스를 체크할 때만 status를 바꾸므로 이 파일을 바꾸는 쪽이 없다. 그래서 `05-plan.md`를 끝내도 README가 `implementing`에 머문다. 규칙 안에서 나갈 길이 없다. 이 수정 전에는 처음 끝난 plan이 README를 바꿨으므로 생기지 않던 상태다.
   수정: 두 곳 모두 "`deprecated`가 아니고 task 박스가 있는 plan (index)"만 센다. 또는 Plan-Close가 `complete`가 아닌 나머지 plan 문서를 나열하고, README를 바꿀지 사용자에게 묻는다. 가드에 같은 구절을 더한다.

2. **Suggestion — 단계 파일과 별도 plan을 가르는 기준이 정의에 없다.**
   근거: 분할 규칙(`RULES_DOCS.md:13`)에 표시가 두 가지 있다. 단계 파일은 머리줄에서 인덱스로 링크하고, 인덱스는 단계마다 체크박스로 파일을 링크한다. 앞의 표시는 가르지 못한다. 이 저장소의 별도 plan도 `05-plan.md`로 링크한다(`command-local-flags/05a-plan-pointer-checks.md:16`, `plugin-install/05a-plan-release-channel.md:128`). 가르는 것은 인덱스 쪽 체크박스뿐이다(`serena-removal/05-plan.md:43-46`). 반면 `command-local-flags/05-plan.md`는 05a를 링크하지 않는다. `reflect.md`와 `test.md`는 이 기준을 적지 않고, `RULES_DOCS.md`는 필요할 때만 읽힌다.
   수정: 정의를 "a split plan's phase file (one its index lists with a checkbox)"로 쓴다.

3. **Suggestion — probe check 한계 목록이 아직 다 적지 못했다.**
   근거: 위 표의 "표에 없음" 행들이다. 한계 ④는 더 넓다. 절 안에 백틱이 하나라도 있으면 통과하므로, 파일 이름만 있어도 통과한다. 또 `Result:`로 시작하는 줄만 빼므로 `**Result:**`와 `- Result:` 줄은 명령으로 친다. 거짓 문장은 아니다. 그리고 G2 결정으로 고치지 않기로 했다.
   수정: 한계 ④를 "절 안에 백틱이 하나라도 있으면 통과(자리표시, 파일 이름)"로 넓힌다. `## Proof footer`를 ⑤에 더한다.

4. **Suggestion — `test.md` verifier 항목을 지키는 가드가 없고, 경로를 넘기라는 말도 없다.**
   근거: 이 문장을 옛 판으로 되돌려도 green이다. `verifier.md:23`은 경로가 없으면 `05-plan.md`를 고른다. 그런데 `test.md:40`은 무엇과 대조할지만 쓰고, 그 plan의 경로를 넘기라고는 쓰지 않는다.
   수정: "passing it the path of the plan doc the work ran from"으로 쓰고, 가드에 넣는다.

## 정의와 규칙이 적힌 곳

| 위치 | 내용 | 일치 |
|---|---|---|
| `reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87` | plan 문서 정의(역할) | 일치, 가드 red. 가르는 기준은 2번 |
| `RULES_DOCS.md:13`, `:19` | 분할 단계 파일, Multi-of-same-phase | 정의와 맞음 |
| `RULES_DOCS.md:31-34` | phase 매핑, never moves back, `deprecated`는 phase를 옮기지 않음 | reflect와 일치. 셀 대상은 1번 |
| `reflect.md:19` Plan-Close | 다른 plan 문서가 모두 `complete`일 때 README `complete`. 다시 열 때 README 그대로 | `RULES_DOCS.md:33`과 일치. 1번 |
| `implement.md:19` | README를 `complete`로 만들지 않음. 첫 박스에서 `implementing`, never moves back | 일치. 단 이 브랜치 밖 참조 |
| `RULES_DOCS.md:58`, `:88`; `intent.md:22` | plan `complete` 조건, Plan-Close의 yes, `--through`는 사용자에게 남김 | 일치 |
| `test.md:40`, `verifier.md:3`·`:23` | verifier가 대조할 plan | 일치(4번) |
| `CHANGELOG.md` [Unreleased] | 두 번째 plan이 plan 문서가 됨, 단계 파일은 제외, 두 plan이 모두 끝나야 README `complete` | 출시 문구와 일치("both"는 plan이 둘인 경우의 말) |
| 분석 문서 적용 표 4번 행, 2차 반영 표 | 측정 기록 | 사실(3번은 빠진 내용일 뿐) |

## 이 브랜치 밖

- **Suggestion — `implement.md:19`의 "The first checked box sets … the README `phase:` to `implementing`".** README가 이미 `complete`인 폴더에서는 이 문장이 "never moves back"(`RULES_DOCS.md:31`, 같은 단계의 뒤 문장)과 부딪힌다. 그런 폴더는 규칙 전에 첫 plan이 끝난 폴더이거나, 끝난 뒤 plan을 더한 폴더다. 글자대로 읽으면 README가 뒤로 간다. 25c1ceea 이후 그대로인 문장이다. 수정: "(unless the README is already further)"를 붙인다.
