---
status: approved-for-plan
revised: 2026-04-27
---

# `/sc:auto-improve` — Karpathy AutoResearch 응용 자율 코드베이스 개선 루프

## 1. Background

Andrej Karpathy의 [AutoResearch](https://github.com/karpathy/autoresearch) (2026-03 공개)는 LLM 에이전트가 코드 수정 → 실험 실행 → 결과 평가 → 다음 변이 결정의 루프를 사람 개입 없이 반복하여 ML 모델의 검증 손실을 자동으로 낮추는 **자율 실험 프레임워크**다. 핵심 통찰은 "효율적으로 평가 가능한 메트릭을 가진 모든 문제는 에이전트 스웜으로 자동 연구화될 수 있다"는 일반 명제이며, 이미 Claude Code skill 자기개선 등 ML 외 도메인으로의 응용이 검증됐다 (Medium/MindStudio 사례, 2026-03~04).

본 spec은 그 패턴을 **SuperClaude에 새 command `/sc:auto-improve`로 통합**하여, 사용자가 임의 코드베이스에 대해 "객관 수치 메트릭 + shell 명령"만 정의하면 백그라운드 오버나이트 자율 개선 루프를 돌릴 수 있게 하는 것을 목표로 한다.

## 2. Goals / Non-Goals

### Goals
- **G1**: 도메인 무관 — 임의 코드베이스 + shell-driven 메트릭이면 동작
- **G2**: 사용자 진입장벽 최소화 — `--eval-cmd` + `--metric` 두 인자로 실행 가능
- **G3**: 무인 오버나이트 안전성 — 4중 가드(시간/plateau/regression/smoke)로 **main repo + 작업 worktree 내** 무손상 보장. **명시적 한계**: eval-cmd가 외부 시스템(DB/API/클라우드/$$$)에 일으키는 부작용은 본 가드 범위 밖 — 사용자가 eval-cmd를 격리하거나 dry-run 모드로 작성할 책임 (§5 R2 참조)
- **G4**: Karpathy 원본 정신 유지 — operational 정의: **단일 git lineage + LLM이 mutation+selection 둘 다 + git/results.tsv가 research memory** (3가지가 모두 충족되어야 G4 만족)
- **G5**: SuperClaude 인프라 재활용 — agent 위임, MCP, 기존 hook 구조

### Non-Goals
- **NG1**: ML 모델 학습 자체에 특화된 기능 (GPU 스케줄링, distributed training 등) — 사용자가 eval-cmd로 캡슐화
- **NG2**: AutoML/NAS 식 구조화 검색 공간 — LLM 자유 mutation이 결정
- **NG3**: Population/tournament 검색 (Round 2에서 단일 lineage로 결정)
- **NG4**: Named mutation operator 카탈로그 (Round 3에서 LLM 자유로 결정)
- **NG5**: Web UI / 대시보드 — `tail -f results.tsv` + `git log`로 충분

## 3. Resolved Decisions

| Q | Decision | Mode | Rationale |
|---|----------|------|-----------|
| Q1.1 도메인 | 범용 코드베이스 메트릭 | confirmed | 도메인 추상화 우선, ML 한정 회피 |
| Q1.2 평가 | 객관 수치 메트릭 | confirmed | 노이즈 최소, isolation 단순 |
| Q1.3 SC 관계 | 새 command로 통합 | confirmed | SC agent/MCP 인프라 재활용 |
| Q1.4 런타임 | 오버나이트 자율 루프 | confirmed | Karpathy 원본 핵심 가치 ("morning에 결과 확인") |
| Q2.1 Mutation scope | git worktree 격리 + 임의 | confirmed | main 안전 + 격리 내 자유 — 최대 자유도 + 격리 보장 |
| Q2.2 Lineage | 단일 (Karpathy 원본) | confirmed | 단순, results.tsv와 1:1, 첫 출시 적합 |
| Q2.3 Eval API | 단일 명령 + JSON 추출 키 | confirmed | `--eval-cmd 'pytest --json' --metric '.passed'` |
| Q2.4 Safety | 시간/plateau/regression/smoke 4중 | confirmed | 무인 실행 필수 가드 모두 채택 |
| Q3.1 Command 이름 | `/sc:auto-improve` | confirmed | 자율(autonomous) 의미 명확, `/sc:improve` 인터랙티브 변형과 명확히 구분 (revised 2026-04-27 — 원안 `/sc:self-improve`에서 변경) |
| Q3.2 State store | results.tsv + git log | confirmed | Karpathy 원본, 최소 의존성, ML 엔지니어 멘탈 친화 |
| Q3.3 Mutation | LLM 자유 mutation | confirmed | Karpathy 원본, 최대 유연 |

> **Decision-mode 요약**: 11/11 confirmed, 0 delegated. Review handoff에 mandatory audit 표현 불필요.

## 4. High-Level Architecture (개요만 — 디테일은 `/sc:design`)

```
┌──────────────────────────────────────────────────────────────────┐
│ /sc:auto-improve <project> --eval-cmd <sh> --metric <jq>         │
│   --budget 8h --scope 'src/**' [--smoke <sh>]                    │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Coordinator (SC cmd) │
                  │  - worktree 생성/정리 │
                  │  - 가드 enforcement   │
                  │  - 사이클 루프 제어   │
                  └─────────┬────────────┘
                            │ spawns isolated worktree
                            ▼
        ┌──────────────────────────────────────┐
        │ Mutator Agent (격리 worktree에서 작업) │
        │  1. read git log + results.tsv        │
        │  2. propose mutation (free-form)      │
        │  3. apply changes                     │
        │  4. run --eval-cmd → extract metric   │
        │  5. commit (성공 시) or rollback     │
        └──────────────┬───────────────────────┘
                       │ writes
                       ▼
              ┌────────────────────┐
              │ results.tsv + .git │ (lineage = single branch)
              └────────────────────┘
```

### 사이클 의사코드
```python
# Phase 0: 사전 게이트
user_confirm_eval_cmd_responsibility()     # R2 (1회)
baseline = run_dry_run_baseline()          # OQ7 resolved
if baseline.failed:
    stderr("dry-run failed: " + baseline.error); exit(1)  # I4

# Phase 1: 메인 루프
while not budget_exceeded() and not plateau_5_stale():
    if not smoke_gate():                   # G3-d (smoke 미지정 시 eval-cmd timeout 30s)
        skip_cycle(); continue
    mutator_agent.propose_and_apply()      # G4 (LLM 자유)
    score = run_eval_cmd_and_extract()
    log_to_results_tsv(desc=mutator.rationale, tokens=mutator.tokens)  # R3 + R6
    if score < baseline.best_score:        # G3-c
        rollback()
    else:
        commit_to_lineage()                # G4 (단일 lineage)
        update_baseline_if_improved()
report_morning_summary()                   # G1 핵심 가치
```

## 5. Risks (현 시점 식별 — `/sc:design`에서 확장)

| ID | Risk | 완화 방향 |
|----|------|-----------|
| R1 | `/sc:improve`와 명령 이름 혼동 가능성 (잔여) | `auto-` 접두사로 자율성 시그널은 명확하나, 탭 자동완성 시 동시 노출됨. `/sc:design`에서 다음 3옵션 중 택1 필요: **(a)** 도움말 텍스트만 차별화 (현 가정), **(b)** `/sc:improve`에 alias로 묶기, **(c)** `/sc:improve --auto` 플래그로 흡수 (별도 command 없앰) |
| R2 | Worktree 격리에도 eval-cmd 외부 작용 (네트워크/DB/$$$/클라우드) | **v0.1 강제 가드**: (1) 첫 실행 시 dry-run 1회 강제 — 사용자 명시적 confirm 후 루프 진입; (2) `/sc:auto-improve` 시작 메시지에 "eval-cmd is YOUR responsibility to sandbox" 경고 노출; (3) §2 G3에 한계 명시. 본격 sandbox는 v0.2+ |
| R3 | LLM 자유 mutation의 trace 어려움 | **단일 source of truth**: results.tsv `desc` 컬럼이 normative — mutation 시도 1건당 1행 강제. 커밋 메시지는 부수적 (검증 안 함). 검증 메커니즘: 사이클 종료 시 desc가 비어 있으면 사이클 실패 처리 |
| R4 | 메트릭 hacking (LLM이 eval을 직접 수정) | `--eval-cmd` 외부 정의 + scope에서 eval 파일 제외 권장 (그러나 강제 X — 사용자 책임) |
| R5 | 단일 lineage의 plateau 회복 한계 | plateau detector → 5회 stale 시 강제 종료 (현 결정). 향후 population/tournament는 v2에서 검토 |
| R6 | 오버나이트 cost (LLM API 호출) | **v0.1**: 시간 budget 하드캡 + 사이클당 token usage 로깅 (results.tsv 신규 컬럼); **v0.2**: 환경변수 기반 일일 cost 한도 + 통화 환산 |
| R7 | results.tsv 동시쓰기 충돌 | 단일 lineage라 단일 writer — 현 설계로 회피. population 도입 시 재검토 |

## 6. MVP Scope (v0.1 — `/sc:plan`에서 확정)

### Must-have (v0.1)
- `/sc:auto-improve` command 등록 (entry point)
- worktree 생성/정리
- `--eval-cmd` 실행 + JSON 메트릭 추출 (`jq`-style)
- 단일 lineage commit
- results.tsv 기록 (필수 컬럼: `cycle_id, commit_hash, metric_value, status, desc, tokens_used, wall_seconds`)
- 4중 안전 가드:
  - **시간**: `--budget` 하드캡 (디폴트 8h)
  - **plateau**: 5회 연속 비개선 → 강제 종료
  - **regression block**: 신 metric < 현 best → 자동 rollback (커밋 안 함)
  - **smoke**: 사이클 시작 전 `--smoke-cmd` 실행 (미지정 시 `--eval-cmd`를 timeout 30s로 짧게 재실행 — fallback 명시)
- **첫 사이클 baseline 측정**: mutation 0회 dry-run을 강제로 1회 실행하여 baseline 확보 (regression block의 reference point). **dry-run 실패 시**: 즉시 루프 거부 + 사용자에게 stderr 출력 노출 + exit code ≠ 0
- **첫 실행 dry-run 게이트** (R2 완화): 사용자 명시적 confirm 후 루프 시작
- token usage 로깅 (results.tsv에 컬럼)
- 사이클당 morning summary 리포트

### Defer to v0.2+
- claude-mem 연동 (현재 results.tsv로 충분)
- Population/tournament 모드
- Named mutation operator 카탈로그
- Web 대시보드
- Eval-cmd sandbox 격리 (네트워크 차단 등 — 현재 사용자 책임)
- 환경변수 기반 일일 cost 한도 + 통화 환산
- Smoke gate 사용자 정의 DSL (현재 shell 명령으로 충분)

<!-- Defer 섹션은 위로 통합됨 (중복 제거) -->

## 7. Open Questions → `/sc:design`

- **OQ1**: Coordinator 구현체 = 신규 Python module vs 기존 SC agent (sc:agent + 새 sub-skill) — 디자인 결정
- **OQ2**: Mutator agent의 model 선택 정책 (Opus 4.7 / Sonnet 4.6 / Haiku 4.5 비용·품질 trade-off)
- **OQ3**: results.tsv 정확한 스키마 (Karpathy 원본 컬럼 + 확장 컬럼?)
- **OQ4**: `--eval-cmd` 타임아웃 정책 (사이클당 hard timeout 필요 여부)
- **OQ5**: 진척률 외부 노출 — `tail -f`외에 SC `/sc:status`-style 조회 명령 필요한가?
- ~~OQ6~~: **resolved (review v1.2)** — smoke 미지정 시 `--eval-cmd` timeout 30s로 fallback. §6 참조.
- ~~OQ7~~: **resolved (review v1.2)** — mutation 0회 dry-run을 첫 사이클로 강제. §6 참조.

## 8. Validation Criteria (수락 기준 — `/sc:plan` Phase 0)

본 spec이 `/sc:design` → `/sc:plan` 단계로 진행 가능하려면 다음을 만족해야 한다:

- [x] Goals/Non-Goals 명시 (§2)
- [x] 모든 Resolved Decisions가 confirmed 또는 명시적 delegated 태깅 (§3)
- [x] High-level architecture sketch (§4)
- [x] 식별된 Risks (§5)
- [x] MVP scope 분리 (§6)
- [x] Open Questions를 design 단계로 위임 (§7)
- [ ] **`/sc:review` 1회 이상 통과** (status: draft → approved-for-plan)

## 9. Self-Review Iteration Log

| Version | Date | Reviewer | Outcome | Notes |
|---------|------|----------|---------|-------|
| v1 | 2026-04-27 | (pending) | (awaiting `/sc:review`) | 초안 — 3-round Socratic으로 11개 결정 모두 confirmed |
| v1.1 | 2026-04-27 | author (rename) | command rename | `/sc:self-improve` → `/sc:auto-improve` (사용자 요청). R1 risk 문구 갱신, 의미 변동 없음 |
| v1.2 | 2026-04-27 | self-review (`/sc:review --loop --validate`) iteration 1 | critical+important 수정 적용 | **C1 해결** (OQ6/OQ7을 §6 MVP로 끌어올려 fallback 정의 명시); **C2 해결** (G3에 한계 명시 + R2 v0.1 강제 가드 3개 추가); **I1 해결** (R6 v0.1/v0.2 분리); **I2 해결** (R3 results.tsv `desc` 단일화); **I3 해결** (R1 3-옵션 명시) |
| v1.3 | 2026-04-27 | self-review iteration 2 | iteration 2 신규 갭 + suggestion 일부 적용 | **I4 해결** (dry-run 실패 처리 — 즉시 루프 거부 + stderr + exit≠0); **S1 해결** (G4 operational 정의 추가). S2 (G2 측정 기준)는 `/sc:plan` 수락 기준에서 자연스럽게 처리될 것으로 deferred |
| v1.4 | 2026-04-27 | self-review iteration 3 | 의사코드 일관성 수정 | **I5 해결** (§4 사이클 의사코드를 v0.1 MVP 변경에 정렬: Phase 0 게이트 추가, smoke fallback, results.tsv 컬럼 — `desc`/`tokens` — 명시적 로깅) |

---

## Handoff

> **Run `/sc:review` on this spec before `/sc:plan`. Plan handoff is gated on review.**

(All 11 decisions are `confirmed` — no delegated audit phrase needed.)

After review approves: `/sc:design` (architecture detailed) → `/sc:plan` (TDD tasks).
