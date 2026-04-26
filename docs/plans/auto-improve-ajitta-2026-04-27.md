---
status: draft
revised: 2026-04-27
---

# `/sc:auto-improve` Implementation Plan

**Goal**: Karpathy AutoResearch 응용 자율 코드베이스 개선 루프를 SuperClaude `/sc:auto-improve` command로 구현 (v0.1 MVP).

**Architecture**: CC-native command markdown이 사용자 진입점 + Python 워커(`scripts/auto_improve/`)가 백그라운드 루프 실행. 단일 git lineage worktree에서 Mutator sub-agent가 LLM 자유 mutation, EvalRunner가 shell-driven 객관 메트릭 측정, 4중 guard로 무인 안전성 보장.

**Tech Stack**: Python 3.10+, UV, pytest, Claude Agent SDK, jmespath (jq-style 추출), git worktree, ruff.

**Source spec**: `docs/specs/auto-improve-design-ajitta-2026-04-27.md` (10/10 커버리지)
**Branch**: `feat/auto-improve` ← `master`
**Test baseline**: 1,628 passing → 1,628+N (N=신규, 회귀 0)

---

## Validation (--validate, pre-execution)

| Risk | Assessment |
|------|-----------|
| **Agent SDK 통합 검증 부재** | 0.7 — Mutator가 SDK API 변경에 취약. Phase 3에 격리 테스트 필요 |
| **jmespath 의존성 추가** | 0.3 — 순수 Python, 안정적 라이브러리 |
| **git worktree edge cases** | 0.5 — 실 git CLI 의존, integration test 필수 (Phase 5) |
| **Test baseline 회귀** | 0.4 — 격리 디렉토리(`scripts/auto_improve/`)에 추가, 기존 영향 최소 |
| **Plan-스펙 불일치 발견 시** | 회귀 시 spec v1.4로 복귀, 본 plan revise |

**전체 위험**: 0.5 (medium). 각 phase 종료마다 `make test` 통과 확인. Phase 3 (Mutator)에서 Agent SDK가 예상과 다르면 Phase 3 재설계 후 후속 phase 재정렬.

---

## File Map

### Create (신규 13)
```
src/superclaude/commands/auto-improve.md
src/superclaude/scripts/auto_improve/__init__.py
src/superclaude/scripts/auto_improve/coordinator.py
src/superclaude/scripts/auto_improve/worktree.py
src/superclaude/scripts/auto_improve/eval_runner.py
src/superclaude/scripts/auto_improve/guards.py
src/superclaude/scripts/auto_improve/results_tsv.py
src/superclaude/scripts/auto_improve/mutator.py
src/superclaude/scripts/auto_improve/reporter.py
tests/unit/scripts/auto_improve/__init__.py
tests/unit/scripts/auto_improve/test_results_tsv.py
tests/unit/scripts/auto_improve/test_worktree.py
tests/unit/scripts/auto_improve/test_eval_runner.py
tests/unit/scripts/auto_improve/test_guards.py
tests/unit/scripts/auto_improve/test_coordinator.py
tests/integration/auto_improve/test_e2e_smoke.py
```

### Modify (2)
```
src/superclaude/commands/README.md       (auto-improve 행 추가)
pyproject.toml                            (jmespath 의존성)
```

---

## Phase 1: Foundation — Schema + Worktree

**Commit**: `feat(auto-improve): scaffold scripts dir + results.tsv schema + worktree manager`

### Task 1.1: 스켈레톤 + dependency
**Files**: Create `scripts/auto_improve/__init__.py`, `tests/unit/scripts/auto_improve/__init__.py`. Modify `pyproject.toml` (add `jmespath>=1.0`).
- [ ] Add `jmespath` to `[project.dependencies]`
- [ ] Run `uv pip install -e ".[dev]"`
- [ ] Verify `make test` passes (baseline 1,628)
- [ ] Commit

### Task 1.2: results.tsv I/O (TDD)
**Files**: Create `scripts/auto_improve/results_tsv.py`, `tests/unit/scripts/auto_improve/test_results_tsv.py`
- [ ] Test: `test_writes_header_on_init` (8-column header per design §4)
- [ ] Test: `test_appends_row_with_all_columns`
- [ ] Test: `test_rejects_empty_desc` (R3 normative — empty desc → ValueError)
- [ ] Test: `test_status_enum_validation` (baseline/improved/regressed/smoke_fail/eval_timeout/mutation_error)
- [ ] Verify all tests fail (red)
- [ ] Implement `ResultsTsv` class with `init(path)`, `append(row: ResultRow)`, `read_all() -> list[ResultRow]`
- [ ] Verify all pass (green) + `make test` (1,628 + 4)

### Task 1.3: Worktree manager (TDD)
**Files**: Create `scripts/auto_improve/worktree.py`, `tests/unit/scripts/auto_improve/test_worktree.py`
- [ ] Test: `test_create_worktree_at_expected_path` (`<repo>/.worktrees/auto-improve-<timestamp>/`)
- [ ] Test: `test_cleanup_removes_worktree`
- [ ] Test: `test_init_creates_results_tsv_inside_worktree`
- [ ] Test: `test_main_repo_unmodified_after_create_cleanup`
- [ ] Verify red, implement using `subprocess.run(["git", "worktree", ...])`, verify green
- [ ] `make test` passes (1,628 + 8)

---

## Phase 2: Pure Logic — EvalRunner + Guards

**Commit**: `feat(auto-improve): eval runner + 4-guard logic with isolated tests`

### Task 2.1: EvalRunner (TDD)
**Files**: Create `scripts/auto_improve/eval_runner.py`, `tests/unit/scripts/auto_improve/test_eval_runner.py`
- [ ] Test: `test_extracts_jmespath_from_json_stdout` (e.g., `--metric '.passed'` from `{"passed": 42}`)
- [ ] Test: `test_returns_none_value_on_extraction_failure` (malformed JSON, missing key)
- [ ] Test: `test_enforces_timeout_kills_subprocess`
- [ ] Test: `test_captures_exit_code_and_wall_seconds`
- [ ] Implement `run_eval(cmd, metric_path, timeout) -> EvalResult`
- [ ] Verify green + `make test` (1,628 + 12)

### Task 2.2: Guards (TDD)
**Files**: Create `scripts/auto_improve/guards.py`, `tests/unit/scripts/auto_improve/test_guards.py`
- [ ] Test: `BudgetGuard` — `pass=True` before deadline, `False` after
- [ ] Test: `PlateauDetector` — 5회 비개선 → fail; 5회 중 1회 개선 → pass + window reset
- [ ] Test: `RegressionBlock` — score < baseline → fail; score >= baseline → pass
- [ ] Test: `SmokeGate` — custom smoke_cmd 사용; 미지정 시 eval_cmd timeout 30s fallback
- [ ] Test: `GuardVerdict` 균일 인터페이스 (pass: bool, reason: str)
- [ ] Implement 4 guard 클래스 + 공통 인터페이스
- [ ] Verify green + `make test` (1,628 + 17)

---

## Phase 3: Mutator (Agent SDK 통합) — 위험 phase

**Commit**: `feat(auto-improve): mutator agent wrapper with Bash-stripped tool surface`

### Task 3.1: Mutator wrapper (TDD)
**Files**: Create `scripts/auto_improve/mutator.py`, `tests/unit/scripts/auto_improve/test_mutator.py`
- [ ] Test: `test_mutator_calls_agent_sdk_with_sonnet_default` (mock SDK)
- [ ] Test: `test_mutator_strips_bash_from_tools` (R2 v0.1 가드 — Bash 차단 검증)
- [ ] Test: `test_mutator_passes_worktree_as_cwd` (D1 위험 완화)
- [ ] Test: `test_mutator_returns_rationale_files_tokens`
- [ ] Test: `test_mutator_returns_error_on_empty_rationale` (R3 normative)
- [ ] Test: `test_mutator_model_override_via_arg`
- [ ] Implement `mutate(worktree_path, model="sonnet-4-6") -> MutationResult` 사용 anthropic Agent SDK
- [ ] Verify green + `make test` (1,628 + 23)

**Phase 3 위험 게이트**: Agent SDK API가 예상과 다르면 (signature 변경, tool 제어 방법 등) 본 phase 정지 후 plan revise. master 머지 시 다른 phase 영향 없음 — 격리 디렉토리.

---

## Phase 4: Coordinator + Reporter

**Commit**: `feat(auto-improve): state machine coordinator + morning summary reporter`

### Task 4.1: Reporter (TDD — coordinator 종속성 적음, 먼저)
**Files**: Create `scripts/auto_improve/reporter.py`, `tests/unit/scripts/auto_improve/test_reporter.py`
- [ ] Test: `test_morning_summary_from_empty_tsv` ("not running, no history")
- [ ] Test: `test_morning_summary_with_n_cycles_shows_best_metric_and_delta`
- [ ] Test: `test_status_mode_uses_pid_file_to_detect_active_run`
- [ ] Implement `morning_summary(tsv_path, pid_path) -> str` (markdown stdout)
- [ ] Verify green + `make test` (1,628 + 26)

### Task 4.2: Coordinator state machine (TDD)
**Files**: Create `scripts/auto_improve/coordinator.py`, `tests/unit/scripts/auto_improve/test_coordinator.py`
- [ ] Test: `test_phase0_dry_run_baseline_records_cycle_id_zero`
- [ ] Test: `test_phase0_failure_exits_nonzero_no_loop_entry` (I4)
- [ ] Test: `test_loop_aborts_on_budget_exceeded`
- [ ] Test: `test_loop_aborts_on_5_stale_plateau`
- [ ] Test: `test_regressed_score_does_not_commit`
- [ ] Test: `test_smoke_fail_skips_cycle_no_mutation_attempted`
- [ ] Test: `test_each_cycle_writes_exactly_one_results_tsv_row` (불변식)
- [ ] Test: `test_status_mode_skips_loop_runs_reporter_only`
- [ ] Test: `test_pid_file_written_on_loop_start_removed_on_exit`
- [ ] Implement state machine: `INIT → CONFIRM → BASELINE → LOOP → REPORT` + `status_mode()`
- [ ] Verify green + `make test` (1,628 + 35)

---

## Phase 5: Command MD + Integration + Docs

**Commit**: `feat(auto-improve): CC command entry + e2e smoke test + README`

### Task 5.1: Command markdown
**Files**: Create `src/superclaude/commands/auto-improve.md`. Modify `src/superclaude/commands/README.md` (table 행 추가).
- [ ] Frontmatter: `description: Autonomous overnight code improvement loop driven by objective metric` (≥10 chars, action-oriented)
- [ ] XML: `<component name="auto-improve" type="command">` + role/syntax/flow/outputs/tools/gotchas/examples/bounds/handoff
- [ ] flow에 Phase 0 confirm + Python 워커 spawn + --status 분기 명시
- [ ] gotchas에 R1 (`/sc:improve`와 혼동), D3 (CC 세션 종료 후 워커 생존)
- [ ] Verify: `uv run pytest tests/unit/test_command_structure.py -v` (XML 구조 검증)
- [ ] Verify: `make deploy` 후 `~/.claude/commands/auto-improve.md` 존재 확인

### Task 5.2: Integration smoke test
**Files**: Create `tests/integration/auto_improve/test_e2e_smoke.py`
- [ ] Test: `test_e2e_dry_run_baseline_then_one_cycle` — temp git repo, simple eval-cmd (`echo '{"passed":1}'`), single cycle, mock Mutator
- [ ] Test: `test_status_mode_after_no_run_returns_clean_message`
- [ ] Verify green + `make test` (1,628 + 37)

### Task 5.3: README + commands README
**Files**: Modify `README.md` (project root, "Commands" 섹션에 한 줄), `src/superclaude/commands/README.md` (table 행).
- [ ] auto-improve 한 줄 설명 + 도움말 차별화 텍스트 (R1: "Interactive: /sc:improve | Autonomous overnight: /sc:auto-improve")
- [ ] Verify `make verify`

### Final verification
- [ ] `make lint` (ruff clean)
- [ ] `make test` final: 1,628 + 37 = **1,665 passing, 0 regressions**
- [ ] `make deploy` (CLI editable install)
- [ ] Manual smoke: `/sc:auto-improve <test-repo> --eval-cmd 'echo {"passed":1}' --metric '.passed' --budget 1m --dry-run` 단일 baseline 통과 확인

---

## Self-Review Iteration Log (--loop)

| Version | Date | Reviewer | Outcome | Delta |
|---------|------|----------|---------|-------|
| v1 | 2026-04-27 | self (--loop iter 1) | initial | 5-phase 분해, --validate risk 0.5 |
| v1.1 | 2026-04-27 | self (--loop iter 2) | gap closure | Phase 3에 위험 게이트 추가 (Agent SDK API mismatch 시 plan revise 절차); Phase 5 final verification에 manual smoke 추가; Task 1.1에 baseline 1,628 검증 명시 |

**Loop 종료 조건 도달**: iter 2 후 의미있는 추가 갭 없음. 아래 항목은 implement 단계에서 자연스럽게 해결될 것:
- jmespath import 경로의 정확한 spelling — Phase 1 import 시점에 결정
- Agent SDK 정확한 함수 시그니처 — Phase 3 첫 테스트에서 mock 작성 시 결정
- README.md 수정 위치 (Commands 섹션) — Phase 5 시점에 grep으로 위치 확인

---

## Handoff

> **`/sc:implement --plan docs/plans/auto-improve-ajitta-2026-04-27.md`** — Phase 1부터 순차 실행. 각 phase 종료 시 commit + `make test` baseline 검증.

권장 모델: Phase 1-2 (pure logic) Sonnet 4.6 충분. Phase 3 (Agent SDK) Opus 4.7 권장 (외부 API 통합 디버깅 복잡). Phase 4-5 Sonnet 4.6.
