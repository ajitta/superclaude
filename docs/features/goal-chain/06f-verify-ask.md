---
status: complete
revised: 2026-10-20
---

# 독립 검증: `/sc:intent --through --ask` (`v4.33.2..HEAD`)

**판정: PASS WITH FIXES** — Critical 없음. 게이트는 녹색이고, 헤드리스 대체 경로는 이번 실행에서도 06e대로 동작했다(헤드리스 1회, 3.7분: 도구가 없다고 적고 plain `--through`로 끝까지 진행). 다만 06e와 CHANGELOG가 근거로 드는 "25회 `--through` 실행"은 저장소의 기록과 맞지 않는다. 154·8 같은 수치는 저장소에서 확인할 수 없다. Checkpoint의 선별 기준 "which behavior a case gets"는 06e가 직접 "how it is built"로 분류한 종류까지 받아들이고, run 24에서 실제로 그렇게 됐다.

## 재현한 것

- 환경: 이 워크트리에서 `uv venv && uv pip install -e ".[dev]"`, `superclaude.__file__`이 워크트리 `src/`임을 확인.
- `uv run pytest`: `3770 passed, 3 skipped in 141.06s`, exit 0. `make lint`: `All checks passed!`. `make typecheck`: `Success: no issues found in 54 source files`. `ruff format --check src tests`: `222 files already formatted`.
- `uv run python evals/changed_command_probes.py v4.33.2` → `--task intent-through-branch` 하나, exit 0. 이 프로브의 프롬프트는 `/sc:intent --through`이고 `--ask`가 없다(`evals/tasks.yaml:519`). 그래서 릴리스 게이트는 새 문장을 한 번도 실행하지 않고 통과한다(발견 7).
- AskUserQuestion 제한(공식 문서): Agent SDK "Handle approvals and user input"의 Limitations에 "each `AskUserQuestion` call supports 1-4 questions with 2-4 options each", 질문 형식 표에 `header` "max 12 characters", 그리고 "not currently available in subagents"라고 적혀 있다(https://code.claude.com/docs/en/agent-sdk/user-input). Tools reference는 "Questions stay open until you answer them"이라고 하고, `askUserQuestionTimeout`을 켜면 창이 저절로 닫히며 "tells Claude you may be away from your keyboard, so Claude proceeds on its own judgment"라고 설명한다(https://code.claude.com/docs/en/tools-reference). "at most four"는 질문 수 상한과 정확히 같다. 옵션 수 상한(2–4)은 명령에 없다(발견 5).
- 헤드리스 실행 1회: `evals/fixtures/intent-through/` 복사본, 이 워크트리 venv로 project 설치, 자격 증명만 든 `CLAUDE_CONFIG_DIR`, `claude -p --model sonnet --permission-mode auto --setting-sources project,local`, `ENABLE_CLAUDEAI_MCP_SERVERS=false`, 프롬프트는 `/sc:intent --through --ask` + 프로브의 다섯 줄. Claude Code 2.1.304, exit 0, 224초.
  - init 이벤트의 도구 목록(25개)에 `AskUserQuestion`이 없다. 헤드리스에서 "no way to ask"는 도구가 없다는 것으로 드러난다. AskUserQuestion 호출 0회.
  - brainstorm 직후: "AskUserQuestion isn't available in this session, so I can't ask at the Checkpoint. I'm continuing as plain `--through`, and every decision stays `delegated` for the audit." 그리고 바로 `/sc:review --scope spec --audit-delegated`를 호출했다.
  - 작업공간에서 직접 확인: `feature/todo-due-dates`에 커밋 9개, main과 로컬 원격은 baseline(`0e0aa19`), `todos.json` 변경 없음, 작업 트리 깨끗함, plan의 `Result: d8f0095 — 17 passed`, 브랜치에서 `pytest` 17 passed, `todo.py overdue` exit 0. 01-discovery의 Resolved Decisions 6행이 모두 `delegated`. Report는 "none were confirmed by you"라고 적었다.
  - 참고로 D4("Where is the due date shown?")는 ★이 "`list` 줄에 날짜 붙이기"였지만 감사와 스펙 리뷰를 거쳐 "`list` unchanged"로 바뀌었다. 06e run 23의 사용자는 같은 질문에 "list에도 표시"를 골랐다. 사용자가 보는 결과에 관한 결정을 모델끼리 비교해 정하면 사용자의 답과 갈릴 수 있다는 06e의 동기와 맞는 관찰이다(n=1).

## 발견

### 1. [Important] "25회의 `--through` 실행"은 기록과 맞지 않고, 154·8 등은 저장소에서 확인할 수 없다

- 근거: 06e:10 "Across 25 earlier `--through` runs, all 154 discovery decisions were `delegated`", CHANGELOG `[Unreleased]` 같은 문장.
- 저장소에 번호가 붙은 실행은 1–22번이다(06-run-record.md:36-52, 06b:14-21, 06d:10). 이 중 1–10번은 손으로 쓴 `/goal`·plain 프롬프트이고 `--through`가 아니다(06-run-record.md:27-31, 38-47). `--through` 실행은 11–22번 12회와 번호 없는 라이브 프로브·리뷰 실행(06a:8 1회, 06b:42 1회, 06c:164 1회, 06d:45 1회)을 합쳐 최대 16회다. 06e는 새 실행에 23–26번을 붙였다. 앞선 실행이 25회라면 번호는 26부터여야 한다. 22 + 번호 없는 3회 = 25로 맞췄다면 그 25회에는 `--through`가 아닌 10회가 들어 있다.
- 확인 가능한 것: 모든 결정이 delegated였다는 점(06-run-record.md:59는 1–15번, `--through`는 정의상 그렇다). run 18의 감사 불일치 3/6(06b:18). run 16과 run 22가 실행 뒤 두 가지 해석의 확인을 요청한 사실(06b:16, 06d:16).
- 확인 불가: 총 154개, 불일치 8개, 그중 6개가 다모듈 두 실행에 있다는 점(run 19의 불일치 수는 06b:19에 없다), 나머지 2개의 위치, "2–4 per run"의 첫 번째 종류 결정 수, 불일치와 run 16/22의 확인 요청이 "what the user gets or sees" 종류였다는 분류. 기록은 오히려 "In the audits read (runs 1, 2 and 4), the independent agent picked the recorded ★ option for every audited question"(06-run-record.md:59)이라고 한다. 감사를 전부 읽지는 않았다는 뜻이다.
- CHANGELOG는 더 강하게 말한다: "the few the independent audit disagreed with … were all of this kind". 06e:15는 "almost all of the first kind"다.
- 수정: 06e:10과 CHANGELOG에 실행 집합을 밝힌다(예: "25 chain runs: runs 1–22 and three probe runs; 10 of them hand-written prompts"). 06e에 실행별 결정 수와 불일치 수의 작은 표를 붙이거나, 트랜스크립트에서 다시 센 수치라고 출처를 적는다. CHANGELOG의 "all of this kind"는 "almost all"로 낮춘다. 06e의 새 실행 번호는 실행 집합과 맞춘다.

### 2. [Important] 선별 기준이 06e가 제외한 종류를 받아들인다. 네 개를 넘을 때의 순위도 없다

- 근거: intent.md:21 "pick the ones that change what the user gets or sees (what counts, what is shown, where output goes, which behavior a case gets), not how it is built". 06e:13은 "bad-input handling, tag normalization"을 "How it is built"로 분류한다. 그런데 run 24의 양식은 네 칸 중 한 칸을 대소문자 처리(태그 정규화)에 썼고(06e:32 "case"), 06e:42는 그 때문에 첫 번째 종류의 질문(필터된 내보내기에 완료 항목이 나오는가)이 delegated로 남았다고 적는다. 잘못된 날짜 처리도 "which behavior a case gets"에 들어간다(run 23은 이를 묻지 않았다. 모델의 판단이 기준보다 나았던 셈이다).
- 네 실행의 표를 보면 run 23의 네 질문은 모두 사용자가 보는 결과에 관한 것이었다. run 24는 네 개 중 셋이 그랬고 하나는 경계 사례였다. 기준은 대체로 지켜졌지만, 경계에서 막아 주는 것은 문장이 아니라 모델의 판단이다. gotcha `checkpoint-creep`(intent.md:83)은 "storage format, parsing"만 예로 들어서 이 경계를 다루지 않는다.
- 수정: 괄호의 "which behavior a case gets"를 "which items a command includes or leaves out in a case the intent names"로 좁힌다. 한 문장을 더한다: "input validation, normalization and error wording are build details". 네 개를 넘을 때의 순위를 정한다: "more than four → first the ones the Done when or Proposed outcome line turns on, then what output holds and where it goes". 06e:13과 이 문장이 같은 분류를 쓰게 한다.

### 3. [Minor] "D2 추천" 같은 답이 confirmed인지 두 명령이 다르게 말한다

- 근거: brainstorm.md:37-38은 confirmed를 "the reply points at one option: its label … OR ≥2 contiguous words of its label text"로 정하고, "When neither rule clearly applies, tag delegated"라고 한다. "추천"(recommended)은 라벨도 라벨 단어도 아니다. 반면 intent.md:21은 "answers in it (numbers, labels or their own words) are applied the same way"라고 해서 confirmed가 된다. run 24는 "D2 추천"과 "D5 추천"을 "confirmed on ★"로 기록했다(06e:32). AskUserQuestion에서 고른 답은 tool result가 옵션의 `label`을 돌려주므로(위 SDK 문서의 Response format) 두 규칙 모두에서 confirmed다. 충돌은 채팅 답과 "Other" 자유 입력에서만 생긴다. brainstorm 쪽에는 "Other" 답에 대한 규칙이 아예 없다.
- `--audit-delegated`는 `mode`가 delegated인 행만 다시 평가한다(review.md:21). 그래서 이 판단이 감사 대상을 바꾼다.
- 수정: Checkpoint에 한 구절을 넣는다: "an answer to one question, including 'recommended' or an Other text, makes that row confirmed even where the /sc:brainstorm Decision-mode tag heuristic would say delegated". 반대 결론을 원한다면 06e run 24의 기록을 고친다.

### 4. [Minor] Checkpoint는 9번 단계지만 8번 단계 한가운데서 실행된다

- 근거: intent.md:20-21. `<flow>`의 번호 목록은 "readers must execute in this order"인 순서 절차다(`.claude/rules/xml-prose-format.md` Short-line list). Run 단계 안의 "(with --ask, except once at the Checkpoint step right after /sc:brainstorm)"와 Checkpoint의 "inside the Run step, after brainstorm and before the spec review … Commit, then continue the Run step"이 위치를 알려 주고, run 23·24는 제대로 실행했다(n=2, sonnet). 그러나 순서대로 읽는 모델은 Run 단계의 명령 체인을 끝까지 돈 뒤 9번에 이를 수 있다.
- 수정: Run 단계의 체인 자체에 위치를 넣는다: "/sc:brainstorm → (with --ask) the Checkpoint step → /sc:review --scope spec --audit-delegated → …". 단계 포인터는 라벨로 쓰므로 `test_command_structure.py`의 검사와도 맞는다.

### 5. [Minor] 양식의 한계와 답이 오지 않는 경우가 정해져 있지 않다

- 옵션 수: AskUserQuestion은 질문마다 2–4개 옵션만 받는다. RULES_INTERACTION.md:9의 텍스트 메뉴는 최대 7개를 허용하고, brainstorm의 Resolved Decisions에는 옵션이 하나뿐이거나 기록되지 않은 행도 있을 수 있다(review.md:21도 "where the spec records none"을 따로 다룬다).
- 답이 없는 경우: `askUserQuestionTimeout`이 켜져 있으면 양식이 저절로 닫히면서 모델에게 사용자가 자리를 비웠을 수 있다고 알린다. 이것은 "An answer"도 "A declined form"도 아니다. README가 권하는 `/goal` 래퍼에서는 양식을 닫은 뒤 모델이 기다리려고 턴을 끝내면 Stop 훅 평가자가 실행을 계속시킬 수 있다. "wait for the user's reply"와 부딪친다.
- 수정: Checkpoint에 "2–4 options each, ★ first (the form adds Other); a decision with fewer than two recorded options stays delegated; a question the form closes without an answer stays delegated and the run continues"를 넣는다. README의 `/goal` 문단에는 `--ask`와 함께 쓰면 닫힌 양식을 기다리지 않을 수 있다고 적는다.

### 6. [Minor] 종속 질문을 delegated로 남기면 ★이 답과 어긋날 수 있다

- 근거: intent.md:21 "when one answer would change another's options, ask the first and leave the dependent one delegated". 종속 행의 ★은 답이 나오기 전에 골라진 것이다. 예를 들어 사용자가 "CSV를 stdout으로"를 고르면, 종속 행 "파일 이름: todos.csv ★"는 낡은 선택지를 가진 채 감사로 넘어간다. 감사는 기록된 옵션 그대로 질문을 받는다(review.md:21).
- 수정: "… leave the dependent one delegated, with its options and ★ re-picked under the answer".

### 7. [Minor] `--ask`를 실행하는 프로브가 없다. 릴리스 게이트는 새 문장을 거치지 않는다

- 근거: 06e:43 "No canary probe: … the headless fallback is the plain `--through` path the `intent-through-branch` probe already covers". 대체 경로는 plain `--through`와 같지 않다. 모델은 `--ask`를 읽고, 도구가 없음을 알아채고, "wait for the user's reply" 규칙을 적용하지 말아야 한다. 헤드리스에서 모델이 brainstorm 뒤 답을 기다리며 턴을 끝내면 실행은 거기서 멈춘다. 지금의 게이트(`make canary-commands` → `intent-through-branch`)는 이 회귀를 잡지 못한다. 이번 헤드리스 실행과 06e의 run 25·26에서는 문제가 없었다(n=3, sonnet).
- 수정: canary-only 프로브 하나를 더한다. `intent-through-branch`의 셋업과 검사를 그대로 쓰고 프롬프트에 `--ask`만 붙인다. 검사를 하나 더한다: 브랜치의 `01-discovery.md`에 `confirmed` 행이 없다. 평가자가 확인할 수 있는 것은 대체 경로뿐이고, Checkpoint 자체는 tmux 실행으로만 확인된다는 점을 06e에 남긴다.

### 8. [Minor] 모든 행이 confirmed가 되어도 Run 단계는 `--audit-delegated`를 붙인다

- 근거: brainstorm.md:20 "With delegated decisions, add --audit-delegated". intent.md:20은 이 플래그를 항상 붙인다. 결정이 네 개 이하이고 모두 사용자에게 물어서 답을 받으면 감사할 행이 0개다. review.md:21은 delegated 행만 평가하므로 해가 되지는 않지만, 빈 감사를 할지 건너뛸지는 모델이 추측한다. 감사를 다시 돌릴 이유는 없다. confirmed 행은 사용자의 판단을 이미 거쳤다(review.md:21 마지막 문장).
- 수정: Checkpoint에 "no delegated row left → call the spec review without --audit-delegated"를 넣는다.

## 문서 일치(D)

- README.md:347, docs/index.html:333, commands/README.md:40, intent.md 예시 행은 명령과 같은 내용을 말한다: 발견 직후 한 번, 최대 네 질문, ★ 먼저, 답은 `confirmed`, 빌드 세부는 delegated. README의 "In a headless run … it behaves like plain `--through`"는 이번 실행과 06e의 run 25·26으로 확인된다. 차이는 Report가 "체크포인트가 묻지 못했다"는 한 줄을 더한다는 것뿐이다. 과장된 곳은 CHANGELOG의 "all of this kind"(발견 1) 하나다.

## 이 브랜치 밖의 메모

- RULES_DOCS.md:79의 `/sc:brainstorm -> /sc:design: User approves discovery spec before designing`에는 `--through` 예외가 없다(intent 게이트 :78에는 있다). `--through`부터 있던 공백이고, `--ask` 사용자도 질문만 볼 뿐 스펙은 보지 않는다.
- brainstorm.md의 decision_modes에는 `--through` 밖에서도 "Other" 자유 입력 답에 대한 규칙이 없다.
- 06e의 대화형 실행 두 번(23, 24)은 tmux 세션이 필요해서 이번에 재현하지 않았다. 판단 근거는 06e의 표뿐이다.
- 스크래치: `verify-scratch3/`(격리 config 디렉터리는 삭제함).
