# superclaude 컨텍스트 엔지니어링 가이드

> v3.2 — 3-Tier Context Disclosure System
> 대상: superclaude 사용자 (Opus 4.6 + Claude Code)

---

## 개요

superclaude v3.2는 Anthropic의 컨텍스트 엔지니어링 원칙을 기반으로 **3단계 컨텍스트 주입 시스템**을 도입했습니다. 핵심 원리는 단순합니다:

> **원하는 결과의 가능성을 최대화하는 가장 작은 고신호 토큰 세트를 찾아라.**

이 시스템은 MCP 플래그 사용 시 토큰 소비를 **58~93%** 줄이면서, 필요할 때 전체 컨텍스트에 접근하는 경로를 유지합니다.

---

## 1. 3-Tier 주입 시스템

### 작동 방식

플래그를 사용하면 `context_loader.py`가 컨텍스트 파일의 종류에 따라 자동으로 주입 수준을 결정합니다:

| Tier | 콘텐츠 수준 | 대상 | 토큰 비용 | XML 태그 |
|------|-----------|------|----------|---------|
| **Tier 0** | 1줄 요약 | Tool MCP (Context7, Playwright 등) | ~15 토큰 | `<sc-context-hint>` |
| **Tier 1** | 핵심 운용 지침 | Behavioral MCP (Serena, Tavily) | ~100 토큰 | `<sc-context>` |
| **Tier 2** | 전체 .md 파일 | 모드 (brainstorm, research 등) | ~400-800 토큰 | `<context-inject>` |

### 왜 이렇게 나누는가?

- **Tool MCP** (Context7, Sequential, Playwright, DevTools, Magic, Morphllm): Claude는 이미 MCP 서버로부터 도구 설명(tool descriptions)을 받습니다. 1줄 힌트만 추가하면 충분합니다.
- **Behavioral MCP** (Serena, Tavily): 도구를 넘어서 워크플로우, 의사결정 규칙, 초기화 절차가 필요합니다. 압축된 운용 지침을 주입합니다.
- **모드** (Brainstorming, Research, Token Efficiency 등): 인지 오버레이(cognitive overlay)로서 사고방식, 커뮤니케이션 스타일, 우선순위를 재정의합니다. 전체 콘텐츠가 필요합니다.

### 측정된 토큰 절감

| 시나리오 | 이전 | 이후 | 절감율 |
|---------|------|------|-------|
| `--brainstorm --serena --tavily` | ~2,998 토큰 | ~926 토큰 | **-69%** |
| `--all-mcp` (8개 MCP 전부) | ~7,365 토큰 | ~513 토큰 | **-93%** |
| `--research --seq` | ~1,455 토큰 | ~612 토큰 | **-58%** |

---

## 2. 플래그 사용법

### MCP 플래그 (Tier 0/1 자동 적용)

```bash
# Tool MCP → Tier 0 (1줄 힌트만 주입)
/sc:implement auth API --c7        # Context7 라이브러리 문서 참조
/sc:analyze --seq                  # Sequential 멀티스텝 추론
/sc:test --play                    # Playwright 브라우저 테스트
/sc:analyze --perf                 # Chrome DevTools 성능 프로파일링

# Behavioral MCP → Tier 1 (운용 지침 주입)
/sc:implement --serena             # Serena 심볼 기반 코드 탐색
/sc:research --tavily              # Tavily 웹 검색
```

### 모드 플래그 (Tier 2 — 항상 전체 .md 주입)

```bash
/sc:brainstorm "아이디어" --brainstorm    # 소크라틱 탐색 모드
/sc:research "주제" --research            # 체계적 조사 모드
/sc:implement --uc                        # 토큰 효율 모드 (30-50% 압축)
```

### 복합 플래그

```bash
--frontend-verify    # Playwright + DevTools + Serena (3개 MCP)
--all-mcp            # 8개 MCP 전부 (주의: 토큰 예산 초과 가능)
```

### 새 플래그: --verbose-context

Tier 0/1 지침이 너무 간결해서 Claude가 MCP를 잘못 사용하는 경우, 전체 .md 주입을 강제합니다:

```bash
# 평소 (Tier 0 — 17 토큰):
/sc:implement --c7
# → <sc-context-hint>Context7: resolve-library-id first...</sc-context-hint>

# 전체 주입 강제 (Tier 2 — 751 토큰):
/sc:implement --verbose-context --c7
# → <context-inject file="mcp/MCP_Context7.md" tokens="~751">전체 내용</context-inject>
```

**사용 시점:** 짧은 지침으로 Claude가 Context7의 2단계 워크플로우를 건너뛰거나, Serena 초기화를 빠뜨리는 경우.

---

## 3. 토큰 예산 이해

### 항상 로드되는 기본 콘텐츠

`CLAUDE_SC.md` @import 체인을 통해 매 세션 시작 시 자동 로드:

| 파일 | 토큰 | 예산 비율 |
|------|------|----------|
| FLAGS.md | ~1,433 | 18% |
| RULES.md | ~2,005 | 25% |
| PRINCIPLES.md | ~564 | 7% |
| **합계** | **~4,002** | **50%** |

**나머지 ~4,000 토큰**이 on-demand 컨텍스트(모드, MCP, 실행 디렉티브)에 사용됩니다.

### 예산 초과 시

토큰 예산(8K)을 초과하면 우선순위가 낮은 컨텍스트가 자동으로 스킵되고 경고가 표시됩니다:

```
<!-- ⚠️ Budget exceeded: skipped mcp/MCP_Magic.md, mcp/MCP_Morphllm.md -->
```

이 경고가 보이면:
1. 불필요한 플래그를 줄이거나
2. `--no-mcp`로 MCP 컨텍스트를 모두 비활성화하거나
3. 모드와 MCP를 분리된 세션에서 사용하세요

---

## 4. 예시 기반 규칙 시스템

### 배경

Anthropic의 가이드에 따르면: "다양하고 대표적인 소수의 예시가 장황한 규칙 목록보다 효과적이다."

이전 RULES.md는 106줄의 규칙에 예시가 거의 없었습니다 (13:1 비율). 이제 핵심 규칙마다 구체적인 시나리오 예시가 포함됩니다.

### core_rules 예시 (8개 시나리오)

| 시나리오 | 잘못된 대응 | 올바른 대응 | 규칙 |
|---------|-----------|-----------|------|
| 유저: "로그인 버그 수정해" | 인증 리팩토링 + 테스트 추가 + 문서 갱신 | 해당 버그만 수정 | [R06] Scope 🟡 |
| 기능 구현 시작 전 | 바로 코딩 시작 | `git log` + `grep`으로 이미 완료됐는지 확인 | [R02] Status Check 🔴 |
| API 500 에러 | 코드 버그라고 가정 | 포트 점유? DB 실행 중? 환경변수 설정? 먼저 확인 | [R03] Diagnosis 🔴 |
| 유저: "대시보드 개선해" | "차트 추가"로 추측 | "성능, UX, 데이터 정확도 중 어느 쪽?" 질문 | [R12] Clarification 🟡 |
| 유저: "auth 모듈 구조 변경" | 파일 이동 시작 | "확인: src/auth/ 파일 구조 재편, 로직 재작성 아님. 맞나요?" | [R13] Intent Verification 🔴 |
| 유저가 정정: "아니, API 라우트" | 조용히 파일 변경 | 피드백 메모리 저장: {trigger, misread, actual, prevention} | [R14] Correction Capture 🟡 |

### anti_over_engineering 예시 (3개 시나리오)

| 요청 | 과잉 엔지니어링 | 적정 규모 |
|------|--------------|---------|
| "API에 재시도 추가" | RetryStrategy 클래스 + 백오프 + 지터 + 서킷 브레이커 | 3줄 재시도 루프 + 지수 백오프 |
| "에러 메시지 오타 수정" | 에러 핸들링 모듈 전체 리팩토링 | 해당 문자열 1개 변경 |
| "로그인 시 유저 ID 로깅" | 구조화 로깅 프레임워크 + 로테이션 | `logger.info(f"Login: {user_id}")` |

---

## 5. 서브에이전트 의사결정 가이드

### 직접 작업 vs 서브에이전트

| 기준 | 직접 작업 | 서브에이전트 |
|------|---------|-----------|
| 파일 수 | 단일 파일, <3 단계 | 3+ 독립 작업 스트림 |
| 의존성 | 순차 의존 관계 | 병렬 가능, 격리 가능 |
| 컨텍스트 | 이미 로드됨 | >20K 토큰 탐색 예상 |
| 시간 | <30초 직접 완료 | 전문 도메인 필요 |

### 구체적 판단 예시

| 작업 | 판단 | 이유 |
|------|------|------|
| "UserAuth 정의 위치 찾기" | 직접 grep | 단일 검색, 즉시 완료 |
| "보안 + 성능 + 접근성 감사" | 3개 서브에이전트 | 독립 도메인, 병렬 가능 |
| "이 파일 읽고 42번째 줄 수정" | 직접 | 순차 의존 관계 |
| "React 19 + Vue 4 + Svelte 5 조사" | 3개 서브에이전트 | 독립 연구, 컨텍스트 격리 |
| "한 파일의 함수 2개 리팩토링" | 직접 | 작은 범위, 병렬 가능해도 직접이 효율적 |

---

## 6. 명령어 범위 구분

유사한 명령어 간 혼동 방지를 위한 가이드:

### 분석 계열
- **analyze**: 정적 코드 품질 측정 (메트릭, 패턴, 스멜)
- **review**: 변경 단위 리뷰 (PR, diff, 특정 커밋)
- **reflect**: 구현 후 자기 검증 ("내가 이걸 맞게 했나?")

### 프로젝트 관리 계열
- **task**: 단일 세션 작업 분해 + 진행 추적
- **pm**: 멀티 세션 오케스트레이션 + 위임 + 학습 캡처
- **spawn**: 일회성 병렬 서브에이전트 실행

### 구현 계열
- **implement**: 코드 작성/수정 (기능, 버그 수정)
- **build**: 컴파일, 패키징, 배포 아티팩트

### 문서 계열
- **document**: 사람이 읽는 산문 문서
- **index**: 구조화된 지식 베이스 생성
- **index-repo**: 리포지토리 구조 카탈로그 (토큰 효율적)

### 탐색 계열
- **brainstorm**: 소크라틱 요구사항 발굴 (대화형, 탐색적)
- **research**: 체계적 증거 기반 조사 (웹 검색, 인용)

---

## 7. 세션 관리

### 세션 목표 설정

`/sc:load` 시 세션 목표를 선택적으로 설정할 수 있습니다:

```
/sc:load
> 세션 목표: "auth 모듈 마이그레이션 완료"
```

- 컨텍스트가 60%를 초과하면 목표를 리마인더로 표시
- `/sc:save` 시 목표 달성 상태를 평가 (완료/부분/보류)

### 컴팩션 전략

`/sc:save` 시 자동 적용되는 보존/폐기 기준:

| 보존 (고신호) | 폐기 (저신호) |
|-------------|-------------|
| 아키텍처 결정 + 근거 | 도구 출력 원문 (파일 내용, grep 결과) |
| 미해결 이슈 | 막다른 길 도달한 중간 검색 결과 |
| 핵심 패턴 발견 | 이미 커밋된 코드 diff |
| 세션 목표 상태 | 이전 세션의 중복 컨텍스트 |

### 규칙 효과성 추적

모든 핵심 규칙에 [R01]~[R16] ID가 부여되었습니다. Correction Capture (R14) 시 어떤 규칙이 위반됐는지 기록합니다:

```
{
  trigger: "유저가 말한 것",
  misread: "내가 이해한 것",
  actual_intent: "실제 의도",
  violated_rule: "[R06]",
  prevention: "다음에 이렇게 방지"
}
```

시간이 지나면 어떤 규칙이 가장 자주 위반되는지, 어떤 규칙은 불필요한지 패턴을 분석할 수 있습니다.

---

## 8. 환경 변수

| 변수 | 기본값 | 설명 |
|------|-------|------|
| `CLAUDE_CONTEXT_MAX_TOKENS` | `8000` | on-demand 컨텍스트 토큰 예산 |
| `CLAUDE_CONTEXT_USE_INSTRUCTIONS` | `1` | `0`으로 설정 시 모든 파일 full .md 주입 |
| `CLAUDE_CONTEXT_INJECT` | `1` | `0`으로 설정 시 directive 모드 (Claude가 직접 Read) |
| `CLAUDE_SHOW_SKILLS` | `1` | `0`으로 설정 시 스킬 요약 숨김 |

---

## 9. 문제 해결

### Claude가 MCP를 잘못 사용할 때

```bash
# 1단계: --verbose-context로 전체 지침 주입
/sc:implement --verbose-context --serena

# 2단계: 그래도 안 되면 환경 변수로 전체 모드
CLAUDE_CONTEXT_USE_INSTRUCTIONS=0
```

### "Budget exceeded" 경고가 자주 뜰 때

```bash
# 불필요한 플래그 줄이기
/sc:research --tavily            # --seq 제거 (기본 추론 충분)
/sc:implement --c7               # --serena 제거 (심볼 탐색 불필요 시)

# 또는 MCP 완전 비활성화
/sc:implement --no-mcp           # 네이티브 도구 + WebSearch만 사용
```

### 모드가 로드되지 않을 때

모드는 세션 내 중복 방지(dedup) 캐시를 사용합니다. 같은 세션에서 이미 로드된 모드는 다시 주입되지 않습니다. 새로 로드하려면:

```bash
# 캐시 초기화 (새 세션 시작과 동일 효과)
rm ~/.claude/.superclaude_hooks/claude_context_*.txt
```

---

## 10. 아키텍처 요약

```
사용자 프롬프트
    │
    ▼
context_loader.py (UserPromptSubmit 훅)
    │
    ├── 플래그 해석 (FLAG_ALIASES, 퍼지 매칭)
    ├── 실행 디렉티브 (_EXECUTION_DIRECTIVES)
    ├── 트리거 감지 (TRIGGER_MAP, COMPOSITE_FLAGS)
    │
    ▼
_get_injection_tier() — 파일별 Tier 결정
    │
    ├── Tier 0 → TIER_0_MAP (1줄)    → <sc-context-hint>
    ├── Tier 1 → INSTRUCTION_MAP     → <sc-context>
    └── Tier 2 → full .md read       → <context-inject>
    │
    ▼
토큰 예산 확인 (MAX_TOKENS_ESTIMATE)
    │
    ├── 예산 내 → 주입
    └── 초과 → 스킵 + ⚠️ 경고
```

---

## 부록: 관련 파일

| 파일 | 역할 |
|------|------|
| `src/superclaude/scripts/context_loader.py` | 3-Tier 주입 엔진 |
| `src/superclaude/core/FLAGS.md` | 플래그 분류 체계 |
| `src/superclaude/core/RULES.md` | 규칙 + 예시 ([R01]-[R16]) |
| `src/superclaude/core/PRINCIPLES.md` | 원칙 + 예시 |
| `src/superclaude/commands/help.md` | 명령어 범위 구분 (scope_map) |
| `src/superclaude/commands/load.md` | 세션 목표 설정 |
| `src/superclaude/commands/save.md` | 컴팩션 전략 + 목표 평가 |
| `tests/unit/test_context_loader.py` | 28개 테스트 (Tier 검증 포함) |
| `docs/specs/2026-03-22-context-engineering-*` | 설계 스펙 |
| `docs/plans/2026-03-22-context-engineering-*` | 구현 계획 |
