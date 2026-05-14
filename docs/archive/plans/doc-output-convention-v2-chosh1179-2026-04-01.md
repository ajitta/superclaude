---
status: done
revised: 2026-04-01
---

# Doc Output Convention v2 Implementation Plan

**Goal:** 13개 커맨드/코어 파일의 문서 출력 패턴을 v2 convention으로 변경
**Architecture:** 마크다운 파일의 문자열 교체 (코드 변경 없음)
**Spec:** `docs/specs/doc-output-convention-v2-design-chosh1179-2026-04-01.md`

---

## Phase 1: Dated Document Commands + RULES.md (6 tasks, 병렬 가능)

### Task 1: RULES.md — doc_output_convention 교체
**Files:** Modify: `src/superclaude/core/RULES.md:102-109`
- [x] `doc_output_convention` 섹션 전체 교체 (7개 변경 포인트)
- [x] 변경: Pattern 날짜→끝, Suffix→shared only, Living docs→docs/reports/, Frontmatter 추가, Formatter 추가, Example 갱신

### Task 2: brainstorm.md — 패턴 변경 + suffix 수정
**Files:** Modify: `src/superclaude/commands/brainstorm.md:19,27`
- [x] line 19: `docs/specs/YYYY-MM-DD-<topic>-design-<username>.md` → `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md`
- [x] line 19: frontmatter 지시 추가 `(with frontmatter: status: draft, revised: <today>)`
- [x] line 27: outputs table 동일하게 변경

### Task 3: plan.md — 패턴 변경 + frontmatter 지시
**Files:** Modify: `src/superclaude/commands/plan.md:18,25`
- [x] line 18: `docs/plans/YYYY-MM-DD-<feature-name>-<username>.md` → `docs/plans/<feature-name>-<username>-YYYY-MM-DD.md`
- [x] line 18: frontmatter 지시 추가
- [x] line 25: outputs table 동일하게 변경

### Task 4: research.md — 패턴 변경 + suffix 제거
**Files:** Modify: `src/superclaude/commands/research.md:18`
- [x] `docs/research/YYYY-MM-DD-<topic>-research-<username>.md` → `docs/research/<topic>-<username>-YYYY-MM-DD.md`

### Task 5: analyze.md — 패턴 변경 + suffix 제거
**Files:** Modify: `src/superclaude/commands/analyze.md:26-27`
- [x] line 26 (json): `docs/analysis/YYYY-MM-DD-<target>-analysis-<username>.json` → `docs/analysis/<target>-<username>-YYYY-MM-DD.json`
- [x] line 27 (report): `docs/analysis/YYYY-MM-DD-<target>-analysis-<username>.md` → `docs/analysis/<target>-<username>-YYYY-MM-DD.md`

### Task 6: design.md — dated output 패턴 추가
**Files:** Modify: `src/superclaude/commands/design.md`
- [x] outputs table에 design spec 행 추가: `docs/specs/<topic>-design-<username>-YYYY-MM-DD.md`
- [x] flow에 save step 추가 (frontmatter 지시 포함)

---

## Phase 2: Living Document Commands (6 tasks, 병렬 가능)

모든 living docs/artifacts 경로에 `docs/reports/` prefix 추가.

### Task 7: workflow.md — 경로 변경
**Files:** Modify: `src/superclaude/commands/workflow.md:24,26`
- [x] `WORKFLOW.md` → `docs/reports/WORKFLOW.md`
- [x] `WORKFLOW_STATUS.md` → `docs/reports/WORKFLOW_STATUS.md`

### Task 8: index-repo.md — 경로 변경
**Files:** Modify: `src/superclaude/commands/index-repo.md:17-18`
- [x] `PROJECT_INDEX.md` → `docs/reports/PROJECT_INDEX.md`
- [x] `PROJECT_INDEX.json` → `docs/reports/PROJECT_INDEX.json`

### Task 9: index.md — 경로 변경
**Files:** Modify: `src/superclaude/commands/index.md:24-26`
- [x] `KNOWLEDGE.md` → `docs/reports/KNOWLEDGE.md`
- [x] `API.md` → `docs/reports/API.md`
- [x] `STRUCTURE.md` → `docs/reports/STRUCTURE.md`
- [x] `README.md`는 루트 유지 (변경 없음)

### Task 10: build.md — 경로 변경
**Files:** Modify: `src/superclaude/commands/build.md:24-26`
- [x] `BUILD_DEV.log` → `docs/reports/BUILD_DEV.log`
- [x] `BUILD_REPORT.md` → `docs/reports/BUILD_REPORT.md`
- [x] `BUILD_TEST.log` → `docs/reports/BUILD_TEST.log`
- [x] `dist/` 디렉토리는 변경 없음

### Task 11: test.md — 경로 변경
**Files:** Modify: `src/superclaude/commands/test.md:25-27`
- [x] `TEST_UNIT.log` → `docs/reports/TEST_UNIT.log`
- [x] `TEST_E2E.log` → `docs/reports/TEST_E2E.log`
- [x] `TEST_REPORT.md` → `docs/reports/TEST_REPORT.md`
- [x] `coverage/`는 변경 없음

### Task 12: spawn.md — 경로 변경
**Files:** Modify: `src/superclaude/commands/spawn.md:25-26`
- [x] `SPAWN_PLAN.md` → `docs/reports/SPAWN_PLAN.md`
- [x] `SPAWN_RESULT.md` → `docs/reports/SPAWN_RESULT.md`

---

## Phase 3: Cleanup Command Extension (1 task)

### Task 13: cleanup.md — `--type docs` 추가
**Files:** Modify: `src/superclaude/commands/cleanup.md:10,20-27,39-43,46-54`
- [x] syntax: `code|imports|files|all` → `code|imports|files|docs|all` + `[--dry-run]` 추가
- [x] outputs table: `docs` 행 추가 + 기존 경로에 `docs/reports/` prefix
- [x] patterns: `Docs: Convention validation → rename + move (--dry-run supported)` 추가
- [x] examples: `--type docs --dry-run` + `--type docs` 예시 추가

---

## Phase 4: Validation

### Task 14: 테스트 실행
- [x] `uv run pytest tests/unit/test_command_structure.py -v` — 462 passed ✓
- [x] `uv run pytest tests/unit/ -v` — 1623 passed, 63 skipped, 0 failed ✓
- [x] 6 collection errors는 pre-existing (우리 변경과 무관)

---

## Verification

```bash
# Phase 4에서 실행
uv run pytest tests/unit/test_command_structure.py -v
uv run pytest tests/unit/ -v
```

성공 기준: 기존 테스트 pass count 유지 (baseline: ~1,694 passing)
