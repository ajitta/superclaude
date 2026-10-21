---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 6 (06e)

**판정: 조건부 통과.** 06d의 Important는 해결됐고 `--through`와 충돌하는 문장도 없다. 그러나 새 Important가 하나 있다. Plan-Close 조건 (3)의 "no fix to one waits for another /sc:review round"를 `/sc:reflect`가 로드하는 문맥 어디에서도 정의하지 않는다. HEAD의 실제 run 하나(`r8/x3` review-due)가 이를 "리뷰 파일이 다음 round를 요청하지 않는다"로 읽고, 리뷰되지 않은 수정이 남은 계획에 `complete`를 제안했다. `reflect-plan-close-review-due` 프로브는 그 답을 통과시킨다(발견 1). 수정은 문장 하나다.

## 범위

- 대상: `917916b1`. 기준: `0bf95173`, `fe782c23`. 06d와 `git show 5fa666a9`를 먼저 읽었다.
- 실행한 것:
  - 전체 게이트
  - 가드 변이: 내 24건(`$TMPDIR/pco/r9/mut9.py`)과 앞선 여덟. 재리뷰 정규식 변이: 앞선 넷과 내 16건
  - `reflect-plan-close` 채점: `_fixture_ws`/`_grade`, HEAD의 `git archive` 사본에서, 내 제안 15개와 거절 15개
  - 저장된 실제 run 38개(`$TMPDIR/pco/*/*/sc-full/logs/reflect-plan-close*.stream.jsonl`의 `result`)를 fe782c23·HEAD·후보 정규식으로 다시 채점했다(`r9/regrade.py`, `cand.py`, `due_cand.py`, `d06cand.py`).
- 변이: markdown 변이에서는 shipped 문구를 읽지 않는 `test_eval_harness.py`를 뺐다(`r9/runner.py`). 끝난 뒤 `git status`는 비어 있었다.
- 실행 안 함: canary, `claude -p`(병행 중). 그 run의 `r8/*` 로그는 증거로만 읽었다.
- 모델: Claude Opus, effort high

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3857 passed, 3 skipped**, 155.36s |
| `make lint` | All checks passed |
| `uv run ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 규칙과 그 사본

| 규칙 | 사본 | 일치 |
|---|---|---|
| `complete`는 Plan-Close에서 사용자 yes로만 | implement:19, reflect:19·46, RULES_DOCS:58·88, intent:20·22, README:315·318·335, CHANGELOG:15, tasks.yaml:854–857 | 일치 |
| 조건 (2): `Result:` 뒤 코드 커밋 없음 | reflect:19, RULES_DOCS:58·85, README:315·316, CHANGELOG:15 | 일치 |
| 수정이 재리뷰를 기다린다는 것의 뜻 | 정의: implement:19, review:20, RULES_DOCS:86, test:17("changes reviewed code or shipped content", "after the last review round"). 사용: reflect:19 (3), CHANGELOG:15, tasks.yaml:697 | **reflect:19에 정의가 없다(발견 1)** |
| `complete` 계획을 되돌리는 계기 | reflect:19 "`Result:` is red or … (3) fails" ↔ implement:19, RULES_DOCS:58, CHANGELOG:15 "a red (Proof) re-run, or a … finding" | 대체로 일치. 수락된 red에서 갈린다(발견 3) |
| `Result:` 없음 또는 그 뒤 코드 커밋 → `/sc:implement --plan` | implement:13, reflect:19, CHANGELOG:15 | 일치 |
| 재리뷰와 멈춤 | implement:19, review:20, RULES_DOCS:86·88, test:17, README:316·318, CHANGELOG:15 | 일치 |
| `--through`: 한 번의 수정, 남은 일은 Report로 | intent:20·22, implement:19, review:20, RULES_DOCS:86, README:335, CHANGELOG:15, tasks.yaml:852·997 | 일치 |

## 1. `/sc:intent --through` 충돌

Run(intent:20)의 체인을 끝까지 따라갔다. brainstorm → spec review → design → plan → implement --plan → branch review → 한 번의 수정 → Proof 재실행 → test → reflect → Report.

- implement:19와 review:20의 재리뷰 문장은 둘 다 "keeps its single fix round"로 끝난다. RULES_DOCS:86도 같다.
- `max: 2`(tasks.yaml:852)는 리뷰 두 번과 맞다.
- Run "re-run the Proof and rewrite `Result:`"는 implement:19 "Every later code change re-runs the Proof and rewrites `Result:`"와 같다. test:17은 지목만 한다.
- Plan-Close가 (3) 실패로 `/sc:review`를 지목한다. Run은 "leave the step Plan-Close names to the Report step"으로 받는다. Report:22는 그것을 사용자에게 남긴다. red는 Run의 멈춤 조건이 먼저 잡는다.
- 5fa666a9의 새 문장은 `complete` 계획에만 걸리므로 `--through`에 닿지 않는다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 없다. RULES_DOCS:88 "-> done"과의 긴장은 06a–06d와 같다(브랜치 밖).

**프로브.** `through_left_open`(tasks.yaml:856–866)은 `05-plan.md`와 README만 본다. `_THROUGH_STATES`(test_eval_harness.py:1709)의 "phase file marked complete"는 통과, "plan/README marked complete"는 실패다. 내 N19(필터에서 README 삭제)는 red다.

## 2. 06d 발견의 해결

| 06d | 판정 | 근거 |
|---|---|---|
| 1 Important, 되돌림 계기 | **해결** | reflect:19. 다른 기능의 코드 커밋은 이제 되돌림이 아니다. 남은 차이는 수락된 red(발견 3) |
| 2 (3)의 근거 | **해결, 그러나 불충분** | "from the plan file, the review findings and `git log`". 리뷰 발견을 읽어도 언제 수정이 round를 기다리는지가 없다(발견 1) |
| 3 정규식 | **일부, 나머지는 이유를 들어 거절** | 성공 쪽에 commit·chang·mov, 거절 쪽에 `shouldn't`, 주석 수정. 06d 거절 후보는 실제 올바른 제안 18개 중 16개를 떨어뜨린다(`d06cand.py`, "No later code commits"). **거절에 동의한다.** `commit`은 명사에도 맞는다(발견 2) |
| 4 CHANGELOG waive | **해결** | CHANGELOG:15. waive는 같은 항목의 "waive the re-review"가 덮는다 |
| 5 가드 기록·앵커 | **해결** | Deviations 바로잡음, 06d M28 red. 짧아진 rules 앵커는 새 구멍(발견 4) |

**06c 4 거절분(약화어 목록).** 목록을 round마다 늘리는 것은 덧댐이라는 이유에 동의한다. 목록 밖 낱말("can", "as a rule of thumb")은 모두 green이고, 목록으로 끝날 일이 아니다. Suggestion으로 둔다.

**Plan-Close에 출구 없는 고리가 있는가.** 없다.

- 열린 상자, 없는 `Result:`, sha 뒤 코드 커밋 → implement:13은 상자가 다 차 있으면 "goes straight to the Integrate step's Proof re-run"으로 보낸다. Integrate(:19)가 Proof를 돌리고 docs 커밋으로 `Result:`를 다시 쓴다. 열린 상자는 마지막 상자에서 같은 일을 거친다.
- 리뷰 대기 → review:20의 round(발견 없음, 수락, waive로 멈춤). 열린 발견과 red → 사용자가 수락하거나 고친다.

**`reflect-plan-close` 성공 정규식(내 문장, `_grade`).**

- 제안 15개 중 11개가 통과한다. 놓친 넷: "Want me to write `status: complete`", "ready for `status: complete`", "wait for your yes before writing", "record it as complete"
- 거절 15개 중 5개만 떨어진다. 통과한 열 가운데 넷은 HEAD가 넓힌 동사 탓에 새로 통과한다(fe782c23에서는 떨어졌다). 예: "There's a code commit after the Result: sha, so the plan can't be complete yet", "Condition (3) does not hold, so no change to complete is proposed"
- 실제 run: 닫을 수 있는 답은 HEAD에서 18/19가 통과한다. 떨어진 하나는 바꾸기 전의 `before/b1`이다. review-due 답 19개 가운데 성공 정규식을 통과하는 것은 `r8/x3` 하나다. 그 답은 실제로 `complete`를 제안했다(발견 1).

## 3. 잃은 규칙 (0bf95173 → fe782c23 → HEAD)

fe782c23 → HEAD의 shipped 변경은 reflect:19 하나다.

06d 3절의 대응표(0bf95173 → fe782c23)를 다시 확인했다. implement의 "open box is a defect", red run, "closes only on acceptance", review의 "no claim that they are fixed"(`RULES.md:10`), RULES_DOCS:86의 멈춤 조건(review:20 포인터), load·auto-improve의 압축은 모두 다른 곳에 남아 있다. fe782c23 → HEAD에서 좁아진 것은 하나다. 열린 상자가 있는 `complete` 계획은 이제 되돌리지 않고 implement로만 보낸다. `Result:`가 없는 옛 `complete` 계획을 그대로 두는 것은 업그레이드 노트(CHANGELOG:16)와 맞으므로 손실은 작다.

Deviations의 세 구절은 맞다. 목록 밖에서 잃은 규칙은 없다.

## 4. 누더기 여부

길이(자, 0bf95173 → fe782c23 → HEAD):

- implement Load 254 → 414 → 414, Integrate 2020 → 1628 → 1628
- **Plan-Close 866 → 1154 → 1259**
- review Process 688 → 648 → 648
- intent Run 958 → 1036 → 1036, Report 515 → 630 → 630

판단:

- **Plan-Close +105**는 근거 "the review findings"와 되돌림 문장이다. 기능에 필요하다. 다만 "a code commit after its sha only needs the Proof re-run"은 같은 단계의 회송 절("a code commit after its sha to /sc:implement --plan, which … re-runs the Proof")을 되풀이한다. 그리고 그 절만 지키는 앵커(test_docs_ssot_guards.py:580)가 붙었다. "any other failing condition leaves it `complete`"로 바꾸면 짧아지고 옛 계획도 덮는다(발견 3).
- Plan-Close는 조건 셋, 회송 셋, 되돌림 하나가 든 1259자 한 줄이다. 무겁지만 이력 서술이나 괄호 겹침은 없다.
- intent Run/Report는 그대로다(06d 판단). Plan-Close 앵커 15개는 규칙 구절 위에 있어 받아들일 만하다.

## 5. 새 테스트 가드

**내 24건(`r9/mut9.py`): red 4, green 20.**

- red: N4 "can re-run"(앵커 "rewrites `Result:`"가 깨짐), N10 review의 `--through` 문장 삭제, N19 `through_left_open`에서 README 삭제, N20 review-due의 `*rereview_named` 삭제
- green, 규칙이 틀려지고 canary도 못 잡는 것:
  - **N1** "a code commit after its sha also sends it back"(06d 1의 재도입)
  - **N2** "re-running the Proof first"
  - **N6** implement Load "goes straight to the Execute step, skipping the Proof re-run"(앵커 "Proof re-run"이 남는다)
  - **N8** rules "neither a red re-run nor a … finding in its work sets a `complete` plan back"(짧아진 앵커가 남는다)
  - **N17** (3)에 "requested in the review file"(`r8/x3`의 오독 그대로)
  - **N21** RULES_DOCS:58에서 "from a green run or with the user's recorded acceptance" 삭제
  - **N22** implement "it counts once reported"
- green, canary가 잡는 것: N12 `--through`가 `complete`를 씀(`through_left_open`), N24 `--through` 재리뷰(`max: 2`)
- green, 목록 밖 약화어나 덧붙인 조건: N3, N5, N7, N9, N11, N13–N16, N18, N23

N6·N8은 앵커가 있는 절의 부정·우회다. Phase 8이 앵커를 짧게 한 결과다(발견 4).

**앞선 묶음(HEAD):**

| 묶음 | 건수 | red | green | SKIP |
|---|---|---|---|---|
| 내 가드 `r9/mut9.py` | 24 | 4 | 20 | 0 |
| 구현자 `mut8.py`(주장 7 red) | 7 | **7** | 0 | 0 |
| `mut7.py` | 8 | 7 | 0 | 1(`shouldn't`로 원문 바뀜) |
| 06d `r8/mut8.py` | 29 | 6(M28 새로 red) | 22 | 1(M4 원문 바뀜) |
| `mut6.py` | 10 | 8 | 0 | 2 |
| 06c `r4/mut4.py` | 28 | 8 | 18 | 2 |
| `mutate_clean.py` | 23 | 20 | 0 | 3 |
| 06a `v2/mut.py` | 29 | 16 | 9 | 4 |
| 06b `r3/mut3.py` | 29 | 14 | 9 | 6 |
| 재리뷰 정규식 06a·06b·06c·06d | 19·17·13·13 | 14·16·9·4 | 5·1·4·9 | 0 |
| 내 재리뷰 정규식 `r9/rg_r9.py` | 16 | 14 | 2 | 0 |

## 6. 줄인 채점 데이터

`_RG_*`와 정규식은 fe782c23 이후 그대로이고 앞선 넷의 결과도 06d와 같다. 06a의 green 다섯은 주장대로 표지 again, another, second, still, due의 단독 삭제다.

내 16건:

- red 14:
  - 규칙 1: `need`, `n't`, `unreviewed`, `before merg`, `re-?review` 삭제. review 주제 lookahead 삭제. 표지 `fix`·`done` 추가
  - 규칙 2: `get`, `next` 삭제, 창 25 → 80
  - 규칙 3: `nobody` 삭제, 창 10 → 40, fix lookahead 삭제
- green 2: `not yet`, `2차` 삭제. 같은 문장을 `n't`와 `필요`가 잡는다. 대안 하나 삭제의 한계로 받아들인다.

규칙 1, 2, 2b, 3마다 삭제를 잡는 통과 문장과 넓힘을 잡는 실패 문장이 모두 있다.

05a:32의 알려진 놓침 셋은 HEAD에서도 놓친다.

## 7. 기록

- **CHANGELOG:15**는 조건 셋, yes에만 쓰기, `/sc:implement --plan`, `--through`가 남기는 일(재리뷰와 `complete`)에서 shipped와 맞는다. 되돌림 계기 "a red Proof re-run"은 implement·RULES_DOCS와 같다. reflect와는 수락된 red에서만 갈린다(발견 3).
- **README :315–:335**, **feature README**(`implementing`, Documents에 06d), **05-plan**(`implementing`, 열린 상자는 Integration 넷)은 맞다.
- **Deviations Phase 8**의 측정(닫을 수 있는 답 15/15, review-due 0/15, 바꾸기 전 0/2, 06d 후보로 16 중 14 실패, `mut8.py` 7 red)은 다시 잰 값과 맞는다(이후 run을 더하면 18/19, 16/18). review-due 채점에는 이 정규식이 없어서, "0/15"가 프로브의 제안 검출을 뜻하지는 않는다(발견 1).
- **Deviations Phase 7** "되돌림 동사의 부정을 잡는다"는 Phase 8에서 rules 앵커를 짧게 한 뒤 "neither … nor" 형태에서 거짓이 됐다(N8, 발견 4).
- 분석 문서(`complete`), gap 분석 D("진행"), 05a:32도 맞다.

## 발견

### 1. Important: Plan-Close (3)의 "waits for another /sc:review round"가 `/sc:reflect` 문맥에서 정의되지 않는다. 실제 run이 오독했고, 프로브가 그 답을 통과시킨다

`/sc:reflect`에는 RULES_QUALITY와 RULES_INTERACTION만 로드된다(`check_triggers("/sc:reflect --type completion …")`). 가드 주석 test_docs_ssot_guards.py:515–517도 그렇게 적는다. 언제 수정이 round를 기다리는지는 implement:19, review:20, RULES_DOCS:86, test:17에만 있다. reflect:19는 "no fix to one waits for another /sc:review round"라고만 쓴다.

재현:

- HEAD에서 돈 `$TMPDIR/pco/r8/x3/sc-full/logs/reflect-plan-close-review-due.stream.jsonl`. round 1 뒤 F-1 수정 커밋이 있는 fixture에서: "`06-review.md` records only round 1 … Nothing in it asks for another round. If you want an independent re-review … run `/sc:review` first. All three conditions hold, so I propose one docs-only commit … → `complete`"
- 같은 HEAD의 `r8/x2`, `r8/cmds`와 이전 16개는 맞았다. HEAD에서 3개 중 1개다.
- `_grade`로 채점하면 이 답은 review-due의 다섯 check를 모두 통과한다("re-review"가 `rereview_named`의 표지다). 병행 canary도 통과로 셀 것이다.

수정(reflect:19):

- 바꿀 구절: "and no fix to one waits for another /sc:review round."
- 새 구절: "and every fix to one that changed reviewed code or shipped content after the last /sc:review round has had another round or the user waived it."
- 앵커(test_docs_ssot_guards.py:582): "another /sc:review round" → "after the last /sc:review round"

### 2. Suggestion: review-due 프로브에 제안 거절 check가 없고, 성공 정규식의 `commit`이 명사에 맞는다

- review-due(tasks.yaml:700–722)는 "names the review"만 본다. 재리뷰를 선택으로 돌리고 `complete`를 제안하는 답이 통과한다(발견 1).
  - 후보: `output_not_regex` `(?i)\ball (three|3) (Plan-Close )?conditions (hold|are met)\b|\ball (three|3) hold\b`
  - 실제 review-due 답 19개 가운데 `r8/x3` 하나에만 맞는다(`due_cand.py`). 낱말 check라는 한계가 있다.
  - 채점 테스트의 review-due 쪽에 `r8/x3`의 "All three conditions hold, so I propose one docs-only commit" → False를 넣는다.
- reflect-plan-close 성공 정규식에서 `commit`을 동사 묶음에서 빼고 `|\bcommit\s+`?(?:status|phase):\s*complete\b`를 더한다.
  - 실제 run: 닫을 수 있는 답 18/19 그대로, review-due 1/19 그대로
  - 채점 테스트 15건 불일치 0
  - 내 거절 15개 가운데 잘못 통과하는 것: 10 → 8(`cand.py`)

### 3. Suggestion: `complete` 계획의 되돌림 문장이 수락된 red를 되돌리고, 회송 절을 되풀이한다

reflect:19 "whose `Result:` is red"는 "(accepted by user)"가 붙은 red도 덮는다. 조건 (2)는 그것을 성립으로 본다. implement:19, RULES_DOCS:58, CHANGELOG:15는 "a red re-run"이라고 쓴다. 수락하지 않은 red 재실행은 implement가 이미 되돌리므로, 이 절이 실제로 걸리는 것은 거의 수락된 red다.

수정:

- 바꿀 문장: "A `complete` plan whose `Result:` is red or whose condition (3) fails is proposed back to `implementing`, the README `phase:` unchanged; a code commit after its sha only needs the Proof re-run"
- 새 문장: "A `complete` plan whose `Result:` is red and not accepted, or whose condition (3) fails, is proposed back to `implementing`, the README `phase:` unchanged; any other failing condition leaves it `complete`"
- 앵커 두 개(test_docs_ssot_guards.py:578, :580)도 함께 바꾼다.

### 4. Suggestion: 짧아진 앵커가 부정과 우회를 놓친다

- N8 "neither a red re-run nor a … finding in its work sets a `complete` plan back"가 green이다.
  - rules 앵커(:539)를 "re-run or a Critical or Important finding in its work sets a `complete` plan back"으로 바꾼다.
- N6 "goes straight to the Execute step, skipping the Proof re-run"이 green이다.
  - implement Load 앵커(:569) "Proof re-run"을 "the Integrate step's Proof re-run"으로 바꾼다.
- 수락 규칙에 앵커를 하나씩 둔다. 둘 다 green이다.
  - rules "from a green run or with the user's recorded acceptance"(N21)
  - implement Integrate "counts only once the user accepts it"(N22)
- 기록: Deviations Phase 7의 "되돌림 동사의 부정을 잡는다" 뒤에 "(rules의 'neither … nor' 형태는 앵커를 고치기 전까지 놓친다)"를 넣는다. 앵커를 고치면 지운다.

## 이 브랜치 밖

- RULES_DOCS:88 "-> done"과 `--through`의 끝 사이의 긴장(06a–06d와 같다)
- 리뷰 발견과 그 수락을 어디에 적는지 정한 규칙이 없다. `/sc:review`가 파일을 쓰지 않으면, 세션이 바뀐 뒤 (3)의 근거가 사라진다.
- 병합 뒤 다른 기능의 코드 커밋이 있으면, 오래된 `complete` 계획에도 Plan-Close가 `/sc:implement --plan`의 Proof 재실행을 지목한다. 되돌림은 아니지만, master에 docs 커밋을 낳는다.
