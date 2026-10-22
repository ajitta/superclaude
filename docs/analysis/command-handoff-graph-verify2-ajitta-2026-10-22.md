---
status: complete
revised: 2026-10-22
---

# 핸드오프 그래프 브랜치 독립 검증 2차

**판정: 조건부 통과.** shipped 계약은 맞물린다. 옆에 쓴 roadmap(`05<letter>-plan-workflow.md`)은 이제 plan 문서를 정의하는 세 곳 모두에 들어갔다. Plan-Close와 `/sc:implement --plan`은 그 파일의 박스, Proof, `Result:`로 그대로 작동하고, 빠져나갈 길이 없는 상태는 찾지 못했다. 남은 조건은 분석 문서의 적용 표다. 이 표가 probe check를 두고 거짓 문장 하나를 적고 있다(1번).

대상: `verify/roadmap-proof-handoff-2` @ a5af3b88(수정 diff `79d26c57..a5af3b88`). 모델: Claude Opus. 재채점 결과(0/6 → 3/3)는 저장소 밖 run이라 주장으로 다뤘다. canary는 운영자가 돌리고 있다.

## 실행한 검사

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3866 passed, 3 skipped (exit 0) |
| `make lint` / `make typecheck` | All checks passed / mypy 54 files 이상 없음 |
| probe check 변이: 통째로 삭제 · `Result:` 제외 제거 · 펜스 필터 제거 | `test_roadmap_builds_on_a_draft_design_and_approves_it`가 세 경우 모두 red. 매번 `git checkout HEAD -- evals/tasks.yaml`로 되돌렸다 |
| plan 문서 정의 변이: 세 파일에서 roadmap 구절 삭제 | `test_roadmap_and_review_handoffs_follow_the_chain`가 세 경우 모두 red. 되돌렸고 status는 깨끗하다 |
| `git diff --stat v4.34.2 a5af3b88 -- core hooks commands` | 5개 파일, "릴리스 때" 줄과 같다 |

직접 만든 문서로 probe check를 돌렸다(exit 0 = 통과):

| 문서 | exit | 맞는가 |
|---|---|---|
| `` Result: `abc1234` ``만 · 펜스 안에만 `## Proof`(LF, CRLF) · 꼬리말 없음 | 1 | 맞음 |
| 펜스로 감싼 명령 / CRLF / 끝 탭 | 0 | 맞음 |
| 빈 꼬리말 뒤의 아무 펜스 블록(예: 기대 출력만 담은 ```` ```text ````) | 0 | 잘못 통과: 펜스 표시 자체가 백틱이다 |
| `~~~` 펜스 안의 `## Proof` | 0 | 잘못 통과 |
| `## Proof` 뒤에 다른 `## ` 절(마지막이 아님) | 0 | 관대함 |
| `` `<command>` → <expected> `` 자리표시 | 0 | 잘못 통과(기록된 한계) |
| `## Proof:`, `### Proof` | 1 | 잘못 실패(기록된 한계) |

옛 check(79d26c57)를 끝 탭 문서와 CRLF 문서에 돌리면 둘 다 exit 0이다. 옛 정규식이 이미 `[ \t]*`였고, `read_text`가 CRLF를 LF로 바꾸기 때문이다.

## 1차 발견 재확인

| # | 상태 | 근거 |
|---|---|---|
| G1 분석 문서가 현재 상태를 거짓으로 적음 | 해결 | 첫 줄 "지금 상태"에 해결된 것(G1 Proof, G2, G3 review→design, G5)과 열린 것(G1 `Evidence:`, D2, G4, G6–G10)이 있다. a5af3b88에서 모두 사실이다. 구멍 표의 G1·G2·G3 행, "각 절은 d7f04869 시점" 표시, 부록 캡션, "릴리스 때" 줄도 HEAD와 맞는다 |
| G2 roadmap `Evidence:` 규칙을 지키게 하는 곳 없음 | 열린 채 기록됨 | 구멍 표의 G1이 "부분 해결 … `Evidence:` 규칙은 보류"로 적혀 있다. `roadmap.md:17`의 문장은 그대로이고 `implement.md`에는 `Evidence`가 0건이다. 이와 모순되는 새 문장은 없다 |
| G3 roadmap→implement 관문 | 해결 | `RULES_DOCS.md:84`는 `/sc:roadmap -> /sc:implement --plan: Roadmap document committed; … ends with its Proof footer`이다. :83 plan 줄과 모양이 같다. `roadmap.md:17`("/sc:implement --plan runs it after the last box"), `implement.md:19` Integrate, `roadmap.md:68` 핸드오프(`/sc:implement`, plan.md:89와 같은 표기)와도 맞다 |
| G4 probe check가 관대함 | 부분 해결 | 펜스 안 제목과 `Result:`만 있는 경우는 이제 실패하고, 변이 검사로 테스트가 이를 지킨다. 남은 관대함은 위 표에 있다(2번) |
| G5 roadmap 옆 파일이 plan 문서가 아님 | 해결(잔여 제안 3) | 정의는 세 곳에 있고 셋 다 고쳤다: `reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87`. README:316·319, `docs/index.html`, `_GATE_ANCHORS`에는 정의가 없다. Plan-Close는 그 파일의 박스, 꼬리말, `Result:`로 돈다. `implement --plan`은 Load와 Integrate에서 경로만 쓰므로 그대로 작동한다. 남는 이름 충돌, 두 plan의 README `phase:`, verifier 위치는 3–5번이다 |

## 새 발견

1. **Important — 적용 표가 probe check를 두고 사실이 아닌 문장을 적는다.**
   근거: "독립 검증 반영" 4번 행에 "끝 탭도 이제 인식한다"가 있다. 그런데 옛 check도 끝 탭과 CRLF를 통과시켰다(위 실행 결과). 같은 행의 "남은 한계"는 자리표시와 `## Proof:` 두 가지만 적는다. 1차에서 "관대함"으로 기록한 "Proof가 마지막 절이 아님"과 펜스 관련 잘못 통과 두 가지는 빠져 있다. 실제 영향은 작지만 측정 기록이 사실과 다르다.
   수정: 탭 문장을 지운다. 남은 한계에 "펜스 블록은 내용과 상관없이 명령으로 친다", "`~~~` 펜스는 무시하지 않는다", "마지막 절인지 보지 않는다"를 더한다.

2. **Suggestion — probe check의 남은 관대함.**
   근거: 위 표의 잘못 통과 세 가지. 가장 그럴듯한 경우는 꼬리말이 명령 없이 기대 출력만 ```` ```text ```` 블록에 담는 것이다. 펜스 표시의 백틱 때문에 이 문서도 통과한다. 이 부분을 지키는 테스트 사례는 없다.
   수정: 펜스 표시 줄(```` ``` ````/`~~~`)은 백틱으로 세지 않는다. 대신 펜스 안에 비어 있지 않은 줄이 있는지 본다. 고친다면 저장된 run을 다시 채점한다.

3. **Suggestion — 분할 plan 단계 이름과 roadmap 이름이 겹친다.**
   근거: 분할 plan의 단계 파일은 `05<letter>-plan-<phase-name>.md`이다(`RULES_DOCS.md:13`). 그래서 단계 이름이 `workflow`이면 roadmap 정의와 글자가 같아진다. Plan-Close는 "check its plan (index)"라고 쓰고, 분할 plan의 작업은 어차피 reflect로 간다. 그래서 실제 결과는 같다. 다만 모델이 단계 파일을 인덱스로 읽으면 "`Result:` 없음"으로 판정할 수 있다.
   수정: 정의를 이름이 아니라 역할로 적는다("05 슬롯의 plan (index)"). 아니면 분할 규칙에서 `workflow`를 단계 이름으로 쓰지 못하게 한다. 이 브랜치 밖의 항목과 함께 고치면 된다.

4. **Suggestion — 한 폴더에 plan 문서가 둘이면 README `phase:`가 끝난 것처럼 보인다.**
   근거: `05a-plan-workflow.md`가 먼저 `complete`가 되면, Plan-Close가 `05-plan.md`가 아직 `implementing`인데도 README를 `phase: complete`로 바꾼다(`reflect.md:19`, `RULES_DOCS.md:33`). 이 경로는 이번 수정으로 새로 생겼다. 반대 순서에서는 README가 처음부터 `complete`에 머물고, 이쪽은 원래 있던 경로다. 둘 다 규칙과 모순되지는 않는다(phase는 "도달한 가장 먼 단계"이고 되돌아가지 않는다). 각 plan의 Plan-Close도 여전히 쓸 수 있어 막힌 상태는 아니다. 다만 README를 읽는 사람은 기능이 끝났다고 오해한다.
   수정: Plan-Close가 README를 `complete`로 바꾸는 조건을 "폴더의 모든 plan (index)가 `complete`일 때"로 좁힌다.

5. **Suggestion — `test.md`의 verifier 항목이 plan 문서를 `05-plan.md`로만 적는다.**
   근거: `test.md:40`은 "(05-plan.md Proof section and task list)"라고 쓰고, `verifier.md:23`은 경로가 주어지지 않으면 `05-plan.md`를 고른다. 같은 파일의 `test.md:17`은 이제 `05<letter>-plan-workflow.md`도 plan 문서라고 쓴다. 경로 없이 띄우면 roadmap이 아니라 주 plan과 대조한다. verifier는 요청할 때만 돌아 Suggestion이다.
   수정: `test.md:40`을 "the plan doc the work ran from (its Proof section and task list)"로 바꾼다.

## plan 문서 정의·roadmap 출력 계약·핸드오프가 적힌 곳

| 위치 | 내용 | 일치 |
|---|---|---|
| `reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87` | plan 문서 = 05-plan, roadmap의 05<letter>-plan-workflow, docs/plans | 일치(가드 있음, 변이 검사 red) |
| `RULES_DOCS.md:58`, `:32-33`, `:88` | plan (index) `complete` 조건, phase 매핑 | 일치. 두 plan의 경우는 4번 |
| `RULES_DOCS.md:13` | 분할 단계 파일 `05<letter>-plan-<phase>` | 이름 겹침(3번) |
| `test.md:40`, `verifier.md:23` | verifier가 대조할 plan = 05-plan.md | 좁음(5번) |
| `roadmap.md:17-18`, `:29` | 박스 + 빈 Evidence, `## Proof`, `--plan`이 `Result:`를 씀, 경로 | 기준 |
| `implement.md:13`, `:19` | Load, Integrate, Proof, `Result:` | 일치. Evidence는 G2(보류) |
| `RULES_DOCS.md:83-84`; `roadmap.md:68`, `review.md:76`, `design.md:62`, `estimate.md:50` | 관문, 핸드오프 | 일치 |
| README:313·316·319, `commands/README.md:43`, `help.md:50`, `recommend.md:36`, `docs/index.html` | 설명뿐, 정의나 roadmap→task 없음 | 일치 |
| `CHANGELOG.md` [Unreleased] | Proof, task 제거, review→design, roadmap 옆 파일이 plan 문서가 됨, probe 3개 | 출시 문구와 일치. 4.34.2 항목의 옛 정의는 출시 기록이라 그대로 둔다 |
| 분석 문서 맨 위, 구멍 표, 부록 캡션, "릴리스 때" | 현재 상태 | 일치. 적용 표 4번 행은 1번 |

## 이 브랜치 밖

- **Important 후보 — 다른 독립 plan `05<letter>-plan-<distinguisher>.md`도 plan 문서 정의에 없다.** 이 저장소는 실제로 두 번째 plan을 그렇게 쓴다: `command-local-flags/05a-plan-pointer-checks.md`, `plugin-install/05a-plan-release-channel.md`. 둘 다 05-plan.md와 별도의 계획이다. 이런 파일을 `/sc:implement --plan`으로 돌리면 고친 roadmap 경우와 같은 이유로 `implementing`에서 나갈 길이 없다. 이번 수정은 roadmap 이름 하나만 넣었다. 수정: 3번과 함께 정의를 "05 슬롯의 plan (index): `05-plan.md`, 또는 어떤 plan 인덱스도 단계로 링크하지 않는 `05<letter>-plan-*.md`, 또는 `docs/plans/` plan"으로 바꾼다.
