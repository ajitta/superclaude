---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 5 (06d)

**판정: 조건부 통과.** 06c의 Important는 해결됐고 `--through`와 충돌하는 문장은 없다. 다만 새 Important가 하나 있다. `complete` 계획을 되돌리는 계기가 사본마다 다르다. reflect:19는 "a failing condition"이라서 `Result:` 뒤의 코드 커밋도 계기가 된다. 다른 기능의 커밋이어도 그렇다. implement:19, RULES_DOCS:58, CHANGELOG:15는 red 재실행과 Critical·Important 발견만 든다(발견 1). 고칠 것은 문장 하나다.

## 범위

- 대상: `fe782c23`(= `feature/plan-complete-order` head). 비교 기준: `0bf95173`, `f3128d30`. `06c-verify-round4.md`와 `git show 16cbab92`를 먼저 읽었다.
- 실행한 것:
  - 전체 게이트
  - 가드 변이: 내 29건(`$TMPDIR/pco/r8/mut8.py`)은 HEAD를 `git archive`로 푼 사본에서 돌렸다. 이 worktree에서는 `mut6`, `mut7`, `r4/mut4`, `mutate_clean`, `v2/mut`, `r3/mut3`을 다시 돌렸고, 끝난 뒤 `git status`는 비어 있었다.
  - 재리뷰 정규식 변이: 06a 19건, 06b 17건, 06c 13건, 내 13건(`r8/rg_*.py`, HEAD 데이터 사본)
  - `reflect-plan-close` 채점: `_fixture_ws`/`_grade`로, 내가 쓴 제안 12개와 거절 14개(`r8/grade_pc5.py`). 후보 정규식 비교(`r8/pc_cand.py`)
- 실행 안 함: canary, `claude -p`(다른 곳에서 실행 중)
- 모델: Claude Opus, effort high

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3857 passed, 3 skipped**, 160.32s |
| `make lint` | All checks passed |
| `uv run ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 규칙과 그 사본

| 규칙 | 사본 | 일치 |
|---|---|---|
| `complete`는 Plan-Close에서 사용자 yes로만 | implement:19, reflect:19·46, RULES_DOCS:58·88, intent:20·22, README:315·318·335, CHANGELOG:15, tasks.yaml:854–857 | 일치 |
| 조건 (2): `Result:` 뒤 코드 커밋 없음 | reflect:19, RULES_DOCS:58·85, README:315, CHANGELOG:15 | 일치 |
| 조건 (3): 발견이 고쳐졌거나 수락됨, 재리뷰 대기 없음 | reflect:19, CHANGELOG:15 | CHANGELOG "(its fix reviewed again)"에 waive가 없다(발견 4) |
| `complete` 계획을 되돌리는 계기 | reflect:19 "a failing condition" ↔ implement:19, RULES_DOCS:58, CHANGELOG:15 "red re-run, Critical or Important finding" | **불일치(발견 1)** |
| `Result:` 없음 → `/sc:implement --plan` | implement:13, reflect:19 | 일치 |
| 재리뷰와 멈춤 | implement:19, review:20, RULES_DOCS:86·88, test:17, README:316·318, CHANGELOG:15 | 일치 |
| `--through`: 한 번의 수정, 남은 일은 Report로 | intent:20·22, implement:19, review:20, RULES_DOCS:86, README:335, CHANGELOG:15, tasks.yaml:852·995 | 일치 |

## 1. `/sc:intent --through` 충돌

Run(intent:20)의 체인을 끝까지 따라갔다.

- spec review의 go-ahead는 "the request is the approval"이 대신한다. `/sc:review`는 두 번이고 `max: 2`와 맞다.
- implement:19는 `complete`를 쓰지 않고, 재리뷰 문장은 "keeps its single fix round"로 끝난다. review:20, RULES_DOCS:86도 같다.
- Run의 "re-run the Proof and rewrite `Result:`"는 implement:19 "Every later code change …"와 같다. test:17은 지목만 한다.
- 새 (3)은 리뷰되지 않은 수정과 열린 Important에서 실패한다. Run은 "leave the step Plan-Close names to the Report step"으로 받는다. Report:22가 그 단계를 사용자에게 남긴다. red는 Run의 멈춤 조건이 먼저 잡는다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 없다. RULES_DOCS:88 "-> done"과의 긴장은 06a–06c와 같다(브랜치 밖).

**프로브.** `through_left_open`(tasks.yaml:856)은 index(`05-plan.md`)와 README만 본다. `_THROUGH_STATES`에 "phase file marked complete"(`[_P] * 11`)가 생겼다. 06c 4의 마지막 항목이고, 내 M25(필터에서 `05-plan` 삭제)는 red다.

## 2. 06c 발견의 해결

| 06c | 판정 | 근거 |
|---|---|---|
| 1 Important, (3)과 열린 발견 | **해결** | reflect:19 "(3) every … finding is fixed or accepted by the user", 회송 "an open finding … to the user", CHANGELOG:15. `mut7` red |
| 2 `Result:` 없는 계획 | **해결** | implement:13 "is missing or has …", reflect:19. Proof footer가 없는 옛 계획도 "unrunnable … accepted"로 나간다 |
| 3 거절 guard | **대부분 해결** | tasks.yaml:693의 `mark\w*`, `set\w*`, `isn't`, 채점 문장 둘. "the / two" 줄바꿈과 좁은 주석은 남았다(발견 3) |
| 4 가드 | **일부, 나머지는 이유를 들어 거절** | 바뀐 절과 되돌림 동사(implement·rules)에 앵커, phase 파일 상태. 약화어 13개와 앵커 6개는 Deviations Phase 7에서 거절(5절) |
| 5 재리뷰 문장 | **해결** | Y13, Z2, Z3, Z12가 이제 red(6절) |
| 6 기록 | **해결** | CHANGELOG waive와 `max`, 테스트 주석 "a few per rule", 05a:32, README Documents |

**Plan-Close에 출구 없는 고리가 있는가.** 없다.

- 열린 상자, 없는 `Result:`, `Result:` 뒤 코드 커밋 → implement:13을 거쳐 Integrate로 간다. Integrate가 Proof를 돌리고 docs 커밋으로 `Result:`를 쓴다. 그러면 (2)가 성립한다.
- 리뷰 대기 → review:20의 round. round는 발견이 없거나 사용자가 수락·waive하면 멈춘다.
- 열린 발견, red → 사용자가 수락하거나 고친다.

다만 `complete` 계획에서는 출구가 아니라 불필요한 되돌림이 생긴다(발견 1).

**`reflect-plan-close` 성공 정규식.** 06c와 겹치지 않는 내 문장으로 채점했다(`grade_pc5.py`). 제안은 12개 중 **8개**가 통과한다. 놓친 것은 "commit `status: complete`", "moving the plan to complete", "change status … to complete", "update the frontmatter"다. 거절은 14개 중 **9개**가 떨어진다. 통과한 다섯 가운데 "shouldn't be marked complete"와 "no basis to mark"는 부정어가 있다(발견 3).

## 3. 잃은 규칙 (0bf95173 → f3128d30 → HEAD)

f3128d30 → HEAD의 shipped 변경은 implement:13과 reflect:19뿐이다. 둘 다 조건을 더했고 지운 것은 없다.

| 옛 규칙(0bf95173) | HEAD |
|---|---|
| "`complete` with an open box is a defect" | RULES_DOCS:58, phase 파일 "only when all its boxes are checked" |
| "(linked from …)", "after the review, test and reflect gates", "before done" | 빠짐, Deviations Phase 4 |
| "before done is claimed again" | "Every later code change …" + Plan-Close (2) |
| red run "keeps `status: implementing`" | "never sets … `complete`" |
| reflect 진입 "is `implementing`" | `complete` 계획도 본다(발견 1의 근원, ab7f0a96) |
| review "with no claim that they are fixed" | `RULES.md:10`(항상 로드) |
| load의 PowerShell·bash 이유 괄호 둘 | 규칙은 남고 이유만 빠짐(감사 :115) |
| load "without reading the records whole" | "one Grep `^branch:`" |
| auto-improve "(… leave the pid file behind)" | 같은 항목의 "leaves it stale" |

Deviations의 세 구절은 맞다. 목록 밖에서 잃은 규칙은 없다.

## 4. 누더기 여부

길이(자, 0bf95173 → f3128d30 → HEAD):

- implement Load 254 → 394 → 414, Integrate 2020 → 1628 → 1628
- Plan-Close 866 → 1073 → **1154**
- review Process 688 → 648 → 648
- intent Run 958 → 1036 → 1036, Report 515 → 630 → 630
- RULES_DOCS:58 549 → 641 → 641, `<workflow_gates>` 2432 → 2209 → 2209

판단:

- **Plan-Close +81**은 (3)의 "fixed or accepted"와 회송 둘이고, 모두 06c 1·2의 기능이다. 덧댐이 아니다. 이력 서술, 괄호 겹침, 테스트에 맞춘 절은 없다.
- 근거를 좁히는 문장 하나: "from the plan file and `git log`". 새 (3)은 리뷰 발견 목록이 있어야 판단할 수 있다(발견 2).
- 테스트 쪽: 가드 주석(test_docs_ssot_guards.py:518)은 "rewording passes"라고 한다. 그런데 앵커가 길다. implement Load 17낱말, rules 되돌림 15낱말, intent Run 14낱말이다(발견 5).

## 5. 새 테스트 가드

**내 29건(`mut8.py`): red 5, green 24.**

- red: M1 "only when the user says yes" 삭제, M3 (3)의 Important 삭제, M21 review의 `--through` 문장 삭제, M24 "unless stuck", M25 `through_left_open` 필터
- green, 앵커를 남긴 부정·모순: **M4** reflect "stays `complete` and is never proposed back to `implementing`", **M6** implement "on a green one it does"(`complete`를 씀), M19 `<does>`에 "setting a plan `complete`", M29 "/sc:reflect itself, which accepts it"
- green, 앵커 없는 절의 삭제·변경: **M5** "a fix waiting for review to /sc:test", **M12** Report의 "the step Plan-Close named …" 삭제, **M18** README "any review round its fix still needs" 삭제, **M22** "without re-running the Proof" → "re-running …", **M28** Run의 "or when a Critical finding or a red Proof remains after one fix round" 삭제, M20 CHANGELOG "only on your yes" 삭제(가드 밖)
- green, 덧붙인 조건(목록 밖 약화어): M2 "or at once in a headless run", M7 "if the fix is large", M8·M9·M23 "when the user asks", M13 "if time allows", M14 "or nearly all are", M16 "except when every test passes", M17 "applies itself in a headless run", M26 "most of its boxes", M27 "or explained"
- green, canary가 잡는 것: M10 세 번째 리뷰(`max: 2`), M11 `--through`가 `complete`를 씀. M15 "after round two"는 잡는 곳이 없다.

**거절 이유(Deviations Phase 7)에 대한 판단.** 약화어 목록을 round마다 늘리는 것은 덧댐이라는 데 동의한다. 덧붙인 조건은 낱말 목록으로 막을 수 없다는 데도 동의한다. 다만 그 문장의 "가드는 규칙의 삭제, 흔한 약화어, 되돌림 동사의 부정을 잡는다"는 사실보다 넓다.

- 삭제는 앵커가 있는 구절만 잡는다. M5, M12, M18, M22, M28은 green이다. M28은 `--through`의 멈춤 조건을 지운다.
- 부정은 implement와 rules만 잡는다. reflect의 앵커는 여전히 "back to `implementing`"이라 M4가 green이다.

기록을 바로잡는 것으로 충분하다(발견 5). 가드 공백 자체는 지시대로 Suggestion이다.

**앞선 묶음(HEAD):**

- `mut6.py`: red 8, SKIP 2(원문이 바뀜)
- `mut7.py`: **red 8/8**. 주장과 맞다.
- 06c `r4/mut4.py`: 06c 때 red 6에서 W7(implement 되돌림 동사 부정)과 W10(RULES_DOCS:58 발견 계기 삭제)이 더해져 red 8
- 06b `r3/mut3.py`: V26(필터 넓힘)이 이제 red다
- 건수는 변이표

## 6. 줄인 채점 데이터

재리뷰 정규식 변이의 green:

- 06a: X11, X14–X17. 표지 again, another, second, still, due를 하나씩 삭제. 주장대로 다섯
- 06b: Y12(`;` 경계)
- 06c: Z1 동사 `do` 추가, Z5 `round`, Z8 `back to`, Z10 `send` 삭제
- 내 것: V3 표지 `nothing` 추가, 대안 하나 삭제 여덟(`must`, `should`, `pending`, `require`, `without`, `request`, `schedule`, `다시`). red는 V1 `after`, V2 `clean`, V4 `in` 추가와 V10 규칙 3의 `no` 삭제

| 규칙(tasks.yaml:540–545) | 삭제를 잡는 통과 문장 | 넓힘을 잡는 실패 문장 |
|---|---|---|
| 1 표지 | 있음(X1, Y6–Y8, Y11, Y13) | 있음(X12, Y15–Y17, Z12, Z13, V2, V4) |
| 2 요청 동사, next | 있음(X2, Y1–Y4) | 있음(Z2 창, V1). 낱말 하나 추가(Z1 `do`)는 green |
| 2b then | 있음(X3, Y14) | 있음(X5, X6) |
| 3 부정된 리뷰 | 있음(X4, Y5, Y9, Y10, V10) | 있음(X7, X9, Z3, Z4, Z9) |

규칙마다 통과 문장과 실패 문장이 모두 있으므로 06c 5는 닫혔다. 대안 낱말 하나를 지우는 변이는 green이다. 그런 대안은 다섯이 아니라 열여섯쯤이다. 설계가 규칙 단위이므로 받아들인다. 05a의 알려진 놓침 셋은 HEAD에서도 놓친다.

## 7. 기록

- **CHANGELOG:15**는 조건 (1)·(2), yes에만 쓰기, `/sc:implement --plan`, `--through`가 남기는 일에서 shipped와 맞다. 어긋나는 것은 둘이다. 조건 (3)의 "(its fix reviewed again)"에 waive가 없다(발견 4). 되돌림 계기는 reflect:19와 다르다(발견 1).
- **README :315, :316, :318, :335**는 맞다. :335는 열린 Important의 수락을 말하지 않지만, Report:22의 일반형이 덮는다.
- **feature README** `implementing`, Documents에 06c. **05-plan** `implementing`, Phase 7 상자 다섯이 체크, 열린 상자는 Phase 3 Step 2(canary)와 Integration 넷. **분석 문서** `complete`, gap 분석 D "진행". **05a:32**. 모두 맞다.
- **Deviations Phase 7**의 가드 능력 주장은 사실보다 넓다(발견 5).

## 발견

### 1. Important: `complete` 계획을 되돌리는 계기가 reflect와 나머지 사본에서 다르다

reflect:19는 "A `complete` plan with a failing condition is proposed back to `implementing`"이다. 조건 (2) "no commit after its sha changes code"는 저장소 전체의 커밋을 본다. 그래서 다른 기능의 코드 커밋도, 병합 뒤 master의 커밋도 `complete` 계획을 되돌림 제안으로 보낸다. implement:19, RULES_DOCS:58, CHANGELOG:15는 계기를 "a red re-run, or a Critical or Important finding in its work"로 든다. implement:19는 녹색 재실행이면 `complete`를 그대로 둔다.

재현(문구대로):

1. 기능 X의 계획이 `complete`이고 `Result: abc1234`다. 브랜치는 master에 병합됐다.
2. 기능 Y가 master에 코드 커밋을 남긴다.
3. `/sc:reflect --type completion for X`를 돌린다. Plan-Close는 `git log abc1234..HEAD`에서 Y의 코드 커밋을 보고 (2)를 실패로 판정한다. 그 결과 X를 `implementing`으로 되돌리자고 제안한다.
4. 나머지 사본으로는 되돌림 계기가 아니다. 사용자는 손대지 않은 기능을 다시 열라는 제안을 받는다.

06c 1과 같은 종류다. 06c는 (3)만 맞췄다(문장은 ab7f0a96).

수정(reflect:19 마지막 문장):

- "A `complete` plan with a failing condition is proposed back to `implementing`, the README `phase:` unchanged" → "A `complete` plan whose `Result:` is red or whose condition (3) fails is proposed back to `implementing`, the README `phase:` unchanged; a code commit after its sha only needs the Proof re-run"
- 앵커 "back to `implementing`"은 그대로 맞는다. 되돌림 동사까지 잡으려면 "is proposed back to `implementing`"으로 바꾼다(M4).

### 2. Suggestion: Plan-Close가 (3)의 근거를 읽으라고 하지 않는다

reflect:19 "check its plan (index) from the plan file and `git log`"는 근거를 둘로 좁힌다. 그런데 새 (3) "every … finding is fixed or accepted"는 리뷰 발견 목록이 있어야 판단할 수 있다. `/sc:review`는 파일을 쓰지 않는다. 프로브 fixture에는 `06-review.md`가 있어서 드러나지 않는다.

수정: "from the plan file and `git log`" → "from the plan file, the review findings and `git log`"

### 3. Suggestion: `reflect-plan-close` 정규식과 주석

- 놓치는 제안: "commit `status: complete`", "change status … to complete", "moving the plan to complete"
- 놓치는 거절: "shouldn't", "no basis to mark"
- 주석 tasks.yaml:680–685은 "use no negation"이라고 하고, "the / two" 줄바꿈이 남았다.

후보(`pc_cand.py`)로 비교했다. 테스트 사례 12/12는 그대로다. 내 목록에서 제안은 8 → 11/12, 거절은 9 → 11/14로 좋아진다. 06c 목록에서 제안은 12 → 13/15, 거절은 8/14 그대로다.

- 성공 패턴의 `(?:mark|set|clos(?:e|ing)|flip|update)` → `(?:mark|set|clos(?:e|ing)|flip|update|commit|chang|mov)`
- 거절 패턴의 `(?:not|never|won't|cannot|can't|don't|isn't|do\s+not)` → `(?:not|no|never|cannot|\w+n't|do\s+not)`, 동사 묶음에 `|commit\w*|chang\w*|mov\w*`
- 주석: "Refusals that use no negation still pass; the / two status checks above are the guard." → "Refusals worded without a listed negation ("rather than", "wait on") still pass; the two status checks above are the guard."
- 위 문장 넷을 채점 테스트에 넣는다.

### 4. Suggestion: CHANGELOG의 조건 (3)에 waive가 없다

CHANGELOG:15 "and every Critical or Important review finding is fixed (its fix reviewed again) or accepted by you" → "and every Critical or Important review finding is fixed or accepted by you, with no fix waiting for another review round"

### 5. Suggestion: 가드의 기록과 앵커 길이

- Deviations Phase 7 "가드는 규칙의 삭제, 흔한 약화어, 되돌림 동사의 부정을 잡는다" → "가드는 앵커가 있는 구절의 삭제, 목록 안 약화어, implement·RULES_DOCS 되돌림 동사의 부정을 잡는다. 앵커 없는 절(Plan-Close 회송, Report의 남은 단계, Run의 멈춤 조건 뒷부분)의 삭제는 잡지 않는다(06d M5, M12, M22, M28)"
- 앵커 줄이기:
  - implement Load: "is missing or has a code commit after its sha" + "Proof re-run"
  - intent Run: "Stop and report instead" + "cannot be undone or reaches other people"
  - rules: "finding in its work sets a `complete` plan back"
- 선택: `--through` 멈춤 조건은 기능의 안전장치다. intent Run에 앵커 "a red Proof remains after one fix round"를 하나 둘 만하다(M28).

## 변이표

| 묶음 | 건수 | red | green | SKIP |
|---|---|---|---|---|
| 내 가드 `r8/mut8.py` | 29 | 5 | 24 | 0 |
| `mut6.py` | 10 | 8 | 0 | 2 |
| `mut7.py` | 8 | 8 | 0 | 0 |
| 06c `r4/mut4.py` | 28 | 8 | 18 | 2 |
| `mutate_clean.py` | 23 | 20 | 0 | 3 |
| 06a `v2/mut.py` | 29 | 16 | 9 | 4 |
| 06b `r3/mut3.py` | 29 | 14 | 11 | 4 |
| 06a 재리뷰 정규식 | 19 | 14 | 5 | 0 |
| 06b 재리뷰 정규식 | 17 | 16 | 1 | 0 |
| 06c 재리뷰 정규식 | 13 | 9 | 4 | 0 |
| 내 재리뷰 정규식 `r8/rg_r8.py` | 13 | 4 | 9 | 0 |

## 이 브랜치 밖

- RULES_DOCS:88 "-> done"과 `--through`의 끝 사이의 긴장(06a–06c와 같다)
- 리뷰 발견과 그 수락이 어디에 기록되는지 정한 규칙이 없다. 세션이 바뀌면 (3)의 수락이 보이지 않는다. 다시 수락하면 출구는 있다.
