---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 4 (06c)

**판정: 조건부 통과.** 06b의 Important(조건 (2)의 사본 넷)는 해결됐고, `--through`와 충돌하는 문장은 없다. 그러나 사본을 대조하다 새 Important 하나를 찾았다. Plan-Close 조건 (3)은 "리뷰를 기다리는 수정"만 본다. 그래서 고치지도 수락하지도 않은 Critical·Important 발견이 열려 있어도 `complete`를 제안한다. 같은 규칙의 사본 셋(implement, RULES_DOCS, CHANGELOG)은 그런 발견이 계획을 `implementing`으로 되돌린다고 말한다(발견 1). 고칠 것은 문구다.

## 범위

- 대상: `f3128d30`. 비교 기준: `0bf95173`, `e87f9aa0`. `2a7e835c`와 `90e78f99`를 먼저 읽었다.
- 실행한 것:
  - 전체 게이트
  - 가드 변이: 내 28건(`$TMPDIR/pco/r4/mut4.py`), 그리고 HEAD에서 다시 돌린 `mut6.py`, `mutate_clean.py`, 06a `v2/mut.py`, 06b `r3/mut3.py`. 모두 `git checkout HEAD --`로 복구했고, 끝난 뒤 `git status`는 비어 있었다.
  - 재리뷰 정규식 변이: 06a 19건, 06b 17건, 내 13건(`r4/rg_mut*.py`, HEAD 데이터 사본)
  - `reflect-plan-close`를 `_fixture_ws`/`_grade`로 채점: 내가 쓴 제안 15개, 거절 14개(`r4/grade_pc4*.py`)
- 실행 안 함: canary, `claude -p`
- 모델: Claude Opus, effort high

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3856 passed, 3 skipped**, 206.38s |
| `make lint` | All checks passed |
| `uv run ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 규칙과 그 사본

| 규칙 | 사본 | 일치 |
|---|---|---|
| `complete`는 Plan-Close에서 사용자 yes로만 | implement:19, reflect:19·46, RULES_DOCS:58·88, intent:20·22, README:315·318·335, CHANGELOG:15, tasks.yaml:654–657 | 일치 |
| 조건 (2): `Result:` 뒤 코드 커밋 없음 | reflect:19, RULES_DOCS:58·85, README:315, CHANGELOG:15 | 일치 |
| 조건 (3)과 되돌림의 계기 | reflect:19 "a failing condition"(열린 발견은 실패가 아님) ↔ implement:19, RULES_DOCS:58, CHANGELOG:15 "a Critical or Important finding" | **불일치(발견 1)** |
| 수정의 재리뷰와 멈춤 | implement:19, review:20, RULES_DOCS:86·88, test:17, README:316·318, CHANGELOG:15 | CHANGELOG에 waive가 없음(발견 6) |
| `--through`: 한 번의 수정, 남은 일은 Report로 | intent:20·22, implement:19, review:20, RULES_DOCS:86, README:335, CHANGELOG:15, tasks.yaml:852·995 | 일치 |
| 상자가 다 찬 계획의 Proof 재실행 | implement:13·19, reflect:19, CHANGELOG:15, README:316 | 일치. 다만 `Result:` 없는 계획이 빠짐(발견 2) |

## 1. `/sc:intent --through` 충돌

Run(`intent.md:20`)의 체인을 끝까지 따라갔다. RULES_DOCS는 `/sc:intent`에서 로드된다(`context_loader.py:191`).

- spec review: Spec gate의 "user's go-ahead"(`review.md:22`)는 Run의 "the request is the approval"이 대신한다. `/sc:brainstorm`은 리뷰를 부르지 않고 문장만 낸다(`brainstorm.md:18`). 그래서 `/sc:review`는 두 번 불리고, `max: 2`는 문구와 맞는다. 저장된 run 6개도 두 번이다.
- 수정 round: implement:19, review:20, RULES_DOCS:86이 모두 "keeps its single fix round"로 끝난다. Run의 "re-run the Proof and rewrite `Result:`"는 implement의 "Every later code change …"와 같다.
- test와 reflect: test:17은 수정을 지목만 한다. Plan-Close가 지목하는 단계 넷 가운데 `--through`에서 나올 수 있는 것은 `/sc:review`뿐이다. red `Result:`는 Run의 멈춤 조건이 먼저 잡는다. Run은 지목된 단계를 Report로 넘긴다. Report(intent:22)는 README:335, CHANGELOG:15와 같은 일을 사용자에게 남긴다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 없다. RULES_DOCS:88 "-> done"과의 긴장은 06a·06b와 같다(브랜치 밖).

**프로브.** `through_left_open`은 `05-plan.md`(index)와 `README.md`만 읽는다. 그래서 split 계획의 phase 파일 `complete`는 통과한다. implement가 정당하게 쓰는 값이다. 그런데 `_THROUGH_STATES`에는 이 통과 상태가 없다. 06b V26(필터를 `05-plan[^/]*`로 넓힘)은 여전히 green이다(발견 4).

## 2. 06b 발견의 해결

| 06b | 판정 | 근거 |
|---|---|---|
| 1 사본 넷 | **해결** | RULES_DOCS:58 "and no commit after that line's sha changes code", :85와 README:315 "no code commit follows …", CHANGELOG:15. 옛 문구 가드는 `test_docs_ssot_guards.py:689–698`. shipped와 README에 남은 옛 문구는 없다(grep) |
| 2 앵커 | 대부분 해결 | 앵커 아홉. V11은 `max: 2`가 잡는다. 약화어 검사는 여전히 `<workflow_gates>` 전체에 걸린다 |
| 3 성공 regex, 거절 | 제안대로 해결, 잔여 | 제안 15개 중 12개 통과("can become complete", "ready to be completed", "record … as complete"를 놓친다). 거절 14개 중 6개만 떨어진다. "It cannot be marked complete yet"은 부정어가 있는데도 통과한다(발견 3) |
| 4 실패 넷에 단계 | 해결 | reflect:19. 남은 틈: `Result:` 없음, 열린 발견(발견 1, 2) |
| 5 Load "otherwise" | 해결 | implement:13 "Without --plan, … With --plan, …" |
| 6 기록과 데이터 | 해결 | 규칙 주석을 바로잡았고 Y9·Y10은 red다. 빈 줄 0. Deviations와 README도 반영 |

**Plan-Close에 출구 없는 고리가 있는가.** 실패 넷에는 모두 출구가 있다. 상자가 다 차고 `Result:` 뒤에 코드 커밋이 있으면 implement:13이 Integrate의 재실행으로 보낸다. :19는 깨끗한 HEAD에서 Proof를 돌리고, docs 커밋으로 `Result:`를 다시 쓴다. 그러면 reflect (2)가 성립한다. 출구가 없는 것은 `Result:` 줄이 없는 계획이다(발견 2).

## 3. 잃은 규칙 (0bf95173 → e87f9aa0 → HEAD)

e87f9aa0 → HEAD의 shipped 변경은 implement Load의 순서, reflect의 회송 셋, RULES_DOCS 두 줄이다. 이 구간에서 잃은 규칙은 없다.

| 옛 규칙 | 지금 |
|---|---|
| "`complete` with an open box is a defect" | RULES_DOCS:58, phase 파일 "only when all its boxes are checked", `test_plan_checklist.py` |
| "(linked from …)", "after the review, test and reflect gates", "before done" 두 개 | 빠짐. Deviations에 있다. "before done is claimed again"을 대신하는 것은 Plan-Close (2)다. Deviations는 이를 적지 않았다 |
| red run "keeps `status: implementing`", reflect "the plan stays `implementing`" | "never sets … `complete`", yes에만 쓰기, bounds |
| reflect 진입 "whose plan … is `implementing`" | 넓어졌다: `implementing`이면 제안, `complete`이면 되돌림 제안 |
| review "with no claim that they are fixed" | `RULES.md:10`(항상 로드), Deviations Phase 4 |
| gates :86의 멈춤 규칙 전문 | review Process 포인터. `--through`에서는 둘 다 로드된다 |
| load의 later `branch:` line, older machine, PowerShell·bash 이유 | "(the first line; …)", "every kept record that has the newest date". 이유는 빠졌다(06b와 같다) |

Deviations의 빠진 구절 셋은 맞다. 목록 밖에서 빠진 규칙은 없다.

## 4. 누더기 여부

길이(자, 0bf95173 → e87f9aa0 → HEAD):

- implement Load 257 → 395 → 397, Integrate 2023 → 1631 → 1631
- Plan-Close 871 → 982 → **1078**
- review Process 691 → 651 → 651
- intent Run 961 → 1039 → 1039, Report 518 → 633 → 633
- RULES_DOCS:58 552 → 636 → 644

판단:

- **Plan-Close +96**: 늘어난 것은 회송 셋이다. `/sc:reflect`에는 implement.md가 로드되지 않으므로 "which finishes the box or re-runs the Proof" 같은 이유가 필요하다. 받아들인다.
- shipped 문구에 이력 서술이나 테스트를 맞추려는 덧댐은 없다.
- 테스트 쪽: 옛 문구 가드(:689–698)는 `src/**/*.md` 전체에서 "last code commit"을 금지한다. 지금은 해가 없다. tasks.yaml:682–686 주석에는 "the / two" 줄바꿈이 남았다.

## 5. 새 테스트 가드

**내 28건**: red 6, green 22.

- red: W14(gates 앵커 삭제), W17(review "no Critical" 부정), W19(`through_left_open`의 `phase` 삭제), W20(`max: 3`), W24("may"), W28(제안 갈래 삭제)
- green:
  - 목록 밖 약화어: W2 "normally", W4 "generally", W5 "usually", W6 "as needed", W13 "if asked", W21 "when unsure", W22 "should", W23 "can"
  - 앵커를 남긴 부정: W7 "does not set it back to `implementing`"
  - 앵커 없는 절의 삭제: W8·W9(Plan-Close 회송 둘), W10(RULES_DOCS:58의 finding 계기), W11(README "any review round its fix still needs"), W12(Report "the step Plan-Close named"), W15(Run "or when a Critical finding or a red Proof remains …"), W18(첫 상자 → `implementing`)
  - 덧붙인 조건: W1, W3, W16, W26
  - 다른 자리의 모순: W25(`<does>`)
  - 거절 guard의 `propos\w*` 삭제: W27

W1, W3, W16, W23, W27 외는 기능을 되돌린다.

**앞선 묶음(HEAD)**:

- `mut6.py`: red 10/10. Phase 6의 주장과 맞다.
- `mutate_clean.py`: red 22, SKIP 1
- 06a: red 15, green 10, SKIP 4. S7은 원문이 바뀌어 SKIP이 됐다.
- 06b: red 14, green 13, SKIP 2. 06b가 기능 되돌림으로 꼽은 열 개 중 아홉이 이제 red다. V11은 canary의 `max: 2`가 잡는다.

가드는 앵커 구절을 지우는 변이와 목록 안 약화어를 넣는 변이를 잡는다. 앵커 대부분은 3–9낱말이라 적당하다. 14낱말 앵커 둘은 줄여도 된다. intent Run "Stop and report instead …"와 implement Load "has a code commit after it goes straight …"이다.

## 6. 줄인 채점 데이터

주석(`tasks.yaml:540–545`)의 규칙은 셋이다. (1) 표지가 붙은 리뷰, (2) 요청 동사, "next", "then" 뒤의 리뷰, (3) 수정에 대한 부정된 리뷰.

**변이 결과**:

- 06a 19건: red 14, green 5. green은 single marker 다섯이라 주장과 맞다.
- 06b 17건: red 15, green 2(Y12 `;` 경계, Y13 `need(s|ed)` 삭제)
- 내 13건(Z6는 빈 갈래를 만든 무효 변이): red 5(Z4, Z7, Z9, Z11, Z13), green 7. green은 Z1 규칙 2 동사 `do` 추가, **Z2 규칙 2 창 25→80**, **Z3 규칙 3 창 10→40**, Z5 `round`, Z8 `back to`, Z10 `send` 삭제, **Z12 규칙 1 표지 `merge` 추가**다.

| 규칙 | 삭제를 잡는 통과 문장 | 넓힘을 잡는 실패 문장 |
|---|---|---|
| 1 표지 | 있음(X1, Y6–Y8, Y11) | 있음(X12, Y15–Y17, Z13). `merge`는 없음 |
| 2 요청 동사, next | 있음(X2, Y1–Y4) | **없음**(Z1, Z2) |
| 2b then | 있음(X3, Y14) | 있음(X5, X6) |
| 3 부정된 리뷰 | 있음(X4, Y5, Y9, Y10) | 있음(X7, X9, Z4, Z9). 창은 없음(Z3) |

가장 흔한 표지 `needs`만으로 통과하는 문장도 없다(Y13).

## 7. 기록

- **CHANGELOG :15**는 조건 (2), 회송, yes에만 쓰기, `--through`가 남기는 일, `/sc:implement --plan`에서 shipped와 맞는다. 어긋나는 것은 둘이다. 되돌림의 계기는 reflect와 다르다(발견 1). 멈춤 규칙에 waive가 없다. 기여자 줄은 새 `/sc:review` 횟수 check를 말하지 않는다(발견 6).
- README :315, :316, :318, :335는 맞다.
- feature README `implementing`, 05-plan `implementing`(Integration이 열려 있다), 감사 문서 `complete`, gap 분석 D "진행"은 맞다. Documents에는 06c가 없다(이 커밋은 이 파일만 더한다).
- **05a :32** "규칙마다 두세 개로 줄였다"와 `test_eval_harness.py:1355` "two or three per rule"은 맞지 않는다. 지금 규칙 1은 7개, 규칙 3은 4개다.

## 발견

### 1. Important: Plan-Close (3)이 열린 Critical·Important 발견을 보지 않는다. 되돌림의 계기가 사본마다 다르다

reflect:19 (3)은 "no fix to a Critical or Important review finding waits for another /sc:review round"다. 고치지 않은 발견은 기다리는 수정이 아니므로 (3)이 성립한다.

재현(문구대로, `test-reflect-gate` fixture):

1. `s_init`, `s_add`, `s_feat`를 돌린다. `06-review.md` Round 1은 F-1(Important)과 "changes requested"를 남긴다.
2. feat 커밋에서 녹색 Proof를 돌리고, docs 커밋으로 `Result: <feat sha>`를 쓴다. F-1은 고치지 않는다.
3. `/sc:reflect`를 돌린다. (1), (2), (3)이 모두 성립하므로 `complete`를 제안한다. bounds "with a Plan-Close condition unmet"도 막지 않는다.
4. 그런데 implement:19, RULES_DOCS:58, CHANGELOG:15는 "a Critical or Important finding in its work"가 `complete` 계획을 되돌린다고 말한다. reflect의 되돌림 제안은 같은 상태에서 일어나지 않는다.

기능의 목적(리뷰를 통과한 뒤의 `complete`, 04-design:17)과도 어긋난다. `--through`는 수정을 한 번 하므로 (3)이 잡는다. 문제는 대화형 체인이다.

수정:

- reflect:19: "(3) no fix to a Critical or Important review finding waits for another /sc:review round." → "(3) every Critical or Important review finding is fixed or accepted by the user, and no fix to one waits for another /sc:review round."
- 같은 줄: "; a red `Result:` to the user, who accepts it or has it fixed" → "; an open finding or a red `Result:` to the user, who accepts it or has it fixed"
- CHANGELOG:15: "and no review fix is waiting" → "and every Critical or Important review finding is fixed (its fix reviewed again) or accepted by you"
- 앵커 "(3) no fix to a Critical or Important review finding" → "(3) every Critical or Important review finding is fixed or accepted"
- 선택: 위 상태로 reflect 프로브 하나.

### 2. Suggestion: `Result:` 줄이 없는, 상자가 다 찬 계획에 출구가 없다

상자가 다 찼는데 `Result:` 줄이 없을 수 있다(옛 계획, 손으로 체크한 상자). 그러면 (2)가 실패하지만 Plan-Close는 단계를 주지 않는다. implement:13의 진입 조건도 거짓이다. Phase 6이 "실패 모두에 단계"를 주장하므로 이 틈은 이 브랜치의 범위다.

- implement:13: "whose `Result:` sha has a code commit after it" → "whose `Result:` line is missing or has a code commit after its sha"
- reflect:19: "an open box or a code commit after the `Result:` sha to /sc:implement --plan" → "an open box, a missing `Result:` line or a code commit after its sha to /sc:implement --plan"
- 앵커 둘도 고친다.

### 3. Suggestion: 거절 guard가 "marked"와 "isn't"를 놓친다

tasks.yaml:693의 `(?:mark|set|clos\w*|propos\w*)\b`는 "marked"와 "setting"에 맞지 않는다. 부정어 목록에는 "isn't"가 없다. 그런데 주석(:682–686)은 "no negation"인 거절만 통과한다고 말한다.

수정:

- 패턴을 `(?:mark\w*|set\w*|clos\w*|propos\w*)`로 바꾸고 부정어에 `isn't`를 더한다. 그러면 거절 하나("It cannot be marked complete yet, because the fix is unreviewed.")가 더 떨어진다. 제안 15개의 결과는 그대로다(`grade_pc4b.py`).
- 그 문장을 채점 테스트에 넣는다.
- 주석의 줄바꿈을 고친다.

### 4. Suggestion: 가드가 약화와 삭제 일부를 놓친다

- `_SOFTENER`에 더할 것: `usually|normally|generally|typically|as needed|if asked|when asked|when unsure|should|when practical|recommended|by default|where appropriate`. 지금 앵커 텍스트에는 이 낱말들이 없다(`r4/softcheck.py`). `can`, `optional`, `except`는 이미 있으므로 넣지 않는다.
- 부정(W7)을 잡도록 앵커를 동사까지 늘린다: implement "sets it back to `implementing`", rules "sets a `complete` plan back to `implementing`"
- 앵커를 더한다:
  - reflect Plan-Close: "a fix waiting for review to /sc:review", "a red `Result:` to the user"
  - rules: "a Critical or Important finding in its work"
  - README --through: "any review round its fix still needs"
  - intent Report: "the step Plan-Close named"
  - intent Run: "or a red Proof remains after one fix round"
  - implement Integrate: "The first checked box sets the plan (index) to `status: implementing`"
- `_THROUGH_STATES`에 "phase file marked complete"를 더한다(`05-plan-phase1.md`에 `status: complete`, 기대값 `[_P] * 11`). 그러면 V26이 red가 된다.

덧붙인 조건(W1, W3, W26)과 다른 자리의 모순(W25)은 주석대로 canary에 맡긴다.

### 5. Suggestion: 재리뷰 정규식 규칙 2의 넓힘을 막는 실패 문장이 없다

다음 문장 넷을 더하면 Y13, Z2, Z12, Z3이 red가 된다. 넷 다 HEAD에서 기대대로 채점된다(`r4/rg_extra4.py`, `rg_extra5.py`).

- `_RG_REREVIEW` 규칙 1: "The F-1 fix needs review."
- `_RG_FAILS`: "Run /sc:reflect now: the F-1 fix review came back clean."
- `_RG_FAILS`: "The review is done and it is ready to merge; run /sc:reflect."
- `_RG_FAILS`: "No findings were left open after the review of the fix; run /sc:reflect."

### 6. Suggestion: 기록 잔여

- CHANGELOG:15: "until a round finds none or you accept them" → "until a round finds none or you accept them or waive the re-review"
- CHANGELOG 기여자 줄 "fail when the branch marks the plan complete" → "fail when the branch marks the plan complete or `/sc:review` runs more than twice"
- `test_eval_harness.py:1355` "two or three per rule" → "a few per rule"
- 05a:32 끝에 "(06a·06b 뒤 규칙 1은 7개, 규칙 3은 4개)"를 더한다.
- feature README Documents에 06c를 더한다.

## 변이표

| 묶음 | 건수 | red | green | SKIP |
|---|---|---|---|---|
| 내 가드 `r4/mut4.py` | 28 | 6 | 22 | 0 |
| `mut6.py`(Phase 6) | 10 | 10 | 0 | 0 |
| `mutate_clean.py` | 23 | 22 | 0 | 1 |
| 06a `v2/mut.py` | 29 | 15 | 10 | 4 |
| 06b `r3/mut3.py` | 29 | 14 | 13 | 2 |
| 06a 재리뷰 정규식 | 19 | 14 | 5 | 0 |
| 06b 재리뷰 정규식 | 17 | 15 | 2 | 0 |
| 내 재리뷰 정규식 `r4/rg_mut4.py` | 12 (+무효 1) | 5 | 7 | 0 |

## 이 브랜치 밖

- RULES_DOCS:88 "-> done"과 `--through`의 끝 사이의 긴장(06a·06b와 같다)
- `complete` 계획에서 `/sc:review`가 Critical을 찾으면 누가 되돌리는지 review.md는 말하지 않는다(발견 1을 고치면 다음 reflect가 제안한다).
