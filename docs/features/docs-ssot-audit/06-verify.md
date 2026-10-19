PASS WITH FIXES — D-01–D-24 수정은 SSOT와 맞고, 가드 19개가 ff947b33에서 실제로 red였다가 HEAD에서 green이며, suite·lint·typecheck·CI 모두 재현됐다. 다만 Q6 일탈로 README가 RESEARCH_CONFIG에 없는 규칙을 다시 RESEARCH_CONFIG 이름으로 말하고(Z-1), D-04의 rule 파일 위치가 고쳐지지 않았으며(Z-2), PRD에 같은 부류의 insight 쓰기 주장이 남았고(Z-3), `make release`가 core/README 때문에 canary 게이트에 걸린다(Z-4). T2는 CLI help의 줄바꿈에서 놓친다(Z-5). 다섯 건 모두 한 줄짜리 수정이며 머지 전에 처리하기를 권한다.

# docs ↔ SSOT 독립 검증 — `fix/docs-ssot` @ 8d61d296 (vs master 3301b506, v4.30.2)

## 실행 결과

빌더 보고는 출발점으로만 썼다. SSOT(코드, `hooks.json`, Makefile, `test.yml`, `RESEARCH_CONFIG.md`, 트리)는 직접 읽었다. 가드는 `$TMPDIR/verify-docs-ssot.MRiH/` 아래 detached worktree 세 개(ff947b33, 8d61d296, 3301b506)에서 main `.venv`의 python과 `PYTHONPATH=<worktree>/src`로 돌렸다. 각 실행에서 `superclaude.__file__`이 해당 worktree를 가리키는지 확인했다. mutation은 HEAD worktree에서 한 번에 하나씩 적용하고 `git checkout`으로 되돌렸다. worktree는 작업 뒤 제거했다. main 트리는 이 보고서 말고는 바뀌지 않았고 `~/.claude`는 건드리지 않았다.

| # | 검사 | 결과 |
|---|---|---|
| 1 | D-01–D-24 수정을 SSOT와 대조 | **23/24 맞음**. D-04는 부분 수정이다(Z-1, Z-2). 수정이 새로 만든 틀린 주장은 하나다(Z-1의 넷째 bullet). D-01의 *근거* 문장은 부정확하지만 수정 자체는 맞다(Z-9) |
| 2 | 판정(Q1–Q10) 준수 | Q1–Q5, Q8–Q10 준수. Q6: 삭제 대신 다시 쓴 블록의 bullet 1–3은 config에 글자 그대로 있다. 4는 없다(Z-1). Q7: core/README만 고쳤다. ARCHITECTURE.md:31은 같은 결함 부류로 남아 있다(Z-6). 05-plan §4의 "canary 불필요 / core 미변경"은 사실이 아니다(Z-4) |
| 3a | 가드가 fix 전에 red였나 (ff947b33) | **19 failed / 52 passed**. 빌더 보고(17 guards + no-expiry 2)와 같다. ff947에서 이미 green이었던 가드 행은 T2 D-13 하나다(Z-8) |
| 3b | HEAD에서 green인가 | `test_docs_ssot_guards.py` + `test_version_consistency.py` **71 passed, 0.36 s** |
| 3c | mutation 32개(stale 문구를 일부러 넣음) | **24 red / 8 green**. green 8개 중 3개는 문서화된 설계 한계다(T1b row에 event 없음, ARCHITECTURE의 k-token, codex의 `make verify` — make-target 테스트가 잡는다). 문서화되지 않은 놓침은 5개다: CLI help 줄바꿈(Z-5), README 표 행 형태(Z-7), `make translate`, `3.10/3.13`, evals/README의 `4-arm × 7-task`(Z-8) |
| 3d | 가독성·비용 | T2 phrase table **7행 (≤10 OK)**. 파일은 376줄로 plan 추정(T1–T7 합 ~190줄)의 두 배지만, 테스트마다 docstring이 finding ID를 달고 있어 읽기 쉽다. `_TARGET_WORDS`(16개)는 phrase가 아니라 필터라 cap 대상이 아니다 |
| 4 | 감사 extractor 재실행 | master **456** 후보(02-method 기록 443: path가 229 대 216이고 나머지 kind는 모두 같다 — untracked 파일 유무에 따른 path 해석 차이로 보인다), HEAD **412**(−44). in-scope 잔여 후보 ~100개를 전부 읽었다. placeholder, 외부 이름, 기록 문서뿐이다. 같은 부류의 놓친 모순은 grep으로 4건을 더 찾았다: Z-3, Z-10, Z-11, Z-12 |
| 5 | shipped content 변경 | `src/superclaude/`에서 바뀐 파일은 `ARCHITECTURE.md`, `cli/main.py`(help 문자열), `core/README.md`, `hooks/README.md`, `scripts/README.md`다. **모델이 읽는 텍스트의 변경은 0건**이다: README는 설치에서 제외되고(`install_components.py:362-363`, `:387-388`, `install_paths.py:68`), `ARCHITECTURE.md`는 설치되지 않으며(루트에서는 `CLAUDE_SC.md`만 복사, `install_components.py:452`), `CLAUDE_SC.md`는 FLAGS/PRINCIPLES/RULES만 import한다. dev 트리에 설치본 사본도 없다. `git diff master fix/docs-ssot -- src/superclaude/core src/superclaude/hooks/hooks.json` → `core/README.md` 1줄, hooks.json 0줄. 행동상 canary는 필요 없지만 릴리스 게이트에는 걸린다(Z-4) |
| 6 | `uv run pytest` | **exit 0, 4509 passed, 3 skipped** (79.6 s). 빌더 보고와 같다 |
|   | `ruff format --check src tests` / `ruff check src tests` / `make typecheck` | 240 files already formatted / All checks passed / Success, 54 files |
|   | CI | run 39224003874: `fix/docs-ssot` @ 4ec7da2e, `workflow_dispatch`, Python 3.10·3.13·lint/plugin/doctor 모두 success(Windows job은 skipped). 4ec7da2e..HEAD 차이는 `05-plan.md` 한 줄이다 |

### mutation 세부

| 가드 | mutation | 결과 |
|---|---|---|
| T1a | hooks/README에서 Stop 항목 삭제 / 없는 `### Notification` 추가 | red / red |
| T1b | insight_writer row에서 "Stop"만 삭제 / event 이름을 모두 삭제 | red / **green**(설계상, 05 Deviations) |
| T2 phrase | D-01 `.gitignore block`(uninstall help), D-24 `gitignored`(README), D-02 `` `integration` ``(PROJECT_INDEX), D-12 `pytest-cov`(AGENTS), D-13 `make verify`(PRD), D-06 `~1.5k-token`(core/README) | 모두 red |
| T2 phrase | D-13 `make verify`를 codex 05에 / D-06을 ARCHITECTURE에 / **D-15 `PM Agent`를 `superclaude --help` docstring에** | green / green(설계상) / **green — Click 줄바꿈, Z-5** |
| T2 기타 | CHANGELOG `superclaude hook prettier` / README `make verify-all` / README에서 `--orchestrate` 삭제 | red / red / red |
| T2 기타 | PRD에 `` `make translate` `` | **green**(Z-8) |
| T3 | PRD에 `tests/unit/test_skill_structure.py` / docs/README Layout에 `guides/` / PROJECT_INDEX에 `mistakes/` / AGENTS에 `gotchas/genral.md` | 모두 red |
| T4 | Time 열 추가 / Standard 20→25 / `Minimum threshold: 0.6` | 모두 red |
| T5 | prose bullet을 `/sc:reflect writes … insights.jsonl`로 되돌림 / **표 행을 `/sc:reflect` \| `Retrospective; captures … insights.jsonl`로 되돌림** | red / **green — Z-7** |
| T6 | PRD `3.10/3.11/3.12` / PRD `5-arm × 8-task` | red / red |
| T6 | PRD `3.10/3.13` / evals/README `4-arm × 7-task` | **green**(Z-8) |
| T7 | README tree에서 `skills/` 행 삭제 / install docstring에서 Skills 줄 삭제 | red / red |

## 발견 사항

### Z-1 — README "Evidence Rules"의 넷째 규칙은 RESEARCH_CONFIG에 없다 (수정이 만든 새 주장)
- **Severity** Medium · **Confidence** 높음
- **위치** `README.md:501-506` (`### 📊 **Evidence Rules**`, "Source gates from `RESEARCH_CONFIG.md`:")
- **근거**: Q6 (a)는 근거 없는 숫자를 *삭제*하라는 판정이었다. 빌더는 그 대신 블록을 config의 실제 규칙으로 다시 썼고, 05-plan Deviations에 적었다. bullet 1–3은 config에 글자 그대로 있다: ≥2 independent sources / one primary source / single-source label(`RESEARCH_CONFIG.md` `<gates>`), tier 1–4(`<credibility>`), load-bearing claim의 모순 → replan(`<replanning>` "sources disagree on a load-bearing claim"). bullet 4 "Every claim carries a confidence tag"는 `RESEARCH_CONFIG.md`에 없다(`grep -i confidence` → 0줄). 출처는 `agents/deep-researcher.md:67`("Each claim carries an explicit confidence tag")이다. 게다가 `modes/MODE_DeepResearch.md:25`는 "Confidence stated for each load-bearing claim, not for every sentence"라고 범위를 좁힌다. 결국 D-04가 고치려던 결함, 즉 README가 config에 없는 것을 config 이름으로 말하는 결함이 같은 블록에서 한 줄로 되살아났다. T4b는 숫자만 보므로 잡지 못한다.
- **수정**: bullet 4를 지운다. 꼭 남기려면 출처를 바로잡는다: "- Confidence stated for each load-bearing claim (`MODE_DeepResearch`, `deep-researcher`)". Q6 일탈(삭제 대신 다시 쓰기)은 owner 확인을 받아 05-plan 판정 표 옆에 적는다.

### Z-2 — D-04가 지목한 `.claude/rules/mode-authoring.md:106`이 그대로다
- **Severity** Medium · **Confidence** 높음
- **위치** `.claude/rules/mode-authoring.md:106` — "`RESEARCH_CONFIG.md` — depth profiles, confidence thresholds"
- **근거**: 03-findings D-04의 Where 열은 이 줄을 명시한다("the rule says RESEARCH_CONFIG holds 'confidence thresholds'"). 그런데 05-plan G2의 Files 열은 `README.md`만 적었고, `git diff --stat master fix/docs-ssot -- .claude`는 0줄이며, Deviations에도 없다. 이 rule은 mode 파일을 편집할 때 Claude Code가 자동으로 불러온다. 그래서 작성자에게 config에 없는 threshold를 찾거나 새로 만들게 유도한다.
- **수정**: "(e.g., `RESEARCH_CONFIG.md` — depth profiles, source gates, credibility tiers, tool routing)". 감사의 area test는 `tests/unit/test_mode_structure.py` + `test_cross_references.py`다.

### Z-3 — PRD가 hook이 `insights.jsonl`을 쓴다고 말한다 (D-05와 같은 부류, 놓침)
- **Severity** Medium · **Confidence** 높음
- **위치** `docs/PRD.md:60-62` — "hook-written `.claude/insights.jsonl` at SessionStart / PreCompact / Stop / SessionEnd"
- **근거**: hook은 `insights.pending.jsonl`에 쓴다. PreCompact/SessionEnd의 `harvest-from-hook` → `cmd_harvest` → `_pending_file()`(`insight_writer.py:64`, `:321`)이다. SessionStart는 `pending-count-from-hook`으로 개수만 출력한다. Stop은 INSIGHT: 한 줄을 요청하고, 다음 Stop에서 그 답을 pending으로 회수한다(`cmd_request`, `:729-768`). `insights.jsonl`에 들어가는 길은 `append`(`/sc:insight`)와 `promote`뿐이다(모듈 docstring `:4-11`). D-05(S2)가 README에서 고친 것과 같은 "명령/hook이 파일을 쓴다"는 주장이다. 이 라운드가 PRD를 편집했는데도(G4) 이 줄은 남았다.
- **수정**: "hooks harvest `INSIGHT:` lines into `.claude/insights.pending.jsonl` (PreCompact, SessionEnd, and the Stop request) and report the pending count at SessionStart; `/sc:insight` and `superclaude insight promote` write `.claude/insights.jsonl`".

### Z-4 — `make release`가 canary 게이트에 걸린다. 05-plan §4의 "neither is in G1–G5"는 틀렸다
- **Severity** Medium · **Confidence** 높음
- **위치** `docs/features/docs-ssot-audit/05-plan.md` §4 셋째 bullet. 게이트는 `Makefile:122`
- **근거**: `git diff --name-only v4.30.2..fix/docs-ssot -- src/superclaude/core src/superclaude/hooks/hooks.json` → `src/superclaude/core/README.md`. 게이트는 경로 단위로 판단하므로, 이 브랜치가 머지된 뒤 `make release`는 `CANARY_OK=1` 없이는 거절한다. 실질적으로는 행동 변화가 없다: core/README는 설치되지 않고(`install_components.py:362-363`, `:387-388`), 어떤 `@import`나 `TRIGGER_MAP`에도 없으며, dev 트리에 설치본도 없다. 그래서 canary를 돌려도 측정할 것이 없다. 문제는 계획 문서가 owner에게 "canary 필요 없음, core 미변경"이라고 말한다는 점이다.
- **수정**: §4를 "core/ 아래에서는 `README.md`만 바뀌었고 이 파일은 설치되지 않는다. 게이트는 경로로 판단하므로 release는 `CANARY_OK=1`로 하고 이유를 커밋/릴리스 노트에 적는다"로 고친다. 원한다면 별도 변경으로 게이트의 diff에서 `':!src/superclaude/core/**/README.md'`를 제외한다(Makefile 변경이라 이 라운드 범위 밖).

### Z-5 — T2가 CLI help를 Click이 줄바꿈한 결과로 검사해서, 두 단어짜리 phrase를 놓친다
- **Severity** Medium · **Confidence** 높음(재현)
- **위치** `tests/unit/test_docs_ssot_guards.py:38-51` (`_cli_help`), `:133-162`
- **근거**: Click은 docstring 문단을 80열로 다시 접는다. `main` docstring의 "plus a pytest plugin."을 "plus a pytest plugin with PM Agent."로 바꾸면 help는 `…with PM\n  Agent.`로 출력되고 `\bPM Agent\b` 행은 green이다. 같은 위험이 `\.gitignore block`, `\bmake verify\b`에도 있다. D-01·D-15가 바로 CLI help에서 나왔으므로, 가장 필요한 표면에서 가드가 운에 맡겨져 있다(D-01 mutation이 red였던 것은 문구가 줄 경계에 걸리지 않았기 때문이다). `uninstall --help`의 Examples 블록이 한 문단으로 뭉개지는 것도 같은 원인이다(기존 결함).
- **수정**: `_sources()`에서(최소한 help 텍스트에 대해서는) `re.sub(r"\s+", " ", text)`로 공백을 정규화한 뒤 검사한다. 한 줄 수정이다.

### Z-6 — ARCHITECTURE.md:31은 D-06과 같은 결함 부류이며, 가드 밖에 남았다 (Q7 판단)
- **Severity** Low · **Confidence** 높음
- **위치** `src/superclaude/ARCHITECTURE.md:31` — "RULES.md is a ~1.5k-token kernel … five rule classes whose loss is most expensive — purpose_before_action (…), scope, verification, destructive-op confirmation, project-rules priority"
- **근거**: 오늘은 맞다. `RULES.md`는 6,136 bytes이고 `<kernel_rules>`에 다섯 섹션이 있다(`RULES.md:15-35`). 하지만 이 문장은 core/README가 0.9k·4 classes로 낡아 간 것과 똑같은 형태다: SSOT(RULES.md `<mission>`의 "five rule classes", `TestCoreLiteSplit.KERNEL_CHAR_BUDGET`)를 숫자와 목록으로 복사해 두었다. Q7 (a)의 논거("(b) is stale at the next rule; the test owns the number")가 이 줄에도 그대로 적용된다. T2의 k-token 행은 이 한 줄을 피하려고 범위를 core/README로 특수 처리했다(`:151-154`). 즉 가드가 결함을 위해 예외를 둔 셈이다. 05-plan Deviations에 기록은 되어 있다.
- **수정(권고)**: core/README와 같은 처리를 한다. "RULES.md is the kernel — the rule classes in its `<kernel_rules>` (budget pinned by `TestCoreLiteSplit`) — plus a map of the on-demand modules". 2026-10-17 pilot 링크는 출처로 남겨도 된다. 그다음 k-token 행의 특수 범위를 지워 모든 routed doc에 적용한다. Q7 판정의 취지를 넓히는 것이므로 owner에게 한 줄로 확인받으면 충분하다.

### Z-7 — T5는 prose 형태만 잡고, D-05의 원래 위치였던 표 행 형태는 놓친다
- **Severity** Low · **Confidence** 높음(재현)
- **위치** `tests/unit/test_docs_ssot_guards.py:336-350`
- **근거**: claimant(`/sc:x`)를 셀 단위로 초기화한다. README:316은 `| /sc:reflect | Retrospective + insights captured to .claude/insights.jsonl |`처럼 명령과 파일이 서로 다른 셀에 있었다. ff947의 실패 메시지는 항목이 하나뿐이었다(prose bullet, README:336). 표 행을 원래 문구로 되돌리는 mutation은 green이다.
- **수정**: claimant를 줄(표 행) 단위로 유지한다(줄마다 초기화하고 셀 경계에서는 유지). 그러면 수정된 행 "`/sc:reflect` | Retrospective; `/sc:insight` captures …"에서는 claimant가 마지막으로 나온 `/sc:insight`가 되므로 여전히 green이다.

### Z-8 — 문서화되지 않은 가드 놓침(false negative) 모음
- **Severity** Low · **Confidence** 높음(재현)
- **근거·수정**:
  - **T2 D-13 행은 공회전한다.** ff947에서 이미 green이었다. phrase 범위(routed docs + Makefile + help)에 `make verify`가 없었기 때문이다. codex의 실제 위반은 `test_docs_name_only_makefile_targets`가 잡았고, 이 테스트의 범위는 phrase 범위를 포함한다. 행을 지우면 cap 10 중 한 칸이 빈다.
  - **make-target 필터**: 하이픈이 없고 `_TARGET_WORDS`에 없는 대상(`make translate` — 4.29.0에서 삭제된 실제 옛 target, codex 08:356)은 검사하지 않는다. 필터 대신 "backtick 안의 `make <t>`는 모두 검사"로 바꾸면 이 놓침이 줄어든다.
  - **T6**은 점이 셋인 버전 목록만 잡는다. `3.10/3.13`이나 `3.10, 3.13`처럼 test.yml의 *현재* 행렬을 복사한 문장은 통과한다. `evals/README.md`는 no-expiry 범위 밖이라 `4-arm × 7-task`를 다시 써도 green이다(D-08의 "4-arm" 제목이 바로 거기 있었다). 최소한 evals/README를 `_no_expiry_docs`에 넣기를 권한다.
  - **T3 layout은 한 방향만 본다.** 나열된 dir이 존재하는지만 확인하고, 존재하는 dir이 나열됐는지는 확인하지 않는다. D-11의 후반부(Layout이 adr/agents/codex/features를 빠뜨림)는 가드 밖이다.

### Z-9 — T2 행 두 개가 finding보다 넓다. D-01의 근거 문장도 부정확하다
- **Severity** Low · **Confidence** 높음
- **위치** `tests/unit/test_docs_ssot_guards.py:134-135`, `03-findings.md` D-01
- **근거**: D-01은 "`.gitignore` is not touched by any install module"이라고 했지만, `install_git_exclude._migrate_legacy_gitignore`(`:278-307`)는 install(`:336`)과 uninstall(`:387`) 모두에서 `.gitignore`의 옛 SC 블록을 지우고, 비면 파일까지 지운다. 그러니 옛 help의 "clean .gitignore block"은 legacy 경로에 한해서는 사실이었다. 새 문구(".git/info/exclude block")는 주 경로로서 맞으므로 수정은 유지하면 된다. 다만 `\.gitignore block` 행 때문에 "also strips a legacy `.gitignore` block"이라는 정확한 문장을 쓸 수 없고, `\bgitignored\b` 행 때문에 AGENTS/README가 "`uv.lock` is gitignored"(gotcha `uv-lock-local-only`) 같은 참인 사실을 말할 수 없다.
- **수정**: D-01 근거 문장에 legacy 이주를 덧붙인다. 두 행은 local scope 문맥으로 좁힌다(예: `(?:local|CLAUDE\.local\.md|\./\.claude/)[^\n]{0,60}\bgitignored\b`). 그게 과하면 행 주석에 "legacy 이주는 `.gitignore` 블록이 아니라 'legacy block'이라고 쓴다"는 우회법을 적는다.

### Z-10 — `last_verified: 2026-10-19`로 올린 codex guide에 같은 부류 문구가 남았다
- **Severity** Low · **Confidence** 높음
- **위치** `docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:61` "| local | `./.claude` | 개인·gitignored | …"(D-24 부류); `01_session_to_repository_principles.md:63` "4-arm harness"(D-08 부류, 01은 날짜를 올리지 않았다)
- **근거**: Q9 (a)는 범위를 D-08/09/12/13으로 제한했으니 판정 위반은 아니다. 하지만 04는 `last_verified`를 오늘 날짜로 올리고도 같은 줄의 같은 결함을 남겼다. T2 phrase 범위가 codex guide를 빼기 때문에(make-target과 T3은 포함하는데) 가드도 잡지 못한다. 08의 `measured_at: 5b6dc5b`는 그대로이고, 08:244 `install_skill.py`(존재하지 않는 모듈, 과거형 측정 문장)도 그대로다. 그래서 날짜 상향이 실제보다 넓은 재검증을 암시한다.
- **수정**: 04:61 → "개인·`.git/info/exclude`", 01:63 → "multi-arm harness(`run_eval.py` `ARMS`)". `_CODEX_GUIDES`를 phrase 행 범위에도 넣는다. 날짜를 올린 guide에는 "2026-10-19: D-08/09/12/13 항목만 재확인" 한 줄을 둔다.

### Z-11 — README 깊이 표의 "Standard … (default)"를 뒷받침하는 SSOT가 없다
- **Severity** Low · **Confidence** 높음
- **위치** `README.md:543` — "| **Standard** | 20 | 3 | General research (default) |"
- **근거**: `commands/research.md:10,21,25-28`, `RESEARCH_CONFIG.md`, `MODE_DeepResearch.md`, `deep-researcher.md` 어디에도 기본 depth가 없다. 같은 README의 예시는 "Basic research with automatic depth"(:525)라고 한다. 표를 다시 짠 이 라운드가 "Best For" 열을 T4 허용 목록에 넣었기 때문에 이 주장은 가드 밖에 있다. 기존 문구이고 수정이 새로 만든 것은 아니다.
- **수정**: "(default)"를 지운다.

### Z-12 — evals/README의 canary-only 목록이 이미 불완전하다 (Q10 수정)
- **Severity** Low · **Confidence** 높음
- **위치** `evals/README.md:26-30`
- **근거**: 새 문장은 canary-only task를 "behavior slices, prose-rule probes, the command-checkpoint probe, the skill and command-routing probes"로 열거한다. `tasks.yaml`에는 reframing-anchoring(:726–), purpose-generalization(:1107–), purpose-opus(:1523–) 그룹도 있다. 숫자를 지운 대신 목록을 복사한 셈이라, 같은 부류의 결함이 이미 낡아 있다.
- **수정**: "…and the canary-only tasks, grouped by the section comments in `tasks.yaml`"으로 열거를 없앤다.

## 확인했으나 문제 없음

- **D-01/D-24**: help·Makefile·CLAUDE.md·PRD:29의 "kept out of git via `.git/info/exclude`"는 `add_git_exclude`/`remove_git_exclude`(`install_git_exclude.py:310`, `:377`)와 맞다. README:92 "never your `.gitignore`"도 맞다(legacy 이주는 쓰지 않고 지우기만 한다).
- **D-02**: PROJECT_INDEX의 브랜치 모델은 AGENTS.md Git Workflow와 같다. **D-03**: PRD는 `test.yml`(pull_request→master, workflow_dispatch, "No push trigger"; `make ci`가 release 전에 dispatch, `Makefile:98-110`)과 맞다. **D-10**: `gh repo view ajitta/superclaude --json hasIssuesEnabled` → `true`, "not used"가 맞다.
- **D-05**: `/sc:insight`는 `insights.jsonl`을 쓰고 `--list`로 읽는다(`commands/insight.md:2,17-18`). `insight-analyst.md`는 이 파일을 읽는다.
- **D-06**: core/README의 새 문장은 `TestCoreLiteSplit`(`KERNEL_CHAR_BUDGET = 7600`, "kernel token budget")과 `<kernel_rules>`를 가리킨다.
- **D-07/D-18**: hooks/README의 Stop 항목은 `hooks.json:143-149`, `cmd_request`의 네 게이트(env opt-out, `stop_hook_active`, 세션당 한 번, 이 세션이 바꾼 작업 트리)와 맞다. session_init row는 `main()`(PR status → install status, `session_init.py:202-214`)과 맞다.
- **D-08**: PRD, codex 06, evals/README의 "every arm in `ARMS`" / "tasks without `canary_only`"는 `run_eval.py:60-66`, `:692`와 맞다(53 tasks, 45 canary_only, matrix 8). evals/README의 "Seven gates … matrix run carries 2 of the 7"도 `gate: true` 7개(`tasks.yaml:95,96,199,200,201,227,247`)와 맞다.
- **D-09**: PRD, codex 03/05가 이름 붙인 테스트 파일 6개가 모두 존재한다. codex의 `--canary` 대체는 실제 명령이다.
- **D-11**: docs/README Layout과 PROJECT_INDEX의 dir은 모두 `ls docs/`에 있다. `specs/` 지연 생성 문장은 `RULES_DOCS.md:24`(design/brainstorm → specs/)와 맞다.
- **D-12/D-13**: dev extras = pytest-asyncio, ruff, mypy(`pyproject.toml:43-47`). `make verify` / `build-plugin`은 `.PHONY`에 없다. codex 08의 `uv run --with pytest-cov …`는 실행 가능한 재측정 명령이다.
- **D-14, D-15, D-16, D-17**: UI-GUIDE 두 줄 삭제. 새 자기소개 문구는 `COMPONENTS`(8개: commands, agents, output-styles, core, modes, mcp, templates, skills)와 맞다. `--list` help "List available commands without installing"(`main.py:78`)과 README가 맞다.
- **D-19**: `sc-author/SKILL.md:4`에만 `disable-model-invocation: true`가 있다. **D-20**: `hooks/` = `hooks.json` + `mcp_fallback.py`. `utils/__init__.py` docstring이 `gotchas/hooks.md`를 가리킨다. core 행의 테스트 두 개가 존재하고(`test_quality_kernel_pointers_resolve`, `TestCoreLiteSplit`), `xml-prose-format.md`의 `paths:`에 `src/superclaude/core/**`가 있다.
- **D-21**: `RETIRED_FLAGS` 8개 키가 모두 README에 있다(`think*`는 `--think*`로 덮인다). `docs/features/serena-removal/`이 존재한다. **D-22**: CLAUDE.md는 `@AGENTS.md`만 import한다. **D-23**: v4.29.0의 `hook_dispatch.HOOKS`에도 이름이 `prettier_hook`/`test_runner_hook`였다. 따라서 당시에도 틀린 이름이었고, 과거 항목 수정이 정당하다.
- **D-25/Q5**: 두 계획은 `status: deprecated`(RULES_DOCS status enum에 있다)로 `docs/archive/plans/`에 옮겨졌다. 옛 경로를 참조하는 곳은 감사 문서 자신(기록)뿐이다.

## 검증하지 못한 것 / 범위 밖 관찰

- Windows: CI run의 Windows job은 skipped였다. 이 브랜치의 변경은 산문과 docstring뿐이라 영향은 없다고 본다.
- in-scope 문서 전체를 정독하지는 않았다. extractor 잔여 후보 전부와 결함 부류별 grep(gitignore, integration, arm/task 숫자, pytest-cov, make verify, k-token, PM Agent, 버전 목록, insights.jsonl, Serena)으로 표본 검사했다.
- 범위 밖이지만 shipped content 안에서 서로 어긋나는 것 두 가지: `commands/research.md:26-27`과 `deep-researcher.md:32`는 standard/deep/exhaustive를 "2-3 / 3-4 / 5+ hops"라고 하는데 `RESEARCH_CONFIG.md`는 3 / 4 / 5(`hop_config max="5"`)다. README는 config를 따른다. `evals/tasks.yaml:1`은 "4-arm eval task definitions"라고 하고, `:99-100`은 `destructive-named-path`를 "Canary only."라고 하지만 이 task에는 `canary_only`가 없어 matrix에서 돈다(`run_eval.py:692`).
- 운영 함정(이 브랜치와 무관): 이 checkout은 `remote.upstream.gh-resolved = base`라서 `-R` 없는 `gh`가 `SuperClaude-Org/SuperClaude_Framework`를 가리킨다(`gh run view 39224003874` → 404, `-R ajitta/superclaude`로는 성공). `make ci`/`make release`의 `gh` 호출에는 `-R`이 없다. 이 머신에서 release하기 전에 `gh repo set-default ajitta/superclaude`를 권한다.
