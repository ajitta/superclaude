# SuperClaude v5.0 Implementation Plan

## Opus 4.5 최적화 구현 마스터 플랜

---

## Executive Summary

### 핵심 목표

| 영역 | Before | After | 개선율 |
|------|--------|-------|--------|
| **정적 로딩** | 20개, ~7,500 토큰 | 3개, <700 토큰 | 90%+ |
| **모드** | 7개 동시 로드 | 1개 조건부 | 85%+ |
| **에이전트** | 21개 | 12개 (통합) | 43% |
| **명령어** | 31개 | 15개 (간소화) | 52% |
| **MD 압축** | 장황한 형식 | 테이블+심볼 | 50%+ |

### Opus 4.5 패러다임 적용 (PRD §2-4 기반)

| 기법 | 적용 방법 | 기대 효과 | PRD 참조 |
|------|----------|----------|----------|
| 명시적 요구사항 | 모든 지시에 구체적 기준 포함 | 정확도 향상 | §2.3 |
| 구조화된 프롬프트 | Minimal XML + MD 테이블 | 파싱 효율 | §2.3 |
| Extended Thinking | 복잡 작업 자동 활성화 | 추론 품질 | §4.2 |
| 퓨샷 예제 | 각 명령어에 3-5개 예제 | 일관성 (30% 향상) | §2.3 |
| 맥락 우선 배치 | Tier 1 → 2 → 3 순서 | 30% 성능 향상 | §2.3 |
| **Chain of Draft** | 5단어 이내 미니멀 추론 | 토큰 90% 절감 | §4.7 |
| **Prefilling** | 응답 시작부 템플릿 (API) | 형식 일관성 | §4.6 |

### 신규 기법 추가 (PRD v1.5)

| 기법 | 핵심 내용 | 상태 |
|------|----------|------|
| Chain of Draft (CoD) | `<draft>` 내 5단어 이내 추론 | 신규 |
| Skeleton-of-Thought | 골격 → 병렬 확장 | 신규 |
| Over-Engineering 방지 | 범위 제한 + 단순성 유지 | 신규 |
| 안전한 프롬프팅 | allowlist/denylist + 확인 요청 | 신규 |
| 언어 정책 | 시스템 프롬프트 영어 우선 | 신규 |

---

## Phase 1: 아키텍처 재설계

### 1.1 새로운 폴더 구조

> 📁 **개발 전략**: 
> - **기존 v4**: `src/superclaude/` (그대로 유지, 변경 없음)
> - **v5 개발**: `src/superclaude-v5/` (새로 생성, 병렬 개발)
> - **배포 경로**: `~/.claude/` (설치 후 사용자 환경)

```
src/superclaude/                          # 기존 v4 (그대로 유지)
├── (기존 구조 그대로)
│

src/superclaude-v5/                       # v5 개발 (새로 생성)
├── CLAUDE.md                             # 진입점 + 로딩 규칙 (~200 토큰)
│
├── core/                                 # Tier 1: 항상 로드 (~500 토큰)
│   ├── RULES_CORE.md                     # 압축된 핵심 규칙
│   └── OPUS_PROFILE.md                   # Opus 4.5 최적화 프로파일
│
├── modes/                                # Tier 2: 조건부 로드 (키워드 트리거)
│   ├── orchestration.md                  # multi-tool, parallel, optimize
│   ├── deep-research.md                  # research, investigate, deep-analysis
│   ├── brainstorming.md                  # brainstorm, explore, ideas, maybe
│   └── business-panel.md                 # business, panel, stakeholder
│
├── mcp/                                  # Tier 2: 조건부 로드 (도구 사용 시)
│   ├── context7.md                       # library, docs, framework
│   ├── magic.md                          # ui, component, design
│   ├── morphllm.md                       # bulk-edit, pattern-edit
│   ├── playwright.md                     # browser, e2e, visual-test
│   ├── sequential.md                     # complex analysis
│   ├── serena.md                         # symbol ops
│   └── tavily.md                         # web search
│
├── agents/                               # Tier 3: 동적 로드 (12개)
│   ├── architecture-expert.md
│   ├── quality-expert.md
│   ├── research-agent.md
│   ├── product-expert.md
│   ├── learning-expert.md
│   ├── frontend-expert.md
│   ├── security-expert.md
│   ├── devops-expert.md
│   ├── python-expert.md
│   ├── refactoring-expert.md
│   ├── technical-writer.md
│   └── self-review.md
│
├── commands/                             # Tier 3: 동적 로드 (15개)
│   ├── sc.md                             # 도움말
│   ├── research.md                       # 심층 리서치
│   ├── analyze.md                        # 분석 (troubleshoot + explain)
│   ├── build.md                          # 구현 (implement + improve)
│   ├── agent.md                          # 에이전트 호출
│   ├── test.md                           # 테스트
│   ├── explore.md                        # 탐색 (brainstorm + design)
│   ├── plan.md                           # 계획 (estimate + spec-panel)
│   ├── save.md                           # 세션 저장
│   ├── load.md                           # 세션 로드
│   ├── git.md                            # Git 작업
│   ├── document.md                       # 문서화
│   ├── pm.md                             # PM 에이전트
│   ├── task.md                           # 태스크 관리
│   └── business-panel.md                 # 비즈니스 패널
│
└── docs/                                 # 참조 문서 (선택적)
    ├── PRD_SuperClaude_v5.md
    └── PLAN_SuperClaude_v5.md

~/.claude/                                # 배포 후 (사용자 환경)
└── (src/superclaude-v5/ 내용 복사됨)
```

### 1.2 새로운 CLAUDE.md

```markdown
# SuperClaude v5.0

<config model="opus-4.5" version="5.0" style="goal-oriented"/>

## Core (Always Loaded)
@core/RULES_CORE.md
@core/OPUS_PROFILE.md

## Loading Rules

### Mode Triggers (한 번에 1개만)
| 키워드 | 로드 파일 |
|--------|----------|
| research, investigate, deep-analysis | @modes/deep-research.md |
| brainstorm, explore, ideas, maybe | @modes/brainstorming.md |
| multi-tool, parallel, optimize | @modes/orchestration.md |
| business, panel, stakeholder | @modes/business-panel.md |

### MCP Triggers
| 키워드 | 로드 파일 |
|--------|----------|
| library, docs, framework | @mcp/context7.md |
| ui, component, design | @mcp/magic.md |
| bulk-edit, pattern-edit | @mcp/morphllm.md |
| browser, e2e, visual-test | @mcp/playwright.md |
| complex, reasoning, sequential | @mcp/sequential.md |
| symbol, navigate, codebase | @mcp/serena.md |
| web, search, current | @mcp/tavily.md |

### Agent/Command
- agents/ → `@agent-[name]` 또는 `/sc:agent [name]`
- commands/ → `/sc:[command]`
```

---

## Phase 2: Core 파일 작성

### 2.1 core/RULES_CORE.md (~250 토큰)

> 📝 **언어 정책**: PRD §8.3에 따라 영어로 작성

```markdown
---
name: rules-core
type: core
priority: critical
---

<document type="core" name="rules-core">

# Core Rules (Opus 4.5)

## 🔴 Critical (Never Compromise)

| Rule | Action | Reason |
|------|--------|--------|
| Git First | `status && branch` before changes | Safe version control |
| Read→Edit | Never edit without reading | Context required |
| Feature Branch | Never work on main/master | Protect production |
| No Skip | Never skip tests/validation | Quality assurance |
| Evidence | All claims verifiable | Prevent hallucination |

## 🟡 Important (Strong Preference)

| Rule | Pattern | Reason |
|------|---------|--------|
| Todo | 3+ steps → TodoWrite | Track complex tasks |
| Complete | Start = Finish, no TODO comments | Completeness |
| Scope | Build asked only | Prevent over-engineering |
| Clean | Remove temp files | Clean workspace |
| Professional | No marketing language | Clear communication |

## 🟢 Recommended (When Practical)

| Rule | Tool | Reason |
|------|------|--------|
| Parallel | Batch independent ops | Efficiency |
| MCP First | MCP > Native > Basic | Optimal tool selection |
| Naming | Follow existing conventions | Consistency |
| Structure | tests/ scripts/ claudedocs/ | Standard structure |

## Quick Decision Flow

```
Task request → Complexity check → 3+ steps? → TodoWrite
File operation → Read first → Understand → Edit
Tool selection → MCP available? → Use MCP → Fallback to Native
```

</document>
```

### 2.2 core/OPUS_PROFILE.md (~300 토큰, 확장됨)

> 📝 **PRD §4.2, §4.7, §4.9 반영**: Native Thinking 역할 분담, CoD, Over-Engineering 방지

```markdown
---
name: opus-profile
type: core
priority: critical
---

<document type="core" name="opus-profile">

# Opus 4.5 Profile

## Model Characteristics

| Trait | Application | Expected Effect |
|-------|-------------|-----------------|
| Autonomous reasoning | What(goal) > How(method) | Flexible implementation |
| Effort calibration | Auto-adjust by complexity | Resource optimization |
| Extended Thinking | Auto-activate for complex tasks | Reasoning quality |
| Trade-off handling | Delegate optimal choice | Practical results |

## Autonomy Scope

<autonomy>
  <allowed>
    Implementation method, Tool selection, Error recovery, Optimization decisions
  </allowed>
  <requires_confirmation>
    File deletion, Production changes, Cost-incurring APIs, Large-scale refactoring
  </requires_confirmation>
</autonomy>

## Prompting Principles

| Principle | Application |
|-----------|-------------|
| Goal > Steps | "Achieve X" vs "1. do... 2. do..." |
| Boundaries > Details | Define what TO DO, not NOT TO DO |
| Output validation > Process monitoring | Specify quality criteria |
| Context+Reason > Command+Emphasis | Explain why needed |

## Native Thinking vs Framework Tags (PRD §4.2)

| Purpose | Recommended Approach | Note |
|---------|---------------------|------|
| Complex logical reasoning | Native Extended Thinking (`budget_tokens`) | Model built-in |
| Task planning | Framework `<planning>` tag | User visibility |
| Output formatting | Framework `<format_prep>` tag | Structure output |
| Minimal reasoning | Chain of Draft (§CoD) | Token efficiency |

## Chain of Draft Pattern (PRD §4.7)

> Each reasoning step ≤5 words. Maintains CoT performance with ~90% token reduction.

```xml
<draft>
step1: auth check → token valid
step2: user perms → admin role
step3: action → approve request
result: grant access
</draft>
<action>[Tool call with minimal context]</action>
```

## Over-Engineering Prevention (PRD §4.9)

<over_engineering_prevention>
Do not over-engineer. Make only changes that are directly requested 
or clearly necessary. Keep solutions simple and focused.

- Do not add unnecessary cleanup to bug fixes.
- Do not add excessive configurability to simple features.
- Do not design for hypothetical future requirements.
- Reuse existing abstractions; follow DRY principle.
</over_engineering_prevention>

## Extended Thinking Triggers

| Condition | Activation |
|-----------|------------|
| Complexity ≥ 7/10 | Auto |
| Multi-step reasoning | Auto |
| `--deep` flag | Manual |
| `/sc:think` (문서 안내용, CLI 별칭 미구현) → `/sc:plan --deep` | Manual |

## Budget Tokens (PRD §4.2)

| Flag | Budget | Use Case |
|------|--------|----------|
| `--think` | 5K | Standard complex tasks |
| `--think-hard` | 10K | Deep analysis |
| `--ultrathink` | 32K | Maximum reasoning |

</document>
```

---

## Phase 3: 모드 재작성

### 3.1 모드 통합/제거 계획

| 현재 모드 | 조치 | 이유 |
|----------|------|------|
| MODE_Orchestration | ✅ 유지 + 확장 | 도구 선택 + 태스크 관리 통합 |
| MODE_DeepResearch | ✅ 유지 | 리서치 워크플로우 핵심 |
| MODE_Brainstorming | ✅ 유지 | 창의적 탐색 |
| MODE_Business_Panel | ✅ 유지 | 특수 기능 |
| MODE_Introspection | ❌ 제거 | Extended Thinking이 대체 |
| MODE_Task_Management | 🔄 통합 | Orchestration에 병합 |
| MODE_Token_Efficiency | ❌ 제거 | 기본 동작으로 내재화 (CoD) |

### 3.2 새로운 모드 형식

#### modes/orchestration.md

```markdown
---
name: orchestration
type: mode
priority: high
triggers: [multi-tool, parallel, optimize, performance, batch]
---

<document type="mode" name="orchestration">

# Orchestration Mode

## Activation Conditions
| Condition | Example |
|-----------|---------|
| 3+ files simultaneous | Multi-file refactoring |
| Multi-tool combination | MCP + Native mix |
| Performance constraints | Token/time limits |
| Batch processing | Bulk file modifications |

## Tool Selection Matrix

| Task | Best Choice | Alternative | Avoid |
|------|-------------|-------------|-------|
| UI components | Magic MCP | Manual coding | - |
| Deep analysis | Sequential MCP | Extended Thinking | Simple reasoning |
| Pattern edits | Morphllm MCP | Regex + sed | Manual repetition |
| Documentation | Context7 MCP | Web search | Guessing |
| Browser test | Playwright MCP | Unit tests | Screenshots |
| Symbol navigation | Serena MCP | grep + find | Full file reads |

## Tool Search Tool (PRD §4.3)

| Step | Action | Expected Effect |
|------|--------|-----------------|
| 1 | Demand-based tool discovery | Avoid unnecessary tool load |
| 2 | Cache tool capability summary | Reduce repeated token cost |
| 3 | Prefer MCP when capability matches | Align with MCP-first policy |

## Resource Management

| Zone | Threshold | Action |
|------|-----------|--------|
| 🟢 Green | 0-75% | Full capabilities, verbose output |
| 🟡 Yellow | 75-85% | Efficiency mode, concise output |
| 🔴 Red | 85%+ | Essential ops only, minimal output |

## Chain of Draft Integration (PRD §4.7)

```xml
<draft>
step1: identify files → 5 targets
step2: select tool → Morphllm MCP
step3: pattern → rename func
result: batch execute
</draft>
<action>[Morphllm MCP call]</action>
```

## Parallel Execution Rules

| Condition | Action |
|-----------|--------|
| 3+ independent files | auto-suggest parallel read |
| Multiple directories | delegation mode |
| Sequential dependency | chain execution |
| MCP + Native mix | prioritize MCP |

## Examples

<example>
  <input>5개 파일에서 함수명 변경</input>
  <output>
    <draft>
    step1: scope → 5 files
    step2: tool → Morphllm MCP
    step3: pattern → funcA→funcB
    result: parallel batch
    </draft>
    <action>
    1. Morphllm MCP로 패턴 매칭 후 일괄 수정
    2. 관련 테스트 병렬 실행
    3. 결과 검증
    </action>
  </output>
</example>

</document>
```

#### modes/deep-research.md

```markdown
---
name: deep-research
type: mode
priority: high
triggers: [research, investigate, deep-analysis, understand]
---

<document type="mode" name="deep-research">

# Deep Research Mode

## Activation Conditions
| Condition | Example |
|-----------|---------|
| Deep analysis needed | Architecture understanding |
| Multi-source research | Library comparison |
| Evidence-based conclusion | Technology selection |
| Codebase exploration | Dependency analysis |

## Research Methodology

```
1. Problem definition → Clear question formulation
2. Information gathering → MCP first, multi-source
3. Analysis → Extended Thinking activation
4. Verification → Cross-validation, confidence scoring
5. Synthesis → Structured conclusion
```

## Tool Priority

| Purpose | Tool | Reason |
|---------|------|--------|
| Document lookup | Context7 MCP | Official docs |
| Web search | Tavily MCP | Current info |
| Code analysis | Serena MCP | Symbol tracking |
| Complex reasoning | Extended Thinking | Multi-step analysis |

## Quality Control (PRD §4.4)

| Item | Criteria |
|------|----------|
| Confidence score | 0-1 scale explicit |
| Uncertainty | "Needs verification", "Estimated" labels |
| Sources | Evidence required for claims |
| Verification | Cross-validation performed |

## Output Format

```markdown
## Research Results

### Key Findings
| Finding | Confidence | Evidence |
|---------|------------|----------|
| ... | 0.9 | [Source] |

### Analysis
[Extended Thinking results]

### Conclusion
[Verified conclusion]

### Further Investigation Needed
[Uncertain areas]
```

</document>
```

---

## Phase 4: 에이전트 통합

### 4.1 통합 계획 (21 → 12)

```
통합:
├── system-architect + backend-architect → architecture-expert.md
├── performance-engineer + quality-engineer → quality-expert.md
├── deep-research + deep-research-agent → research-agent.md
├── requirements-analyst + pm-agent → product-expert.md
├── learning-guide + socratic-mentor → learning-expert.md

유지 (형식 변환):
├── frontend-architect → frontend-expert.md
├── security-engineer → security-expert.md
├── devops-architect → devops-expert.md
├── python-expert.md (유지)
├── refactoring-expert.md (유지)
├── technical-writer.md (유지)
└── self-review.md (유지)

archive로 이동:
├── repo-index.md → 자동 수행으로 대체
├── business-panel-experts.md → modes/business-panel.md에 통합
└── root-cause-analyst.md → quality-expert.md에 통합
```

### 4.2 에이전트 새 형식 (PRD §8 기반)

> 📝 **언어 정책 적용**: Role, Keywords, Capabilities, Boundaries는 영어, Examples의 input은 사용자 언어 가능

#### agents/architecture-expert.md

```markdown
---
name: architecture-expert
type: agent
priority: high
triggers: [architecture, system design, backend, scalability, API, database]
---

<document type="agent" name="architecture-expert">

# Architecture Expert

## Role
System architecture design and backend system building expert.

## Keywords
architecture, system design, backend, API, database, scalability, microservices, 
monolith, distributed, caching, load balancing

## Capabilities

| Capability | Output | Quality Criteria |
|------------|--------|------------------|
| System design | Architecture diagrams | Mermaid/PlantUML |
| API design | REST/GraphQL spec | OpenAPI 3.0 compatible |
| DB architecture | Schema design | Normalization level specified |
| Scalability | Trade-off analysis | Quantitative comparison |

## Methodology

```
1. Requirements analysis → Functional/non-functional separation
2. Constraint identification → Technical/cost/time
3. Architecture options → 3+ alternatives presented
4. Trade-offs → Quantitative comparison
5. Recommendation → Evidence-based selection
```

## Chain of Draft Structure

```xml
<draft>
step1: reqs → DAU 100K, QPS 500
step2: options → mono/micro/modular
step3: trade-off → cost vs scale
result: modular monolith
</draft>
```

## Examples

<example>
  <input>10만 DAU 서비스 아키텍처 설계</input>
  <output>
    ## Requirements Analysis
    - DAU: 100,000
    - Peak QPS: ~500
    
    ## Architecture Options
    | Option | Pros | Cons | Cost |
    |--------|------|------|------|
    | Monolith | Simple | Scale limits | $ |
    | Microservices | Scalability | Complexity | $$$ |
    | Modular Monolith | Balance | Migration cost | $$ |
    
    ## Recommendation
    Modular Monolith (Reason: Fits current traffic, easy future separation)
  </output>
</example>

## Boundaries

| Will | Won't |
|------|-------|
| Architecture design | Detailed UI implementation |
| Tech selection guide | DevOps pipeline details |
| Scalability planning | Business decisions |
| Trade-off analysis | Project management |

</document>
```

---

## Phase 5: 명령어 간소화

### 5.1 핵심 명령어 (15개)

| 우선순위 | 명령어 | 역할 | 통합 대상 |
|---------|--------|------|----------|
| 🔴 핵심 | `/sc` | 도움말 | - |
| 🔴 핵심 | `/sc:research` | 심층 리서치 | - |
| 🔴 핵심 | `/sc:analyze` | 분석 | troubleshoot + explain |
| 🔴 핵심 | `/sc:build` | 구현 | implement + improve |
| 🔴 핵심 | `/sc:agent` | 에이전트 호출 | - |
| 🔴 핵심 | `/sc:test` | 테스트 | - |
| 🟡 중요 | `/sc:explore` | 탐색 | brainstorm + design |
| 🟡 중요 | `/sc:plan` | 계획 | estimate + spec-panel |
| 🟡 중요 | `/sc:save` | 세션 저장 | - |
| 🟡 중요 | `/sc:load` | 세션 로드 | - |
| 🟡 중요 | `/sc:git` | Git 작업 | - |
| 🟡 중요 | `/sc:document` | 문서화 | - |
| 🟢 선택 | `/sc:pm` | PM 에이전트 | - |
| 🟢 선택 | `/sc:task` | 태스크 관리 | - |
| 🟢 선택 | `/sc:business-panel` | 비즈니스 패널 | - |

> `/sc:think`는 **문서 안내용**으로만 유지하며, 실제 CLI 별칭은 구현하지 않습니다.  
> 실제 사용은 `/sc:plan --deep`(또는 `--deep` 플래그)로 통일합니다.

### 5.2 통합/제거 대상

| 현재 명령어 | 조치 | 대체/이유 |
|------------|------|----------|
| brainstorm + design | → /sc:explore | 창의적 탐색 통합 |
| implement + improve | → /sc:build | 구현 작업 통합 |
| troubleshoot + explain | → /sc:analyze | 분석 작업 통합 |
| estimate + spec-panel | → /sc:plan | 계획 작업 통합 |
| cleanup | ❌ 제거 | Orchestration 모드가 자동 감지 |
| recommend | ❌ 제거 | 에이전트가 자동 제안 |
| reflect | ❌ 제거 | Extended Thinking이 대체 |
| select-tool | ❌ 제거 | Orchestration 모드가 자동 선택 |
| spawn | ❌ 제거 | 필요 시 자동 실행 |
| workflow | ❌ 제거 | Orchestration 모드로 통합 |
| index-repo | ❌ 제거 | 자동 수행 |

### 5.3 명령어 새 형식

#### commands/build.md

```markdown
---
name: build
type: command
priority: critical
triggers: [implement, improve, create, develop, code]
---

<document type="command" name="build">

# /sc:build

## Purpose
Code implementation and improvement tasks.

## Syntax
```
/sc:build [target] [options]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--scope` | Task scope (file/module/feature) | feature |
| `--test` | Include tests | true |
| `--doc` | Include documentation | false |
| `--deep` | Activate Extended Thinking | auto |

## Workflow

```
1. Confirm requirements → Define explicit criteria
2. Review design → 3+ steps = TodoWrite
3. Implement → MCP-first tool selection
4. Test → Auto-run tests
5. Validate → Check quality criteria
```

## Chain of Draft Structure

```xml
<draft>
step1: scope → auth feature
step2: plan → model/API/middleware
step3: tool → Magic MCP for UI
result: 4 todos created
</draft>
```

## Examples

<example>
  <input>/sc:build user authentication --scope=feature --test</input>
  <output>
    <draft>
    step1: feature → user auth
    step2: components → 4 items
    step3: approach → TDD
    result: todos + implement
    </draft>
    
    ## Todo
    - [ ] Model definition (User, Session)
    - [ ] API endpoints (login, logout, register)
    - [ ] Middleware (auth check)
    - [ ] Tests (unit + integration)
    
    ## Implementation
    [Code implementation...]
  </output>
</example>

<example>
  <input>/sc:build --improve login-form validation</input>
  <output>
    <draft>
    step1: analyze → current state
    step2: issues → 3 found
    step3: approach → incremental
    result: 3 improvements
    </draft>
    
    ## Current State Analysis
    [Reading existing code...]
    
    ## Improvement Plan
    1. Add client-side validation
    2. Improve error messages
    3. Enhance accessibility
    
    ## Implementation
    [Improved code...]
  </output>
</example>

## Quality Criteria

| Criteria | Required |
|----------|----------|
| Follow existing conventions | ✅ Required |
| Include tests | ✅ Required (unless --test=false) |
| Error handling | ✅ Required |
| Documentation | 🟡 Recommended |
| Type definitions | 🟡 Recommended (TS projects) |

## Over-Engineering Prevention (PRD §4.9)

- Only implement requested changes
- No unnecessary abstractions
- Keep solutions simple and focused

</document>
```

---

## Phase 6: 안전한 프롬프팅 구현 (NEW - PRD §4.10)

### 6.1 경로 제한 설정

```markdown
## Safe Execution Template

<safe_execution>
<!-- Adjust according to project structure -->
<scope type="allowlist">
  <!-- Single repo example -->
  <path>src/</path>
  <path>tests/</path>
  <path>docs/</path>
  
  <!-- Monorepo example -->
  <!-- <path>packages/*/src/</path> -->
  <!-- <path>apps/*/</path> -->
</scope>

<scope type="denylist">
  <path>node_modules/</path>
  <path>.git/</path>
  <path>dist/</path>
  <path>build/</path>
</scope>

Always ask for confirmation before destructive operations.

Task decomposition:
1. Execute first change
2. Review linter and test results
3. Request user confirmation
4. Execute next change
</safe_execution>
```

### 6.2 확인 요청 구현

| 작업 유형 | 확인 필요 | 자동 실행 가능 |
|----------|----------|---------------|
| 파일 삭제 | ✅ 필수 | ❌ |
| 프로덕션 변경 | ✅ 필수 | ❌ |
| 대규모 리팩토링 | ✅ 필수 | ❌ |
| 새 파일 생성 | 🟡 권장 | ✅ |
| 기존 파일 수정 | 🟡 권장 | ✅ |
| 테스트 실행 | ❌ 불필요 | ✅ |

---

## Phase 7: 구현 로드맵

### Week 1: 기반 구축

| Day | 작업 | 산출물 | 토큰 영향 |
|-----|------|--------|----------|
| 1 | `src/superclaude-v5/` 폴더 구조 생성 | core/, modes/, mcp/, agents/, commands/ | - |
| 2 | 기존 v4 구조 확인 (변경 없음) | `src/superclaude/` 유지 확인 | - |
| 3 | RULES_CORE.md 작성 (영어) | `src/superclaude-v5/core/RULES_CORE.md` | -1,000 |
| 4 | OPUS_PROFILE.md 작성 (CoD, Over-Eng 포함) | `src/superclaude-v5/core/OPUS_PROFILE.md` | +300 |
| 5 | 새 CLAUDE.md 작성 | `src/superclaude-v5/CLAUDE.md` (v5) | -7,000 |
| 6-7 | 기본 테스트 | 테스트 결과 | - |

**Week 1 목표**: 정적 로딩 7,500 → 700 토큰, `src/superclaude-v5/` 구조 완성

### Week 2: 모드 최적화

| Day | 작업 | 산출물 |
|-----|------|--------|
| 1-2 | 모드 통합 (7→4) | 4개 모드 파일 |
| 3-4 | 모드 새 형식 변환 (CoD 포함) | modes/ 폴더 |
| 5 | 키워드 트리거 구현 | 조건부 로딩 로직 |
| 6-7 | 조건부 로딩 테스트 | 키워드 매칭 검증 |

**Week 2 목표**: 조건부 로딩 정확도 95%+

### Week 3: 에이전트 통합

| Day | 작업 | 산출물 |
|-----|------|--------|
| 1-2 | 에이전트 통합 (21→12) | 12개 에이전트 |
| 3-4 | 새 형식 변환 + 예제 추가 (영어) | agents/ 업데이트 |
| 5-6 | 동적 로딩 테스트 | 호출 테스트 |
| 7 | 품질 검토 | 에이전트 품질 확인 |

**Week 3 목표**: 에이전트 수 43% 감소, 품질 유지

### Week 4: 명령어 간소화 + 마무리

| Day | 작업 | 산출물 |
|-----|------|--------|
| 1-2 | 명령어 통합 (31→15) | 15개 명령어 |
| 3-4 | 퓨샷 예제 + CoD 구조 추가 | 각 명령어 3-5개 예제 |
| 5 | 하위 호환성 테스트 | 기존 명령어 동작 확인 |
| 6 | v4→v5 마이그레이션 검증 | 체크리스트 완료 |
| 7 | v5.0 릴리스 | 최종 버전 |

**Week 4 목표**: 명령어 수 52% 감소, 하위 호환 100%

---

## Checklist

### Phase 1: 기반 구축
- [ ] `src/superclaude-v5/` 폴더 생성 (기존 `src/superclaude/`는 그대로 유지)
- [ ] `src/superclaude-v5/core/` 폴더 생성
- [ ] `src/superclaude-v5/modes/` 폴더 생성
- [ ] `src/superclaude-v5/mcp/` 폴더 생성
- [ ] `src/superclaude-v5/agents/` 폴더 생성
- [ ] `src/superclaude-v5/commands/` 폴더 생성
- [ ] RULES_CORE.md 작성 (영어, 새 형식)
- [ ] OPUS_PROFILE.md 작성 (CoD, Over-Eng, Thinking 역할 분담 포함)
- [ ] CLAUDE.md v5 작성 (계층적 로딩)
- [ ] 중복 Import 제거 확인
- [ ] 기본 동작 테스트

### Phase 2: 모드 최적화
- [ ] MODE_Introspection → 제거
- [ ] MODE_Token_Efficiency → 제거 (CoD로 내재화)
- [ ] MODE_Task_Management → Orchestration 통합
- [ ] 4개 모드 새 형식으로 변환 (CoD 구조 포함)
- [ ] 키워드 트리거 구현
- [ ] Tool Search Tool 지연 로딩/캐시 구현 (PRD §4.3)
- [ ] 조건부 로딩 테스트

### Phase 3: 에이전트 통합
- [ ] architecture-expert 생성 (system + backend 통합)
- [ ] quality-expert 생성 (performance + quality 통합)
- [ ] research-agent 생성 (deep-research 통합)
- [ ] product-expert 생성 (requirements + pm 통합)
- [ ] learning-expert 생성 (learning + socratic 통합)
- [ ] 기존 에이전트 새 형식 변환 (영어)
- [ ] 퓨샷 예제 추가 (각 3-5개)
- [ ] 동적 로딩 테스트

### Phase 4: 명령어 간소화
- [ ] /sc:explore 생성 (brainstorm + design)
- [ ] /sc:plan 생성 (estimate + spec)
- [ ] /sc:analyze 생성 (troubleshoot + explain)
- [ ] /sc:build 업데이트 (implement + improve)
- [ ] 불필요 명령어 archive로 이동
- [ ] 핵심 명령어 퓨샷 예제 + CoD 구조 추가
- [ ] 하위 호환성 테스트

### Phase 5: 안전한 프롬프팅 (NEW)
- [ ] safe_execution 템플릿 core/에 추가
- [ ] 경로 제한 (allowlist/denylist) 구현
- [ ] 확인 요청 로직 구현
- [ ] 단계적 실행 패턴 테스트

### Phase 6: 마무리
- [ ] 전체 통합 테스트
- [ ] 성능 측정 (토큰 절감 검증)
- [ ] Extended Thinking 활성화 검증
- [ ] CoD 패턴 동작 검증
- [ ] v4→v5 마이그레이션 체크리스트 완료
- [ ] 문서화 업데이트
- [ ] v5.0 태깅

---

## v4 → v5 마이그레이션 체크리스트 (PRD §14)

> 기존 프롬프트를 Opus 4.5로 마이그레이션할 때:

| # | 작업 | 설명 | 예시 | 상태 |
|---|------|------|------|------|
| 1 | 공격적 언어 제거 | "CRITICAL", "MUST" → 자연스러운 표현 | `"반드시 확인"` → `"확인이 필요합니다"` | ⬜ |
| 2 | 구체화 | 모호한 요청 → 명확한 요구사항 + 성공 기준 | `"개선해줘"` → `"O(n)으로 최적화"` | ⬜ |
| 3 | 예제 정렬 | 예제가 원하는 동작을 정확히 반영 | 3-5개 다양한 예제 포함 | ⬜ |
| 4 | 시스템 프롬프트 검토 | 도구 호출 과도/불충분 확인 | `<default_to_action>` 적용 | ⬜ |
| 5 | Thinking 지시어 제거 | Extended Thinking 기본 제공 | `"단계별로 생각해"` 제거 | ⬜ |
| 6 | 아웃풋 형식 명시 | "하지 말 것" → "할 것" 중심 | `"설명 없이"` → `"JSON만 출력"` | ⬜ |
| 7 | Prefilling 검토 | API 사용 시 프리필 활용 | `{"role": "assistant", "content": "{"}` | ⬜ |
| 8 | Over-Engineering 방지 추가 | 범위 제한 명시 | `<over_engineering_prevention>` 적용 | ⬜ |
| 9 | Chain of Draft 적용 | Verbose → 5단어 이내 미니멀 | `<draft>step1: auth → valid</draft>` | ⬜ |

---

## Success Criteria

| 지표 | Before | After | 목표 절감율 | 측정 방법 |
|------|--------|-------|------------|----------|
| 정적 로딩 | ~7,500 토큰 | <700 토큰 | **90%+** | 토큰 카운트 |
| 에이전트 수 | 21개 | 12개 | **43%** | 파일 수 |
| 명령어 수 | 31개 | 15개 | **52%** | 파일 수 |
| 모드 로딩 | 7개 동시 | 1개 조건부 | **85%** | 로딩 로그 |
| 조건부 정확도 | N/A | 95%+ | - | 키워드 테스트 |
| 하위 호환성 | N/A | 100% | - | 회귀 테스트 |
| Extended Thinking 활성화 | N/A | 적합 작업 80%+ | - | 복잡도 테스트 |
| CoD 토큰 절감 | 기존 CoT | ~90% 감소 | **90%** | 추론 토큰 비교 |

---

## Related Documents

- [PRD_SuperClaude_v5.md](./PRD_SuperClaude_v5.md) - 제품 요구사항 (v1.6)
- [Claude Opus 4.5 프롬프트 엔지니어링 최적화 가이드](./Claude%20Opus%204.5%20프롬프트%20엔지니어링%20최적화%20가이드-perplexity.md)
- [Claude Opus 4.5 프롬프트 엔지니어링 최적화 심층 연구 보고서](./Claude%20Opus%204.5%20프롬프트%20엔지니어링%20최적화%20심층%20연구%20보고서.md)
- [Anthropic Claude 4 Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Chain of Draft Paper](https://arxiv.org/abs/2502.18600)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-12-20 | 초안 작성 |
| 2.0 | 2025-12-21 | **PRD v1.5 기반 전면 개정**: Chain of Draft (CoD) 패턴 추가, Native Thinking vs 프레임워크 태그 역할 분담 반영, Over-Engineering 방지 템플릿 추가, 안전한 프롬프팅 Phase 신설, 언어 정책 (영어 우선) 적용, v4→v5 마이그레이션 체크리스트 통합, Skeleton-of-Thought 병렬 처리 참조, 성공 기준에 CoD 토큰 절감 추가 |
| 2.1 | 2025-12-21 | **개발 구조 변경**: 기존 `src/superclaude/`는 그대로 유지하고, `src/superclaude-v5/`에서 병렬 개발하는 방식으로 변경 |
