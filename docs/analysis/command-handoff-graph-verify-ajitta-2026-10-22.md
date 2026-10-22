---
status: complete
revised: 2026-10-22
---

# 핸드오프 그래프 브랜치 독립 검증

**판정: 조건부 통과.** shipped 계약은 맞물린다. roadmap 문서에 미체크 박스, 빈 `Evidence:` 줄, `## Proof` 꼬리말이 있으면 `/sc:implement --plan`이 Proof를 돌려 `Result:`를 쓰고, `/sc:reflect` Plan-Close와 `RULES_DOCS.md:58`이 그 줄로 `complete`를 판정한다. 남은 조건은 분석 문서다. 이 브랜치가 고친 G1·G2·G3 증상을 아직 열린 구멍으로 적고 있다(1번).

대상: `verify/roadmap-proof-handoff` @ 5b28dd7e, 기준 e69cfbe6. 모델: Claude Opus. claude 실행 횟수(0/6, 3/3)는 다시 돌리지 않았으므로 주장으로만 다뤘다.

## 실행한 검사

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3866 passed, 3 skipped |
| `make lint`, `make typecheck` | All checks passed, mypy 54 files 이상 없음 |
| `git diff v4.34.2 HEAD --stat -- core hooks.json commands` | `commands/review.md`, `commands/roadmap.md`, `core/rules/RULES_DOCS.md` |
| `evals/changed_command_probes.py` | `roadmap-draft-spec-gate`, `roadmap-design-discovery-draft`, `roadmap-design-draft`, `intent-through-branch`, `intent-through-ask-headless` |
| 사전 등록 | c4afeca3(evals와 테스트만 바꿈)이 9b4ae86e보다 앞선다. 그 뒤로 check는 바뀌지 않았다(`git diff c4afeca3 HEAD -- evals tests/unit/test_eval_harness.py` 비어 있음) |
| 변이 | Proof check를 지우자 `test_roadmap_builds_on_a_draft_design_and_approves_it`가 red(1 failed, 2 passed). `git checkout HEAD -- evals/tasks.yaml`로 복원했고 status는 깨끗하다 |
| dry-run 작업 공간 | build ok. 설치된 `.claude/commands/sc/roadmap.md`에 새 Proof 문장이 있다 |
| 분석 문서 재집계 | 사용 표(15개: 12/1/2/0, complete 11·implementing 2·draft 1·approved-for-plan 1), enum 밖 status 11건(approved 3은 모두 `00-intent.md`, frozen 4, 기타 4), G8–G10 핸드오프, 인용 줄 번호: 모두 재현됨 |

직접 만든 문서로 Proof check를 돌린 결과(exit 0 = 통과):

| 문서 | exit | 맞는가 |
|---|---|---|
| `## Proof` 아래 `Result:`만 있음(sha 포함) | 1 | 맞음 |
| 펜스 코드 블록에 명령 | 0 | 맞음 |
| 뒤 공백 있는 `## Proof   `, CRLF 문서 | 0 | 맞음 |
| 꼬리말 없음 | 1 | 맞음 |
| `## Proof` 뒤에 `## Risks`가 옴(마지막이 아님) | 0 | 관대함 |
| `## Proof`가 펜스 코드 블록 안에만 있음 | 0 | 잘못 통과 |
| `` `<command>` → <expected> `` 자리표시 | 0 | 잘못 통과 |
| 명령 없이 `` Result: `abc1234` `` 줄에만 백틱 | 0 | 잘못 통과 |
| `## Proof:`, `### Proof` 제목 | 1 | 잘못 실패 |

## 발견

1. **Important — 분석 문서가 HEAD에서 거짓인 내용을 열린 구멍으로 적는다.**
   근거: 고친 증상이 현재형으로 남아 있다. G1 "`## Proof` 꼬리말은 없다", G2 "roadmap 핸드오프에는 `/sc:task`가 있다", G3 "review 태그는 `plan implement test troubleshoot`뿐이다". 구멍 표는 G1·G2를 아직 Important로 두고, 첫 문단은 "구멍은 roadmap 경로…에 있다", "고치기 전에 결정이 두 개 필요하다"고 쓴다. 부록 핸드오프 표의 roadmap(`implement task`)과 review(design 없음) 행도 옛 값이다. 이 브랜치의 "구현과 측정" 절과 맞지 않는다. 같은 문서가 G5에는 "해결됨"과 "아래는 d7f04869 시점의 기록이다"를 붙였는데, G1–G3에는 그런 표시가 없다.
   수정: 구멍 표에서 G1을 "부분 해결(9b4ae86e: Proof 추가, Evidence 규칙은 보류)", G2를 "해결됨(9b4ae86e)"으로 바꾼다. G3에는 "첫 증상 해결"을 적는다. 각 절 머리와 부록 표 캡션에 "d7f04869 시점"을 붙이고, 첫 문단을 결정과 구현이 끝난 상태로 고친다.

2. **Suggestion — roadmap의 `Evidence:` 규칙을 지키게 하는 곳이 없다(이 브랜치 이전 문구).**
   근거: `roadmap.md:17`은 "the implementing session checks the box only when Evidence cites the check"라고 쓴다. 이 문장은 roadmap 세션만 읽는다. 구현 세션은 `implement.md:19`("check a box only when the code backs it")를 따르고, Plan-Close (1)(`reflect.md:19`)은 박스가 체크됐는지만 본다. `implement.md`에서 `Evidence`는 0건이다. 그래서 `Evidence:` 줄이 빈 채로 `complete`까지 갈 수 있다. 서로 모순되지는 않는다. implement는 Evidence 기입을 막지 않고, 더 약한 규칙을 적용할 뿐이다. 소유자가 "가장 작은 범위"를 고르면서 보류한 부분이다(분석 문서 D1①).
   수정(택일): roadmap이 이 규칙을 문서 머리에 공유 규칙으로 적는다. 또는 문장을 빼고 implement의 박스 규칙에 맡긴다.

3. **Suggestion — `RULES_DOCS.md:84` 관문이 `--plan`과 "committed"를 말하지 않는다.**
   근거: :83은 `/sc:plan -> /sc:implement --plan: Plan document committed`이다. :84는 `/sc:roadmap -> /sc:implement: Roadmap tasks defined; implementation proceeds per task list`이다. 이번 수정은 "/sc:implement --plan runs it"(`roadmap.md:17`)에 기대므로, `--plan` 없이 구현하면 Proof는 돌지 않는다. roadmap.md가 `--plan`을 직접 적고 있어 모순은 아니다.
   수정: :84를 :83과 같은 모양으로 맞춘다. 단 core 변경이라 `make canary-gates` 대상이 된다.

4. **Suggestion — probe check가 관대하다.**
   근거: 위 표의 잘못 통과 세 가지와 잘못 실패 한 가지. 관찰된 실패 형태가 "빈 `## Proof` + `Result:`"였으므로, `Result:` 줄에 백틱을 넣은 자리표시가 3/3 안에 섞여도 check로는 가려낼 수 없다. 측정 쪽 기록은 세 run 모두 명령과 기대 출력을 적었다고 하지만, 이 판단은 check가 아니라 사람이 읽고 한 것이다.
   수정: 제목을 찾기 전에 펜스 블록을 지운다. 본문에서 `Result:` 줄을 뺀 뒤 백틱을 찾는다. 원하면 마지막 `## ` 절인지도 확인한다(roadmap은 "End the doc with"라고 쓴다). 사후 수정이므로 바꾸면 저장된 run을 다시 채점해 표를 고친다.

확인했지만 문제가 아닌 것:
- **review → design**: review의 handoff 태그는 scope마다 나눈 목록이 아니라 합집합이다. 이미 있던 `/sc:plan`도 spec·design 리뷰 뒤에만 맞는다. 그래서 `/sc:design`을 더해도 code·branch 리뷰에서 새로 생기는 오해는 `/sc:plan` 수준을 넘지 않는다. 더 좁은 대안은 Spec gate 단계 문장에서 안내하는 것인데, 그러면 D2(체인 기준)를 정해야 한다. 소유자가 D2를 보류했으므로 이번 변경 범위로는 태그가 맞다.
- **`/sc:task` 제거**: task flow는 plan 문서를 읽지도 쓰지도 않는다(증거는 TaskCreate 설명에 남긴다). roadmap → task로 안내하는 shipped 문장, README 행, help·recommend 매핑, `docs/index.html`, 테스트는 0건이다(`git ls-files`로 grep). roadmap `<outputs>`의 TaskCreate/TaskUpdate는 harness 도구라 별개다.
- **분석 문서의 정정 세 가지**: G1 수락 경로(`implement.md:19` "(accepted by user)"), G3 태그 순서(`brainstorm.md:83`), G6 `_GATE_ANCHORS`. 모두 맞다. 심각도 재조정도 저장소 관례(관찰된 실패 없음 → 두 shipped 파일이 어긋날 때만 Important)와 맞는다.

## roadmap 출력 계약·핸드오프를 적는 곳

| 위치 | 내용 | 일치 |
|---|---|---|
| `commands/roadmap.md:17` | 박스 + 빈 Evidence, `## Proof`, `--plan`이 `Result:` 기록, `status: draft` | 기준 |
| `commands/roadmap.md:18`, `:29-31` | 경로(05, 05<letter>-plan-workflow, docs/plans/-workflow-) | 일치 |
| `commands/roadmap.md:68` | `next="/sc:implement"` | 일치 |
| `commands/plan.md:16`, `:60` | plan 꼬리말 Proof = 명령 + 기대 출력 | 일치("as for a /sc:plan plan") |
| `commands/implement.md:13`, `:19` | 마지막 박스 뒤 Proof 실행, `Result:`. Evidence 없음 | 일치(2번) |
| `commands/reflect.md:19`, `commands/test.md:17` | Plan-Close, reflect로 보내기 | 05-plan·docs/plans는 일치. 05<letter> 변형은 아래 |
| `RULES_DOCS.md:13`, `:18`, `:24-25` | 05 슬롯 = plan·roadmap 산출물, 분할 시 꼬리말은 인덱스에 | 일치 |
| `RULES_DOCS.md:58` | plan `complete` = 박스 + Proof `Result:` | 일치 |
| `RULES_DOCS.md:82` | design → roadmap | 일치 |
| `RULES_DOCS.md:84` | roadmap → implement | 부분 일치(3번) |
| `design.md:62`, `estimate.md:50` | roadmap으로 들어오는 간선 | 일치 |
| `README.md:313`, `:692`, `commands/README.md:43`, `help.md:50`, `recommend.md:36` | 설명만, 핸드오프 없음 | 일치 |
| `commands/review.md:76` | `plan design implement test troubleshoot` | 일치 |
| `brainstorm.md:18`, `:20` / `README.md:298`, `:303`, `intent.md:20` | review 뒤 plan / review 뒤 design | 두 체인이 공존. D2 보류로 기록됨(G3 Low) |
| `CHANGELOG.md` [Unreleased] | Proof, task 제거, review → design | 일치 |
| `test_docs_ssot_guards.py:686-694` | 문장, roadmap 태그 == `[/sc:implement]`, review에 design | 일치 |
| `evals/tasks.yaml` roadmap-design-draft | Proof 절에 백틱 | 일치(관대함, 4번) |
| 분석 문서 G1–G3, 부록 표 | 옛 상태 | 불일치(1번) |

## 이 브랜치 밖

- **Important 후보 — `05<letter>-plan-workflow.md` roadmap이 Plan-Close 대상으로 이름이 불리지 않는다.** `reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87`은 plan 문서를 "a feature folder's `05-plan.md` or a `docs/plans/` plan"으로 정의한다. 기본 plan이 있을 때 roadmap이 쓰는 `05a-plan-workflow.md`는 여기에 들지 않는다. implement는 `complete`를 쓰지 않으므로, 글자 그대로 읽으면 `implementing`에서 나갈 길이 없다. 이 이름은 분할 plan의 단계 파일 패턴 `05<letter>-plan-<phase>.md`(`RULES_DOCS.md:13`)와도 겹친다. 수정: 정의를 "05-slot plan doc(05*-plan*.md)"으로 넓히거나 roadmap 변형의 이름을 바꾼다.
- **릴리스 canary**: v4.34.2 이후 `RULES_DOCS.md`도 바뀌었다(6d0985c8, 이 브랜치 아님). 그래서 `make canary-commands`만이 아니라 `make canary-gates`도 필요하다. 분석 문서의 "릴리스 때" 줄은 canary-commands만 적는다.
