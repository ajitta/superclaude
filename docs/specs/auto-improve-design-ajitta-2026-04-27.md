---
status: draft
revised: 2026-04-27
---

# `/sc:auto-improve` — Architecture Design

**Source spec**: `docs/specs/auto-improve-discovery-ajitta-2026-04-27.md` (v1.4, status: approved-for-plan)
**Type**: architecture
**Scope**: v0.1 MVP design + 3 deferred OQ resolution

## 1. Resolved Open Questions

| OQ | Question | Decision | Rationale |
|----|----------|----------|-----------|
| **OQ1** | Coordinator 구현체 = 신규 Python module vs SC agent | **command markdown + `src/superclaude/scripts/auto_improve/` Python 워커** (하이브리드) | 워크플로 정의 = command markdown (CC-native), 장시간 루프 + I/O = Python script. Command은 인자 파싱 + 워커 spawn만 |
| **OQ2** | Mutator agent 모델 정책 | **default = Sonnet 4.6**, `--mutator-model` 인자로 오버라이드 (opus/sonnet/haiku) | 비용·속도·품질 중간점. 임의 코드 수정에는 Sonnet 4.6 충분. 복잡한 도메인은 Opus 4.7로 업그레이드 가능 |
| **OQ3** | results.tsv 정확한 스키마 | **고정 8컬럼** (아래 §4) | spec v1.4의 컬럼 + cycle_id/timestamp 보강. 추가 컬럼은 v0.2 예약 |
| **OQ4** | `--eval-cmd` 사이클 타임아웃 정책 | **`--cycle-timeout` 인자 (default 600s)** + 사이클당 hard kill | budget/expected_cycles로 추정 가능하나 명시 인자가 안전 |
| **OQ5** | 진척률 외부 노출 | **v0.1 = `/sc:auto-improve --status`** (같은 command 재진입, results.tsv 요약 출력). 별도 `/sc:status` 미생성 | R18 — 별도 command 신설은 진입점 분산. 같은 command의 sub-mode가 단순 |
| **R1** | `/sc:improve` 명령 충돌 | **(a) 도움말 차별화 + 별도 command 유지** | (b) alias는 SC 컨벤션 미지원 (filename = name). (c) 흡수는 인터랙티브 `/sc:improve` 의미 변형 — 사용자 혼란. (a)가 최소 침습 |

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│ User: /sc:auto-improve <project> --eval-cmd <sh> --metric <jq> │
│                       --budget 8h --scope 'src/**' [--status]  │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │  src/superclaude/commands/    │
                │       auto-improve.md         │  ← CC-native command (workflow spec)
                │  - 인자 파싱 + 검증           │
                │  - Phase 0 사용자 confirm     │
                │  - Python 워커 spawn          │
                │  - --status 분기              │
                └──────────────┬────────────────┘
                               │ subprocess
                               ▼
        ┌──────────────────────────────────────────┐
        │ src/superclaude/scripts/auto_improve/    │
        │   coordinator.py    ← main loop          │
        │   ├── worktree.py   ← create/cleanup     │
        │   ├── eval_runner.py← shell + jq parse   │
        │   ├── guards.py     ← 4-guard impl       │
        │   ├── results_tsv.py← state store I/O    │
        │   ├── mutator.py    ← Agent SDK wrapper  │
        │   └── reporter.py   ← morning summary    │
        └──────────────┬───────────────────────────┘
                       │ spawns isolated agent
                       ▼
            ┌────────────────────────────┐
            │ Mutator Sub-Agent          │ ← Claude Agent SDK call
            │  (Sonnet 4.6 default)      │   in worktree CWD
            │  - reads git log + tsv     │
            │  - proposes mutation       │
            │  - applies file changes    │
            │  - returns rationale       │
            └────────────────────────────┘
                       │ writes
                       ▼
            ┌────────────────────────────┐
            │ git worktree (isolated)    │
            │  ├── .git/ (single branch) │
            │  └── results.tsv           │ ← single source of truth
            └────────────────────────────┘
```

## 3. Component Specs (R18 Necessity Test 적용)

### 3.1 Command markdown (`commands/auto-improve.md`)
- **Necessity**: 핵심 — CC-native 진입점. 없으면 사용자가 호출 불가.
- **Responsibility**: 인자 파싱, Phase 0 사용자 confirm 표시, 코드네이터 spawn, --status 분기
- **인터페이스**:
  ```
  /sc:auto-improve <project_path>
    --eval-cmd <shell-cmd>      # required
    --metric <jq-expression>     # required (default: '.passed')
    --budget <duration>          # default: 8h
    --scope <glob-pattern>       # default: '**'
    --smoke-cmd <shell-cmd>      # optional, fallback: eval-cmd timeout 30s
    --cycle-timeout <seconds>    # default: 600
    --mutator-model <name>       # default: sonnet-4-6
    --status                     # display mode (no loop)
    --dry-run                    # baseline only, no mutations
  ```

### 3.2 Coordinator (`coordinator.py`)
- **Necessity**: 핵심 — 루프 제어자. 없으면 sub-component들이 독립 동작 못 함.
- **Responsibility**: Phase 0 (dry-run baseline) → Phase 1 (mutation loop) → Phase 2 (morning summary)
- **State machine**:
  ```
  INIT → CONFIRM → BASELINE → LOOP[smoke→mutate→eval→commit/rollback] → REPORT
            │           │             │
            └─ abort    └─ exit≠0     └─ plateau/budget/regression → REPORT
  ```

### 3.3 Worktree Manager (`worktree.py`)
- **Necessity**: 핵심 — Q2.1 결정 (worktree 격리). 없으면 main repo 오염.
- **Responsibility**: `git worktree add` / `remove`, scope glob enforcement
- **불변식**: 루프 동안 main repo의 작업 디렉토리는 절대 변경 금지

### 3.4 Eval Runner (`eval_runner.py`)
- **Necessity**: 핵심 — Q2.3 결정. 없으면 메트릭 추출 불가.
- **Responsibility**: shell 실행, stdout JSON 캡처, jq-style 추출, 타임아웃 enforcement
- **인터페이스**: `run_eval(cmd: str, metric_path: str, timeout: int) -> EvalResult{value, exit_code, wall_seconds, stderr}`

### 3.5 Guards (`guards.py`)
- **Necessity**: 핵심 — Q2.4 4중 가드 모두 v0.1 must-have.
- **Subcomponents**:
  - `BudgetGuard(deadline)` — wall clock 비교
  - `PlateauDetector(window=5)` — 5회 비개선 감지
  - `RegressionBlock(baseline)` — `score < baseline` 시 rollback 신호
  - `SmokeGate(cmd, fallback_eval_cmd)` — 사이클 진입 전 검사

### 3.6 Results.tsv I/O (`results_tsv.py`)
- **Necessity**: 핵심 — Q3.2 + R3 (`desc` normative).
- **Responsibility**: append-only 쓰기 (단일 writer 전제), 스키마 §4 enforce
- **불변식**: 매 mutation 시도당 정확히 1행

### 3.7 Mutator Agent (`mutator.py`)
- **Necessity**: 핵심 — Q3.3 LLM 자유 mutation, G4 정의의 일부.
- **Responsibility**: Agent SDK 호출 wrapper. system prompt에 "git log + results.tsv 읽고 다음 mutation 제안" 명령. Tool: Edit/Write 한정 (Bash 차단).
- **인터페이스**: `mutate(worktree_path, model) -> MutationResult{rationale, files_changed, tokens_used}`

### 3.8 Reporter (`reporter.py`)
- **Necessity**: 핵심 — G1 ("morning에 결과 확인") 핵심 가치 충족.
- **Responsibility**: 종료 시 markdown 요약 stdout. `--status` 모드에서도 재사용.

### 3.9 Status mode (no separate component)
- **Necessity**: borderline — R18 적용. 별도 command 또는 daemon은 거부 (OQ5).
- **구현**: `coordinator.py status_mode()` 함수가 results.tsv 읽고 reporter.py 재사용.
- **현재 실행 중인 루프 감지**: PID 파일 (`<worktree>/.auto_improve.pid`)로 표시. 미존재 = "not running, last run summary".

### 3.10 Excluded (R18 거부)
- ❌ Web UI (spec NG5)
- ❌ Population/tournament (spec NG3)
- ❌ Named operator catalog (spec NG4)
- ❌ Sandbox network/FS isolator (v0.2)
- ❌ Daily cost limit env-var (v0.2)
- ❌ Daemon process for status (`tail -f` + sub-mode 충분)

## 4. Data Schema — `results.tsv`

| Column | Type | Source | Purpose |
|--------|------|--------|---------|
| `cycle_id` | int | coordinator | monotonic counter (0 = baseline dry-run) |
| `timestamp` | ISO8601 | coordinator | UTC, second precision |
| `commit_hash` | str(40) or `-` | git | `-` if rolled back |
| `metric_value` | float | eval_runner | jq 추출 결과 |
| `status` | enum | coordinator | `baseline` / `improved` / `regressed` / `smoke_fail` / `eval_timeout` / `mutation_error` |
| `desc` | str | mutator (R3) | mutation rationale, **비어 있으면 `mutation_error` 강제** |
| `tokens_used` | int | mutator | input + output, R6 v0.1 |
| `wall_seconds` | int | eval_runner | 사이클 실측 |

**파일 위치**: `<worktree>/results.tsv` (worktree 격리 일부 — main repo와 분리)
**헤더**: 첫 행 `# cycle_id\ttimestamp\tcommit_hash\tmetric_value\tstatus\tdesc\ttokens_used\twall_seconds`

## 5. Interface Contracts

### 5.1 CLI (사용자 진입점)
§3.1 참조.

### 5.2 Coordinator → Mutator
```python
@dataclass
class MutationResult:
    rationale: str          # results.tsv `desc` (필수, 비어 있으면 실패)
    files_changed: list[Path]
    tokens_used: int
    error: Optional[str]    # None on success
```

### 5.3 Coordinator → EvalRunner
```python
@dataclass
class EvalResult:
    metric_value: Optional[float]  # None on extraction failure
    exit_code: int
    wall_seconds: int
    stderr: str                    # 디버깅용, results.tsv에는 미저장
    timed_out: bool
```

### 5.4 Coordinator → Guards
각 guard는 `check(state) -> GuardVerdict{pass: bool, reason: str}` 균일 인터페이스.
실행 순서: Smoke → Mutator → Eval → Regression → (success) → Plateau check → Budget check.

## 6. Operational Constraints (R18 documented)

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Budget hard cap | `--budget` (default 8h) | spec G3 |
| Cycle timeout | `--cycle-timeout` (default 600s) | OQ4 |
| Plateau window | 5 cycles (고정) | spec Q2.4 |
| Smoke timeout (fallback) | 30s (고정) | spec v1.4 |
| results.tsv writer | 단일 (단일 lineage) | spec G4 |
| Mutator tool surface | Edit, Write만 (Bash 차단) | R2 완화 — agent가 외부 명령 실행 못 하게 |
| Worktree path | `<repo>/.worktrees/auto-improve-<timestamp>/` | main repo 분리 |

## 7. Validation — Requirements Coverage ≥ 90%

| Spec ID | Spec 요구 | Design 충족 |
|---------|----------|-------------|
| G1 도메인 무관 | shell-driven 메트릭 | ✅ §3.4 EvalRunner |
| G2 진입장벽 최소 | 2 인자 (`--eval-cmd`/`--metric`) | ✅ §3.1 |
| G3 무인 안전성 (4가드) | 시간/plateau/regression/smoke | ✅ §3.5 Guards |
| G3 한계 (eval-cmd 외부 작용) | 사용자 책임 명시 | ✅ §3.7 (Mutator Bash 차단) + Phase 0 confirm |
| G4 Karpathy 정신 | 단일 lineage + LLM 양역 + git/tsv | ✅ §3.3 + §3.6 + §3.7 |
| G5 SC 인프라 재활용 | command + Agent SDK | ✅ §3.1 + §3.7 |
| R2 v0.1 강제 가드 (3개) | dry-run + 경고 + G3 한계 | ✅ §3.2 Phase 0 + Bash 차단 |
| R3 desc normative | results.tsv `desc` 단일 source | ✅ §4 + §3.6 불변식 |
| R6 token logging | results.tsv 컬럼 | ✅ §4 `tokens_used` |
| OQ1-5 + R1 | 모두 해소 | ✅ §1 |

**커버리지**: 10/10 = 100%. 누락 spec 요구 없음.

## 8. Risks (Design 단계 신규 식별)

| ID | Risk | 완화 |
|----|------|-----|
| **D1** | Agent SDK가 worktree CWD를 정확히 sandbox하지 못 함 | 명시적 `cwd=worktree_path` 전달 + Mutator system prompt에 "DO NOT cd outside worktree" |
| **D2** | jq-style 추출 라이브러리 선택 (Python `jq` vs `jmespath` vs custom) | `jmespath` 추천 — 순수 Python, 의존성 가벼움 |
| **D3** | Python worker가 CC 세션 종료 시 함께 죽음 | `nohup`-style fork + PID 파일. CC 세션 무관하게 백그라운드 진행 |
| **D4** | results.tsv 스키마 변경 시 기존 파일 호환성 | header 첫 행 강제 + `# v0.1` 버전 마커 |
| **D5** | --status 모드와 진행 중 루프의 race | PID 파일 + atomic read of results.tsv |

## 9. Implementation Outline (for `/sc:plan`)

```
src/superclaude/
├── commands/
│   └── auto-improve.md              ← 신규 (XML template per command-authoring.md)
├── scripts/
│   └── auto_improve/                ← 신규 디렉토리
│       ├── __init__.py
│       ├── coordinator.py           ← main(): orchestrates state machine
│       ├── worktree.py
│       ├── eval_runner.py
│       ├── guards.py                ← BudgetGuard, PlateauDetector, RegressionBlock, SmokeGate
│       ├── results_tsv.py
│       ├── mutator.py
│       └── reporter.py
└── tests/unit/scripts/auto_improve/ ← 신규
    ├── test_coordinator.py
    ├── test_guards.py
    ├── test_eval_runner.py
    ├── test_results_tsv.py
    └── test_worktree.py
```

**Test 베이스라인**: 1,628 → 1,628+N (N=신규 테스트). 기존 테스트 회귀 0건 목표.

## 10. Handoff

> **Run `/sc:plan` on this design.** Plan generates TDD task list with file paths and verification commands per `<doc_output_convention>`.

권장: `/sc:plan docs/specs/auto-improve-design-ajitta-2026-04-27.md`
