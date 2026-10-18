PASS WITH FIXES — 코드·테스트·버전·카나리 게이트는 모두 사실로 확인됐으나, v4.29.2와 v4.29.3의 GitHub 릴리스 노트가 `make release`의 CHANGELOG 추출 버그로 비어 있다(R-1).

# SuperClaude v4.29.3 독립 리뷰

- 대상: tag `v4.29.3` = `d61d79cd` = `origin/stable` (detached worktree, 수정 없음 — 리뷰 후 `git status` clean)
- 범위: `git log v4.29.1..v4.29.3` (36 commits, 49 files, +1731/−219)
- 리뷰 일자: 2026-10-19, Linux aarch64, Python 3.11.16 (`.venv`)

## 실행 결과

| 명령 | exit | 핵심 수치 |
|---|---|---|
| `uv run pytest` (전체, 1회차) | 0 | **3871 passed, 3 skipped**, 42.46s (wall 44.2s) |
| `uv run pytest -rs` (2회차, skip 사유 확인) | 0 | 3871 passed, 3 skipped, 32.95s. skip: `test_parallel_ab_e2e.py:24` (`AB_E2E=1` 필요), `test_prettier_hook.py:65,77` (Windows `.cmd`) |
| `uv run pytest --co -q` / `--ignore=tests/unit/scripts` 추가 | 0 | 3874 / 3734 collected → `tests/unit/scripts` 140건이 기본 실행에 포함됨 |
| `uv run ruff format --check src tests` | 0 | 234 files already formatted |
| `uv run ruff check src tests` | 0 | All checks passed (`ruff check .`도 0) |
| `make help` | 0 | 3개 섹션, 21개 타깃 = `.PHONY` 21개와 일치. `mawk`·`gawk`로 돌린 출력의 md5가 동일 |
| mypy | — | Makefile/CI에 mypy 타깃 **없음**. 참고용으로 `uv run mypy src` 실행: exit 1, **34 errors / 16 files** (v4.29.1 트리는 31개, R-5) |
| `HOME=<scratch> superclaude install --scope user` (사용자 훅을 미리 넣은 settings.json) | 0 | 83 installed, 0 failed. 사용자 `PreToolUse` 훅과 `"model"` 보존, SC 훅 14개 병합 |
| 같은 install `--force` 재실행 | 0 | 훅 15개(사용자 1 + SC 14) — 중복 없음, 멱등 |
| `superclaude doctor --scope user` | 0 | 5개 체크 모두 ✅ |
| `superclaude uninstall --scope user --yes` | 0 | 8 removed; settings.json에는 사용자 훅과 `model`만 남음, CLAUDE.md import 줄 제거 |
| `superclaude install --list-all` | 0 | commands 35, agents 24, output styles 1, modes 7(6 MODE + RESEARCH_CONFIG), skills 2 |
| `superclaude context explain "/sc:analyze --delegate …"` (env 미설정) | 0 | `budget: 12000`, 4개 파일 주입 ~8297 tokens: QUALITY 3245 + DELEGATION 2236 + DOCS 2534 + INTERACTION 282 |
| 같은 명령, `CLAUDE_CONTEXT_MAX_TOKENS=8000` | 0 | RULES_DOCS.md가 "dropped by the token budget"으로 빠짐 → 회귀 재현, 12K에서 해소 확인 |
| `claude plugin validate .` / `… portable-skills/plugins/socratic` | 0 / 0 | 둘 다 "Validation passed" (marketplace는 README 설치 줄에 대한 권고만 출력) |
| author-check 코퍼스 diff (v4.29.1 vs v4.29.3, tracked `*.md` 569개) | 0 | finding 차이 1건: `RULES_DELEGATION.md:63` 오탐 X2 제거. format 추론 차이 0 |
| author-check 코퍼스 diff (`a1d6ca7a^` vs v4.29.3) | 0 | 차이 0건 → "findings on every tracked `*.md` are unchanged" 사실 |
| author-check, 배포 콘텐츠 77개 파일 | — | error 0, warning 5 (N1 4건은 예시 경로, N4 1건은 VS 템플릿 반복 — 결함 아님) |
| `gh api …/setup-uv/git/ref/tags/v10.3.0` | 0 | `1c37ad07a6a961277cf70c0d37d6f313000f5884` → 워크플로 핀과 일치 |
| `gh run list --workflow Tests` | 0 | `d61d79cd` master 디스패치 run 39154675014 success; 문서가 인용한 39153742114(`3e64dc82`), 39151749108(`cd9f7e63`) success |
| `gh release view v4.29.{0,1,2,3} --json body` | 0 | 본문 길이 1922 / 1036 / **1** / **1** 자 (R-1) |

## 발견 사항

### R-1 — High — 확신도 높음(재현됨): v4.29.2·v4.29.3 GitHub 릴리스 노트가 비어 있음

- 위치: `Makefile:115`, `CHANGELOG.md:9`
- 증거:
  - `Makefile:115`: `awk '/^## \[/{n++; next} n==1' CHANGELOG.md > .release-notes.md;`
  - `CHANGELOG.md:9`: `## [Unreleased]` (본문 없음), 그 아래 `## [4.29.3] - 2026-10-19`
  - `gh release view v4.29.3 --json body` → 길이 1, v4.29.2도 1. v4.29.1은 1036.
  - 현재 트리에서 `awk '/^## \[/{n++; next} n==1' CHANGELOG.md | wc -c` → `1`
  - 원인 커밋: 4.29.1 bump(`c11f0e24`)는 `## [Unreleased]`를 버전 제목으로 **바꿨다**. 4.29.2 bump(`2b2e0a9c`)는 빈 `## [Unreleased]`를 위에 **남기고** 그 아래에 버전 제목을 추가했다. awk는 첫 번째 `## [` 섹션, 즉 빈 Unreleased를 가져간다.
- 영향: CHANGELOG 4.20.1이 약속한 "Each release is a GitHub release … and its notes are this file's entry for that version"이 두 릴리스 연속 깨졌다. 빈 `[Unreleased]` 헤더가 남아 있는 한 다음 릴리스도 빈 노트로 나간다. 추출 결과가 비어도 `gh release create`가 그대로 진행하고, 이를 잡는 테스트가 없다(`tests/`에서 `release-notes`나 `n==1`을 검색해도 없음).
- 수정:
  1. `Makefile:115`를 버전 키로 추출하고, 결과가 비면 중단하게 바꾼다. mawk·gawk 모두에서 4.29.3(365 B)과 4.29.2(1945 B)를 정확히 뽑는 것을 확인했다:
     ```make
     awk -v v="$$V" 'index($$0, "## [" v "]") == 1 { f = 1; next } /^## \[/ { if (f) exit } f' CHANGELOG.md > .release-notes.md; \
     grep -q '[^[:space:]]' .release-notes.md || { echo "❌ CHANGELOG has no entry for $$V"; exit 1; }; \
     ```
  2. 이미 나간 두 릴리스를 보정한다. 각각 `gh release edit v4.29.2 --notes-file <(awk -v v=4.29.2 '…' CHANGELOG.md)`, v4.29.3도 같은 방식(외부 공개 작업이므로 소유자가 실행).
  3. `tests/unit/test_makefile_help.py` 옆에 회귀 테스트를 추가한다. 현재 CHANGELOG의 `pyproject` 버전에 위 awk를 돌려 비어 있지 않은지 확인한다.

### R-2 — Low — 확신도 높음(재현됨): Markdown 첫 줄 `<word …` 바로 다음 줄이 blockquote면 XML로 오추론되어 오탐 X2 error

- 위치: `src/superclaude/cli/author_check.py:197-200` (`_ATTR_RE_SRC`/`_ATTR_LINE_RE`), `:204-218` (`_is_multiline_tag`)
- 증거: 파일 내용 `"<draft notes for the team\n> quoted reply\n\nSome prose here.\n"`
  - v4.29.3: `superclaude author-check …` → `1: X2 error: `<draft>` is never closed`, `1 errors`, **exit 1**
  - v4.29.1: format `md`, finding 0
  - 원인: TAG_RE의 lazy 매치가 다음 줄의 blockquote `>`에서 끝나 토큰이 `<draft notes for the team\n>`가 된다. 연속 줄 `>`는 `_ATTR_LINE_RE`의 "closer alone" 분기에 맞고, 매치가 줄 시작에서 시작하므로 `_is_multiline_tag`가 태그로 받아들인다.
- 영향: CHANGELOG 4.29.2와 docstring은 "angle-bracket terms in Markdown prose are unaffected"라고 한다. 그런데 보호하는 테스트(`test_author_check.py:504-520`)는 term과 blockquote 사이에 산문 줄(`for things.`)이 있는 경우만 다룬다. 바로 인접한 경우는 이전에 md였는데 이제 error/exit 1이다. 실제 트리에는 해당 파일이 없다(코퍼스 diff 0). 그래서 Low.
- 수정: 연속 줄이 bare closer뿐이면 그 줄은 줄 시작 `>`가 아니라 직전 줄 끝에 붙은 경우만 인정한다. 예를 들어 `_is_multiline_tag`에서 마지막 연속 줄이 `^\s*>`이고 원문에서 그 `>` 뒤에 같은 줄 텍스트가 이어지면(blockquote) 거부한다. 그리고 `infer_format("<draft notes for the team\n> quoted reply\n") == "md"` 테스트를 추가한다.

### R-3 — Low — 확신도 높음: 커밋된 insight가 철회된 동작을 현재 사실로 기술

- 위치: `.claude/insights.jsonl:174`
- 증거: `"`tests/unit/scripts/` is only excluded from the default pytest run (`--ignore` in addopts, …); CI runs it in a separate `pytest tests/unit/scripts -o addopts=` step and `make test-scripts` runs it locally."`
- 영향: `insight-analyst` 에이전트와 `/sc:insight`가 이 파일을 검색 대상으로 쓴다(`agents/insight-analyst.md:24`). 트리 전체를 grep한 결과(`docs/features`·`docs/archive`·CHANGELOG 제외) `--ignore`/`-o addopts=` 잔존 문구는 이 줄이 유일하다. AGENTS.md, Makefile, CI, pyproject, PRD, workflows/README는 모두 갱신됐다.
- 수정: 파일 규약(append-only `annotation` 항목, `insight-analyst.md:32`)대로 174번 항목을 superseded로 표시하는 annotation을 추가한다. 근거로 `docs/features/test-exclusion-lift`와 커밋 `3e64dc82`를 단다.

### R-4 — Low — 확신도 높음: CHANGELOG 헤더의 태깅 규칙과 맞지 않는 항목 2개

- 위치: `CHANGELOG.md:5`, `:309`, `:336`
- 증거: 헤더 `A release is tagged `vX.Y.Z``. 그러나 `## [4.20.0+ajitta]`, `## [4.19.0+ajitta]`에 대응하는 태그가 없다(`git tag --list` 결과는 v4.20.1부터). 나머지 19개 버전은 모두 태그가 있다.
- 영향: 태깅 정책은 4.20.1에서 생겼으니(그 항목의 "Added") 역사적 사실이다. 다만 "CHANGELOG의 모든 버전 = 태그"를 기계적으로 검사하면 실패한다.
- 수정: 헤더에 "4.20.1부터"를 명시하거나("Releases from 4.20.1 on are tagged…"), 두 항목 제목 옆에 "(untagged)"를 붙인다.

### R-5 — Low — 확신도 높음: mypy가 dev 의존성·`[tool.mypy]` 설정만 있고 게이트가 없어 오류가 늘고 있음

- 위치: `pyproject.toml:46` (`"mypy>=1.0"`), `:100` (`[tool.mypy]`); Makefile·`test.yml`에 mypy 호출 없음
- 증거: `uv run mypy src` → v4.29.3 34 errors, v4.29.1 31 errors. 증가분은 이번 범위의 `author_check.py` 변경에서 나온다. 예: `:511` `Incompatible types in assignment (expression has type "str | bool", variable has type "str")` — `tag_parts()`가 `str`를 반환하도록 주석이 달려 `selfclose or is_void(name)`이 `str|bool`이 됨. 그 밖에 `context_loader.py:200`/`:680`, `main.py:996`은 `TRIGGER_MAP`이 `list[tuple[str,str,int]]`로 주석돼 있지만 실제로는 `Pattern`을 담는다는 주석 드리프트다. 런타임 버그는 아니다(테스트 통과, `context explain` 정상).
- 영향: 이번 릴리스의 결함은 아니다. 다만 AGENTS.md가 mypy를 dev 툴체인의 일부로 언급하는데 아무도 돌리지 않아 타입 주석이 실제와 계속 벌어진다.
- 수정: 둘 중 하나를 고른다. (a) `make typecheck` 타깃을 추가하고 현재 34건을 baseline으로 고정해 증가만 막는다. (b) mypy를 dev extras와 `[tool.mypy]`에서 빼서 "실행되지 않는 도구"를 없앤다.

### R-6 — Low — 확신도 높음: authoring 규칙 3개가 형식 명세와 반대로 `<examples><example>` 중첩을 지시

- 위치: `.claude/rules/command-authoring.md:54`, `.claude/rules/mode-authoring.md:43`, `.claude/rules/mcp-authoring.md:32` ↔ `.claude/rules/xml-prose-format.md:154`
- 증거: 세 파일의 공통 문장은 `plural↔singular containers (`<examples><example>`) for multi-line items.`이다. 세 파일이 따른다고 밝힌 명세(`xml-prose-format.md:154`)는 `<example>` is not a sub-item of `<examples>` — they are two distinct constructs.`라고 한다. `command-authoring.md:107`은 명세 쪽을 반복하므로 같은 파일 안에서도 모순이다.
- 영향: Claude Code가 자동 로드하는 authoring 규칙이 둘 다 따를 수 없는 지시를 동시에 준다. 콘텐츠 작성 시 어느 쪽을 따를지가 우연에 맡겨진다.
- 수정: 세 줄에서 `plural↔singular containers (`<examples><example>`)`를 명세에 맞게 고친다. 예: "`<examples>` table for short uniform rows, a standalone `<example>` for multi-line items (two distinct constructs)".

### R-7 — Low — 확신도 중간: 문서 전용 변경의 검증 수준이 kernel과 on-demand 모듈에서 다름

- 위치: `src/superclaude/core/RULES.md:26` ↔ `src/superclaude/core/rules/RULES_QUALITY.md:79`, `:84`
- 증거: kernel은 `For docs-, comment- or text-only changes that no test, build or linter reads, the check is inspection`이라고 조건을 단다. `<verification_ladder>`는 조건 없이 `| 0 | docs/comments/text-only changes | static inspection only` 및 `Docs-only changes stay Level 0.`라고 한다.
- 영향: markdown을 테스트가 읽는 저장소(이 저장소 자체: AGENTS.md "content counts, cross-refs and doc structure have tests")에서, RULES_QUALITY가 로드된 세션은 Level 0을 근거로 테스트를 건너뛸 수 있다. kernel 규칙과 충돌한다.
- 수정: ladder의 Level 0 Trigger를 `docs/comments/text-only changes that no test, build or linter reads`로 맞추고, `:84` 끝 문장을 "Docs-only changes that a test reads are Level 1"로 바꾼다.

### R-8 — Low — 확신도 높음: CLI 도움말 예시 경로가 존재하지 않음

- 위치: `src/superclaude/cli/main.py:726`
- 증거: `superclaude parallel-ab docs/experiments/brainstorm-ab/variants.yaml`. 실제 파일은 `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml`이고, `docs/experiments/brainstorm-ab`는 없다.
- 영향: 도움말 예시를 그대로 실행하면 파일 없음으로 실패한다. 이번 범위의 변경은 아니다.
- 수정: 예시 경로를 `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml`로 고친다.

## 검증했으나 문제 없음

- **버전 일치**: `pyproject.toml:7`, `src/superclaude/__init__.py:7`, README 배지(`:8`)와 "Current Stable Version"(`:48`)이 모두 `4.29.3`. `.claude-plugin/marketplace.json`에는 버전 필드가 없다. `portable-skills` 플러그인은 독립 버전(1.0.1)이고 이번 범위에서 변경 없음.
- **태그**: CHANGELOG의 숫자 버전 19개(4.20.1–4.29.3)에 모두 태그가 있다. `v4.29.2`→`1f57aa62`, `v4.29.3`→`d61d79cd` = `origin/stable`. GitHub release `v4.29.3`의 target은 `d61d79cd`.
- **카나리 면제**: `git diff --stat v4.29.1 v4.29.3 -- src/superclaude/core src/superclaude/hooks/hooks.json` 결과가 비어 있다. `make release` 게이트 조건과 일치해 카나리 생략이 정당하다.
- **4.29.2 Removed**: `tool_called`/`parallel_tool_calls_min`과 `tools_called`/`max_parallel_tool_calls` 필드가 `evals/run_eval.py`에서 제거됐다. 남은 참조는 README 설명과 "rejected" 테스트(`test_eval_harness.py:781-794`, `unknown check type` ValueError)뿐.
- **4.29.2 Fixed — 컨텍스트 예산**: 수치 8,015(=3245+2236+2534), 282, 12,000을 `context explain`으로 재현했다. 상수 하나(`utils/__init__.py:65`)를 loader(`context_loader.py:52`)와 `context explain`(`main.py:1038`)이 함께 쓴다. env override는 유지되고 malformed 값은 기본값으로 대체된다. 헤드룸 테스트(`test_context_loader.py:341-376`)는 실제로 실패할 수 있는 구조이고(전체 rule 모듈 + 최대 routed mode + 500), 기본 예산 e2e 테스트는 `env_unset`으로 개발자 env를 차단한다. 트리 전체에 남은 `8K`/`8000` 표기는 `docs/archive`, CHANGELOG 과거 항목, `int_env` 단위 테스트뿐이다. ARCHITECTURE.md와 scripts/README.md는 갱신됨.
- **4.29.2 Fixed — author-check 따옴표**: `RULES_DELEGATION.md:63` 오탐 제거를 코퍼스 diff로 확인했다. `<step note=don't>`는 자기 줄에 `unbalanced quote` X2를 보고한다(프로브).
- **4.29.2 Fixed — 멀티라인 추론과 N4**: 멀티라인 opener(`<component\n  name="x">`)를 xml로 추론하고 미닫힘을 보고한다(프로브). 트리 전체의 finding은 `a1d6ca7a^` 대비 불변(R-2의 인접 blockquote 예외 제외).
- **4.29.3 Changed**: `pyproject` addopts에서 `--ignore` 제거, 기본 실행에 140건 포함, `make test-scripts` = `pytest tests/unit/scripts`, CI의 별도 단계 삭제를 확인했다. `c97705c0`이 실제로 `--ignore`를 추가한 커밋이다. AGENTS.md, workflows/README, PRD, Makefile 주석 모두 새 상태를 기술한다. AGENTS.md의 "the suite's only asyncio tests"는 기본 실행 기준으로 참이다(`parallel_ab/test_orchestrator.py`·`test_runner.py`, e2e는 skip).
- **setup-uv 핀**: SHA가 `v10.3.0`(2026-10-09, 최신 릴리스) 태그와 일치한다. "no major-version tags past v7"도 원격 태그 목록으로 확인(v7은 있고 v8/v9/v10 floating 태그는 없음). `enable-cache: false` 사유도 타당하다.
- **Dependabot**: `github-actions`, `directory: /`, monthly, grouped, `target-branch: master`. "default branch(stable)에서 읽으므로 다음 릴리스에 활성화" 주장은 실제로 맞았다. 릴리스 직후 PR #23(`actions/checkout@v4→v7`, `setup-python@v5→v7`)이 master 대상으로 열렸고 CI success.
- **Makefile help**: `.PHONY` 21개 = 문서화된 규칙 21개 = 실제 규칙 21개. 테스트 3개는 각각 누락 방향을 잡도록 짜여 있다(주석 없는 PHONY 타깃, PHONY 밖 규칙, 수기 목록 복귀).
- **설치/병합**: 격리 HOME에서 install → force 재설치 → doctor → uninstall 전 과정에서 사용자 훅을 보존하고 중복 병합이 없었다.
- **콘텐츠 수**: `02_component_and_delivery_map.md` §1(agents 24, commands 35, core 3, rules 4, MODE 6, CONFIG 1, mcp 3, skills 2, hook 등록 14, Python module 53), README의 "35 slash commands"/"6 behavioral modes"/"24 agent definitions"가 트리·설치 결과·mypy 모듈 수와 모두 일치한다.
- **`@`-import**: `CLAUDE_SC.md`의 `@core/FLAGS.md`, `@core/PRINCIPLES.md`, `@core/RULES.md`가 모두 존재한다. core/*.md에는 추가 `@` import가 없다.
- **퇴역 이름·규칙 태그**(sub-agent 스윕 후 직접 재확인): `--task-manage`/`--orchestrate`/`MODE_Task_Management`/`MODE_Orchestration`/`/sc:sc`는 `context_loader.py`의 redirect 안내에만 남아 있다. `FLAGS.md`는 실제 6개 mode만 나열한다. `[Rnn]` 태그와 `<workflow_delegation>` 등 파일+태그 참조는 모두 해석된다. 그 밖의 후보(RULES.md:34 vs RULES_QUALITY.md:89의 gotcha 위치, security-engineer "Use immediately" vs 위임 금지, Ask First 문장 verbatim 복제)는 문맥상 조정되거나 의도된 것으로 판단해 제외했다.
- **frontmatter**: 배포 콘텐츠 77개(commands, agents, skills, output-styles, modes, core, rules)에 author-check F/X/S error 0건.

## 검증하지 못한 것

- **Windows 재현**: "eight full runs … reproduced nothing (six sequential, two concurrent)"은 Windows 전용 주장이다. 이 리뷰는 Linux에서만 실행했으므로 기록(`docs/features/test-exclusion-lift/01-verification.md`)을 확인하지 못했다. Linux CI run 39153742114가 green이라는 것까지만 확인했다.
- **카나리/evals**: 지시대로 `claude -p` 기반 `make canary-gates`와 evals는 실행하지 않았다. core/hooks.json 변경이 없어 이번 릴리스의 필수 조건은 아니다.
- **Python 3.10/3.13**: 로컬은 3.11.16 하나다. 매트릭스 두 버전은 GitHub CI run(success) 결과로만 확인했다.
- **`make release` 실제 실행**: 외부 공개 작업이라 실행하지 않았다. R-1의 수정 awk는 로컬 CHANGELOG에서만 검증했다.
