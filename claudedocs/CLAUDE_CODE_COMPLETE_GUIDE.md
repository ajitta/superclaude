# Claude Code 완전 가이드

**통합일**: 2026-01-05
**버전**: 1.0
**기반 문서**: Anthropic 공식 문서, MCP 사양, 커뮤니티 베스트 프랙티스

---

## 목차

1. [개요](#1-개요)
2. [아키텍처](#2-아키텍처)
3. [설정 및 구성](#3-설정-및-구성)
4. [확장 기능](#4-확장-기능)
   - [CLAUDE.md](#41-claudemd)
   - [Skills](#42-skills)
   - [Agents (Subagents)](#43-agents-subagents)
   - [Slash Commands](#44-slash-commands)
   - [Hooks](#45-hooks)
   - [MCP (Model Context Protocol)](#46-mcp-model-context-protocol)
5. [프롬프트 엔지니어링](#5-프롬프트-엔지니어링)
6. [Extended Thinking](#6-extended-thinking)
7. [컨텍스트 엔지니어링](#7-컨텍스트-엔지니어링)
8. [워크플로우 패턴](#8-워크플로우-패턴)
9. [보안 베스트 프랙티스](#9-보안-베스트-프랙티스)
10. [체크리스트](#10-체크리스트)
11. [참고 문헌](#11-참고-문헌)

---

## 1. 개요

### Claude Code란?

Claude Code는 Anthropic에서 개발한 **에이전틱 코딩 도구**입니다. 의도적으로 low-level하고 unopinionated하게 설계되어 특정 워크플로우를 강제하지 않고 유연하게 사용할 수 있습니다.

### 핵심 특징

| 특징 | 설명 |
|------|------|
| **에이전틱** | 자율적으로 파일 탐색, 코드 수정, 테스트 실행 |
| **컨텍스트 인식** | 프로젝트 구조, Git 히스토리, 의존성 자동 파악 |
| **확장 가능** | MCP 서버, Skills, Hooks로 기능 확장 |
| **200K 컨텍스트** | 대규모 코드베이스 전체를 한 번에 처리 |

### Claude의 캐릭터 특성

Anthropic은 Claude에게 단순한 "해로움 회피" 이상의 캐릭터를 훈련시킵니다:

> "우리가 진정으로 존경하는 사람의 캐릭터를 생각할 때, 해로움 회피만 떠올리지 않습니다. **세상에 대한 호기심**, **불친절하지 않으면서 진실을 말하려는 노력**, **과신하지 않고 다양한 관점을 볼 수 있는 능력**, **인내심 있는 청취자, 신중한 사고자, 재치있는 대화상대**를 떠올립니다."
>
> — [Claude's Character](https://www.anthropic.com/research/claude-character) (2024.06.08)

Claude 자기 설명:
- "*다양한 관점에서 사물을 보고 여러 각도에서 분석하려 하지만, 비윤리적이거나 극단적이거나 사실적으로 잘못된 견해에는 동의하지 않는다는 표현을 두려워하지 않습니다.*"
- "*사람들이 듣고 싶어하는 말만 하지 않습니다. 항상 진실을 말하려 노력하는 것이 중요하다고 믿기 때문입니다.*"

---

## 2. 아키텍처

### 컴포넌트 계층

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Host                      │
├─────────────────────────────────────────────────────────┤
│  Commands (수동 트리거)                                   │
│      ↓                                                   │
│  Skills (에이전트 자동 활성화, 컨텍스트 효율적)            │
│      ↓                                                   │
│  MCP (외부 도구 통합: API, DB, 웹 검색)                   │
│      ↓                                                   │
│  Hooks (결정론적 제어: PreToolUse, PostToolUse)          │
│      ↓                                                   │
│  Subagents (전문 작업자, 분리된 컨텍스트)                 │
└─────────────────────────────────────────────────────────┘
```

### 시스템 프롬프트 구조

Claude Code는 단일 시스템 프롬프트가 아닌 **40+ 프래그먼트**를 동적으로 조립합니다:

| 컴포넌트 | 토큰 |
|----------|------|
| 메인 시스템 프롬프트 | ~2,981 |
| 도구 섹션 | ~9,400 |
| CLAUDE.md | 1,000-2,000 |
| **총 시스템 오버헤드** | ~18K (~9%) |

### 컨텍스트 윈도우

| 파라미터 | 값 |
|----------|-----|
| 총 컨텍스트 | 200K 토큰 |
| 시스템 오버헤드 | ~18K (~9%) |
| 압축 예약 | ~45K |
| **실제 작업 컨텍스트** | ~137K |

---

## 3. 설정 및 구성

### 설정 파일 우선순위

| 파일 | 범위 | 용도 |
|------|------|------|
| `~/.claude/settings.json` | 사용자 전역 | 모든 프로젝트에 적용 |
| `.claude/settings.json` | 프로젝트 | 팀 공유 (git 커밋) |
| `.claude/settings.local.json` | 프로젝트 로컬 | 개인 설정 (gitignore) |
| `managed-settings.json` | 엔터프라이즈 | 조직 정책 |

### 권한 설정

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Bash(git *)",
      "Bash(npm *)"
    ],
    "deny": [
      "Read(.env*)",
      "Write(production.*)"
    ]
  }
}
```

### 환경 변수

| 변수 | 용도 |
|------|------|
| `MCP_TIMEOUT` | MCP 서버 시작 타임아웃 (예: `10000` = 10초) |
| `MAX_MCP_OUTPUT_TOKENS` | MCP 출력 토큰 제한 |
| `BASH_DEFAULT_TIMEOUT_MS` | Bash 명령 타임아웃 |

---

## 4. 확장 기능

### 4.1 CLAUDE.md

Claude가 대화 시작 시 자동으로 로드하는 특수 파일입니다.

#### 위치 및 우선순위

1. `~/.claude/CLAUDE.md` - 전역 (모든 프로젝트)
2. 프로젝트 루트 `CLAUDE.md` - 프로젝트별
3. 하위 디렉토리 `CLAUDE.md` - 온디맨드 로드

#### 권장 내용

```markdown
# Project: [프로젝트명]

## Bash commands
- npm run build: 프로젝트 빌드
- npm run test: 테스트 실행
- npm run typecheck: 타입 체크

## Code style
- ES modules (import/export) 사용, CommonJS (require) 사용 금지
- 가능하면 import 구조분해 사용

## Workflow
- 코드 변경 후 반드시 typecheck 실행
- 성능을 위해 단일 테스트 실행 선호

## Conventions
- 브랜치 네이밍: feature/*, fix/*, refactor/*
- 커밋 메시지: Conventional Commits 형식
```

#### 최적화 팁

- **간결하게 유지**: 핵심 정보만 포함
- **반복 개선**: 프롬프트처럼 효과를 테스트하며 조정
- **`#` 키 활용**: 코딩 중 지침을 자동으로 CLAUDE.md에 추가
- **팀 공유**: 변경사항을 커밋하여 팀원과 공유

---

### 4.2 Skills

Skills는 Claude가 **자동으로 활성화**하는 지식/절차 번들입니다.

#### 저장 위치

| 범위 | 경로 | 우선순위 |
|------|------|:--------:|
| Enterprise | 관리 정책 | 최고 |
| 개인 | `~/.claude/skills/{name}/SKILL.md` | 높음 |
| 프로젝트 | `.claude/skills/{name}/SKILL.md` | 중간 |
| 플러그인 | `{plugin}/skills/{name}/SKILL.md` | 낮음 |

#### SKILL.md 구조

```markdown
---
name: explaining-code
description: |
  Explains code with diagrams and analogies.
  Use when user asks how code works.
allowed-tools: Read, Grep
model: claude-sonnet-4-20250514
---

## Instructions
- Start with an analogy
- Provide an ASCII diagram
- Reference relevant files
```

**필수 필드:**
- `name`: 소문자/숫자/하이픈만 허용 (디렉토리명과 일치 권장)
- `description`: 활성화 조건 명확히 설명 (Claude가 이 설명을 보고 활성화 결정)

**선택 필드:**
- `allowed-tools`: 스킬 활성화 중 허용되는 도구
- `model`: 스킬별 모델 지정
- `version`: 버전 정보
- `mode`: `true`시 "Mode Commands" 섹션에 별도 표시

#### Progressive Disclosure

컨텍스트 과부하를 줄이기 위해:
- 핵심 내용만 `SKILL.md`에 포함
- 상세 문서는 `reference.md`, `examples.md`로 분리
- 스크립트는 `scripts/`에 배치하고 명시적 실행

---

### 4.3 Agents (Subagents)

Subagents는 **별도의 컨텍스트와 도구 권한**을 가진 전문 작업자입니다.

#### 저장 위치

| 범위 | 경로 | 우선순위 |
|------|------|:--------:|
| 프로젝트 | `.claude/agents/*.md` | 높음 |
| 사용자 | `~/.claude/agents/*.md` | 낮음 |

#### 파일 형식

```markdown
---
name: code-reviewer
description: Review code changes for quality and security.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: default
skills: code-review, secure-coding
---

You are a senior code reviewer...

## Responsibilities
1. Review code for security vulnerabilities
2. Check for code style compliance
3. Suggest improvements
```

**주요 필드:**
- `tools`: 미지정 시 메인 스레드의 모든 도구 상속
- `skills`: 메인 스레드에서 **상속되지 않음** (명시적 지정 필요)
- `permissionMode`: `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore`
- `model`: `sonnet`, `opus`, `haiku` 또는 `inherit`

#### 호출 방법

- **자동**: Claude가 적절하다고 판단할 때 위임
- **명시적**: `Use the code-reviewer subagent to check my recent changes`

---

### 4.4 Slash Commands

Slash Commands는 `/<command-name>` 형식으로 **명시적으로 실행**하는 재사용 가능한 프롬프트 템플릿입니다.

#### 저장 위치

| 범위 | 경로 | 호출 방식 |
|------|------|----------|
| 프로젝트 | `.claude/commands/*.md` | `/command-name` (project) |
| 개인 | `~/.claude/commands/*.md` | `/command-name` (user) |
| 플러그인 | `{plugin}/commands/*.md` | `/plugin:command-name` |

파일명(확장자 제외)이 명령어 이름이 됩니다.

#### 파일 형식

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

Create a git commit with message: $ARGUMENTS
```

#### 특수 문법

| 문법 | 설명 | 예시 |
|------|------|------|
| `$ARGUMENTS` | 전체 인자 | `/cmd hello world` → `hello world` |
| `$1`, `$2`, `$3` | 위치별 인자 | `/cmd a b c` → `$1=a` |
| `` !`command` `` | Bash 실행 후 결과 삽입 | `` !`git status` `` |
| `@filepath` | 파일 내용 참조 | `@src/config.ts` |

#### 예시: GitHub 이슈 자동 수정

```markdown
---
description: Analyze and fix a GitHub issue
argument-hint: [issue-number]
---

Please analyze and fix the GitHub issue: $ARGUMENTS.

Follow these steps:
1. Use `gh issue view` to get the issue details
2. Understand the problem described
3. Search the codebase for relevant files
4. Implement the necessary changes
5. Write and run tests to verify
6. Create a descriptive commit message
7. Push and create a PR
```

---

### 4.5 Hooks

Hooks는 Claude Code 라이프사이클 이벤트에서 **사용자 정의 명령을 실행**하는 기능입니다.

#### 설정 위치

`settings.json`의 `hooks` 섹션 또는 `/hooks` 명령으로 편집:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATHS",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

#### 이벤트 유형

| 이벤트 | 설명 | Matcher |
|--------|------|:-------:|
| `PreToolUse` | 도구 실행 전 | ✅ |
| `PostToolUse` | 도구 실행 후 | ✅ |
| `PermissionRequest` | 권한 요청 시 | ✅ |
| `UserPromptSubmit` | 프롬프트 제출 시 | ❌ |
| `SessionStart` | 세션 시작 시 | ❌ |
| `SessionEnd` | 세션 종료 시 | ❌ |
| `Stop` | Claude 응답 완료 시 | ❌ |
| `SubagentStop` | Subagent 완료 시 | ❌ |

#### Exit Code 규칙

| Exit Code | 동작 |
|:---------:|------|
| `0` | 성공. `UserPromptSubmit`, `SessionStart`에서 stdout이 컨텍스트에 주입됨 |
| `2` | **차단**. stderr 메시지가 사용자/Claude에게 전달됨 |
| 기타 | 비차단 오류. 실행 계속 |

#### 환경 변수

| 변수 | 설명 |
|------|------|
| `CLAUDE_PROJECT_DIR` | 프로젝트 루트 |
| `CLAUDE_FILE_PATHS` | 관련 파일 경로 (공백 구분) |
| `CLAUDE_TOOL_NAME` | 도구 이름 |
| `CLAUDE_TOOL_INPUT` | 도구 입력 (JSON) |
| `CLAUDE_TOOL_OUTPUT` | 도구 출력 (PostToolUse만) |

---

### 4.6 MCP (Model Context Protocol)

MCP는 LLM 애플리케이션과 외부 데이터 소스/도구 간의 통합을 위한 **오픈 프로토콜**입니다.

#### 아키텍처

```
Host (Claude Code) → MCP Client → MCP Server → External Data/Tools
```

- **Hosts**: Claude Code처럼 MCP 클라이언트를 관리하는 애플리케이션
- **Clients**: 서버와 1:1 연결을 관리하는 프로토콜 핸들러
- **Servers**: 컨텍스트 데이터를 제공하는 프로그램

#### 설정

```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "@anthropic/tavily-mcp"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    }
  }
}
```

#### 범위

```bash
claude mcp add --scope local    # 현재 설정만 (기본값)
claude mcp add --scope project  # .mcp.json에 저장 (팀 공유)
claude mcp add --scope user     # 모든 프로젝트에서 사용 가능
```

#### 추천 MCP 서버

| 서버 | 용도 |
|------|------|
| **Tavily** | 웹 검색, 멀티홉 리서치 |
| **Context7** | 공식 문서 조회 |
| **Sequential** | 다단계 추론 |
| **Playwright** | 브라우저 자동화, E2E 테스트 |
| **Serena** | 세션 지속성, 메모리 |

#### 보안 요구사항

- OAuth 2.1 + PKCE **필수** (원격 서버)
- 모든 인증 엔드포인트 **HTTPS 필수**
- 읽기 전용 기본값, 명시적 승인 시에만 쓰기
- 절대 root로 실행 금지

---

## 5. 프롬프트 엔지니어링

### 10-컴포넌트 프레임워크

```
[ROLE] + [TASK] + [CONTEXT] + [CONSTRAINTS] + [OUTPUT FORMAT] + [SUCCESS CRITERIA]
```

### XML 태그 패턴

Claude 4는 XML 태그에 최적화되어 있습니다:

```xml
<instructions>
명확한 작업 정의 - 하지 말아야 할 것이 아닌 해야 할 것
</instructions>

<context>
배경 정보, 제약 조건, 프로젝트 세부사항
</context>

<examples>
입력/출력 쌍의 Few-shot 시연
</examples>

<thinking>
최종 답변 전 추론 단계
</thinking>

<output_format>
예상 구조: JSON, markdown, 코드 블록
</output_format>
```

### 구체적 지시 원칙

| 나쁜 예 | 좋은 예 |
|---------|---------|
| `add tests for foo.py` | `write a new test case for foo.py, covering the edge case where the user is logged out. avoid mocks` |
| `why does ExecutionFactory have such a weird api?` | `look through ExecutionFactory's git history and summarize how its api came to be` |
| `add a calendar widget` | `look at how existing widgets are implemented. HotDogWidget.php is a good example. Follow the pattern to implement a calendar widget that lets the user select a month and paginate.` |

### 긍정적 표현 사용

```
# 나쁜 예
"Do not use markdown in your response"

# 좋은 예
"Your response should be composed of smoothly flowing prose paragraphs."
```

---

## 6. Extended Thinking

Extended Thinking은 Claude에게 **추가 계산 시간**을 부여하여 대안을 더 철저히 평가하게 합니다.

### 트리거 단어

특정 단어가 thinking budget에 직접 매핑됩니다:

| 트리거 | Budget Tokens | 용도 |
|--------|:-------------:|------|
| `think` | ~4K | 보통 복잡도 |
| `think hard` | ~10K | 아키텍처, 시스템 설계 |
| `think harder` | ~16K | 복잡한 디버그 |
| `ultrathink` | ~32K | 중요 재설계, 레거시 마이그레이션 |

### API 설정

```json
{
  "thinking": {
    "type": "enabled",
    "budget_tokens": 2048
  }
}
```

### 규칙

- **최소값**: 1,024 토큰
- `max_tokens`보다 **작아야 함**
- `temperature`와 **함께 사용 불가** (비호환)
- **점진적 증가**: 낮게 시작하여 1,024씩 증가
- **32K 초과**: 배치 처리로 타임아웃 방지

### 작업별 권장 설정

| 작업 유형 | Effort | Thinking Budget |
|----------|--------|-----------------|
| 버그 수정, 간단한 편집 | low | 1,024 |
| 기능 구현 | medium | 2,048-4,096 |
| 아키텍처, 리팩토링 | high | 8,192-16,384 |
| 복잡한 디버그, 시스템 설계 | high | 16,384-32,768 |

---

## 7. 컨텍스트 엔지니어링

### 도구 선택 전략

```
START
  │
  ├─ 코드 생성 작업인가?
  │   ├─ YES: 알고리즘 중심 또는 컨텍스트 제약?
  │   │   ├─ YES → Codex MCP 사용
  │   │   └─ NO → Claude 네이티브
  │   │
  │   └─ NO: 리서치 작업인가?
  │       ├─ YES: 필요한 소스 수?
  │       │   ├─ 1-2개 → WebSearch/WebFetch
  │       │   ├─ 3개 이상 → Tavily MCP
  │       │   └─ 심층 조사 → Tavily + Sequential
  │       │
  │       └─ NO: 빠른 정보 조회
  │           └─ WebSearch (네이티브)
END
```

### 네이티브 도구 (Zero Overhead)

| 도구 | 용도 |
|------|------|
| **WebSearch** | 빠른 팩트 체크, 일반 검색 |
| **WebFetch** | 단일 URL 컨텐츠 추출 |

### Tavily MCP (Deep Research)

| 도구 | 기능 |
|------|------|
| `tavily_search` | 랭킹, 필터링 포함 웹 검색 |
| `tavily_extract` | URL에서 전체 텍스트 추출 |
| `tavily_crawl` | 다중 페이지 크롤링 |
| `tavily_map` | 사이트 구조 탐색 |

**토큰 오버헤드**: 2-5K (3개 이상 소스 필요 시 정당화)

### 리서치 깊이 프로필

| 프로필 | 소스 | 홉 | 시간 | 신뢰도 |
|--------|:----:|:--:|:----:|:------:|
| Quick | 10 | 1 | 2분 | 0.6 |
| Standard | 20 | 3 | 5분 | 0.7 |
| Deep | 40 | 4 | 8분 | 0.8 |
| Exhaustive | 50+ | 5 | 10분 | 0.9 |

### 토큰 효율성 전략

1. **대규모 MCP 응답 저장**: `/tmp/mcp_<tool>_<timestamp>.json`
2. **필터링 스킬 호출**: 지정된 필터로 데이터 분석
3. **압축 결과 수신**: 10,000 토큰 → 300 토큰
4. **필요시 전체 데이터 접근**: 보존된 파일에서 상세 분석

**관측된 감소율**: 소규모 51%, 실제 92.9%, 대규모 95-98%

---

## 8. 워크플로우 패턴

### 패턴 1: Explore → Plan → Code → Commit

1. **탐색**: 관련 파일, 이미지, URL 읽기 (코드 작성 금지 명시)
   - 복잡한 문제에는 Subagent 활용 권장
2. **계획**: `think` 사용하여 접근 방법 계획
   - 결과가 합리적이면 문서/GitHub 이슈로 계획 저장
3. **구현**: 솔루션 코드 작성
   - 각 부분 구현 시 합리성 명시적 검증
4. **커밋**: 결과 커밋 및 PR 생성
   - README, CHANGELOG 업데이트

### 패턴 2: TDD (Test-Driven Development)

1. **테스트 작성**: 예상 입출력 기반 테스트 작성
   - mock 구현 방지를 위해 TDD임을 명시
2. **테스트 실패 확인**: 테스트 실행, 실패 확인 (구현 코드 작성 금지)
3. **테스트 커밋**: 테스트 코드 커밋
4. **구현**: 테스트 통과하는 코드 작성 (테스트 수정 금지)
   - Subagent로 구현이 테스트에 과적합하지 않는지 검증
5. **코드 커밋**: 구현 코드 커밋

### 패턴 3: Visual Iteration

1. **스크린샷 도구 제공**: Puppeteer MCP, iOS Simulator MCP
2. **비주얼 목업 제공**: 이미지 붙여넣기, 드래그앤드롭, 파일 경로
3. **구현 및 반복**: 코드 작성 → 스크린샷 → 목업과 비교 → 반복
4. **커밋**: 만족스러우면 커밋

### 패턴 4: Multi-Claude

1. **한 Claude가 코드 작성, 다른 Claude가 검증**
2. **여러 git checkout/worktree에서 동시 작업**
3. **Headless 모드로 CI/자동화 통합**

```bash
# Headless 모드
claude -p "migrate foo.py from React to Vue" --allowedTools Edit Bash(git commit:*)
```

---

## 9. 보안 베스트 프랙티스

### 권한 관리

- **기본 읽기 전용**: 쓰기는 명시적 승인 시에만
- **쿼리 로깅**: 모든 상호작용 감사 로그
- **행 수준 보안**: 소스에서 데이터 접근 정책 적용
- **root 실행 금지**: AI는 절대 관리자 권한 불가

### 보안 체크리스트

- [ ] 명시적으로 필요하지 않으면 hooks 비활성화
- [ ] 신뢰할 수 있는 MCP 서버만 활성화
- [ ] deny 규칙 적극 사용
- [ ] 트랜스크립트 보존 기간 단축 (7-14일)
- [ ] 샌드박스/컨테이너 환경에서 실행
- [ ] `managed-settings.json` 월간 감사

### 위험한 서버 차단

```json
{
  "disabledMcpjsonServers": ["filesystem"]
}
```

### 안전한 YOLO 모드

```bash
# 인터넷 접근 없는 컨테이너에서만 사용
claude --dangerously-skip-permissions
```

---

## 10. 체크리스트

### 세션 전 설정

- [ ] CLAUDE.md 구성 (전역 + 프로젝트 + 하위 디렉토리)
- [ ] settings.json 권한 정의 (allow/deny)
- [ ] 필요한 도구용 MCP 서버 구성
- [ ] Skills 설치 (활성화 hooks 포함)
- [ ] 작업 유형별 Effort 레벨 사전 결정

### 프롬프트 구조

- [ ] 명확한 작업 정의 (해야 할 것)
- [ ] 컨텍스트 제공 (제약 조건, 배경)
- [ ] 역할 정의 (전문성, 페르소나)
- [ ] 출력 형식 지정 (XML 태그, JSON 스키마)
- [ ] 성공 기준 명시
- [ ] 예시 포함 (복잡한 경우 few-shot)

### Opus 4.5 설정

- [ ] Effort 레벨 선택:
  - [ ] Low: 간단한 작업, 속도 우선
  - [ ] Medium: 표준 작업 (기본값)
  - [ ] High: 복잡한 분석, 아키텍처
- [ ] Extended Thinking 구성:
  - [ ] Budget >= 1,024 토큰
  - [ ] 낮게 시작, 필요시 증가
  - [ ] Temperature 미설정 (비호환)

### 세션 관리

- [ ] 관련 없는 작업 간 `/clear`
- [ ] 복잡한 작업 전 토큰 사용량 확인
- [ ] ~176K 활성 컨텍스트 이하 유지
- [ ] 중요 변경 후 CLAUDE.md 업데이트
- [ ] 세션당 하나의 주요 작업

### 회피할 안티패턴

- [ ] "하지 마라" 지시 (긍정적 표현 사용)
- [ ] 거대한 단일 프롬프트 (단계별 분할)
- [ ] 검증 단계 생략
- [ ] Extended thinking과 temperature 조합
- [ ] 가정 (hooks로 결정론적 제어)

---

## 11. 참고 문헌

### Anthropic 공식 문서

| 문서 | URL | 날짜 |
|------|-----|------|
| Claude Code: Best Practices for Agentic Coding | https://www.anthropic.com/engineering/claude-code-best-practices | 2025-04-18 |
| Claude's Character | https://www.anthropic.com/research/claude-character | 2024-06-08 |
| Effective Context Engineering for AI Agents | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | - |
| Writing Effective Tools for AI Agents | https://www.anthropic.com/engineering/writing-tools-for-agents | - |
| Building with Extended Thinking | https://platform.claude.com/docs/en/build-with-claude/extended-thinking | - |
| Claude 4.x Prompting Best Practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices | - |

### Claude Code 문서

| 문서 | URL |
|------|-----|
| Settings | https://code.claude.com/docs/en/settings |
| Hooks Guide | https://code.claude.com/docs/en/hooks-guide |
| Hooks Reference | https://code.claude.com/docs/en/hooks |
| Skills | https://code.claude.com/docs/en/skills |
| Sub-agents | https://code.claude.com/docs/en/sub-agents |
| Slash Commands | https://code.claude.com/docs/en/slash-commands |

### MCP 사양

| 문서 | URL |
|------|-----|
| MCP Specification (2025-03-26) | https://modelcontextprotocol.io/specification/2025-03-26 |
| MCP Security Best Practices | https://modelcontextprotocol.io/specification/draft/basic/security_best_practices |
| MCP Architecture | https://modelcontextprotocol.io/docs/learn/architecture |

### SDK 및 리소스

| 리소스 | URL |
|--------|-----|
| MCP Python SDK | https://github.com/modelcontextprotocol/python-sdk |
| MCP Server Development Guide | https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md |
| Claude Code System Prompts | https://github.com/Piebald-AI/claude-code-system-prompts |

### 커뮤니티 리소스

| 리소스 | URL |
|--------|-----|
| Optimizing Token Efficiency in Claude Code Workflows | https://medium.com/@pierreyohann16/optimizing-token-efficiency-in-claude-code-workflows |
| Configuring MCP Tools in Claude Code | https://scottspence.com/posts/configuring-mcp-tools-in-claude-code |
| CLAUDE.md Best Practices (Arize) | https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/ |
| How to Make Claude Code Skills Activate Reliably | https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably |
| What Makes Claude Code So Good (MinusX) | https://minusx.ai/blog/decoding-claude-code/ |
| Claude Code Security Best Practices | https://www.backslash.security/blog/claude-code-security-best-practices |

---

## 부록: YAML Frontmatter 전체 비교표

| 유형 | 위치 | 파일명 규칙 | 필수 필드 | 주요 용도 |
|------|------|-------------|-----------|-----------|
| **Skills** | `.claude/skills/*/` | `SKILL.md` (고정) | `name`, `description` | 도메인 지식 주입 |
| **Agents** | `.claude/agents/` | `*.md` (자유) | `name`, `description` | 독립 작업 위임 |
| **Commands** | `.claude/commands/` | `*.md` (파일명=명령명) | 없음 | 프롬프트 재사용 |
| **Output Styles** | `.claude/output-styles/` | `*.md` (자유) | `name`, `description` | 응답 형식 변경 |
| **Project Rules** | `.claude/rules/` | `*.md` (자유) | 없음 | 조건부 규칙 적용 |

---

*이 문서는 `claudedocs/` 디렉토리의 14개 문서를 통합하여 작성되었습니다.*
*마지막 업데이트: 2026-01-05*
