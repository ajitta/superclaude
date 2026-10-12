---
status: implementing
revised: 2026-10-12
---

# Serena 의존 제거 Implementation Plan

**Goal:** SuperClaude가 특정 심볼/메모리 MCP 서버에 기대어 동작하는 부분을 모두 없애고, 세션 기억은 커밋되는 독립 폴더 `.claude/memories/` + auto memory로 옮긴다.
**Architecture:** 배포 콘텐츠(커맨드·에이전트·규칙·모드·MCP 문서), 훅 스크립트(context_loader, mcp_fallback), 설치기(install_mcp)에서 해당 서버의 이름·도구·플래그·주입을 걷어 낸다. 코드 탐색 지시는 도구 이름 없는 Symbolic-First로 바꾼다. 마지막에 가드 테스트가 `src/superclaude/` 아래에 이름이 다시 들어오지 못하게 막는다.
**Tech Stack:** Markdown 콘텐츠, Python 3.10+ (click CLI, 훅 스크립트), pytest, ruff.

입력: [01-discovery.md](./01-discovery.md) (approved-for-plan), [00-intent.md](./00-intent.md). 줄 번호는 master `9e23d9f1` 기준이며, 앞 phase의 편집으로 밀릴 수 있으니 각 task는 grep으로 위치를 다시 잡는다.

## Shared rules

- 브랜치: master에서 `feature/serena-removal`. 첫 커밋은 이 폴더의 문서(00, 01, 05*, README).
- 사용자 지시 "serena를 언급하지 않는다"의 적용 범위
  - 0건이어야 하는 곳: `src/superclaude/` 전체, `README.md`, `SECURITY.md`, `AGENTS.md`, `docs/PRD.md`, `docs/reports/PROJECT_INDEX.md`, `.claude/rules/`
  - 남는 곳 (이유)
    - `.gitignore:122-123`, `.github/workflows/test.yml:8-9`, `.github/workflows/README.md:5`: 남겨 두기로 한 `.serena/` 폴더를 다루는 설정과 그 설명
    - `tests/`: 제거된 것을 가리켜야 하는 가드와 fixture
    - 과거 기록: `docs/features/*`, `docs/analysis`, `docs/research`, `docs/archive`, `.serena/memories`, `.claude/insights.jsonl`
    - CHANGELOG: Q5 결정. 다음 version-bump 커밋에서 추가한다 (아래 Release note)
- 메모리 폴더 결정: `.claude/memories/`
  - 파일 이름은 지금 쓰는 이름 그대로, 평평한 basename: `session_[date].md`, `learnings_[topic].md`, `context_[project].md`, `pm_context.md`, `last_session.md`, `next_actions.md`
  - 근거: SuperClaude가 이미 커밋되는 프로젝트별 데이터를 `.claude/`에 둔다 (`.claude/insights.jsonl`, `scripts/insight_writer.py:55`). SC의 git-exclude 목록(`cli/install_git_exclude.py:87-123`)에도, 이 레포 `.gitignore`의 `.claude/agent-memory*/`에도 걸리지 않는다
- 도구 중립 문구 결정 (Phase D가 그대로 쓴다)
  - R17: "when exploring unfamiliar code and a symbol-aware tool is connected (LSP or code-index MCP), start with its overview, definition and reference queries rather than reading whole files. Use Grep for text and regex matches, and Read when the file is small, non-code, or already identified."
  - 에이전트 full 형: `- Symbolic-First: with a symbol-aware tool connected (LSP or code index), query overview → definition → references before whole-file Read; without one, targeted Grep then Read of the matched range.` + 에이전트 고유 Grep 문구 + `Read whole files only when small or non-code.`
  - 에이전트 light 형: `- Symbolic-First: prefer symbol-aware queries (when connected) or targeted Grep over whole-file Read when exploring code.`
  - 에이전트에 줄을 그대로 두는 이유: subagent는 core rules를 받지 않는다 (`.claude/rules/agent-authoring.md`의 memory protocol 설명)
- 설치기 결정: core/plugin 구분을 없앤다. 대화형 `superclaude mcp`는 모든 서버를 번호로 나열하고 기본값 없이 고르게 한다. 빈 입력은 아무것도 설치하지 않는다 (`"No servers selected"`)
- 매 phase 끝: `uv run pytest` exit 0, `make lint` 통과, 그다음 커밋. Phase C·D가 `src/superclaude/scripts/`를 건드리면 `uv run pytest tests/unit/scripts -o addopts=`도 실행

## Deviations from 01-discovery

- P4: `AGENTS.md:36`은 `.serena/`를 언급하지 않고 새 폴더만 안내한다 (plan 시점 사용자 지시 "serena를 언급하지 않는다")
- P6: CHANGELOG 항목은 이 브랜치가 아니라 다음 version-bump 커밋에 넣는다. 근거: CHANGELOG는 bump 커밋에서만 바뀌고(`git log -- CHANGELOG.md`), `tests/unit/test_version_consistency.py:197`이 맨 위 release 제목을 pyproject 버전과 맞춘다
- P8: 허용 목록은 비운다. `cli/install_settings.py:391` 주석은 Phase C에서 이름 없이 고친다

## Phases

- [x] Phase A: [05a-plan-memory-folder.md](./05a-plan-memory-folder.md) — /sc:save·/sc:load와 메모리를 다루는 콘텐츠를 `.claude/memories/` + auto memory로
- [x] Phase B: [05b-plan-loader-flag.md](./05b-plan-loader-flag.md) — MCP 문서 삭제, context_loader 주입·플래그, fallback 힌트, 컴포넌트 카운트
- [ ] Phase C: [05c-plan-installer.md](./05c-plan-installer.md) — 설치기 등록·사전 점검 제거, core/plugin 구분 제거, 설치 문서
- [ ] Phase D: [05d-plan-symbolic-first.md](./05d-plan-symbolic-first.md) — R17, 에이전트 18개, 나머지 콘텐츠의 도구 중립화 + 가드 테스트
- [ ] Phase E: [05e-plan-repo-docs.md](./05e-plan-repo-docs.md) — README·SECURITY·AGENTS·PROJECT_INDEX·mcp-authoring, local scope 재동기화

순서 근거: A가 메모리 대체 경로를 먼저 만들어야 B가 /sc:load·/sc:save 주입을 지워도 기능이 비지 않는다. B가 `--serena`를 FLAGS에서 지우기 전에 이를 쓰는 recommend 줄도 B에서 함께 지운다. 가드 테스트는 `src/`의 마지막 phase인 D에서 넣어야 처음부터 끝까지 suite가 green이다.

## Risks

- 가장 위험한 단계: Phase C의 대화형 설치 경로 재작성. 사용자가 직접 실행하는 CLI 동작이 바뀐다. 기본 입력 `0`(core 전부 설치)이 사라지고 빈 입력은 취소가 된다. 새 테스트가 메뉴 내용과 기본값 없음을 고정한다
- 기존 사용자
  - 설치된 `~/.claude/superclaude/mcp/` 아래 예전 MCP 문서 파일이 남는다. 설치기는 파일 단위로 복사하고 지우지 않는다(`cli/install_components.py`). loader가 더 이상 그 파일을 매핑하지 않으므로 읽히지 않는다. `superclaude verify` drift에는 EXTRA로 보인다. MCP_Context7.md 제거 때와 같은 선례
  - 예전 `.serena/memories/`는 /sc:load가 읽지 않는다 (P10). 그 서버를 계속 쓰는 사용자는 서버 자체 도구로 읽는다
  - 이미 등록된 MCP 서버는 그대로 동작한다 (P2). SuperClaude가 지우거나 경고하지 않는다
  - `--serena`는 오류 없이 효과 없는 텍스트가 된다. 확인: VALID_FLAGS에서 뺀 상태로 `resolve_flags('analyze --serena x')` → `('analyze --serena x', [])`
- `.claude/`를 통째로 gitignore한 사용자 프로젝트에서는 `.claude/memories/`가 커밋되지 않는다. `cli/install_git_exclude.py:80-85` 주석과 같은 입장: 팀이 `.gitignore`로 정할 일
- 심볼 도구가 없는 세션에서는 Symbolic-First가 targeted Grep으로 떨어진다. 지금 fallback과 같은 동작이라 회귀가 아니다

## Alternatives not taken

- 메모리를 `docs/memory/`에: docs/는 사이트로 게시되는 일이 흔하고, `core/rules/RULES_DOCS.md`의 문서 명명 규칙 아래에 있다. project-manager의 patterns/mistakes는 그대로 `docs/memory/`에 남는다
- `.superclaude/memories/`: 이 레포 `.gitignore:124`가 이미 `.superclaude/`를 무시한다. 같은 규칙을 가진 프로젝트에서 조용히 커밋이 안 되어 Q7을 어긴다
- `.claude/superclaude/` 아래: 설치기가 관리하고 덮어쓰며, local scope에서는 git-exclude된다 (`install_git_exclude.py:122`)
- core 카테고리를 빈 채로 유지: "core 전부 설치" 옵션이 아무것도 설치하지 않는 죽은 경로가 남는다
- `--serena`를 `RETIRED_FLAGS`에 추가해 안내: 이름이 배포 콘텐츠에 다시 들어간다. Q5는 효과 없는 텍스트를 골랐다
- 설치된 예전 MCP 문서를 `LEGACY_SKILL_NAMES`처럼 이름으로 지우기: 역시 이름이 `src/`에 들어간다. 남는 파일은 읽히지 않는다
- 에이전트 줄을 R17 포인터 한 줄로: subagent는 core rules를 받지 않아 포인터가 가리킬 내용이 없다

## Proof

1. `git grep -i -l serena -- src/ README.md SECURITY.md AGENTS.md docs/PRD.md docs/reports/ .claude/rules/` → 출력 없음
2. `uv run pytest` → exit 0. `uv run pytest tests/unit/scripts -o addopts=` → exit 0. `make lint` → exit 0
3. `uv run superclaude context explain "/sc:load"` → `mcp/` 파일 주입 없음
4. `uv run superclaude context explain "--serena rename x"` → `mcp/` 파일 주입 없음, 경고 없음
5. `uv run superclaude mcp --list` → 서버 목록에 core/plugin 제목 없음, 제거된 서버 없음
6. `printf '\n' | uv run superclaude mcp --dry-run` → 모든 서버가 번호로 나열되고 `No servers selected`, exit 1
7. `git check-ignore -v .claude/memories/probe.md` → 출력 없음 (exit 1)

## Release note (다음 version-bump 커밋의 CHANGELOG `### Changed` / `### Removed`)

- `/sc:save` and `/sc:load` keep session memories in `.claude/memories/` (committed with the project) plus Claude auto memory. Existing `.serena/memories/` files stay where they are and are no longer read.
- Removed: the Serena MCP doc, the `--serena` flag (now plain text with no effect), and Serena registration in `superclaude mcp`. An already registered Serena server keeps working; register or remove it with `claude mcp`.
- `superclaude mcp` no longer pre-selects servers: the interactive picker lists every server and installs only the numbers you enter.
- Agents and R17 say "symbol-aware tool (LSP or code index)" instead of naming a server.
