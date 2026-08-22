---
title: src/superclaude 구성요소와 전달 지도
status: working-guide
last_verified: 2026-08-22
scope: src/superclaude
---

# `src/superclaude` 구성요소와 전달 지도

## 1. 현재 스냅샷

`5b6dc5b` 소스 트리에서 캐시와 README를 제외해 센 결과다. 이 표는 구성요소
인벤토리의 단일 기재 위치이며, 다른 문서는 값을 복사하지 않고 이 절을 가리킨다.
`tests/unit/test_codex_component_map.py`가 소스에서 직접 세어 이 표와 대조한다.

pytest 카운트, coverage, description 문자 수처럼 커밋마다 바뀌는 측정치는 이 표에
두지 않는다. 그 값들은 `08_current_findings_and_backlog.md`가 재측정 명령과 함께
소유한다.

| 요소 | 현재 수 | 역할 |
|---|---:|---|
| `agents/*.md` | 23 | 도메인 전문성, WHO TO BE |
| `commands/*.md` | 36 | `/sc:*` 사용자 workflow, WHAT TO DO |
| `core` always-loaded | 3 | FLAGS, PRINCIPLES, RULES kernel |
| `core/rules/*.md` | 4 | on-demand 상세 규칙 |
| `modes/MODE_*.md` | 7 | 인지 자세, HOW TO THINK |
| `modes/*CONFIG*.md` | 1 | mode 지원 설정 |
| `mcp/MCP_*.md` | 5 | SC workflow에서 MCP를 WHEN/HOW 사용 |
| `skills/*/SKILL.md` | 5 | CC-native capability/reference |
| `templates/docs-scaffold/*` | 4 | `/sc:init` 문서 scaffold |
| distinct hook entry scripts | 10 | `hooks.json`의 14개 등록에서 직접 호출 |
| 전체 Python module | 58 | CLI, hook, 자동화, 공용 경로, plugin |

## 2. 전달과 강제 경계

```text
Session start
  └─ CLAUDE_SC.md
      └─ core/{FLAGS,PRINCIPLES,RULES}.md          always loaded prose

User prompt
  └─ hooks/hooks.json → scripts/context_loader.py
      ├─ modes/*.md                                on-demand full content
      ├─ core/rules/*.md                           on-demand full content
      └─ mcp/*.md                                  tiered context/instruction

Claude Code native discovery
  ├─ commands/*.md                                 /sc:* entry
  ├─ agents/*.md                                   delegation target
  └─ skills/*/SKILL.md                             capability/reference/hooks

Tool lifecycle
  └─ hooks/hooks.json → scripts/*.py               deterministic automation/guards

Installation
  └─ cli/install_*                                 source → user/project/local scope

Derived delivery
  ├─ okf/superclaude                               generated agent catalog
  └─ scripts/build_superclaude_plugin.py           separate plugin artifact path

Evaluation
  ├─ tests/                                        schema, unit, integration
  └─ evals/                                        behavior and regression
```

`core`, `modes`, `agents`, `commands`, 일반 MCP guidance는 모델이 따르는 prose다.
실제 차단을 보장하는 층은 hook, 도구 권한, CLI 검증 같은 코드다. 이 차이를
리뷰에서 혼동하지 않는다.

## 3. 요소별 계약

### `CLAUDE_SC.md`

- 역할: always-loaded core import chain의 진입점.
- 변경 위험: 모든 세션의 context footprint와 기본 행동에 영향.
- 주요 근거: `tests/integration/test_cross_directory_refs.py`의 core import chain.
- 필수 판단: 새 내용이 정말 모든 세션에 필요한가? on-demand module로 내릴 수
  없는가?

### package root와 `ARCHITECTURE.md`

- `__init__.py`: runtime version/header가 참조하는 package metadata.
- `ARCHITECTURE.md`: taxonomy, delivery, enforcement boundary의 사람용 SSOT.
- 위험: `pyproject.toml`, runtime header, README/dispatcher의 version drift 또는
  architecture가 선언한 파생 catalog 경로의 미갱신.
- 검증 초점: `tests/unit/test_version_consistency.py`, source taxonomy와 파생
  catalog/delivery manifest의 양방향 parity.

### `core/`

- `FLAGS.md`: flag와 mode/tool 선택 인터페이스.
- `PRINCIPLES.md`: 안정적인 의사결정 원칙.
- `RULES.md`: 손실 비용이 큰 kernel 규칙.
- `core/rules/`: quality, delegation, docs, interaction의 on-demand detail.
- `BUSINESS_SYMBOLS.md`: supplementary reference.
- 위험: 중복 규칙, always-loaded 비대화, loader wiring 누락, 서로 다른 임계값.
- 검증 초점: import/trigger 전달, 삭제 효과, 행동 slice.

### `modes/`

- 역할: thinking, communication, priorities, behaviors의 네 축으로 자세를 바꿈.
- 전달: `MODE_*.md`는 `context_loader.py`의 `TRIGGER_MAP`/composite flag를 사용한다.
  `RESEARCH_CONFIG.md`는 자동 주입되는 mode가 아니라 research command/mode가
  참조하는 지원 설정이다.
- 금지 경계: workflow 절차, API 설명, tool routing을 mode에 넣지 않음.
- 검증 초점: XML 구조 + trigger 정밀도 + mode가 실제 출력을 구별되게 바꾸는지.

### `agents/`

- 역할: Claude Code가 description을 보고 선택하는 self-contained 전문 agent.
- 전달: CC-native delegation. parent system/skill을 자동 상속한다고 가정하지 않음.
- 설치 변환: source의 `memory: project`가 scope에 맞게 rewrite됨.
- 위험: description overlap, 과거 경험을 암시하는 환각 유발 표현, 과도한 도구,
  잘못된 memory scope, body가 parent를 가정함.
- 검증 초점: frontmatter/XML/description + 선택·반환 행동 + 설치 후 rewrite.

### `commands/`

- 역할: 사용자-facing `/sc:*` workflow.
- 전달: CC-native command/skill surface.
- trigger: read-only cheap workflow는 auto-triggerable일 수 있고, mutation·비용 큰
  workflow는 explicit-only 또는 `disable-model-invocation`을 사용.
- 위험: 명령 이름/description/body 불일치, negative gate 누락, 죽은 handoff,
  산출되지 않는 수치·토큰에 의존하는 flow.
- 검증 초점: 구조 + handoff + invocation contract + 실제 workflow 결과.

### `skills/`

- 역할: hook, invocation blocking, allowed-tools, script execution 또는
  auto-invoked reference knowledge.
- 전달: 디렉터리 전체가 설치되어 `SKILL.md`, scripts, references, assets가 함께
  살아야 함.
- 위험: description budget/trigger, `context: fork` 의존성, script template path,
  side-effect skill의 자동 호출, 배포 artifact 누락.
- 검증 초점: 구조 + canary + hook/script + clean package install.

### `mcp/`

- 역할: 도구 inventory가 아니라 SuperClaude workflow 안에서 서버를 선택하고
  조합하는 기준.
- 전달: `context_loader.py`의 trigger, instruction, composite mapping.
- 위험: 파일만 있고 mapping이 없는 dead content, CC native 설명 중복, setup/version
  침전.
- 검증 초점: XML + mapping completeness + trigger 결과 + fallback.

### `hooks/`, `scripts/`, `utils/`

- `hooks.json`: lifecycle wiring과 timeout/matcher 계약.
- hook scripts: context, formatting, test, insight, size/destructive/loop guard.
- `utils`: project/install scope와 runtime state 경로의 SSOT.
- 위험: hook CWD를 project root로 오인, user/local state 혼합, fail-open guard,
  matcher와 stdin schema drift, async 결과를 완료로 오인.
- 검증 초점: 경로 격리, stdin/output/exit code, atomic state, hook wiring,
  cross-platform behavior.

### `cli/`

- 역할: 설치·제거·목록·doctor·audit·drift와 scope-specific delivery.
- source→target mapping은 `install_paths.py::COMPONENTS`가 소유.
- 위험: source와 wheel의 차이, merge-vs-replace 위반, scope rewrite 오류,
  검증 명령의 false green.
- 검증 초점: 세 scope, 기존 설정 보존, clean artifact install, uninstall,
  exit-status propagation.

### `templates/`

- 역할: 설치된 후 `/sc:init`이 소비하는 중첩 scaffold.
- 위험: top-level `.md` 복사 로직만 통과하고 하위 폴더가 빠짐, placeholder drift.
- 검증 초점: 설치 inventory + init 결과 파일과 내용.

### `pytest_plugin.py`

- 역할: pytest entry point 자동 등록과 경로 기반 marker 부여.
- 위험: source import는 되지만 built distribution entry point가 빠짐.
- 검증 초점: clean wheel 환경에서 `--trace-config`, marker behavior.

### `scripts/auto_improve/`와 `scripts/parallel_ab/`

- 역할: 각각 objective-metric mutation loop와 headless A/B orchestration.
- 위험: 외부 명령 side effect, worktree 오염, budget/timeout 미전파, 실패 결과를
  채택, observation schema drift.
- 검증 초점: 별도 격리 테스트 프로세스, dry-run/smoke, worktree unchanged,
  regression block, 결과 schema.

### 파생 catalog와 plugin artifact

- `okf/superclaude/`: `ARCHITECTURE.md`가 선언한 generated, agent-navigable view.
  source component마다 정확히 하나의 tracked `resource`가 있어야 한다.
- `make build-plugin`/`sync-plugin-repo`: PyPI와 별개인 plugin artifact 경로.
  입력 SSOT, manifest, source payload parity가 명시돼야 한다.
- 위험: source는 갱신됐지만 catalog나 plugin은 stale/missing, ignore pattern이
  generated skill concept까지 숨김, build 명령만 존재하고 입력 manifest는 없음.
- 검증 초점: tracked-file 기준 양방향 inventory, duplicate/missing resource,
  clean plugin build, manifest schema, payload parity, sync 전 nonzero propagation.

## 4. 변경 파급도

| 등급 | 예 | 기본 검증 폭 |
|---|---|---|
| Critical | `CLAUDE_SC.md`, always-loaded core, destructive guard, install paths | 전 게이트 + behavioral/security + distribution |
| High | context loader, hooks.json, command/agent/skill trigger, settings merge | 구조·unit·integration·behavior |
| Medium | 단일 on-demand component body, MCP workflow doc, template | 대상 구조·wiring·narrow behavior |
| Low | source README, 이 디렉터리의 guide | 링크·사실 대조; 실행 테스트는 내용에 따라 선택 |

## 5. 권위 있는 저장소 문서

- taxonomy와 delivery: `src/superclaude/ARCHITECTURE.md`
- 공통 콘텐츠 품질: `.claude/rules/content-quality.md`
- 형식: `.claude/rules/xml-prose-format.md`
- 타입별 저작: `.claude/rules/{agent,command,skill,mode,mcp}-authoring.md`
- enum SSOT: `.claude/rules/schemas.yaml`
- hook/runtime 함정: `.claude/rules/gotchas/hooks.md`
- 설치 경로: `src/superclaude/cli/install_paths.py`
- hook wiring: `src/superclaude/hooks/hooks.json`
- 행동 평가: `evals/README.md`, `evals/tasks.yaml`

이 가이드는 위 문서의 내용을 복제해 새 SSOT를 만들지 않는다.
