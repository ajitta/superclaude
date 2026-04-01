---
status: draft
revised: 2026-04-01
---

# Doc Output Convention v2 — Design Spec

Discovery: `doc-output-convention-v2-discovery-chosh1179-2026-04-01.md`

## Change Map

13개 파일 수정. 변경을 3개 그룹으로 분류합니다.

### Group 1: Dated Document Commands (5 files)

파일명 패턴을 `YYYY-MM-DD-<topic>-<suffix>-<username>.md` → `<topic>-<suffix?>-<username>-YYYY-MM-DD.md`로 변경.

---

#### 1.1 `src/superclaude/commands/brainstorm.md`

**변경:** 날짜 위치 이동 + suffix `design` → `discovery`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| flow step 4 (line 19) | `docs/specs/YYYY-MM-DD-<topic>-design-<username>.md` | `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` |
| outputs table (line 27) | `docs/specs/YYYY-MM-DD-<topic>-design-<username>.md` | `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` |

frontmatter 생성 지시 추가 (flow step 4에 병합):
```
4. Specify: Write spec to docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>)
```

---

#### 1.2 `src/superclaude/commands/plan.md`

**변경:** 날짜 위치 이동 + frontmatter 지시 추가

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| flow step 5 (line 18) | `docs/plans/YYYY-MM-DD-<feature-name>-<username>.md` | `docs/plans/<feature-name>-<username>-YYYY-MM-DD.md` |
| outputs table (line 25) | `docs/plans/YYYY-MM-DD-<name>-<username>.md` | `docs/plans/<name>-<username>-YYYY-MM-DD.md` |

frontmatter 생성 지시 추가 (flow step 5에 병합):
```
5. Save: Write to docs/plans/<feature-name>-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>)
```

---

#### 1.3 `src/superclaude/commands/research.md`

**변경:** 날짜 위치 이동 + suffix 제거

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| flow step 5 (line 18) | `docs/research/YYYY-MM-DD-<topic>-research-<username>.md` | `docs/research/<topic>-<username>-YYYY-MM-DD.md` |

suffix `-research` 제거 — `docs/research/` 디렉토리가 이미 type을 나타냄.

---

#### 1.4 `src/superclaude/commands/analyze.md`

**변경:** 날짜 위치 이동 + suffix 제거

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| outputs json (line 26) | `docs/analysis/YYYY-MM-DD-<target>-analysis-<username>.json` | `docs/analysis/<target>-<username>-YYYY-MM-DD.json` |
| outputs report (line 27) | `docs/analysis/YYYY-MM-DD-<target>-analysis-<username>.md` | `docs/analysis/<target>-<username>-YYYY-MM-DD.md` |

suffix `-analysis` 제거 — `docs/analysis/` 디렉토리가 이미 type을 나타냄.

---

#### 1.5 `src/superclaude/commands/design.md`

**변경:** dated output 패턴 추가

현재 design.md는 `ARCHITECTURE.md`, `API_SPEC.md` 등 project-specific artifacts만 정의.
Convention에 따라 **design spec 문서**의 출력 패턴을 추가합니다.

outputs table에 행 추가:
```
| (all types) | spec (default) | `docs/specs/<topic>-design-<username>-YYYY-MM-DD.md` |
```

flow에 save step 추가:
```
5. Document: Save design spec to docs/specs/<topic>-design-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>)
```

Note: 기존 project-specific artifacts (ARCHITECTURE.md 등)는 변경하지 않음.

---

### Group 2: Living Document Commands (6 files)

출력 경로를 project root → `docs/reports/`로 변경.

---

#### 2.1 `src/superclaude/commands/workflow.md`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| outputs (line 24) | `WORKFLOW.md` | `docs/reports/WORKFLOW.md` |
| outputs (line 26) | `WORKFLOW_STATUS.md` | `docs/reports/WORKFLOW_STATUS.md` |

---

#### 2.2 `src/superclaude/commands/index-repo.md`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| flow step 4 (line 17) | `PROJECT_INDEX.md` | `docs/reports/PROJECT_INDEX.md` |
| flow step 5 (line 18) | `PROJECT_INDEX.json` | `docs/reports/PROJECT_INDEX.json` |

---

#### 2.3 `src/superclaude/commands/index.md`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| outputs docs (line 24) | `KNOWLEDGE.md` | `docs/reports/KNOWLEDGE.md` |
| outputs api (line 25) | `API.md` | `docs/reports/API.md` |
| outputs structure (line 26) | `STRUCTURE.md` | `docs/reports/STRUCTURE.md` |

Note: `README.md`는 프로젝트 설정 파일이므로 루트 유지 (convention 범위 밖).

---

#### 2.4 `src/superclaude/commands/build.md`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| outputs dev (line 24) | `BUILD_DEV.log` | `docs/reports/BUILD_DEV.log` |
| outputs prod (line 25) | `BUILD_REPORT.md` | `docs/reports/BUILD_REPORT.md` |
| outputs test (line 26) | `BUILD_TEST.log` | `docs/reports/BUILD_TEST.log` |

Note: `dist/`, `dist-dev/`, `dist-test/` 빌드 산출물 디렉토리는 변경하지 않음 (코드 산출물, 문서 아님).

---

#### 2.5 `src/superclaude/commands/test.md`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| outputs coverage (line 24) | `coverage/` | `coverage/` (변경 없음 — 코드 산출물) |
| outputs unit (line 25) | `TEST_UNIT.log` | `docs/reports/TEST_UNIT.log` |
| outputs e2e (line 26) | `TEST_E2E.log` | `docs/reports/TEST_E2E.log` |
| outputs default (line 27) | `TEST_REPORT.md` | `docs/reports/TEST_REPORT.md` |

---

#### 2.6 `src/superclaude/commands/spawn.md`

| 위치 | 현재 | 변경 후 |
|------|------|---------|
| outputs (line 25) | `SPAWN_PLAN.md` | `docs/reports/SPAWN_PLAN.md` |
| outputs (line 26) | `SPAWN_RESULT.md` | `docs/reports/SPAWN_RESULT.md` |

---

### Group 3: Convention + Formatter (2 files)

---

#### 3.1 `src/superclaude/core/RULES.md`

`doc_output_convention` 섹션 (lines 102-109) 전체 교체:

**현재:**
```xml
<doc_output_convention note="Unified naming for all file-producing commands">
Pattern: docs/<type>/YYYY-MM-DD-<topic-slug>-<suffix>-<username>.md
Username: `git config user.name` (lowercase, no spaces) — fallback to system username
Directory: brainstorm→docs/specs/ | design→docs/specs/ | plan→docs/plans/ | workflow→docs/plans/ | analyze→docs/analysis/ | research→docs/research/
Suffix: brainstorm→discovery | design→design | plan→(topic only) | workflow→workflow | analyze→analysis | research→research
Living docs (no date/username): PROJECT_INDEX.md, WORKFLOW.md, BUILD_REPORT.md, CLEANUP_REPORT.md, KNOWLEDGE.md
Example: docs/specs/2026-03-20-selection-protocol-design-ajitta.md
</doc_output_convention>
```

**변경 후:**
```xml
<doc_output_convention note="Unified naming for all file-producing commands">
Pattern: docs/<type>/<topic-slug>-<suffix?>-<username>-YYYY-MM-DD.md
Username: `git config user.name` (lowercase, no spaces) — fallback to system username
Directory: brainstorm→docs/specs/ | design→docs/specs/ | plan→docs/plans/ | workflow→docs/plans/ | analyze→docs/analysis/ | research→docs/research/
Suffix (shared dirs only): brainstorm→-discovery | design→-design | workflow→-workflow
Living docs (UPPER_SNAKE, no date/username): all in docs/reports/
Frontmatter: specs/+plans/ require {status, revised}. research/+analysis/ optional. reports/ none
Formatter: /sc:cleanup --type docs (validate + transform + migrate)
Example: docs/specs/selection-protocol-design-ajitta-2026-03-20.md
</doc_output_convention>
```

**변경 포인트 (7개):**
1. Pattern: 날짜 위치 끝으로
2. Suffix: `(shared dirs only)` 조건 추가, analyze/research suffix 제거
3. Living docs: 경로 `docs/reports/` 명시
4. Frontmatter: 새 규칙 추가
5. Formatter: 새 도구 참조 추가
6. Example: 새 패턴 반영
7. Plan suffix 제거 (이미 없었지만 명시적으로 표에서 제외)

---

#### 3.2 `src/superclaude/commands/cleanup.md`

**변경 1:** syntax에 `docs` 타입 추가

현재 (line 10):
```
<syntax>/sc:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]</syntax>
```

변경:
```
<syntax>/sc:cleanup [target] [--type code|imports|files|docs|all] [--safe|--aggressive] [--interactive] [--dry-run]</syntax>
```

**변경 2:** outputs table에 `docs` 행 추가

현재 (lines 20-27):
```
| Type | Actions | Report |
|------|---------|--------|
| code | Remove dead code | CLEANUP_CODE.md |
| imports | Remove unused imports | CLEANUP_IMPORTS.md |
| files | Remove orphan files | CLEANUP_FILES.md |
| all | All above | CLEANUP_REPORT.md |
```

변경:
```
| Type | Actions | Report |
|------|---------|--------|
| code | Remove dead code | docs/reports/CLEANUP_CODE.md |
| imports | Remove unused imports | docs/reports/CLEANUP_IMPORTS.md |
| files | Remove orphan files | docs/reports/CLEANUP_FILES.md |
| docs | Validate + transform doc naming | docs/reports/CLEANUP_DOCS.md |
| all | All above | docs/reports/CLEANUP_REPORT.md |
```

**변경 3:** patterns 섹션에 Docs 패턴 추가

현재 (lines 39-43):
```
<patterns>
  - DeadCode: Usage analysis → safe removal
  - Imports: Dependency analysis → optimization
  - Structure: Arch analysis → modular improvements
  - Safety: Pre/during/post checks
</patterns>
```

변경:
```
<patterns>
  - DeadCode: Usage analysis → safe removal
  - Imports: Dependency analysis → optimization
  - Structure: Arch analysis → modular improvements
  - Docs: Convention validation → rename + move (--dry-run supported)
  - Safety: Pre/during/post checks
</patterns>
```

**변경 4:** examples에 docs 예시 추가

```
| `--type docs --dry-run` | Preview doc naming fixes |
| `--type docs` | Auto-fix doc naming convention |
```

---

## Cleanup --type docs: Formatter Spec

`/sc:cleanup --type docs`가 수행하는 구체적 동작:

### Phase 1: Scan

```
1. docs/ 하위 모든 파일 수집 (Glob "docs/**/*.{md,json}")
2. 파일을 3 범주로 분류:
   a. Dated docs: docs/{specs,plans,research,analysis}/ 내 파일
   b. Living docs: UPPER_SNAKE 패턴 파일
   c. Unknown: 분류 불가 파일 (경고 출력)
```

### Phase 2: Validate

각 파일에 대해 convention 위반 검사:

| 검사 | 대상 | 위반 시 |
|------|------|---------|
| 날짜 위치 | Dated docs | 앞에 있으면 끝으로 이동 제안 |
| 중복 suffix | research/, analysis/ | suffix 제거 제안 |
| 누락 suffix | specs/ (brainstorm/design 구분 불가) | 경고 (자동 수정 불가) |
| username 누락 | Dated docs | git log에서 추출 시도 → 추가 제안 |
| frontmatter 누락 | specs/, plans/ | 추가 제안 |
| 잘못된 위치 | 루트의 living docs | docs/reports/로 이동 제안 |
| 잘못된 case | living docs | UPPER_SNAKE 아니면 경고 |

### Phase 3: Transform (--dry-run이 아닐 때)

```
1. 파일 rename (git mv 사용 — 이력 보존)
2. frontmatter 삽입 (status: draft, revised: <today>)
3. 디렉토리 생성 (docs/reports/ 등)
4. 결과 리포트 생성: docs/reports/CLEANUP_DOCS.md
```

### Output: CLEANUP_DOCS.md

```markdown
# Doc Convention Cleanup Report

## Summary
- Scanned: 42 files
- Violations: 12
- Fixed: 10
- Warnings: 2 (manual review needed)

## Changes
| File | Action | Old | New |
|------|--------|-----|-----|
| ... | rename | 2026-03-20-auth-design-ajitta.md | auth-design-ajitta-2026-03-20.md |
| ... | move | PROJECT_INDEX.md | docs/reports/PROJECT_INDEX.md |
| ... | add frontmatter | (none) | status: draft, revised: 2026-04-01 |

## Warnings
- docs/specs/old-file.md — cannot determine if brainstorm or design (no suffix, ambiguous)
```

---

## CLAUDE.md Impact

프로젝트 CLAUDE.md에서 `doc_output_convention` 참조가 있는 경우 업데이트 필요:

현재 CLAUDE.md (이 프로젝트):
```
- **Suffix**: brainstorm→discovery | design→design | ...
```

이 라인은 RULES.md의 `doc_output_convention`을 간접 참조하므로, RULES.md 변경 시 자동 반영됨 (CLAUDE.md 자체 수정 불필요).

---

## Validation

모든 변경 후 실행:

```bash
# 구조 테스트 (기존 — command/agent 구조 검증)
uv run pytest tests/unit/test_command_structure.py -v
uv run pytest tests/unit/test_agent_structure.py -v

# 전체 테스트 (regression 확인)
uv run pytest tests/unit/ -v
```

마크다운 변경이므로 테스트 실패 위험 없음 (tests are docs-change-safe).

---

## Implementation Order

의존성 기반 실행 순서:

```
Phase 1 (독립, 병렬 가능):
  ├── 3.1 RULES.md doc_output_convention 교체
  ├── 1.1 brainstorm.md 패턴 변경
  ├── 1.2 plan.md 패턴 변경
  ├── 1.3 research.md 패턴 변경
  ├── 1.4 analyze.md 패턴 변경
  └── 1.5 design.md 패턴 추가

Phase 2 (독립, 병렬 가능):
  ├── 2.1 workflow.md 경로 변경
  ├── 2.2 index-repo.md 경로 변경
  ├── 2.3 index.md 경로 변경
  ├── 2.4 build.md 경로 변경
  ├── 2.5 test.md 경로 변경
  └── 2.6 spawn.md 경로 변경

Phase 3 (Phase 1 이후):
  └── 3.2 cleanup.md --type docs 추가

Phase 4:
  └── Validation (uv run pytest)
```

Phase 1과 2는 서로 독립적이므로 동시 실행 가능.

---

## Non-Goals (discovery에서 승계)

- 기존 문서 자동 마이그레이션 (프로젝트별 판단)
- `/sc:design`의 project-specific artifacts 표준화 (ARCHITECTURE.md 등)
- `/sc:document`의 project-specific artifacts 표준화 (API.md 등)
- Frontmatter를 활용한 검색/필터링 도구
