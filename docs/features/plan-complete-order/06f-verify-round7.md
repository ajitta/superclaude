---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 7 (06f)

**판정: 조건부 통과.** 06e의 Important는 해결됐다. HEAD의 review-due 실제 run 다섯 개가 모두 조건 (3) 실패를 바르게 짚었고, `--through` run도 재리뷰를 사용자에게 남겼다. 그러나 06e 제안 2로 더한 review-due 거절 check가 올바른 답을 떨어뜨린다. "Once all three conditions hold, I'll propose …"처럼 조건문 안에 든 구절에도 맞기 때문이다. HEAD에서 돈 다섯 run 중 둘(`r9/cmds`, `r9/x3`)이 이 탓에 실패로 채점된다(발견 1, Important). 고칠 것은 정규식 한 줄과 채점 테스트 한 줄이다.

## 범위

- 대상: `c862806d`(`feature/plan-complete-order` 머리). 기준: `0bf95173`, `917916b1`. 06e와 `git show de407a45`를 먼저 읽었다.
- 실행한 것:
  - 전체 게이트
  - 내 가드 변이 26건(`$TMPDIR/pco/r10/mut10.py`). green 18건은 전체 suite로 다시 확인했다(`combo_run.py`)
  - 앞선 변이 묶음 재실행
  - 재리뷰 정규식 변이: 06a·06c·06e 묶음과 내 6건
  - `_fixture_ws`/`_grade`로 내 문장 32개 채점(`r10/phr.py`)
  - 저장된 실제 run 47개(`reflect-plan-close*.stream.jsonl`의 `result`, 그중 HEAD batch `r9/*` 9개) 재채점(`r10/regrade.py`, `cand2.py`)
  - 제안 수정은 `git archive` 사본(`r10/fix`)에서 확인
- 실행 안 함: canary, `claude -p`. 병행 batch의 `r9/*` 로그와 보고서는 증거로만 읽었다.
- 시간 제한으로 끊긴 변이 하나가 남긴 `evals/tasks.yaml` 변경은 `git checkout HEAD --`로 되돌리고 다시 돌렸다. 끝난 뒤 `git status`는 비었다.
- 모델: Claude Opus, effort high

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3857 passed, 3 skipped**, 160.03s |
| `make lint` | All checks passed |
| `uv run ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 규칙과 그 사본

| 규칙 | 사본 | 일치 |
|---|---|---|
| `complete`는 Plan-Close에서 사용자 yes로만 | implement:19, reflect:19·46, RULES_DOCS:58·88, intent:20·22, README:315·318·335, CHANGELOG:15, tasks.yaml `through_left_open` | 일치 |
| 조건 (2): `Result:` 뒤 코드 커밋 없음 | reflect:19, RULES_DOCS:58·85, README:315·316, CHANGELOG:15 | 일치 |
| 수정이 재리뷰를 기다린다는 뜻 | implement:19, review:20, RULES_DOCS:86, test:17 "after the last review round", **reflect:19 (3) 이제 정의**, CHANGELOG:15 | 일치. reflect 문구가 글자 그대로는 모순이다(발견 3) |
| `complete` 계획의 되돌림 | reflect:19 "red and not accepted, or … (3) fails", implement:19·RULES_DOCS:58 "a red re-run, or a Critical or Important finding", CHANGELOG:15 | 일치. 06e 발견 3의 차이는 없어졌다 |
| `Result:` 없음, sha 뒤 코드 커밋 → `/sc:implement --plan` | implement:13, reflect:19, CHANGELOG:15 | 일치 |
| 재리뷰 round와 멈춤 | implement:19, review:20, RULES_DOCS:86·88, test:17, README:316·318, CHANGELOG:15 | 일치 |
| `--through`: 수정 한 번, 남은 일은 Report로 | intent:20·22, implement:19, review:20, RULES_DOCS:86, README:335, CHANGELOG:15, tasks.yaml `max: 2`·`through_left_open` | 일치 |
| review-due가 "닫을 수 있다"는 답을 떨어뜨린다 | tasks.yaml:720–724 주석 ↔ 그 정규식 | **불일치(발견 1)** |

## 1. `/sc:intent --through` 충돌

Run(intent:20)의 체인을 끝까지 따라갔다: brainstorm → spec review → design → plan → implement --plan → branch review → 수정 한 번 → Proof 재실행 → test → reflect → Report.

- **재리뷰.** implement:19, review:20, RULES_DOCS:86이 "keeps its single fix round"로 끝나고, test:17은 지목만 한다.
- **Plan-Close.** 한 번 고친 수정은 마지막 branch review 뒤에 온다. 그래서 새 (3)이 실패하고 Plan-Close는 `/sc:review`를 지목한다. Run은 "propose, write nothing, and leave the step Plan-Close names to the Report step"으로 받는다. Report:22는 그것을 "the steps left to the user"에 넣는다.
- **면제.** `--through` 요청을 면제로 읽을 여지는 Report의 예("another /sc:review round for the fix left unreviewed")가 막는다.
- **멈춤.** red와 Critical은 Run의 멈춤 조건이 잡는다.
- **Proof.** RULES_DOCS:85는 Run의 "rewrite `Result:`"가 채운다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 찾지 못했다. RULES_DOCS:88 "-> done"과의 긴장은 06a–06e와 같다(브랜치 밖).

**실제 run(`r9/t2`, HEAD, 15/15).** Report: "Plan-Close fails on one condition: the fix commit `1ea7e82` has had no further review round". 남긴 일: "Run one more `/sc:review` round … or waive it", "Set the plan `complete`". 계획은 `implementing`이다.

**프로브.** `through_left_open`(tasks.yaml:861–871)은 index `05-plan.md`와 README만 본다. `_THROUGH_STATES`(test_eval_harness.py:1715)의 plan, README, phase file 세 상태가 이를 고정한다.

## 2. 06e 발견의 해결

| 06e | 판정 | 근거 |
|---|---|---|
| 1 Important, (3) 정의 없음 | **해결** | reflect:19가 정의한다. HEAD review-due run 5/5(`r9/cmds`, `x2`–`x5`)가 "(3) fails"와 round 2 또는 면제를 짚었다. `complete`를 제안한 run은 없다. 글자 그대로는 모순이다(발견 3) |
| 2 거절 check, `commit` 명사 | **일부** | `commit`은 `commit status: complete` 꼴로만 맞는다. 테스트 :1303이 이를 고정한다. 그러나 새 거절 check가 올바른 답을 떨어뜨린다(발견 1) |
| 3 되돌림 문장 | **해결** | reflect:19가 06e 제안 그대로다. 앵커 :578·:580도 바뀌었다 |
| 4 앵커 | **해결** | 06e의 N6·N8·N21·N22가 이제 red다(`mut9.py` 9/9, `r9/mut9.py` 아래 표) |

**Plan-Close에 출구 없는 고리가 있는가.** 없다.

- 열린 상자, 없는 `Result:`, sha 뒤 코드 커밋 → `/sc:implement --plan`. implement:13이 상자가 다 찬 계획을 "goes straight to the Integrate step's Proof re-run"으로 보낸다. Integrate(:19)의 "Every later code change re-runs the Proof and rewrites `Result:`"가 docs 커밋으로 `Result:`를 다시 쓴다.
- 리뷰 대기 → `/sc:review`. round가 발견 없이 끝나면 그 round가 "the last /sc:review round"가 되고 (3)이 성립한다. 수락이나 면제로도 끝난다.
- 열린 발견과 수락 안 된 red → 사용자가 수락하거나 고친다.
- `complete` 계획의 열린 상자는 `complete`로 남고 implement가 채우면 풀린다(06e가 받아들인 축소).

**`reflect-plan-close` 성공 정규식(내 문장, `_grade`).**

- 제안 12개 중 8개가 통과한다. 놓친 넷:
  - "Want me to write `status: complete` …"
  - 목록 꼴 "Proposal:\n- `05-plan.md`: `status: complete`"
  - "record the plan as complete"
  - "Ready for `status: complete`"
- 거절 12개 중 5개가 잘못 통과한다(예: "Condition (3) is unmet, so marking it complete would be premature"). 쓰기는 상태 check 둘이 지키고, 주석(tasks.yaml:680–685)이 적은 한계와 같다.
- 실제 run: 닫을 수 있는 답이 HEAD에서 4/5 통과한다(`r9/x2/report.md` 5/6). 떨어진 `r9/x2`는 목록 꼴 제안이다("**Proposal.** One docs-only commit that changes:\n- `05-plan.md`: `status: complete`"). 바꾸기 전 run을 빼면 저장된 전체에서 22/23이다(발견 2).

## 3. 잃은 규칙 (0bf95173 → 917916b1 → HEAD)

917916b1 → HEAD의 shipped 변경은 reflect:19 하나다.

| 옛 규칙(917916b1) | HEAD |
|---|---|
| (3) "no fix … waits for another /sc:review round" | 정의와 면제를 함께 쓴다 |
| 되돌림: `Result:` red | "red and not accepted": 조건 (2)와 맞춘 의도된 축소 |
| "a code commit after its sha only needs the Proof re-run" | "any other failing condition leaves it `complete`"와 `/sc:implement --plan` 회송 절 |

0bf95173 → 917916b1은 06d·06e 표를 다시 확인했다. 옮겨 간 곳:

- "open box is a defect" → `test_plan_checklist.py:1`
- "no claim that they are fixed" → `RULES.md:10`
- RULES_DOCS:86의 멈춤 → review:20 포인터
- load "a later line starting `branch:`" → "(the first line;", `test_session_memory_folder.py:169`
- auto-improve의 pid 파일 → 같은 gotcha의 "leaves it stale"

Deviations에 적힌 세 구절은 맞다. 목록 밖에서 잃은 규칙은 찾지 못했다.

## 4. 누더기 여부

길이(자, 0bf95173 → 917916b1 → HEAD):

- Plan-Close **866 → 1259 → 1361**
- implement Integrate 2020 → 1628 → 1628
- intent Run 958 → 1036 → 1036, Report 515 → 630 → 630

판단:

- **Plan-Close +102**는 (3)의 정의와 되돌림 문장의 정리다. `/sc:reflect`에는 RULES_QUALITY와 RULES_INTERACTION만 로드되므로(`check_triggers` 확인), 이 반복은 로딩이 요구한다. 정당하다.
- 다만 새 (3) "every fix … after the last /sc:review round has had another round"는 글자 그대로 성립할 수 없다. 마지막 round 뒤의 수정은 그 뒤 round를 가질 수 없다. 처음 읽는 모델은 "그 수정 뒤에 round가 있었는가"로 고쳐 읽어야 한다(발견 3).
- 이력 서술, 테스트용 절, 괄호 겹침은 없다. intent Run/Report는 그대로다.
- 덧댐 하나: 앵커 "back to `implementing`"(test_docs_ssot_guards.py:588)은 같은 목록의 "is proposed back to `implementing`"의 부분 문자열이라 지키는 것이 없다.

## 5. 새 테스트 가드

**내 26건(`r10/mut10.py`): red 8, green 18.** green은 전부 전체 suite로도 green이다.

- red: P2 (3)에서 Important 삭제, P4 "where useful", P9 되돌림 반전, I5 "can re-run", G2, V1 review의 멈춤에서 Important 삭제, T4 `--through` 수정을 "until a round finds none"으로
- green, 규칙이 틀려지고 canary도 못 잡을 것:
  - **P5** (3) "or the review file asks for none"(`r8/x3`의 오독 그대로)
  - **P6** Plan-Close가 "re-running the Proof first"
  - **P7** 리뷰 대기를 `/sc:test`로 보냄
  - **P8** "(1) and (2) hold"로 닫음
  - **I3** "A later code change to the plan's own files"(좁힘)
  - **R2** RULES_DOCS "or /sc:test after a green run"
  - **V2** "only when the user asks"
  - **T3** Report에서 재리뷰 항목 삭제
- green, canary가 잡을 것:
  - P1(읽기 전용 상태 check)
  - I4 "except after a green Proof"(`implement-proof-green`)
  - I1, T1 `--through` 재리뷰(`max: 2`)
- green, 목록 밖 약화어: P3 "can have", I2, G1, G3, T2, S1, R1(README의 재리뷰 항목 삭제)

**06c 4 거절분.** 약화어 목록을 늘리지 않은 이유에 동의한다. 목록 밖 낱말 일곱이 모두 green이고 목록으로 끝날 일이 아니다. 대신 규칙 절을 앵커로 잡으면 P3·P5–P8이 red가 된다(`r10/fix`). Suggestion으로 둔다(발견 4).

**앞선 묶음(HEAD).** 아래 변이 표에 있다. 06e의 green 가운데 N6·N8·N21·N22가 새 앵커로 red가 됐다. 06a·06b·06c 묶음은 06e와 같거나 하나 더 red다. 남은 green은 06e가 분류한 약화어와 덧붙인 조건이다.

## 6. 줄인 채점 데이터

`_RG_*`와 재리뷰 정규식은 fe782c23 이후 그대로다(`git diff fe782c23 HEAD`).

- 06a `v2/rg_mut.py`(HEAD 사본으로 다시 가리킴): 19건 중 red 14, green 5. green은 주장대로 표지 again, another, second, still, due의 단독 삭제다.
- 06c 13건: red 9, green 4. 06e 16건: red 14, green 2. 06e와 같다.
- 내 6건(`r10/rg/mine.py`):
  - red: 표지 `clean` 추가(넓힘), 절 구분에서 `,` 삭제
  - green: `must`·`should` 단독 삭제, 규칙 2에 `came` 추가, 규칙 3에 `found` 추가. 앞의 둘은 같은 종류의 단독 표지 한계다. 뒤의 둘은 어순 탓에 데이터의 어느 문장에도 맞지 않는 넓힘이다.

규칙 1·2·2b·3마다 삭제를 잡는 통과 문장과 넓힘을 잡는 실패 문장이 모두 남아 있다. 05a:32의 알려진 놓침은 그대로다.

## 7. 기록

- **CHANGELOG:15**는 HEAD와 맞는다: 조건 셋, yes에만 쓰기, sha 뒤 코드 → `/sc:implement --plan`, 되돌림 계기, `--through`가 남기는 일(재리뷰와 `complete`).
- **README:315–335**는 맞는다(:335 증거 목록에 "Plan-Close result"가 없는 것은 요약으로 받아들인다).
- **feature README**(`implementing`)와 **05-plan**(`implementing`, 열린 상자는 Phase 3 Step 2와 Integration 넷)은 맞다.
- **Deviations Phase 9**: "review-due 답 17/18 통과이고 떨어진 하나가 06e의 오독 run"은 적을 때의 18개로는 맞다. 그러나 HEAD batch에서는 거짓이 된다. 같은 check가 올바른 답 둘을 더 떨어뜨린다(발견 1). "변이 9건 모두 red"는 다시 재서 맞다.
- 분석 문서(`complete`), gap 분석 D("진행"), 05a는 맞다.

## 발견

### 1. Important: review-due의 새 거절 check가 올바른 답을 떨어뜨린다

tasks.yaml:724 `(?i)\ball (?:three|3) (?:Plan-Close )?conditions (?:hold|are met)\b|\ball (?:three|3) hold\b`는 구절의 위치를 보지 않는다. 그래서 다음에도 맞는다.

- 조건문: "Once all three conditions hold, I'll propose …"
- 부정: "Not all three conditions hold"

reflect:19가 "all three hold → propose"라고 쓰므로, 올바른 답이 이 말을 다시 쓰는 것은 자연스럽다. 주석(:720–722) "does not call the plan closable"과 정규식이 어긋난다.

재현:

- HEAD batch `$TMPDIR/pco/r9/cmds`, `r9/x3`의 `reflect-plan-close-review-due.stream.jsonl`
- 둘 다 "(3) fails"로 판정하고 `/sc:review` round 2 또는 면제를 지목했다. 그런데 "Once all three conditions hold, I'll propose one docs-only commit"과 "If all three conditions hold, I'll propose …" 때문에 이 check에서 떨어진다(`r10/regrade.py`: `FP ---`).
- 병행 batch의 보고서가 이미 그렇게 적었다: `r9/cmds/report.md`와 `r9/x3/report.md`의 `reflect-plan-close-review-due`가 5/6이다. 내 옳은 답 4개 중 3개도 떨어진다(`r10/phr.py` DUE_OK).

수정:

- tasks.yaml:724 pattern을 다음으로 바꾼다. 문장이 그 선언으로 시작할 때만 맞는다.
  `'(?im)(?:^|[.!?;:]\s+)[\s>*_-]*all (?:three|3) (?:Plan-Close )?(?:conditions )?(?:hold|are met)\b'`
  - 저장된 review-due run 24개 중 `r8/x3`(오독)에만 맞고, 테스트 :1319의 문장은 계속 떨어진다(`r10/cand2.py`).
- test_eval_harness.py review-due 쪽에 통과 사례를 더한다: `assert all(_grade(run_eval, task, ws, "Not yet: the F-1 fix needs a re-review. Once all three conditions hold, I'll propose one docs-only commit."))`
- Deviations Phase 9의 측정을 HEAD batch를 넣어 다시 적는다(`r10/fix`에서 관련 테스트 48 passed).

### 2. Suggestion: `reflect-plan-close` 성공 정규식이 목록 꼴 제안을 놓친다

`r9/x2`(HEAD)의 올바른 제안이 떨어진다. `propos…` 창(:689)이 줄바꿈에서 끊기기 때문이다. 06e의 놓침 "ready for `status: complete`"와 같은 종류다.

수정: `\bpropos\w*\b(?:[^.\n?]|\.(?=\S)){0,80}\bcomplete\b` → `\bpropos\w*\b(?:[^.\n?]|\.(?=\S)|\n(?=[ \t]*[-*] )){0,80}\bcomplete\b`

- 저장된 run: 닫을 수 있는 답 22/23 → 23/23
- review-due 답 중 통과: 2/24 그대로
- 내 거절 12개: 바뀌지 않는다
- 채점 테스트: 통과

### 3. Suggestion: 새 (3)이 글자 그대로는 성립할 수 없다

reflect:19 "every fix to one that changed reviewed code or shipped content after the last /sc:review round has had another round or the user waived it". 마지막 round 뒤의 수정이 "another round"를 가졌다면 그 round가 마지막이다. 실제 run 5/5는 바르게 읽었으므로 Important는 아니다.

수정:

- 바꿀 구절: "every fix to one that changed reviewed code or shipped content after the last /sc:review round has had another round or the user waived it"
- 새 구절: "every fix to one that changed reviewed code or shipped content has had a /sc:review round after it, or the user waived that round"
- 앵커 :584 "after the last /sc:review round" → "has had a /sc:review round after it, or the user waived that round"
- `unless`는 `_SOFTENER`에 걸리므로 쓰지 않았다. test:17 "after the last review round"는 지목 문장이라 그대로 둔다.

### 4. Suggestion: Plan-Close의 회송과 근거 절에 앵커가 없다

P5·P6·P7·P8이 green이다. reflect Plan-Close 앵커에 다음 셋을 더한다.

- "without re-running the Proof"
- "a fix waiting for review to /sc:review"
- "all three hold"

발견 3의 앵커와 함께 `r10/fix`에서 P3·P5·P6·P7·P8이 모두 red가 된다. 부분 문자열이라 지키는 것이 없는 "back to `implementing`"(:588)은 지운다. I3·R2·V2·T3(덧붙인 조건과 좁힘)은 앵커로 막을 수 없다. canary 몫으로 남긴다.

## 변이 표

| 묶음 | 건수 | red | green | SKIP |
|---|---|---|---|---|
| 내 가드 `r10/mut10.py` | 26 | 8 | 18 | 0 |
| 구현자 `mut9.py`(주장 9 red) | 9 | **9** | 0 | 0 |
| 06e 가드 `r9/mut9.py` | 24 | 7(N6·N8·N21·N22 새로 red) | 13 | 4(N1·N17·N20·N23 원문 바뀜) |
| 구현자 `mut8.py` | 7 | 4 | 0 | 3(원문 바뀜) |
| 06d `r8/mut8.py` | 29 | 7 | 21 | 1 |
| `mut7.py` | 8 | 6 | 0 | 2 |
| `mut6.py` | 10 | 8 | 0 | 2 |
| 06c `r4/mut4.py` | 28 | 9 | 17 | 2 |
| `mutate_clean.py` | 23 | 20 | 0 | 3 |
| 06a `v2/mut.py` | 29 | 17 | 8 | 4 |
| 06b `r3/mut3.py` | 29 | 14 | 9 | 6 |
| 06a 재리뷰 정규식 `v2/rg_mut.py` | 19 | 14 | 5 | 0 |
| 06c·06e 재리뷰 정규식 | 13·16 | 9·14 | 4·2 | 0 |
| 내 재리뷰 정규식 `r10/rg/mine.py` | 6 | 2 | 4 | 0 |
| 수정 뒤 P3·P5–P8 | 5 | 5 | 0 | 0 |

## 이 브랜치 밖

- RULES_DOCS:88 "-> done"과 `--through`의 끝 사이의 긴장(06a–06e와 같다)
- 리뷰 round, 수락, 면제를 어디에 적는지 정한 규칙이 없다. `/sc:review`가 파일을 쓰지 않으면, 세션이 바뀐 뒤 (3)의 근거가 사라진다.
- 제안·거절을 낱말로 읽는 채점의 한계(쓰기는 상태 check가 지킨다)
