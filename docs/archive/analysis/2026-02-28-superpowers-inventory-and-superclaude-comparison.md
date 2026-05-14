# Superpowers 인벤토리 정리 및 SuperClaude 비교 (Claude 기준)

작성일: 2026-02-28  
범위: `superpowers` vs `superclaude/src/superclaude`  
제외: Codex/OpenCode/Cursor 전용 동작 상세

## 1) 요약

- `superpowers`는 **프로세스 강제형 스킬 체계**가 중심이다.
  - Skills: 14
  - Commands: 3 (모두 스킬 위임 래퍼)
  - Agents: 1
- `superclaude`는 **도메인 기능/오케스트레이션 폭**이 중심이다.
  - Skills: 3
  - Commands: 30
  - Agents: 20
- 결론적으로, `superclaude`는 기능 폭이 넓고 실행 엔진이 강하지만, `superpowers` 수준의 워크플로우 강제성(특히 스킬 우선 규율)과 행동 검증 테스트는 상대적으로 약하다.

## 2) Superpowers 인벤토리

### 2.1 Skills (14)

| Skill | 핵심 목적 |
|---|---|
| `using-superpowers` | 모든 작업 전 스킬 우선 적용 규율 강제 |
| `brainstorming` | 구현 전 요구사항/설계 확정 |
| `writing-plans` | 상세 구현계획 작성 (작은 단계) |
| `executing-plans` | 계획 기반 배치 실행 |
| `subagent-driven-development` | 태스크별 서브에이전트 + 2단계 리뷰 |
| `test-driven-development` | RED-GREEN-REFACTOR 강제 |
| `systematic-debugging` | 원인 분석 우선 디버깅 |
| `verification-before-completion` | 완료 주장 전 검증 강제 |
| `requesting-code-review` | 코드리뷰 요청 표준화 |
| `receiving-code-review` | 리뷰 수용/반박 절차 표준화 |
| `dispatching-parallel-agents` | 독립 작업 병렬 서브에이전트 운영 |
| `using-git-worktrees` | 구현 전 워크트리 격리 |
| `finishing-a-development-branch` | 브랜치 종료/병합 결정 절차 |
| `writing-skills` | 스킬 작성/검증 표준화 |

### 2.2 Commands (3)

| Command | 역할 |
|---|---|
| `brainstorm` | `brainstorming` 스킬 위임 |
| `write-plan` | `writing-plans` 스킬 위임 |
| `execute-plan` | `executing-plans` 스킬 위임 |

특징:
- 3개 커맨드 모두 `disable-model-invocation: true` 기반의 얇은 래퍼 구조.

### 2.3 Agents (1)

| Agent | 역할 |
|---|---|
| `code-reviewer` | 계획 대비 구현 검증 + 품질 리뷰 |

## 3) SuperClaude 대응 자산 (src/superclaude)

### 3.1 Skills (3)

| Skill | 핵심 목적 |
|---|---|
| `confidence-check` | 구현 전 신뢰도 평가 |
| `ship` | add/commit/push/PR 배송 자동화 |
| `simplicity-coach` | OSL 코칭/의존성 감사/단순화 리뷰 |

### 3.2 Commands (30, 주요 분류)

- 기획/분석: `brainstorm`, `design`, `workflow`, `analyze`, `research`
- 구현/실행: `implement`, `task`, `spawn`, `build`, `test`, `troubleshoot`, `improve`
- 오케스트레이션: `pm`, `agent`, `select-tool`, `recommend`, `sc`
- 세션/인덱싱: `index`, `index-repo`, `load`, `save`, `reflect`
- 유틸/기타: `git`, `document`, `estimate`, `explain`, `cleanup`, `help` 등

### 3.3 Agents (20)

대표:
- `requirements-analyst`, `system-architect`, `backend-architect`, `frontend-architect`
- `quality-engineer`, `root-cause-analyst`, `security-engineer`, `self-review`
- `pm-agent`, `repo-index`, `technical-writer`, `simplicity-guide` 등

## 4) Superpowers ↔ SuperClaude 유사 항목 비교

### 4.1 Skill 단위 비교

| Superpowers | SuperClaude 대응 | 유사도 | 코멘트 |
|---|---|---|---|
| `using-superpowers` | 훅(`session_init.py`, `skill_activator.py`, `context_loader.py`) + `/sc:help` | 중간 | 세션 부트스트랩은 있으나 “항상 스킬 우선” 규율은 약함 |
| `brainstorming` | `/sc:brainstorm` + `requirements-analyst` | 높음 | 요구사항 탐색 기능은 강함 |
| `writing-plans` | `/sc:workflow`, `/sc:design` | 중간 | 상세 TDD 태스크 템플릿 강제는 약함 |
| `executing-plans` | `/sc:task`, `/sc:spawn`, `/sc:pm` | 중간 | 계획 실행은 가능하나 고정 절차 강제는 약함 |
| `subagent-driven-development` | `/sc:spawn`, `/sc:pm`, `execution/parallel.py` | 중간 | 병렬/위임 강점은 있으나 “spec→quality 2단계 리뷰 규율”은 약함 |
| `test-driven-development` | `/sc:test`, `quality-engineer` | 낮음~중간 | 테스트 실행은 강하나 test-first 강제는 약함 |
| `systematic-debugging` | `/sc:troubleshoot`, `root-cause-analyst` | 높음 | root cause 지향이 잘 맞음 |
| `verification-before-completion` | `self-review` agent + `SelfCheckProtocol` | 높음 | 근거 기반 검증 철학이 유사 |
| `requesting-code-review` | `quality-engineer`, `spec-panel`, `self-review` | 중간 | 리뷰 자원은 많으나 요청 프로토콜 스킬은 없음 |
| `receiving-code-review` | `/sc:improve`, `refactoring-expert` | 낮음~중간 | “리뷰 수용 절차” 전용 스킬 부재 |
| `dispatching-parallel-agents` | `/sc:spawn`, `/sc:pm`, `execution/parallel.py` | 높음 | 병렬 실행 능력은 충분 |
| `using-git-worktrees` | `/sc:git` | 낮음 | worktree 전용 운영 가이드/강제 부재 |
| `finishing-a-development-branch` | `ship` skill, `/sc:git` | 중간 | 배송 자동화는 있으나 브랜치 종료 결정 절차는 약함 |
| `writing-skills` | 직접 대응 없음 | 낮음 | 스킬 제작 표준화 워크플로우 부재 |

### 4.2 Command 비교

| 항목 | Superpowers | SuperClaude |
|---|---|---|
| 철학 | 명령은 스킬 실행 진입점 (thin wrapper) | 명령 자체가 풍부한 실행 지시문 |
| 개수 | 3 | 30 |
| 장점 | 행동 일관성 높음 | 기능 범위 넓음 |
| 리스크 | 표현력 제한 가능 | 워크플로우 일관성 분산 가능 |

### 4.3 Agent 비교

| 항목 | Superpowers | SuperClaude |
|---|---|---|
| 에이전트 수 | 1 | 20 |
| 성격 | 코드리뷰 특화 단일 에이전트 | 도메인/역할 분화된 다중 에이전트 |
| 장점 | 리뷰 역할 명확 | 복잡 과업에 맞춤 위임 용이 |
| 리스크 | 역할 확장성 낮음 | 운영 규율 없으면 오케스트레이션 편차 발생 |

## 5) 문서화 관점 결론

1. `superpowers`는 “어떻게 일할지”를 강하게 표준화한다.  
2. `superclaude`는 “무엇을 할 수 있는지”를 넓게 제공한다.  
3. `superclaude` 개선 관점에서 참조 가치가 큰 부분은 다음이다.
- 스킬 우선 실행 규율(세션 시작 강제)
- thin-wrapper 명령 구조(핵심 플로우에서만)
- 행동 회귀 테스트(`claude -p` 기반 스킬 호출/순서 검증)
- 구현 단계의 고정 품질 게이트(예: spec 리뷰 후 quality 리뷰)

## 6) 즉시 적용 가능한 비교 기준 (체크리스트)

- [ ] 새 기능 추가 시: `superclaude` 명령으로 둘지, 스킬 중심으로 둘지 먼저 결정
- [ ] 구현형 작업 시: `brainstorm -> plan -> execute -> verify` 표준 흐름 적용 여부 확인
- [ ] 디버깅 시: root cause 조사 단계가 실제로 선행되는지 확인
- [ ] 완료 보고 전: 테스트/근거/검증 로그 확인
- [ ] 서브에이전트 작업 시: 스펙 적합성 리뷰와 코드 품질 리뷰를 분리할지 결정

