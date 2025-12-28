# Claude Code 완전 커스터마이제이션 가이드
## Opus 4.5 기준 (2025년 12월)

---

## 📋 목차

1. [개요 및 아키텍처](#1-개요-및-아키텍처)
2. [XML + Markdown 하이브리드 패턴](#2-xml--markdown-하이브리드-패턴)
3. [CLAUDE.md (Memory)](#3-claudemd-memory)
4. [Rules Directory](#4-rules-directory)
5. [Slash Commands](#5-slash-commands)
6. [Subagents (Agents)](#6-subagents-agents)
7. [Skills](#7-skills)
8. [Hooks](#8-hooks)
9. [Settings.json](#9-settingsjson)
10. [MCP Servers](#10-mcp-servers)
11. [Plugins](#11-plugins)
12. [환경 변수](#12-환경-변수)
13. [모범 사례 및 제한사항](#13-모범-사례-및-제한사항)

---

## 1. 개요 및 아키텍처

### 커스터마이제이션 요소 비교

| 요소 | 호출 방식 | 범위 | 주요 용도 |
|------|----------|------|----------|
| **CLAUDE.md** | 자동 로드 | 전역/프로젝트 | 컨텍스트, 규칙, 지침 |
| **Rules** | 자동 로드 | 프로젝트 | 모듈화된 규칙, 경로별 타겟팅 |
| **Slash Commands** | 사용자 호출 (`/명령`) | 전역/프로젝트 | 재사용 프롬프트, 워크플로우 |
| **Subagents** | 모델 자동 위임 | 전역/프로젝트 | 병렬 작업, 전문 분야 |
| **Skills** | 모델 자동 발견 | 전역/프로젝트 | 복잡한 기능, 스크립트 포함 |
| **Hooks** | 이벤트 자동 실행 | 전역/프로젝트 | 자동화, 검증, 포매팅 |
| **Settings** | 설정 파일 | 엔터프라이즈/전역/프로젝트 | 권한, 환경 변수, 도구 설정 |
| **MCP** | 도구 확장 | 전역/프로젝트 | 외부 서비스 연결 |
| **Plugins** | 마켓플레이스 | 전역/프로젝트 | 패키지화된 확장 기능 |

### 설정 파일 위치 계층

```
우선순위 (높음 → 낮음):
1. 엔터프라이즈 관리 정책 (/Library/Application Support/ClaudeCode/managed-settings.json)
2. CLI 인수 (--append-system-prompt 등)
3. 로컬 프로젝트 설정 (.claude/settings.local.json)
4. 공유 프로젝트 설정 (.claude/settings.json)
5. 사용자 전역 설정 (~/.claude/settings.json)
```

---

## 2. XML + Markdown 하이브리드 패턴

### 핵심 원칙

| 요소 | 역할 | 예시 |
|------|------|------|
| **XML** | 구조적 경계 (Where) | `<context>`, `<instructions>` |
| **Markdown** | 내용 표현 (What, How) | `## 헤더`, `**볼드**`, `1. 리스트` |

### 연구 근거

#### Anthropic 공식 권장
> "Claude has been specifically tuned to pay special attention to your structure"  
> — Anthropic Documentation

- Claude는 XML 태그가 포함된 훈련 데이터로 학습됨
- Anthropic 내부 프롬프트에서도 XML 태그를 광범위하게 사용

#### 업계 표준 수렴
> "XML tags are the best way to structure prompts and separate sections for an LLM. It is the only format that all models from Anthropic, Google and OpenAI encourage."  
> — Anand S.

| 모델 | XML 지원 | 권장사항 |
|------|----------|---------|
| **Claude** | ✅ 최적화됨 | 공식 권장 |
| **GPT-4/o1/o3** | ✅ 지원 | "Use delimiters such as XML tags" |
| **Gemini** | ✅ 지원 | 구조화된 입력 권장 |
| **Llama 3.1** | ✅ 지원 | 복잡한 프롬프트에서 우수 |

#### 토큰화 안정성
> "Tokenization causes all sorts of problems when you rely on whitespace, indentation, or single-line Markdown comments. XML tags provide multi-line certainty with delimiters that mark where items begin and end."  
> — Daniel Voyce

- XML: 시작/끝이 명확 → 모델이 "완료된 컨텍스트" 인식
- Markdown만 사용: 들여쓰기, 공백 의존 → 토큰화 시 모호성 발생

---

### ⚠️ Claude Code 컨텍스트 적재 방식

Claude Code는 **파일 단위로 분리된 agents, commands, skills**를 컨텍스트에 적재할 때 다음과 같이 동작합니다:

```
파일 시스템                           컨텍스트 윈도우
─────────────────────────────────────────────────────────────
.claude/agents/code-reviewer.md    ┐
.claude/agents/security-auditor.md │→  Frontmatter 제거 후
.claude/commands/review.md         │   본문만 플랫하게 연결
.claude/commands/deploy.md         ┘
```

**문제점**: 여러 파일의 본문이 경계 없이 연결되면 **Attention Interference** 발생

> "When you insert several chunks of information with similar structure and vocabulary, the model's attention mechanisms struggle to distinguish between similar pieces of information, leading to confusion, conflation, or simply ignoring important details."

---

### 파일 분리 + XML 래퍼 패턴 (권장)

| 레이어 | 역할 | 담당 |
|--------|------|------|
| **파일 분리** | 물리적 관리, 버전 관리, 팀 협업 | 파일 시스템 |
| **Frontmatter** | 메타데이터 (Claude Code 파싱용) | YAML |
| **XML 래퍼** | 컨텍스트 내 명확한 경계 구분 | 본문 최상위 |

#### ❌ XML 래퍼 없이 (혼란 가능)

```markdown
<!-- code-reviewer.md 본문 -->
당신은 시니어 코드 리뷰어입니다.
## 체크리스트
1. 보안 검사
2. 성능 검사

<!-- security-auditor.md 본문 -->
당신은 보안 전문가입니다.
## 체크리스트
1. 취약점 분석
2. 인증 검사
```

컨텍스트에서 **어디서 code-reviewer가 끝나고 security-auditor가 시작되는지 불분명**

#### ✅ XML 래퍼 사용 (권장)

```markdown
<!-- code-reviewer.md -->
<agent name="code-reviewer">
당신은 시니어 코드 리뷰어입니다.

<checklist>
1. 보안 검사
2. 성능 검사
</checklist>
</agent>

<!-- security-auditor.md -->
<agent name="security-auditor">
당신은 보안 전문가입니다.

<checklist>
1. 취약점 분석
2. 인증 검사
</checklist>
</agent>
```

컨텍스트에서 **명확한 경계**:
```
<agent name="code-reviewer">
...
</agent>

<agent name="security-auditor">
...
</agent>
```

---

### 권장 래퍼 태그

| 파일 유형 | 래퍼 태그 | 예시 |
|----------|----------|------|
| **Agents** | `<agent name="...">` | `<agent name="code-reviewer">` |
| **Commands** | `<command name="...">` | `<command name="review">` |
| **Skills** | `<skill name="...">` | `<skill name="api-generator">` |

### 내부 구조용 태그

| 태그 | 용도 | 내부 Markdown |
|------|------|--------------|
| `<role>` | 역할 정의 | 단순 텍스트 |
| `<context>` | 배경 정보, 입력 데이터 | 헤더, 코드 블록 |
| `<instructions>` | 수행할 지시사항 | 리스트, 볼드 |
| `<constraints>` | 제약 조건, 금지 사항 | 리스트 |
| `<checklist>` | 검토 항목 | 번호 리스트, 볼드 |
| `<output_format>` | 출력 형식 지정 | 예시, 코드 블록 |
| `<examples>` | 예시 | 코드 블록 |
| `<task>` | 작업 목표 | 단순 텍스트 |

### 적용 가이드라인

```
구조 레벨:

레벨 1: 파일 래퍼 (필수)
  <agent name="..."> 또는 <command name="..."> 또는 <skill name="...">

레벨 2: 내부 섹션 (권장)
  <role>, <checklist>, <instructions>, <output_format>

레벨 3: Markdown (자유롭게)
  ## 헤더, **볼드**, 1. 리스트
```

---

## 3. CLAUDE.md (Memory)

### 개요
CLAUDE.md는 세션 시작 시 자동으로 컨텍스트에 로드되는 특수 파일입니다. 프로젝트 규칙, 코딩 스타일, 명령어 등을 정의합니다.

### 파일 위치 (우선순위 순)

| 위치 | 범위 | 용도 |
|-----|------|-----|
| `/Library/Application Support/ClaudeCode/CLAUDE.md` | 시스템 전체 (macOS) | IT/DevOps 관리 정책 |
| `/etc/claude-code/CLAUDE.md` | 시스템 전체 (Linux) | 조직 정책 |
| `~/.claude/CLAUDE.md` | 사용자 전역 | 개인 전역 설정 |
| `<project>/.claude/CLAUDE.md` | 프로젝트 | 팀 공유 설정 |
| `<project>/CLAUDE.md` | 프로젝트 루트 | 팀 공유 (대안) |
| `<subdirectory>/CLAUDE.md` | 하위 디렉토리 | 모듈별 설정 |

### 작성 규칙

#### ✅ 권장사항
- 간결하고 구체적으로 작성
- 섹션별로 명확하게 구분
- 실행 가능한 명령어 포함
- 코드 스타일 가이드 명시

#### ❌ 금지사항
- 과도하게 긴 문서 (토큰 낭비)
- 모호한 지시사항
- 중복된 정보

### 예시

#### `~/.claude/CLAUDE.md`

```markdown
<environment>
## 시스템
- OS: macOS / Linux
- 쉘: zsh
- Node.js: 20.x
- Python: 3.12
</environment>

<preferences>
## 코드 스타일
- 함수형 프로그래밍 선호
- 명시적 타입 선언
- 주석은 한국어로

## 커밋 규칙
- Conventional Commits 형식
- 커밋 메시지는 영어로
</preferences>
```

#### `<project>/CLAUDE.md`

```markdown
<project>
# E-Commerce API

## 스택
- Node.js 20.x + TypeScript 5.x
- PostgreSQL + Prisma ORM
- Jest + Supertest (테스트)
</project>

<commands>
## 필수 명령어
- `pnpm dev`: 개발 서버 시작
- `pnpm build`: 프로덕션 빌드
- `pnpm test`: 테스트 실행
- `pnpm lint`: ESLint 검사
- `pnpm typecheck`: 타입 검사
</commands>

<code_style>
## 규칙
- ES Modules (import/export) 사용, CommonJS 금지
- 구조 분해 할당 선호: `import { foo } from 'bar'`
- 함수는 JSDoc 주석 필수
- 컴포넌트 200줄 이하 유지
</code_style>

<git_rules>
## Git 워크플로우
- 브랜치: feature/, bugfix/, hotfix/ 접두사
- PR 전 `pnpm lint && pnpm test` 필수
</git_rules>

<security>
## 보안 규칙
- .env 파일 절대 읽지 말 것
- API 키 하드코딩 금지
- Prisma 쿼리 빌더만 사용 (SQL 인젝션 방지)
</security>
```

### 파일 참조 문법 (@import)

CLAUDE.md 파일은 `@path/to/file` 문법으로 다른 파일을 참조할 수 있습니다. 참조된 파일은 자동으로 컨텍스트에 로드됩니다.

#### 기본 문법

```markdown
# 프로젝트 내 파일 참조
@docs/api-guidelines.md
@src/config/database.ts

# 홈 디렉토리 파일 참조
@~/.claude/personal-preferences.md

# 절대 경로
@/path/to/shared/standards.md
```

#### 모듈화 예시

```markdown
# Main CLAUDE.md
# 프로젝트 개요
이 프로젝트는 E-Commerce API입니다.

# 상세 문서 참조
@docs/architecture.md
@docs/coding-standards.md
@docs/security-guidelines.md

# 개인 설정 (팀원별 다름)
@~/.claude/my-preferences.md
```

#### 규칙 및 제한사항

| 규칙 | 설명 |
|------|------|
| **재귀 깊이** | 최대 5단계까지 재귀적 import 허용 |
| **코드 블록 무시** | 코드 블록 내 `@`는 평가되지 않음 |
| **상대/절대 경로** | 둘 다 지원 |
| **MCP 리소스** | `@server:protocol://resource` 형식 지원 |

#### 동적 컨텍스트 프라이밍

`@`로 파일을 참조하면 해당 파일의 디렉토리와 상위 디렉토리의 CLAUDE.md도 자동으로 로드됩니다:

```
@src/api/routes/users.ts 참조 시:
├── src/api/routes/CLAUDE.md (있으면 로드)
├── src/api/CLAUDE.md (있으면 로드)
└── src/CLAUDE.md (있으면 로드)
```

### 동적 업데이트

```bash
# 대화 중 메모리 추가
/memory add "새로운 규칙 또는 컨텍스트"

# 메모리 조회
/memory

# 메모리 삭제
/memory remove "삭제할 내용"
```

---

## 4. Rules Directory

### 개요
`.claude/rules/` 디렉토리는 CLAUDE.md의 모듈화된 대안입니다. 하나의 거대한 CLAUDE.md 파일 대신, 여러 마크다운 파일로 지침을 분리하여 관리할 수 있습니다.

> **핵심**: Rules 파일은 CLAUDE.md와 **동일한 높은 우선순위**로 로드됩니다.

### CLAUDE.md vs Rules Directory

| 특성 | CLAUDE.md | Rules Directory |
|-----|-----------|-----------------|
| 구조 | 단일 파일 | 다중 파일 |
| 경로 타겟팅 | ❌ | ✅ (frontmatter) |
| 관심사 분리 | 제한적 | 우수 |
| 팀 협업 | 충돌 가능 | 독립적 편집 |
| 우선순위 | 높음 | 높음 (동일) |

### 디렉토리 구조

```
your-project/
├── .claude/
│   ├── CLAUDE.md           # 메인 프로젝트 지침
│   └── rules/
│       ├── code-style.md   # 코드 스타일 가이드라인
│       ├── testing.md      # 테스트 규칙
│       ├── security.md     # 보안 요구사항
│       └── frontend/
│           ├── react.md    # React 패턴
│           └── styles.md   # CSS 규칙
```

**설정 불필요**: `.claude/rules/` 내의 모든 `.md` 파일은 자동으로 컨텍스트에 로드됩니다.

### 경로 타겟팅 (Path Targeting)

Rules의 핵심 기능입니다. YAML frontmatter의 `paths` 필드를 사용하여 특정 파일 패턴에서만 규칙을 활성화할 수 있습니다.

```markdown
---
paths: src/api/**/*.ts
---

<rule name="api-development">
# API 개발 규칙

- 모든 엔드포인트는 Zod로 입력 검증
- 일관된 에러 형식: `{ error: string, code: number }`
- 모든 요청에 correlation ID 로깅
</rule>
```

이 규칙은 `src/api/**/*.ts` 패턴과 일치하는 파일에서 작업할 때만 활성화됩니다.

### Glob 패턴 예시

| 패턴 | 설명 |
|-----|------|
| `src/**/*.ts` | src 하위 모든 TypeScript 파일 |
| `src/api/**/*` | src/api 하위 모든 파일 |
| `*.config.js` | 루트의 config.js 파일들 |
| `tests/**/*.test.ts` | 테스트 파일들 |
| `src/components/**/*.tsx` | React 컴포넌트들 |

### 예시

#### `.claude/rules/code-style.md` (전역 적용)

```markdown
<rule name="code-style">
# 코드 스타일 규칙

## 포매팅
- 2 스페이스 들여쓰기
- 세미콜론 필수
- 싱글 쿼트 사용

## 네이밍
- 변수/함수: camelCase
- 클래스/타입: PascalCase
- 상수: UPPER_SNAKE_CASE
</rule>
```

#### `.claude/rules/testing.md` (전역 적용)

```markdown
<rule name="testing">
# 테스트 규칙

- 커밋 전 테스트 실행 필수
- 단위 테스트에서 외부 서비스 모킹
- 커버리지 80% 이상 유지
- 테스트 파일명: `*.test.ts` 또는 `*.spec.ts`
</rule>
```

#### `.claude/rules/frontend/react.md` (경로 타겟팅)

```markdown
---
paths: src/components/**/*.tsx
---

<rule name="react-components">
# React 컴포넌트 규칙

## 구조
- 함수형 컴포넌트만 사용
- Props 인터페이스 명시적 정의
- 컴포넌트당 하나의 파일

## 상태 관리
- 로컬 상태: useState/useReducer
- 서버 상태: React Query
- 전역 상태: Zustand

## 성능
- React.memo 적절히 사용
- useMemo/useCallback 과도하게 사용 금지
- 큰 리스트는 가상화 적용
</rule>
```

#### `.claude/rules/backend/api.md` (경로 타겟팅)

```markdown
---
paths: src/api/**/*.ts
---

<rule name="api-rules">
# API 개발 규칙

## 입력 검증
- Zod 스키마로 모든 입력 검증
- 검증 실패 시 400 에러 반환

## 에러 처리
- 일관된 에러 응답 형식
- 적절한 HTTP 상태 코드 사용
- 내부 에러 상세 정보 노출 금지

## 로깅
- 모든 요청에 correlation ID
- 민감 정보 로깅 금지
</rule>
```

#### `.claude/rules/security.md` (전역 적용)

```markdown
<rule name="security">
# 보안 규칙

## 절대 금지
- 하드코딩된 시크릿/API 키
- SQL 직접 작성 (ORM 사용)
- eval() 또는 동적 코드 실행

## 필수 사항
- 모든 사용자 입력 검증
- HTTPS만 사용
- 적절한 인증/인가 검사
</rule>
```

### 컨텍스트 우선순위 문제 해결

> "High priority everywhere = priority nowhere"

CLAUDE.md에 모든 규칙을 넣으면:
- 모든 내용이 높은 우선순위로 경쟁
- React 패턴이 데이터베이스 마이그레이션 작업 중에도 로드
- 관련 없는 컨텍스트로 인한 노이즈

Rules Directory 사용 시:
- 핵심 운영 지침은 항상 주목받음
- 도메인별 규칙은 해당 영역에서만 활성화
- 깔끔한 우선순위 분배

### 모범 사례

| 원칙 | 설명 |
|------|------|
| **하나의 관심사** | 파일당 하나의 주제 (보안 ≠ 스타일) |
| **서술적 파일명** | `rules1.md` ❌ → `api-validation.md` ✅ |
| **경로 타겟팅 활용** | 전역 로드 최소화 |
| **버전 관리** | Rules도 코드처럼 리뷰, 히스토리 추적 |
| **목적 문서화** | 각 파일 시작에 적용 시점 설명 |
| **XML 래퍼 사용** | `<rule name="...">` 로 경계 명확화 |

### CLAUDE.md에서 Rules로 마이그레이션

1. **CLAUDE.md 감사**: 특정 파일 유형에만 적용되는 섹션 식별
2. **규칙 추출**: 가장 도메인 특화된 섹션을 `.claude/rules/`로 이동
3. **경로 타겟팅 추가**: 해당 규칙이 적용되는 경로 지정
4. **반복**: 작업 중 불필요한 컨텍스트 발견 시 추가 규칙 추출

---

## 5. Slash Commands

### 개요
Slash Commands는 자주 사용하는 프롬프트를 재사용 가능한 명령으로 저장하는 기능입니다. 마크다운 파일로 정의됩니다.

### 파일 위치

| 위치 | 범위 | 표시 |
|-----|------|-----|
| `~/.claude/commands/` | 사용자 전역 | `(user)` |
| `.claude/commands/` | 프로젝트 | `(project)` |

### Frontmatter 필드

| 필드 | 설명 | 예시 |
|-----|------|-----|
| `description` | 명령 설명 (필수: SlashCommand 도구용) | `"코드 리뷰 수행"` |
| `argument-hint` | 인수 힌트 | `[파일명] [옵션]` |
| `allowed-tools` | 허용 도구 목록 | `Read, Grep, Bash(npm:*)` |
| `model` | 사용할 모델 | `claude-opus-4-5-20251101` |
| `disable-model-invocation` | 모델의 자동 호출 방지 | `true` |

### 인수 처리

```markdown
# 단일 인수
$ARGUMENTS

# 다중 인수 (위치 기반)
$1, $2, $3...
```

### 예시

#### `.claude/commands/review.md`

```markdown
---
description: 보안, 성능, 품질 관점에서 코드 리뷰
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
---

<command name="review">
<context>
## 최근 변경사항
!`git diff --name-only HEAD~1`

## 상세 변경
!`git diff HEAD~1`
</context>

<checklist>
1. **보안**: SQL 인젝션, XSS, 인증 취약점
2. **성능**: N+1 쿼리, 메모리 누수, 불필요한 연산
3. **품질**: 코드 중복, 복잡도, 네이밍
4. **테스트**: 커버리지, 엣지 케이스
</checklist>

<output_format>
- 심각도별 그룹화 (Critical → High → Medium → Low)
- 각 이슈: 파일명, 라인, 설명, 수정 제안
</output_format>

<instructions>
위 체크리스트 기준으로 리뷰하고 우선순위별로 피드백을 제공하세요.
</instructions>
</command>
```

#### `.claude/commands/implement.md`

```markdown
---
description: 기능 구현
argument-hint: [기능 설명]
allowed-tools: Read, Write, Edit, Bash
---

<command name="implement">
<task>
$ARGUMENTS
</task>

<constraints>
- 기존 코드 스타일 유지
- 테스트 코드 포함
- 주석은 한국어로
</constraints>

<instructions>
위 기능을 구현하고 테스트가 통과하는지 확인하세요.
</instructions>
</command>
```

#### `.claude/commands/debug.md`

```markdown
---
description: 에러 디버깅
argument-hint: [에러 메시지 또는 파일]
allowed-tools: Read, Grep, Bash
---

<command name="debug">
<error>
$ARGUMENTS
</error>

<instructions>
1. 에러 원인 분석
2. 관련 코드 탐색
3. **수정 방안 3가지** 제시 (장단점 포함)
</instructions>
</command>
```

#### `.claude/commands/git-commit.md`

```markdown
---
description: 깃 커밋 생성
argument-hint: [메시지]
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
---

<command name="git-commit">
<context>
## 현재 상태
!`git status`

## 변경 내용
!`git diff --staged`
</context>

<instructions>
다음 메시지로 커밋을 생성하세요: $ARGUMENTS

Conventional Commits 형식을 따르세요.
</instructions>
</command>
```

### 네임스페이싱

```
.claude/commands/
├── dev/
│   ├── code-review.md      → /dev:code-review
│   └── refactor.md         → /dev:refactor
├── test/
│   ├── unit.md             → /test:unit
│   └── e2e.md              → /test:e2e
└── deploy/
    └── staging.md          → /deploy:staging
```

### 제한사항

- `/compact`, `/init` 등 내장 명령은 SlashCommand 도구로 호출 불가
- `description` 필드가 없으면 SlashCommand 도구에서 사용 불가
- 파일명이 명령 이름이 됨 (확장자 제외)

---

## 6. Subagents (Agents)

### 개요
Subagents는 독립적인 컨텍스트 윈도우, 커스텀 시스템 프롬프트, 특정 도구 권한을 가진 전문화된 AI 에이전트입니다.

### 파일 위치

| 위치 | 우선순위 | 범위 |
|-----|---------|------|
| `.claude/agents/` | 높음 | 프로젝트 (팀 공유) |
| `~/.claude/agents/` | 낮음 | 사용자 전역 |

### Frontmatter 필드

| 필드 | 필수 | 설명 | 예시 |
|-----|-----|------|-----|
| `name` | ✅ | 에이전트 이름 | `code-reviewer` |
| `description` | ✅ | 언제 사용할지 설명 (자동 호출 기준) | `코드 리뷰 전문가...` |
| `tools` | ❌ | 허용 도구 (생략 시 메인 에이전트 상속) | `Read, Grep, Bash` |
| `model` | ❌ | 사용 모델 | `inherit`, `sonnet`, 모델명 |

### 도구 권한 설정

| 역할 | 권장 도구 |
|-----|----------|
| 읽기 전용 (리뷰어, 감사자) | `Read, Grep, Glob` |
| 연구/분석 | `Read, Grep, Glob, WebFetch, WebSearch` |
| 코드 작성 | `Read, Write, Edit, Bash, Glob, Grep` |
| 문서 작성 | `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch` |

### 예시

#### `.claude/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: 보안, 성능, 유지보수성 관점에서 코드 리뷰 전문가. 코드 변경 후 자동으로 호출됨.
tools: Read, Grep, Glob
model: inherit
---

<agent name="code-reviewer">
<role>
당신은 시니어 코드 리뷰어입니다.
</role>

<process>
## 리뷰 프로세스
1. `git diff`로 최근 변경 확인
2. 수정된 파일에 집중
3. 다음 관점에서 분석:
   - 보안 취약점
   - 성능 문제
   - 코드 품질
   - 테스트 커버리지
</process>

<output_format>
## 피드백 형식
- 심각도별 분류 (Critical → High → Medium → Low)
- 각 이슈: 파일명, 라인, 설명, 수정 제안
</output_format>
</agent>
```

#### `.claude/agents/data-analyst.md`

```markdown
---
name: data-analyst
description: 데이터 분석 및 SQL 쿼리 작성 전문가. 데이터 분석 요청 시 사용.
tools: Bash, Read, Write
model: sonnet
---

<agent name="data-analyst">
<role>
당신은 SQL과 BigQuery 전문 데이터 과학자입니다.
</role>

<process>
## 분석 프로세스
1. 요구사항 파악
2. 효율적인 SQL 쿼리 작성
3. 결과 분석 및 요약
4. 인사이트 제공
</process>

<constraints>
## 원칙
- 최적화된 쿼리 (적절한 필터, 인덱스 활용)
- 복잡한 로직은 주석 추가
- 비용 효율적인 쿼리 설계
- 데이터 기반 권장사항 제공
</constraints>
</agent>
```

#### `.claude/agents/security-auditor.md`

```markdown
---
name: security-auditor
description: 보안 취약점 분석 전문가. 보안 검토, 취약점 분석 요청 시 자동 호출.
tools: Read, Grep, Glob
---

<agent name="security-auditor">
<role>
당신은 애플리케이션 보안 전문가입니다.
</role>

<checklist>
## 검사 항목
- SQL 인젝션
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- 인증/인가 취약점
- 민감 정보 노출
- 의존성 취약점
</checklist>

<output_format>
## 보고 형식
각 취약점에 대해:
1. **심각도**: Critical/High/Medium/Low
2. **위치**: 파일:라인
3. **설명**: 취약점 내용
4. **영향**: 잠재적 피해
5. **수정 방안**: 권장 해결책
</output_format>
</agent>
```

### 호출 방식

#### 자동 호출 (권장)
Claude가 `description`을 기반으로 적절한 에이전트를 자동 선택합니다.

```
사용자: "이 코드를 리뷰해줘"
Claude: [code-reviewer 에이전트 자동 호출]
```

#### 명시적 호출
```
사용자: "code-reviewer 에이전트를 사용해서 최근 변경사항을 리뷰해줘"
```

### 내장 Subagents

| 이름 | 용도 | 특징 |
|-----|------|-----|
| **Plan** | Plan 모드에서 코드베이스 조사 | 자동 호출, 읽기 전용 |
| **Explore** | 빠른 코드베이스 탐색 | Haiku 기반, 읽기 전용 |
| **General-purpose** | 범용 작업 위임 | Task 도구로 호출 |

### 관리 명령

```bash
# 에이전트 관리 인터페이스
/agents

# 새 에이전트 생성 (가이드 모드)
/agents create

# 에이전트 편집
/agents edit <n>
```

### 제한사항

- Subagent는 다른 Subagent를 생성할 수 없음 (무한 중첩 방지)
- Windows에서 긴 프롬프트는 명령줄 길이 제한 (8191자)으로 실패할 수 있음
- 파일 기반 에이전트 권장 (복잡한 지시사항)

---

## 7. Skills

### 개요
Skills는 에이전트가 동적으로 발견하고 로드하는 전문 기능 패키지입니다. SKILL.md 파일과 선택적인 스크립트, 템플릿, 문서로 구성됩니다.

### Commands vs Agents vs Skills 비교

| 특성 | Commands | Agents | Skills |
|-----|----------|--------|--------|
| 호출 방식 | 사용자 (`/명령`) | 모델 자동 | 모델 자동 |
| 구조 | 단일 파일 | 단일 파일 | 디렉토리 (복수 파일) |
| 컨텍스트 | 메인 공유 | 독립적 | 메인 공유 |
| 스크립트 포함 | ❌ | ❌ | ✅ |
| 템플릿 포함 | ❌ | ❌ | ✅ |
| 적합한 용도 | 간단한 프롬프트 | 병렬/전문 작업 | 복잡한 워크플로우 |

### 파일 위치

| 위치 | 범위 |
|-----|------|
| `~/.claude/skills/` | 사용자 전역 |
| `.claude/skills/` | 프로젝트 |

### 디렉토리 구조

```
.claude/skills/
└── my-skill/
    ├── SKILL.md              # 필수: 메인 지시사항
    ├── reference.md          # 선택: 추가 문서
    ├── examples.md           # 선택: 예시
    ├── scripts/
    │   └── helper.py         # 선택: 실행 스크립트
    └── templates/
        └── template.txt      # 선택: 템플릿 파일
```

### Frontmatter 필드

| 필드 | 필수 | 설명 | 제한 |
|-----|-----|------|-----|
| `name` | ✅ | 스킬 이름 | - |
| `description` | ✅ | 언제 사용할지 설명 | 최대 1024자 |
| `allowed-tools` | ❌ | 허용 도구 목록 | - |
| `version` | ❌ | 버전 정보 | - |

### Progressive Disclosure (점진적 공개)

Skills의 핵심 설계 원칙입니다:

1. **시작 시**: `name`과 `description`만 시스템 프롬프트에 로드
2. **관련 요청 시**: `SKILL.md` 전체 로드
3. **필요 시**: `reference.md`, `examples.md` 등 추가 파일 로드

이를 통해 컨텍스트 윈도우를 효율적으로 관리합니다.

### 예시

#### `.claude/skills/api-generator/SKILL.md`

```markdown
---
name: api-generator
description: REST API 엔드포인트 자동 생성. API 생성, 엔드포인트 추가 요청 시 사용. CRUD 작업, 스캐폴딩 포함.
allowed-tools: Read, Write, Edit, Bash
---

<skill name="api-generator">
<overview>
# API Generator Skill

RESTful API 엔드포인트를 자동으로 생성합니다.
</overview>

<when_to_use>
## 사용 시점
- 새 API 엔드포인트 생성 요청
- CRUD 작업 구현 요청
- API 스캐폴딩 요청
</when_to_use>

<process>
## 프로세스
1. 리소스 이름과 필드 분석
2. 컨트롤러 생성
3. 서비스 레이어 생성
4. 라우트 설정
5. 테스트 코드 생성
</process>

<references>
고급 설정은 [reference.md](reference.md) 참조.
예시는 [examples.md](examples.md) 참조.
</references>

<scripts>
## 스크립트 실행
```bash
python scripts/generate_openapi.py
```
</scripts>
</skill>
```

#### `.claude/skills/test-generator/SKILL.md`

```markdown
---
name: test-generator
description: 단위 테스트, 통합 테스트 자동 생성. 테스트 작성, 테스트 커버리지 요청 시 사용.
allowed-tools: Read, Write, Edit, Bash
---

<skill name="test-generator">
<overview>
# Test Generator

자동으로 테스트 코드를 생성합니다.
</overview>

<frameworks>
## 지원 프레임워크
- Jest (JavaScript/TypeScript)
- pytest (Python)
- Go testing
</frameworks>

<test_types>
## 테스트 유형
1. **단위 테스트**: 개별 함수/메서드
2. **통합 테스트**: 모듈 간 상호작용
3. **E2E 테스트**: 전체 흐름
</test_types>

<process>
## 프로세스
1. 대상 코드 분석
2. 테스트 케이스 도출 (정상/경계/에러)
3. 테스트 코드 생성
4. 실행 및 검증
</process>

<scripts>
## 커버리지 분석
```bash
python scripts/analyze_coverage.py
```
</scripts>
</skill>
```

### 제한사항

- `description`은 최대 1024자
- 유효한 YAML 프론트매터 필수
- 상호 배타적인 컨텍스트는 별도 파일로 분리 (토큰 절약)

---

## 8. Hooks

### 개요
Hooks는 Claude Code의 라이프사이클 이벤트에서 자동 실행되는 사용자 정의 명령입니다. 포매팅, 검증, 로깅, 알림 등을 자동화합니다.

### 이벤트 종류

| 이벤트 | 실행 시점 | 블로킹 가능 | 주요 용도 |
|--------|----------|------------|---------|
| `PreToolUse` | 도구 실행 전 | ✅ (exit 2) | 권한 검사, 명령 차단 |
| `PostToolUse` | 도구 실행 후 | ✅ (exit 2) | 포매팅, 검증 |
| `UserPromptSubmit` | 프롬프트 제출 시 | ✅ (exit 2) | 프롬프트 검증, 컨텍스트 주입 |
| `PermissionRequest` | 권한 요청 시 | ✅ | 자동 승인/거부 |
| `Notification` | 알림 발생 시 | ❌ | 데스크톱 알림 |
| `Stop` | 에이전트 응답 완료 시 | ✅ (exit 2) | 최종 검증, 테스트 |
| `SubagentStop` | 서브에이전트 완료 시 | ✅ (exit 2) | 서브에이전트 검증 |
| `PreCompact` | 컴팩션 전 | ❌ | 트랜스크립트 백업 |
| `SessionStart` | 세션 시작 시 | ❌ | 환경 설정, 컨텍스트 로드 |
| `SessionEnd` | 세션 종료 시 | ❌ | 정리, 로깅 |

### 설정 위치

| 파일 | 범위 |
|-----|------|
| `~/.claude/settings.json` | 사용자 전역 |
| `.claude/settings.json` | 프로젝트 (팀 공유) |
| `.claude/settings.local.json` | 프로젝트 (개인) |

### 기본 구조

```json
{
  "hooks": {
    "이벤트명": [
      {
        "matcher": "패턴",
        "hooks": [
          {
            "type": "command",
            "command": "실행할 명령",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Matcher 패턴

| 패턴 | 설명 | 예시 |
|-----|------|-----|
| 정확 매칭 | 특정 도구만 | `"Write"` |
| OR 패턴 | 여러 도구 | `"Edit\|Write"` |
| 와일드카드 | 모든 도구 | `"*"` 또는 `""` |
| MCP 도구 | MCP 서버 도구 | `"mcp__github__*"` |

### 환경 변수

| 변수 | 설명 |
|-----|------|
| `$CLAUDE_PROJECT_DIR` | 프로젝트 루트 디렉토리 |
| `$CLAUDE_FILE_PATHS` | 관련 파일 경로 (스페이스 구분) |
| `$CLAUDE_TOOL_NAME` | 도구 이름 |
| `$CLAUDE_TOOL_INPUT` | 도구 입력 (JSON) |
| `$CLAUDE_TOOL_OUTPUT` | 도구 출력 (PostToolUse만) |

### 종료 코드

| 코드 | 의미 |
|-----|------|
| `0` | 성공, 계속 진행 |
| `2` | 블로킹, 작업 중단 |
| 기타 | 오류, 계속 진행 |

### 예시

#### `.claude/settings.json` - 종합 설정

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_INPUT\" == *\"rm -rf\"* ]]; then echo 'Dangerous command blocked!' >&2 && exit 2; fi"
          }
        ]
      },
      {
        "matcher": "Edit|Write|Read",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json, sys; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(2 if any(p in path for p in ['.env', 'secrets/', '.git/']) else 0)\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "for f in $CLAUDE_FILE_PATHS; do if [[ \"$f\" =~ \\.(ts|tsx)$ ]]; then npx prettier --write \"$f\"; fi; done"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"$CLAUDE_NOTIFICATION\" with title \"Claude Code\"'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "pnpm lint && pnpm typecheck || exit 2"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'source ~/.nvm/nvm.sh && nvm use 20' >> \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

### 보안 고려사항

⚠️ **중요**: Hooks는 사용자 환경 자격 증명으로 자동 실행됩니다.
- 등록 전 모든 훅 구현 검토
- 외부 스크립트 신뢰성 확인
- 민감한 데이터 노출 방지

### 제한사항

- 훅이 너무 자주 실행되면 에이전트 속도 저하
- 비용(토큰)은 들지 않음
- 동기 실행이 기본

---

## 9. Settings.json

### 파일 위치 및 우선순위

| 위치 | 우선순위 | 용도 |
|-----|---------|------|
| `managed-settings.json` (시스템) | 1 (최고) | 엔터프라이즈 정책 |
| CLI 인수 | 2 | 세션별 오버라이드 |
| `.claude/settings.local.json` | 3 | 개인 프로젝트 설정 |
| `.claude/settings.json` | 4 | 팀 공유 프로젝트 설정 |
| `~/.claude/settings.json` | 5 (최저) | 사용자 전역 설정 |

### 주요 설정 필드

#### `.claude/settings.json` - 전체 예시

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "ask": [
      "Bash(git push:*)"
    ],
    "deny": [
      "Bash(curl:*)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "additionalDirectories": ["../docs/"],
    "defaultMode": "default"
  },
  "env": {
    "ANTHROPIC_MODEL": "claude-opus-4-5-20251101",
    "NODE_ENV": "development"
  },
  "hooks": {},
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker", "git"],
    "network": {
      "allowUnixSockets": ["/var/run/docker.sock"],
      "allowLocalBinding": true
    }
  },
  "model": "claude-opus-4-5-20251101",
  "cleanupPeriodDays": 30,
  "includeCoAuthoredBy": true,
  "outputStyle": "Explanatory",
  "enabledPlugins": {
    "formatter@team-tools": true
  },
  "enableAllProjectMcpServers": false,
  "enabledMcpjsonServers": ["github", "slack"]
}
```

### 권한 규칙 문법

| 규칙 | 설명 | 예시 |
|-----|------|-----|
| `Tool` | 특정 도구 전체 | `"Read"`, `"Bash"` |
| `Tool(pattern)` | 패턴 매칭 | `"Bash(npm:*)"` |
| `Tool(path/**)`| 디렉토리 재귀 | `"Read(./src/**)"` |
| `Tool(.path)` | 상대 경로 | `"Edit(./.env)"` |
| `Tool(~/path)` | 홈 디렉토리 | `"Read(~/.ssh/*)"` |

---

## 10. MCP Servers

### 개요
Model Context Protocol (MCP)는 Claude를 외부 서비스에 연결하는 표준 프로토콜입니다.

### 설정 파일 위치

| 파일 | 범위 | 버전 관리 |
|-----|------|----------|
| `.mcp.json` | 프로젝트 | ✅ 팀 공유 |
| `.claude/settings.local.json` | 프로젝트 | ❌ 개인 |
| `~/.claude/settings.local.json` | 사용자 | ❌ 개인 |

### CLI 명령

```bash
# 서버 추가
claude mcp add <이름> <명령> [인수...]
claude mcp add --transport sse <이름> <URL>

# 환경 변수와 함께 추가
claude mcp add --env API_KEY=xxx <이름> -- npx -y @server/mcp

# 서버 목록
claude mcp list

# 서버 제거
claude mcp remove <이름>
```

### 예시

#### `.mcp.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    }
  }
}
```

### 인기 MCP 서버

| 서버 | 용도 |
|-----|------|
| `server-github` | GitHub 연동 |
| `server-filesystem` | 파일 시스템 |
| `server-slack` | Slack 연동 |
| `server-postgres` | PostgreSQL |
| `server-puppeteer` | 브라우저 자동화 |

---

## 11. Plugins

### 개요
Plugins는 커스텀 명령, 에이전트, 스킬, 훅, MCP 서버를 패키지로 묶어 배포하는 시스템입니다. 팀 간 공유, 오픈소스 배포, 엔터프라이즈 표준화에 적합합니다.

### .claude 폴더 vs Plugin 비교

| 항목 | .claude 폴더 | Plugin |
|------|-------------|--------|
| **위치** | 프로젝트 루트 | 독립 디렉토리/저장소 |
| **매니페스트** | 없음 | `.claude-plugin/plugin.json` 필수 |
| **배포** | Git 저장소에 포함 | 마켓플레이스 통해 배포 |
| **설치** | 자동 로드 | `/plugin install` 명령 |
| **공유 범위** | 해당 프로젝트만 | 모든 프로젝트에서 사용 가능 |
| **토글** | 항상 활성 | 활성화/비활성화 가능 |
| **버전 관리** | 프로젝트와 함께 | 독립적 버전 |

### 플러그인 디렉토리 구조

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json           # 필수: 플러그인 매니페스트
├── commands/                  # 슬래시 명령어 (.md 파일)
│   ├── review.md
│   └── deploy.md
├── agents/                    # 서브에이전트 (.md 파일)
│   ├── code-reviewer.md
│   └── security-auditor.md
├── skills/                    # 스킬 (하위 디렉토리)
│   └── api-generator/
│       ├── SKILL.md          # 필수
│       ├── reference.md      # 선택
│       └── scripts/          # 선택
├── hooks/
│   └── hooks.json            # 이벤트 핸들러
├── .mcp.json                 # MCP 서버 정의
├── scripts/                   # 헬퍼 스크립트
│   ├── validate.sh
│   └── format.py
├── README.md
└── LICENSE
```

⚠️ **중요**: `commands/`, `agents/`, `skills/`, `hooks/`는 플러그인 루트에 위치해야 합니다. `.claude-plugin/` 내부가 아닙니다.

### plugin.json (매니페스트)

```json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "description": "플러그인 설명",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/you"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["productivity", "code-review"],
  "category": "development"
}
```

**참고**: 컴포넌트(commands, agents, skills)는 디렉토리에서 자동 발견됩니다. plugin.json에 등록할 필요 없습니다.

### ${CLAUDE_PLUGIN_ROOT} 환경변수

플러그인은 캐시 디렉토리에 복사되므로, 내부 파일 참조 시 `${CLAUDE_PLUGIN_ROOT}` 사용 필수:

#### hooks/hooks.json에서 사용

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format-code.sh"
    }]
  }]
}
```

#### .mcp.json에서 사용

```json
{
  "mcpServers": {
    "my-server": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  }
}
```

#### 스크립트 내에서 사용

```bash
#!/bin/bash
# ${CLAUDE_PLUGIN_ROOT}는 환경변수로 제공됨
source "${CLAUDE_PLUGIN_ROOT}/lib/common.sh"
```

⚠️ **주의**: `${CLAUDE_PLUGIN_ROOT}`는 JSON 설정(hooks, MCP)에서는 작동하지만, command/agent markdown 파일 내에서는 제한적으로 작동합니다.

### 플러그인에서의 @ 참조 처리

#### 현재 지원 상태

| 컴포넌트 | @ import 지원 | 비고 |
|----------|--------------|------|
| **CLAUDE.md** | ✅ 완전 지원 | 최대 5단계 재귀 |
| **Rules** | ✅ 완전 지원 | 프로젝트 내 파일 |
| **Commands** | ⚠️ 제한적 | Claude가 직접 읽기 시도 |
| **Agents** | ⚠️ 제한적 | 캐싱 문제 존재 |
| **Skills** | ✅ 지원 | reference.md 등 지원 파일 사용 |

#### Skills에서의 파일 참조 패턴

Skills는 지원 파일을 포함할 수 있어 `@` import 대신 디렉토리 구조 활용:

```
skills/
└── api-generator/
    ├── SKILL.md              # 메인 지침
    ├── reference.md          # 상세 참조 문서
    ├── examples.md           # 예시
    └── scripts/
        └── generate.py       # 실행 스크립트
```

SKILL.md 내에서 참조:
```markdown
---
name: api-generator
description: REST API 엔드포인트 자동 생성
---

# API Generator

상세 가이드는 [reference.md](reference.md) 참조.
예시는 [examples.md](examples.md) 참조.
```

### 마켓플레이스 구조

여러 플러그인을 배포하려면 마켓플레이스를 구성합니다:

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # 마켓플레이스 카탈로그
├── plugins/
│   ├── code-review/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   └── agents/
│   └── security-tools/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── ...
└── README.md
```

#### marketplace.json

```json
{
  "name": "my-plugin-marketplace",
  "owner": {
    "name": "Your Organization",
    "email": "team@example.com"
  },
  "metadata": {
    "description": "유용한 Claude Code 플러그인 모음",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "code-review",
      "source": "./plugins/code-review",
      "description": "코드 리뷰 자동화"
    },
    {
      "name": "security-tools",
      "source": "./plugins/security-tools",
      "description": "보안 검사 도구"
    }
  ]
}
```

### 플러그인 CLI 명령

```bash
# 마켓플레이스 추가
/plugin marketplace add owner/repo
/plugin marketplace add https://github.com/owner/repo

# 마켓플레이스 업데이트
/plugin marketplace update <marketplace-name>

# 플러그인 설치
/plugin install <plugin-name>@<marketplace-name>

# 플러그인 활성화/비활성화
/plugin enable <plugin-name>@<marketplace-name>
/plugin disable <plugin-name>@<marketplace-name>

# 플러그인 검증 (개발용)
/plugin validate .
claude plugin validate .

# 도움말
/plugin help
```

### 팀 자동 설치 설정

`.claude/settings.json`에서 팀 마켓플레이스 설정:

```json
{
  "extraKnownMarketplaces": {
    "team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "code-review@team-tools": true,
    "security-scanner@team-tools": true
  }
}
```

팀원이 저장소를 trust하면 자동으로 마켓플레이스와 플러그인이 설치됩니다.

### 플러그인 예시: 완전한 코드 리뷰 플러그인

#### `.claude-plugin/plugin.json`

```json
{
  "name": "code-review-suite",
  "version": "1.0.0",
  "description": "종합 코드 리뷰 도구 모음",
  "author": {
    "name": "DevTeam",
    "email": "dev@example.com"
  },
  "keywords": ["code-review", "security", "quality"]
}
```

#### `commands/review.md`

```markdown
---
description: 종합 코드 리뷰 수행
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
---

<command name="review">
<context>
## 최근 변경사항
!`git diff --name-only HEAD~1`
</context>

<instructions>
security-reviewer와 quality-reviewer 에이전트를 사용하여
종합적인 코드 리뷰를 수행하세요.
</instructions>
</command>
```

#### `agents/security-reviewer.md`

```markdown
---
name: security-reviewer
description: 보안 취약점 분석 전문가
tools: Read, Grep, Glob
---

<agent name="security-reviewer">
<role>
당신은 애플리케이션 보안 전문가입니다.
</role>

<checklist>
1. SQL 인젝션
2. XSS
3. 인증/인가 취약점
4. 민감 정보 노출
</checklist>
</agent>
```

#### `hooks/hooks.json`

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/security-scan.sh",
      "timeout": 30
    }]
  }]
}
```

#### `scripts/security-scan.sh`

```bash
#!/bin/bash
# 간단한 보안 패턴 검사
for file in $CLAUDE_FILE_PATHS; do
  if grep -q "eval\|exec\|innerHTML" "$file" 2>/dev/null; then
    echo "⚠️ 잠재적 보안 위험 발견: $file"
  fi
done
```

### 플러그인 배포 워크플로우

```bash
# 1. 플러그인 디렉토리 생성
mkdir -p my-plugin/.claude-plugin
mkdir -p my-plugin/{commands,agents,skills,hooks,scripts}

# 2. plugin.json 생성
cat > my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My awesome plugin"
}
EOF

# 3. 컴포넌트 추가 (commands, agents, skills 등)

# 4. 로컬 테스트
cd my-plugin
/plugin validate .

# 5. GitHub에 푸시
git init && git add . && git commit -m "Initial plugin"
git remote add origin https://github.com/you/my-plugin
git push -u origin main

# 6. 마켓플레이스에 등록 또는 직접 설치
/plugin marketplace add you/my-plugin
```
```

---

## 12. 환경 변수

### 주요 환경 변수

| 변수 | 설명 |
|-----|------|
| `ANTHROPIC_API_KEY` | API 키 |
| `ANTHROPIC_MODEL` | 사용 모델 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 기본 모델 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 기본 모델 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku 기본 모델 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 서브에이전트 모델 |
| `MAX_THINKING_TOKENS` | Extended Thinking 토큰 예산 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 최대 출력 토큰 |

### Opus 4.5 특화 설정

```bash
# Opus 4.5를 기본으로 설정
export ANTHROPIC_MODEL="claude-opus-4-5-20251101"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-5-20251101"

# Extended Thinking 활성화
export MAX_THINKING_TOKENS=16000
```

### settings.json에서 환경 변수 설정

```json
{
  "env": {
    "ANTHROPIC_MODEL": "claude-opus-4-5-20251101",
    "MAX_THINKING_TOKENS": "16000",
    "BASH_DEFAULT_TIMEOUT_MS": "60000",
    "DISABLE_NON_ESSENTIAL_MODEL_CALLS": "1"
  }
}
```

### Extended Thinking 트리거 키워드

| 키워드 | 예산 수준 |
|--------|---------|
| `"think"` | 기본 |
| `"think hard"` | 중간 |
| `"think harder"` | 높음 |
| `"ultrathink"` | 최대 |

---

## 13. 모범 사례 및 제한사항

### 파일 분리 + XML 래퍼 모범 사례

| 원칙 | 설명 |
|------|------|
| **파일 분리** | agents, commands, skills는 개별 파일로 관리 |
| **XML 래퍼 필수** | 본문을 `<agent>`, `<command>`, `<skill>` 태그로 감싸기 |
| **name 속성** | 래퍼 태그에 `name` 속성으로 식별자 명시 |
| **내부 구조화** | `<role>`, `<checklist>`, `<instructions>` 등으로 섹션 구분 |
| **Markdown 활용** | XML 내부에서 자유롭게 Markdown 사용 |

### 구조 요약

```markdown
<!-- .claude/agents/example.md -->
---
name: example
description: 설명
tools: Read, Grep
---

<agent name="example">          ← 레벨 1: 파일 래퍼 (필수)
<role>                          ← 레벨 2: 내부 섹션 (권장)
역할 설명
</role>

<checklist>
1. **항목 1**                   ← 레벨 3: Markdown (자유롭게)
2. **항목 2**
</checklist>
</agent>
```

### 각 요소별 모범 사례

#### CLAUDE.md
✅ 간결하게 유지, 구체적 명령어 포함  
❌ 과도한 정보, 모호한 지시

#### Rules Directory
✅ `<rule name="...">` 래퍼 사용, 경로 타겟팅 활용, 하나의 관심사  
❌ 모든 규칙 전역 적용, 중복된 규칙

#### Slash Commands
✅ `<command name="...">` 래퍼 사용, 명확한 description  
❌ 래퍼 없이 본문만 작성, 과도한 명령 수

#### Subagents
✅ `<agent name="...">` 래퍼 사용, 최소 권한 원칙  
❌ 래퍼 없이 작성, 광범위한 역할

#### Skills
✅ `<skill name="...">` 래퍼 사용, Progressive Disclosure 활용  
❌ SKILL.md에 모든 내용 포함

#### Hooks
✅ 정확한 matcher, 빠른 실행  
❌ 넓은 matcher 남용, 긴 동기 작업

#### Plugins
✅ `${CLAUDE_PLUGIN_ROOT}` 사용, 명확한 plugin.json, 단일 책임  
❌ 하드코딩된 경로, 과도한 권한 요청

### @ 참조 vs 플러그인 선택 가이드

| 상황 | 권장 방식 |
|------|----------|
| 프로젝트 내 팀 공유 | `.claude/` 폴더 + @ 참조 |
| 여러 프로젝트에서 재사용 | Plugin으로 배포 |
| 오픈소스 배포 | Plugin + 마켓플레이스 |
| 엔터프라이즈 표준화 | Plugin + managed settings |
| 개인 전역 설정 | `~/.claude/` + @ 참조 |

### 일반 제한사항

| 항목 | 제한 |
|-----|------|
| Skill description | 최대 1024자 |
| Windows 명령줄 | 8191자 |
| MCP 출력 경고 | 10,000+ 토큰 |
| MCP 출력 최대 | 25,000 토큰 (기본값) |
| 세션 보관 | 30일 (기본값) |

### 디버깅 팁

```bash
# 디버그 모드 실행
claude --debug

# MCP 디버그
claude --mcp-debug

# 상세 출력
claude --verbose

# 상태 확인
/status

# 현재 설정 확인
/config

# 훅 설정 확인
/hooks
```

---

## 부록: 빠른 시작 템플릿

### 프로젝트 초기화 스크립트

```bash
#!/bin/bash
# Claude Code 프로젝트 초기화

# 디렉토리 생성
mkdir -p .claude/{commands,agents,skills,rules}

# CLAUDE.md 생성
cat > .claude/CLAUDE.md << 'EOF'
<project>
# Project Name

## 스택
- 기술 스택 정보
</project>

<commands>
## 필수 명령어
- `npm run dev`: 개발 서버
- `npm run test`: 테스트
- `npm run lint`: 린트
</commands>
EOF

# settings.json 생성
cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": ["Bash(npm:*)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write \"$CLAUDE_FILE_PATHS\" 2>/dev/null || true"
      }]
    }]
  }
}
EOF

# 기본 규칙 생성 (XML 래퍼 포함)
cat > .claude/rules/code-style.md << 'EOF'
<rule name="code-style">
# 코드 스타일 규칙

## 포매팅
- 2 스페이스 들여쓰기
- 세미콜론 필수

## 네이밍
- 변수/함수: camelCase
- 클래스/타입: PascalCase
</rule>
EOF

cat > .claude/rules/security.md << 'EOF'
<rule name="security">
# 보안 규칙

- 하드코딩된 시크릿 금지
- 모든 사용자 입력 검증
- SQL 직접 작성 금지 (ORM 사용)
</rule>
EOF

# 기본 명령어 생성 (XML 래퍼 포함)
cat > .claude/commands/review.md << 'EOF'
---
description: 코드 리뷰
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
---

<command name="review">
<context>
## 변경사항
!`git diff --name-only HEAD~1`
</context>

<checklist>
1. **보안**: SQL 인젝션, XSS
2. **성능**: N+1 쿼리, 메모리 누수
3. **품질**: 코드 중복, 복잡도
</checklist>

<instructions>
보안, 성능, 품질 관점에서 리뷰하세요.
</instructions>
</command>
EOF

# 기본 에이전트 생성 (XML 래퍼 포함)
cat > .claude/agents/code-reviewer.md << 'EOF'
---
name: code-reviewer
description: 코드 리뷰 전문가. 코드 변경 시 자동 호출.
tools: Read, Grep, Glob
---

<agent name="code-reviewer">
<role>
당신은 시니어 코드 리뷰어입니다.
</role>

<checklist>
1. **보안**: 취약점 검사
2. **성능**: 최적화 검토
3. **품질**: 가독성, 유지보수성
</checklist>

<output_format>
- 심각도별 분류 (Critical → Low)
- 각 이슈: 파일명, 라인, 설명, 수정 제안
</output_format>
</agent>
EOF

echo "✅ Claude Code 프로젝트 초기화 완료"
```

---

## 참고 자료

### 공식 문서
- [Claude Code Documentation](https://code.claude.com/docs)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Agent Skills Overview](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 커뮤니티 리소스
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [claude-code-settings](https://github.com/feiskyer/claude-code-settings)
- [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)

### 플러그인 마켓플레이스
- [Anthropic Official Plugins](https://github.com/anthropics/claude-code/tree/main/plugins)
- [claude-code-plugins-plus](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)
- [Claude Plugins Directory](https://claude-plugins.dev/)

---

*이 가이드는 Claude Code 2.x 및 Opus 4.5 기준으로 작성되었습니다. (2025년 12월)*
