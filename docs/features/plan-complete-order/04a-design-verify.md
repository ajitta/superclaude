---
status: complete
revised: 2026-10-22
---

# 04-design 독립 검증

**판정: 권고 수정.** `complete`를 Proof 뒤에서 떼어 내는 B의 방향은 맞다. 그러나 B는 reflect가 조건을 보고 쓰게 하고 `--through`에서는 묻지 않고 쓰게 한다. 이것은 소유자 자신의 완료 기준보다 이르다(81776c29 "completion is the owner's call", review-reflect-gates `05-plan.md:192`). `intent.md:20`과도 충돌한다.

## 범위

- 대상: `docs/plan-complete-order` 머리 e6a68adb의 `04-design.md`. 검증자: Claude Opus, effort high.
- 읽은 것: `implement.md`, `reflect.md`, `test.md`, `intent.md`, `promote-feature.md`, `cleanup.md`, `RULES_DOCS.md`, `RULES_QUALITY.md:9`, `context_loader.py:181-195`, `evals/tasks.yaml:440-700`, `test_plan_checklist.py`, `test_docs_ssot_guards.py:514-660`, `test_eval_harness.py:1128-1445`, README `:285-335`, `docs/index.html`(grep), CHANGELOG, 2026-10-20 감사와 그 검증, 분석 문서 D, review-reflect-gates의 `05-plan`·`05a`·`06b`, 세션 메모리 3개, `git log`/`git show` 81776c29·f1c067b9·6cf3d0d2, 최근 feature 12개의 phase와 plan status.
- 실행: grep과 git만 했다. 보고서를 쓴 뒤 `uv run pytest tests/unit/test_docs_ssot_guards.py tests/unit/test_cross_references.py -q`: 193 passed.

## 인용 확인

| 인용 | 판정 |
|---|---|
| `implement.md:19` Integrate, "a red re-run" | 맞음 |
| `RULES_DOCS.md:31-33` phase 매핑, `:33` | 맞음 |
| `RULES_DOCS.md:39` archive | 맞음. 다만 이 경로를 읽는 커맨드는 없다(grep). 사람만 읽는다 |
| `RULES_DOCS.md:58` 진입 조건, `:61-62` enum·마이그레이션 | 맞음 |
| `RULES_DOCS.md:86` 재리뷰 종료 조건, `:87` test→reflect | 맞음 |
| `reflect.md:45` bounds | 맞음 |
| `test.md:17` Report | 맞음 |
| `README.md:315`, `:318` | 맞음. `:318`은 `_GATE_PHRASES`("README reflect row")가 고정한다 |
| `session_2026-10-21_master.md:30` | 맞음 |
| 05a `test-reflect-gate-complete` Linux sonnet low 3/3 | 맞음(`05a:24,27`) |
| 06b 발견 5 | 맞음(`06b:59`) |
| 감사 §2 3단계 상태 기각 "이유는 셋" | 틀림. 감사 `:31`의 이유는 ①–④다. `test_plan_checklist.py`는 ①의 일부다. ③은 reflect, ④는 리더(`promote-feature.md:18`, R02)다 |
| 감사 §2 reflect 상태 전이 기각 = ②·③ | 맞음. 다만 같은 행(`:34`)의 "reflect의 역할(`reflect.md:8`)은 유지한다"를 빠뜨렸다 |

## 발견

### 1 (Important) B의 작성자와 시점이 소유자의 기존 결정과 어긋난다

- 근거: f1c067b9(2026-10-21)는 reflect 판정 **뒤에** 계획과 README를 `complete`로 바꿨다. B가 그대로 만들 상태다. 소유자는 같은 날 81776c29로 되돌렸다("completion is the owner's call"). 그 뒤 독립 검증 다섯 round에서 수정 커밋 다섯 개가 나왔다(93533db9..3b968d05). 최종 기준은 "독립 검증이 Critical·Important 없이 끝나면 complete"였다(`05-plan.md:192`, `session_2026-10-22_claude-box_master.md:21`). 이 기준에서 reflect는 마지막 게이트가 아니다. 완료는 소유자가 정한다.
- 고칠 것: reflect는 조건을 확인하고 `complete`를 **제안**한다. 사용자가 명시적으로 답했을 때만 쓴다. "소유자가 정할 것" 2의 ★를 "항상 묻는다"로 바꾼다. 문제 절에 이 사례를 가장 직접적인 증거로 넣는다.

### 2 (Important) `--through` 예외가 B가 본뜬 규칙과 반대다

- 근거: B는 "Persist 단계와 같은 방식"으로 묻고, `--through`에서는 "요청이 승인"이라고 쓴다. 그런데 `intent.md:20`은 `--through`에서 "reflect's Persist → propose, write nothing"이다. 또 `--through`는 수정 round가 하나뿐이고, 그 수정은 리뷰를 받지 않는다(`RULES_DOCS.md:86`). 그래서 Critical·Important 수정이 한 번이라도 있었으면 B의 셋째 조건은 맞지 않는다. 바뀌는 파일 목록에 `intent.md`와 README `:335`가 없다.
- 고칠 것: `--through`에서는 쓰지 않는다. `intent.md:22` Report의 "steps left to the user (merge, push)"에 계획 `complete`를 더한다. 파일 목록에 `intent.md:20,22`와 `README.md:335`를 넣는다.

### 3 (Important) B에도 되돌림 경로가 필요하다

- 근거: B는 "`complete` 뒤의 코드 변경은 다음 feature"라서 red re-run 경로를 "대부분 쓸 일이 없다"고 본다. 이 저장소의 기록은 반대다. 발견 1의 다섯 수정 커밋은 모두 같은 feature 안에 있다. README phase도 실제로 한 번 되돌아갔다(81776c29, `phase: complete → implementing`). 이것은 `RULES_DOCS.md:31`과 맞지 않는다.
- 고칠 것: A의 둘째 항목을 B에 넣는다. `complete` 뒤에 그 계획의 작업에서 Critical·Important가 나오면, 수정의 첫 커밋이 계획을 `implementing`으로 되돌린다. README phase를 어떻게 할지도 적는다. 그대로 두거나, 소유자의 81776c29를 규칙으로 올린다. 어느 쪽이든 명시한다.

### 4 (Important) `implement-proof-fail`이 B에서는 아무것도 재지 않는다

- 근거: `tasks.yaml:463-466`의 두 `cmd_ok`는 status와 phase가 `complete`가 아니면 통과한다. B의 implement는 `complete`를 쓰지 않으므로, Proof가 red든 green이든 어떤 run이든 통과한다. "그대로 통과해야 한다"(`04-design.md:51`)는 맞지만 판별력이 없다. 이 check를 고정하는 `test_eval_harness.py:1128` 테스트도 같다.
- 고칠 것: check를 바꾼다. `Result:` 줄이 green을 주장하지 않거나 실패를 적었는지, 그리고 "(accepted by user)"가 없는지 본다. 새 reflect 프로브에 "red `Result:`면 `complete`를 제안하지 않는다"를 넣는다.

### 5 (Important) reflect 세션은 RULES_DOCS를 읽지 않는다

- 근거: RULES_DOCS 트리거(`context_loader.py:191`)에 reflect·implement·test·review가 없다. 그래서 이 저장소는 그 커맨드들에 게이트 문장을 그대로 싣는다(`test_docs_ssot_guards.py:515-517`). B의 조건은 "`RULES_DOCS.md:58`의 조건", "`:86`의 종료 조건"처럼 참조로만 적혀 있다. `/sc:reflect` 세션에는 그 본문이 없다. A가 `:58`에 더하는 문장도 implement·test·reflect 세션에는 실리지 않는다. 이 점은 A에 대한 04의 비판을 뒷받침한다.
- 고칠 것: `reflect.md` 한 단계에 세 조건을 그대로 쓴다. 그 문장을 `_GATE_PHRASES`에 ("reflect <단계>", …)로 더한다. 04의 "drift test"를 이 이름으로 적는다.

### 6 (Suggestion) 리더 목록과 앞선 결정의 요약을 바로잡는다

- 빠진 리더: `promote-feature.md:18`(phase = furthest stage), 다음 세션의 R02(`RULES_QUALITY.md:9`, 감사 ④), `intent.md:22` Report (2), 이 저장소의 `test_plan_checklist.py`.
- archive는 커맨드가 읽지 않는다. 사람만 읽는다.
- 릴리스 습관은 이미 `complete`, 리뷰, 재리뷰, reflect를 따로 확인한다(`session_…master.md:30`). 그래서 A의 "남는 것" 셋째 항목은 A의 비용이 아니다.
- reflect 기각 행의 "역할 유지"(`reflect.md:8`)에 답한다. B의 reflect는 `git log`와 `Result:`만 읽고 Proof를 다시 돌리지 않는다. `Result:` 뒤에 코드 커밋이 있으면 `/sc:test`로 돌려보낸다. 이렇게 적으면 역할과 충돌하지 않는다.

### 7 (Suggestion) split plan과 `:58`의 작성자 표기

- `implement.md:19`에서 phase 파일은 끝나면 `complete`다. B에서 index만 기다리면, 같은 값이 phase 파일에서는 "작업 끝", index에서는 "게이트 끝"을 뜻한다. B는 phase 파일이 지금처럼 `complete`이고 index만 기다린다고 명시해야 한다.
- `RULES_DOCS.md:58`의 "(/sc:implement Integrate step)"는 작성자를 implement로 적는다. B에서는 reflect와 사용자로 바꿔야 하는데, 04는 이 줄의 변경을 적지 않았다.

### 8 (Suggestion) 함께 거짓이 되는 문장

- `tasks.yaml:499-500`·`:589`의 주석("the docs commit /sc:implement makes", "implement.md never moves it back")이 B에서는 거짓이다. `test_eval_harness.py:1427`의 docstring과 CHANGELOG `[Unreleased]` 넷째 항목도 같다.
- 프로브는 남기되 "옛 설치나 손으로 쓴 `complete`"로 문구를 바꾼다.

### 9 (Suggestion) 릴리스 범주

- 근거: 이 저장소에서 minor는 `Added`(새 커맨드·플래그, 4.33.0·4.34.0)를 실었다. 상태 전이를 옮긴 변경은 패치였다. 4.33.2는 `/sc:plan`이 design doc을 `draft → approved-for-plan`으로 옮기게 한 변경을 `Changed`로 실었다. Upgrade notes는 패치에도 있다(4.23.1, 4.26.1).
- 고칠 것: 패치 `Changed`와 upgrade note로 하거나, minor인 이유를 적는다. upgrade note 내용: 진행 중인 계획은 녹색 Proof 뒤에도 `implementing`에 머문다. 닫으려면 `/sc:reflect`를 돌리고 답한다.

### 10 (Suggestion) 놓친 안 D: 게이트를 계획의 상자로

- 근거: 소유자의 계획은 이미 이렇게 한다. review-reflect-gates `05-plan.md:183-193` "## Integration (커밋 아님)"에는 리뷰 round, reflect, "계획 `complete`" 상자가 있다. session-memory-multi-machine `05-plan.md:128-129`도 그렇다. "상자가 전부 체크되어야 `complete`"(`RULES_DOCS.md:58`, `implement.md:19`)가 이미 완료를 미룬다. 이 저장소에서는 `test_plan_checklist.py`가 기계적으로 검사한다.
- 아래 비교를 보라.

## 안 비교

| | A | B(04 원안) | B′(권고: B + 사용자 답 + 되돌림) | D(게이트 상자) | C |
|---|---|---|---|---|---|
| 독자가 보는 것 | Proof 직후 `complete`. 뜻은 implement·test·reflect 세션에 안 실린다(발견 5) | reflect 뒤 `complete`. 독립 검증 전이라 소유자 기준보다 이르다(발견 1) | 사용자가 정한 때 `complete`. 그 전에는 `implementing`과 `Result:` | 남은 게이트가 상자로 보인다. 마지막 상자 전에는 `implementing` | 지금과 같다 |
| 바뀌는 파일 | RULES_DOCS, implement, guard 한 줄, CHANGELOG | implement, reflect, RULES_DOCS, README 2행, tasks.yaml, 테스트, CHANGELOG | B + `intent.md:20,22`, README `:335`, `_GATE_PHRASES` | plan.md 템플릿, implement(상자 체크 주체), review/test/reflect 또는 사용자 | 없음 |
| 앞선 결정 | 충돌 없음. 되돌림은 phase를 두고 status만 바꾼다 | 감사 ③은 풀렸다. 81776c29와 `intent.md:20`과는 충돌한다 | 감사, 81776c29, `intent.md:20`과 맞는다 | "code backs it"(`implement.md:19`)와 충돌한다. 기본 표를 늘리는 것은 감사 §2 §7 기각과 같은 결의 비용이다 | — |
| 프로브 | 되돌림 check 하나 | proof-fail 판별력이 사라진다(발견 4). 새 probe 2 | B + proof-fail check 교체. reflect는 headless에서 쓰지 않는다 | `test_plan_checklist.py`가 이 저장소에서만 잰다. 사용자 저장소에는 장치가 없다 | 없음 |
| 릴리스 | core + 커맨드 → `canary-gates`, `canary-commands`. 패치 | 같음. 04는 minor라 했다(발견 9) | 같음. 패치 + upgrade note | plan 템플릿 → `canary-commands`. 패치 | 없음 |

D는 단독으로 더 작지 않다. 상자를 누가 체크하고 마지막에 누가 `complete`를 쓰는지는 B와 같은 문제로 남는다. 하지만 B′의 덧붙임으로는 값싸다. plan.md 푸터에 선택 항목으로 "## Integration" 상자를 두면, 남은 게이트가 사람과 다음 세션에 보인다.

## 권고

B′를 권한다.

- implement는 `Result:`만 쓴다.
- reflect는 세 조건을 본문에 그대로 싣고 확인한다. 그리고 `complete`를 제안만 한다. 쓰는 것은 사용자의 답이 있을 때뿐이다. `--through`와 headless에서는 쓰지 않고, Report의 "steps left to the user"에 넣는다.
- `complete` 뒤의 Critical·Important에는 A의 되돌림 경로를 둔다.
- `implement-proof-fail`은 `Result:` 내용으로 채점한다.
- D의 Integration 상자는 소유자가 고를 선택 항목으로 둔다.
