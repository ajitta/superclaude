---
title: 문서 셋 검증 결과와 개선 계획
status: verified-plan
last_verified: 2026-08-22
measured_at: 5b6dc5b
scope: docs/codex/prompting_session_raw
---

# 문서 셋 검증 결과와 개선 계획

이 문서는 `docs/codex/prompting_session_raw/`의 가이드 묶음(`README.md`, `01`~`09`)을
현재 저장소 상태와 대조한 결과와, 확인된 결함을 없애기 위한 계획을 담는다. 대상은
가이드 자신이지 가이드가 기술하는 저장소 결함이 아니다. `F-001`~`F-016`의 실제 수정은
이 계획의 범위 밖이며 `08_current_findings_and_backlog.md`가 계속 소유한다.

## 1. 검증 방법과 기준선

측정 커밋: `5b6dc5b` (`master`, 2026-08-22).

문서 묶음은 커밋 `a358bcb`에서 추가됐다. 그 이후 `src/superclaude/`를 변경한 커밋이
9개 병합됐다.

```bash
git log a358bcb..HEAD --oneline -- src/
```

- `0a37af8` Sequential MCP와 `--seq` 플래그 제거
- `a5d16c3` command description 정정
- `d68b8c3` runtime state 정리
- `f25d91a` 취소·실패 install의 정직성 수정
- `d56fe1a` context loader 플래그 판독 수정
- `19237ba`, `692952c` insight 수집 수정
- `e360ca5`, `f94bbcb` hook 소유권과 install 갱신 수정

이 커밋들이 가이드에 박힌 스냅샷 수치를 낡게 만들었고, 결함 하나를 실제로 해결했다.

## 2. 통과한 항목

문서 구조는 전부 통과했다.

```text
대상: README.md, 01~09 (가이드 10개, 2,233줄)
YAML frontmatter 파싱: PASS
상대 링크 대상 존재: PASS
code fence 짝수: PASS
trailing whitespace 없음: PASS
```

가이드 전용 줄 수 2,233은 `09_VERIFICATION.md`가 기록한 값과 정확히 일치한다. 원문
`00_raw_session_verbatim.md`는 무변경 tracked 상태로 보존돼 있다. 문서 간 상호 참조
링크도 모두 유효하다.

`01`, `03`, `06`, `07`은 저장소 수치에 의존하지 않는 원칙·절차 문서이며 현재 규칙 및
테스트 구조와 모순되는 서술이 발견되지 않았다.

## 3. 확인된 결함

### D-01 — 스냅샷 수치 드리프트 (9건)

| 항목 | 문서 기재 | 실측 `@5b6dc5b` | 기재 위치 |
|---|---|---|---|
| `mcp/MCP_*.md` 개수 | 6 | 5 | `02:23` |
| `uv run pytest -q` | 2157 passed | 2279 passed, 28 skipped, 4 deselected | `05:6`, `08:130`, `09:98` |
| commands description 합계 | 11,507자 | 11,594자 | `08:170`, `09:68`, `09:114` |
| description total | 13,338자 | 13,425자 | `08:172`, `09:68`, `09:114` |
| `ruff format --check .` 대상 | 3 files | 10 files | `05:54`, `08:205-210`, `09:102` |
| coverage TOTAL | 38% | 42% (4,809 stmts / 2,770 miss) | `08:291`, `09:103` |
| OKF on-disk / tracked | 87 / 82 | 94 / 88 | `08:312`, `09:72`, `09:115` |
| OKF 누락 skill concept | 5 | 6 | `08:313`, `04:180` |
| mypy python-only 범위 | 15 files, 43 errors | 재현 불가 — 실행 경로 미기록 | `08:298-300`, `09:105` |

`MCP_*.md` 개수는 `0a37af8`의 Sequential 제거 결과다. `ruff format` 대상 확대는 단순
증가가 아니라 성격이 바뀐 것으로, 아래 D-04에서 따로 다룬다.

재현 명령:

```bash
uv run pytest -q
uv run pytest --cov=superclaude --cov-report=term -q
uv run ruff format --check .
ls src/superclaude/mcp/MCP_*.md | wc -l
find okf/superclaude -name '*.md' | wc -l
git ls-files okf/superclaude | wc -l
```

description 합계는 Markdown 본문 검색이 아니라 각 파일의 YAML frontmatter를 파서로
읽어 계산한다. 대상은 README를 제외한 `commands/*.md`와 `skills/*/SKILL.md`다.

### D-02 — 해결된 결함을 열린 상태로 기재 (F-003)

`08:79-93`은 `F-003`을 P0 FAIL로 두고 install 성공값이 활성화 실패 네 종류를 무시한다고
기록한다. 현재 코드는 네 종류를 모두 누적 실패에 반영한다.

| 활성화 항목 | 현재 위치 | 처리 |
|---|---|---|
| agent memory directory | `install_components.py:469-473` | `except OSError` → `total_failed += 1` |
| `CLAUDE_SC.md` 설치 | `install_components.py:511-515` | 실패 시 `total_failed += 1` |
| `CLAUDE.md` import | `install_components.py:528-534` | 실패 시 `total_failed += 1` |
| local scope git exclude | `install_components.py:539-544` | 실패 시 `total_failed += 1` |

`528-534`에는 판단 근거가 주석으로 남아 있다.

```text
Counted, not merely warned: without the import the framework is
installed and inert, which is the state the summary would
otherwise call a success.
```

`overall_success = total_failed == 0` (`558`)이므로 활성화 실패는 이제 프로세스 실패로
전파된다. 수정 주체는 runtime-behavior-audit remediation 커밋들(`f25d91a`, `e360ca5`)이다.
`08`의 권장 실행 순서 2번은 절반이 이미 완료된 상태를 남은 작업처럼 제시한다.

### D-03 — 근거가 낡은 finding 서술 (F-007)

`08:155-156`은 agent trigger uniqueness 검사가 "deprecated `triggers - ...` 형태만
파싱해 사실상 비어 있다"고 기술한다. 현재 `tests/unit/test_agent_structure.py`에는
`triggers` 필드를 파싱하는 코드가 없다. 대신 `test_description_has_cc_idiom_trigger`가
description에 CC-idiom delegation trigger 문장이 있는지만 확인한다.

결론(인접 agent 간 trigger 중복을 검사하지 않음)은 유효하다. 근거 서술만 낡았다.
잘못된 근거는 수정 대상 코드를 잘못 지목하게 만든다.

### D-04 — formatting baseline의 성격 변화 미반영 (F-009)

`08:205-210`은 재포맷 대상을 테스트 파일 3개로 열거하고 "현재 작업이 문서-only라 이
파일을 부수적으로 바꾸지 않는다"고 기록한다. 현재 대상은 10개이며, 그중 3개는 테스트가
아니라 배포되는 프로덕션 코드다.

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

`src/` 파일이 목록에 들어온 것은 수치 증가가 아니라 상태 변화다. 문서가 "기존 테스트
파일 3개"라고 기술하는 한 이 사실은 보이지 않는다.

### D-05 — 스냅샷 SSOT 부재

동일 수치가 네 파일에 중복 기재돼 있다.

```text
pytest 카운트     → 05 frontmatter, 08 §F-006, 09 실행 증거 표
description 합계  → 08 §F-008, 09 수정 표, 09 파생 경로 표
OKF 카운트        → 08 §F-015, 09 수정 표, 09 파생 경로 표
ruff format 대상  → 05 §G1, 08 §F-009, 09 실행 증거 표
```

`README:67`은 "이 디렉터리에는 원문 규칙을 복사하지 않고 링크, 게이트, 작업 순서만
둔다"고 선언하고, `.claude/rules/content-quality.md`는 규칙마다 답이 한 곳에만 있어야
한다고 요구한다. 스냅샷 수치는 두 규칙 모두의 대상이며 둘 다 지켜지지 않았다. 갱신하려면
네 곳을 찾아야 하고, 실제로는 한 곳도 갱신되지 않았다.

### D-06 — 드리프트 감지 수단 없음

`README:66`은 "구성요소 수와 테스트 명령은 스냅샷이다. 변경 시 소스에서 다시 계산한다"고
규정한다. 이 규칙을 강제하는 테스트, 스크립트, hook이 없다. 규칙이 도입된 뒤 소스가 9개
커밋만큼 변했고 재계산은 일어나지 않았다.

`README:61`의 공통 판정 3번은 "프롬프트는 정책을 표현하고, 보장이 필요한 제약은 hook·
권한·코드가 강제한다"이다. 문서 묶음은 자기 수치의 최신성이라는 제약을 산문에만 맡겨
자신의 판정을 위반했다.

### D-07 — 만료 조건 없는 검증 도장

`09_VERIFICATION.md`의 frontmatter는 `verified: 2026-08-22`, `status: passed`이고 본문은
"문서 목표: PASS — 8/8 must-haves verified"로 시작한다. 어떤 커밋 기준 측정인지 SHA가
없고 만료 조건도 없다. 낡은 상태에서도 신뢰 신호를 그대로 방출한다.

`repository_findings_open: F-001..F-016`도 F-003이 해결된 지금 부정확하다.

### D-08 — 재현 명령 누락

`08:298-300`은 mypy 결과를 "Python-only 하위 경로를 명시해 실행하면 15개 파일의 43개
오류가 남는다"고 기록한다. 어떤 경로를 명시했는지 적지 않아 재현이 불가능하다. 같은
문서 `08:291`은 coverage에 대해 "다음 정확한 명령에서"라며 명령을 고정하므로, 문서가
자기 기준을 한 항목에서만 지킨 셈이다.

참고로 현재 측정값은 다음과 같다.

```bash
uv run mypy src/superclaude
# exit 2 — "confidence-check is not a valid Python package name"

uv run mypy src/superclaude/cli src/superclaude/utils src/superclaude/hooks
# Found 35 errors in 10 files (checked 19 source files)
```

두 번째 명령이 문서가 말한 "Python-only 하위 경로"와 같은 범위라는 보장은 없다. 그래서
이 값은 새 baseline이며 과거 값과의 비교가 아니다.

## 4. 재현 확인된 기존 finding

`F-003`을 제외한 15개는 현재도 재현된다. 대표 증거만 남긴다.

| ID | 재현 증거 `@5b6dc5b` |
|---|---|
| F-001 | wheel/sdist에 `superclaude/skills/` 0개. 대조군 정상 — templates 4, commands 38 |
| F-002 | `Makefile`의 `test-plugin`, `verify`가 `... && echo ✅ \|\| echo ❌` 패턴으로 exit 0 유지 |
| F-004 | `verify_drift.py` docstring이 templates·installed scripts·merged hooks 제외를 명시 |
| F-005 | `skill-authoring.md`가 필드 카탈로그에 실은 `model`, `context: fork`, `agent`를 `test_skill_structure.py`의 세 테스트가 금지 |
| F-006 | `pyproject.toml` addopts에 `--ignore=tests/unit/scripts`, `-m not canary` |
| F-007 | `core/` 전용 구조 테스트 없음, agent trigger uniqueness 검사 없음 (근거는 D-03에서 정정) |
| F-008 | description 합계 13,425자, 문서상 fallback 예산 약 8,000자 초과 |
| F-009 | 재포맷 대상 10개, 그중 `src/` 3개 (D-04) |
| F-010 | `coordinator.py`의 `scope_glob`가 mutator 프롬프트 전달용 advisory, `aggregator.py`가 wall time과 output token으로 winner 선택 |
| F-011 | coverage 0% — `doctor.py`, `install_mcp.py`, `install_skill.py` |
| F-012 | `publish-pypi.yml` smoke가 대문자 `SuperClaude` 호출, entry point는 소문자 `superclaude` |
| F-013 | `docs/testing/procedures.md`에 `black`, `flake8`, 90% coverage 서술 잔존 |
| F-014 | coverage 42%, `fail_under` 없음, mypy package-wide exit 2 |
| F-015 | tracked OKF skill concept 0개, on-disk 6개 |
| F-016 | `plugins/superclaude/manifest/metadata.json` 부재로 `make build-plugin` 실행 불가 |

## 5. 개선 설계

### 5.1 수치를 두 계층으로 나눈다

드리프트의 원인은 수치를 기록한 것 자체가 아니라, 변동 주기가 다른 두 종류를 같은
방식으로 다룬 것이다.

**계층 1 — 안정 인벤토리.** 컴포넌트 종류별 개수. 결함 근거가 아니라 지도 역할이고,
변경 주기가 릴리스 단위다. 문서에 값을 유지할 값어치가 있다.

```text
agents 23 | commands 36 | core always-loaded 3 | core/rules 4
MODE_*.md 7 | *CONFIG*.md 1 | MCP_*.md 5 | skills 5 | templates 4
distinct hook entry scripts 10 (hooks.json 등록 14) | Python modules 58
```

기재 위치는 `02_component_and_delivery_map.md` §1 한 곳으로 고정한다. 다른 문서는
링크만 둔다.

**계층 2 — 변동 측정치.** pytest 카운트, coverage 비율, description 문자 수, ruff format
대상 수, mypy 오류 수, OKF 카운트. 커밋마다 바뀌므로 값을 박으면 반드시 낡는다. 값 대신
재측정 명령과 마지막 관측을 SHA와 함께 둔다.

```text
`uv run pytest -q` 로 재측정 (마지막 관측 2279 passed @ 5b6dc5b)
```

이 형식이면 값이 낡아도 독자가 `git log 5b6dc5b..HEAD -- src/`로 즉시 판별하고 명령 한
줄로 갱신할 수 있다. 값이 사라지는 것이 아니라 유효 범위가 명시된다.

### 5.2 계층 1만 테스트로 강제한다

`tests/unit/test_codex_component_map.py`를 추가해 `02` §1 표를 파싱하고 소스에서 직접
센 값과 대조한다.

경로는 하드코딩하지 않고 `src/superclaude/cli/install_paths.py::COMPONENTS`에서 가져온다.
컴포넌트 → 소스 경로 매핑의 SSOT가 이미 그곳이고, 새 컴포넌트가 추가되면 테스트도 함께
따라가야 하기 때문이다.

기존 `tests/unit/test_version_consistency.py`가 문서 문자열 lint의 선례지만, 그 테스트는
문서끼리만 비교해 전부 낡은 상태에서도 통과하는 약점이 있다. 새 테스트는 반드시 소스를
직접 센다.

계층 2는 테스트로 강제하지 않는다. 매 커밋 실패하는 게이트는 무시되고, 무시되는 게이트는
없는 것보다 나쁘다.

### 5.3 검증 도장에 만료 조건을 붙인다

`09_VERIFICATION.md` frontmatter에 `measured_at`을 추가하고 판정 문단에 한 줄을 넣는다.

```text
이 판정은 measured_at 커밋 기준이다. `git log <SHA>..HEAD -- src/`가
비어 있지 않으면 재검증 전까지 passed를 신뢰하지 않는다.
```

`status: passed`를 지우지는 않는다. 판정 자체는 그 시점에 유효했고, 필요한 것은 유효
범위의 명시다.

## 6. 실행 계획

| # | 작업 | 대상 | 상태 |
|---|---|---|---|
| 1 | 이 문서 추가, 문서 지도에 행 등록 | `10_improvement_plan.md`, `README.md` | 완료 |
| 2 | MCP 개수 6 → 5, §1을 인벤토리 SSOT로 명시 | `02` | 완료 |
| 3 | OKF skill concept 5 → 6 | `04` | 완료 |
| 4 | frontmatter `baseline:` 제거, ruff 서술을 명령+SHA로 | `05` | 완료 |
| 5 | F-003을 해결된 finding으로 이동, 요약 표 판정 변경, 권장 순서에서 제거 | `08` | 완료 |
| 6 | F-007 근거 문장 교체, F-009 대상 목록 갱신, F-014 mypy 명령 명시, F-015 카운트 정정 | `08` | 완료 |
| 7 | 계층 2 값 전부 명령+SHA 형식으로 교체 | `05`, `08`, `09` | 완료 |
| 8 | `measured_at` 추가, 만료 조건 명시, `repository_findings_open` 정정 | `09` | 완료 |
| 9 | 갱신 규칙에 수치 계층 구분과 신선도 확인 절차 추가 | `README` | 완료 |
| 10 | 인벤토리 대조 테스트 추가 | `tests/unit/test_codex_component_map.py` | 완료 |

8번은 원안에서 한 가지를 바꿨다. `09`의 실행 증거 표를 현재 값으로 덮어쓰면 원 검증
기록이 왜곡되므로, 표는 `@a358bcb` 관측으로 명시해 보존하고 현재 값은 §재검증 절을
새로 만들어 담았다. 해결된 결함을 삭제하지 않고 이력으로 남기는 것과 같은 이유다.

## 7. 완료 판정

실행 결과:

```text
uv run pytest tests/unit/test_codex_component_map.py -q
→ 13 passed

02 §1의 MCP 값을 5에서 6으로 되돌린 상태
→ 1 failed, 12 passed
   "02 §1 says mcp/MCP_*.md = 6, source has 5"

uv run pytest -q
→ 2292 passed, 28 skipped, 4 deselected   (2279 + 신규 13, 회귀 0)

uv run ruff check .
→ All checks passed

uv run ruff format --check .
→ 10 files would be reformatted, 105 already formatted
   (F-009 목록 불변 — 신규 테스트는 포맷됨)

문서 구조 검사 (README + 01~10)
→ frontmatter, 상대 링크, code fence, trailing whitespace 전부 PASS
```

Hard gate 판정:

- 정정된 모든 수치가 재측정값과 일치한다 — PASS
- `F-003`이 해결된 finding으로 기재되고 수정 위치가 `file:line`으로 지목된다 — PASS
- 새 테스트가 `02` §1을 소스와 대조하며, 값을 의도적으로 틀리게 바꾸면 실패한다 — PASS
- 전체 스위트에 회귀가 없다 — PASS
- 문서 구조 검사가 신규 문서를 포함해 통과한다 — PASS

신규 테스트 13개가 추가되면서 저장소 baseline이 2279에서 2292로 바뀌었다. `CLAUDE.md`,
`AGENTS.md`, `README.md`의 baseline 문자열도 함께 갱신했다.

이 계획은 저장소 결함을 수정하지 않는다. 계획이 끝나도 `F-001`, `F-002`, `F-004`~`F-016`은
열린 상태로 남으며 우선순위는 `08_current_findings_and_backlog.md`가 소유한다.
