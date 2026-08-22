---
phase: superclaude-improvement-verification-guides
verified: 2026-08-22
status: passed
score: "8/8 must-haves verified"
measured_at: a358bcb
revalidated_at: 5b6dc5b
repository_findings_open: "F-001..F-002, F-004..F-016 (15 open; F-003 fixed)"
human_verification:
  - "인증·비용이 필요한 model canary/full matrix는 NOT RUN"
---

# SuperClaude 개선·검증 문서 검증 보고서

## 판정

**문서 목표: PASS — 8/8 must-haves verified.** 측정 커밋 `a358bcb`.

이 판정은 문서 묶음이 `src/superclaude`의 분석·개선·검증 가이드로서 정확하고
실행 가능하다는 뜻이다. `08_current_findings_and_backlog.md`에 기록된 저장소 결함이
해결됐다는 뜻은 아니다.

**판정의 유효 범위.** 이 PASS는 `measured_at` 커밋 기준이다.
`git log <measured_at>..HEAD -- src/`가 비어 있지 않으면 재검증 전까지 `passed`를
신뢰하지 않는다. 아래 §재검증이 마지막 재확인 결과를 담는다.

검증은 `gsd-verifier`의 goal-backward audit로 1차 수행했고, 발견된 gap을 수정한
뒤 main agent가 각 근거와 실행 결과를 다시 확인했다.

## Must-have 판정

| # | 완료를 위해 참이어야 하는 상태 | 판정 | 증거 |
|---|---|---|---|
| 1 | 원문이 변경되지 않고 적용 가이드와 분리된다 | VERIFIED | `00_raw_session_verbatim.md`는 tracked 원본이고 diff가 없음; `README.md`가 보존·해석 경계를 명시 |
| 2 | `src/superclaude`의 content/runtime/package 요소와 enforcement 경계가 분류된다 | VERIFIED | `02_component_and_delivery_map.md`의 snapshot, package root, component contract |
| 3 | 각 content 요소에 분석·개선·좁은 검증 절차가 있다 | VERIFIED | `03_content_component_playbook.md`의 core/agent/command/mode/MCP/skill 절 |
| 4 | CLI/hooks/scripts/utils/templates/plugin에 실행 가능한 절차가 있다 | VERIFIED | `04_runtime_and_distribution_playbook.md`의 scope, hook, CLI, artifact, automation 절 |
| 5 | hard/soft gate와 변경 표면별 명령이 있고 false green을 구분한다 | VERIFIED | `05_quality_gate_catalog.md`의 G0~G7, matrix, untracked 문서 검사 |
| 6 | 실제 `evals/` contract에 맞는 행동 회귀 절차가 있다 | VERIFIED | `06_behavioral_eval_playbook.md`의 4 arms, 7 matrix tasks, 14 canary tasks, hard/soft 판정 |
| 7 | Claude/Codex가 evidence와 canonical state를 유지하며 실행할 수 있다 | VERIFIED | `07_ai_operator_runbook.md`의 입력, 재현, gate, evidence packet, 중단 조건 |
| 8 | 현재 finding과 파생 OKF/plugin/PyPI 경로가 재현 가능하게 기록된다 | VERIFIED | `08_current_findings_and_backlog.md`의 F-001~F-016과 exact command |

## Artifact와 wiring

| Artifact | 역할 | 판정 |
|---|---|---|
| `README.md` | AI 진입점, 증거 등급, 읽기 순서 | VERIFIED; 01~09 상대 링크 연결 |
| `01_session_to_repository_principles.md` | 원문 원칙을 저장소 계약으로 변환 | VERIFIED |
| `02_component_and_delivery_map.md` | 요소, 전달, 강제, 파생 catalog 지도 | VERIFIED |
| `03_content_component_playbook.md` | content 개선·검증 | VERIFIED |
| `04_runtime_and_distribution_playbook.md` | runtime/install/PyPI/OKF/plugin 절차 | VERIFIED |
| `05_quality_gate_catalog.md` | G0~G7과 evidence schema | VERIFIED |
| `06_behavioral_eval_playbook.md` | golden task, A/B, ablation, release 판정 | VERIFIED |
| `07_ai_operator_runbook.md` | Claude/Codex 실행·보고 계약 | VERIFIED |
| `08_current_findings_and_backlog.md` | 검증된 현재 상태와 우선순위 | VERIFIED |
| `09_VERIFICATION.md` | 독립 검증, 수정 내역, 잔여 위험 | VERIFIED |
| `10_improvement_plan.md` | 문서 셋 재검증 결과와 드리프트 방지 계획 | VERIFIED `@5b6dc5b` |

핵심 연결은 다음과 같다.

```text
raw session
→ repository principles
→ source component/delivery map
→ content or runtime playbook
→ G0-G7
→ deterministic/integration/behavior/distribution evidence
→ current finding and release decision
```

## 1차 verifier가 찾은 gap과 수정 결과

| Gap | 수정 | 재검증 |
|---|---|---|
| F-008 description 합계 1자 오차 | commands 11,507 + skills 1,831 = total 13,338로 정정 | YAML frontmatter parser로 재계산 |
| F-014 coverage 명령 누락 | `--cov=superclaude` exact command와 38% baseline 명시 | 동일 명령으로 38% 재현 |
| `git diff --check`가 untracked 문서를 제외 | YAML/link/fence/whitespace를 신규 파일 목록에 직접 적용하는 gate 추가 | 10개 문서 모두 통과 |
| wheel probe가 editable source에 오염될 수 있음 | 임시 CWD + `--isolated --no-project --with <wheel>`로 고정 | clean wheel pytest plugin probe 1 passed |
| OKF catalog edge 누락 | 02/04/05/06/08에 tracked resource parity gate와 F-015 추가 | tracked 82, on-disk 87, tracked skill concept 0 재현 |
| plugin delivery edge 누락 | 02/04/05/08에 build/sync gate와 F-016 추가 | manifest 부재와 build failure 근거 재확인 |
| `RESEARCH_CONFIG.md` 전달 설명이 넓음 | 자동 주입 mode가 아닌 지원 설정임을 02에 명시 | `ARCHITECTURE.md`와 loader 설계 대조 |
| package root 계약이 암묵적 | `__init__.py`, `ARCHITECTURE.md`, version parity를 02/05에 추가 | version consistency test 경로 확인 |

## 실행 증거

### 문서 자체

```text
대상: README.md, 01~09
YAML frontmatter: PASS
relative links: PASS
code fence balance: PASS
trailing whitespace: PASS
git diff --check: PASS
총 문서 줄 수: 2,233
```

실제 신규 파일은 `git status --short`로 확정해 검사했다. 따라서 untracked 파일을
보지 못하는 `git diff --check`만으로 PASS를 선언하지 않았다.

### 저장소 기준선 (`@a358bcb`)

아래는 원 검증 시점의 관측이다. 현재 값은 §재검증과
[`08_current_findings_and_backlog.md`](08_current_findings_and_backlog.md)를 본다.

| 명령 | 결과 |
|---|---|
| `uv run pytest -q` | 2157 passed, 28 skipped, 4 deselected; exit 0 |
| `uv run pytest tests/unit/scripts -o addopts= -q --tb=short` | 120 passed; exit 0 |
| `uv run python evals/run_eval.py --dry-run` | 4 arms × 7 tasks = 28 workspace; exit 0 |
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | 기존 test 3개 때문에 exit 1; F-009와 일치 |
| `uv run pytest --cov=superclaude --cov-report=term -q` | TOTAL 38%; F-014와 일치 |
| `uv run mypy src/superclaude` | hyphenated package-name 오류; exit 2 |
| Python-only mypy 범위 | 15 files, 43 errors; exit 1 |

### Distribution과 파생 경로 (`@a358bcb`)

| Probe | 결과 |
|---|---|
| clean `uv build` wheel/sdist inventory | `skills/` 0개; F-001 재현 |
| wheel-only `superclaude install --scope project` | skills 1 failed, process exit 1 |
| wheel-only pytest entry-point probe | `superclaude.pytest_plugin` 등록, 1 passed |
| description YAML 합계 | commands 11,507, skills 1,831, total 13,338 |
| OKF resources | on-disk 87, tracked 82, tracked skill concepts 0 |
| plugin input | `plugins/superclaude/manifest/metadata.json` missing; F-016 |

## 재검증 `@5b6dc5b`

원 검증 이후 `src/superclaude/`를 바꾼 커밋 9개가 병합됐다. 전체 재검증 결과와 개선
계획은 [`10_improvement_plan.md`](10_improvement_plan.md)에 있다. 요지만 남긴다.

문서 구조는 통과를 유지한다. frontmatter, 상대 링크, code fence, trailing whitespace
검사가 신규 문서를 포함해 모두 통과했다.

기준선 변화:

| 항목 | `@a358bcb` | `@5b6dc5b` |
|---|---|---|
| `uv run pytest -q` | 2157 passed | 2279 passed, 28 skipped, 4 deselected |
| coverage TOTAL | 38% | 42% |
| `ruff format --check .` 대상 | 3 files (모두 tests) | 10 files (`src/` 3개 포함) |
| commands description | 11,507자 | 11,594자 |
| description total | 13,338자 | 13,425자 |
| `mcp/MCP_*.md` | 6 | 5 (`0a37af8` Sequential 제거) |
| OKF on-disk / tracked | 87 / 82 | 94 / 88 |

finding 상태 변화:

- `F-003` **해결됨**. `install_components.py`가 활성화 실패 네 종류를 모두
  `total_failed`에 반영한다. 상세는 `08`의 §해결된 finding.
- 나머지 15개는 재현된다. `F-001`은 wheel/sdist에 `superclaude/skills/` 0개로 그대로
  재현됐고, 대조군(templates 4, commands 38)은 정상이다.
- `F-007`의 근거 서술을 정정했다. agent trigger uniqueness 검사가 없다는 결론은
  유효하지만, `triggers` 필드 파싱은 현재 테스트에 존재하지 않는다.
- `F-009`는 성격이 바뀌었다. 재포맷 대상에 배포되는 `src/` 모듈 3개가 포함된다.
- `F-014`의 mypy 값은 실행 경로가 기록되지 않아 재현할 수 없었다. 명령을 고정한 새
  baseline으로 교체했다.

재발 방지: 구성요소 인벤토리는 `02` §1을 단일 기재 위치로 두고
`tests/unit/test_codex_component_map.py`가 소스에서 직접 세어 대조한다. 커밋마다 바뀌는
측정치는 `08`이 재측정 명령과 관측 커밋을 함께 소유하며 테스트로 강제하지 않는다.

## NOT RUN과 잔여 위험

- 실제 model canary와 full comparative matrix는 인증·비용이 필요해 실행하지 않았다.
  문서는 이를 `NOT RUN`으로 취급하며 dry-run을 행동 PASS로 승격하지 않는다.
- 이 변경은 Markdown-only다. 저장소의 F-001~F-016을 구현으로 수정하지 않았다.
- 전체 format, coverage, mypy가 green이라는 주장을 하지 않는다. 각각의 현재
  baseline과 실패 범위는 `08_current_findings_and_backlog.md`에 봉인했다.
- component 수, 테스트 baseline, 파생 catalog는 snapshot이므로 source가 바뀌면
  이 보고서와 `last_verified`를 다시 갱신해야 한다.

## 최종 결론

사용자 요구인 “`src/superclaude` 각 요소를 분석하고, 개선·검증 가능한 가이드와
게이트를 Claude/Codex가 읽기 좋은 여러 문서로 만든다”는 문서 수준에서 달성됐다.
이후 구현 작업은 `08_current_findings_and_backlog.md`의 우선순위와
`05_quality_gate_catalog.md`의 G0~G7을 함께 사용한다.

---

_Verifier: independent `gsd-verifier` audit + main-agent evidence recheck_
