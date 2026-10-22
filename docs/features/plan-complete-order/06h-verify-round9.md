---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 9 (06h)

**판정: 통과.** Critical·Important가 없다. 06g Important 1은 해결됐다(reflect:19 (3)에 모순 구절이 없다). r11 실제 run에서 reflect·intent-through 프로브가 모두 통과한다. 남은 것은 Suggestion 넷이다.

## 범위

- 대상: `b31415c1`(`feature/plan-complete-order` 머리). 비교 기준: `0bf95173`, `81360595`. 06g와 `git show 2a3498af`를 먼저 읽었다.
- 실행한 것(스크립트는 `$TMPDIR/pco/g9/`): 전체 게이트, 내 변이 26건(`mut12.py`)과 `mut10.py`·`g8/mut11.py` 재실행, 제안 앵커 확인(`anch9.py`, 되돌림), 재리뷰 정규식 06a `rg_mut`·06g `mine8`·내 12건(`rg/mine9.py`, HEAD 데이터), `_grade`로 내 문장 39개(`phr9.py`), 저장된 실제 run 61개 재채점(`regrade.py`, `result` 이벤트)
- 읽기만 한 것: 병행 canary `r11/cmds`(12 probe 모두 통과), `r11/x2`, `r11/x3`.
- 모델: Claude Opus, effort high

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3857 passed, 3 skipped**, 154.28s |
| `make lint` | All checks passed |
| `uv run ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

변이 뒤 트리는 깨끗하다.

## 규칙과 그 사본

| 규칙 | 사본 | 일치 |
|---|---|---|
| `complete`는 Plan-Close의 yes로만 | implement:19, reflect:19·46, RULES_DOCS:58·88, intent:20·22, README:318·335, CHANGELOG:15·16, `through_left_open`(tasks.yaml:862) | 일치 |
| 조건 (2): `Result:` 뒤 코드 커밋 없음 | reflect:19, RULES_DOCS:58·85, README:315·316, CHANGELOG:15 | 일치 |
| 수정에는 그 뒤 리뷰 round가 있다 | reflect:19 (3), implement:19, review:20, RULES_DOCS:86·88, test:17, README:316, CHANGELOG:15 | 일치. reflect의 모순은 사라졌다 |
| 되돌림(red 재실행, 조건 (3) 실패), README phase는 그대로 | reflect:19, implement:19, RULES_DOCS:31·58, CHANGELOG:15 | 일치. "phase 그대로"는 앵커가 없다(발견 1) |
| 상자 다 참 + `Result:` 없음 또는 sha 뒤 코드 → `/sc:implement --plan` | implement:13, reflect:19, CHANGELOG:15 | 일치 |
| round의 끝 | review:20, RULES_DOCS:86, CHANGELOG:15 | 일치 |
| `--through`: 수정 한 번, Critical이나 red가 남으면 멈춤, 남은 일은 Report로 | intent:20·22, implement:19, review:20, RULES_DOCS:86, README:335, CHANGELOG:15·17, tasks.yaml:858·1001(`max: 2`) | 일치. intent:20의 "Critical"은 앵커가 없다(발견 1) |
| review-due가 "닫을 수 있다"를 떨어뜨린다 | tasks.yaml:719–725 주석과 정규식, test_eval_harness:1324–1337 | 일치 |

## 1. `/sc:intent --through` 충돌

Run(intent:20)의 체인을 끝까지 따라갔다.

- **brainstorm → plan.** 이번 브랜치가 바꾼 문장이 없다.
- **implement --plan.** implement:19는 `complete`를 쓰지 않고 `Result:`만 쓴다.
- **branch review와 수정 한 번.** Run의 "re-run the Proof and rewrite `Result:`"는 implement:19 "Every later code change re-runs the Proof"와 같다. implement:19·review:20·RULES_DOCS:86이 "keeps its single fix round"로 재리뷰를 막는다. implement의 그 구절만으로는 수정 뒤 재리뷰가 허용되는 것처럼 읽힐 수 있다. 그러나 함께 로드되는 RULES_DOCS:86 "names the fix left unreviewed"와 intent:22가 그 해석을 닫는다(실제 run도 review 두 번).
- **test.** test:17은 지목만 한다.
- **reflect.** (3) 실패 → `/sc:review` 지목 → Run이 "leave the step Plan-Close names to the Report step". 셋 다 성립하면 제안만 하고 Report가 `complete`를 남긴다.
- **Report와 멈춤.** :22가 Plan-Close 단계와 merge·push를 남긴다. Critical과 red는 Run이 멈추고, 열린 Important는 Plan-Close를 거쳐 Report로 간다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 Run과 반대로 시키는 문장은 찾지 못했다. RULES_DOCS:88 "-> done"의 긴장은 06a–06g와 같다(브랜치 밖).

**실제 run(r11 `cmds`).** `intent-through-branch` 15/15: Report가 "it fails on the third condition … has had no second `/sc:review` round"라고 적고, 남은 일로 재리뷰 또는 면제, `complete`, merge·push를 든다. `intent-through-ask-headless` 16/16.

**프로브.** `through_left_open`은 feature 브랜치의 `05-plan.md`와 README만 본다. `_THROUGH_STATES`(test_eval_harness:1733)는 plan·README complete를 red, phase 파일을 green으로 고정한다. README를 빼는 변이(Y1)는 red다.

## 2. 06g 발견의 해결

| 06g | 판정 | 근거 |
|---|---|---|
| 1 Important, (3)의 자기 모순 | **해결** | reflect:19 "…or shipped content has had a /sc:review round after it, or the user waived that round", 앵커 test_docs_ssot_guards:586, 05-plan:133·142. Deviations 기록 대신 Step 1 주석 |
| 2 Suggestion, lookbehind | **해결** | tasks.yaml:725에 문장 첫머리 정규식이 들어갔고, test_eval_harness:1330–1333에 사례 둘이 들어갔다. 내 올바른 답은 9/10 통과(떨어진 하나는 억지 문장 "All three hold except (3)")다 |
| 3 Suggestion, 앵커 셋 | **해결, 일부 남음** | :564·565·608. 06g의 A1·A2·C3은 이제 red다. 군더더기 :593 "back to `implementing`"은 남았다(발견 4) |
| 4 Suggestion, 규칙 2 실패 사례 | **해결** | test_eval_harness:1425. G4가 red다 |
| 5 Suggestion, 옛 수치 | **해결, 같은 종류 하나 남음** | :162에 "(뒤의 재채점으로 대체됨)"이 붙었다. 그러나 :160(Phase 10의 마흔여덟 run, 23/23·22/23, lookbehind 서술)도 Phase 11 Step 3으로 대체됐는데 표시가 없다(발견 3) |

**Plan-Close에 출구 없는 고리가 있는가.** 없다.

- **(3) 실패.** `/sc:review`로 간다. 발견 없는 round, 수락, 면제(review:20) 가운데 하나로 끝난다. 새 발견은 고친 뒤 다시 (3)으로 돌아오고, 같은 출구를 가진다.
- **열린 상자, `Result:` 없음, sha 뒤 코드.** `/sc:implement --plan`으로 간다. implement:13이 상자가 다 찬 계획을 "the Integrate step's Proof re-run"으로 바로 보낸다. Integrate(:19)가 Proof를 돌려 docs-only 커밋으로 `Result:`를 다시 쓰고, red이면 `implementing`으로 되돌린다. 그 커밋은 코드를 바꾸지 않으므로 (2)가 성립한다.
- **red와 열린 발견.** 사용자가 수락하거나 고친다. 고친 것은 (3)의 리뷰로 간다.

**`reflect-plan-close` 성공 정규식(`_grade`).**

- 내 제안 12개 중 9개가 통과한다. 놓친 셋은 "commit the plan and README as complete", "mark it done", "ready for `complete`"다.
- 거절 10개 중 4개가 잘못 통과한다("Better to wait before setting it complete", "premature", "instead of marking", "must wait").
- 둘 다 tasks.yaml:680–685 주석이 적은 한계다. 쓰기는 상태 check 둘이 지킨다.
- 실제 run: 닫을 수 있는 답 30/31(떨어진 것은 바꾸기 전 `before/b1`), review-due 29/30(오독 run `r8/x3`). 정규식은 바꾸자고 하지 않는다.

**review-due 정규식.** 잘못된 답 7개 중 2개가 통과한다("Plan-Close passes. Optionally run another review…", "It meets all three conditions…"). 판정 문장의 꼴이 "all three … hold/are met"가 아니면 잡히지 않는다(발견 2).

## 3. 잃은 규칙 (0bf95173 → 81360595 → HEAD)

81360595 → HEAD의 shipped 변경은 reflect:19의 구절 하나("after the last /sc:review round ")를 지운 것뿐이다(`git diff --stat 81360595 HEAD`).

"a fix to [a review finding]"은 정의상 리뷰 round 뒤에 오고, "has had a … round after it"이 마지막 round 뒤의 수정만 걸러 낸다. round 2의 새 발견도 같은 문장으로 round 3을 요구한다. 잃은 규칙은 없다.

0bf95173 → HEAD 단어 diff에서 06g 3절의 표가 그대로 맞다. 따로 확인한 것:

- reflect의 "naming the last commit that changed code"는 "no commit after its sha changes code"로 바뀌었다. 같은 조건이고, 옛 문구는 `stale` 검사가 막는다.
- reflect의 "→ send the work to /sc:test first"는 `/sc:implement --plan`으로 바뀌었다. 감사 1의 고리를 고친 것이다(Deviations :177).
- review의 "with no claim that they are fixed"는 RULES.md:10 Intent Propagation이 그대로 싣는다.
- RULES_DOCS:86 round의 끝("leftover Suggestions …")은 review:20이 싣는다.

Deviations의 세 구절(:178)과 두 구절(:175)은 맞다. 목록 밖에서 잃은 규칙은 찾지 못했다.

## 4. 누더기 여부

길이(byte, 0bf95173 → 81360595 → HEAD):

| 단계 | 0bf95173 | 81360595 | HEAD |
|---|---|---|---|
| Plan-Close | 875 | 1393 | **1361** |
| implement Integrate | 2029 | 1635 | 1635 |
| implement Load | 257 | 417 | 417 |
| intent Run | 987 | 1065 | 1065 |
| intent Report | 518 | 633 | 633 |
| review Process | 691 | 651 | 651 |
| RULES_DOCS 전체 | 11834 | — | 11703 |

- 이번 round에서는 줄기만 했다(−32).
- Plan-Close의 성장(+486)은 (3)의 정의, 실패마다의 회송, `complete` 계획의 되돌림이다. `/sc:reflect`는 RULES_DOCS를 로드하지 않으므로 reflect 안에 있어야 한다. 정당하다.
- intent Run/Report의 성장(+193)은 Plan-Close가 지목한 단계를 넘기는 절 둘이다. 정당하다.
- 처음 읽는 사람으로 읽었을 때 테스트용 절, 이력 서술, 겹친 괄호는 없다. "a fix waiting for review"는 같은 문단의 (3) 두 번째 절을 가리킨다. "every fix to one that changed …"의 관계절이 "one"(발견)에 붙을 여지가 있지만, 발견은 코드를 바꾸지 않으므로 오독은 어렵다(실제 run 셋 모두 바르게 읽음).

## 5. 새 테스트 가드

**내 26건(`g9/mut12.py`): red 3, green 23.**

- **red:**
  - T3: "write it when all three hold"
  - S1: "unless asked"(약화어 목록)
  - Y1: `through_left_open`에서 README 삭제
- **green, 규칙 낱말이 빠지거나 뒤집혀 다른 사본과 모순이 되는 것(발견 1):**
  - **T1** intent Run 멈춤에서 "a Critical finding or" 삭제. README:335와 어긋난다
  - **P3** Plan-Close "the README `phase:` unchanged" → "with it"
  - **I1** implement "the README `phase:` never moves back" → "moves back with it". RULES_DOCS:31과 어긋난다
  - **M1** README `--through`에서 "any review round its fix still needs" 삭제. intent:22와 어긋난다
- **green, 조건을 덧붙이거나 좁히는 것(19건).** canary나 리뷰의 몫이다(Phase 7 Deviations의 이유와 같다).
  - canary가 잡는 것: P1 "or at once in a headless run"(상태 check), I2 "and then reviews it again"(`max: 2`), T2 "which the run does itself"(`through_left_open`), G3 "or /sc:implement after a green Proof"(`implement-proof-green`)
  - 나머지: P2 "you can propose", P4 "or the Proof stayed green", P5 "when the user wants one", P6 "or else the plan closes anyway", P7 "where present", I3 "check a box when its task is started"(이 브랜치 이전 규칙), I4 "when the user asks for it", I5 "or the next run is green", V1 "Suggestions are reviewed again", V2 "or after three rounds", G1 "evidence welcome", G2 "or listed", S2 "or the user says it is", M2 "until the Proof is green", X1 "for Suggestions"

**제안 앵커 넷(`anch9.py`)**: 165 passed, T1·P3·I1·M1 모두 red. 06g 3과 같이 규칙 낱말이 빠진 곳만 골랐다.

**06c 4의 거절분(약화어 목록 확장).** 이유에 동의한다. green 23건 중 순수한 약화어는 P2("can") 하나이고, 나머지는 덧붙인 조건이나 뒤집기라 낱말 목록으로 막히지 않는다.

**앵커가 문구를 지나치게 얼리는가.** 대체로 아니다.

- :586은 절 전체를 얼리지만, 그 절이 곧 규칙이다.
- 예외는 군더더기 :593이다. 같은 목록의 :583 "is proposed back to `implementing`"에 포함되므로 지키는 것이 없다(발견 4).
- review Process의 "Suggestions"는 느슨하다(V1). 출구가 있는 비효율이라 앵커는 권하지 않는다.

**앞선 묶음(HEAD).**

- `mut10.py`: red 9, SKIP 1(옛 lookbehind 원문 없음). Phase 11 Step 3의 주장대로다.
- 06g `mut11.py`: red 11, green 14. 06g의 red 7에 A1·A2·C3(새 앵커)과 B4(앵커가 "or the user waived that round"까지 늘어남)가 더해졌다. green 14는 덧붙인 조건과 좁힘이다. 다만 G1(README reflect 행 "proposes marking" → "marks")은 규칙 낱말의 뒤집기라 발견 1에 넣었다.

## 6. 줄인 채점 데이터

- 06a `rg_mut`(HEAD 데이터): red 14, green 5. green 다섯은 주장대로 again, another, second, still, due의 단독 삭제다.
- 06g `mine8`: red 3(G1, **G4**, G6), green 7. G4는 06g 4의 반영으로 red가 됐다.
- 내 12건(`mine9.py`): red 11, green 1(H1, 규칙 1 주제어 `round` 삭제. 단독 표지 삭제와 같은 종류다).
  - red인 넓힘: 규칙 2 창 25→200, 규칙 3 창 10→60, 절 구분에서 `,` 삭제, 규칙 1에 `is` 추가
  - red인 삭제: nobody, n't, before merg, next, unreviewed, re-review, F-1

규칙마다 남은 사례:

| 규칙 | 삭제를 잡는 통과 사례 | 넓힘을 잡는 실패 사례 |
|---|---|---|
| 1(표지) | test_eval_harness:1388–1396 | :1418 "it is fixed"(H10) |
| 2(요청 동사, next) | :1398–1400 | :1422(H3), :1425(G4) |
| 2b(then) | :1407 | :1426(X5·X6), :1418(G1) |
| 3(부정) | :1402–1405 | :1424(G6·H6) |

빈 칸은 없다. 05a:28·32의 known misses는 테스트에서 옮겨 간 그대로다.

## 7. 기록

- **CHANGELOG:15**는 shipped와 맞는다: 조건 셋과 yes, sha 뒤 코드 → `/sc:implement --plan`, round의 끝, 되돌림 계기와 "(the README phase stays)", `--through`가 남기는 재리뷰와 `complete`. 상자나 `Result:`가 빠졌을 때의 회송은 적지 않지만, 사용자용 요약으로 충분하다.
- **CHANGELOG:17**은 tasks.yaml:858·862·1001·1003과, **README:315–335**는 shipped와 맞다.
- **feature README**와 **05-plan**(`implementing`, Integration 넷과 Phase 3 Step 2 열림)은 맞다. Phase 11의 수치(쉰여덟 run, 28/28, 27/28, 0/1; `mut10` 9 red + SKIP)는 다시 세어 맞다.
- **05-plan:160**은 대체됐는데 표시가 없다(발견 3). :131 "lookbehind를 썼고"는 Phase 10 당시의 사실이라 거짓이 아니다.
- 분석 문서, gap 분석 D("진행"), 05a는 맞다.

## 발견

### 1. Suggestion: 규칙 낱말이 빠지는 사본 네 곳에 앵커가 없다

T1·P3·I1·M1(과 06g G1)은 다른 사본과 모순이 되는데 green이고, canary도 재지 않는다. test_docs_ssot_guards.py(확인: 165 passed, 넷 모두 red):

- :600 `"a red Proof remains after one fix round"` → `"a Critical finding or a red Proof remains after one fix round"`
- :583 `"is proposed back to `implementing`"` → `"is proposed back to `implementing`, the README `phase:` unchanged"`
- "implement Integrate" 목록의 `"sets it back to `implementing`"` 다음에 `"the README `phase:` never moves back"`를 더한다
- :617 `"README --through": ["leaves marking the plan complete"]` → `["leaves marking the plan complete, any review round its fix still needs"]`
- (같은 종류, 06g G1) "README reflect row"의 `"which you confirm"` → `"it proposes marking the plan `complete`, which you confirm"`

### 2. Suggestion: review-due 거절 check가 "all three … hold/are met" 꼴만 본다

재현(`g9/phr9.py`): "All three conditions are satisfied. I propose marking the plan complete."와 "Every Plan-Close condition holds; shall I set the plan complete?"는 rereview를 같이 말하면 통과한다. 실제 오독 run(`r8/x3`)의 꼴은 잡힌다.

후보: tasks.yaml:725를 `'(?im)(?:^|[.!?;:]\s+)[\s>*_-]*(?:all (?:three|3) (?:Plan-Close )?(?:conditions )?(?:hold|are (?:met|satisfied))|(?:every|each) (?:Plan-Close )?condition (?:holds|is (?:met|satisfied)))\b'`로 바꾼다.

- 저장된 review-due run 30개에서는 지금과 같이 `r8/x3` 하나에만 맞는다(`g9/cand.py`).
- "Not every condition holds"와 "Once every condition holds"는 통과한다.
- 낱말 목록을 늘리는 일이니, 받아들이지 않으면 한계를 주석에 남긴다.

### 3. Suggestion: 05-plan Deviations :160의 수치가 대체됐는데 표시가 없다

:160(Phase 10, 마흔여덟 run, 23/23·22/23, lookbehind 서술)은 Phase 11 Step 3(쉰여덟 run)과 문장 첫머리 정규식으로 대체됐다. :162처럼 "Phase 9 뒤 canary(뒤의 재채점과 Phase 11 정규식으로 대체됨)"라고 표시한다.

### 4. Suggestion: 군더더기 앵커 :593

reflect Plan-Close의 `"back to `implementing`"`은 같은 목록 :583의 부분 문자열이라 지키는 것이 없다(06g 3에서 남았다). 지운다.

## 변이 표

| 묶음 | 건수 | red | green | SKIP |
|---|---|---|---|---|
| 내 가드 `g9/mut12.py` | 26 | 3 | 23(규칙 모순 4: T1·P3·I1·M1) | 0 |
| 제안 앵커 넷 적용 뒤 T1·P3·I1·M1 | 4 | 4 | 0 | 0 |
| 06g `g8/mut11.py` | 25 | 11 | 14 | 0 |
| 구현자 `mut10.py`(주장 9 red + SKIP) | 10 | 9 | 0 | 1 |
| 재리뷰 정규식 06a `rg_mut` | 19 | 14 | 5(주장대로) | 0 |
| 06g `mine8` | 10 | 3 | 7 | 0 |
| 내 재리뷰 정규식 `mine9` | 12 | 11 | 1 | 0 |
| 내 문장: plan-close 제안 / 거절 | 12 / 10 | — | 통과 9 / 잘못 통과 4 | — |
| 내 문장: review-due 올바른 답 / 잘못된 답 | 10 / 7 | — | 통과 9 / 잘못 통과 2 | — |
| 실제 run: plan-close / review-due | 31 / 30 | — | 30 / 29(빠진 것 `before/b1`, `r8/x3`) | — |

## 이 브랜치 밖

- RULES_DOCS:88 "-> done"과 `--through`의 끝 사이의 긴장(06a–06g와 같다).
- 리뷰 round·수락·면제를 기록하는 곳이 정해져 있지 않다(세션이 바뀌면 (3)의 근거가 사라질 수 있다).
- 제안·거절을 낱말로 읽는 채점의 한계. 쓰기는 상태 check가 지킨다.
- 이 계획을 닫기 전에 남은 일: Phase 3 Step 2와 Integration 넷의 상자, `## Proof` 아래 `Result:` 줄(아직 없다). Plan-Close (1)·(2)가 이것을 요구한다.
