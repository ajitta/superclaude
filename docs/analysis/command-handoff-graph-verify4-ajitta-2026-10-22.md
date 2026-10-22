---
status: complete
revised: 2026-10-22
---

# 핸드오프 그래프 브랜치 독립 검증 4차

**판정: 조건부 통과.** 3차 Important(박스 없는 부속 파일이 README를 붙잡음)는 해결됐다. 정의 세 곳은 글자까지 같고, 게이트도 모두 green이다. 남은 조건은 1번 하나다. 마지막 Plan-Close가 끝난 뒤에 남은 plan을 `deprecated`로 바꾸거나 `archive/`로 옮기면, README를 `complete`로 쓰는 단계가 없다.

대상: `verify/roadmap-proof-handoff-4` @ f548bfcb(수정 diff `64f0fabe..f548bfcb`). 모델: Claude Opus. canary는 운영자가 돌린다.

## 실행한 검사

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3866 passed, 3 skipped (exit 0) |
| `make lint` / `make typecheck` | All checks passed / mypy 54 files 이상 없음 |
| 새 문장을 하나씩 되돌림(7개: reflect 정의·README 조건, test 정의·verifier, RULES_DOCS 매핑·관문 정의, implement "not already further") | 7개 모두 `test_roadmap_and_review_handoffs_follow_the_chain` red. 매번 `git checkout HEAD -- <f>`로 복구했고 `git status`는 깨끗 |
| `_SOFTENER`(implement Integrate, reflect Plan-Close, test Report, 관문) | 새 문장에 걸리는 말 없음. 3차가 제안한 "unless"를 "when it is not already further"로 바꾼 이유도 이것이다 |
| probe check(HEAD 판)를 직접 만든 문서 8개에 돌림 | 아래 3번 |
| `docs/features/*/05*.md` 47개의 status·박스 수·인덱스 링크 | 아래 G1·G2 |

## G1–G5

| # | 상태 | 근거 |
|---|---|---|
| G1 README `complete` | **부분 해결(1번)** | 두 plan: 어느 쪽이 먼저 닫혀도 마지막 Plan-Close가 README를 쓴다. 박스 없는 부속 파일(`runtime-behavior-audit/05a`)은 "with task boxes"로 빠진다. 분할 plan: 단계 파일은 정의에서 빠지고, 인덱스의 단계 박스는 implement("the plan's (index's) last box")와 Plan-Close (1)이 그 plan의 박스로 다루므로 "with task boxes"로 읽힌다. 규칙 전에 이미 `complete`인 README는 G5로 그대로 남는다. plan이 **닫히기 전에** `deprecated`가 된 경우는 풀린다. **닫힌 뒤에** `deprecated`나 `archive/`가 된 경우는 막힌다(1번). 두 문장은 `archive/` 한 군데가 다르다(2번) |
| G2 단계 파일 기준 | 해결 | `RULES_DOCS.md:13`(인덱스는 단계마다 체크박스로 파일을 링크)과 맞다. 실제 폴더: `serena-removal`, `authoring-skill`의 05a–g는 인덱스 체크박스 줄(`05-plan.md:43-50`)에 있으니 단계 파일이다. `command-local-flags/05a`, `plugin-install/05a`, `runtime-behavior-audit/05a·05b`는 체크박스 줄에 없으니 별도 plan이다. 규칙 전의 크기 분할(`install-upgrade-audit/05a·05b`, `over-engineering-audit/05a–g`)은 산문으로 링크되어 별도 plan으로 분류된다. 하지만 박스가 0개라 README 규칙에 영향이 없고, 옛 문서는 그대로 둔다는 규칙(`RULES_DOCS.md:27`)에 든다 |
| G3 probe 한계 목록 | 해결, 잔여 3번 | 3차가 제안한 수정(④를 넓힘, ⑤에 `## Proof footer`를 더함, `**Result:**`·`- Result:`)은 모두 들어갔고, 재현해 보니 사실이다. 들여쓴 펜스는 빠졌다 |
| G4 verifier 경로 | 해결, 잔여 4번 | `verifier.md:23`(주어진 경로 → `05-plan.md` → `docs/plans/`)과 맞다. 가드도 red가 된다 |
| G5 "not already further" | 해결 | "never moves back"(`implement.md:19` 끝, `RULES_DOCS.md:31`)과 맞는다. `complete`와 `abandoned`인 README를 되돌리지 않는다. `_SOFTENER`도 통과한다 |

## 새 발견

1. **Important — plan이 닫힌 뒤 남은 plan을 버리거나 옮기면 README가 `implementing`에서 나갈 길이 없다.**
   근거: README를 `complete`로 쓰는 곳은 Plan-Close뿐이다. 그런데 Plan-Close는 plan이 `implementing`일 때만 제안한다(`reflect.md:19` "The plan is `implementing` and all three hold"). 그래서 A가 닫힐 때 B가 열려 있으면 README는 그대로다. 그 뒤 B를 `deprecated`로 바꾸거나 `archive/`로 옮기면 `RULES_DOCS.md:33`의 조건은 채워진다. 하지만 `:34`는 "`deprecated` docs never move it"이고, A에 /sc:reflect를 다시 돌려도 A가 `complete`라서 README를 제안하지 않는다. `deprecated`를 쓰는 명령도 없다. 실례 후보: `plugin-install`은 05a가 `complete`이고 05-plan은 보류된 `draft`(박스 44개)다. 소유자가 05-plan을 버리면 이 상태가 된다. CHANGELOG의 "a `deprecated` plan … do not hold it back"은 버린 순서가 앞일 때만 맞는다.
   수정: Plan-Close에 한 줄을 더한다. 예: "a `complete` plan whose folder README is not `complete` while every other plan with task boxes is `complete` or `deprecated` (`archive/` aside) → propose the README `phase: complete`". 또는 `:34`에 "deprecating or archiving a plan re-checks the complete rule"을 쓴다. 가드에 넣는다.

2. **Suggestion — reflect의 README 조건에 "(`archive/` aside)"가 없다.**
   근거: `RULES_DOCS.md:33`과 CHANGELOG에는 있다. README를 실제로 쓰는 `reflect.md:19`에는 없다. 문자 선택 규칙(`RULES_DOCS.md:19` "`archive/` included")은 `archive/`를 폴더의 일부로 본다. 그래서 상태가 그대로인 옛 판이 `archive/`에 있으면, reflect의 글자만 읽어서는 README를 붙잡을 수 있다. RULES_DOCS는 문서를 만드는 맥락에서만 주입된다. 지금 저장소에 `archive/` 폴더는 없다.
   수정: reflect에 같은 괄호를 넣고 가드 구절을 늘린다.

3. **Suggestion — probe 한계 목록에 들여쓴 펜스가 빠졌다.**
   근거: fence 정규식은 `^```` (줄 첫 칸)만 본다. 측정해 보니 1–3칸 들여쓴 ```` ``` ```` 펜스나 목록 안 펜스(`- ```md`) 안의 `## Proof`는 무시되지 않고 잘못 통과했다. 줄 첫 칸 펜스는 실패하는 게 맞았다. 3차 표에 이미 "들여쓴 펜스 안 제목"이 있었지만, 4번 행은 "` ``` ` 펜스 블록 안의 제목을 무시"라고만 쓴다. 나머지 주장(`~~~`, `**Result:**`, 파일 이름만, `## Proof footer` 실패, `Result:`만 실패)은 모두 재현됐다.
   수정: "줄 첫 칸에서 여는 ` ``` ` 펜스만 본다(들여쓴 펜스나 목록 안 펜스 안의 제목은 무시하지 않는다)"를 더한다.

4. **Suggestion — `test.md:40` 문장이 꼬였다.**
   근거: "…(its Proof section and task list), whose path it is passed and reports every mismatch"는 쉼표가 빠져서 "and reports"가 관계절에 붙는다. 경로를 넘기라는 말도 서술형이라 지시로 읽기 어렵다. `verifier.md:23`과는 맞다.
   수정: "…(its Proof section and task list; pass it that path), and reports…"로 쓰고 가드 구절을 바꾼다.

## 정의와 규칙이 적힌 곳

| 위치 | 내용 | 일치 |
|---|---|---|
| `reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87` | plan 문서 정의(+ 인덱스 체크박스 기준) | 글자까지 같다. 셋 다 가드가 red가 된다 |
| `RULES_DOCS.md:13`, `:19` | 분할 단계 파일, Multi-of-same-phase(`archive/` 포함) | 정의와 맞다. `:19`는 2번 |
| `RULES_DOCS.md:31-34` | phase 매핑, never moves back, `deprecated`는 phase를 옮기지 않음 | `:33`은 reflect와 같은 뜻이고 `archive/`만 다르다(2번). `:33`과 `:34` 사이 순서 문제는 1번 |
| `reflect.md:19` Plan-Close | README `complete` 조건, 다시 열 때 README 그대로 | 1번, 2번 |
| `implement.md:19` | 첫 박스에서 `implementing`(이미 더 나아갔으면 그대로), `complete`로 만들지 않음, never moves back | 일치 |
| `RULES_DOCS.md:58`, `:88`; `intent.md:22` | plan `complete` 조건, Plan-Close의 yes, `--through`는 사용자에게 남김 | 일치 |
| `test.md:40`, `verifier.md:23` | verifier가 받는 plan 경로 | 일치(4번은 문장만) |
| `CHANGELOG.md` [Unreleased] | 두 plan, 박스 없는 파일·`deprecated`·`archive/` 제외, 첫 박스가 `complete`를 되돌리지 않음 | 출시 문구와 대체로 맞다. `deprecated`는 1번, `archive/`는 RULES_DOCS와만 맞음(2번) |
| 분석 문서 적용 표 4번 행, 3차 반영 표 | 측정 기록 | 사실. 빠진 것은 3번 |
