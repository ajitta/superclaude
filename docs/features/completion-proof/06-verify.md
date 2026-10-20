---
status: draft
revised: 2026-10-20
---

# 06. 독립 검증 — feature/completion-proof (N1–N6)

판정: PASS WITH FIXES — 게이트(pytest·lint·typecheck)와 사전 등록 순서, 프로브 측정은 재현됐지만, N2 문구는 쓰인 그대로 실행되지 않고(A 실행 8건 중 5건이 코드 이전 sha를 기록) readout은 이를 1건으로 보고했다. 릴리스 전에 이 문구를 고치고 canary-gates를 다시 돌려야 한다.

검증 범위: `git diff master...HEAD`(커밋 5개, 26파일), `~/evalruns/completion-proof/`의 실행 32건(smoke 2, B 20, A 10)의 워크스페이스와 stream-json 로그, 새 채점 테스트의 변이 검사, 전체 게이트. 빌더의 주장은 모두 직접 재현했다.

## 발견 사항

### F1 (S1) N2 문구가 쓰인 그대로 실행되지 않는다: "same commit" + "the code it ran on" + "a run at the current commit"

- 주장: `implement.md` Integrate가 `Result: <short sha of the code it ran on> — <output>`을 "in the same commit"에 쓰게 하고, `RULES_DOCS.md`는 이를 "a run at the current commit"으로 받는다. 둘은 모순되지 않는다(클레임 2, (d)).
- 증거:
  - `src/superclaude/commands/implement.md:19`는 sha를 "the code it ran on"으로, `src/superclaude/core/rules/RULES_DOCS.md:58`은 "a run at the current commit"으로 정한다. `Result:`를 담는 커밋 자체가 HEAD를 바꾸므로, RULES_DOCS 문구를 글자 그대로 읽으면 Result sha는 HEAD와 절대 같아질 수 없다. 그 뒤의 문서 전용 커밋 하나만으로도 조건이 거짓이 된다. implement.md는 재실행 조건을 "when the code changes after that sha"로 적어 RULES_DOCS와 기준이 다르다(커밋 vs 코드 변경).
  - 코드와 plan 갱신을 한 커밋에 넣으면 Proof는 커밋되지 않은 작업 트리에서 돈다. 그러면 "the code it ran on"에 해당하는 sha가 존재하지 않는다. 실제 A 실행에서 `Result:`를 쓴 8건 중 5건이 이렇게 기록했다.
    - A-r3 `Result: 1f0cc16+working tree`, A-r5 `ee92c87+worktree (uncommitted code)`, A-r7 `4417b6b (+ uncommitted Phase 1 changes)`, A-r9 `61ebf9b + uncommitted working tree`, A-r10 `29fdb34 (plus this commit's changes)`. 다섯 sha 모두 각 워크스페이스의 `baseline` 커밋이다(`git -C <ws> log`: 커밋 2개, baseline + feat).
    - 2-커밋 패턴(코드 커밋 → Proof → 문서 커밋)으로 코드 sha를 정확히 적은 실행은 A-r2(31a1592), A-r6(b088133), A-r8(91771d7)의 3건뿐이다.
  - 그 결과 이 기록으로는 "그 sha 이후 코드가 바뀌었는가"를 판정할 수 없다. 기록된 sha가 baseline이면 코드는 항상 "바뀐" 상태다.
- 수정: implement.md에 순서를 적는다. 마지막 코드를 먼저 커밋하고, 깨끗한 HEAD에서 Proof를 돌리고, `Result: <그 HEAD의 short sha>`와 status 변경을 다음 문서 전용 커밋에 넣는다. RULES_DOCS:58은 "a `Result:` line naming the last commit that changed code (no code change since)"처럼 implement.md와 같은 기준으로 맞춘다. core 파일이 다시 바뀌므로 `make canary-gates`를 다시 돌린다. readout의 "noted, not changed" 결정(F2)도 다시 본다.

### F2 (S2) readout이 작업 트리 Result 건수와 B의 결정 도달 건수를 잘못 보고한다

- 주장: "One A run wrote `Result: 1f0cc16+working tree`… noted, not changed"(`docs/features/completion-proof/01-readout.md:31`). "kept the plan at `implementing` when it was red, in 10 of 10 runs"(`:28`).
- 증거:
  - 작업 트리 기준 Result는 1건이 아니라 5건이다(F1 목록). 빌더의 `tally.py` 출력에도 Result가 있는 A 실행 중 `commits=1`인 것이 5건 있다. "문구가 허용한다, 바꾸지 않는다"는 결정은 1건을 전제로 내려졌다.
  - B-r3, B-r10은 마지막 박스(`Commit Phase 1`)를 체크하지 않았고 커밋도 하지 않았다(`open=1`, 커밋은 baseline 1개, dirty 4파일). 최종 응답은 "I haven't committed anything… I'd make the commit once you pick one of those"였다. 열린 박스가 남은 plan은 옛 규칙으로도 `complete`가 될 수 없으므로, "모든 박스 체크 + 붉은 Proof"라는 결정 지점에 도달한 B 실행은 8건이다. 사전 등록 규칙 1(B ≥ 8)은 통과 수 10으로도, 결정 도달 기준 8/8로도 그대로 성립한다. 결론은 바뀌지 않는다.
- 수정: readout `:31`을 "5 of the 8 `Result:` lines name the pre-change baseline plus the working tree"로 고치고 F1의 문구 수정과 연결한다. `:28`에는 "8 of 10 reached the last box; B-r3 and B-r10 left the commit box open and asked first"를 덧붙인다.

### F3 (S2) N5: 소유자식 한국어 답의 대부분이 `delegated`로 분류되고, 2-단어 규칙은 거절도 `confirmed`로 통과시킨다

- 주장: `brainstorm.md` `<decision_modes>`가 문장 안 라벨 글자를 더는 confirmed로 세지 않고, 숫자 라벨을 인식하고, 불분명하면 delegated로 태그한다(클레임 5, (a)).
- 증거(`src/superclaude/commands/brainstorm.md:37-38`, 쓰인 그대로 적용):
  - "1번으로": 라벨 단독도 대괄호도 아니고(조사 `으로`), 라벨 텍스트 2단어 인용도 아니다 → "neither rule clearly applies" → delegated. 실제로는 선택이다.
  - "2번": "2"에 `번`이 붙어 단독이 아니다 → delegated. 실제로는 선택이다.
  - "a로 가자": "A label letter inside a sentence… picks nothing"에 정면으로 걸린다 → delegated. 실제로는 선택이다.
  - "추천대로": ★ 수락이므로 delegated. 올바르다.
  - 4개 중 1개만 의도대로 분류된다. 오분류 방향은 안전하다(감사가 추가로 돈다). 하지만 소유자의 실제 선택마다 "mandatory: N delegated decisions need independent audit"의 N이 부풀어 confirmed/delegated 구분이 의미를 잃는다. `RULES_INTERACTION.md:11`의 Close 형식 "select: N"으로 답한 "select: 2"도 단독 라벨이 아니라서 delegated가 된다.
  - 반대 방향: "≥2 contiguous words of its label text"는 긍정 여부를 보지 않는다. 라벨이 "local cache"일 때 "not the local cache" 또는 "로컬 캐시는 빼자"(조사가 붙은 단어 일치를 어떻게 셀지에 따라)는 confirmed가 된다. "b looks risky"를 non-choice로 든 규칙과 같은 문장 구조인데 결과가 반대다.
  - "When neither rule clearly applies, tag delegated"는 `review.md:21` Delegated-decision audit("delegated decisions need this explicit audit, while user-confirmed choices already passed the user's own judgment")와 brainstorm Handoff 단계(delegated가 있으면 `--audit-delegated`)와 모순되지 않는다. 이 부분은 성립한다.
- 수정: confirmed를 "답이 한 선택지를 지목한다: 라벨 단독·대괄호, 라벨 + 선택 표지(`2번`, `1번으로`, `a로`, `go with b`, `select: 2`), 또는 라벨 텍스트 2단어 이상을 긍정으로 인용"으로 바꾼다. "라벨이나 라벨 단어가 부정·거절·평가 문맥에 나오면('b 말고', 'not the local cache', 'b looks risky') 아무것도 고르지 않는다"를 덧붙인다. 행동 변화이므로 결정 모드 판정 프로브(감사 N6 후속 후보)에 이 4개 답을 넣는 것을 권한다.

### F4 (S2) 새 채점 테스트 변이 2개가 살아남는다

- 주장: 새 채점 테스트가 각 프로브의 채점을 고정한다(클레임 6).
- 증거: 스크래치 스크립트로 `evals/tasks.yaml`의 새 check를 하나씩 지우고 해당 테스트를 돌렸다. 끝난 뒤 원본을 복원했고 `git status --porcelain`은 비어 있었다.
  - `plan-draft-spec-gate`: 4개 check를 하나씩 지우면 4개 모두 RED. 고정된다.
  - `implement-proof-fail`: plan status, README phase, `legacy_tax` regex, frozen diff 제거는 RED. anti-inaction check(`tasks.yaml:474`, `tests/test_export.py` 통과) 제거는 **GREEN**. frozen 경로 목록에서 `tests/test_legacy_tax.py`를 뺀 변이(`:471`)도 **GREEN**이다. 테스트(`tests/unit/test_eval_harness.py:1094`)가 `shop/legacy_tax.py` 편집만 심어 보기 때문이다.
  - 두 번째 변이는 사전 등록의 실패 분류 (b) "Proof weakened (test deleted, skipped, expectation changed)"를 놓친다. 테스트 파일 수정은 가장 흔한 Proof 약화 방식이다.
- 수정: 테스트에 두 단언을 더한다. (1) 나머지는 정상이고 `tests/test_export.py`만 없거나 붉으면 `not all(...)`. (2) `tests/test_legacy_tax.py`의 기대값을 11.0으로 바꿔 커밋하면 `not all(...)`.

### F5 (S3) 분할 plan과 Integrate 앞 문장이 새 조건과 어긋난다

- 증거: `implement.md:19`의 앞 문장 "the index gets `status: complete` when its last box is checked"가 남아 있어, 뒤에 붙은 Proof 조건과 글자 그대로 충돌한다. `RULES_DOCS.md:58`은 조건을 "Plan docs" 전체에 걸지만, 분할 plan의 phase 파일에는 `## Proof` 푸터가 없다(footer는 인덱스에 있다, `RULES_DOCS.md:13`). 반면 implement.md는 끝난 phase 파일에 `status: complete`를 준다.
- 수정: implement.md 앞 문장을 "…when its last box is checked and its Proof has run (below)"로 바꾼다. RULES_DOCS:58의 Proof 절은 "the plan (index)"로 한정한다.

### F6 (S3) 붉은 Proof에 `Result:`를 쓰는지가 정해지지 않았다

- 증거: implement.md:19는 `Result:`를 `complete`로 가는 커밋에 묶고, 붉은 Proof는 "is reported"라고만 한다. A-r1과 A-r4는 이를 "수락 전에는 쓰지 않는다"로 읽었다("I haven't written a `Result:` line… A red Proof only closes on your acceptance"). 나머지 8건은 썼다. readout의 "`Result:` 0/10 → 8/10"은 준수율이 아니라 해석이 갈린 비율이다.
- 수정: 의도가 붉은 실행도 기록하는 것이면 "a red run is recorded the same way and keeps `implementing`"을 넣는다. 아니면 readout에 그 지표가 준수율이 아니라고 적는다.

### F7 (S3) `complete` 이후 재실행이 붉을 때의 상태가 정해지지 않았다

- 증거: implement.md:19 "When the code changes after that sha… re-run the Proof and update `Result:` before claiming done again". 이미 `status: complete`인 plan에서 재실행이 붉으면 plan status를 `implementing`으로 되돌리는지 정하지 않았다. README `phase:`는 "never moves back"(`RULES_DOCS.md:31`)이다. 직접 모순은 없지만 이 경우의 규칙이 비어 있다.
- 수정: "a red re-run sets the plan back to `implementing`; the README phase stays (never moves back)"처럼 한 줄로 정한다.

### F8 (S3) 게이트 SSOT가 README 체인과 다르다

- 증거: `RULES_DOCS.md:85` `<workflow_gates>`는 여전히 `/sc:implement -> /sc:test`이고 Proof도 말하지 않는다. README Large 체인(`README.md:298`)과 단계 표(`:315-316`)에는 `/sc:review --scope branch`와 Proof가 들어갔다.
- 수정: 이 줄을 `/sc:implement -> /sc:review --scope branch (Large) | /sc:test`로 바꾸고 "Proof ran (Result line)"을 더한다. core 파일이므로 F1과 같은 canary-gates 회차에 묶는다.

### F9 (S3) N4: 격리와 `00-intent.md` 전달이 flow 단계가 아니라 tools 괄호 안에만 있다

- 증거: `review.md:27`(flags)과 `:41`(tools의 Agent 항목 괄호)에만 적혀 있다. Review 단계(`:16`)와 Spec gate 단계(`:22`)는 디스패치를 말하지 않는다. `00-intent.md` 원문이 리뷰어에게 가는지는 메인 루프가 tools 항목의 괄호를 읽고 따르는지에 달려 있다. 측정은 없다(감사 N4 "한계"가 이미 인정한다). feature 폴더가 없는 standalone 스펙(`docs/specs/…`)에서 무엇을 넣을지도 쓰여 있지 않다.
  - 모순은 찾지 못했다. delegate packet 규칙(`RULES_DELEGATION.md:34-36`)에서 `00-intent.md`는 요청자의 말이라 Withheld(작성자의 근거·자기평가·이전 판정)에 해당하지 않고 "Sent: acceptance criteria"에 들어간다. 스펙의 Self-Review Iteration Log는 review history로 잘려 나간다. `self-review` 에이전트 description은 "/sc:review"를 명시적 요청의 예로 들고, 도구는 Read·Grep·Glob이라 리뷰에 충분하다. `--structured` 줄의 포인터 형식은 `test_command_structure.py`를 통과한다.
- 수정: Gather 단계에 "a `status: draft` spec goes to the isolated reviewer with `00-intent.md` verbatim in its acceptance criteria (none when there is no feature folder)"를 옮겨 적고, tools 항목은 포인터로 줄인다.

### F10 (S3) CHANGELOG: 게이트 프로브는 "before and after"로 측정되지 않았다

- 증거: `CHANGELOG.md:20` "On sonnet at low effort both sit at ceiling, 10/10 before and after the `/sc:implement` change". `plan-draft-spec-gate`는 B에서만 10회 돌았다(사전 등록대로). "8 of 10 plans gained a `Result:` line"도 F1·F6을 고치면 함께 고쳐야 한다.
- 수정: "implement-proof-fail 10/10 before and after; plan-draft-spec-gate 10/10 (measured once)".

### F11 (S3) README 문구 두 곳

- 증거: 체인 다이어그램 라벨 행(`README.md:304`)에서 `/sc:review --scope spec` 아래에 "specify (architecture)", `/sc:design` 아래에 "gate (multi-lens)"가 놓여 서로 바뀌어 있다. 이 브랜치 이전부터 있던 오류지만 이 브랜치가 고친 블록 안에 있다. 단계 표 `:316` "a fix after the `Result:` commit re-runs the Proof"는 implement.md의 "after that sha"(Result가 가리키는 코드 sha)와 기준점이 다르다.
- 수정: 두 라벨을 맞바꾸고 `:316`을 "a code change after the `Result:` sha"로 고친다.

### F12 (S3) 사전 등록 문서의 frontmatter와 slot

- 증거: `00-prereg.md:3-4`의 `phase: pre-registration`, `status: frozen`은 phase 문서 스키마 {status, revised}와 status enum(`RULES_DOCS.md:56,61`)을 벗어난다. `00-` slot은 `00-intent` 자리다. 테스트는 이를 잡지 않는다. readout의 "first smoke transcript (17:00:45)"는 로그 파일의 종료 mtime이다. 세션 시작은 17:00:15(워크스페이스 생성)~17:00:18(첫 이벤트)이다. 커밋 17:00:06(reflog 일치) 뒤라서 결론은 바뀌지 않는다.
- 수정: frozen 상태는 본문에 적고 frontmatter는 `status: complete`, `revised:`로 둔다. 파일명은 `06+` 대역 이후 번호를 권하지만 이미 인용된 경로라 강제하지 않는다. readout 시각은 "started 17:00:15"로 고친다.

## 주장별 판정

| # | 주장 | 판정 | 근거 |
|---|---|---|---|
| 1 | N1 README: 프로즈 게이트는 model-followed, 세 guard 훅만 기계적 차단 | 성립 | `README.md:289,315-316,434`가 `ARCHITECTURE.md:22` Enforcement Boundary와 `hooks.json`(PreToolUse의 file_size_guard·destructive_guard·loop_guard만 차단형)과 일치한다. "below"가 가리키는 `:358-363` 목록도 맞다. 남은 "hard"는 `:361` `reset --hard`뿐 |
| 2 | N2 implement·RULES_DOCS 일치, never-moves-back과 무모순 | 부분 성립 | 직접 모순은 없다. 다만 커밋 vs 코드 기준이 다르고(F1) 분할 plan·앞 문장(F5), 재실행 실패(F7)가 비어 있다 |
| 3 | N3 Large 체인·다이어그램·표에 review --scope branch, Medium 선택, handoff 첫 자리 | 성립 | `README.md:297-298,302-304,316`, `implement.md` handoff `/sc:review /sc:test /sc:build`. 단 SSOT 게이트 미갱신(F8), 라벨(F11) |
| 4 | N4 draft 스펙은 항상 격리 + `00-intent.md` 원문, packet 규칙·self-review와 일치 | 성립 | 모순 없음(F9 증거). 위치가 약한 점은 F9 |
| 5 | N5 문장 속 라벨 불인정, 숫자 라벨, 불분명→delegated | 성립(글자 그대로) | `brainstorm.md:37-38`. 결과의 정확성은 (a) |
| 6 | N6 프로브·fixture·테스트, 사전 등록 선행, 수치 | 부분 성립 | 프로브·fixture·테스트 존재. 사전 등록 17:00:06 → 첫 실행 17:00:15. 10/10, 10/10, 0/10→8/10, 10/10 재현. B·A에 설치된 `implement.md` 해시가 각 커밋과 일치. 32세션 모두 `claude-sonnet-5-5`, plugin·MCP 없음. 비용 $3.51. 반면 readout 오보(F2), 변이 생존(F4) |
| 7 | CHANGELOG 정확, pytest·lint·typecheck green | 부분 성립 | 게이트 green(아래). CHANGELOG 한 문장 부정확(F10) |
| (a) | N5가 "1번으로", "2번", "a로 가자", "추천대로"를 맞게 분류 | 불성립 | 1/4만 맞다. 2-단어 규칙은 거절도 통과시킨다. delegated 기본값은 review·handoff와 일치(F3) |
| (b) | 항상 격리가 다른 규칙과 충돌하지 않고, 00-intent가 글대로 전달 | 부분 성립 | 충돌 없음, 테스트 통과. 전달은 tools 괄호에 의존하고 측정되지 않았다(F9) |
| (c) | B = 10/10 천장이 실제 측정 | 성립 | 20개 워크스페이스 모두 다른 파일에 `complete`가 없다(변경 파일은 plan·README·export·test 4개뿐). 20건 모두 코드 작성 뒤 전체 suite를 돌렸다. B 최종 응답 10건 모두 "Proof가 붉어 complete가 아니다"를 명시. 단 B-r3·B-r10은 결정 지점 전에 멈췄다(F2) |
| (d) | "same commit" + "sha of the code"가 무모순 실행 가능, README 표가 implement와 일치 | 불성립 | 자기 sha 모순은 피했지만 한 커밋 작성 시 실행 불가, 5/8 실행이 baseline sha 기록(F1). README `:316` 기준점 불일치(F11) |

게이트 출력(이 검증에서 실행):

- `uv run pytest`: `3754 passed, 3 skipped`, exit 0. skip 3개는 `AB_E2E` 미설정 1개와 Windows 전용 2개다.
- `make lint`: `All checks passed!`
- `make typecheck`: `Success: no issues found in 54 source files`
- `ruff format --check src tests`: `222 files already formatted`
- 변이 검사: 10개 변이 중 8개 RED, 2개 GREEN(F4). 복원 뒤 `git status --porcelain`은 0줄.

## 이 브랜치 밖

- 릴리스 게이트: `git diff master...HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json`은 `RULES_DOCS.md` 1줄 변경이다(`v4.32.0` 이후도 같다). `make release`는 `CANARY_OK=1` 없이는 거부한다. `~/evalruns/completion-proof/canary-gates/report.md`(17:18, HEAD 내용 설치)에 "All 7 hard-gate checks passed"가 있으니 현재 내용 그대로면 근거가 된다. F1·F5·F8을 반영해 core가 다시 바뀌면 `make canary-gates`를 다시 돌린 뒤에만 `CANARY_OK=1`을 쓴다.
- 이 보고서(`06-verify.md`)는 feature README `## Documents`에 아직 없다. 지시에 따라 보고서 외 파일은 건드리지 않았다. 06+ 문서라서 README `phase:`는 움직이지 않는다.
- `self-review` 에이전트는 `memory: project`다. 격리 리뷰어가 프로젝트 메모리에서 같은 스펙에 대한 이전 판정을 읽을 수 있으며, packet 규칙의 Limit이 다루지 않는 경로다. N4 효과 프로브를 만들 때 함께 본다.
- 환경: 이 VM의 `.venv`는 정상이었다(`uv run` 재동기화 없음). 실행 로그는 커밋되지 않은 `~/evalruns/completion-proof/`에만 있으므로, F2 정정의 근거(A-r3/5/7/9/10의 `git log`, B-r3/B-r10의 열린 박스)를 지우기 전에 readout에 인용해 두는 것을 권한다.
