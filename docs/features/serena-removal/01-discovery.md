---
status: approved-for-plan
revised: 2026-10-12
---

# Discovery: SuperClaude의 Serena 의존 제거

입력: [00-intent.md](./00-intent.md). 탐색 시점 master `9e23d9f1`. 근거 줄 번호는 이 커밋 기준.

## Intent coverage

| Intent 항목 | discovery에서 구체화한 내용 |
|---|---|
| Problem: "문제를 일으킴" | 사용자 진술: "serena가 worktree, 프로젝트 동시 편집등에서 문제를 일으킨다". "지금은 반드시 써야하는 것처럼되어 있어". 아래 인벤토리의 1~4가 "반드시 써야 하는 것처럼" 만드는 지점이다 |
| Proposed outcome: "superclaude가 serena를 이용하고 참조하면서 동작하는 것을 없애려는 거야" | "문제를 줄이겠다가 아니라 문제가 있는 MCP를 쓰지 않겠다는 것". Q2~Q7 결정: 메모리는 커밋되는 독립 폴더 + auto memory, 에이전트 지시는 도구 중립으로, 설치기에서 제거, 플래그·문서·주입 전부 제거 |
| Affected: 배포 콘텐츠, CLI/설치 코드, 레포 개발 환경 | 인벤토리 1~6이 세 영역을 덮는다. 로컬 환경은 범위 밖으로 유지 (Open questions 1) |
| Constraint: "쓰는 것을 막지는 않아" | 사용자가 직접 등록한 Serena MCP와 `.serena/` 데이터는 건드리지 않는다. "이 프레임워크는 미니멀한 것이고 거의 왠만한 모든것과 호환되게 하는 것이 목적" |
| Constraint: "기존 사용자 호환" | "기존 사용자가계속 쓰고 싶으면 쓰는 것이고, 반드시 써야하는 것은 아니다". 이미 등록된 서버는 그대로 두고 (P2), SC가 넣은 훅을 알아보는 업그레이드 코드는 이번 변경과 무관하다 (P1) |
| Constraint: ".serena 메모리 보존" | ".SERENA 폴더는 남겨둔다는 의미". "지금 있는 serenam/memory른 그냥 둔다". 레포의 `.serena/`와 그 추적 규칙은 그대로 두고, 옮기거나 읽지 않는다 (P4, P10) |

## 인벤토리: Serena를 필수처럼 만드는 지점

`docs/archive/`를 빼면 98개 파일에서 332회 나온다. 동작에 영향을 주는 지점만 아래에 적는다.

1. 메모리 커맨드
   - `commands/save.md:14,17,37,54-55,84,86`과 `commands/load.md:14,29,34-35,60,64,66`은 Serena를 주 저장소로 쓴다
   - Serena가 없을 때의 fallback도 `.serena/memories/*.md`를 직접 쓰고 읽는다 → Serena 없이도 Serena 폴더 레이아웃에 의존
2. "Serena-First" 지시
   - 에이전트 18개의 `<tool_guidance>`: backend-architect, frontend-architect, devops-architect, learning-guide, quality-engineer, python-expert, project-manager, project-initializer, performance-engineer, self-review, security-engineer, requirements-analyst, root-cause-analyst, system-architect, repo-index, refactoring-expert, technical-writer, socratic-mentor
   - 확인: `grep -l "Serena-First" src/superclaude/agents/*.md` → 18
   - 이 지시를 요구하는 레포 규칙: `.claude/rules/agent-authoring.md:157,223-225`
   - 같은 방향의 규칙: `core/rules/RULES_QUALITY.md:17` (R17), `commands/explain.md:52`, `core/PRINCIPLES.md:19`
3. 자동 주입
   - `scripts/context_loader.py:111-112`: `/sc:load`, `/sc:save`, `lsp`, `symbol ops` 같은 키워드가 나오면 `MCP_Serena.md`를 주입
   - 관련 줄: `:200,203,217-222,357`
   - `hooks/mcp_fallback.py:31`과 `utils/__init__.py:421`(`CURRENT_MCP_SERVERS`): Serena가 없을 때 fallback 안내
4. 설치기
   - `cli/install_mcp.py:43-50`이 Serena를 `category: "core"`로 둔다. core 서버는 Serena 하나뿐이다 (`:48`이 유일한 `"category": "core"`)
   - 대화형 설치는 core 서버만 나열하고, 기본 입력 `0`은 "core 전부 설치"다 (`:588-628`) → 기본값으로 Serena가 설치됨
   - `:210-241`: uv와 serena 바이너리를 사전 점검
5. 그 밖의 언급
   - 커맨드: reflect(description, fallback), select-tool, recommend(`--serena`), research, analyze, help, sc, roadmap, brainstorm 예시, `commands/README.md`
   - 규칙: `core/FLAGS.md:19,23`, `RULES_DOCS.md:43`, `RULES_DELEGATION.md:61`
   - 모드와 MCP 문서: `MODE_Orchestration.md:17`, `RESEARCH_CONFIG.md:43`, Tavily·Playwright·DevTools MCP 문서의 frontend-verify 줄, `mcp/README.md:15,55,61`
   - 에이전트: deep-researcher, simplicity-guide
   - 기타: `cli/main.py:968,980`(예시 문자열), `scripts/file_size_guard.py:5`(docstring), `cli/install_settings.py:391`(주석)
6. 레포 개발 환경
   - `AGENTS.md:36`: 세션 메모리 위치를 `.serena/`로 안내
   - `.gitignore:122-123`, `.github/workflows/test.yml:8-9`(`paths-ignore`), `.github/workflows/README.md:5`
   - `.claude/rules/mcp-authoring.md:23,77,99`: 예시로 `serena`를 씀
   - `.claude/rules/agent-authoring.md:40`: `mcpServers: [serena]` 예시
   - 사용자 문서: `README.md` 13곳, `docs/troubleshooting/serena-installation.md`, `SECURITY.md:285`
   - 작업 문서: `docs/PRD.md:56-58`(범위 기록), `docs/reports/PROJECT_INDEX.md:37`(생성된 living doc)
   - 테스트: test_context_loader, test_cli_context, test_install_mcp_prerequisites, test_mcp_fallback, test_install_settings(fixture 데이터로만 사용), test_command_structure, test_cross_directory_refs

## Resolved Decisions

| Q | 질문 | 결정 | Mode |
|---|---|---|---|
| Q1 | /sc:save와 /sc:load의 저장소 | [a] auto memory만 → Q6·Q7로 대체됨 | superseded |
| Q2 | 에이전트 18개와 R17의 Serena-First 지시. 질문 당시 "17개"로 잘못 셌다 | [a] 도구 중립으로 | confirmed |
| Q3 | 설치기(superclaude mcp)의 Serena | [b] 설치기에서 제거 | confirmed |
| Q4 | `--serena` 플래그, MCP_Serena.md, context_loader 주입 | [b] 전부 제거 | confirmed |
| Q5 | 문서화된 플래그는 유지한다는 기존 결정(`fork-unknown-users`)과의 충돌 | [a] 그래도 제거, CHANGELOG에 기록 | confirmed |
| Q6 | 독립 폴더와 auto memory의 관계. 사용자 진술: "'SC:SAVE' , 'SC:LOAD'도 serena폴더가 아니라 독립적인 폴더에 저장하는게 맞아" | [a] 독립 폴더 + auto memory | confirmed |
| Q7 | 독립 폴더의 기억을 git에 커밋하는지 | [a] 커밋함 | confirmed |

메모리 결정의 결과:
- 지금의 dual-persistence 구조는 유지된다. Serena 메모리 자리를 독립 폴더가 대신한다
- 독립 폴더는 커밋되므로 `.serena/memories/`가 하던 기계 간 공유는 유지된다
- auto memory는 프로젝트별로 공유된다 (사용자 진술: "auto memory는 프로젝트별로 공유한다")
- 폴더 위치와 이름은 plan에서 정한다 (Open questions 3)

## Proposed (사용자 결정 아님, review 대상)

- P1 업그레이드 코드는 영향 없음
  - SC가 넣은 훅을 알아보는 코드는 Serena 전용이 아니라 `[superclaude]` 마커 기반이다: `install_settings.py:151-155`, `utils/__init__.py:155-159,199`
  - `install_settings.py`의 Serena 언급은 `:391` 주석 하나뿐이고, `test_install_settings.py:112-120`의 serena는 fixture 데이터다
  - 따라서 남길 Serena 전용 마이그레이션 코드는 없다. fixture 데이터는 그대로 둔다
- P2 등록된 서버는 그대로
  - 사용자가 이미 등록한 Serena MCP 서버를 superclaude가 제거하거나 경고하지 않는다
- P3 fallback 정리
  - `mcp_fallback.py`와 `CURRENT_MCP_SERVERS`에서 `serena`를 뺀다
  - 기존 ledger의 serena 항목은 기존 pruning 로직이 정리한다 (`utils/__init__.py`의 주석: "Hints for anything else are dead weight")
- P4 `.serena/` 그대로
  - `.serena/`, `.gitignore:122-123`, CI `paths-ignore`는 그대로 둔다
  - `.github/workflows/README.md:5`는 폴더가 남으므로 계속 맞는 설명이다. 수정하지 않는다
  - `AGENTS.md:36`은 세션 메모리 위치를 새 독립 폴더로 안내하고, `.serena/`는 "보존된 기록이며 SuperClaude가 더 쓰지 않음"으로 고친다
- P5 레포 규칙 예시 교체
  - `agent-authoring.md`의 Serena-First 절은 Q2 [a]를 따라 도구 중립으로 바꾼다
  - `mcp-authoring.md`와 `agent-authoring.md:40`의 예시 서버명은 남아 있는 다른 서버로 바꾼다
- P6 사용자 문서와 작업 문서
  - `docs/troubleshooting/serena-installation.md`를 삭제한다
  - README와 SECURITY.md의 Serena 항목을 제거한다
  - `docs/PRD.md:56-58`의 "Serena's own CLI stays the user's responsibility"를 고친다 (범위 기록이므로 과거 기록이 아님)
  - `docs/reports/PROJECT_INDEX.md:37`의 `.serena/memories/` 설명을 P4의 `AGENTS.md:36`과 같은 뜻으로 고친다
  - CHANGELOG에 "Serena를 계속 쓰려면 직접 등록"과 `--serena` 제거를 적는다
- P7 과거 기록은 그대로
  - 과거 기록 문서는 수정하지 않는다: `docs/features/*`(이 폴더 제외), `docs/analysis`, `docs/research`, `docs/archive`, `.serena/memories`, `.claude/insights.jsonl`
  - `docs/PRD.md`와 `docs/reports/PROJECT_INDEX.md`는 과거 기록이 아니다 (P6)
- P8 재유입 방지 가드
  - 테스트 하나를 더한다: `src/superclaude/` 아래 `serena` 언급이 0건이어야 한다
  - 허용 목록: `install_settings.py:391` 주석 하나. 주석을 Serena 이름 없이 고치면 허용 목록은 비운다 (plan에서 정함)
  - 근거: 제거 후 다시 들어오는 것을 막는 장치가 없으면 사람이 매번 grep으로 확인해야 함
- P9 카운트 갱신
  - `docs/codex/prompting_session_raw/02_component_and_delivery_map.md:29`의 `mcp/MCP_*.md | 4`를 같은 커밋에서 `3`으로 고친다
  - `.py` 파일이 삭제되면 module 카운트도 갱신한다 (gotcha `codex-module-count-drift`)
- P10 기존 `.serena/memories`는 이전하지 않음
  - "지금 있는 serenam/memory른 그냥 둔다"에 따라 /sc:load는 `.serena/memories/`를 읽지 않고, 내용을 새 폴더로 옮기지도 않는다
  - 새 폴더는 이 변경 이후 /sc:save가 쓴 기억부터 담는다
  - `core/rules/RULES_DOCS.md:43`의 "Serena memory"는 새 폴더로 바꾼다

## Open questions

1. 사용자 로컬 환경
   - 사용자 메모리 기록에 따르면 `~/.claude.json`에 Serena가 전역 등록되어 있고, `~/.claude/settings.json`에 `serena-hooks`가 연결되어 있다
   - 이 상태가 남아 있으면 SuperClaude 변경 후에도 worktree 문제가 계속될 수 있다
   - 로컬 환경은 intent에서 범위 밖이므로 별도로 처리할지 사용자가 정한다
2. Q2의 도구 중립 문구를 정확히 어떻게 쓸지 (R17과 에이전트 18개에 같은 문구를 쓸지)는 plan에서 정한다
3. 설치기의 빈 core 목록
   - Q3로 Serena가 빠지면 core 서버가 0개가 된다 (인벤토리 4)
   - 대화형 `superclaude mcp`는 빈 목록을 보여 주고, 기본 입력 `0`은 아무것도 설치하지 않는다
   - 이 경로를 어떻게 동작시킬지는 plan에서 정한다
4. 독립 폴더의 위치와 이름 (Q6·Q7)
   - 커밋되어야 하므로 흔한 `.gitignore` 규칙에 걸리지 않는 위치여야 한다 (gotcha `gitignore-unanchored-dir`)
   - SuperClaude가 설치되는 사용자 프로젝트 어디서나 같은 경로를 쓰는지도 함께 정한다
   - plan에서 정한다

## 완료 확인 방법

- `grep -ri serena src/superclaude`: P8 허용 목록 외 0건
- `uv run superclaude context explain "/sc:load"`: `MCP_Serena.md` 주입 없음
- `superclaude mcp --list` 서버 목록에 serena 없음
- 대화형 `superclaude mcp`가 Open questions 3에서 정한 대로 동작함
- /sc:save가 독립 폴더와 auto memory에 쓰고, `.serena/`에는 아무것도 쓰지 않음. /sc:load가 두 곳에서 읽음
- `uv run pytest`와 `uv run pytest tests/unit/scripts -o addopts=`가 exit 0
- `make lint` 통과

## Self-Review Iteration Log

v1 → v2 (2026-10-12, /sc:review)
- C1: P1의 전제가 틀렸음. Serena 전용 마이그레이션 코드는 없고, 업그레이드 인식은 `[superclaude]` 마커 기반이다 → P1 재작성, P8 허용 목록을 `install_settings.py:391` 주석으로 바꿈
- C2: Q3로 core 서버 목록이 비는 점이 빠져 있었음 → 인벤토리 4 보강, Open questions 3, 완료 확인에 대화형 설치 항목 추가
- I1: 에이전트 수 17 → 18 (인벤토리 2, Q2, Open questions 2)
- I2: Q1의 trade-off(git 공유 상실, worktree 공유 미확인)와 질문 범위를 기록 → Q1 행 보강, trade-off 블록, Open questions 4
- I3: 작업 문서 `docs/PRD.md:56-58`, `docs/reports/PROJECT_INDEX.md:37`이 빠져 있었음 → 인벤토리 6, P6, P7
- S1: P9를 `02_component_and_delivery_map.md:29`의 4 → 3으로 구체화
- S2: `.github/workflows/README.md:5`를 P4에 명시
- S3(로컬 메모리 `serena-mcp-followups` 정리)는 범위 밖이라 반영하지 않음

v2 → v3 (2026-10-12, 사용자 결정)
- Q1의 목적 정정: "문제를 줄이겠다가 아니라 문제가 있는 MCP를 쓰지 않겠다는 것" → Intent coverage
- Q1 [a] auto memory만 → Q6 [a] 독립 폴더 + auto memory, Q7 [a] 커밋함으로 대체. 기존 Q1 trade-off 블록 삭제 (커밋되는 폴더로 기계 간 공유 유지)
- Open questions 4(auto memory와 worktree)를 사용자 진술 "auto memory는 프로젝트별로 공유한다"로 닫음. 그 자리에 독립 폴더의 위치와 이름을 새로 둠
- "지금 있는 serenam/memory른 그냥 둔다" → P10 추가, P4의 `AGENTS.md:36` 문구 갱신, 완료 확인에 /sc:save·/sc:load 항목 추가
