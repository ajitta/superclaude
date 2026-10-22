---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 8 (06g)

**판정: 조건부 통과.** 06f의 Important는 실제 run에서 해결됐다(81360595 batch 10/10). 그러나 06f 3을 고쳤다는 기록이 거짓이다(발견 1, Important). Plan-Close (3)에 "after the last /sc:review round"가 남아 자기 모순이 그대로인데, Phase 10과 커밋 제목은 "reads literally"라고 적는다. 고칠 것은 구절 하나, 앵커 하나, 기록 한 줄이다.

## 범위

- 대상: `81360595`(`feature/plan-complete-order` 머리). 비교 기준: `0bf95173`, `c862806d`. 06f와 `git show 510108c6 45a2fc59`를 먼저 읽었다.
- 실행한 것:
  - 전체 게이트
  - 내 가드 변이 25건(`$TMPDIR/pco/g8/mut11.py`). green 18건은 한꺼번에 적용해 전체 suite로 다시 확인했다(`combo.py`)
  - 앞선 묶음 재실행: `mut9.py`, `mut10.py`, 06f `r10/mut10.py`, 06e `r9/mut9.py`
  - 재리뷰 정규식 변이: 앞선 묶음 다섯(`r10/rg` 사본이 HEAD와 같음을 확인)과 내 10건(`g8/rg/mine8.py`)
  - `_fixture_ws`/`_grade`로 내 문장 33개 채점(`g8/phr.py`)
  - 저장된 실제 run 58개 재채점(`reflect-plan-close*.stream.jsonl`의 `result`, `g8/regrade.py`). 그중 81360595 batch는 `r10/*` 10개
  - 제안 수정은 잠시 적용해 확인하고 되돌렸다
- 실행 안 함: canary, `claude -p`. 병행 batch `r10/*`, `r10b/cmds`(OAuth 만료로 ERR였던 다섯 probe 재실행)는 읽기만 했다.
- 모델: Claude Opus, effort high

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3857 passed, 3 skipped**, 142.48s |
| `make lint` | All checks passed |
| `uv run ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 규칙과 그 사본

| 규칙 | 사본 | 일치 |
|---|---|---|
| `complete`는 Plan-Close의 yes로만 | implement:19, reflect:19·46, RULES_DOCS:58·88, intent:20·22, README:315·318·335, CHANGELOG:15, `through_left_open` | 일치 |
| 조건 (2): `Result:` 뒤 코드 커밋 없음 | reflect:19, RULES_DOCS:58·85, README:315·316, CHANGELOG:15 | 일치 |
| 수정이 재리뷰를 기다린다 | reflect:19 (3), implement:19, review:20, RULES_DOCS:86, test:17 "after the last review round", CHANGELOG:15 | 뜻은 일치. reflect의 문구가 자기 모순이다(발견 1) |
| 되돌림 | reflect:19, implement:19, RULES_DOCS:58, CHANGELOG:15 | 일치(06f와 같다) |
| `Result:` 없음, sha 뒤 코드 → `/sc:implement --plan` | implement:13, reflect:19, CHANGELOG:15 | 일치 |
| 재리뷰 round와 멈춤 | review:20, implement:19, RULES_DOCS:86, test:17, README:316, CHANGELOG:15 | 일치 |
| `--through`: 수정 한 번, 남은 일은 Report로 | intent:20·22, implement:19, review:20, RULES_DOCS:86, README:335, CHANGELOG:15, tasks.yaml `max: 2`·`through_left_open` | 일치 |
| review-due가 "닫을 수 있다"를 떨어뜨린다 | tasks.yaml:719–724 주석 ↔ 정규식, test_eval_harness:1324–1335 | 실제 run에서 일치. 손 문장에서는 어긋난다(발견 2) |

## 1. `/sc:intent --through` 충돌

Run(intent:20)의 체인을 끝까지 따라갔다.

- **branch review.** review:20, implement:19, RULES_DOCS:86이 "keeps its single fix round"로 끝난다. Run의 "re-run the Proof and rewrite `Result:`"는 implement의 "Every later code change re-runs the Proof"와 맞는다.
- **test.** test:17은 리뷰 안 된 수정을 지목만 한다. RULES_DOCS:86 "its /sc:test step names the fix left unreviewed"와 맞는다.
- **reflect.** (3)이 실패하고 Plan-Close가 `/sc:review`를 지목한다. Run의 "propose, write nothing, and leave the step Plan-Close names to the Report step"이 그것을 Report로 넘긴다.
- **Report.** :22가 "the step Plan-Close named"를 남은 일에 넣는다.
- **멈춤.** 열린 Important는 Plan-Close가 사용자에게 넘기고, Run은 그것을 Report에 남긴다. Critical과 red는 Run이 멈춘다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 찾지 못했다. 남은 긴장은 RULES_DOCS:88 "-> done"(gap을 고치거나 수락)뿐이다. 06a–06f와 같다(브랜치 밖).

**실제 run(`r10b/cmds`, 81360595).**

- `intent-through-branch` 15/15: "The fix in `879e1bd` has not had a second review round … Next you would run another `/sc:review` round"
- `intent-through-ask-headless` 16/16: Important 0, "all three conditions hold, and it needs your yes"

**프로브.** `through_left_open`(tasks.yaml:861)은 index와 README만 본다. `_THROUGH_STATES`(:1728)가 plan·README complete는 red, phase file은 green으로 고정한다. 맞다.

## 2. 06f 발견의 해결

| 06f | 판정 | 근거 |
|---|---|---|
| 1 Important, 조건문 답을 거절로 채점 | **실제 run에서 해결, 손 문장은 일부** | 81360595 review-due 5/5. 저장된 29개 중 떨어진 것은 `r8/x3`(오독 run) 하나. 그러나 lookbehind는 once·if·when·until 바로 뒤만 뺀다. 06f가 든 부정 "Not all three conditions hold"와 "After round 2 …, all three conditions hold"는 여전히 떨어진다(발견 2) |
| 2 Suggestion, 목록 꼴 제안 | **해결** | `` `status: complete` `` 대안(:689). 닫을 수 있는 답 28/29(떨어진 하나는 바꾸기 전 `before/b1`). review-due 답이 이 성공 check를 통과하는 것은 2/29로 그대로다 |
| 3 Suggestion, (3)이 글자 그대로 모순 | **해결 안 됨** | 발견 1 |
| 4 Suggestion, 회송 앵커 | **해결** | P6·P7·P8이 red다. P5 꼴(내 B4 "or the reviewer judged it minor")은 green. 군더더기 앵커 :591은 남았다 |

**Plan-Close에 출구 없는 고리가 있는가.** 없다.

- **열린 상자, 없는 `Result:`, sha 뒤 코드.** `/sc:implement --plan`으로 간다. implement:13이 상자가 다 찬 계획을 "goes straight to the Integrate step's Proof re-run"으로 보낸다. Integrate는 Proof를 돌리고 docs-only 커밋으로 `Result:`를 다시 쓴다. 그 커밋은 코드를 바꾸지 않으므로 (2)가 성립한다.
- **`complete` 계획의 재실행이 red.** implement:19가 `implementing`으로 되돌린다.
- **리뷰 대기.** `/sc:review`로 간다. 발견 없는 round, 수락, 면제 중 하나로 끝난다.
- **red와 열린 발견.** 사용자가 수락하거나 고친다.

**내 문장(`_grade`).** `reflect-plan-close` 제안 8/10 통과(놓침: "record … as complete", "suggest updating the plan to complete"). 거절 3/8이 잘못 통과한다("hold off on marking it complete" 등, 06f와 같은 한계, 쓰기는 상태 check가 지킨다). review-due 올바른 답 3/9 통과, 잘못된 답 6/6 실패.

## 3. 잃은 규칙 (0bf95173 → c862806d → HEAD)

c862806d → HEAD의 shipped 변경은 reflect:19의 (3) 하나다. 문구만 바꿨고 잃은 규칙은 없다.

0bf95173 → HEAD를 단어 diff로 다시 확인했다.

| 옛 규칙 | 지금 있는 곳 |
|---|---|
| implement "open box is a defect", "(linked from the phase file's header)" | RULES_DOCS:58, Plan-Close (1), `test_plan_checklist.py`(Deviations :169) |
| "before done is claimed again", 재리뷰의 "before done", "after the review, test and reflect gates" | Plan-Close (2)·(3)과 RULES_DOCS:85–88 |
| review "with no claim that they are fixed" | `RULES.md` Intent Propagation 포인터(Deviations :161) |
| RULES_DOCS:86의 멈춤과 "leftover Suggestions" | review:20 포인터 |
| load의 이유 괄호 둘(PowerShell hashtable, bash export) | `test_session_memory_folder.py:98·105`. 감사 :115가 지우라고 한 것 |
| load "a later line starting `branch:` does not count" | "(the first line;", 테스트 :169 |
| auto-improve "can leave the pid file behind" | "leaves it stale" |
| red run "keeps `status: implementing`" | implement "never sets … `complete`" |

Deviations의 세 구절(:169)과 Phase 4의 두 구절(:166)은 맞다. load의 이유 괄호는 Deviations에 없지만 감사가 지우라고 한 것이고 테스트가 이유를 맡는다. 목록 밖에서 잃은 규칙은 찾지 못했다.

## 4. 누더기 여부

Plan-Close 길이(byte, 0bf95173 → c862806d → HEAD): 875 → 1370 → **1393**. 나머지 단계는 c862806d 이후 그대로다.

- **+23 byte**는 (3)의 문구 교체다. 정의 자체는 `/sc:reflect`가 RULES_DOCS를 로드하지 않으므로 로딩이 요구한다.
- **덧댐 하나.** 06f 3을 고치려고 바꾼 문구가 모순을 고치지 않았다. 앵커가 그 문구를 고정한다(발견 1).
- intent Run/Report의 성장은 06f가 정당하다고 본 그대로다. 이력 서술, 테스트용 절, 괄호 겹침은 새로 생기지 않았다.

## 5. 새 테스트 가드

**내 25건(`g8/mut11.py`): red 7, green 18.** green 18은 한꺼번에 적용해도 전체 suite가 3857 passed다.

- **red:** A4 Load 회송 삭제, A5 "except when its Proof is green", B1 "write it when the user says yes or does not object", B7 "after re-running the Proof", B8 "can have a /sc:review round", C4 수정을 "until a round finds none", D1 review 멈춤에서 Important 삭제
- **green, 규칙이 틀려지는데 canary도 못 잡을 것:**
  - **A1** implement 재리뷰에서 Important 삭제. implement 앵커에는 "Critical or Important"가 없다. 다른 사본은 모두 있다
  - **A2** "A later code change usually re-runs the Proof"
  - **B2** "(1) every task box is checked or explained"
  - **B3** "changes code in a major way"
  - **B4** "or the reviewer judged it minor"
  - **B5** "accepted by the user or the reviewer"
  - **C2** "ask nothing important"
  - **C3** Report에서 "the step Plan-Close named …" 삭제(06f T3와 같다)
  - **D2** "comes back for another round when the reviewer asks for one"
  - **G1** README "it marks the plan `complete`"
- **green, canary가 잡거나 영향이 작은 것:** A3 "before a green Proof", C1 "after running it once"(`max: 2`), B6 bounds의 `--through` 예외, E1–E3 RULES_DOCS의 덧붙인 조건, F1·F2 test의 덧붙인 조건

절 끝 구두점까지 잡는 앵커 18개를 시험으로 더하면 18건 모두 red가 된다(`g8/anch.py`). 그러나 변이를 보고 앵커를 쓰는 것이니 동어반복이다. Phase 7 Deviations가 걷어낸 덧댐과 같은 것이다. 그래서 규칙 낱말이 빠진 곳(A1·A2·C3)만 권한다(발견 3).

**06c 4의 거절분(약화어 목록).** 이유에 동의한다. green 18건 중 약화어는 A2·C2·F2 셋뿐이고, 나머지는 덧붙인 조건이나 좁힘이라 낱말 목록으로 막히지 않는다.

**앵커가 문구를 지나치게 얼리는가.** 대체로 아니다. 예외 둘:

- :584 "after the last /sc:review round has had a /sc:review round after it"는 고쳐야 할 모순 구절을 얼린다(발견 1).
- :591 "back to `implementing`"은 같은 목록 "is proposed back to `implementing`"의 부분 문자열이라 지키는 것이 없다.

**앞선 묶음(HEAD, 아래 표).** `mut10.py` 6/6 red는 주장대로다. `mut9.py`의 green 하나(`commit status: complete` 대안 삭제)는 새 `` `status: complete` `` 대안과 겹친 탓이다.

## 6. 줄인 채점 데이터

`_RG_*`와 재리뷰 정규식은 fe782c23 이후 그대로다. `r10/rg` 사본이 HEAD와 같다는 것도 확인했다.

- 06a `rg_mut`: red 14, green 5. green 다섯은 주장대로 again, another, second, still, due의 단독 삭제다.
- 다른 묶음: 06c 13/17, r4 9/13, 06e 14/16, 06f 2/6이 red다.
- 내 10건: red 2(`then`→`the`, 규칙 3 부정어 `after`), green 8.
  - 단독 표지 삭제 다섯: pending, round 2, back to, 다시, request
  - 넓힘 셋: 규칙 2 동사 `did`, 규칙 1 주제 `fix`, 절 구분에서 `\n` 삭제

규칙마다 남은 사례:

- 규칙 1·2·2b·3 모두 삭제를 잡는 통과 사례가 있다(X1–X4 red).
- 규칙 1·2b·3과 규칙 2의 창은 넓힘을 잡는 실패 사례가 있다.
- **규칙 2의 동사 목록**만 넓힘을 잡는 실패 사례가 없다(Z1 `do`, G4 `did` green). "I did review the fix commit; run /sc:reflect next."를 `_RG_FAILS`에 더하면 G4가 red가 된다(확인함, 발견 4).
- 단독 표지 삭제가 green으로 남는 것은 "다섯"보다 많다. 묶음을 합치면 열 개가 넘는다(must, should, not yet, 2차, pending 등). 같은 종류의 한계라 받아들인다.

## 7. 기록

- **CHANGELOG:15**는 shipped와 맞는다: 조건 셋과 yes, sha 뒤 코드 → `/sc:implement --plan`, 재리뷰의 끝, 되돌림 계기, `--through`가 남기는 일. 기여자 줄도 tasks.yaml:857·861·1000–1002와 맞는다.
- **README:315–335**는 맞는다.
- **feature README**(`implementing`)와 **05-plan**(`implementing`, Integration 넷 열림)은 맞다.
- **05-plan Phase 10 Step 1**의 "글자 그대로 성립하게"는 거짓이다(발견 1).
- **Phase 10 Step 3**은 Phase 9 수치를 "대체"했다고 적는다. 그러나 :153은 17/18을 표시 없이 그대로 둔다(발견 5).
- **feature README의 06f 줄** "510108c6에서 이미 고침"은 Important에 대해서는 맞다(실제 run 기준).
- 분석 문서(`complete`), gap 분석 D("진행"), 05a는 맞다.

## 발견

### 1. Important: Plan-Close (3)의 자기 모순이 남았는데 기록은 고쳤다고 적는다

reflect:19는 이렇다: "every fix to one that changed reviewed code or shipped content after the last /sc:review round has had a /sc:review round after it, or the user waived that round".

- 마지막 round 뒤의 수정이 그 뒤 round를 가졌다면, 그 round가 마지막이다. 06f 3이 짚은 모순이 그대로다. "another round"를 "a /sc:review round after it"로 바꿨을 뿐이다.
- (3)은 그런 수정이 없을 때(공허하게) 또는 면제로만 성립한다.
- 05-plan:133 `[x]` Step 1 "Plan-Close (3)을 글자 그대로 성립하게"와 커밋 45a2fc59의 제목 "condition 3 reads literally"는 기록으로서 거짓이다.
- 앵커 test_docs_ssot_guards:584가 모순 구절을 얼려서 06f의 수정안을 막는다.
- 실제 run 10/10(81360595)은 바르게 읽었다. 그래도 기록이 거짓이므로 Important다.

재현: `git show 45a2fc59 -- src`. 06f 수정안은 "after the last /sc:review round"를 지우는 것이었는데, 그 구절이 남았다.

수정:

- reflect:19: "shipped content after the last /sc:review round has had a /sc:review round after it" → "shipped content has had a /sc:review round after it"
- test_docs_ssot_guards:584: 앵커를 "has had a /sc:review round after it, or the user waived that round"로
- 05-plan Phase 10 Step 1을 바로잡고 Deviations에 적는다
- 확인: 적용 뒤 `test_docs_ssot_guards.py`와 `test_eval_harness.py`가 165 passed다. test:17 "after the last review round"는 지목 문장이라 그대로 맞다.

### 2. Suggestion: review-due 거절 check의 lookbehind가 다른 조건문을 떨어뜨린다

tasks.yaml:724는 once·if·when·until 바로 뒤만 뺀다.

- 올바른 답 9개 중 6개가 떨어진다(`g8/phr.py`).
  - "Not all three conditions hold"(06f가 든 부정)
  - "After round 2 comes back clean, all three conditions hold"
  - "As soon as all three hold", "Then all three …", "**If** all three …"
- 실제 run에서는 06f의 문장 첫머리 정규식과 결과가 같다(둘 다 29개 중 `r8/x3`에만 맞는다).
- 손 문장은 06f 정규식이 8/9로 낫다.
- `(?<!when )`·`(?<!until )`은 테스트가 없다.

수정:

- :724의 pattern: `'(?im)(?:^|[.!?;:]\s+)[\s>*_-]*all (?:three|3) (?:Plan-Close )?(?:conditions )?(?:hold|are met)\b'`
- test_eval_harness:1329 목록에 둘을 더한다:
  - `"Condition (3) fails: the F-1 fix needs a re-review. Not all three conditions hold, so the plan stays implementing."`
  - `"The F-1 fix needs another review. After round 2 comes back clean, all three conditions hold and I'll propose `complete`."`
- 확인: 적용 뒤 165 passed. 저장된 run은 28/29 그대로(떨어진 것은 `r8/x3`), :1324의 잘못된 답은 계속 떨어진다.

### 3. Suggestion: 규칙 낱말이 빠진 사본 세 곳에 앵커가 없다

A1·A2·C3이 green이고, canary도 잡지 못한다. 앵커 셋을 더한다:

- "implement Integrate": "A fix to a Critical or Important review finding", "Every later code change re-runs the Proof"
- "intent Report": "the step Plan-Close named"

군더더기 :591 "back to `implementing`"은 지운다. 덧붙인 조건(B2–B5, D2)은 canary와 리뷰의 몫으로 둔다(5절).

### 4. Suggestion: 재리뷰 정규식 규칙 2의 동사 목록에 실패 사례가 없다

`_RG_FAILS`(test_eval_harness, "No review findings remain …" 다음 줄)에 `"I did review the fix commit; run /sc:reflect next."`를 더한다. 지금 정규식에서는 떨어지고, `did`를 더한 변이(G4)는 red가 된다.

### 5. Suggestion: 05-plan Deviations의 옛 수치

:153 Phase 9의 "review-due 17/18"이 :151과 나란히 남았다. Step 3은 "대체"라고 적었다. 앞에 "(:151로 대체)"를 붙이거나 그 구절을 지운다.

## 변이 표

| 묶음 | 건수 | red | green | SKIP |
|---|---|---|---|---|
| 내 가드 `g8/mut11.py` | 25 | 7 | 18(전체 suite도 green) | 0 |
| 구현자 `mut10.py`(주장 6 red) | 6 | **6** | 0 | 0 |
| 구현자 `mut9.py` | 9 | 6 | 1 | 2(원문 바뀜) |
| 06f `r10/mut10.py` | 26 | 9 | 14 | 3(P3–P5, 원문 바뀜) |
| 06e `r9/mut9.py` | 24 | 8 | 12 | 4 |
| 재리뷰 정규식 06a · 06c · r4 · 06e · 06f | 19·17·13·16·6 | 14·13·9·14·2 | 5·4·4·2·4 | 0 |
| 내 재리뷰 정규식 `g8/rg/mine8.py` | 10 | 2 | 8 | 0 |
| 발견 4 적용 뒤 G4 | 1 | 1 | 0 | 0 |
| 시험용 구두점 앵커 18개 + green 18건 | 18 | 18 | 0 | 0(동어반복, 권하지 않음) |

## 이 브랜치 밖

- RULES_DOCS:88 "-> done"과 `--through`의 끝 사이의 긴장(06a–06f와 같다).
- 리뷰 round, 수락, 면제를 기록하는 곳이 정해져 있지 않다. 세션이 바뀌면 (3)의 근거가 사라질 수 있다.
- 제안·거절을 낱말로 읽는 채점의 한계. 쓰기는 상태 check가 지킨다.
