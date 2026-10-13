---
status: draft
revised: 2026-10-13
---

# `sc-author` 스킬 Implementation Plan

**Goal:** SuperClaude 사용자 프로젝트에서 `/sc-author`로 Claude가 읽는 지시·컨텍스트 문서를 형식에 맞추고 no-op 문장을 걷어내며, 결과를 `superclaude author-check`로 기계 검사한다.
**Architecture:** 검사기는 패키지 안 click 명령(`cli/author_check.py`)이고 규칙 데이터는 스킬 참고 파일 `fields.yaml` 한 원본을 읽는다. 스킬은 새 디렉터리 컴포넌트 `skills`로 설치된다. `templates`의 copytree 분기를 디렉터리 컴포넌트 공통 분기로 일반화해 install·uninstall·git-exclude·verify-drift·inventory가 같은 경로를 탄다. 스킬 본문은 절차만 담고 판단 기준은 `references/`에 사용자 프로젝트용으로 독립 작성한다(D10).
**Tech Stack:** Python 3.10+ (click, PyYAML), pytest, ruff, Markdown 콘텐츠, `evals/run_eval.py`(로컬 `claude -p`).

입력: [04-design.md](./04-design.md), [04a-design-checker.md](./04a-design-checker.md), [04b-design-common-pass.md](./04b-design-common-pass.md), [03-analysis.md](./03-analysis.md), [00-intent.md](./00-intent.md). 줄 번호는 `feature/authoring-skill` `4a379a32` 기준이다. 앞 phase의 편집으로 밀릴 수 있으니 각 task는 grep으로 위치를 다시 잡는다.

## Shared rules

- 브랜치: `feature/authoring-skill` (worktree `.claude/worktrees/authoring-skill`). 첫 커밋은 이 plan 문서와 README 갱신
- 매 phase 끝: `uv run pytest` exit 0, `make format` 후 `make lint` exit 0, 그다음 커밋. `src/superclaude/scripts/`는 건드리지 않는다 (건드리게 되면 `uv run pytest tests/unit/scripts -o addopts=`도)
- `src/superclaude/` 아래 `.py`를 더하는 phase는 같은 커밋에서 `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` §1 "전체 Python module" 행을 다시 센다: `uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"` (gotcha `codex-module-count-drift`)
- 배포 콘텐츠(SKILL.md, references)는 영어로 쓴다 (04-design C2: 배포 콘텐츠는 언어 중립)
- 배포 콘텐츠는 저장소 파일을 링크하지 않는다 (gotcha `install-tree-boundary`). 저장소 `.claude/rules/`는 고치지 않고 import하지 않는다 (D10). 예외: C6에서 정한 `skill-authoring.md` 신설, `agent-authoring.md:112` 문구, `schemas.yaml` 주석
- 배포 콘텐츠는 저장소 rules의 형식(압축 문체, 섹션 순서, 골격)과 내용을 옮기지 않는다. 기준은 설치된 각 프로젝트 (D18–D20)
- `tests/unit/test_shipped_content_server_neutral.py`의 금지어(`serena`, `write_memory`, `read_memory`, `list_memories`, `find_symbol`, `get_symbols_overview`, `find_referencing_symbols`)는 references 예시에도 쓰지 않는다. N2 예시의 MCP 도구 이름은 `mcp__example__lookup` 같은 가상 이름으로
- 외부 문서 조회(D12)는 구현 시점에 다시 하고, 조회일을 `sources`에 남긴다. 기억한 값으로 필드 목록을 채우지 않는다

## §9 미결 해소 (plan에서 확인)

- PowerShell 허용 규칙 문법: `PowerShell(superclaude author-check *)`. 근거: `code.claude.com/docs/en/permissions` "PowerShell" 절, "PowerShell permission rules use the same shape as Bash rules" (2026-10-13 조회). SKILL.md `allowed-tools`에 `Bash(superclaude author-check *)`와 함께 둔다
- Fable 5.1 가이드 URL: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1` (2026-10-13 조회, 제목 "Prompting Claude Fable 5.1"). Opus 5.5·Sonnet 5.5와 같은 경로 형식

## 구현 시작 결정 (2026-10-13)

`/sc:implement` 호출 시 사용자: "참조하는 rules파일들의 formatter와 내용을 그냥 가져오면 안된다. rules파일들은 이 프로젝트에 종속된 파일들이고 만들고자하는 것은 설치되는 각각의 프로젝트를 기준으로 맥락이 맞게 생성시키는 것이다"

| # | 결정 | 바뀌는 곳 |
|---|---|---|
| D18 | `--xml` 검사는 어떤 XML 본문에도 성립하는 구조 규칙만: X1(루트 하나), X2(태그 짝), X7(output-style 제외). X3–X6(snake_case, 4단 깊이, `<example>` 밖 헤더, `<should>`·`<avoid>`)은 이 저장소 `xml-prose-format.md`의 관례라 삭제. 태그 이름·깊이·섹션은 대상 프로젝트의 기존 문서를 따름 (사용자 선택 "구조 규칙만") | 04a 규칙표, 05a, 05d `format-xml.md` |
| D19 | 프로젝트 관례 우선: Load 단계에서 같은 유형의 기존 문서 1–2개와 load-set 문서를 읽고 언어·용어·헤딩/태그 모양·섹션 구성을 맞춤. references 템플릿은 프로젝트에 같은 유형 문서가 없을 때만 (사용자 선택 "프로젝트 관례 우선") | 04-design C2 3·4단계, 05d 템플릿 절, 05e |
| D20 | references의 출처는 외부 문서(`sources`)와 이 설계의 결정뿐. 저장소 rules(`content-quality.md`, `xml-prose-format.md`, `*-authoring.md`, core rules)의 절 구성·문체·용어를 옮기지 않음. SuperClaude 고유 어휘(`/sc:` 명령, `<component>`·`<handoff>` 골격, R 코드, `RULES_*`, `CLAUDE_SC`)가 배포 references에 없음을 테스트로 고정. `skill-authoring.md`의 "rules를 바꾸면 references도 확인" 동기화 줄은 삭제 (rules가 references의 원본이 아님) | 04-design C3 `quality.md` 행·C6 첫 행, 05d, 05f |

## Phases

- [x] Phase A: [05a-plan-checker-core.md](./05a-plan-checker-core.md) — `fields.yaml`, `author-check` 인터페이스·유형/형식 추론·F/R/S/X 규칙, XML 회귀 말뭉치
- [x] Phase B: [05b-plan-checker-noop.md](./05b-plan-checker-noop.md) — `--with`와 N1–N4, N 규칙 말뭉치
- [ ] Phase C: [05c-plan-skills-component.md](./05c-plan-skills-component.md) — `skills` 디렉터리 컴포넌트: install, uninstall, git-exclude, verify-drift, inventory
- [ ] Phase D: [05d-plan-references.md](./05d-plan-references.md) — 유형 참고 5개, `format-xml.md`, `quality.md` + 최신성·예시 개수 테스트
- [ ] Phase E: [05e-plan-skill-body.md](./05e-plan-skill-body.md) — `SKILL.md` + 구조 테스트 + 자기 검사
- [ ] Phase F: [05f-plan-repo-docs.md](./05f-plan-repo-docs.md) — C6 저장소 쪽 변경과 README
- [ ] Phase G: [05g-plan-probes.md](./05g-plan-probes.md) — `evals/tasks.yaml` 효과·명시 호출 프로브와 실행 기록

순서 근거:
- A가 `src/superclaude/skills/sc-author/`를 처음 만든다 (`fields.yaml`). C의 `COMPONENTS["skills"]`는 소스 디렉터리가 있어야 `tests/integration/test_cross_directory_refs.py:164` 가 green
- B를 A와 나눈 이유: 규칙 16개 + N 4개를 한 커밋에 넣으면 리뷰 단위가 너무 큼. N은 `--with`라는 별도 인터페이스를 더함
- D가 E보다 먼저: SKILL.md가 링크하는 참고 파일이 없으면 자기 검사가 R1 error
- C–D 사이 커밋에서는 설치본에 `skills/sc-author/references/fields.yaml`만 들어간다. 브랜치 안의 중간 상태이고 릴리스되지 않는다
- G는 설치된 스킬 전체가 있어야 의미가 있으므로 마지막

## Risks

- 가장 위험한 단계: Phase C. 모든 사용자의 install·uninstall·verify-drift 경로를 바꾸고, 처음으로 Claude Code의 공유 디렉터리 `.claude/skills/`에 쓴다. uninstall이 `sc-author` 말고 다른 스킬을 지우면 사용자 데이터 손실이다. 제3자 스킬을 심어 둔 테스트가 install·uninstall·drift 세 경로 모두를 고정한다
- verify-drift가 디렉터리 컴포넌트를 재귀 비교하면서 지금까지 검사하지 않던 `templates/`도 검사하게 된다. 기존 설치에서 새로 MISSING·DRIFTED 줄이 보일 수 있다. 이는 올바른 보고이고, `verify-drift` 도움말과 모듈 docstring의 "Not checked: templates/"를 같은 커밋에서 고친다
- X 규칙 오탐: 사용자 문서의 산문 속 `<3`, `<5KB` 등. A의 회귀 말뭉치(배포되는 agents·commands 전체)가 막는다. 말뭉치에서 진짜 위반이 나오면 콘텐츠는 고치지 않고(범위 밖) `## Deviations`에 기록한다
- `fields.yaml`은 Claude Code 문서가 바뀌면 낡는다. 미등록 필드는 F4 warning이라 새 필드를 막지는 않는다. 최신성 테스트(D)는 모델 ID 집합만 강제하고 CC 필드 변경은 강제하지 않는다 (04-design §8 수용)
- 업그레이드: `--force` 없는 `superclaude install`은 기존 `skills/sc-author/`를 건너뛴다 (templates와 같은 규칙). 낡은 사본은 verify-drift가 DRIFTED로 보여 준다
- 스킬의 Check 단계는 `superclaude`가 PATH에 있어야 한다. 없으면 SKILL.md가 "기계 검사 안 함"이라고 Hand-off에 쓰게 한다. 하지 않은 확인을 했다고 말하는 것이 03 §3.4의 해로움이다
- 이 브랜치는 core 변경 `ba88edd3`(RULES_DOCS size)을 이미 담고 있다. 이 plan의 범위는 아니지만 릴리스 전에 `make canary-gates`가 필요하다 (AGENTS.md)

## Alternatives not taken

- 검사기를 스킬 디렉터리의 `scripts/check.py`로 배포: 설치본에는 패키지가 없어 `superclaude.*` import가 깨진다 (gotcha `script-needs-console-entry`). 콘솔 하위 명령이 이 저장소의 정해진 방식
- `skills` 전용 분기를 `templates` 분기 옆에 복사: 같은 모양(하위 디렉터리 단위 복사)의 코드가 다섯 모듈에 두 벌씩 생긴다. `DIRECTORY_COMPONENTS` 하나로 일반화
- verify-drift에서 `templates`를 계속 제외: 디렉터리 컴포넌트 안에서 다시 분기가 필요하고, 설치된 템플릿의 drift가 계속 안 보인다
- 검사기 규칙을 한 phase에: 위 순서 근거
- 효과 프로브를 기본 4-arm 행렬에: vanilla 등 다른 arm에는 스킬이 없어 비교 의미가 없다. `canary_only` 선례(`implement-checkpoint`)를 따른다 (05g)
- CHANGELOG를 이 브랜치에서 갱신: CHANGELOG는 version-bump 커밋에서만 바뀐다 (`tests/unit/test_version_consistency.py`가 맨 위 release 제목을 pyproject 버전과 맞춤). 아래 Release note를 그 커밋이 쓴다

## Proof

1. `uv run pytest` → exit 0. `make lint` → exit 0
2. `uv run superclaude author-check src/superclaude/skills/sc-author/SKILL.md` → 마지막 줄 `0 errors, N warnings`, exit 0
3. references마다 `uv run superclaude author-check src/superclaude/skills/sc-author/references/<file>.md --type generic` → exit 0
4. 임시 프로젝트에서 설치 확인 (`superclaude.__file__`이 이 worktree를 가리키는지 먼저 확인, gotcha `venv-inherited-by-worktree`)
   - `git init` + `.claude/skills/other/SKILL.md` 심기 → `superclaude install --scope local --force` → `.claude/skills/sc-author/SKILL.md` 존재, `.git/info/exclude`에 `.claude/skills/sc-author/` 한 줄
   - `superclaude verify-drift --scope local` → exit 0, `skills` 행 OK
   - `superclaude uninstall --scope local` → `.claude/skills/sc-author/` 없음, `.claude/skills/other/SKILL.md` 남음
5. `uv run python evals/run_eval.py --canary --task sc-author-skill --task sc-author-plain` → `sc-author-skill`의 `author-check` 확인 통과, `sc-author-plain`의 `author-check` 미실행 확인 통과. 결과는 05g "Results"에 기록
6. (사용자, Claude Code 재시작 후) 실제 세션에서 `/sc-author agent <설명>` 한 번 → Resolve 한 줄, Load-set 한 줄, 같은 유형 기존 문서를 읽음(있으면, D19), diff 승인 요청, `author-check` 실행이 보임

## Release note (다음 version-bump 커밋의 CHANGELOG `### Added`)

- `/sc-author` skill: write or revise any file Claude reads as instructions (skills, subagents, slash commands, output styles, CLAUDE.md, AGENTS.md, `.claude/rules`, and other instruction docs). It reformats the body (`--md` default, `--xml` for XML bodies), proposes no-op and harmful sentences for removal with evidence, and asks before writing. User-invoked only.
- `superclaude author-check <path>`: validates frontmatter fields, references, XML structure and broken pointers in such files. Exit 1 on errors.
- Installs now include a `skills` component (`.claude/skills/sc-author/`). Uninstall removes only that directory; other skills stay. `verify-drift` now also checks installed templates.
