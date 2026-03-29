# Claude Code Skills 설계 가이드

> **Anthropic 내부 설계 원칙 기반 · 공식 소스 교차 검증 완료**
>
> 이 가이드는 Anthropic 엔지니어링 팀이 내부에서 수백 개의 Claude Code 스킬을 운영하며 발견한 설계 원칙을
> 공식 문서, 엔지니어링 블로그, GitHub 레포지토리, 실제 시스템 구조와 교차 검증하여 정리한 것입니다.

---

## 목차

1. [검증 결과 요약](#1-검증-결과-요약)
2. [핵심 원칙 6가지](#2-핵심-원칙-6가지)
3. [9가지 스킬 유형 카탈로그](#3-9가지-스킬-유형-카탈로그)
4. [폴더 구조 설계](#4-폴더-구조-설계)
5. [SKILL.md 작성법](#5-skillmd-작성법)
6. [Description — 트리거 최적화](#6-description--트리거-최적화)
7. [Gotchas 섹션 운영법](#7-gotchas-섹션-운영법)
8. [점진적 공개 패턴](#8-점진적-공개-패턴)
9. [안전 모드 — 스킬 내장 훅](#9-안전-모드--스킬-내장-훅)
10. [배포 전략](#10-배포-전략)
11. [출시 전 체크리스트](#11-출시-전-체크리스트)
12. [출처 및 참조](#12-출처-및-참조)

---

## 1. 검증 결과 요약

아래 표는 AgentOS 채널 영상(7분 15초)의 핵심 주장을 공식 소스와 교차 검증한 결과입니다.

| # | 주장 | 판정 | 근거 |
|---|------|------|------|
| 1 | 스킬은 파일이 아니라 폴더다 | ✅ 확인 | 공식 문서: "Each skill is a directory with SKILL.md as the entrypoint" + 실제 시스템 구조 일치 |
| 2 | 9가지 스킬 유형 카탈로그 | ✅ 확인 | Anthropic 엔지니어링 블로그에서 9개 카테고리 명시 |
| 3 | 뻔한 말 하지 마라 | ✅ 확인 | "focus on information that pushes Claude out of its normal way of thinking" |
| 4 | Gotchas 섹션 = 최고 가치 | ✅ 확인 | "The highest-signal content in any skill is the Gotchas section" |
| 5 | 점진적 공개 | ✅ 확인 | "Progressive disclosure is the core design principle" — 3단계 로딩 구조 |
| 6 | description은 트리거다 | ✅ 확인 | "This is the primary triggering mechanism" — skill-creator 공식 코드 |
| 7 | On Demand Hooks (/careful, /freeze) | ⚠️ 부분 확인 | 스킬 내장 훅 메커니즘은 공식 확인. /careful, /freeze는 빌트인이 아닌 **커스텀 구현 예시** |
| 8 | 스킬 배포 — 팀으로 확장 | ✅ 확인 | .claude/skills + Plugin Marketplace 두 가지 경로 공식 문서 확인 |

### 추가 발견 사항 (영상 미언급)

- `disable-model-invocation: true` — Claude의 자동 호출 방지, 위험한 작업에 필수
- `context: fork` — subagent 격리 실행, 메인 컨텍스트 보호
- `$ARGUMENTS`, `$0`, `$1` — 위치 인자 전달 패턴
- `ultrathink` 키워드 — SKILL.md 본문에 포함 시 extended thinking 활성화
- `allowed-tools` — 스킬 실행 중 사용 가능 도구 제한
- `${CLAUDE_PLUGIN_DATA}` — 스킬 업그레이드 시에도 유지되는 안정 저장 경로
- 스킬(확률적) vs 훅(결정론적) — 안전 규칙은 반드시 훅으로

---

## 2. 핵심 원칙 6가지

### 원칙 1: 스킬은 폴더다

> "A skill is a directory containing a SKILL.md file that contains organized folders of
> instructions, scripts, and resources."
> — Anthropic Engineering Blog, 2026.01.28

SKILL.md 하나로 만든 스킬은 메모에 불과합니다.
진정한 스킬은 Claude가 탐색하고 실행할 수 있는 **완전한 작업 환경**입니다.

```
my-skill/
├── SKILL.md              # 진입점 — 개요 + 파일 안내 (필수)
├── references/           # API 문서, 코드 스니펫 (필요시 로드)
│   ├── api.md
│   └── patterns.md
├── scripts/              # 검증/실행 스크립트 (Claude가 실행)
│   ├── validate.sh
│   └── helper.py
├── templates/            # 출력 템플릿 (Claude가 복사 후 작성)
│   └── report.md
└── examples/             # 예시 출력 (기대 형식 시연)
    └── sample.md
```

**폴더명은 관례(convention)이지 강제 규격이 아닙니다.**
`resources/`, `references/`, `assets/` 등 팀에 맞는 이름을 사용하되, SKILL.md에서 각 파일의 역할과
로드 시점을 명시하세요.


### 원칙 2: 모델이 이미 아는 것을 반복하지 마라

Claude는 Python, JavaScript, REST API 호출법을 이미 알고 있습니다.
스킬에 일반적인 프로그래밍 지식을 넣으면 컨텍스트만 낭비됩니다.

스킬에 담아야 할 것: **Claude가 추론만으로는 절대 도달할 수 없는 조직 고유의 규칙과 제약**

```
❌ 나쁜 예 — 모델이 이미 아는 것
"Python에서 requests 라이브러리로 API를 호출하려면 import requests를 하고..."

✅ 좋은 예 — 모델이 모르는 조직 고유 규칙
"우리 내부 API는 반드시 X-Internal-Auth 헤더를 포함해야 하며,
 /v2 엔드포인트는 deprecated이므로 /v3를 사용하라.
 rate limit은 분당 100회이며, 429 응답 시 exponential backoff 필수."
```

**실전 사례**: Anthropic의 frontend-design 스킬은 "Inter 폰트 쓰지 마라",
"보라색 그라데이션 쓰지 마라" 같은 Claude의 기본 성향을 깨는 규칙을 담아서
디자인 품질을 크게 향상시켰습니다.


### 원칙 3: Gotchas가 가장 높은 가치를 갖는다

> "The highest-signal content in any skill is the Gotchas section."

처음부터 완벽한 스킬을 만들려 하지 마세요.
**몇 줄로 시작해서, Claude가 실수할 때마다 한 줄씩 추가**하는 것이 최선입니다.

```markdown
## Gotchas

- ❌ `createUser()`를 호출하기 전에 반드시 `validateEmail()`을 먼저 호출하라.
  순서가 바뀌면 DB에 잘못된 레코드가 생성된다.
- ❌ 환경변수 `DB_HOST`는 production에서 읽기 전용 레플리카를 가리킨다.
  쓰기 작업은 반드시 `DB_WRITE_HOST`를 사용하라.
- ❌ date 필드에 ISO 8601 형식을 쓰되, 타임존은 항상 UTC로 통일하라.
  KST로 보내면 중복 레코드가 생긴다.
```


### 원칙 4: 점진적 공개로 컨텍스트를 아껴라

> "Progressive disclosure is the core design principle that makes Agent Skills flexible and scalable."

스킬 로딩은 3단계로 작동합니다:

```
Level 1: name + description만 시스템 프롬프트에 로드 (~50-100 tokens/스킬)
         → Claude가 "이 스킬이 지금 필요한가?" 판단

Level 2: SKILL.md 본문 전체 로드 (<5,000 tokens)
         → 핵심 지시사항, Gotchas, 파일 안내

Level 3: 추가 파일 필요시 로드 (references/, scripts/ 등)
         → 상세 API 문서, 코드 스니펫, 템플릿
```

**SKILL.md에 모든 것을 넣으면 단순한 작업에도 불필요한 토큰을 소비합니다.**
메인 파일에는 개요와 파일 목록만 넣고, 상세 내용은 별도 파일로 분리하세요.


### 원칙 5: Description은 사람을 위한 요약이 아니라 모델을 위한 트리거다

```yaml
# ❌ 사람을 위한 요약 — 트리거 실패 확률 높음
description: 배포 관련 스킬

# ✅ 모델을 위한 트리거 조건 — 명확한 활성화
description: >
  프로덕션에 코드를 배포하거나, PR 머지 후 배포 상태를 확인하거나,
  롤백이 필요할 때 사용한다. 사용자가 "deploy", "배포", "release",
  "롤백", "rollback"을 언급하면 이 스킬을 사용하라.
```

Claude는 스킬을 사용해야 할 때도 안 쓰는 "undertrigger" 경향이 있습니다.
Anthropic은 description을 의도적으로 "pushy"하게 작성하라고 권장합니다.


### 원칙 6: 스킬은 확률적, 훅은 결정론적

CLAUDE.md에 "rm -rf 실행하지 마라"고 써도 **약 70%만 따릅니다.**
안전 규칙은 반드시 **훅(hook)**으로 구현해야 100% 보장됩니다.

```
스킬(Skill) = 제안 — Claude가 판단하여 따를 수도, 안 따를 수도 있음
훅(Hook)   = 강제 — exit code 2로 물리적 차단, 협상 불가
```

의사결정 기준:
- 코딩 컨벤션, 스타일 가이드 → **스킬** (유연한 적용)
- rm -rf 차단, 시크릿 노출 방지, force-push 금지 → **훅** (100% 차단)

---

## 3. 9가지 스킬 유형 카탈로그

Anthropic이 내부 스킬 수백 개를 분류한 결과, 9가지 유형으로 정리됩니다.
**좋은 스킬은 딱 하나의 유형에 깔끔하게 들어맞고, 나쁜 스킬은 여러 유형에 걸칩니다.**

### 유형 1: 라이브러리/API 레퍼런스
라이브러리, CLI, SDK의 올바른 사용법을 설명합니다.
내부 라이브러리와 Claude가 잘 못 쓰는 외부 라이브러리 모두 해당합니다.

**필수 구성**: 코드 스니펫 폴더 + Gotchas 목록

| 예시 스킬 | 설명 |
|-----------|------|
| internal-billing-lib | 에지 케이스, 흔한 오용 패턴, 주의사항 |
| internal-platform-cli | 각 서브커맨드 설명 + 사용 시점 |
| frontend-design | 팀 디자인 시스템 준수 지침 |


### 유형 2: 제품 검증
코드가 정상 작동하는지 테스트/검증하는 방법을 기술합니다.
Playwright, Tmux 등 외부 도구와 결합하여 실제 검증을 수행합니다.

> Anthropic은 검증 스킬을 완성하는 데 **1주일을 투자할 가치가 있다**고 제안합니다.

| 예시 스킬 | 설명 |
|-----------|------|
| signup-flow-driver | 가입→이메일인증→온보딩을 headless browser로 실행 |
| checkout-verifier | Stripe 테스트 카드로 결제 UI 검증 |
| tmux-cli-driver | TTY가 필요한 대화형 CLI 테스트 |


### 유형 3: 데이터 조회/분석
팀의 데이터 및 모니터링 인프라에 연결합니다.
데이터 fetching 라이브러리, 대시보드 ID, 일반적 워크플로우 지침 포함.

| 예시 스킬 | 설명 |
|-----------|------|
| funnel-query | 가입→활성화→결제 전환경로 조회 |
| cohort-comparison | 두 코호트 간 retention/전환율 비교 |
| grafana-integration | 데이터소스 UID, 클러스터명, 문제→대시보드 매핑 |


### 유형 4: 비즈니스 자동화
반복적인 업무를 단일 명령으로 단순화합니다.
실행 이력을 로그 파일에 저장하면 모델의 일관성이 향상됩니다.

| 예시 스킬 | 설명 |
|-----------|------|
| standup-report | 티켓+GitHub+Slack 집계 → 스탠드업 포맷 |
| create-ticket | 스키마 강제(유효 enum, 필수 필드) + 생성 후 워크플로우 |
| weekly-recap | 머지된 PR + 닫힌 티켓 + 배포 → 주간 요약 |


### 유형 5: 코드 스캐폴딩
코드베이스의 특정 기능을 위한 보일러플레이트를 생성합니다.
코드만으로 표현할 수 없는 자연어 요구사항이 있을 때 특히 유용합니다.

| 예시 스킬 | 설명 |
|-----------|------|
| new-workflow | 팀 어노테이션 기반 서비스/워크플로우 생성 |
| migration-template | 마이그레이션 파일 템플릿 + 흔한 실수 |
| new-app | 인증/로깅/배포 사전 설정된 내부 앱 생성 |


### 유형 6: 코드 리뷰/품질
조직의 코드 품질 기준을 강제합니다.
결정론적 스크립트를 포함하면 견고성이 높아지며, 훅이나 GitHub Actions와 연동 가능합니다.

| 예시 스킬 | 설명 |
|-----------|------|
| adversarial-review | fresh-eyes subagent가 비평 → 수정 → 반복 |
| code-style | Claude 기본 성향과 다른 코드 스타일 강제 |
| testing-practices | 테스트 작성법 및 테스트 대상 가이드 |


### 유형 7: CI/CD
코드의 fetch, push, 배포를 지원합니다.

| 예시 스킬 | 설명 |
|-----------|------|
| pr-monitor | PR→flaky CI 재시도→머지 충돌 해결→auto-merge |
| service-deploy | 빌드→smoke test→점진적 트래픽→auto-rollback |
| production-cherry-pick | 격리 worktree→cherry-pick→PR 생성 |


### 유형 8: 런북 (장애 대응)
증상(Slack 스레드, 알림, 에러 시그니처)을 입력받아 다중 도구 조사를 수행하고
구조화된 보고서를 생성합니다.

| 예시 스킬 | 설명 |
|-----------|------|
| service-debug | 증상→도구→쿼리 패턴 매핑 |
| oncall-runner | 알림 수집→일반 원인 확인→결과 포매팅 |
| log-correlator | request ID 기반 전체 시스템 로그 추적 |


### 유형 9: 인프라 운영
루틴 유지보수 및 운영 절차를 수행합니다.
파괴적 작업이 포함될 수 있으므로 가드레일이 중요합니다.

| 예시 스킬 | 설명 |
|-----------|------|
| orphan-cleanup | 고아 pod/volume 발견→Slack 알림→대기→확인→정리 |
| dependency-mgmt | 의존성 승인 워크플로우 |
| cost-investigation | 스토리지/egress 비용 급등 원인 조사 |

---

## 4. 폴더 구조 설계

### 최소 구조 (시작용)

```
my-skill/
├── SKILL.md           # 필수. 지시사항 + gotchas
└── references/
    └── api.md         # 상세 API 문서 (필요시 로드)
```

### 표준 구조 (대부분의 스킬)

```
my-skill/
├── SKILL.md           # 개요 + 파일 안내 + 핵심 gotchas
├── references/
│   ├── api.md         # API 함수 시그니처, 파라미터
│   └── patterns.md    # 코드 패턴, 안티패턴
├── scripts/
│   └── validate.sh    # 출력 검증 스크립트
└── templates/
    └── output.md      # 출력 형식 템플릿
```

### 고급 구조 (복합 스킬)

```
my-skill/
├── SKILL.md
├── agents/            # subagent 정의
│   └── reviewer.md
├── references/
│   ├── api.md
│   ├── schemas.md
│   └── examples.md
├── scripts/
│   ├── validate.py
│   ├── helper.py
│   └── utils.py
├── templates/
│   └── report.md
├── assets/
│   └── eval_review.html
└── eval-viewer/       # 평가 도구
    └── viewer.html
```

### 명명 규칙

- 폴더명: `kebab-case` (예: `sprint-planner`, `code-review`)
- 진입점: 반드시 `SKILL.md` (대소문자 구분, 변형 불가)
- 관례적 하위 폴더: `references/`, `scripts/`, `templates/`, `examples/`, `assets/`, `agents/`

---

## 5. SKILL.md 작성법

### Frontmatter (YAML)

```yaml
---
name: my-skill                    # /slash-command 이름이 됨
description: >                    # 트리거 조건 (아래 섹션 6 참조)
  이 스킬이 언제 사용되어야 하는지를
  구체적 키워드와 함께 기술
disable-model-invocation: true    # (선택) 사용자만 호출 가능
context: fork                     # (선택) subagent 격리 실행
allowed-tools: Read, Grep, Glob   # (선택) 사용 가능 도구 제한
agent: Explore                    # (선택) context: fork일 때 실행 환경
hooks:                            # (선택) 스킬 내장 훅
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/safety-check.sh"
---
```

### Frontmatter 필드 결정 기준

| 필드 | 언제 사용하는가 |
|------|---------------|
| `disable-model-invocation: true` | 배포, 삭제, DB 마이그레이션 등 부작용이 있는 작업 |
| `context: fork` | 리서치, 코드 리뷰 등 메인 컨텍스트와 격리해야 할 때 |
| `allowed-tools` | 읽기 전용 작업, 안전한 도구만 허용할 때 |
| `hooks` | 스킬 활성 시에만 특정 안전 규칙을 적용할 때 |


### 본문 구조 권장

```markdown
# [스킬명]

## 개요
이 스킬이 무엇을 하는지 1-2문장으로.

## 사용 가능한 파일
- `references/api.md` — API 함수 시그니처. 함수 호출 전 참조하라.
- `scripts/validate.sh` — 출력 검증. 작업 완료 후 실행하라.
- `templates/output.md` — 출력 템플릿. 이 형식에 맞춰 작성하라.

## 핵심 규칙
1. [조직 고유의 중요 규칙 1]
2. [조직 고유의 중요 규칙 2]
3. [조직 고유의 중요 규칙 3]

## Gotchas
- ❌ [Claude가 반복 실패하는 지점 1]
- ❌ [Claude가 반복 실패하는 지점 2]

## 워크플로우
1. [단계 1]
2. [단계 2]
3. [단계 3]
```

### $ARGUMENTS 사용

```yaml
---
name: fix-issue
description: GitHub 이슈를 수정한다
disable-model-invocation: true
---
GitHub 이슈 $ARGUMENTS를 코딩 표준에 맞게 수정하라.
```

호출: `/fix-issue 42` → `$ARGUMENTS`가 `42`로 치환

위치 인자도 지원: `$ARGUMENTS[0]` 또는 단축형 `$0`, `$1`, `$2`

### Extended Thinking 활성화

SKILL.md 본문 어디에든 `ultrathink` 키워드를 포함하면 extended thinking 모드가 활성화됩니다.

```markdown
## 분석 모드
이 스킬은 복잡한 분석이 필요하므로 ultrathink 모드를 사용합니다.
```

---

## 6. Description — 트리거 최적화

### Description은 Claude의 의사결정 입력이다

세션 시작 시 Claude는 모든 설치된 스킬의 name + description을 스캔합니다.
이 정보만으로 "이 요청에 맞는 스킬이 있는가?"를 판단합니다.

### 작성 공식

```
[이 스킬이 하는 일] + [어떤 상황에서 사용해야 하는지] + [트리거 키워드]
```

### 예시 비교

```yaml
# ❌ 나쁨 — 트리거 신호 없음
description: 프로젝트 관리를 돕는 스킬

# ⚠️ 보통 — 무엇은 있지만 언제가 없음
description: Linear에서 스프린트를 계획하고 태스크를 생성한다

# ✅ 좋음 — 무엇 + 언제 + 키워드
description: >
  Linear 프로젝트 워크플로우를 관리한다. 스프린트 계획, 태스크 생성,
  상태 추적을 포함한다. 사용자가 "sprint", "Linear tasks", "프로젝트 계획",
  "스프린트", "태스크 생성"을 언급하면 이 스킬을 사용하라.
  명시적으로 요청하지 않아도 태스크 관리 맥락이면 사용을 고려하라.
```

### Undertrigger 대응

Claude는 스킬을 사용해야 할 때도 안 쓰는 경향이 있습니다.
Anthropic의 공식 권장: description을 약간 "pushy"하게 작성하세요.

```yaml
# 실전 예시 — 의도적으로 pushy
description: >
  내부 Anthropic 데이터를 표시하는 대시보드를 빌드하는 방법.
  사용자가 대시보드, 데이터 시각화, 내부 메트릭을 언급하거나
  어떤 종류의 회사 데이터를 표시하고 싶어할 때 반드시 이 스킬을 사용하라.
  사용자가 명시적으로 '대시보드'를 요청하지 않더라도 사용을 고려하라.
```

### Description 최적화 자동화

Anthropic의 skill-creator 스킬은 description 최적화 루프를 제공합니다:
- eval 쿼리 세트를 60% 학습 / 40% 테스트로 분할
- 현재 description의 트리거 성공률 측정 (쿼리당 3회 실행)
- Claude가 실패 패턴 분석 후 개선안 제안
- 최대 5회 반복 후 HTML 리포트 생성

---

## 7. Gotchas 섹션 운영법

### 시작 방법

1. **빈 Gotchas 섹션으로 시작**: `## Gotchas` 헤더만 만들어 놓기
2. **Claude가 실수할 때마다 한 줄 추가**: 실패 → 원인 분석 → Gotcha 기록
3. **주기적 리뷰**: 해결된 Gotcha 제거, 새로운 패턴 추가

### 좋은 Gotcha의 조건

```markdown
## Gotchas

# ✅ 좋은 Gotcha — 구체적 + 행동 지시 + 왜(why)
- ❌ `api.get_user(id)` 호출 시 id는 string이어야 한다. int를 넘기면
  500 에러가 발생하지만, 에러 메시지에 타입 정보가 없어 디버깅이 어렵다.
  반드시 `str(id)`로 변환 후 전달하라.

# ❌ 나쁜 Gotcha — 모호 + 행동 지시 없음
- id 타입에 주의하라
```

### Gotcha 카테고리화 (스킬이 커졌을 때)

```markdown
## Gotchas

### API 관련
- ...

### 데이터 형식
- ...

### 환경별 차이
- ...
```

---

## 8. 점진적 공개 패턴

### 패턴 1: 참조 파일 분리

SKILL.md에서 상세 문서를 별도 파일로 안내합니다.

```markdown
# API Client 스킬

## 사용 가능한 파일
- `references/endpoints.md` — 전체 엔드포인트 목록과 파라미터.
  API 호출 전에 이 파일을 먼저 읽어라.
- `references/error-codes.md` — 에러 코드별 대응 방법.
  에러 처리 로직을 작성할 때 참조하라.

## 핵심 규칙
모든 요청에 X-Api-Version: 2024-01 헤더를 포함하라.
```

Claude는 API 호출이 필요할 때만 `endpoints.md`를 읽고,
에러 처리가 필요할 때만 `error-codes.md`를 읽습니다.


### 패턴 2: 스크립트를 문서이자 도구로

```markdown
## 사용 가능한 스크립트
- `scripts/fetch_data.py` — 이벤트 소스에서 데이터를 가져오는 헬퍼 함수 라이브러리.
  이 함수들을 import하여 분석 스크립트를 생성하라. 직접 수정하지 마라.
```

Claude는 이 스크립트를 읽어서 함수 시그니처를 파악한 뒤,
새로운 분석 스크립트를 생성할 때 이 함수들을 조합합니다.


### 패턴 3: 템플릿 기반 출력

```markdown
## 출력 형식
`templates/report.md`를 복사한 뒤, 각 섹션을 채워서 결과를 생성하라.
```

### 패턴 4: 상호 배타적 경로 분리

```markdown
## 사용 가능한 파일
- `references/rest-api.md` — REST API를 사용할 때 참조
- `references/graphql.md` — GraphQL을 사용할 때 참조

두 파일을 동시에 읽을 필요는 없다. 사용자의 요청에 맞는 것만 읽어라.
```

이렇게 하면 REST 작업 시 GraphQL 문서의 토큰을 소비하지 않습니다.

---

## 9. 안전 모드 — 스킬 내장 훅

스킬의 YAML frontmatter에 hooks를 정의하면, **해당 스킬이 활성화된 동안에만** 훅이 작동합니다.
세션이 끝나면 자동으로 비활성화됩니다.

### /careful — 프로덕션 안전 모드

```yaml
---
name: careful
description: >
  프로덕션 환경에서 작업할 때 안전 모드를 활성화한다.
  위험한 명령어를 자동으로 차단한다.
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|DROP TABLE|git push --force|kubectl delete' && echo 'BLOCKED: Destructive command detected' >&2 && exit 2 || exit 0"
---

# 🛡️ 프로덕션 안전 모드 활성화

다음 명령어가 자동으로 차단됩니다:
- `rm -rf` — 재귀적 삭제
- `DROP TABLE` — 테이블 삭제
- `git push --force` — 강제 푸시
- `kubectl delete` — 쿠버네티스 리소스 삭제

안전 모드를 해제하려면 세션을 종료하세요.
```


### /freeze — 디버깅 잠금 모드

```yaml
---
name: freeze
description: >
  특정 디렉토리 외의 파일 수정을 차단한다.
  디버깅 중 의도치 않은 코드 수정을 방지한다.
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: |
            ALLOWED_DIR="src/debug"
            FILE_PATH=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
            if [[ "$FILE_PATH" != *"$ALLOWED_DIR"* ]]; then
              echo "BLOCKED: File outside $ALLOWED_DIR" >&2
              exit 2
            fi
            exit 0
---

# 🧊 디버깅 잠금 모드

`src/debug` 디렉토리 외의 모든 파일 수정이 차단됩니다.
로그 추가 등 디버깅 작업만 해당 폴더에서 수행하세요.
```

### 커스텀 안전 모드의 핵심

- `exit 2` = 차단 (물리적으로 실행 불가)
- `exit 0` = 허용
- `exit 1` = 경고만 (실행은 됨)
- `disable-model-invocation: true` = 사용자가 명시적으로 `/careful`을 입력해야만 활성화

---

## 10. 배포 전략

### 소규모 팀 (2-10명)

```
프로젝트-루트/
└── .claude/
    └── skills/
        ├── deploy/
        │   └── SKILL.md
        └── code-review/
            └── SKILL.md
```

`.claude/skills/`를 Git에 커밋하면 팀 전원이 동일한 스킬을 사용합니다.

**주의**: 커밋된 모든 스킬은 세션 시작 시 description이 컨텍스트에 추가됩니다.
스킬이 많아지면 컨텍스트 비용이 누적됩니다.


### 중규모 팀 (10-50명)

**Plugin Marketplace 방식**을 도입합니다.

1. **샌드박스 단계**: 개인이 스킬을 만들어 GitHub에 올림
2. **홍보 단계**: Slack 등에서 "이 스킬 써보세요" 공유
3. **마켓플레이스 등록**: 충분한 사용 실적이 쌓이면 PR로 공식 등록

```bash
# Plugin marketplace 등록 (Claude Code)
/plugin marketplace add my-org/my-skills-repo

# 필요한 스킬만 설치
/plugin install deploy-skill@my-org-skills
```


### 대규모 조직 (50명+)

- **Managed Settings**로 조직 전체에 필수 스킬 배포
- 마켓플레이스에서 선택적 설치
- PreToolUse 훅으로 스킬 사용 현황 로깅
- 중복/저품질 스킬 큐레이션 프로세스 운영


### 스킬 의존성

스킬 간 의존성 관리는 아직 네이티브로 지원되지 않습니다.
SKILL.md에서 다른 스킬을 이름으로 참조하면 Claude가 설치된 경우 호출합니다.

```markdown
## 의존성
이 스킬은 `file-upload` 스킬이 설치되어 있어야 합니다.
CSV를 생성한 후 `file-upload` 스킬을 호출하여 업로드하세요.
```

---

## 11. 출시 전 체크리스트

### 구조 점검

- [ ] `SKILL.md` 파일이 루트에 존재하는가?
- [ ] 폴더명이 kebab-case인가?
- [ ] SKILL.md에 YAML frontmatter가 있는가?
- [ ] 모든 하위 파일이 SKILL.md에서 안내되어 있는가?

### Description 점검

- [ ] "무엇을 하는가" + "언제 사용하는가"가 모두 포함되어 있는가?
- [ ] 구체적인 트리거 키워드가 포함되어 있는가?
- [ ] 충분히 "pushy"한가? (undertrigger 방지)

### 내용 점검

- [ ] Claude가 이미 아는 일반 지식을 반복하고 있지 않은가?
- [ ] 조직 고유의 규칙, 제약, 컨벤션에 집중하고 있는가?
- [ ] Gotchas 섹션이 있는가? (비어 있어도 괜찮음 — 점진적 추가)
- [ ] 점진적 공개를 활용하고 있는가? (모든 것을 SKILL.md에 넣지 않았는가?)

### 안전 점검

- [ ] 부작용이 있는 작업에 `disable-model-invocation: true`가 설정되어 있는가?
- [ ] 파괴적 명령어에 대한 훅이 필요한가? (스킬 아닌 훅으로)
- [ ] API 키, 토큰, 크레덴셜이 SKILL.md에 하드코딩되어 있지 않은가?
- [ ] 스크립트에 보안 취약점이 없는가?

### 품질 점검

- [ ] 단일 스킬 유형에 깔끔하게 들어맞는가?
- [ ] 3가지 다른 시나리오에서 테스트했는가?
- [ ] Claude에게 지나치게 구체적인 지시를 하고 있지 않은가? (유연성 보존)

---

## 12. 출처 및 참조

### 공식 소스

| 소스 | URL |
|------|-----|
| Claude Code 공식 문서 — Skills | https://code.claude.com/docs/en/skills |
| Anthropic Engineering Blog — Agent Skills | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| Anthropic 32페이지 가이드 PDF | https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf |
| Claude Code 공식 문서 — Hooks | https://code.claude.com/docs/en/hooks-guide |
| Anthropic 공식 Skills 레포 | https://github.com/anthropics/skills |
| skill-creator SKILL.md | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md |
| Claude API — Agent Skills | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |

### Anthropic 엔지니어링 팀 블로그

| 소스 | 설명 |
|------|------|
| Lessons from Building Claude Code: How We Use Skills | 9가지 유형 카탈로그, Gotchas, 점진적 공개, description 트리거, On Demand Hooks, 배포 전략 |

### 커뮤니티 분석

| 소스 | URL |
|------|-----|
| 스킬 내부 구조 리버스 엔지니어링 | https://mikhail.io/2025/10/claude-code-skills/ |
| 32페이지 가이드 분석 | https://medium.com/@AdithyaGiridharan/anthropic-just-released-a-32-page-playbook |
| 스킬+훅 실전 가이드 | https://genaiunplugged.substack.com/p/claude-code-skills-commands-hooks-agents |

---

> **이 가이드는 2026년 3월 기준입니다.**
> Claude Code Skills는 빠르게 발전하는 기능이므로, 공식 문서를 정기적으로 확인하세요.
> 가이드 내 모든 주장은 위 출처에서 교차 검증되었으며, 부분 확인 사항은 ⚠️로 표시했습니다.
