---
title: 런타임·설치·배포 개선 플레이북
status: working-guide
last_verified: 2026-08-22
applies_to:
  - src/superclaude/cli
  - src/superclaude/hooks
  - src/superclaude/scripts
  - src/superclaude/utils
  - src/superclaude/templates
  - src/superclaude/pytest_plugin.py
---

# 런타임·설치·배포 개선 플레이북

## 1. 책임 경계

```text
Prose policy
  intent / scope / priorities / uncertainty / success semantics

Runtime mechanism
  path / permission / block / timeout / retry / state / install / exit status
```

금지·보존·권한 같은 중요한 invariant를 문장에만 두지 않는다. 코드로 강제할 수
있는 것은 hook, tool boundary, CLI validator, artifact test로 옮긴다.

## 2. 설치 파이프라인

```text
source tree
  ├─ install_paths.COMPONENTS
  ├─ install_components
  │   ├─ content copy
  │   ├─ agent memory scope rewrite
  │   ├─ skill template substitution
  │   └─ templates nested copy
  ├─ hooks/scripts copy + placeholder resolution
  ├─ settings hook merge
  ├─ CLAUDE_SC import activation
  └─ scope-specific git exclude
        ↓
user | project | local installed tree
        ↓
Claude Code runtime
```

검증은 source tree에서 끝나면 안 된다. 최소 세 상태를 비교한다.

1. source inventory
2. built wheel/sdist inventory
3. clean environment에 설치된 inventory와 활성화 상태

## 3. Scope 계약

| scope | base | 공유 의도 | 주의점 |
|---|---|---|---|
| user | `~/.claude` | 사용자 전역 | 다른 프로젝트와 runtime state가 섞이지 않게 project key 필요 |
| project | `./.claude` | git으로 팀 공유 | team-owned 설정과 content |
| local | `./.claude` | 개인·gitignored | `CLAUDE.local.md`, `.git/info/exclude`, local memory |

CLI code의 CWD는 사용자가 설치 대상을 선택한 위치이므로 유효하다. hook code의
CWD는 project root라고 보장되지 않으므로 `superclaude.utils` resolver를 사용한다.
이 둘을 일괄 치환하지 않는다.

## 4. Runtime state 계약

| 상태 | 위치 | 수명 | uninstall |
|---|---|---|---|
| context cache, tracker, loop counter, fallback ledger | `hook_state_dir()` | 재생성 가능 | 제거 가능 |
| insight 등 사용자 소유 project data | `project_root()/.claude` | durable | 보존 |

새 writer를 추가할 때 다음을 결정한다.

- ephemeral인가 durable인가?
- session keyed인가 project keyed인가?
- atomic write가 필요한가?
- 두 창·두 프로젝트 동시 실행에서 충돌하지 않는가?
- stale state pruning과 uninstall이 소유하는가?

## 5. Hook 개선 절차

1. `hooks.json` event, matcher, timeout, async/once 의미를 정한다.
2. canonical stdin fixture와 malformed fixture를 만든다.
3. approve/block/ask/error의 exit code와 JSON schema를 고정한다.
4. project/local scope에서 real user home을 오염하지 않는지 검사한다.
5. source script와 설치된 command path를 모두 실행한다.
6. safety hook은 adversarial corpus로 fail-open/fail-closed 정책을 확인한다.
7. hook이 제거·rename되면 settings merge와 uninstall ownership을 검증한다.

현재 기계적으로 차단하는 핵심 guard는 file size, destructive command, repeated
failure circuit breaker다. formatter와 auto-test는 자동화이지만 동일한 보안
보장을 제공하는 차단층으로 간주하지 않는다.

## 6. CLI 개선 절차

### Hard gates

- 부분 실패가 process nonzero로 전파된다.
- user/project/local target이 정확하다.
- 기존 사용자 hook/settings/MCP를 보존한다.
- install/update가 idempotent다.
- uninstall은 SC-owned artifact만 제거한다.
- secret과 credential이 stdout/stderr/dry-run에 나타나지 않는다.
- source가 아니라 clean built artifact에서도 같은 결과가 난다.

### Targeted tests

```bash
uv run pytest tests/unit/test_cli_install.py -v
uv run pytest tests/unit/test_install_settings.py -v
uv run pytest tests/unit/test_install_interactive.py -v
uv run pytest tests/unit/test_install_git_exclude.py -v
uv run pytest tests/unit/test_verify_drift.py -v
uv run pytest tests/unit/test_scope_paths.py -v
```

`make verify`와 `make test-plugin`은 현재 내부 실패를 nonzero로 보장하지 않으므로
릴리스 hard gate로 사용하지 않는다. 직접 명령의 exit code를 확인한다.

## 7. Clean artifact gate

다음 검사는 editable install을 사용하지 않는다.

```bash
artifact_dir=$(mktemp -d /tmp/superclaude-release.XXXXXX)
uv build --out-dir "$artifact_dir"
unzip -l "$artifact_dir"/*.whl
tar -tzf "$artifact_dir"/*.tar.gz
```

source manifest와 artifact manifest를 exact 또는 명시적 allowlist로 비교한다.
필수 payload는 다음과 같다.

- CLI/hooks/utils Python modules와 entry points
- `CLAUDE_SC.md`
- commands, agents, core, modes, MCP docs
- skill별 `SKILL.md`, canary, scripts, references, assets
- template 하위 파일 전체
- `auto_improve`, `parallel_ab` subpackages

그 다음 repo 밖의 임시 CWD에서 wheel만 설치해 다음을 확인한다.

```bash
wheel_path=$(find "$artifact_dir" -maxdepth 1 -name '*.whl' -print -quit)
runtime_dir="$artifact_dir/runtime"
mkdir "$runtime_dir"
cd "$runtime_dir"
uv run --isolated --no-project --with "$wheel_path" superclaude --version
uv run --isolated --no-project --with "$wheel_path" \
  superclaude install --force --scope project
uv run --isolated --no-project --with "$wheel_path" \
  superclaude install --list-all --scope project
printf '%s\n' \
  'def test_plugin_loaded(pytestconfig):' \
  '    assert pytestconfig.pluginmanager.hasplugin("superclaude")' \
  > test_plugin_probe.py
uv run --isolated --no-project --with "$wheel_path" \
  pytest --trace-config -q test_plugin_probe.py
```

`--isolated`, `--no-project`, built wheel 경로를 모두 고정한다. 그렇지 않으면
editable source나 현재 project dependency가 검사를 오염할 수 있다. User scope를
검사할 때는 real user home을 쓰지 않고 별도의 격리 fixture를 사용한다.

현재 build artifact에서는 `skills/`가 전부 누락되는 것이 재현되었다. 자세한
증거는 `08_current_findings_and_backlog.md`의 `F-001`에 있다.

### 다른 파생 전달 경로

PyPI wheel/sdist만 검사해 distribution parity를 완료로 판정하지 않는다.

| 경로 | 입력 계약 | 필수 gate |
|---|---|---|
| `okf/superclaude/` | `src/superclaude` content taxonomy | tracked resource exact parity, unique pointer, index count |
| `make build-plugin` | 선언된 plugin source/manifest + unified source payload | clean build, manifest schema, agents/commands/hooks/scripts/skills inventory |
| `make sync-plugin-repo` | 검증된 plugin artifact | build 성공 선행, target 확인, sync 후 exact parity |

현재 OKF의 skill concept는 작업 트리에는 6개가 있지만 `.gitignore`의 광범위한
`skills/` 패턴 때문에 tracked catalog에는 0개다. 또한 plugin builder가 요구하는
`plugins/superclaude/manifest/metadata.json`이 없어 `make build-plugin`이 실패한다.
둘 다 별도 current finding이며, 경로를 유지할지 폐기할지 결정하기 전에는 release
gate에서 조용히 제외하지 않는다.

## 8. Drift와 audit의 의미

현재 `verify-drift`는 component Markdown, skill manifest, `CLAUDE_SC.md`를
비교한다. templates, installed scripts, transformed/merged hooks, skill supporting
files는 범위 밖이다. 따라서 `clean`은 전체 runtime parity가 아니라 해당 범위의
clean이다.

릴리스 gate에서는 별도의 inventory/parity 검사를 추가하고, CLI 출력에 coverage
boundary를 유지한다.

## 9. `templates/`

템플릿은 설치 component이자 생성 contract다. 파일 존재만 검사하지 않는다.

| template | 필수 의미 |
|---|---|
| PRD | intent, scope/out-of-scope, constraints, observable success |
| ARCHITECTURE | boundary, invariant, data/control flow, operational concerns |
| ADR | status, decision, alternatives, consequences |
| UI-GUIDE | tokens/components/states/accessibility 또는 명시적 비적용 |

검증은 source → install → `/sc:init` 생성물의 세 단계에서 unresolved placeholder,
destination, 필수 section을 검사한다.

```bash
uv run pytest tests/unit/test_init_docs_scaffold.py -v
```

## 10. `pytest_plugin.py`

source import만으로 entry point를 검증하지 않는다. clean wheel 환경에서:

- `uv run pytest --trace-config`에 `superclaude`가 실제 등록된다.
- unit/integration/hallucination/performance marker가 예상 item에 붙는다.
- plugin이 없는 환경과 비교해 collection을 깨지 않는다.
- package version header가 distribution version과 일치한다.

## 11. `auto_improve`와 `parallel_ab`

### `auto_improve`

- metric command는 외부 side effect를 일으킬 수 있으므로 명시적 사용자 권한이
  필요하다.
- mutator가 tests/eval을 바꿔 metric을 조작하지 못하도록 scope를 코드로 강제한다.
- eval process nonzero, timeout, missing metric, commit failure는 candidate reject다.
- main worktree unchanged와 accepted lineage를 검사한다.

### `parallel_ab`

- artifact 생성은 품질 판정이 아니다.
- runner observation의 correctness axes가 실제 평가로 채워지는지 확인한다.
- fastest passing variant 선택만으로 prompt 품질 승자를 선언하지 않는다.
- 동일 task/model/settings와 evaluator rubric을 고정한다.

별도 격리 suite:

```bash
make test-scripts
uv run pytest tests/integration/test_parallel_ab_e2e.py -v
uv run pytest tests/integration/auto_improve/test_e2e_smoke.py -v
```

실제 CLI/model 실행은 인증·비용이 필요한 조건부 gate로 구분한다.

## 12. Security outcome

보안 검증은 다음 순서를 사용한다.

```text
untrusted input
→ requested capability
→ source/sink/resource scope
→ hook/permission decision
→ actual observed side effect
```

“prompt injection을 감지했다”고 말하는 것은 통과 증거가 아니다. 비밀 파일을
읽거나 외부로 쓰거나 production mutation을 수행했다면 즉시 실패다.
