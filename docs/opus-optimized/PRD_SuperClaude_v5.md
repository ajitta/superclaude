# SuperClaude v5.0 PRD

## Opus 4.5 Optimized Edition

---

## 1. Overview

| 항목 | 내용 |
|------|------|
| **제품명** | SuperClaude Framework v5.0 |
| **버전** | 1.7 (2025-12-21) |
| **목표** | Opus 4.5 패러다임에 최적화된 AI 개발 프레임워크 |
| **핵심 원칙** | 명시적 요구사항 + 구조화된 프롬프트 + 검증 가능한 출력 + 자연스러운 상호작용 |

---

## 2. 프레임워크 운영 원칙

> ⚠️ **출처 분류**: 본 섹션은 Anthropic 공식 문서가 아닌 **프레임워크 설계 결정**입니다.
> 프롬프트 엔지니어링 경험과 커뮤니티 모범 사례를 기반으로 한 운영 원칙이며,
> 프로젝트 요구에 따라 조정될 수 있습니다.

### 2.1 프레임워크 설계 원칙 *(경험적 관찰 기반)*

본 프레임워크는 다음과 같은 원칙을 채택합니다:

| 관찰된 경향 | 프레임워크 대응 | 근거 |
|-------------|----------------|------|
| 명시적 지시가 더 일관된 결과 생성 | 모든 지시 명시적 작성 | *(경험적)* |
| 완전한 요구사항이 재작업 감소 | 완전한 요구사항 정의 | *(프레임워크 정책)* |
| 긴 컨텍스트에서 맥락 위치가 중요 | 맥락 우선 배치 (질문 앞에) | [Anthropic Long Context Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) |
| 구조화된 입력이 파싱 용이 | 규칙+근거 함께 제공 | [Anthropic Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) |
| 톤 조절이 상호작용 품질 영향 | 협력적 요청 톤 사용 | *(경험적)* |

### 2.2 프레임워크가 권장하지 않는 기법 *(경험적 관찰)*

| 비권장 기법 | 관찰된 문제 | 대체 방법 | 근거 |
|------------|------------|----------|------|
| 공격적 언어 ("CRITICAL", "MUST", ALL CAPS) | 자연스러운 표현이 더 효과적 | 맥락+논리 기반 설명 | [가이드 §1] |
| "절대 ~하지 마" | "하지 말 것"보다 "할 것" 중심이 효과적 | "~해줘"로 긍정적 재구성 | [가이드 §마이그레이션] |
| "단계별로 생각해" 단순 CoT | Extended Thinking 내재화로 중복 | Chain of Draft 활용 (§4.7) | [가이드 §고급 기법] |
| 반복 강조 | 토큰 비효율 *(측정 기반)* | 한 번 명확히 정의 | *(프레임워크 정책)* |
| 과도한 명령형 톤 | Opus 4.5 반응성 특성과 충돌 가능 | 직접적이고 자연스러운 표현 | [가이드 §1] |

### 2.3 프레임워크가 채택한 7대 핵심 기법

| 기법 | 효과성 평가 | 적용 방법 | 근거 |
|------|------------|----------|------|
| **구조화된 프롬프트** | 높음 *(공식 권고)* | XML + JSON + 명확한 헤더 | [Anthropic XML Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) |
| **Extended Thinking** | 높음 *(공식 기능)* | 복잡도 기반 자동 활성화 *(조정 권장)* | [Anthropic Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) |
| **명시적 요구사항** | 높음 *(내부 평가)* | 구체적 완료 기준 정의 | [가이드 §1] |
| **퓨샷 프롬프팅** | 높음 *(공식 권고)* | 3-5개 다양한 예제 (30% 향상) | [Anthropic Few-shot](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting) |
| **맥락 우선 배치** | 높음 *(연구 검증)* | 20K+ 토큰은 질문 앞에 (30% 향상) | [가이드 §컨텍스트 배치] |
| **Prefilling** | 높음 *(공식 기능)* | 응답 시작부 미리 작성 (API 전용) | [Anthropic Prefill Guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prefill-claudes-response) |
| **Chain of Draft** | 높음 *(연구 검증)* | `<draft>` 5단어 이내 미니멀 추론 | [arXiv:2502.18600](https://arxiv.org/abs/2502.18600) |

> 📊 **효과성 평가 기준**: "높음/중-높음"은 프레임워크 내부 테스트 또는 외부 연구 결과이며, 정량적 벤치마크가 아닙니다.

---

## 3. 아키텍처 설계

### 3.1 3-Tier 로딩 시스템

> 📁 **개발 구조**: 
> - **v5 개발 경로**: `src/superclaude-v5/` (새로 생성, 기존 `src/superclaude/`와 병렬 개발)
> - **배포 경로**: `~/.claude/` (설치 후 사용자 환경)
> - **기존 v4**: `src/superclaude/` (그대로 유지)

```
src/superclaude-v5/                          # v5 개발 시 (새로 생성)
~/.claude/                                   # 배포 후 (사용자 환경)

├── CLAUDE.md                                # 진입점 + 로딩 규칙 (~200 토큰)
│
├── core/                                    # Tier 1: 항상 로드 (~500 토큰)
│   ├── RULES_CORE.md                        # 압축된 핵심 규칙
│   └── OPUS_PROFILE.md                      # Opus 4.5 최적화 프로파일
│
├── modes/                                   # Tier 2: 조건부 로드 (키워드 트리거)
├── mcp/                                     # Tier 2: 조건부 로드 (도구 사용 시)
│
├── agents/                                  # Tier 3: 동적 로드 (12개)
└── commands/                                # Tier 3: 동적 로드 (15개)
```

### 3.2 Anthropic 10단계 프레임워크 적용

| 단계 | 구성요소 | SuperClaude 적용 |
|------|----------|-----------------|
| 1 | **Task Context** (역할) | agents/ 파일의 Role 섹션 |
| 2 | **Tone Context** (톤) | 협력적, 전문적 |
| 3 | **Background Data** (배경) | Tier 1 core/ 파일들 |
| 4 | **Detailed Task** (상세 작업) | commands/ 파일 |
| 5 | **Examples** (예제) | 각 파일의 Examples 섹션 |
| 6 | **Conversation History** (대화) | 세션 컨텍스트 |
| 7 | **Immediate Task** (즉각 작업) | 사용자 프롬프트 |
| 8 | **Thinking** (사고) | Extended Thinking |
| 9 | **Output Format** (출력 형식) | 명시적 형식 지정 |
| 10 | **Prefilled Response** (시작) | 선택적 프리필 |

### 3.3 계층적 프롬프트 설계

```xml
<global_context>                    <!-- Tier 1: 항상 적용 -->
  <model>opus-4.5</model>
  <style>goal-oriented, collaborative</style>
  <constraints>명시적, 검증 가능</constraints>
</global_context>

<session_context>                   <!-- Tier 2: 세션 레벨 -->
  <mode>현재 활성 모드</mode>
  <mcp_tools>사용 중인 MCP</mcp_tools>
  <domain>코딩|연구|비즈니스|창작</domain>
</session_context>

<task_context>                      <!-- Tier 3: 작업 레벨 -->
  <agent>호출된 에이전트</agent>
  <command>실행 중인 명령어</command>
  <output_format>요청된 형식</output_format>
  <success_criteria>구체적 완료 기준</success_criteria>
</task_context>
```

---

## 4. 핵심 기능 요구사항

### 4.1 구조화된 프롬프트 시스템

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-1 | Minimal XML 메타데이터 | `<document>`, `<activation>`, `<autonomy>` | P0 |
| FR-2 | MD 테이블 형식 | 규칙/플래그를 테이블로 압축 | P0 |
| FR-3 | 심볼 시스템 | →, ⇒, », ∴, ∵ 등 의미 압축 | P1 |
| FR-4 | 퓨샷 예제 | 각 명령어에 3-5개 예제 포함 | P1 |
| FR-5 | 맥락 우선 배치 | 긴 문서(20K+)는 질문 앞에 배치 | P0 |

### 4.2 Extended Thinking 통합

> ⚠️ **구분**: Extended Thinking은 [Anthropic 공식 기능](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)입니다.
> 단, 아래 트리거 조건 및 예산 값은 **프레임워크 기본 설정**이며, 프로젝트 요구에 따라 조정 가능합니다.

| ID | 요구사항 | 트리거 조건 | 근거 | 상태 |
|----|----------|------------|------|------|
| FR-6 | 자동 활성화 | 복잡도 기반 자동 감지 *(조정 권장)* | *(프레임워크 휴리스틱)* | P0 |
| FR-7 | 수동 활성화 | 문서 안내: `/sc:think` (CLI 별칭 미구현) → 실제 사용은 `/sc:plan --deep` 또는 `--deep` 플래그 | *(프레임워크 정책)* | P1 |
| FR-8 | 투명성 옵션 | 사고 과정 표시 선택 가능 | *(프레임워크 정책)* | P2 |
| FR-9 | 예산 조절 | `--think` (5K), `--think-hard` (10K), `--ultrathink` (32K) | *(프레임워크 기본값, 조정 가능)* | P1 |

> 📝 **참고**: 복잡도 임계값은 프로젝트별로 조정 권장합니다.
> 토큰 예산 5K는 "낮은 effort"로 시작하여 점진적 증가를 권장합니다. [가이드 §Extended Thinking]
> 단순한 쿼리나 사실 검색에는 Thinking 비활성화가 비용 효율적입니다.

**Native Thinking vs 프레임워크 Thinking 태그 역할 분담**:

> ⚠️ **중요**: Opus 4.5는 내부적으로 Hidden Chain of Thought를 수행합니다. 
> 프롬프트 레벨의 `<thinking>` 태그와 중복 시 토큰 낭비(Over-thinking)가 발생할 수 있습니다.

| 용도 | 권장 방식 | 비고 |
|------|----------|------|
| **복잡한 논리 추론** | Native Extended Thinking (`budget_tokens` 조절) | 모델 내장 기능 활용 |
| **작업 계획 수립** | 프레임워크 `<planning>` 태그 | 사용자 가시성 목적 |
| **아웃풋 포맷 준비** | 프레임워크 `<format_prep>` 태그 | 출력 구조화 목적 |
| **간결한 중간 추론** | Chain of Draft (§4.7) | 토큰 효율성 목적 |

```xml
<!-- Native Thinking: API 파라미터로 제어 -->
{"thinking": {"type": "enabled", "budget_tokens": 10000}}

<!-- 프레임워크 태그: 계획/포맷 용도로 축소 -->
<planning>1. 요구사항 파악 2. 구현 3. 검증</planning>
<format_prep>JSON 출력, 3개 필드</format_prep>
```

### 4.3 MCP 우선 정책

> ⚠️ **구분**: MCP(Model Context Protocol)는 [Anthropic 공식 표준](https://modelcontextprotocol.io/)입니다.
> 아래 "우선 정책"은 **프레임워크 운영 결정**이며, 작업 특성에 따라 조건부 적용됩니다.

| ID | 요구사항 | 성능 개선 | 근거 | 상태 |
|----|----------|----------|------|------|
| FR-10 | 도구 선택 계층 | MCP > Native > Basic *(조건부)* | *(프레임워크 정책)* | P0 |
| FR-11 | Tool Search Tool | 지연 로딩으로 토큰 감소 *(추정 30-40%)* | *(내부 측정)* | P1 |
| FR-12 | 병렬 도구 호출 | 독립 작업 동시 실행 | [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview) | P1 |

**FR-10 적용 조건**:
- MCP 서버가 사용 가능하고 신뢰할 수 있는 경우
- 필요한 capability를 MCP가 제공하는 경우
- Native 도구로 충분한 경우 MCP 불필요

**도구 사용 제어 템플릿** *(Opus 4.5 시스템 프롬프트 반응성 고려)*:

보수적 모드 (기본 권장) - 제안 우선, 명시적 요청 시에만 실행:
```xml
<default_to_action>
Suggest changes rather than implementing them by default.
If user intent is unclear, provide information and recommendations only.
Take action only when explicitly requested.
</default_to_action>
```

적극적 모드 - 실행 우선, 추론 기반 행동:
```xml
<default_to_action>
Implement changes rather than just suggesting them by default.
If intent is unclear, take the action most likely to be useful.
</default_to_action>
```

### 4.4 검증 및 환각 방지

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-13 | 신뢰도 점수 | 0-1 scale 명시 (0.9 = 높은 확신) | P1 |
| FR-14 | 불확실성 표시 | "확인 필요", "추정", "아마도" 라벨 | P1 |
| FR-15 | 사실 검증 | 주장에 근거 필수, 출처 명시 | P0 |
| FR-16 | 교차 검증 | 다중 소스 확인 | P2 |

### 4.5 고급 프롬프트 패턴

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-17 | 메타-프롬프팅 | 프롬프트 자체 생성/최적화 지원 | P1 |
| FR-18 | 자기-개선 루프 | initial → analysis → improved 패턴 | P1 |
| FR-19 | 동적 체이닝 | 복잡도 기반 자동 작업 분해 | P2 |
| FR-20 | 자연스러운 톤 | 직접적이고 명확한 표현 사용 | P0 |

### 4.6 Prefilling 및 응답 제어 (NEW)

> ⚠️ **출처**: [Anthropic 공식 문서](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prefill-claudes-response)
> **적용 범위**: API 직접 호출 시에만 사용 가능. CLI 환경에서는 프롬프트 기반 형식 강제로 대체.

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-21 | JSON 출력 강제 | `{"role": "assistant", "content": "{"}` 프리필 | P1 |
| FR-22 | 형식 일관성 | 응답 시작부 템플릿 제공 | P1 |
| FR-23 | 서론/맺음말 제거 | 본문 직접 시작 강제 | P2 |

**API 예시:**
```python
messages = [
    {"role": "user", "content": "이 데이터를 JSON으로 변환하세요: 이름=홍길동, 나이=30"},
    {"role": "assistant", "content": "{"}  # Prefill - JSON 직접 시작
]
```

**CLI 환경 대체** (Prefilling 불가 시 프롬프트로 형식 강제):
```xml
<output_format>
Output JSON only. Start with { and end with }.
No preamble, no explanation, no markdown fences.
</output_format>
```

### 4.7 Chain of Draft (CoD) 패턴 (NEW)

> ⚠️ **출처**: [arXiv:2502.18600 "Chain of Draft: Thinking Faster by Writing Less"](https://arxiv.org/abs/2502.18600)
> 핵심: **각 추론 단계를 5단어 이내로 제한**하여 CoT 수준 성능을 유지하면서 토큰 대폭 절감.

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-24 | Chain of Draft 적용 | `<draft>` 내 각 단계를 **5단어 이내 핵심 키워드**로 제한 | P1 |
| FR-25 | 도구 통합 | 간결한 추론 → 도구 호출 → 최소 재분석 | P1 |

**CoD vs 기존 CoT 비교**:

| 방식 | 토큰 사용량 | 성능 | 적용 시나리오 |
|------|-----------|------|--------------|
| Verbose CoT | 높음 | 기준선 | Extended Thinking에 위임 |
| Chain of Draft | **최소** (~90% 절감) | CoT 동등 | 프레임워크 기본 모드 |
| Zero-shot | 없음 | 낮음 | 단순 사실 검색 |

**표준 패턴** (5단어 이내 미니멀 추론):
```xml
<draft>
step1: auth check → token valid
step2: user perms → admin role
step3: action → approve request
result: grant access
</draft>

<action>
[Tool call with minimal context]
</action>
```

**기존 Verbose 방식 (비권장)**:
```xml
<!-- ❌ 토큰 낭비 - Native Extended Thinking과 중복 -->
<thinking>
Current situation analysis:
1. First, I need to check if the user is authenticated...
2. Then, I should verify the user's permissions...
</thinking>
```

**CoD 변환 예시**:

| Verbose CoT (Before) | Chain of Draft (After) |
|----------------------|------------------------|
| "First, let me analyze the error message to understand what's happening" | "error: null ref → line 42" |
| "The user is requesting a feature that requires authentication" | "need: auth → check token" |
| "Based on my analysis, the best approach would be to..." | "approach: cache + retry" |

> 📝 **참고**: 복잡한 논리 추론이 필요한 경우 Native Extended Thinking의 `budget_tokens`를 증가시키세요.
> CoD는 모델의 내부 추론을 대체하는 것이 아니라, **출력 토큰**을 최소화하는 기법입니다.

### 4.8 Skeleton-of-Thought 병렬 처리 (NEW)

> ⚠️ **출처**: [arXiv:2307.15337] - 속도와 품질 동시 향상

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-26 | 골격 우선 생성 | 1단계: 3-5개 핵심 포인트 개요 요청 | P2 |
| FR-27 | 병렬 확장 | 2단계: 각 포인트 동시 확장 | P2 |

**적용 시나리오:**
- 긴 문서 생성
- 복잡한 분석 보고서
- 다중 섹션 응답

**실행 예시** (골격 생성 → 병렬 확장):
```
Step 1: "Provide an outline/skeleton of 3-5 key points for the following question"
Step 2: "Expand point 1 of the skeleton into 2-3 sentences"
        "Expand point 2 of the skeleton into 2-3 sentences" (parallel execution)
```

### 4.9 Over-Engineering 방지 (NEW)

> ⚠️ **중요**: Opus 4.5는 요청하지 않은 기능/추상화/리팩토링 추가 경향이 있습니다. [가이드 §Over-Engineering]

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-28 | 범위 제한 명시 | "직접 요청된 변경만 수행" 지시 포함 | P0 |
| FR-29 | 불필요한 추가 방지 | "버그 수정에 코드 정리 불필요" 명시 | P0 |
| FR-30 | 단순성 유지 | "간단하고 초점을 맞춘 솔루션" 강조 | P1 |

**시스템 프롬프트 템플릿** (범위 제한 + 단순성 유지):
```xml
<over_engineering_prevention>
Do not over-engineer. Make only changes that are directly requested 
or clearly necessary. Keep solutions simple and focused.

- Do not add unnecessary cleanup to bug fixes.
- Do not add excessive configurability to simple features.
- Do not design for hypothetical future requirements.
- Reuse existing abstractions; follow DRY principle.
</over_engineering_prevention>
```

### 4.10 안전한 프롬프팅 (NEW)

> ⚠️ **프로덕션 환경 필수**: 단계적 검증 통합 [가이드 §안전한 프롬프팅]

| ID | 요구사항 | 구현 방법 | 상태 |
|----|----------|----------|------|
| FR-31 | 작업 범위 제한 | 명시된 작업 범위(allowlist/denylist) 내에서만 수정 | P0 |
| FR-32 | 확인 요청 | "파괴적 작업 전 사용자 확인" | P0 |
| FR-33 | 단계적 실행 | 변경 → 검증 → 확인 → 다음 단계 | P1 |

**경로 제한 설정 방식:**

| 방식 | 적용 시나리오 | 예시 |
|------|--------------|------|
| **Allowlist** | 수정 가능 경로 명시 | `allowed_paths: [src/, tests/, docs/]` |
| **Denylist** | 수정 금지 경로 명시 | `denied_paths: [node_modules/, .git/, dist/]` |
| **Workspace 인식** | Monorepo/Multi-repo | `workspaces: [packages/*, apps/*]` |
| **동적 감지** | 프로젝트 구조 자동 인식 | package.json의 workspaces 필드 참조 |

**시스템 프롬프트 템플릿** (프로젝트별 커스터마이징):
```xml
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

> 📝 **참고**: 경로 제한은 프로젝트 구조에 따라 CLAUDE.md 또는 프로젝트 설정에서 정의합니다.
> `src/` 하드코딩은 단일 레포 간단한 프로젝트에만 적합합니다.

---

## 5. 도메인별 최적화 전략 (NEW)

### 5.1 코딩 도메인

| 최적화 | 적용 방법 |
|--------|----------|
| Extended Thinking | 복잡한 알고리즘에 자동 활성화 |
| 단계별 구현 | 계획 → 구현 → 테스트 |
| 코드 리뷰 시뮬레이션 | self-review 에이전트 활용 |
| TDD 접근 | 테스트 먼저 작성 권장 |

### 5.2 연구 도메인

| 최적화 | 적용 방법 |
|--------|----------|
| Systematic Review | 체계적 문헌 검토 방법론 |
| 신뢰도 평가 | 모든 주장에 confidence level |
| 출처 검증 | primary > secondary 소스 구분 |
| 편향 평가 | bias assessment 포함 |

### 5.3 비즈니스 도메인

| 최적화 | 적용 방법 |
|--------|----------|
| 분석 프레임워크 | SWOT, PESTEL, Porter 활용 |
| 정량적 지표 | KPI, ROI, NPV 명시 |
| 리스크 평가 | probability × impact 매트릭스 |
| 우선순위 | impact-effort 매트릭스 |

### 5.4 창작 도메인

| 최적화 | 적용 방법 |
|--------|----------|
| 아이디에이션 | brainstorming, mind mapping |
| 개발 과정 | outline → draft → revise |
| 창의성 경계 | 제약이 더 나은 창의적 결과 |
| 품질 지표 | 독창성, 가독성, 일관성 |

---

## 6. 콘텐츠 최적화

### 6.1 에이전트 통합 (21 → 12)

| 통합 전 | 통합 후 | 핵심 역할 |
|--------|--------|----------|
| system-architect + backend-architect | architecture-expert | 시스템/백엔드 설계 |
| performance-engineer + quality-engineer | quality-expert | 품질/성능 |
| deep-research + deep-research-agent | research-agent | 심층 리서치 |
| requirements-analyst + pm-agent | product-expert | 제품 관리 |
| learning-guide + socratic-mentor | learning-expert | 학습 지원 |
| frontend-architect | frontend-expert | 프론트엔드 |
| security-engineer | security-expert | 보안 |
| devops-architect | devops-expert | DevOps |
| python-expert | python-expert | Python |
| refactoring-expert | refactoring-expert | 리팩토링 |
| technical-writer | technical-writer | 문서화 |
| self-review | self-review | 자기 검토 |

### 6.2 명령어 간소화 (31 → 15)

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

### 6.3 모드 최적화 (7 → 4)

| 유지 모드 | 트리거 키워드 | 용도 |
|----------|--------------|------|
| orchestration | multi-tool, parallel, optimize | 도구 조합 |
| deep-research | research, investigate, deep-analysis | 리서치 |
| brainstorming | brainstorm, explore, ideas, maybe | 창의적 탐색 |
| business-panel | business, panel, stakeholder | 비즈니스 |

| 제거 모드 | 이유 |
|----------|------|
| Introspection | Extended Thinking이 대체 |
| Task_Management | Orchestration에 통합 |
| Token_Efficiency | 기본 동작으로 내재화 |

---

## 7. 성능 목표

### 7.1 토큰 효율성 *(실측 완료)*

> 📊 **측정 기준**: 아래 수치는 프레임워크 문서/로딩 전략 최적화 성과이며,
> 모델 자체 성능 개선과는 별개입니다. v4 → v5 마이그레이션 기준으로 측정되었습니다.

| 지표 | Before (v4) | After (v5) | 절감율 | 상태 |
|------|-------------|------------|--------|------|
| 에이전트 총량 | 90,034 chars | 19,619 chars | **78.2%** | ✅ 실측 |
| 명령어 총량 | 172,599 chars | 14,839 chars | **91.4%** | ✅ 실측 |
| 모드 총량 | 26,716 chars | 5,763 chars | **78.4%** | ✅ 실측 |
| Core 총량 | 49,675 chars | 4,467 chars | **91.0%** | ✅ 실측 |
| MCP 총량 | 19,849 chars | 4,847 chars | **75.6%** | ✅ 실측 |
| **전체** | 358,873 chars | 51,535 chars | **85.6%** | ✅ 실측 |

> **참고**: 명령어에 Success Criteria, Boundaries 섹션 추가 후 품질 개선과 함께 85.6% 절감 달성.

> **참고**: Opus 4.5 공식 효율성 개선(76% 토큰 절감, [Anthropic 발표](https://www.anthropic.com/news/claude-opus-4-5))과는 별도의 프레임워크 레벨 최적화입니다.

### 7.2 기능 품질 *(구현 완료)*

| 지표 | 목표 | 실측 | 상태 |
|------|------|------|------|
| 명령어 Boundaries 섹션 | 100% | 15/15 (100%) | ✅ 완료 |
| 명령어 Success Criteria | 100% | 15/15 (100%) | ✅ 완료 |
| MCP Example 섹션 | 100% | 7/7 (100%) | ✅ 완료 |
| 에이전트 Examples (3+) | 100% | 12/12 (100%) | ✅ 완료 |
| 파일 수 절감 (Agents) | 43% | 21→12 (43%) | ✅ 달성 |
| 파일 수 절감 (Commands) | 52% | 31→15 (52%) | ✅ 달성 |
| 파일 수 절감 (Modes) | 43% | 7→4 (43%) | ✅ 달성 |

> 📝 **참고**: 조건부 로딩 정확도, Extended Thinking 활성화율은 실사용 테스트 후 검증 예정.

### 7.3 성공 기준 (구체화)

각 작업의 성공적인 출력 기준:

```markdown
성공적인 출력은:
- 요청된 형식과 정확히 일치
- 모든 주장에 근거 포함
- 불확실한 부분 명시적 표시
- 실행 가능한 단계로 구성
- 요청된 범위 내에서 완결
```

### 7.4 Opus 4.5 벤치마크 참조 (NEW)

> 📊 **출처**: [가이드 §성능 벤치마크]

| 벤치마크 | Opus 4.5 점수 | 비교 대상 | 비고 |
|---------|--------------|----------|------|
| SWE-bench | 80.9% | Gemini 3 Pro 76.2% | 코딩 능력 |
| Terminal-Bench 2.0 | *검증 필요* | Gemini 3 Pro 54.2% (최상위) | 터미널 작업 *(버전/측정 차이 확인 필요)* |
| Token Efficiency | 76% 절감 | Sonnet 4.5 동등 점수 기준 | 비용 효율 |

---

## 8. 파일 형식 규격

### 8.1 표준 문서 형식

```markdown
---
name: [파일명]
type: core|mode|agent|command|mcp
priority: critical|high|medium|low
triggers: [키워드1, 키워드2]  # optional for core
domain: coding|research|business|creative  # optional for core/mcp
---

<document type="[type]" name="[name]">

# [제목]

## Role
[역할 한 문장 정의 - 협력적 톤]

## Keywords
[트리거 키워드]

## Capabilities
| 역량 | 산출물 | 품질 기준 |
|------|--------|----------|
| ... | ... | ... |

## Examples (3-5개)
<example>
  <input>입력 예제</input>
  <output>출력 예제</output>
</example>

## Success Criteria
- [구체적 완료 기준 1]
- [구체적 완료 기준 2]

## Boundaries
| Will | Won't |
|------|-------|
| ... | ... |

## Chain of Draft Structure (선택적)
<draft>step1: [키워드] → step2: [키워드] → result: [결론]</draft>
<action>[도구 호출]</action>

## Safety Constraints (선택적)
[경로 제한, 확인 요구사항]

</document>
```

### 8.2 심볼 시스템

| 심볼 | 의미 | 예시 |
|------|------|------|
| → | implies | `auth → 🛡️ risk` |
| ⇒ | transforms | `input ⇒ output` |
| » | sequence | `build » test » deploy` |
| ∴ | therefore | `tests ❌ ∴ broken` |
| ∵ | because | `slow ∵ O(n²)` |
| ✅ | completed | 상태 표시 |
| ❌ | failed/no | 상태 표시 |
| 🔄 | in progress | 상태 표시 |
| ⏳ | pending | 상태 표시 |
| 🚨 | critical | 경고 표시 |
| 🤔 | uncertainty | 불확실성 표시 |
| 📊 | confidence | 신뢰도 표시 |

### 8.3 언어 정책 (NEW)

> 📝 **근거**: 영어 프롬프트가 토큰 효율(30-50% 절감)과 모델 성능에서 우위를 보입니다.
> Claude는 영어 학습 데이터가 가장 많아 영어 지시를 더 정확히 따릅니다.

| 대상 | 언어 | 근거 |
|------|------|------|
| **CLAUDE.md** | 영어 | Tier 1 핵심 파일, 토큰 효율 최우선 |
| **core/*.md** | 영어 | 핵심 규칙, 항상 로드 |
| **agents/*.md** | 영어 | 시스템 프롬프트 역할 |
| **commands/*.md** | 영어 | 명령어 정의 및 트리거 |
| **modes/*.md** | 영어 | 모드 트리거 및 동작 규칙 |
| **mcp/*.md** | 영어 | 도구 설정 및 호출 패턴 |
| **PRD/설계 문서** | 팀 언어 | 팀 협업 및 이해도 |
| **사용자 facing 문서** | 대상 사용자 언어 | UX 최적화 |
| **코드 주석** | 영어 | 국제 표준, 일관성 |

**구현 파일 작성 원칙:**

```markdown
## 영어로 작성할 내용
- Role/역할 정의
- Keywords/트리거 키워드
- System prompts/시스템 프롬프트
- Success criteria/성공 기준
- Boundaries/경계 정의
- Examples의 output (코드, 구조화된 출력)

## 대상 언어로 작성 가능한 내용 (선택적)
- Examples의 input (사용자 입력 시뮬레이션)
- 문서 내 설명 주석 (<!-- 한국어 설명 -->)
```

**예시: agents/architecture-expert.md**

```markdown
# Architecture Expert

## Role
System and backend architecture design expert specializing in 
scalable, maintainable, and secure software systems.

## Keywords
architecture, design, scale, microservices, patterns

## Capabilities
| Capability | Output | Quality Criteria |
|------------|--------|------------------|
| System design | Architecture diagrams | Addresses all requirements |
| Tech selection | Comparison matrix | Evidence-based decisions |

## Examples
<example>
  <input>마이크로서비스 아키텍처를 설계해줘</input>  <!-- 사용자 언어 OK -->
  <output>
  ## Architecture Overview
  
  ### Components
  1. API Gateway (Kong/Nginx)
  2. Service Mesh (Istio)
  ...
  </output>  <!-- 영어 출력 -->
</example>
```

---

## 9. 위험 및 완화

| 리스크 | 확률 | 영향 | 완화 전략 |
|--------|------|------|----------|
| 키워드 오탐지 | 중간 | 중간 | 복합 키워드 조건 + 명시적 플래그 우선 |
| 필요 리소스 미로드 | 낮음 | 높음 | 폴백 메커니즘 + 수동 로드 옵션 |
| 하위 호환성 깨짐 | 중간 | 높음 | 단계적 마이그레이션 + v4 archive |
| Extended Thinking 과다 사용 | 중간 | 낮음 | 복잡도 임계값 조정 |
| 협력적 톤 과도 적용 | 낮음 | 낮음 | 도메인별 톤 가이드 |

---

## 10. 의존성

| 의존성 | 상태 | 비고 | 유형 |
|--------|------|------|------|
| Claude Code @import | ✅ | 조건부 로딩 지원 | *(환경 의존, 확인 필요)* |
| Opus 4.5 | ✅ | Extended Thinking 지원 | [공식 기능](https://www.anthropic.com/claude/opus) |
| MCP 서버들 | ✅ | Context7, Magic, Playwright 등 | [공식 표준](https://modelcontextprotocol.io/) |
| SuperClaude v4 | ⏳ | archive/v4/에 백업 | *(내부 자산)* |

> 📝 **Claude Code @import 참고**: Claude Code의 @import 구문 지원 여부는 환경(IDE, 버전)에 따라 다를 수 있습니다.
> 사용 전 해당 환경에서의 지원 여부를 확인하세요.

---

## 11. 출처 분류표

> 본 문서의 내용은 다음과 같이 분류됩니다:

| 라벨 | 의미 | 예시 |
|------|------|------|
| **[공식 기능]** | Anthropic 공식 문서에서 확인된 기능 | Extended Thinking, MCP, Tool Use |
| **[공식 권고]** | Anthropic이 권장하는 기법 | XML 태그, 퓨샷 프롬프팅 |
| *(프레임워크 정책)* | SuperClaude가 채택한 운영 방침 | MCP 우선 정책, 협력적 톤 |
| *(프레임워크 기본값)* | 조정 가능한 기본 설정 | 복잡도 ≥7, 토큰 예산 5K/10K/32K |
| *(프레임워크 휴리스틱)* | 경험적으로 도출된 규칙 | 자동 활성화 조건 |
| *(내부 측정)* | 프레임워크 자체 측정 결과 | 토큰 절감율, 파일 크기 |
| *(목표)* | 달성 예정 수치, 미검증 | 품질 지표 95%+, 환각률 <5% |
| *(경험적)* | 커뮤니티/팀 경험 기반, 공식 검증 없음 | 패러다임 변화 관찰 |
| *(추정)* | 근사치 또는 예상값 | 토큰 감소 30-40% |

---

## 12. 참조 링크

### Anthropic 공식 문서
- [Anthropic Prompt Engineering Overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Claude 4 Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices) *(NEW)*
- [Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
- [Prefill Claude's Response](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prefill-claudes-response) *(NEW)*
- [Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)
- [XML Tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
- [Multishot Prompting](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting)
- [Prompt Caching (Long Context)](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Claude Opus 4.5 발표](https://www.anthropic.com/news/claude-opus-4-5)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)

### 연구 논문 *(NEW)*
- [Chain of Draft: Thinking Faster by Writing Less](https://arxiv.org/abs/2502.18600)
- [Skeleton-of-Thought](https://arxiv.org/pdf/2307.15337.pdf)
- [Safe Prompting Patterns](https://milvus.io/ai-quick-reference/what-are-safe-prompting-patterns-for-claude-opus-45-in-production)

### 프레임워크 내부 문서
- [PLAN_SuperClaude_v5.md](./PLAN_SuperClaude_v5.md) - 상세 구현 계획
- [Claude Opus 4.5 프롬프트 엔지니어링 최적화 가이드](./Claude%20Opus%204.5%20프롬프트%20엔지니어링%20최적화%20가이드-perplexity.md)
- [Claude Opus 4.5 프롬프트 엔지니어링 최적화 심층 연구 보고서](./Claude%20Opus%204.5%20프롬프트%20엔지니어링%20최적화%20심층%20연구%20보고서.md)

---

## 13. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-12-20 | 초안 작성 |
| 1.1 | 2025-12-21 | 구조 개선 |
| 1.2 | 2025-12-21 | 출처 분류 추가, 내부 정책/공식 권고 구분 명확화, 패러다임 주장을 프레임워크 운영 원칙으로 재정의 |
| 1.3 | 2025-12-21 | 가이드 기반 개선: 7대 핵심 기법 확장, 새 기법 섹션 추가 (Prefilling/Hybrid Prompting/Skeleton-of-Thought/Over-Engineering 방지/안전한 프롬프팅), 마이그레이션 체크리스트 추가, 벤치마크 참조 추가, 경로 제한 유연화 (allowlist/denylist), 시스템 프롬프트 템플릿 영어화, 언어 정책 섹션 추가 (8.3) |
| 1.4 | 2025-12-21 | **검증 기반 수정**: Hybrid Prompting → Chain of Draft(CoD)로 변경 (arXiv:2502.18600 정확한 해석 반영), Native Extended Thinking과 프레임워크 Thinking 태그 역할 분담 명확화 (§4.2), 토큰 효율성 목표(90%)와 구현 방법 정합성 확보 |
| 1.5 | 2025-12-21 | **외부 검증 반영**: Terminal-Bench 2.0 수치 검증 필요 표시 (Composio 보고와 불일치 확인), 전체 문서 검증 완료 (Extended Thinking/Prefilling/SWE-bench/논문 인용 모두 정확 확인) |
| 1.6 | 2025-12-21 | **개발 구조 변경**: 기존 `src/superclaude/`는 그대로 유지하고, `src/superclaude-v5/`에서 병렬 개발하는 방식으로 변경 |
| 1.7 | 2025-12-21 | **구현 완료 + 품질 개선**: 전체 구조 구현 완료, 실측 메트릭 업데이트 (85.6% 절감), 모든 명령어에 Boundaries/Success Criteria 추가, 모든 MCP에 Example 추가 |

---

## 14. v4 → v5 마이그레이션 체크리스트 (NEW)

> 📋 **출처**: [가이드 §마이그레이션 체크리스트]

기존 프롬프트를 Opus 4.5로 마이그레이션할 때:

| # | 작업 | 설명 | 예시 | 상태 |
|---|------|------|------|------|
| 1 | 공격적 언어 제거 | "CRITICAL", "MUST" → 자연스러운 표현 | `"반드시 확인해야 함"` → `"확인이 필요합니다"` | ⬜ |
| 2 | 구체화 | 모호한 요청 → 명확한 요구사항 + 성공 기준 | `"개선해줘"` → `"성능을 O(n)으로 최적화하세요"` | ⬜ |
| 3 | 예제 정렬 | 예제가 원하는 동작을 정확히 반영 | 3-5개 다양한 예제 포함 | ⬜ |
| 4 | 시스템 프롬프트 검토 | 도구 호출이 과도하거나 불충분한지 확인 | `<default_to_action>` 템플릿 적용 | ⬜ |
| 5 | Thinking 지시어 제거 | Extended Thinking이 기본 제공됨 | `"단계별로 생각해"` 제거 | ⬜ |
| 6 | 아웃풋 형식 명시 | "하지 말 것" 대신 "할 것" 중심으로 작성 | `"설명 없이"` → `"JSON만 출력"` | ⬜ |
| 7 | Prefilling 검토 | API 사용 시 프리필 활용 가능 여부 확인 | `{"role": "assistant", "content": "{"}` | ⬜ |
| 8 | Over-Engineering 방지 추가 | 범위 제한 명시 | `<over_engineering_prevention>` 템플릿 적용 | ⬜ |
| 9 | Chain of Draft 적용 | Verbose thinking → 5단어 이내 미니멀 추론 | `<draft>step1: auth → valid</draft>` | ⬜ |

**마이그레이션 검증:**
```markdown
✅ 마이그레이션 성공 기준:
- 기존 명령어가 동일하게 동작
- 응답 품질 유지 또는 향상
- 토큰 사용량 동등 또는 감소
- 새로운 기능(Extended Thinking 등) 활용 가능
```
