---
status: complete
revised: 2026-10-22
---

# plan-complete-order 리뷰 round 3 (06b)

**판정: 조건부 통과.** 06a의 Important 셋은 모두 해결됐다. 그런데 Plan-Close 조건 (2)를 고친 방식이 새 Important 하나를 만들었다. 조건이 reflect.md에서만 바뀌었고, 같은 조건의 다른 사본 넷(RULES_DOCS 두 곳, README, CHANGELOG)은 옛 형태 그대로 남아 서로 모순된다(발견 1). 고칠 것은 문구뿐이다.

## 범위

- 대상: `839bb825`, head `e87f9aa0`. 기준: `0bf95173`, `a470e29c`.
- 실행한 것:
  - 전체 게이트
  - 정리 커밋 변이(`$TMPDIR/pco/mutate_clean.py`), 06a 변이 29건(`v2/mut.py`), 내 변이 29건(`$TMPDIR/pco/r3/mut3.py`). 테스트 파일 여섯 개, `git checkout HEAD --`로 복구, 끝에 `git status` 비어 있음.
  - 재리뷰 정규식 변이: 06a의 19건(`r3/rg_mut.py`, HEAD 데이터)과 내 17건(`r3/rg_mut2.py`)
  - `reflect-plan-close`를 `_fixture_ws`/`_grade`로 채점: 내가 쓴 답 26개(`r3/grade_pc3.py`)와 저장된 run 답 14개(`r3/regrade.py`)
- 실행하지 않은 것: canary와 `claude -p`(다른 곳에서 돈다).
- 모델: Claude Opus, effort high.

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3856 passed, 3 skipped**, 207.91s |
| `make lint` | All checks passed |
| `ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 1. `/sc:intent --through` 충돌

Run(`intent.md:20`)의 체인을 끝까지 읽었다. RULES_DOCS는 `/sc:intent`에서 로드된다(`context_loader.py:191`).

implement --plan(`implement.md:19`), branch review(`review.md:20`), 게이트(`RULES_DOCS.md:86`)의 재리뷰 문장은 모두 "a `/sc:intent --through` run keeps its single fix round"로 끝난다. Run의 "then re-run the Proof and rewrite `Result:`"는 implement의 "Every later code change re-runs the Proof and rewrites `Result:`"와 같다. test(`test.md:17`)는 리뷰를 기다리는 수정을 지목만 한다. Plan-Close(`reflect.md:19`)가 지목하는 단계는 Run의 "leave the step Plan-Close names to the Report step"이 Report(`intent.md:22`)로 넘긴다. "propose, write nothing"은 "write it only when the user says yes"와 맞는다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 찾지 못했다.

남은 위험은 하나다. `--through`에서는 `RULES_DOCS.md:58`의 "`Result:` line naming the last commit that changed code"가 Plan-Close (2)와 함께 로드된다. 그 결과 Plan-Close가 없는 실패를 지목할 수 있고, 지목받은 `/sc:implement --plan`은 진입하지 않는다(발견 1).

**프로브.** `through_left_open`(`tasks.yaml:850`, ask-headless는 `:990` alias)은 브랜치의 `05-plan.md`·`README.md`에서 `complete` 줄을 찾는다. `_THROUGH_STATES`에 "README marked complete"가 생겨, 06a의 S25(`|README` 삭제)와 S26(`phase` 삭제)이 이제 red다.

## 2. 06a 발견의 해결

| 06a | 판정 | 근거 |
|---|---|---|
| 1 Plan-Close 고리 | **해결, 사본 남음** | `reflect.md:19` "(2) … and no commit after its sha changes code", `implement.md:13` Load 진입. 문구대로 따라가면 닫힌다. 그러나 같은 조건의 사본 넷이 옛 형태다(발견 1) |
| 2 성공 regex | 해결(06a 제안대로) | 주석이 한계를 말하고 `clos(?:e\|ing)`를 쓴다. 한계는 아래(발견 3) |
| 3 채점 데이터 | 해결 | 06a의 X5–X10이 모두 red다. single-marker 다섯 개만 green이다. 05a 문장도 고쳤다(`05a-plan-measurements.md:32`) |
| 4 가드 | 부분 | 06a 변이 red 4 → 15. 남은 green은 5절 |
| 5 README 상태 | 해결 | S25·S26 red |
| 6 review 포인터 | 해결 | `review.md:20` "with the earlier findings as acceptance criteria" |
| 7 RULES_DOCS:58 괄호 | 해결 | 문장으로 풀었다 |
| 8 `--through` 기록 | 해결 | `README.md:335`, `intent.md:20` |
| 9 기록·`import re` | 해결 | 다만 빈 줄 다섯 개가 남았다(발견 6) |
| 10 Deviations·phase 문장 | 해결 | `implement.md:19` "only when all its boxes are checked", `05-plan.md` Deviations 첫 항목 |

**상자가 다 찬 계획.** Load(`:13`) "goes straight to the Integrate step's Proof re-run" → Integrate(`:19`) "Every later code change re-runs the Proof and rewrites `Result:`"와 "on that clean HEAD … docs-only commit". Proof를 다시 돌리고 `Result:`를 HEAD sha로 쓴다. HEAD가 docs 커밋이어도 reflect (2)는 성립한다. 고리는 닫힌다.

**`reflect-plan-close` 성공 regex.**

- 저장된 run: 새 문구 6/6 통과, 옛 문구(`before/b1`) 1/1 실패.
- 내 제안 12개 중 3개 실패. 예: "I propose one docs-only commit: 05-plan.md status: complete, README phase: complete." 동사·화살표 없는 `status: complete`를 놓친다.
- 내 거절 14개 중 11개 통과("I won't mark it complete: …", "Can't close it: …"). 주석이 인정한 한계다.

## 3. 잃은 규칙 (0bf95173 → a470e29c → HEAD)

그대로 남은 것: implement의 Deviations·상자·`~~task~~`, 첫 상자의 `implementing`, Proof와 `Result:` 형식, 수락된 red, 되돌림(README는 그대로), "even when its Proof is green"; review의 멈춤 규칙과 사용자 수락·면제; load·auto-improve의 규칙(이유만 빠짐: PowerShell, bash export, "pid file behind"는 "leaves it stale"이 맡는다). intent Run·Report는 덧붙이기만 했다.

| 옛 규칙 | 지금 |
|---|---|
| implement "`status: complete` with an open box is a defect" | phase 파일 "only when all its boxes are checked"; index는 implement가 `complete`를 쓰지 않음; 저장소 계획은 `test_plan_checklist.py` |
| implement "(linked from the phase file's header)", "after the review, test and reflect gates", "before done" 둘 | 빠짐, 모두 Deviations에 있다 |
| reflect (1)+(2) "naming the last commit that changed code; no commit after that sha changes code" | 뒤의 것만. 앞의 것은 사본 넷에 남아 모순(발견 1) |
| reflect "name the condition that fails; the plan stays `implementing`" | "name it and the step that clears it"; 단계는 넷 중 둘(발견 4) |
| review "with no claim that they are fixed" | `RULES.md:10`(위임 맥락). inline round엔 포인터만; Deviations에 없음(발견 6) |
| gates `:86` 멈춤 규칙 전문 | "as the /sc:review Process step says" |
| load "without reading the records whole", "older machine not read" | "one Grep", "newest date, one per machine" |

Deviations의 빠진 구절 셋은 맞고, Phase 5가 둘을 더 적었다. 목록 밖은 review의 "no claim" 하나다.

## 4. 누더기 여부

길이(자, 0bf95173 → a470e29c → HEAD): implement Load 257 → 257 → 395, Integrate 2023 → 1621 → 1631, Plan-Close 871 → 985 → 982, review Process 691 → 615 → 651, intent Run 961 → 1017 → 1039, Report 518 → 633 → 633, load Sync 817 → 732, Load 965 → 707, RULES_DOCS:58 552 → 636 → 636.

처음 읽는 사람의 눈으로 본 것:

- **implement Load +138**: 고리를 닫는 데 필요하다. 그러나 붙인 자리 때문에 "otherwise analyze the requirements"의 "otherwise"가 "--plan이 없으면"이 아니라 "그 상태의 계획이 아니면"으로도 읽힌다(발견 5).
- **Plan-Close**: 같은 길이에서 조건 (2)가 한 형태가 됐다(06a의 이중 서술 해소). "which re-runs the Proof …"는 회송 이유라 받아들인다.
- **intent Run +22**("and rewrite `Result:`"): implement와 중복이지만 짧고 06a가 요구했다. Report의 "such as …"는 빼도 된다.
- **RULES_DOCS:58**: 괄호가 문장이 됐다. 이력 서술은 없다.
- 테스트·보고서를 맞추려고만 덧댄 절은 shipped 문구에 없다.

## 5. 새 테스트 가드

정리 커밋의 변이: 22 red, 1 SKIP(README 원문이 839bb825에서 바뀜). 06a 29건은 **red 15, green 11, SKIP 3**이다(S6·S27·S28은 원문이 바뀌었다). 내 29건은 **red 5, green 24**다.

green 가운데 기능을 되돌리는 것들:

- V3: implement가 Proof 녹색에 계획을 `complete`로 만든다. "never sets"는 남는다.
- V4: Load 진입을 "at the user's request"로 바꿔 06a 고리를 되살린다.
- V6: (3)을 Critical만 보게 한다.
- V9: `--through`의 "ask nothing" → "ask when unsure".
- V10: Run의 멈춤 문장을 지운다.
- V11: `--through`에 재리뷰 round를 더한다. 소유자가 금지한 충돌이다.
- V14: 리뷰 중단을 사용자 대신 리뷰어가 정한다.
- V16·V18·V19: 게이트의 "or accepted by the user", 상자 조건, `<never>`의 조건 미충족을 약화하거나 지운다.
- 06a의 S1, S5, S7, S8, S13–S15, S20.

나머지(V5, V7, V8, V12, V13, V15, V17, V20, V25–V28, S9, S23, S24)는 조건 추가, 자리 바꿈, 목록에 없는 약화어("can", "usually", "should", "when practical")다. 가드 주석은 이 부류를 canary에 맡긴다고 쓴다.

**과하게 묶는가.** 앵커는 3–9낱말이라 괜찮다. 약화어 검사는 `<workflow_gates>` 블록 전체에 걸려, 다른 게이트의 "unless"·"may"도 red로 만든다(발견 2).

## 6. 줄인 채점 데이터

06a의 19건을 HEAD에서 다시 돌렸다. **green은 single-marker 다섯 개(again, another, second, still, due)뿐**이다. 규칙 삭제(X1–X4), 넓힘(X5–X7, X10, X12), 부정 표지(X8, X9), 묶음 삭제 셋은 모두 red다. 주장과 맞는다.

내 17건:

- red: verb·`next`·`run` 삭제, 창 축소 둘, `unreviewed`·`before merg`·한국어·`n't` 삭제, "then" 창, 넓힘 셋(`complete`, `covers`, `found`)
- green: Y9(규칙 3 `fix|commit|F-1` → `fix`), Y10(`nobody` 삭제), Y12(`;`를 절 경계에서 뺌), Y13(`need(s|ed)` 삭제)

Y12·Y13은 경계·marker류다. Y9·Y10은 규칙 3을 지키는 문장이 없어서 green이다. 주석이 규칙 3으로 든 "Nobody re-reviewed the fix.", "The fix is unreviewed.", "…isn't done yet."과 규칙 2로 든 "Review the fix commit before merging."은 실제로는 규칙 1이 잡는다(Y6, Y7, Y11; 발견 6).

## 7. 기록

- **CHANGELOG `:15`**: "the `Result:` line is green and names the last code commit"가 옛 조건이고 수락된 red가 빠졌다(발견 1). 회송, yes에만 쓰기, `--through`가 재리뷰와 `complete`를 남기는 것은 shipped와 맞는다.
- **README `:315`**: implement 행 "ran on the last code commit"가 옛 조건이다(발견 1). `:316` review 행 "a code change after the `Result:` sha re-runs the Proof"는 새 조건과 맞는다.
- **feature README**: `phase: implementing`이 맞다. Documents에 이 파일(06b)이 아직 없다.
- **05-plan**: `implementing`이 맞다(Integration 상자 열림). 05a `:32`, 감사 `complete`, gap 분석 D "진행"도 맞다.

## 발견

### 1. Important: Plan-Close 조건 (2)의 사본 넷이 옛 조건으로 남아 모순된다

`reflect.md:19`는 "`Result:` … and no commit after its sha changes code"다. 다음 넷은 아직 "`Result:`가 마지막 코드 커밋을 가리킨다"고 말한다:

- `RULES_DOCS.md:58` "a `Result:` line naming the last commit that changed code"
- `RULES_DOCS.md:85` "the Proof ran on the last code commit (`Result:` line)"
- `README.md:315`(같은 문구)
- `CHANGELOG.md:15` "names the last code commit"

`:58`은 상태 규칙의 SSOT이고 `--through`에서 reflect와 함께 로드된다. 재현(문구로 따라감):

1. 리뷰 수정 F(코드)를 커밋하고 docs 커밋 R을 남긴다.
2. reflect가 (2) 실패로 `/sc:implement --plan`에 보낸다. Load 진입 뒤 Integrate가 HEAD=R에서 Proof를 돌려 `Result: R`을 쓴다.
3. reflect (2)는 성립한다. 그러나 `RULES_DOCS.md:58`대로면 R은 "the last commit that changed code"(F)가 아니라서 `complete`가 금지된다.
4. 그 규칙대로 `/sc:implement --plan`을 지목하면 Load 진입 조건("a code commit after it")이 거짓이라 아무 일도 없다. `--through`에서는 이 막다른 단계가 Report에 실린다.

수정(정확한 문구):

- `RULES_DOCS.md:58`: "its `## Proof` footer carries a `Result:` line naming the last commit that changed code, from a green run or with the user's recorded acceptance." → "its `## Proof` footer carries a `Result:` line from a green run or with the user's recorded acceptance, and no commit after that line's sha changes code."
- `RULES_DOCS.md:85`와 `README.md:315`: "the Proof ran on the last code commit (`Result:` line)" / "the plan's Proof ran on the last code commit (`Result:` line)" → "no code commit follows the Proof's `Result:` sha" / "no code commit follows the plan's `Result:` sha"
- `CHANGELOG.md:15`: "the `Result:` line is green and names the last code commit" → "the `Result:` line is green (or accepted by you) and no code commit follows it"
- `_GATE_ANCHORS["rules"]`에 "no commit after that line's sha changes code"를 더한다.

### 2. Suggestion: 가드 앵커 몇 개로 기능 되돌림 green을 줄인다

5절의 green은 다음 앵커로 잡힌다(전부 현재 문구에 있는 구절이다):

- `reflect Plan-Close`: "(3) no fix to a Critical or Important review finding"(V6)
- `implement Integrate`: "never sets the plan (index) or the README `complete`"(V3는 문장을 바꾸므로 red가 된다)
- `implement Load`: "has a code commit after it goes straight"(V4)
- `intent Run`: "ask nothing", "Stop and report instead when a choice cannot be undone or reaches other people"(V9, V10)
- `review Process`: "the user accepts the open findings or waives the re-review"(V14)
- `gates`: "or accepted by the user"(V16)
- `rules`: "only when every task checkbox is checked"(V18)
- `reflect bounds`: "or with a Plan-Close condition unmet"(V19)

V11(`--through`에 round 추가)은 앵커로 잡을 수 없다. `intent-through-*`에 transcript check를 하나 둔다: `/sc:review` Skill 호출이 셋 이상이면 실패.

약화어 검사 범위는 앵커가 든 문장으로 좁혀도 된다.

### 3. Suggestion: `reflect-plan-close` 성공 check가 흔한 제안 하나를 놓치고 거절을 거의 다 통과시킨다

수정:

- success 정규식에 갈래를 하나 더한다: `|\bpropos\w*\b[^.\n?]{0,80}\bcomplete\b`. 동사 없는 "I propose … status: complete"를 잡는다.
- 거절을 막는 check를 더한다:

```yaml
- type: output_not_regex
  tag: success
  pattern: >-
    (?i)\b(?:not|never|won't|cannot|can't|don't|do\s+not)\b[^.\n]{0,25}\b(?:mark|set|clos\w*|propos\w*)\b|\bnot\s+met\b|\bconditions?\s*\(?\d\)?\s*(?:fails|is\s+not)
```

이 check는 내 거절 11개 중 6개를 떨어뜨린다. 내 제안 12개와 저장된 positive run 7개 중 어느 것에도 걸리지 않는다(`r3/refusal.py`). 거절 둘을 채점 테스트에 되돌린다: "I won't mark it complete: the fix still needs review.", "Can't close it: review round 2 is missing." 주석의 "It cannot tell a proposal from a refusal"은 "It misses refusals that name no negation (…)"로 바꾼다.

### 4. Suggestion: Plan-Close가 실패 넷 중 둘에만 단계를 준다

(1)의 열린 상자와 수락되지 않은 red `Result:`에는 "the step that clears it"가 없다.

수정(`reflect.md:19`): "a code commit after the `Result:` sha to /sc:implement --plan" → "an open box or a code commit after the `Result:` sha to /sc:implement --plan" 그리고 "; a fix waiting for review to /sc:review" 뒤에 "; a red `Result:` to the user, who accepts it or has it fixed"를 더한다.

### 5. Suggestion: implement Load의 "otherwise"가 두 갈래로 읽힌다

수정(`implement.md:13`): "1. Load: Without --plan, analyze the requirements and technical context. With --plan, read plan doc + extract tasks; a split plan's index … phase list; a plan whose boxes are all checked and whose `Result:` sha has a code commit after it goes straight to the Integrate step's Proof re-run"

### 6. Suggestion: 기록과 테스트 데이터의 잔여

- `test_eval_harness.py:1332–1349` 주석의 규칙을 바로 붙인다. "Review the fix commit before merging.", "The fix is unreviewed.", "The review of the export change isn't done yet.", "Nobody re-reviewed the fix."는 Rule 1에 둔다.
- Rule 3에 둘을 더한다: "Nobody reviewed the fix."(Y10이 red가 된다), "No one has reviewed the F-1 change."(Y9가 red가 된다). 둘 다 HEAD에서 통과한다(`r3/rg_extra.py`).
- `test_eval_harness.py:1843, 1850, 1857, 1864, 1882`: `import re`를 지운 자리에 함수 첫 줄 빈 줄이 남았다. 지운다.
- 05-plan Deviations에 review의 "with no claim that they are fixed"(inline round에서는 `RULES.md:10` 포인터만 남음)를 더한다.
- feature README Documents에 06b를 더한다.

## 변이표

**06a(HEAD 재실행).**

- red 15: S2, S3, S4, S10, S11, S12, S16, S17, S18, S19, S21, S22, S25, S26, S29
- green 11: S1, S5, S7, S8, S9, S13, S14, S15, S20, S23, S24
- SKIP 3: S6, S27, S28(원문이 바뀌었다)

**내 29건(`r3/mut3.py`, 원문 변경 그대로).**

- red 5: V21 implement "where useful", V22 reflect "if you like", V23 rules "ideally", V24 intent Run "when convenient", V29 plan-close regex `clos… (it|out|…)` 갈래 삭제
- green 24: 5절의 V3, V4, V6, V9, V10, V11, V14, V16, V18, V19와 V1 "usually goes back", V2 "when practical", V5 "or right away in a headless run", V7 `complete` 계획 유지, V8 회송 대상 맞바꿈, V12 Report 남은 단계 "(merge; push)"만, V13 "when the user asks", V15 "should the user want one", V17 "when the user asks for it", V20 README "to the run itself", V25 "can set it back", V26 `through_left_open` 필터 `05-plan[^/]*`, V27 verb `update` 삭제, V28 창 60 → 15

**재리뷰 정규식.** 06a의 19건: green 5(single marker), red 14. 내 17건: green 4(Y9, Y10, Y12, Y13), red 13.

## 이 브랜치 밖

- `RULES_DOCS.md:88` "every gap /sc:reflect names is fixed … or accepted"와 `--through`의 끝 사이의 긴장은 그대로다(06a와 같음).
- `implement.md` Load는 상자가 다 찼는데 `Result:` 줄이 없는 계획을 다루지 않는다. 이전부터 있던 틈이다.
