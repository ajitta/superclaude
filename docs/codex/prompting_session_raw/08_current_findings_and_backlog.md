---
title: 현재 검증 사각지대와 개선 백로그
status: verified-snapshot
last_verified: 2026-08-22
measured_at: 5b6dc5b
scope: repository-wide evidence relevant to src/superclaude
---

# 현재 검증 사각지대와 개선 백로그

이 문서는 직접 재현했거나 source/test를 대조해 확인한 사실을 기록한다. 결함 자체는
수정하지 않는다. 상태가 바뀌면 증거와 함께 항목을 갱신한다.

커밋마다 바뀌는 측정치(pytest 카운트, coverage, description 문자 수, format 대상,
mypy 오류, OKF 카운트)는 이 문서가 소유한다. 값은 재측정 명령과 마지막 관측 커밋을
함께 적는다. `git log <SHA>..HEAD -- src/`가 비어 있지 않으면 값을 재측정한다.
구성요소 인벤토리는 여기 두지 않고
[`02_component_and_delivery_map.md`](02_component_and_delivery_map.md) §1이 소유한다.

## 요약

| ID | 우선순위 | 판정 | 내용 |
|---|---|---|---|
| F-001 | P0 | FAIL | wheel/sdist에서 `skills/` 전체 누락 |
| F-002 | P0 | FAIL | `make verify`, `make test-plugin` false-green 가능 |
| F-003 | P0 | FIXED | 핵심 활성화 실패가 install 성공값에 반영되지 않음 — `f25d91a`/`e360ca5`에서 해결, §해결된 finding 참조 |
| F-004 | P1 | REVISE | drift/audit가 runtime payload 일부를 의도적으로 제외 |
| F-005 | P1 | FAIL | skill authoring guide와 validator 정책 충돌 |
| F-006 | P1 | REVISE | 기본 pytest가 script suite와 canary를 제외 |
| F-007 | P1 | REVISE | core/template/graph semantic gate 공백 |
| F-008 | P1 | REVISE | model-facing description registry가 문서상 fallback budget 초과 |
| F-009 | P1 | FAIL | 전체 ruff format check baseline이 green이 아님 |
| F-010 | P1 | REVISE | auto-improve/parallel_ab가 품질·scope를 완전히 강제하지 않음 |
| F-011 | P1 | REVISE | MCP installer·doctor·pytest plugin의 직접 검증 공백 |
| F-012 | P1 | FAIL | publish workflow가 full gate와 artifact 기능 검사를 선행하지 않음 |
| F-013 | P2 | REVISE | testing 문서와 실제 UV/pytest 구성이 drift |
| F-014 | P2 | REVISE | coverage/mypy가 선언적 기대와 실행 가능한 gate로 정렬되지 않음 |
| F-015 | P1 | FAIL | tracked OKF catalog에서 skill concept 5개 누락 |
| F-016 | P1 | FAIL | plugin build 경로의 입력 manifest/source가 없어 실행 불가 |

## F-001 — 배포 artifact에서 skills 누락

**등급:** `[REPO]` · P0 · DIST/B15

재현:

```bash
artifact_dir=$(mktemp -d /tmp/superclaude-doc-audit.XXXXXX)
uv build --out-dir "$artifact_dir"
unzip -l "$artifact_dir"/*.whl | rg 'superclaude/skills/'
tar -tzf "$artifact_dir"/*.tar.gz | rg '/src/superclaude/skills/'
```

결과: 두 검색 모두 0개. 다른 주요 component와 templates는 wheel에 존재했다.

관련 근거:

- `pyproject.toml:73-83` build target
- `.gitignore:114`의 `skills/` 패턴
- `install_paths.py::COMPONENTS`는 skills를 필수 component로 등록

영향: source/editable 환경 테스트가 green이어도 배포 패키지에서 전체 설치와
packaged skill 설치가 실패할 수 있다.

완료 gate:

- wheel/sdist source manifest parity test 추가
- clean wheel install 후 5개 skill과 supporting files 확인
- release workflow가 payload 누락에서 nonzero

## F-002 — Make 검증 타깃 false green

**등급:** `[REPO]` · P0 · TOOL

`Makefile:61-63`, `71-88`의 검사 분기는 실패 시 `echo`를 실행하고 recipe 마지막도
성공 `echo`로 끝난다. 따라서 화면에 `❌`가 있어도 make target exit status는 0일
수 있다.

완료 gate:

- 내부 command failure가 target nonzero로 전파됨
- 의도적으로 plugin/doctor를 실패시키는 meta-test
- 성공 메시지는 모든 하위 검사 통과 후에만 출력

## F-004 — drift/audit coverage boundary

**등급:** `[REPO]` · P1 · DIST

`verify_drift.py:7-10`은 templates, installed scripts, merged hooks를 명시적으로
제외한다. Skill도 `SKILL.md` manifest 외 scripts/references/assets는 비교하지 않는다.

이것은 현재 명시된 기능 경계지만, 전체 runtime release gate로는 불충분하다.
`verify-drift clean`을 “설치된 모든 실행 payload가 source와 동일함”으로 해석하지
않고 별도 artifact/runtime parity gate를 둔다.

## F-005 — skill 저작 규칙과 테스트 충돌

**등급:** `[REPO]` · P1 · SPEC/EVAL

`.claude/rules/skill-authoring.md:89-95,142-145`는 `model`, `context: fork`,
`agent`를 합법 필드로 설명한다. 반면:

- `tests/unit/test_skill_structure.py:163-168`은 `model`을 금지
- 같은 파일 `184-196`은 모든 `context: fork`와 `agent`를 금지

현재 shipped skill에 이 필드가 없어 suite는 green이지만, 문서대로 새 skill을
작성하면 validator가 실패한다.

완료 gate: archetype/field policy를 machine-readable SSOT로 만들고 guide, parser,
tests가 같은 schema를 소비한다.

## F-006 — 기본 green의 coverage 경계

**등급:** `[REPO]` · P1 · EVAL

재측정 명령과 마지막 관측:

```text
uv run pytest -q
→ 2279 passed, 28 skipped, 4 deselected   @5b6dc5b

make test-scripts
→ 120 passed                              @a358bcb

uv run python evals/run_eval.py --dry-run
→ 4 arms × 7 tasks, 28 workspace build 성공  @a358bcb
```

`pyproject.toml:98-107`은 `tests/unit/scripts`와 `canary`를 기본 제외한다. 실제
model/CLI가 필요한 canary와 parallel A/B E2E도 조건 없이 전체 green에 포함되지
않는다.

완료 gate: release job이 default, isolated scripts, conditional behavioral gate를
각각 명시하고 skipped/not-run을 보고한다.

## F-007 — semantic graph와 authoring coverage 공백

**등급:** `[REPO]` · P1 · SPEC/CONTEXT/EVAL

확인된 공백:

- `core/`는 전용 authoring/structural test가 없음
- `RESEARCH_CONFIG.md`는 mode structure fixture 밖에 있음
- template taxonomy/authoring guide와 UI-GUIDE acceptance가 없음
- cross-reference 수집은 commands/agents/modes 중심이며 skills/MCP edge를 빠뜨림
- agent trigger uniqueness 검사가 없음. `tests/unit/test_agent_structure.py`의
  `test_description_has_cc_idiom_trigger`는 delegation trigger 문장의 존재만 확인하며,
  인접 agent 사이의 trigger 중복은 어떤 테스트도 보지 않음
- structure test 다수는 full YAML/XML semantic parser가 아닌 line/regex 기반

완료 gate: component catalog graph를 한 번 생성해 filename, schema, README,
loader, installer, handoff, reference의 양방향 parity를 검증한다.

## F-008 — model-facing description budget

**등급:** `[REPO]` 측정 + `[HYPOTHESIS]` 영향 · P1 · CONTEXT/B12

YAML로 description을 파싱한 문자 수 (마지막 관측 `@5b6dc5b`):

```text
commands: 11,594
skills:    1,831
total:    13,425
```

재현 시 Markdown 본문에서 `description:` 문자열을 검색하지 않고 각 파일의 YAML
frontmatter를 parser로 읽는다. 대상은 README를 제외한 `commands/*.md`와
`skills/*/SKILL.md`다.

`.claude/rules/skill-authoring.md`는 전체 skill/command description 예산을 context의
1%, fallback 약 8,000자로 설명한다. 실제 예산은 runtime/context에 따라 달라질 수
있으므로 현재 수치만으로 잘림을 단정하지 않는다. 그러나 뒤쪽 custom description이
silent truncation될 위험은 측정해야 한다.

완료 gate:

- installed registry의 실제 노출 길이 측정
- 각 description first-200 핵심 trigger 확인
- positive/negative trigger canary
- budget 초과 시 low-value duplicate description 압축

## F-009 — formatting baseline

**등급:** `[REPO]` · P1 · TOOL

재측정 명령과 마지막 관측 `@5b6dc5b`:

```text
uv run ruff check .
→ pass

uv run ruff format --check .
→ exit 1; 10 files would be reformatted, 104 files already formatted
```

재포맷 대상:

```text
src/superclaude/cli/install_inventory.py
src/superclaude/scripts/context_loader.py
src/superclaude/scripts/insight_writer.py
tests/integration/test_readonly_session_is_quiet.py
tests/unit/test_cli_install.py
tests/unit/test_context_loader.py
tests/unit/test_insight_writer.py
tests/unit/test_install_git_exclude.py
tests/unit/test_install_interactive.py
tests/unit/test_install_settings.py
```

목록의 성격이 바뀐 점에 주의한다. `a358bcb` 시점에는 테스트 파일 3개뿐이었으나 지금은
배포되는 `src/` 모듈 3개가 포함된다. 수치 증가가 아니라 상태 변화이며, 릴리스 hard
gate로 전체 format check를 요구하려면 baseline을 별도 변경으로 정리한다.

## F-010 — 자동 개선/A-B 의미론 공백

**등급:** `[REPO]` · P1 · TOOL/EVAL

`auto_improve`:

- scope glob은 filesystem enforcement가 아니라 prompt advisory
  (`coordinator.py:51-54`)
- candidate eval은 timeout과 scalar regression을 보지만 nonzero exit 자체를
  명시적으로 reject하지 않음 (`185-222`)
- commit subprocess return code를 확인하지 않음 (`263-283`)
- mutator가 tests/eval을 바꿔 metric을 올리는 것을 hard gate로 막지 않음

`parallel_ab`:

- output parser가 quality axes를 채울 evaluator를 제공하지 않음
  (`runner.py:98-120,177-189`)
- aggregator는 `exit_status == ok` 중 wall time, output token 순으로 winner 선택
  (`aggregator.py:84-104`)

두 도구는 유용한 orchestration 기반이지만 현재 상태를 일반적인 prompt quality
증명으로 사용하지 않는다. Scope enforcement, evaluator contract, metric integrity,
commit/error gate를 보강한다.

## F-011 — MCP installer·doctor·pytest plugin 검증 공백

**등급:** `[REPO]` · P1 · TOOL/EVAL

현재 테스트 검색과 coverage 실행에서 `install_mcp.py`, `doctor.py`,
`install_skill.py`는 직접 검증이 거의 없거나 0%였다. `pytest_plugin.py`도 clean
distribution에서 marker/entry point를 직접 고정하는 테스트가 없다.

특히 `doctor.py:102,166,203-220`은 skills, settings, `CLAUDE_SC.md`, import를
user home의 `.claude`에 고정해 확인한다. project/local 설치 진단과 현재 user
설치 진단을 구별하지 못할 수 있다.

완료 gate:

- MCP registry command, scope config, secret redaction, partial failure, 사용자 서버
  보존을 mock subprocess로 검증
- doctor에 scope-aware target을 주고 세 scope fixture 실행
- clean wheel에서 console/pytest entry point와 marker behavior 검증
- install-skill의 packaged source 부재·supporting file·destination 검증

## F-012 — publish workflow의 release gate 공백

**등급:** `[REPO]` · P1 · DIST/B15

`.github/workflows/publish-pypi.yml:24-115`의 publish job은 full test job 의존성
없이 pip/build/twine으로 바로 build·publish한다. Payload inventory와
`superclaude install` 기능 검사는 없다. TestPyPI smoke도 import와 CLI stdout만
보고 subprocess return code를 assert하지 않는다 (`149-170`). Entry point 정의는
소문자 `superclaude`인데 smoke는 `SuperClaude`를 호출한다.

완료 gate:

- 프로젝트 UV 명령과 lock을 사용하는 build
- `make test`, `make test-scripts`, lint, artifact parity 성공 후에만 publish
- wheel을 임시 환경에 설치해 `superclaude install`과 pytest plugin 실행
- CLI subprocess nonzero, skills/templates 누락, unresolved placeholder에서 실패
- production publish도 동일 artifact를 사용하고 gate를 우회하지 않음

## F-013 — 테스트 문서 drift

**등급:** `[REPO]` · P2 · CONTEXT

`docs/testing/procedures.md`는 존재하지 않는 옛 테스트 파일, direct `pytest`,
`black`, `flake8`, `setup/`, 강제되지 않는 90% coverage를 설명한다. 현재 프로젝트
규칙은 UV와 ruff를 사용하며 `AGENTS.md`, `pyproject.toml`, `Makefile`이 우선이다.

완료 gate: stale 문서를 현행 명령·coverage boundary·separate script/canary gate로
교체하거나 authoritative 문서로 redirect한다.

## F-014 — coverage와 type-check의 실행 가능성

**등급:** `[REPO]` · P2 · EVAL

다음 정확한 명령에서 전체 coverage는 42%였고(`@5b6dc5b`, 4,809 stmts / 2,770 miss)
`coverage.report.fail_under`가 없다.

```bash
uv run pytest --cov=superclaude --cov-report=term -q
```

coverage target을 `src/superclaude` path로 바꾸면 다른 분모와 결과가 나올 수 있으므로
baseline 비교에서는 target과 명령을 고정한다.

mypy도 명령을 고정한다. package 전체 실행은 hyphenated skill directory 때문에
package-name 단계에서 실패하므로, Python 전용 하위 경로를 명시해야 오류 수를 얻는다.

```bash
uv run mypy src/superclaude
# exit 2 — "confidence-check is not a valid Python package name"   @5b6dc5b

uv run mypy src/superclaude/cli src/superclaude/utils src/superclaude/hooks
# Found 35 errors in 10 files (checked 19 source files)             @5b6dc5b
```

두 번째 명령의 경로 집합이 새 baseline이다. 이전 기록(15 files, 43 errors)은 실행
경로를 남기지 않아 재현할 수 없으므로 비교 대상으로 쓰지 않는다.

따라서 현재 “90%” 또는 “mypy clean”을 이미 존재하는 hard gate로 주장하지 않는다.
먼저 측정 범위와 baseline을 정하고, 변경 파일 또는 위험 모듈부터 점진 gate를
도입한다.

## F-015 — tracked OKF catalog에서 skill concept 누락

**등급:** `[REPO]` · P1 · CONTEXT/DIST

`src/superclaude/ARCHITECTURE.md:204-208`은 `okf/superclaude/`가 각 source
component를 `resource`로 가리키는 generated catalog라고 선언한다. 마지막 관측
`@5b6dc5b`에서 on-disk resource는 94개, tracked resource는 88개다. 빠진 6개는 모두
`okf/superclaude/skills/*.md`이며 `.gitignore`의 광범위한 `skills/` 패턴이 무시한다.

```bash
find okf/superclaude -name '*.md' | wc -l     # 94
git ls-files okf/superclaude | wc -l          # 88
git ls-files okf/superclaude | grep -c skills/  # 0
```

영향: 현재 checkout에서는 catalog가 완전해 보여도 새 clone 또는 배포된 저장소의
agent-readable catalog에는 skill concept가 없다.

완료 gate:

- source concept와 `git ls-files okf/superclaude` resource의 양방향 exact parity
- resource target 존재, uniqueness, index count 검사
- generator와 재생성 명령을 SSOT로 지정
- skill source와 OKF concept가 의도적으로 tracked되는 ignore 예외

## F-016 — plugin build 경로 실행 불가

**등급:** `[REPO]` · P1 · DIST/TOOL

`Makefile:121-139`는 `make build-plugin`과 `sync-plugin-repo`를 지원 경로로
노출한다. 하지만 `scripts/build_superclaude_plugin.py:16-22`가 요구하는
`plugins/superclaude/manifest/metadata.json`과 template/source payload가 tracked
repository에 없어 현재 `make build-plugin`은 exit 2다.

완료 gate:

- plugin 경로를 유지할지 폐기할지 명시
- 유지한다면 unified `src/superclaude`와 plugin input의 SSOT 관계 확정
- clean build에서 manifest schema와 agents/commands/hooks/scripts/skills payload 검사
- build failure가 sync/release를 nonzero로 차단
- source와 plugin artifact의 version·inventory parity

## 해결된 finding

여기 있는 항목은 실제 코드로 수정됐다. 재발 여부를 추적할 수 있도록 수정 커밋과 현재
코드 위치를 함께 남긴다.

### F-003 — install 성공값의 활성화 사각지대 (해결됨)

**등급:** `[REPO]` · P0 · TOOL/DIST · 해결 커밋 `f25d91a`, `e360ca5`

원래 판정은 install 성공값이 활성화 실패 네 종류를 무시한다는 것이었다. 현재 코드는
네 종류를 모두 누적 실패에 반영한다.

| 활성화 항목 | 현재 위치 | 처리 |
|---|---|---|
| agent memory directory | `install_components.py:469-473` | `except OSError` → `total_failed += 1` |
| `CLAUDE_SC.md` 설치 | `install_components.py:511-515` | 실패 시 `total_failed += 1` |
| `CLAUDE.md` import | `install_components.py:528-534` | 실패 시 `total_failed += 1` |
| local scope git exclude | `install_components.py:539-544` | 실패 시 `total_failed += 1` |

`install_components.py:558`의 `overall_success = total_failed == 0`이 그대로이므로,
활성화 실패는 이제 프로세스 실패로 전파된다. `528-534`에는 판단 근거가 주석으로 남아
있다: *"Counted, not merely warned: without the import the framework is installed and
inert, which is the state the summary would otherwise call a success."*

잔여 사항: 필수/선택 activation 항목의 schema 분류는 도입되지 않았다. 현재 구현은 네
항목을 모두 필수로 취급한다. 선택 항목을 도입할 이유가 생기기 전까지 이는 결함이 아니라
설계 선택이다.

## 권장 실행 순서

```text
1. F-001 distribution payload completeness
2. F-002 exit-status truthfulness (F-003은 해결됨)
3. F-004 clean artifact/runtime parity
4. F-005 machine-readable authoring schema
5. F-006/F-009 release gate baseline 정렬
6. F-007 semantic graph validator
7. F-015/F-016 OKF·plugin 파생 전달 경로 복구 또는 폐기
8. F-010 automation correctness gates
9. F-011/F-012 CLI·publish functional gate
10. F-008 behavioral registry budget 측정
11. F-013/F-014 문서·점진 품질 게이트 정리
```
