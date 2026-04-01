---
status: draft
revised: 2026-04-01
---

# Doc Output Convention v2

SuperClaude 문서 출력 시스템의 명명 규칙과 디렉토리 구조를 정의합니다.
모든 프로젝트에 범용으로 적용되는 convention입니다.

## Decisions

| # | 항목 | 결정 | 근거 |
|---|------|------|------|
| B | 날짜 위치 | 끝 | topic-first로 내용 기반 탐색에 유리 |
| G | suffix | 공유 디렉토리만 | 디렉토리가 이미 type을 나타내면 suffix는 중복 |
| H | username | 항상 포함 | 범용 convention, 팀 프로젝트 지원 |
| L | living docs 위치 | 전부 `docs/` 아래 | "생성 파일은 모두 docs/" 단일 규칙 |
| N1 | living docs 네이밍 | UPPER_SNAKE | 생성 파일 vs 수동 파일 즉시 구분 |
| O2b | frontmatter | specs/, plans/ 필수 | 갱신되는 문서만 추적, snapshot은 자유 |
| R | 레거시 | 새 문서만 규정 | convention은 규격, 마이그레이션은 프로젝트별 판단 |
| S2 | formatter | `/sc:cleanup --type docs` | 기존 cleanup 커맨드 확장, 새 커맨드 불필요 |

## Naming Convention

### Dated Documents

문서를 생성하는 커맨드가 사용하는 파일명 패턴:

```
<topic-slug>-<suffix?>-<username>-YYYY-MM-DD.md
```

| 구성 요소 | 규칙 |
|-----------|------|
| `topic-slug` | lowercase, hyphens (e.g., `auth-redesign`) |
| `suffix` | 공유 디렉토리일 때만 포함 (아래 표 참조) |
| `username` | `git config user.name` → lowercase, no spaces. fallback: system username |
| `YYYY-MM-DD` | 생성일 (immutable — 수정해도 파일명 날짜는 변경하지 않음) |

### Suffix Rules

디렉토리에 2개 이상 type이 공존하면 suffix로 구분. 단독이면 생략.

| 디렉토리 | 커맨드 | suffix | 예시 |
|----------|--------|--------|------|
| `docs/specs/` | brainstorm | `-discovery` | `auth-redesign-discovery-kim-2026-04-01.md` |
| `docs/specs/` | design | `-design` | `auth-redesign-design-park-2026-04-03.md` |
| `docs/plans/` | plan | (없음) | `auth-redesign-park-2026-04-02.md` |
| `docs/plans/` | workflow | `-workflow` | `auth-redesign-workflow-park-2026-04-02.md` |
| `docs/research/` | research | (없음) | `context-fork-architecture-ajitta-2026-03-28.md` |
| `docs/analysis/` | analyze | (없음) | `api-latency-chosh1179-2026-04-01.md` |

### Living Documents

커맨드가 반복 실행할 때마다 덮어쓰는 파일. 날짜/username 없음.

```
UPPER_SNAKE_CASE.md
```

| 파일 | 생성 커맨드 | 위치 |
|------|------------|------|
| `PROJECT_INDEX.md` | `/sc:index-repo` | `docs/reports/` |
| `PROJECT_INDEX.json` | `/sc:index-repo` | `docs/reports/` |
| `KNOWLEDGE.md` | `/sc:index` | `docs/reports/` |
| `WORKFLOW.md` | `/sc:workflow` | `docs/reports/` |
| `WORKFLOW_STATUS.md` | `/sc:workflow` | `docs/reports/` |
| `BUILD_REPORT.md` | `/sc:build` | `docs/reports/` |
| `CLEANUP_REPORT.md` | `/sc:cleanup` | `docs/reports/` |
| `SPAWN_PLAN.md` | `/sc:spawn` | `docs/reports/` |
| `SPAWN_RESULT.md` | `/sc:spawn` | `docs/reports/` |
| `TEST_REPORT.md` | `/sc:test` | `docs/reports/` |

### Command-Specific Artifacts

특정 커맨드가 생성하는 부산물. Living docs와 같은 UPPER_SNAKE 규칙.

| 커맨드 | artifacts | 위치 |
|--------|-----------|------|
| `/sc:build` | `BUILD_DEV.log`, `BUILD_TEST.log` | `docs/reports/` |
| `/sc:test` | `TEST_UNIT.log`, `TEST_E2E.log` | `docs/reports/` |
| `/sc:cleanup` | `CLEANUP_CODE.md`, `CLEANUP_IMPORTS.md`, `CLEANUP_FILES.md` | `docs/reports/` |
| `/sc:design` | `ARCHITECTURE.md`, `API_SPEC.md`, `SCHEMA.md`, `ERD.md` 등 | project-specific (convention 범위 밖) |
| `/sc:document` | `API.md`, `GUIDE.md`, `{component}_DOCS.md` | project-specific (convention 범위 밖) |

## Directory Structure

```
project-root/
├── README.md, CLAUDE.md, ...        ← 프로젝트 설정 파일만
└── docs/
    ├── specs/                        ← brainstorm (-discovery), design (-design)
    ├── plans/                        ← plan (no suffix), workflow (-workflow)
    ├── research/                     ← research (no suffix)
    ├── analysis/                     ← analyze (no suffix)
    ├── reports/                      ← living docs + command artifacts
    └── reference/                    ← guides, troubleshooting, developer docs
```

**규칙: 루트에는 생성 파일을 두지 않는다.** 모든 커맨드 출력은 `docs/` 아래.

## Frontmatter

### 필수 (specs/, plans/)

갱신이 일어나는 문서에는 frontmatter를 포함합니다:

```yaml
---
status: draft
revised: 2026-04-01
---
```

| 필드 | 값 | 설명 |
|------|------|------|
| `status` | `draft` → `review` → `approved` → `in-progress` → `done` → `archived` | 문서 상태 |
| `revised` | `YYYY-MM-DD` | 마지막 수정일 (파일명 날짜와 독립) |

### 선택 (research/, analysis/)

Snapshot 성격의 문서는 frontmatter가 없어도 됩니다. 필요하면 같은 형식으로 추가.

### Frontmatter 없음 (reports/)

Living docs는 frontmatter를 사용하지 않습니다 (매번 덮어써서 status 추적이 무의미).

## Formatter

`/sc:cleanup --type docs`로 convention 준수를 검사하고 자동 변환합니다.

### Validation Rules

1. Dated docs: `<topic>-<suffix?>-<username>-YYYY-MM-DD.md` 패턴 검사
2. 올바른 디렉토리에 위치하는지 확인
3. 공유 디렉토리 문서에 suffix가 있는지 확인
4. specs/, plans/ 문서에 frontmatter가 있는지 확인
5. Living docs가 `docs/reports/`에 있는지 확인

### Transformation Rules

Old → New 변환:

```
# 날짜 위치 변환 (앞 → 끝)
2026-03-20-selection-protocol-design-ajitta.md
→ selection-protocol-design-ajitta-2026-03-20.md

# 중복 suffix 제거 (단독 디렉토리)
docs/research/context-fork-architecture-research-ajitta-2026-03-28.md
→ docs/research/context-fork-architecture-ajitta-2026-03-28.md

# 루트 living docs 이동
PROJECT_INDEX.md → docs/reports/PROJECT_INDEX.md

# username 누락 보완 (git log에서 추출)
2026-03-15-opus46-alignment-design.md
→ opus46-alignment-design-<author>-2026-03-15.md
```

### Dry Run

```bash
/sc:cleanup --type docs --dry-run
```

변경 사항을 미리 보여주고, 확인 후 실행.

## Migration Scope

이 convention은 **새 문서에만 적용**됩니다.
기존 문서의 마이그레이션은 프로젝트별로 판단합니다.
`/sc:cleanup --type docs`를 사용하면 기존 문서도 자동 변환할 수 있습니다.

## RULES.md 변경 사항

현재 `doc_output_convention` 섹션을 이 스펙에 맞게 교체합니다:

```xml
<doc_output_convention note="Unified naming for all file-producing commands">
  Pattern: docs/<type>/<topic-slug>-<suffix?>-<username>-YYYY-MM-DD.md
  Username: `git config user.name` (lowercase, no spaces) — fallback to system username
  Directory: brainstorm→docs/specs/ | design→docs/specs/ | plan→docs/plans/ | workflow→docs/plans/ | analyze→docs/analysis/ | research→docs/research/
  Suffix (shared dirs only): brainstorm→-discovery | design→-design | workflow→-workflow
  Living docs (UPPER_SNAKE, no date/username): all in docs/reports/
  Frontmatter: specs/+plans/ require {status, revised}. research/+analysis/ optional
  Formatter: /sc:cleanup --type docs (validate + transform + migrate)
  Example: docs/specs/selection-protocol-design-ajitta-2026-03-20.md
</doc_output_convention>
```

## Commands to Update

이 convention 적용 시 수정이 필요한 커맨드 목록:

| 커맨드 | 변경 내용 |
|--------|----------|
| `brainstorm.md` | 출력 경로 패턴 변경, suffix `-discovery` 적용 |
| `plan.md` | 출력 경로 패턴 변경, frontmatter 생성 추가 |
| `design.md` | 출력 경로 패턴 추가 (현재 미정의) |
| `research.md` | 출력 경로 패턴 변경, suffix 제거 |
| `analyze.md` | 출력 경로 패턴 변경, suffix 제거 |
| `workflow.md` | living docs 경로를 `docs/reports/`로 변경 |
| `index-repo.md` | living docs 경로를 `docs/reports/`로 변경 |
| `index.md` | living docs 경로를 `docs/reports/`로 변경 |
| `build.md` | artifacts 경로를 `docs/reports/`로 변경 |
| `test.md` | artifacts 경로를 `docs/reports/`로 변경 |
| `cleanup.md` | `--type docs` 추가, artifacts 경로 변경 |
| `spawn.md` | living docs 경로를 `docs/reports/`로 변경 |
| `core/RULES.md` | `doc_output_convention` 섹션 교체 |

## Non-Goals

- 기존 문서 자동 마이그레이션 (프로젝트별 판단)
- `/sc:design`의 project-specific artifacts 표준화 (ARCHITECTURE.md 등)
- `/sc:document`의 project-specific artifacts 표준화 (API.md 등)
- Frontmatter를 활용한 검색/필터링 도구
