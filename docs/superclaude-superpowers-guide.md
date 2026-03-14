# SuperClaude + Superpowers 사용법 가이드

> 두 시스템을 함께 사용할 때의 아키텍처, 동작 방식, 워크플로우 가이드

## 1. 아키텍처 — 누가 뭘 담당하는가

```
superpowers (plugin)                    superclaude (package)
────────────────────────               ────────────────────────
12 프로세스 스킬                         4 고유 스킬
  brainstorming                          confidence-check (사전 검증)
  writing-plans                          ship (안전한 git 배포)
  executing-plans                        simplicity-coach (복잡성 방지)
  test-driven-development                using-superclaude (메타스킬)
  systematic-debugging
  verification-before-completion        30 슬래시 커맨드 (/sc:*)
  requesting-code-review                20 전문가 에이전트
  receiving-code-review                  8 행동 모드
  finishing-a-development-branch         9 MCP 서버 가이드
  dispatching-parallel-agents            Core config (FLAGS, RULES, PRINCIPLES)
  using-git-worktrees                    Hooks + Scripts (7개)
  using-superpowers
```

**역할 분담 원칙:**
- **Superpowers** = 프로세스 (HOW) — 어떤 순서로, 어떤 규율로 작업하는가
- **SuperClaude** = 도메인 (WHO + WHAT) — 어떤 전문가가, 어떤 도구로 실행하는가

## 2. 설치 시나리오별 동작

| 시나리오 | Skills 설치 결과 | 비고 |
|---------|-----------------|------|
| superpowers만 | 12 SP process skills | 프로세스 규율만, 도메인 커맨드 없음 |
| superclaude만 | 15 SC skills (12 process + 3 unique) | 프로세스 + 도메인 전체 (독립 사용) |
| **둘 다 (권장)** | 12 SP skills + 4 SC unique skills | 충돌 없음, 최적 조합 |

### 충돌 방지 메커니즘

`superclaude install` 실행 시 superpowers 플러그인 감지:
- **감지됨** → 11개 중복 스킬 스킵, 4개 고유 스킬만 설치
- **감지 안 됨** → 15개 전부 설치 (독립 사용 모드)

```bash
# superpowers 설치 후 superclaude 설치
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
superclaude install --scope user --force    # 자동으로 4개만 설치

# 확인
superclaude install --list-all
# Skills [4/4] ← 충돌 없이 4개만 설치됨
```

## 3. 워크플로우 예시

### 예시: "인증 시스템 구축"

```
사용자: "인증 시스템 만들자"

┌─ Phase 1: 설계 ──────────────────────────────────────┐
│ superpowers:brainstorming 자동 활성화                  │
│ → 요구사항 탐색 (one question at a time)               │
│ → /sc:brainstorm 커맨드로 프로젝트 컨텍스트 탐색        │
│ → requirements-analyst 에이전트 spec 검증 (SC 고유)    │
│ → spec 작성 → 사용자 승인                              │
└──────────────────────────────────────────────────────┘
                        ↓ gate: spec 승인됨
┌─ Phase 2: 계획 ──────────────────────────────────────┐
│ superpowers:writing-plans 자동 활성화                  │
│ → zero-context implementation plan 생성               │
│ → TDD bite-sized tasks + verification commands        │
│ → plan 커밋                                           │
└──────────────────────────────────────────────────────┘
                        ↓ gate: plan 커밋됨
┌─ Phase 3: 실행 ──────────────────────────────────────┐
│ superpowers:executing-plans 활성화                     │
│ → /sc:spawn으로 specialist agents 병렬 위임 (SC 고유)  │
│   ├── backend-architect (API 설계)                    │
│   ├── security-engineer (인증 보안)                    │
│   └── frontend-architect (로그인 UI)                  │
│ → superpowers:test-driven-development (RED-GREEN)     │
│ → uv run pytest 검증                                  │
└──────────────────────────────────────────────────────┘
                        ↓ gate: 모든 task 완료
┌─ Phase 4: 검증 ──────────────────────────────────────┐
│ superpowers:verification-before-completion 활성화      │
│ → 테스트 실행 증거 확인 (output, not claims)           │
│ → confidence-check 스킬 호출 (SC 고유)                │
│   ├── 중복 체크, 아키텍처 적합성, 공식 문서 확인       │
│   └── ≥90%: proceed / <70%: stop                     │
│ → /sc:review + self-review agent (SC 고유)            │
└──────────────────────────────────────────────────────┘
                        ↓ gate: 증거 확인됨
┌─ Phase 5: 마무리 ────────────────────────────────────┐
│ superpowers:finishing-a-development-branch 활성화      │
│ → 4가지 옵션: merge / PR / keep / discard            │
│ → ship 스킬로 안전 배포 (SC 고유)                     │
└──────────────────────────────────────────────────────┘
```

### 예시: "프로덕션 버그 수정"

```
사용자: "로그인이 간헐적으로 실패해"

1. superpowers:systematic-debugging 자동 활성화
   → Phase 1: 에러 메시지 읽기, 재현, 최근 변경 확인
   → /sc:troubleshoot + root-cause-analyst agent (SC 고유)

2. superpowers:test-driven-development
   → 재현하는 실패 테스트 작성 → 최소 코드로 수정

3. superpowers:verification-before-completion
   → 테스트 통과 증거 확인

4. superpowers:finishing-a-development-branch
   → hotfix PR 생성
```

## 4. 빠른 참조 카드

### 프로세스 스킬 (Superpowers 제공)

| 스킬 | 자동 트리거 | 용도 |
|------|-----------|------|
| brainstorming | 기능 생성, 설계 작업 | 설계 승인 없이 코드 작성 금지 |
| writing-plans | spec 승인 후 | zero-context 구현 계획 |
| executing-plans | plan 커밋 후 | subagent 위임 + checkpoint |
| test-driven-development | 코드 작성 시 | RED-GREEN-REFACTOR 강제 |
| systematic-debugging | 버그, 실패 | 4-phase 근본원인 분석 |
| verification-before-completion | 완료 선언 전 | 증거 없이 완료 주장 금지 |
| requesting-code-review | 기능 완료 시 | subagent reviewer 파견 |
| receiving-code-review | 리뷰 피드백 수신 시 | 기술적 엄밀성, 맹목 동의 금지 |
| finishing-a-development-branch | 모든 테스트 통과 후 | merge/PR/keep/discard |
| dispatching-parallel-agents | 2+ 독립 작업 | 병렬 subagent 파견 |
| using-git-worktrees | 격리 작업 필요 시 | 안전한 worktree 설정 |
| using-superpowers | 세션 시작 | 스킬 invocation 규칙 |

### 도메인 커맨드 + 에이전트 (SuperClaude 고유)

| 하고 싶은 일 | 커맨드 | 연결 에이전트 |
|-------------|--------|-------------|
| 코드 품질 분석 | `/sc:analyze` | quality-engineer |
| 아키텍처 설계 | `/sc:design` | system-architect |
| 보안 감사 | `/sc:analyze --focus security` | security-engineer |
| 성능 최적화 | `/sc:analyze --focus perf` | performance-engineer |
| 리팩토링 | `/sc:improve` | refactoring-expert |
| 비즈니스 분석 | `/sc:business-panel` | business-panel-experts |
| 깊은 리서치 | `/sc:research` | deep-research-agent |
| 코드 리뷰 | `/sc:review` | self-review |
| 문서 생성 | `/sc:document` | technical-writer |
| 멘토링 | `/sc:explain` | learning-guide |
| 전문가 위임 | `/sc:spawn` | (auto-select) |
| MCP 도구 선택 | `/sc:select-tool` | — |
| 작업 관리 | `/sc:task` | pm-agent |
| 공수 산정 | `/sc:estimate` | — |

### SuperClaude 고유 스킬 (Superpowers에 없음)

| 스킬 | 용도 | 호출 방식 |
|------|------|----------|
| **confidence-check** | 구현 전 5개 체크 (중복, 아키텍처, 문서, OSS, 근본원인) | 자동 (트리거 감지) |
| **ship** | 안전한 git add → commit → push → PR | 수동 (`/ship`) |
| **simplicity-coach** | OSL 코칭, 복잡성 감사, 의존성 감사 | 자동 |
| **using-superclaude** | 세션 시작 시 SC 스킬 목록 + invocation 규칙 | 자동 |

## 5. MCP 서버 활용 (SuperClaude 가이드)

SuperClaude는 9개 MCP 서버의 사용 가이드를 제공합니다:

| MCP | 플래그 | 용도 | Fallback |
|-----|--------|------|----------|
| Context7 | `--c7` | 공식 라이브러리 문서 | WebFetch |
| Sequential | `--seq` | 복잡한 다단계 추론 | Native reasoning |
| Tavily | `--tavily` | 웹 검색, 리서치 | WebSearch |
| Serena | `--serena` | 시맨틱 코드 이해 | Grep/Glob |
| Playwright | `--play` | 브라우저 E2E 테스트 | DevTools |
| DevTools | `--devtools` | Core Web Vitals 프로파일링 | — |
| Magic | `--magic` | UI 컴포넌트 생성 | Manual coding |
| Morphllm | `--morph` | 대량 패턴 변환 | Individual edits |

`context_loader.py`가 프롬프트 트리거를 감지하여 관련 MCP 가이드를 자동 주입합니다.

## 6. 설치 방법

```bash
# 1. superpowers 플러그인 설치 (Claude Code 내에서)
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# 2. superclaude 패키지 설치
uv tool install --editable /path/to/superclaude

# 3. superclaude 컴포넌트 배포 (superpowers 감지하여 4개 스킬만 설치)
superclaude install --scope user --force

# 4. 확인
superclaude install --list-all
# Commands [30/30], Agents [20/20], Skills [4/4], Modes [8/8], MCP [8/8]

# 5. Claude Code 재시작
```

## 7. FAQ

**Q: superpowers를 나중에 제거하면?**
A: `superclaude install --force`를 다시 실행하면 15개 스킬 전부 설치됩니다 (superpowers 미감지).

**Q: superpowers 스킬을 SC 버전으로 대체하고 싶으면?**
A: `superclaude install --force` 실행 전에 superpowers를 제거하세요 (`/plugin uninstall superpowers`).

**Q: 두 시스템의 스킬이 동시에 뜨면?**
A: 조건부 설치로 중복이 방지됩니다. `superpowers:X`는 플러그인, bare name은 SC — 겹치지 않습니다.

**Q: /sc:* 커맨드는 superpowers 없이도 동작하나요?**
A: 네. 커맨드와 에이전트는 superclaude 독자 기능이며, superpowers와 무관하게 동작합니다.

**Q: 프로세스 스킬의 hard gate를 무시하고 싶으면?**
A: 사용자 지시가 최우선입니다. "TDD 건너뛰고 바로 구현해" 등 명시적 요청 시 스킬이 양보합니다.
