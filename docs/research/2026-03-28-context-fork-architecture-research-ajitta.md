# context: fork Architecture Analysis — Socratic Discovery

**Date:** 2026-03-28
**Author:** ajitta
**Method:** Socratic exploration (guided discovery with sequential reasoning)
**Scope:** SuperClaude skill/agent isolation mechanisms

---

## 1. Core Discovery: Agent vs Skill Isolation

### Agent (`src/superclaude/agents/`)
- **격리 방식:** Agent tool을 통해 **항상** subprocess로 실행 — 격리가 내장됨
- **`context: fork`는 agent frontmatter 필드가 아님** — 사용 불가, 필요 없음
- Agent frontmatter: `name`, `description`, `permissionMode`, `memory`, `color`, `disallowedTools`, `model`, `mcpServers`

### Skill (`src/superclaude/skills/`)
- **격리 방식:** 기본적으로 **inline** (부모 context 안에서 실행)
- `context: fork` 선언 시 별도 subprocess에서 실행
- Skill frontmatter: `name`, `description`, `context`, `agent`, `hooks`, `disable-model-invocation`, `allowed-tools`

### 두 메커니즘의 비교

| 특성 | Agent tool | context: fork (Skill) |
|------|-----------|----------------------|
| **역할** | WHO (누가 하느냐) | HOW (어떻게 실행하느냐) |
| **트리거** | Claude 런타임 판단 (conditional) | 선언적 — 항상 fork (declarative) |
| **prompt** | Claude가 자유롭게 작성 | SKILL.md 본문 전체 자동 주입 |
| **유연성** | 높음 — 상황별 다른 지시 | 낮음 — 매번 동일 실행 |
| **예측 가능성** | 낮음 | 높음 |
| **조합** | `context: fork` + `agent: backend-architect` 가능 | — |

**조합 의미:** "이 skill을 항상 backend-architect agent로 격리 실행하라"

---

## 2. Hook과 Fork: 직교적 메커니즘

```
Claude Code 런타임
├── Tool call 발생 → Hook이 가로챔 (PreToolUse)  ← 런타임 인프라 층위
│
└── Skill 호출 → context: fork → subprocess 생성   ← 실행 격리 층위
```

- **Hook** (`PreToolUse`, `Stop`): CC 런타임이 tool call을 **intercept** — 부모 프로세스에서 동작
- **Fork** (`context: fork`): skill 실행을 subprocess로 **격리** — 별도 프로세스 생성
- 이 둘은 **직교적(orthogonal)** — 서로 독립적으로 동작
- Hook-based skill에 fork를 추가해도 hook은 여전히 부모에서 동작 → 의미 없거나 혼란 야기

---

## 3. 현재 5개 Skill 평가

### Fork 판단 기준 (Tension)

| fork하면 **얻는 것** | fork하면 **잃는 것** |
|---|---|
| 부모 context window 보존 | 부모 대화의 맥락 (왜 이 작업을 하는지) |
| 예측 가능한 격리 | 유연성 (때에 따라 inline이 나을 수도) |

### 개별 평가

| Skill | Fork 판단 | 이유 |
|-------|----------|------|
| `ship` | 🔴 Net negative | commit message를 위해 "왜 변경했는지" 대화 맥락 필요 |
| `finishing-a-development-branch` | 🔴 Net negative | 옵션 추천을 위해 브랜치 작업 맥락 필요 |
| `confidence-check` | 🔴 부적합 | Hook 기반 — fork와 직교적, 대화 중 판단 필요 |
| `simplicity-coach` | 🔴 부적합 | Hook 기반 + interactive coaching, 대화 맥락 필수 |
| `verbalized-sampling` | 🔴 부적합 | Reference skill — "무엇에 대해" 다양한 관점을 낼지 대화 맥락 필수 |

**결론:** 0/5 skill이 fork 후보. 이것은 설계 결함이 아니라 **올바른 설계**.

---

## 4. Fork의 Sweet Spot: "Scan → Summarize" 패턴

### 이상적 후보 특성

| 특성 | 설명 |
|------|------|
| **입력** | filesystem / 코드 / git diff (대화가 아님) |
| **처리** | 대량 읽기 + 분석 (context 소비가 큼) |
| **출력** | 요약 / 보고서 (결과만 부모에게 전달) |
| **대화 맥락** | 불필요하거나 최소한 |

### SuperClaude에서의 후보 Commands

| Command | 패턴 적합성 | 입력 | 이유 |
|---------|-----------|------|------|
| `/sc:analyze` | ✅ 높음 | 코드 전체 | 대량 분석 → 보고서 반환 |
| `/sc:index-repo` | ✅ 높음 | repo 구조 | 전체 탐색 → 요약 인덱스 반환 |
| `/sc:review --scope branch` | ✅ 높음 | git diff | 변경사항 분석 → 리뷰 결과 |

### 부적합 Commands

| Command | 이유 |
|---------|------|
| `/sc:pm` | Orchestration — "무엇을 만드는지" 대화 맥락 필요 |
| `/sc:reflect` | "방금 한 작업" 되돌아보기 — 대화 맥락 필요 |
| `/sc:build` | RTK로 output 이미 압축됨, fork 이점 미미 |

---

## 5. 결론: "측정 먼저, Fork 나중"

1. **현재 상태는 올바르다** — 5개 skill 모두 inline이 정답
2. **미래 후보는 식별됨** — analyze, index-repo, review (command → skill 전환 시)
3. **전환 조건** — 해당 commands가 context pressure를 측정 가능하게 일으킬 때
4. **패턴 이해가 가치** — 미래 설계 판단의 기반

### Verified Behavior (from CDA research)

**`context: fork` reloads:**
- CLAUDE.md + @imports (core/FLAGS, PRINCIPLES, RULES)
- Global .claude/rules/
- MCP tools (inherited)
- Filesystem access

**`context: fork` isolates:**
- Parent conversation history
- Parent tool call results
- Path-scoped .claude/rules/
- Parent's in-progress reasoning

---

## 6. CDA 역할의 Skill 전환 분석 (2026-03-29 추가)

### 질문: Planner, Generator, Evaluator를 skill로 만들면?

CDA spec의 세 역할을 content type에 매핑:

| CDA 역할 | WHO (Agent) | WHAT (Command) | 이미 존재? |
|----------|-------------|----------------|-----------|
| **Planner** | system-architect | `/sc:plan` (personas: arch\|anal) | ✅ 존재 |
| **Generator** | backend/frontend-architect | `/sc:implement` (personas 있음) | ✅ 존재 |
| **Evaluator** | self-review, quality-engineer | `/sc:review` | ⚠️ 부분적 — 아래 참고 |

**결론: 3개 skill이 아니라 1개 (evaluator만).**

### self-review ≠ CDA evaluator

| 특성 | 현재 self-review | CDA evaluator |
|------|-----------------|---------------|
| **context** | generator와 같은 대화 안에서 동작 | `context: fork`로 격리 |
| **정보** | generator의 reasoning 포함 열람 가능 | artifacts만 수신 (code diff + criteria) |
| **도구** | generator와 동일한 MCP tools | 다른 MCP tools (Playwright, Tavily) |
| **위험** | anchoring bias → 동조 → rubber stamp | 독립적 판단 보장 |

self-review는 "같은 맥락에서 확인"하지만, CDA evaluator는 "격리된 상태에서 독립 판단"한다. **generator의 anti로 존재하지 않는 것**이 핵심 차이.

### Fork의 이중 목적 — 핵심 발견

| 목적 | fork가 하는 일 | 예시 |
|------|--------------|------|
| **효율 (Efficiency)** | 중간 결과가 부모 context 오염 방지 | Scan → Summarize (index-repo) |
| **품질 (Quality)** | generator reasoning을 의도적으로 차단 | evaluator의 독립적 판단 보장 |

- Session 1 (3/28): fork = context window 절약 (성능 도구)
- Session 2 (3/29): fork = **의도적 정보 비대칭** (설계 도구)
- 같은 `context: fork` 메커니즘이 완전히 다른 두 목적으로 사용 가능

**Anchoring bias 메커니즘:** Generator의 reasoning이 합리적으로 들리면 evaluator가 동조 → 동조가 반복되면 evaluator는 rubber stamp가 됨 → fork로 reasoning을 차단하면 독립적 판단 가능

### 파일 기반 Handoff 설계

"결과는 전달하되 context는 뒤섞이면 안 된다"

```
                    ┌─────────────────┐
                    │   /sc:plan      │
                    │   (planner)     │
                    └────────┬────────┘
                             │ plan document (file)
                             ▼
                    ┌─────────────────┐
                    │  /sc:implement  │
                    │  (generator)    │
                    └────────┬────────┘
                             │ code + git commit (artifact)
                             ▼
               ┌──────────────────────────┐
               │  evaluator skill         │
               │  context: fork           │
               │  agent: quality-engineer │
               │                          │
               │  입력: code diff +       │
               │        acceptance criteria│
               │  출력: 평가 보고서        │
               │  (NO generator reasoning)│
               └──────────┬───────────────┘
                          │ evaluation report (file)
                          ▼
                 ┌─────────────────┐
                 │  generator에게   │
                 │  피드백 전달     │
                 └─────────────────┘
```

- `context: fork` = 대화 context 격리, **파일시스템은 공유**
- Git commit을 checkpoint로 사용 → 각 단계의 결과가 버전 관리됨
- Fork된 subprocess끼리 파일로 소통 가능 — context 격리 + artifact 공유

### 측정 먼저 원칙

CDA spec이 Research Archive가 된 이유: **문제가 이론적이었음**. 세 agent가 "8개 컴포넌트 중 지금 필요한 것은 0개"라고 결론.

**Evaluator skill 구현 전 확인 사항:**
1. 현재 self-review + skeptical mindset이 실제로 rubber-stamping하고 있는가?
2. self-review가 "문제 없음"으로 넘긴 코드에서 나중에 발견된 결함이 있는가?
3. 증거 없으면 → "존재하지 않는 문제를 해결하는 아키텍처" (CDA spec과 같은 실수)
4. 증거 있으면 → evaluator skill + `context: fork` + `agent: quality-engineer` 구현

---

## 7. 학습 요약 (10 Insights, 2 Sessions)

### Session 1 (2026-03-28): 기초
1. **Agent = 격리 내장** / Skill = 기본 inline → `context: fork`는 skill 전용
2. **Agent tool = WHO + conditional** / context: fork = HOW + declarative
3. **Hook과 fork는 직교적** — 서로 다른 계층에서 독립 동작
4. **Fork의 sweet spot = "Scan → Summarize"** 패턴
5. **현재 올바른 설계** — 변경은 측정된 필요에 의해서만

### Session 2 (2026-03-29): 심화
6. **CDA 3역할 → skill 1개만 필요** — Planner/Generator는 이미 command+agent로 존재
7. **Fork의 이중 목적** — 효율(context 절약) + 품질(의도적 정보 비대칭)
8. **self-review ≠ CDA evaluator** — 같은 context 동조 vs 격리 독립 판단
9. **파일 기반 handoff** — context 격리 + artifact 공유 (git checkpoint)
10. **측정 먼저** — rubber-stamping 증거 수집 → 증거 있으면 evaluator skill 구현
