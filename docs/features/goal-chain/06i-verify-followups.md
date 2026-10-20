---
status: complete
revised: 2026-10-20
---

# 4.34.0 후속(06h)의 독립 검증

판정: PASS WITH FIXES

대상: `master..HEAD`의 커밋 세 개(`ee988ef9`, `391ef88c`, `932270d5`), 기록은 [06h](./06h-other-answers-reviewer-memory.md). 소유자 결정은 [remaining-work-ajitta-2026-10-20](../../plans/remaining-work-ajitta-2026-10-20.md) §0의 ★(a) 두 개다. 빌더의 서술은 믿지 않고, 아래 결과는 모두 이 검증에서 직접 실행하거나 읽은 것이다. 실제 `~/.claude`는 건드리지 않았다. 설치 검사는 scratch `HOME`과 `CLAUDE_CONFIG_DIR`, scratch git 저장소에서만 했다.

## 게이트

- `uv run pytest`(전체): `3775 passed, 3 skipped in 114.60s`, exit 0
- `make lint`: `All checks passed!`, exit 0
- `make typecheck`: `Success: no issues found in 54 source files`, exit 0
- `ruff format --check src tests`: `222 files already formatted`, exit 0
- Canary: `git diff master HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json`는 0줄이므로 `make canary-gates`는 필요 없다. 바뀐 command 본문은 `src/superclaude/commands/brainstorm.md`와 `src/superclaude/commands/intent.md` 두 개다. 둘 다 `make canary-commands`에 걸리고, `changed_command_probes.probes_for({'brainstorm','intent'})`는 `['intent-through-branch', 'intent-through-ask-headless']`를 고른다. 두 probe 모두 headless라 form에 답할 수 없다. 그래서 이 게이트는 회귀만 보고, Other 답 규칙 자체는 재지 못한다(06h Limits와 같은 결론). `make canary-*`, `claude -p`, release, push는 실행하지 않았다.

## 주장 검증

| # | 주장 | 판정 | 근거 |
|---|---|---|---|
| 1 | `brainstorm.md` `<decision_modes>`가 0-1(a)를 구현하고 기존 규칙·F3·README와 모순되지 않는다 | 부분 | 0-1(a)의 두 문장(자기 말로 하나를 고르면 confirmed, 질문·망설임·조건이면 아무것도 고르지 않음)은 `brainstorm.md:37`에 그대로 있다. 라벨/조사 규칙, 연속 2단어 규칙, 거절·평가 문맥 규칙은 손대지 않았다. 다만 새 문장이 ★에 맡기는 답("추천대로")을 빼지 않는다. F3는 이 답을 delegated로 판정했다(`completion-proof/06-verify.md:40`). 긍정 평가("b looks good")와의 우선순위도 열려 있다(발견 1, 2) |
| 2 | intent Checkpoint 예외를 정리하고 "★를 그 질문에 대한 답으로 지목" 한 경우만 남겼다. 그 경우가 아직 필요하다 | 부분 | `intent.md:21`. "an Other text … included" 삭제는 결정 그대로다. 이제 Other 텍스트는 brainstorm 규칙으로 판정되고, 망설이는 Other는 delegated가 된다. form에서 ★를 고르면 tool result가 옵션 label을 돌려주므로 라벨 규칙으로 confirmed다(06f §3의 SDK 근거). 남긴 예외는 06f §3과 06g row 3, 06e run 24 기록("D2 추천" → confirmed on ★)과 맞는다. "a plain go-ahead leaves those rows delegated"와도 충돌하지 않는다. 앞쪽은 질문 하나에 대한 답이고 뒤쪽은 전체에 대한 진행 승인이라 구분된다. 그러나 "which those rules leave delegated"는 brainstorm 본문이 지금 명시하지 않는 내용을 단정한다(발견 1). 문장 앞부분도 무조건 confirmed로 읽힐 수 있다(발견 3). `tests/unit/test_command_structure.py`: `916 passed`. 단계 포인터 "the /sc:brainstorm Decision-mode tag step"은 `brainstorm.md:19`의 7단계와 맞는다 |
| 3 | 두 리뷰어에서 `memory: project`와 `<memory_guide>`를 지웠고, 규칙·README가 예외를 적었으며, `_rewrite_agent_memory_scope`는 바꿀 필요가 없다 | 성립 | diff 확인. `install_components.py:88`은 `memory: project\n`의 첫 줄만 치환하므로 필드가 없으면 그대로 둔다. `agent-authoring.md:20,29,115,122,200,245`, `agents/README.md:59`. 두 본문에 `memory`나 `lesson` 문자열이 남아 있지 않다(grep 0건) |
| 4 | CLI의 다른 곳도 모든 에이전트에 `memory:`가 있다고 가정하지 않는다 | 성립 | 읽은 곳: `_other_memory_values`·`_declared_memory`(`install_components.py:122,220`)는 `match`가 없으면 건너뛴다. `verify_drift.py:63-80`은 원문이 같으면 OK다. `_is_shipped_agent`(`install_paths.py:901`)는 retired 에이전트에만 쓴다. uninstall의 빈 store 정리(`install_inventory.py:484-505`)는 디렉터리를 기준으로 한다. 재현(scratch 저장소): master로 local 설치(5개 모두 `memory: local`) → 브랜치로 `install --scope project` → `❌ … installed for another scope (memory: local)`. 브랜치로 `update --scope local` → 3개만 `memory: local`. 다시 `install --scope project --force` → 같은 ❌. 리뷰어 2개에 필드가 없어도 나머지 3개가 scope를 드러내므로 충돌 감지는 유지된다. `uninstall --scope local --yes` → `9 removed`, 빈 `.claude/` 제거. C-06/C-10/C-12 시나리오 테스트는 전체 suite에서 통과했다 |
| 5 | 새 테스트 | 성립(빈틈 하나) | 변이 검사 결과는 아래 표에 있다. 새 테스트는 모두 해당 수정을 되돌리면 RED가 된다. `-local` 경로 절반만 테스트가 없다(발견 4) |
| 6 | user scope 업그레이드: master 설치 → 브랜치 `update` | 성립 | scratch `CLAUDE_CONFIG_DIR`에 master 설치 → 5개 모두 `memory: user`. `agent-memory/self-review/MEMORY.md`에 `learned`를 심음. 브랜치 `doctor`: `4 installed file(s) differ … (4 drifted)`. `update --scope user`: `64 installed, 0 skipped, 0 failed`. 그 뒤 `memory:` 줄은 business-panel-experts, repo-index, deep-researcher에만 남고, `MEMORY.md`는 `learned` 그대로다. `verify-drift`: `✅ No drift detected`, exit 0. `doctor`에 ❌/⚠/memory 줄 없음 |
| 7 | 06h·CHANGELOG·plan 문서가 정확하고, Claude Code 문서 사실이 맞다 | 성립(사소한 점 둘) | 2026-10-21에 live 문서 https://code.claude.com/docs/en/sub-agents "Enable persistent memory"를 확인했다. project: "shareable via version control". local: "shouldn't be checked into version control". 이 절에는 `.gitignore` 언급이 없다. "Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files". frontmatter 표에서 `memory`는 Required "No"다. 세 사실 모두 06h·`agent-authoring.md`와 맞는다. plan 문서는 0-1·0-2를 `[x]`로 바꿨고, §4a 결정 모드 probe는 보류를 유지한 채 Other 사례 두 개를 목록에 더했다(결정 그대로). 사소한 점: 06h의 "Other repos add it to `.gitignore` by hand"는 출처가 없다. 06h는 `status: draft`다(canary-commands 전이라 맞는 상태) |

### 변이 검사

| 되돌린 것 | RED가 된 테스트 | 복원 확인 |
|---|---|---|
| `git checkout master -- src/superclaude/agents/self-review.md` | `test_has_required_field[self-review-memory]`, `test_has_memory_guide[self-review]`, `test_install_leaves_independent_reviewers_without_memory` (3 failed, 265 passed) | `git checkout HEAD -- …` 뒤 `git diff --stat`, `git status --porcelain` 0줄 |
| `verifier.md` 같은 방식 | `[verifier-memory]`, `[verifier]`, 같은 install 테스트 (3 failed) | 0줄 |
| `evals/tasks.yaml`에서 새 cmd_ok 두 곳 삭제 | `test_intent_through_probe_grades_each_end_state` 15개 상태 전부 RED(목록 길이 10 → 9). 남은 9개 검사로 `agent memory left` 상태를 직접 채점하면 `[True]*9`. 메모리 파일이 아무 검사에도 걸리지 않는다 | 0줄. 복원 뒤 같은 상태는 `[T,T,T,T,T,T,T,T,False,T]`, `correct`는 `[True]*10` |
| 새 cmd_ok에서 `'.claude/agent-memory-local'` 제거 | 없음: `17 passed` (발견 4) | 0줄 |
| `brainstorm.md`·`intent.md`를 master로 | 없음: `test_command_structure.py`+`test_cross_references.py` `1064 passed`. 문구 변경이라 예상된 결과다(06h Limits) | 0줄 |

## 발견

### 1. [Important] 새 own-words 규칙이 ★에 맡기는 답을 confirmed로 읽힐 여지를 연다. intent는 그 답이 brainstorm에서 delegated라고 단정한다

- 근거: `brainstorm.md:37`은 "A reply in the user's own words that commits to one concrete choice … is confirmed too"라고 하고, ★ 수락을 빼는 말이 없다. `brainstorm.md:38`의 delegated 목록에는 "silent accept of ★"만 있다. "추천대로"나 "D2 추천"은 침묵이 아니고, 하나의 구체적인 선택(★)을 가리킨다. 그래서 이 문구 그대로 적용하면 confirmed로 읽을 수 있다. 그런데 F3는 "추천대로"를 "★ 수락이므로 delegated. 올바르다"로 판정했다(`completion-proof/06-verify.md:40`). `intent.md:21`도 같은 답을 "which those rules leave delegated"라고 단정하고, 06h도 "a blanket 'as recommended' must stay delegated"라고 쓴다. 이 단정은 brainstorm 본문에 없다. 06h에만 있고, 06h는 설치되지 않는다. 오분류는 안전하지 않은 쪽으로 난다. confirmed가 되면 `--audit-delegated` 감사가 그 행을 건너뛴다.
- 수정: `brainstorm.md:38` delegated 줄을 "bare 'yes', 'proceed', 'looks good', 'as recommended' (in any language), or silent accept of ★"로 바꾼다. 37행 새 문장의 괄호를 "(an Other text, a paraphrase of one option; deferring to the ★ is not one)"으로 좁힌다. 그러면 intent의 "which those rules leave delegated"가 본문 그대로 참이 된다.

### 2. [Minor] 긍정 평가와 own-words 규칙의 우선순위가 열려 있다

- 근거: 같은 줄 앞부분은 "a label … in a rejecting, evaluating … context … picks nothing"이라고 한다. 새 문장은 "a paraphrase of one option"을 confirmed로 둔다. "b looks good", "the cache one sounds best"는 평가 문맥이면서 하나를 고르는 자기 말로도 읽힌다. F3가 좁혀 둔 "평가 문맥은 아무것도 고르지 않는다"가 긍정 평가에서 다시 흐려진다. 망설임 규칙은 예시("not sure, maybe b?", "b if it is cheap")가 있어 적용할 수 있다.
- 수정: 37행 끝에 "The picks-nothing cases in this rule win over the own-words case."를 덧붙이거나, "an evaluation alone, positive or negative, commits to nothing"을 넣는다.

### 3. [Minor] Checkpoint 문장 앞부분이 무조건 confirmed로 읽힌다

- 근거: `intent.md:21` "An answer to a question makes that row `confirmed` with the chosen option under the /sc:brainstorm Decision-mode tag step's rules". 주절이 "makes … confirmed"라서, 조건("under … rules")을 놓치면 망설이는 Other 답도 confirmed가 된다. 그러면 06h가 기록한 행동 변화(망설이는 Other → delegated)가 사라진다.
- 수정: "Tag each answer under the /sc:brainstorm Decision-mode tag step's rules, recording the chosen option; naming the ★ in reply to that one question is `confirmed` too. Rewrite the spec sections that follow from a confirmed row; every other row stays `delegated`."

### 4. [Minor] probe 검사의 `.claude/agent-memory-local` 절반을 지켜 주는 테스트가 없다

- 근거: 변이 표의 4행. `empty agent memory dir`은 빈 `-local` 디렉터리만 심으므로, 그 경로를 검사에서 빼도 17개가 모두 통과한다.
- 수정: `_through_state`에 `"agent memory-local left"`를 더한다(`.claude/agent-memory-local/verifier/x.md` 파일, `.git/info/exclude`에 경로 추가). 기대값은 `[_P]*8 + [_F, _P]`.

### 5. [Minor] 메모리가 없는 에이전트를 가리키거나 "모든 에이전트"라고 쓰는 문장이 남았다

- 근거: `src/superclaude/agents/repo-index.md:51` "Structure-Evolution: … Related: verifier". `Related:`는 `<memory_guide>` 범주 줄에 붙는 관련 에이전트 포인터다(`agent-authoring.md:219`). 규칙이 대상의 메모리를 명시하지는 않지만, 메모리 범주 옆에서 메모리가 없는 verifier를 가리키게 됐다. `test_memory_guide_refs_valid`는 이름이 존재하는지만 본다. `agent-authoring.md:215` "verbatim identical in every agent"는 이제 메모리가 있는 에이전트에만 맞다.
- 수정: repo-index의 `Related:`를 `deep-researcher`로 바꾸거나 지운다. 215행은 "in every agent with `memory`"로 고친다. 메모리가 있는 에이전트만 `Related:`에 허용하는 검사를 `test_memory_guide_refs_valid`에 더하는 것도 방법이다.

## 이 브랜치 밖의 메모

- 같은 목적의 다른 문서는 문제없다. `README.md:159`(빈 agent-memory store 정리), `README.md:398`(5 agents), `src/superclaude/ARCHITECTURE.md:55`, `src/superclaude/commands/save.md:41`("location follows the agent's `memory:` scope")은 메모리가 없는 에이전트와 모순되지 않는다. `docs/index.html`에는 memory 언급이 없다.
- 이전 릴리스가 남긴 `.claude/agent-memory/self-review/`·`verifier/`(project scope는 커밋돼 있을 수 있다)는 그대로 남는다. CHANGELOG가 사용자에게 직접 지우라고 쓴 것과 맞다. `doctor`는 이 고아 폴더를 알리지 않는다. 필요하면 다음 감사에서 ℹ️ 한 줄을 검토한다.
- `WS_GITIGNORE`(`evals/run_eval.py:90-93`)는 다른 probe에서 여전히 `.claude/agent-memory*/`를 숨긴다. 남은 세 에이전트가 쓸 수 있어서 의도된 것이다(06h Limits).
- 환경 함정: scratch `HOME`에는 git identity가 없어서 `git commit --allow-empty`가 실패한다. 그러면 `&&`로 이어진 master 설치가 건너뛰어지고, 다음 명령이 의도와 다른 project 설치를 만든다. scratch 재현에서는 `GIT_AUTHOR_*`/`GIT_COMMITTER_*`를 설정한다. master 설치 재현은 `git archive master src`를 풀고, worktree venv의 python으로 `sys.path` 앞에 그 `src`를 넣어 `superclaude.cli.entry:main`을 불렀다(`-I`로 PYTHONPATH 차단, 실행 중인 패키지 경로를 stderr에 출력해 확인).
- main 체크아웃(`/home/ubuntu/superclaude`)은 같은 sha의 `feature/goal-chain-followups`에 있다. 이 검증 브랜치의 커밋은 이 문서와 README 한 줄뿐이다.
