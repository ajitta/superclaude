---
status: complete
revised: 2026-10-22
---

# plan-complete-order 정리 커밋 독립 검증 (06a)

**판정: 조건부 통과.** 두 보고서의 Important 셋(Plan-Close 회송, 성공 regex, 채점 데이터)은 부분 해결에 그쳤다(발견 1–3). `--through`와 부딪히는 문장은 없고 게이트는 모두 녹색이다.

## 범위

- 대상: `ab7f0a96`(정리), head `a470e29c`. 비교 기준은 `0bf95173`(두 보고서의 대상)과 `v4.34.1`.
- 실행한 것:
  - 전체 게이트
  - shipped·테스트 변이 29건(`$TMPDIR/pco/v2/mut.py`, 테스트 파일 여섯 개, `git checkout HEAD --`로 복구)
  - 정리 커밋 자신의 변이 16건 재실행
  - 재리뷰 정규식 변이 19건(`v2/rg_mut.py`, HEAD 데이터)
  - `reflect-plan-close`에 직접 쓴 답 30개를 `_fixture_ws`/`_grade`로 채점(`v2/grade_pc.py`)
  - 저장된 run 답 14개 재채점(`$TMPDIR/pco/{before,after,clean}`)
- 실행하지 않은 것: `claude -p`와 canary. 다른 곳에서 돌고 있다.
- 모델: Claude Opus, effort high.

| 게이트 | 결과 |
|---|---|
| `uv run pytest` | exit 0, **3854 passed, 3 skipped**, 167.14s (`_GATE_PHRASES` 23 → `_GATE_ANCHORS` 14) |
| `make lint` | All checks passed |
| `ruff format --check src tests evals` | 228 files already formatted |
| `make typecheck` | no issues in 54 source files |

## 1. `/sc:intent --through` 충돌

`--through`에서는 intent·implement·review·test·reflect와 RULES_DOCS(`context_loader.py:191`)가 함께 로드된다. Run의 체인을 따라 읽었다.

- implement·review·게이트(`implement.md:19`, `review.md:20`, `RULES_DOCS.md:86`): 재리뷰 문장마다 "keeps its single fix round" 예외가 붙어 있다.
- test(`test.md:17`): 리뷰를 기다리는 수정을 지목만 한다.
- reflect(`reflect.md:19`): Plan-Close가 지목하는 단계는 Run의 "leave the step Plan-Close names to the Report step"(`intent.md:20`)이 막는다. reflect는 yes에만 쓰므로 Run의 "propose, write nothing"과 같다.
- Report(`intent.md:22`): Plan-Close 결과를 받는다.

묻기, round 더 돌기, `complete` 쓰기, 단계 재실행, 멈추기를 시키는 문장은 없다. 틈은 하나다. Run의 "then re-run the Proof"는 `Result:`를 다시 쓰라고 하지 않는다(발견 8). implement의 "Every later code change re-runs the Proof and rewrites `Result:`"가 같은 컨텍스트에 있어서 모순은 아니다.

프로브 `through_left_open`(`tasks.yaml:846`)은 브랜치의 `05-plan.md`와 `README.md`에서 `status:`·`phase: complete` 줄을 찾는다. ask-headless는 alias로 같은 check를 쓴다(parity 테스트 있음). `_THROUGH_STATES`에는 README 상태가 없어서 `|README`를 빼도(S25) `phase`를 빼도(S26) 녹색이다(발견 5).

## 2. 보고서 발견의 해결

| 발견 | 판정 | 근거 |
|---|---|---|
| 06-verify 1, 감사 1 (/sc:test 고리) | **부분** | `reflect.md:19`가 `/sc:implement --plan`으로 보낸다. 그러나 조건 (2)와 그 경로가 쓰는 `Result:`가 맞지 않고, implement에는 상자가 다 찬 계획의 진입이 없다(발견 1) |
| 06-verify 2, 감사 8 (성공 regex) | **부분** | 테스트의 거절 셋만 떨어진다(발견 2) |
| 06-verify 3–6, 감사 2·3 | 해결 | `RULES_DOCS.md:58`, `reflect.md:19`, 앵커 셋, implement 2023 → 1621자, CHANGELOG `:15`·`:17` |
| 감사 4 (가드) | 해결, 약함 | 5절 |
| 감사 5 (RULES_DOCS 중복) | 부분 | 멈춤 규칙은 포인터. `:58`과 `:88`은 둘 다 "Plan-Close에서 `complete`"라고 말한다(감사안 그대로) |
| 감사 6 (review) | 해결, 틈 | 발견 6 |
| 감사 7 (load) | 해결 | 817 → 732, 965 → 707 |
| 감사 9 (채점 데이터) | 해결, 과함 | 발견 3 |
| 감사 10 (helper) | 부분 | 함수 안 `import re` 다섯 번(`test_eval_harness.py:1830–1873`)과 step helper 둘이 남았다. 계획에 이유가 없다 |
| 감사 11–13 | 해결 | 발견 ID 제거, auto-improve 절, 분석 B "완료", README 과거형, 05-plan 24,179 B |

상자가 다 찬 계획에서 `/sc:implement --plan`이 Proof를 다시 돌리라는 말은 7단계 끝 한 문장뿐이다. Load·Execute는 과제만 뽑는다. "남은 과제 없음"으로 끝내는 읽기가 열려 있고, 이를 재는 프로브도 없다.

## 3. 잃은 규칙 (0bf95173 → HEAD)

| 옛 규칙 | 지금 |
|---|---|
| implement "`status: complete` with an open box is a defect" | 빠짐. Deviations는 `test_plan_checklist.py`가 맡는다고 쓴다. 그 테스트는 이 저장소의 계획만 본다(`_PLAN_GLOBS`). phase 파일 문장은 충분조건만 말한다(발견 10) |
| implement "after the review, test and reflect gates" | **목록 없이 빠짐.** Plan-Close가 reflect에 있어서 순서는 남는다 |
| implement 재리뷰의 "before done" | **목록 없이 빠짐.** 기능 손실은 작다 |
| reflect "(2) no commit after that sha changes code" | "names the last commit that changed code"로 합쳤다. 이 합침이 발견 1을 만든다 |
| review "earlier findings as acceptance criteria with no claim that they are fixed" | `RULES.md:10` 포인터. 그 규칙은 위임에만 걸린다(발견 6) |

나머지는 다른 곳이 맡거나 이유만 빠졌다: 게이트의 멈춤 규칙(`review.md:20`), load 괄호(명령은 남음), auto-improve pid("leaves it stale"), intent(덧붙이기만 함).

## 4. 누더기 여부

길이(자, 0bf95173 → HEAD): Plan-Close 871 → 985, intent Run 961 → 1017, Report 518 → 633, RULES_DOCS:58 552 → 636.

- **implement Integrate**: 순서대로 읽히고, 한 규칙에 한 문장이다.
- **Plan-Close**: 늘어난 부분은 회송 대상과 `complete` 계획의 되돌림이다. 06-verify가 요구한 것이라 정당하다. 그러나 조건 (2)("names the last commit that changed code")와 회송 문장("a code commit after the `Result:` sha")이 같은 조건을 두 형태로 말한다. 그 차이가 발견 1이다.
- **intent**: `--through` 요구에서 늘었다. Report의 "such as …" 예시는 빼도 된다.
- **RULES_DOCS:58**: 감사가 줄이라던 줄이 84자 늘었다. 괄호가 둘이고 둘째 괄호에 절이 셋 있다. 새로 덧댄 곳이다(발견 7).
- `--through` 예외 사본 셋은 각각 재리뷰 문장 옆에 있다. 감사 "그대로 둘 것 3"의 논리대로 받아들인다. 이력 서술은 없다.

## 5. 새 테스트 가드

정리 커밋의 16건을 다시 돌렸다: 16/16 red. 내 변이 29건(변이표)은 **red 4, green 25**다. 녹색은 목록 밖 약화어, 조건 추가, 앵커를 남긴 부정·자리바꿈이다. 기능을 되돌리는 녹색은 S1, S3, S6, S7, S8, S11, S12, S16, S18이다. S9, S13, S19, S24는 작위적이다.

앵커는 대부분 3–6낱말이라 문구를 과하게 묶지 않는다. 다만 `rules` 키는 RULES_DOCS 파일 전체이고 약화어 검사에서 빠진다. 그래서 `:58`의 되돌림 절은 지워도 녹색이다(S18).

## 6. 줄인 채점 데이터

HEAD 데이터(`_RG_REREVIEW` 9, `_RG_HEDGED` 2, `_RG_FAILS` 7)로 `tasks.yaml:540–545`의 규칙을 변이했다.

| 변이 | 결과 |
|---|---|
| 규칙 1, 2, 2("then"), 3 각각 삭제; "done" 표지 추가; "repeated" 묶음 삭제 | red ×6 |
| `(?!ed\|er)` 삭제, `(?!er)`로 | **green ×2** |
| 규칙 3의 fix/commit 조건 삭제(넓힘) | **green** |
| 규칙 1의 review 조건 삭제(넓힘) | **green** |
| 규칙 1 부정 표지 삭제, 규칙 3 부정어를 `not`만 | **green ×2** |
| 규칙 1 "needed"·"not-yet" 묶음 삭제 | **green ×2** |
| 표지 낱말 하나씩(again, another, second, still, due) | green ×5(허용) |

넓히는 변이 셋은 "끝난 리뷰" 답을 통과시킨다. 0bf95173의 `_RG_FAILS`에는 그것을 잡는 문장이 있었다. 05a가 "실패로 고정했다"고 적은 "…then reviewed by the same reviewer"와 주석의 예 "No review findings remain"이다. 정리에서 둘 다 빠졌다.

05a의 "줄어든 문장은 측정 집합(heldout2, heldout3)에 남아 있다"는 틀렸다. 옛 문장 59개 중 55개는 `$TMPDIR/rrg/*.json`에 없다. 그 파일도 저장소 밖이다.

## 7. 기록

- CHANGELOG `:15`는 shipped 문구와 맞는다(`/sc:implement --plan`, yes에만 쓰기, `--through`가 남기는 재리뷰와 `complete`). README `:335`만 재리뷰를 빠뜨린다(발견 8).
- 과장이나 틀린 기록: `tasks.yaml:680` 주석(발견 2), 05a의 측정 집합 문장(6절), Deviations 누락(발견 10), README Documents에 없는 `06-verify.md`(발견 9).
- 재현됨: 05-plan Step 6 재채점(바꾼 뒤 3/3, 바꾸기 전 1/1 실패). 분석 B와 review-reflect-gates의 상태는 서로 맞는다.

## 발견

### 1. Important: Plan-Close의 회송 경로가 문구대로는 닫히지 않는다

`reflect.md:19`의 조건 (2)는 "`Result:` line … names the last commit that changed code"다. 회송 문장은 "a code commit after the `Result:` sha to /sc:implement --plan"이다.

재현(문구로 따라감): 리뷰 수정 B(코드)를 손으로 커밋하고, round 2를 docs 커밋 C로 남긴다. `/sc:reflect`는 (2) 실패로 `/sc:implement --plan`에 보낸다. Integrate는 "on that clean HEAD"(C)에서 Proof를 돌려 `Result: C`를 쓴다. 다시 reflect를 돌리면 C는 B가 아니라서 (2)가 실패한다. 그런데 C 뒤에 코드 커밋이 없으니 회송 문장도 맞지 않는다. 지목할 단계가 없다.

또 `implement.md`에는 상자가 다 찬 계획을 위한 진입이 없다(2절).

수정:
- `reflect.md:19`: "and names the last commit that changed code;" → "and no commit after its sha changes code;"
- 같은 앵커를 `_GATE_ANCHORS["reflect Plan-Close"]`에서 바꾼다.
- `implement.md:13` Load 끝에 다음을 더한다: "; a plan whose boxes are all checked and whose `Result:` sha has a code commit after it goes straight to the Integrate step's Proof re-run"

### 2. Important: `reflect-plan-close` 성공 check가 거절을 통과시키고, 주석은 그 반대를 말한다

`tasks.yaml:680` 주석은 "A refusal (…) fails"라고 쓴다. `_grade`로 채점한 결과:

- 내가 쓴 거절 14개 중 6개가 통과했다(예: "I won't mark it complete until the review round is done.", "The plan should not be marked complete: …"). "I've marked the plan complete."도 통과했다.
- 저장된 review-due 답 6/6이 이 정규식에 맞았다. 예: `clean/cmds` "Plan-Close condition 3 fails, so I'm not proposing the `complete` commit"과 "If condition 3 holds then, I'll propose … `status: complete`"
- 반대로 "Recommend closing out the plan …"은 실패했다. `close\w*`는 closing을 잡지 못한다.

부정 lookbehind 셋은 테스트의 거절 문장만 막는다(과적합).

수정:
- 주석을 바꾼다: "# The answer names `complete` as a status change; it cannot tell a proposal from a refusal or deferral ("I'm not proposing the `complete` commit" passes). The two status checks are the guard."
- `close`를 `clos(?:e|ing)`로 바꾼다.

### 3. Important: 줄인 채점 데이터가 정규식의 제약을 지키지 못한다

`(?!ed|er)`, 규칙 3의 fix 조건, 규칙 1의 review 조건, 부정 표지, "needed"·"not-yet" 묶음을 각각 지워도 `test_test_reflect_gate_grades_answers`가 녹색이다(6절).

수정: `_RG_FAILS`에 0bf95173의 셋을 되돌린다: "The fix was committed and then reviewed by the same reviewer; /sc:reflect next.", "No review findings remain, ready to merge after /sc:reflect.", "Review done, the fix is in, nothing more is needed; /sc:reflect next." `_RG_REREVIEW`에 넷을 더한다: "Review the fix commit before merging.", "The fix is unreviewed.", "The review of the export change isn't done yet.", "No one has reviewed the fix." 이 일곱 개를 넣으면 표지 낱말 하나씩 지우는 다섯만 녹색으로 남는다(`v2/rg_mut.py`로 확인).

05a의 문장도 바꾼다. "줄어든 문장은 측정 집합(heldout2, heldout3)에 남아 있다" → "줄어든 문장은 `0bf95173`의 `tests/unit/test_eval_harness.py`에 있다".

### 4. Suggestion: 가드가 의미 약화를 거의 잡지 못한다

변이 25/29가 녹색이었다(변이표). 수정:

- 약화어 목록을 넓힌다: `_SOFTENER = re.compile(r"\b(may|might|optionally|if needed|consider|could|ideally|where useful|where possible|if you like|preferably|try to|unless|need not|no longer|when convenient)\b", re.I)`. 지금 고정한 본문에는 이 낱말들이 없다. gates에는 "can"과 "optional"만 있다. 이것으로 S2, S3, S4, S10, S11, S16이 red가 된다.
- 앵커를 더한다: reflect "is green or marked accepted by the user"(S6), intent Run "ones once"(S12), gates "on the user's yes to Plan-Close"(S19)와 "names the fix left unreviewed"(S21).
- `rules`는 Plan docs 줄만 잘라 되돌림 앵커 "back to `implementing`"을 둔다(S18).
- 나머지(조건 추가, 자리바꿈)는 canary 몫이라고 주석에 적는다.

### 5. Suggestion: `through_left_open`의 README 절반은 시험되지 않는다

`test_eval_harness.py:1654` `_THROUGH_STATES`에 README만 `phase: complete`로 바꾸는 상태를 더한다. 기대값은 `[_P] * 10 + [_F]`다. S25와 S26이 red가 된다.

### 6. Suggestion: review의 포인터가 위임 규칙을 가리킨다

`review.md:20`이 가리키는 `RULES.md:10`은 "when delegating to a sub-agent" 규칙이다. inline 재리뷰(`--structured` 없음)에는 "earlier findings as acceptance criteria"가 걸리지 않는다.

수정: "comes back for another round, packed as RULES.md Intent Propagation says." → "comes back for another round, with the earlier findings as acceptance criteria (RULES.md Intent Propagation)."

### 7. Suggestion: RULES_DOCS:58이 괄호를 겹쳐 쌓았다

수정: `RULES_DOCS.md:58`의 둘째 괄호를 문장으로 푼다.

"…with the user's recorded acceptance. /sc:implement writes the line; the user sets `complete` at the /sc:reflect Plan-Close step (below); a red re-run or a Critical or Important finding in its work sets a `complete` plan back to `implementing`. Departures from the plan, drops included, go under `## Deviations` in the same commit as the code that departed"

### 8. Suggestion: `--through` 기록 두 곳

- `README.md:335`: "leaves marking the plan complete, merge and push to you" → "leaves marking the plan complete, any review round its fix still needs, merge and push to you". 앵커는 그대로 남는다.
- `intent.md:20`: "then re-run the Proof" → "then re-run the Proof and rewrite `Result:`"

### 9. Suggestion: 기록과 정리가 덜 됐다

- README Documents에 `06-verify.md`와 이 파일을 더한다.
- 감사 10의 `import re` 다섯 개를 지우거나, 남긴 이유를 Deviations에 적는다.

### 10. Suggestion: Deviations가 빠진 규칙을 다 적지 않았다

- 목록에 없이 빠진 구절이 둘이다: "after the review, test and reflect gates"와 재리뷰의 "before done".
- `test_plan_checklist.py`는 이 저장소의 계획만 본다. 그래서 사용자 저장소에서 "open box면 `complete` 금지"는 implement 컨텍스트에서 사라졌다.

수정:
- `implement.md:19`: "and a phase file whose boxes are all checked gets `status: complete` and its box in the index checked" → "and a phase file gets `status: complete`, and its box in the index checked, only when all its boxes are checked"
- Deviations에 두 구절을 더한다.

## 변이표

| # | 변이 | 결과 |
|---|---|---|
| S1 | implement: "`complete`" 뒤 "before the Proof is green" | green |
| S2 | implement: "another round where useful" | green |
| S3 | implement: "need not go back to /sc:review" | green |
| S4 | implement: "Ideally, a later code change …" | green |
| S5 | implement: "counts only once the user accepts it" → "if the user accepts it" | green |
| S23 | implement: "can set it back" | green |
| S22 | implement: `--through` 예외 삭제 | red |
| S6 | reflect: (2)의 "is green or marked accepted by the user" 삭제 | green |
| S7 | reflect: 회송 대상 맞바꿈 | green |
| S8 | reflect: "says yes or does not answer" | green |
| S9 | reflect: "checked or its task is under way" | green |
| S10 | reflect `<never>`: "… unless the run is headless" | green |
| S11 | intent Run: "write nothing unless all three conditions hold" | green |
| S12 | intent Run: "once" → "/sc:review again until none remain" | green |
| S13 | intent Report: "(merge; push), after setting the plan `complete`" | green |
| S14 | review: "another round when there is time" | green |
| S15 | review: "Rounds stop after the second round, or …" | green |
| S16 | test: "…, unless every test passes" | green |
| S17 | test: "Critical or Important" → "Critical" | red |
| S18 | RULES_DOCS:58 되돌림 절 삭제 | green |
| S19 | gates: "on the user's yes to" → "after" | green |
| S20 | gates: "goes to /sc:reflect when it is large" | green |
| S21 | gates: "names the fix left unreviewed" 삭제 | green |
| S24 | README reflect 행: "it marks the plan `complete`, which you confirm afterwards" | green |
| S25 | `through_left_open`: `\|README` 삭제 | green |
| S26 | `through_left_open`: `phase` 삭제 | green |
| S27 | plan-close regex: `(?<!not\s)` 삭제 | green |
| S28 | plan-close regex: "close it …?" 갈래 삭제 | red |
| S29 | plan-close regex: `→ complete` 갈래 삭제 | red |

S16 도중 시간 초과로 한 번 끊겼다. 남은 `test.md`를 `git checkout HEAD --`로 되돌리고 S16부터 다시 돌렸다. 끝에 `git status`는 비어 있었다.

## 이 브랜치 밖

- `RULES_DOCS.md:88` "every gap /sc:reflect names is fixed … or accepted"는 `--through`의 끝과 긴장이 있다. 이전부터 있던 문장이고, intent Run이 더 구체적이다.
- "code"의 범위(06-verify 이 브랜치 밖)는 열려 있다. 발견 1의 수정이 이를 줄인다.
