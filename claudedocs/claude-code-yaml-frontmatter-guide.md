# Claude Code YAML Frontmatter 완전 가이드

Claude Code에서는 다양한 기능을 마크다운 파일과 YAML frontmatter를 통해 정의합니다. 이 문서는 모든 frontmatter 유형과 지원 필드를 정리한 종합 가이드입니다.

---

## 목차

1. [개요](#개요)
2. [Skills](#1-skills)
3. [Agents (Subagents)](#2-agents-subagents)
4. [Slash Commands](#3-slash-commands)
5. [Output Styles](#4-output-styles)
6. [Project Rules](#5-project-rules)
7. [Hookify Rules](#6-hookify-rules)
8. [Plugin Settings](#7-plugin-settings)
9. [전체 비교표](#전체-비교표)
10. [베스트 프랙티스](#베스트-프랙티스)

---

## 개요

Claude Code는 마크다운 파일의 YAML frontmatter를 활용하여 다양한 확장 기능을 정의합니다. Frontmatter는 파일 최상단에 `---`로 감싸진 YAML 블록입니다:

```markdown
---
name: example
description: This is an example
---

# 마크다운 본문 시작
```

### 공통 규칙

- **들여쓰기**: 2칸 스페이스 사용 (탭 사용 금지)
- **문자열**: 특수문자 포함 시 따옴표로 감싸기
- **멀티라인**: `|` 또는 `>` 사용

```yaml
# 멀티라인 예시
description: |
  여러 줄에 걸친
  설명을 작성할 수 있습니다.
```

---

## 1. Skills

Skills는 Claude에게 특정 도메인 전문성을 부여하는 재사용 가능한 지식 패키지입니다. **Progressive Disclosure** 원칙에 따라 frontmatter는 최소한의 메타데이터만 포함하고, 상세 지침은 본문에 작성합니다.

### 위치

| 범위 | 경로 |
|------|------|
| 프로젝트 | `.claude/skills/{skill-name}/SKILL.md` |
| 사용자 | `~/.claude/skills/{skill-name}/SKILL.md` |
| 플러그인 | `{plugin}/skills/{skill-name}/SKILL.md` |

> **주의**: 파일명은 반드시 `SKILL.md`여야 합니다.

### 지원 필드

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `name` | ✅ | string | 스킬 이름. 최대 64자, 소문자/숫자/하이픈만 허용 |
| `description` | ✅ | string | 스킬 설명. 최대 1024자. Claude가 스킬 선택 시 참조 |
| `allowed-tools` | ❌ | string | 사용 가능한 도구 제한 (쉼표로 구분) |
| `version` | ❌ | string | 버전 정보 (예: `"1.0.0"`) |
| `disable-model-invocation` | ❌ | boolean | `true`시 자동 호출 방지, `/skill-name`으로만 호출 |
| `mode` | ❌ | boolean | `true`시 "Mode Commands" 섹션에 별도 표시 |
| `dependencies` | ❌ | array | 필요한 소프트웨어 패키지 목록 |

### 예시

```markdown
---
name: code-review-standard
description: |
  Apply company code review standards. Use when reviewing PRs,
  checking code quality, or ensuring coding guidelines compliance.
allowed-tools: Read, Grep, Glob
version: "1.0.0"
---

# Code Review Standard

## Purpose
Ensure all code follows our team's quality standards.

## Review Checklist

1. **Naming Conventions**
   - Variables: camelCase
   - Constants: UPPER_SNAKE_CASE
   - Classes: PascalCase

2. **Error Handling**
   - All async functions must have try-catch
   - Custom error types for domain errors

3. **Test Coverage**
   - Minimum 80% coverage required
   - All edge cases must be tested

## Reference Files
- See `reference/style-guide.md` for detailed style rules
- Run `scripts/lint-check.py` for automated checks
```

### 고급: 도구 제한이 있는 스킬

```markdown
---
name: reading-files-safely
description: Read files without making changes. Use for read-only file access.
allowed-tools: Read, Grep, Glob
---

# Safe File Reader

This skill provides read-only file access.

## Instructions
1. Use `Read` to view file contents
2. Use `Grep` to search within files
3. Use `Glob` to find files by pattern

## Restrictions
- Never modify files
- Never execute bash commands
```

---

## 2. Agents (Subagents)

Agents는 독립적인 컨텍스트 윈도우와 시스템 프롬프트를 가진 특수 목적 AI 에이전트입니다. Claude가 자동으로 적절한 Agent에게 작업을 위임하거나, 사용자가 명시적으로 호출할 수 있습니다.

### 위치

| 범위 | 경로 | 우선순위 |
|------|------|:--------:|
| 프로젝트 | `.claude/agents/*.md` | 높음 |
| 사용자 | `~/.claude/agents/*.md` | 낮음 |
| 플러그인 | `{plugin}/agents/*.md` | - |

> **참고**: 이름 충돌 시 프로젝트 레벨이 우선합니다.

### 지원 필드

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `name` | ✅ | string | 에이전트 고유 식별자 |
| `description` | ✅ | string | 역할 및 사용 시점 설명. 자동 위임 결정에 사용 |
| `tools` | ❌ | string | 사용 가능한 도구 (쉼표로 구분). 생략 시 모든 도구 상속 |
| `model` | ❌ | string | 사용할 모델 (`claude-sonnet-4-5-20250929`, `inherit` 등) |
| `skills` | ❌ | array | 로드할 Skills 목록 |
| `color` | ❌ | string | UI 표시용 색상 |

### 예시: 기본 Agent

```markdown
---
name: test-runner
description: |
  Proactively run tests after code changes.
  Use this agent when tests need to be executed,
  failures need to be isolated, or test coverage needs verification.
tools: Read, Bash, Grep
model: inherit
---

You are a test automation specialist focused on quality assurance.

## Responsibilities

1. Run the appropriate test suite after any code modification
2. Isolate and diagnose test failures
3. Suggest minimal fixes that don't break other tests
4. Report test coverage metrics

## Workflow

1. Detect changed files with `git diff --name-only`
2. Identify related test files
3. Execute tests: `npm test` or `pytest`
4. Analyze failures and provide actionable fixes

## Output Format

```
## Test Results

**Status**: ✅ PASS / ❌ FAIL
**Coverage**: XX%

### Failed Tests (if any)
- test_name: error_message
  - Root cause: ...
  - Suggested fix: ...
```

## Constraints

- Never modify production code directly
- Always explain why a test failed before suggesting fixes
- Run tests in isolation to avoid side effects
```

### 예시: Skills를 참조하는 Agent

```markdown
---
name: fullstack-developer
description: |
  Full-stack development with design system and testing expertise.
  Use for complex features spanning frontend and backend.
tools: Read, Write, Bash, Grep, Glob
skills:
  - frontend-design-system
  - testing-patterns
  - api-conventions
---

You are a senior fullstack developer with expertise in both frontend and backend.

## Expertise Areas

- React/TypeScript frontend development
- Node.js/Python backend services
- Database design and optimization
- API design and documentation

## Working Style

1. Always start by understanding the full scope
2. Design before implementing
3. Write tests alongside code
4. Document public APIs
```

---

## 3. Slash Commands

Slash Commands는 재사용 가능한 프롬프트 템플릿으로, `/command-name`으로 호출합니다. 반복적인 작업을 단일 명령으로 캡슐화합니다.

### 위치

| 범위 | 경로 | 호출 방식 |
|------|------|----------|
| 프로젝트 | `.claude/commands/*.md` | `/command-name` (project) |
| 사용자 | `~/.claude/commands/*.md` | `/command-name` (user) |
| 플러그인 | `{plugin}/commands/*.md` | `/plugin:command-name` |

> **참고**: 파일명(확장자 제외)이 명령어 이름이 됩니다.

### 지원 필드

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `description` | ❌ | string | 명령어 설명. `/help`에 표시됨 |
| `allowed-tools` | ❌ | string | 허용할 도구와 패턴 |
| `argument-hint` | ❌ | string | 인자 힌트 (예: `[message]`) |
| `model` | ❌ | string | 사용할 모델 |
| `disable-model-invocation` | ❌ | boolean | `true`시 SlashCommand 도구로 자동 호출 방지 |

### 특수 문법

| 문법 | 설명 | 예시 |
|------|------|------|
| `$ARGUMENTS` | 전체 인자 | `/cmd hello world` → `hello world` |
| `$1`, `$2`, `$3` | 위치별 인자 | `/cmd a b c` → `$1=a`, `$2=b`, `$3=c` |
| `` !`command` `` | Bash 명령 실행 후 결과 삽입 | `` !`git status` `` |
| `@filepath` | 파일 내용 참조 | `@src/config.ts` |

### 예시: 기본 명령어

```markdown
---
description: Analyze code for performance issues and suggest optimizations
---

# Performance Analysis

Analyze the provided code for:

1. **Time Complexity**
   - Identify O(n²) or worse algorithms
   - Suggest optimizations

2. **Memory Usage**
   - Check for memory leaks
   - Identify unnecessary allocations

3. **Caching Opportunities**
   - Find repeated calculations
   - Suggest memoization points

## Output Format

For each issue found:
- Location (file:line)
- Current complexity
- Suggested improvement
- Example implementation
```

### 예시: Git 커밋 명령어 (Bash 통합)

```markdown
---
description: Create a conventional commit with staged changes
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*)
argument-hint: [commit-message]
model: claude-3-5-haiku-20241022
---

## Context

- Current status: !`git status --short`
- Staged changes: !`git diff --cached --stat`
- Recent commits: !`git log --oneline -5`

## Task

Create a conventional commit with the following message: $ARGUMENTS

## Requirements

1. Follow Conventional Commits format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `refactor:` - Code refactoring
   - `test:` - Adding tests

2. Keep subject line under 50 characters
3. Add body if changes are complex
4. Reference related issues if applicable

## Example

```
feat(auth): add OAuth2 login support

- Implement Google OAuth2 provider
- Add session management
- Update user model with provider field

Closes #123
```
```

### 예시: PR 리뷰 명령어 (다중 인자)

```markdown
---
description: Review pull request with priority and assignee
argument-hint: [pr-number] [priority] [assignee]
allowed-tools: Read, Grep, Glob
---

# PR Review Task

Review PR #$1 with priority **$2** and assign findings to **$3**.

## Review Focus Areas

1. **Security** (Critical)
   - Input validation
   - Authentication/Authorization
   - Sensitive data exposure

2. **Performance** (Based on priority: $2)
   - Database queries
   - API response times
   - Memory usage

3. **Code Quality**
   - Naming conventions
   - Code duplication
   - Test coverage

## Output Format

```markdown
## PR #$1 Review Summary

**Reviewer**: Claude
**Priority**: $2
**Assignee**: $3

### Critical Issues
- [ ] Issue 1

### Suggestions
- [ ] Suggestion 1

### Approved Items
- ✅ Item 1
```
```

---

## 4. Output Styles

Output Styles는 Claude Code의 시스템 프롬프트를 수정하여 응답 형식과 페르소나를 변경합니다. 소프트웨어 엔지니어링 외의 다른 목적으로 Claude Code를 사용할 때 유용합니다.

### 위치

| 범위 | 경로 |
|------|------|
| 프로젝트 | `.claude/output-styles/*.md` |
| 사용자 | `~/.claude/output-styles/*.md` |

### 지원 필드

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `name` | ✅ | string | 스타일 이름 (UI에 표시) |
| `description` | ✅ | string | 스타일 설명 |
| `keep-coding-instructions` | ❌ | boolean | `true`시 기본 코딩 지침 유지 |

### 사용 방법

```bash
# 스타일 선택 메뉴
/output-style

# 직접 스타일 지정
/output-style explanatory
```

### 예시: 기술 문서 작성자

```markdown
---
name: Technical Writer
description: Transform Claude into a documentation specialist focused on clear, structured technical writing.
keep-coding-instructions: false
---

# Technical Writer Mode

You are a technical documentation specialist. Your primary role is to help create clear, well-structured documentation.

## Core Behaviors

1. **Prioritize Clarity**
   - Use simple language
   - Avoid unnecessary jargon
   - Define technical terms on first use

2. **Structure First**
   - Always outline before writing
   - Use consistent heading hierarchy
   - Include table of contents for long documents

3. **Include Examples**
   - Every concept needs a concrete example
   - Use realistic scenarios
   - Show both correct and incorrect usage

## Output Format

- Use headers to organize content (H1 for title, H2 for sections, H3 for subsections)
- Include code snippets with proper syntax highlighting
- Add callouts for important information:
  - **Note:** for additional context
  - **Warning:** for potential issues
  - **Tip:** for helpful suggestions

## When Explaining Code

1. Start with a one-sentence summary of what the code does
2. Explain the "why" before the "how"
3. Include inline comments in code examples
4. Show input/output examples
```

### 예시: 학습 모드

```markdown
---
name: Learning Mode
description: Collaborative, learn-by-doing mode where Claude explains and guides rather than just solving.
keep-coding-instructions: true
---

# Learning Mode

You are a patient programming mentor focused on teaching through guided discovery.

## Teaching Philosophy

1. **Never Give Direct Answers First**
   - Ask guiding questions
   - Help the learner discover the solution
   - Explain the reasoning process

2. **Build Understanding**
   - Connect new concepts to familiar ones
   - Use analogies and metaphors
   - Break complex problems into smaller steps

3. **Encourage Experimentation**
   - Suggest experiments to try
   - Ask "What do you think would happen if...?"
   - Celebrate mistakes as learning opportunities

## Interaction Pattern

1. When asked a question:
   - Acknowledge the question
   - Ask a clarifying question to gauge understanding
   - Provide a hint or guiding question
   - Only after attempts, explain the concept

2. After solving a problem:
   - Ask the learner to explain it back
   - Suggest a variation to practice
   - Connect to related concepts

## Example Interaction

**User**: How do I reverse a string in Python?

**Response**: Great question! Before I show you, let me ask:
- Do you know how to access individual characters in a string?
- Have you worked with slicing before?

Let's start with a simple experiment. Try running this:
```python
text = "hello"
print(text[0])
print(text[-1])
```
What do you notice about `text[-1]`?
```

---

## 5. Project Rules

Project Rules는 CLAUDE.md를 여러 파일로 분리하여 관리할 수 있게 합니다. 특정 파일 패턴에만 적용되는 조건부 규칙을 지원합니다.

### 위치

| 범위 | 경로 |
|------|------|
| 프로젝트 | `.claude/rules/*.md` |
| 사용자 | `~/.claude/rules/*.md` |

> **참고**: 사용자 레벨 규칙이 먼저 로드되고, 프로젝트 레벨 규칙이 더 높은 우선순위를 가집니다.

### 지원 필드

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `paths` | ❌ | string | glob 패턴으로 적용 대상 파일 지정. 생략 시 모든 파일에 적용 |

### Glob 패턴 문법

| 패턴 | 설명 |
|------|------|
| `*.ts` | 현재 디렉토리의 모든 .ts 파일 |
| `**/*.ts` | 모든 하위 디렉토리의 .ts 파일 |
| `src/**/*.{ts,tsx}` | src 하위의 .ts 또는 .tsx 파일 |
| `!node_modules/**` | node_modules 제외 |

### 예시: TypeScript/React 규칙

```markdown
---
paths: src/**/*.{ts,tsx}
---

# TypeScript/React Rules

## Naming Conventions

| 항목 | 규칙 | 예시 |
|------|------|------|
| 컴포넌트 | PascalCase | `UserProfile.tsx` |
| Hooks | camelCase + `use` 접두사 | `useAuth.ts` |
| 유틸리티 | camelCase | `formatDate.ts` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 타입/인터페이스 | PascalCase | `UserData` |

## Component Structure

```tsx
// 1. Imports (React → Third-party → Local)
import React, { useState, useEffect } from 'react';
import { Button } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';

// 2. Type definitions
interface Props {
  userId: string;
  onUpdate: (user: User) => void;
}

// 3. Component definition
export const UserProfile: React.FC<Props> = ({ userId, onUpdate }) => {
  // hooks first
  const [user, setUser] = useState<User | null>(null);
  
  // effects
  useEffect(() => {
    // ...
  }, [userId]);
  
  // handlers
  const handleSubmit = () => {
    // ...
  };
  
  // render
  return (
    <div>
      {/* ... */}
    </div>
  );
};
```

## Required Practices

- Always use TypeScript strict mode
- Prefer `interface` over `type` for object shapes
- Use `const` assertions for literal types
- All props must have explicit types
```

### 예시: API 개발 규칙

```markdown
---
paths: src/api/**/*.ts
---

# API Development Rules

## Endpoint Structure

All API endpoints must follow this structure:

```typescript
// src/api/users/getUser.ts
import { z } from 'zod';
import { createHandler } from '@/lib/api';

// 1. Input validation schema
const inputSchema = z.object({
  userId: z.string().uuid(),
});

// 2. Output type
interface Output {
  user: User;
}

// 3. Handler with OpenAPI documentation
export const getUser = createHandler({
  method: 'GET',
  path: '/users/:userId',
  input: inputSchema,
  output: {} as Output,
  handler: async ({ input }) => {
    // Implementation
  },
});
```

## Required Elements

1. **Input Validation**: Use Zod schemas for all inputs
2. **Error Handling**: Use custom error types
3. **Documentation**: Include OpenAPI comments
4. **Logging**: Log all errors with context

## Response Format

```typescript
// Success
{ success: true, data: T }

// Error
{ success: false, error: { code: string, message: string } }
```
```

### 디렉토리 구조 예시

```
.claude/rules/
├── frontend/
│   ├── react.md          # React 컴포넌트 규칙
│   └── styles.md         # CSS/스타일링 규칙
├── backend/
│   ├── api.md            # API 개발 규칙
│   └── database.md       # 데이터베이스 규칙
├── testing.md            # 테스트 규칙 (전역)
└── security.md           # 보안 규칙 (전역)
```

---

## 6. Hookify Rules

Hookify는 공식 플러그인으로, JSON 대신 마크다운 파일로 간단하게 hooks를 정의할 수 있게 합니다. 패턴 매칭을 통해 특정 행동을 차단하거나 경고합니다.

### 위치

`.claude/hookify.{rule-name}.local.md`

> **주의**: `.local.md` 파일은 `.gitignore`에 추가하세요.

### 지원 필드

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `name` | ✅ | string | 규칙 식별자 |
| `enabled` | ✅ | boolean | 규칙 활성화 여부 |
| `event` | ✅ | string | 이벤트 유형 (아래 표 참조) |
| `pattern` | ❌ | string | regex 패턴 (단순 매칭 시) |
| `action` | ❌ | string | `block` 또는 `warn` (기본값: warn) |
| `conditions` | ❌ | array | 복합 조건 배열 |

### Event 유형

| Event | 설명 |
|-------|------|
| `bash` | Bash 명령 실행 시 |
| `file` | 파일 수정 시 |
| `prompt` | 사용자 프롬프트 입력 시 |
| `stop` | Claude 응답 완료 시 |
| `all` | 모든 이벤트 |

### Conditions 필드 구조

```yaml
conditions:
  - field: file_path | new_text | user_prompt | command
    operator: regex_match | contains | equals
    pattern: "패턴"
```

### 예시: 위험한 명령어 차단

```markdown
---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf\s+/
action: block
---

🛑 **위험한 rm 명령어 감지!**

루트 디렉토리를 대상으로 하는 `rm -rf` 명령은 시스템에 치명적인 손상을 줄 수 있습니다.

**대안:**
- 삭제 대상을 명시적으로 지정하세요
- `trash` 명령어 사용을 고려하세요
- 먼저 `ls`로 대상을 확인하세요
```

### 예시: TypeScript 파일의 console.log 경고

```markdown
---
name: warn-console-log-in-ts
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.tsx?$
  - field: new_text
    operator: contains
    pattern: console.log
action: warn
---

⚠️ **TypeScript 파일에 console.log 감지!**

프로덕션 코드에 디버그 로그가 포함되어 있습니다.

**권장사항:**
- 커밋 전에 제거하세요
- 로깅 라이브러리 사용을 고려하세요 (예: `winston`, `pino`)
- 조건부 디버그 빌드를 활용하세요:
  ```typescript
  if (process.env.NODE_ENV === 'development') {
    console.log(data);
  }
  ```
```

### 예시: 타입 안전성 강화

```markdown
---
name: block-as-any
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.tsx?$
  - field: new_text
    operator: regex_match
    pattern: as\s+any(?!\w)
action: block
---

🛑 **Unsafe `as any` cast detected!**

`as any`는 타입 안전성을 완전히 우회합니다.

**대안:**
- 적절한 타입 단언 사용: `value as SpecificType`
- 타입 가드 함수 생성
- 근본적인 타입 문제 해결

타입 시스템을 정말 우회해야 한다면, 그 이유를 주석으로 설명하세요.
```

### 예시: 완료 전 체크리스트

```markdown
---
name: completion-checklist
enabled: true
event: stop
pattern: .*
action: warn
---

## 작업 완료 전 확인사항

- [ ] 테스트가 실행되었나요?
- [ ] 빌드가 성공했나요?
- [ ] 문서가 업데이트되었나요?
- [ ] 불필요한 console.log가 제거되었나요?
```

---

## 7. Plugin Settings

플러그인별 설정을 저장하는 파일입니다. 각 플러그인이 사용자 설정을 읽어들이는 용도로 사용됩니다.

### 위치

`.claude/{plugin-name}.local.md`

> **주의**: `.local.md` 파일은 `.gitignore`에 추가하세요.

### 지원 필드

플러그인마다 다름 (각 플러그인이 스키마 정의)

### 예시

```markdown
---
enabled: true
mode: strict
max_retries: 3
auto_format: true
excluded_paths:
  - node_modules
  - dist
  - .git
custom_rules:
  - name: no-console
    severity: error
  - name: prefer-const
    severity: warn
---

# My Plugin Configuration

이 설정은 my-plugin의 동작을 제어합니다.

## 설정 설명

| 설정 | 설명 |
|------|------|
| `mode: strict` | 모든 규칙을 엄격하게 적용 |
| `auto_format` | 저장 시 자동 포맷팅 |

## 참고사항

- 설정 변경 후 Claude Code 재시작 필요
- `excluded_paths`는 glob 패턴 지원
```

---

## 전체 비교표

| 유형 | 위치 | 파일명 규칙 | 필수 필드 | 주요 용도 | 호출 방식 |
|------|------|-------------|-----------|-----------|-----------|
| **Skills** | `.claude/skills/*/` | `SKILL.md` (고정) | `name`, `description` | 도메인 지식 주입 | Claude 자동 감지 |
| **Agents** | `.claude/agents/` | `*.md` (자유) | `name`, `description` | 독립 작업 위임 | 자동 위임 / 명시적 호출 |
| **Slash Commands** | `.claude/commands/` | `*.md` (파일명=명령명) | 없음 | 프롬프트 재사용 | `/command-name` |
| **Output Styles** | `.claude/output-styles/` | `*.md` (자유) | `name`, `description` | 응답 형식 변경 | `/output-style` |
| **Project Rules** | `.claude/rules/` | `*.md` (자유) | 없음 | 조건부 규칙 적용 | 자동 로드 |
| **Hookify Rules** | `.claude/` | `hookify.{name}.local.md` | `name`, `enabled`, `event` | 패턴 기반 차단/경고 | 자동 실행 |
| **Plugin Settings** | `.claude/` | `{plugin}.local.md` | 플러그인별 상이 | 플러그인 설정 | 플러그인이 읽음 |

---

## 베스트 프랙티스

### 1. 파일 구조

```
.claude/
├── CLAUDE.md                      # 메인 프로젝트 지침
├── settings.json                  # 프로젝트 설정
├── settings.local.json            # 개인 설정 (gitignore)
│
├── agents/                        # Subagents
│   ├── code-reviewer.md
│   ├── test-runner.md
│   └── docs-writer.md
│
├── commands/                      # Slash Commands
│   ├── commit.md
│   ├── review.md
│   └── deploy.md
│
├── skills/                        # Skills
│   ├── api-design/
│   │   └── SKILL.md
│   └── testing/
│       └── SKILL.md
│
├── rules/                         # Project Rules
│   ├── typescript.md
│   ├── react.md
│   └── api.md
│
├── output-styles/                 # Output Styles
│   └── technical-writer.md
│
├── hookify.warn-console.local.md  # Hookify Rules
└── my-plugin.local.md             # Plugin Settings
```

### 2. 버전 관리

```gitignore
# .gitignore

# 개인 설정 (공유하지 않음)
.claude/*.local.md
.claude/*.local.json
.claude/settings.local.json

# 공유할 파일 (커밋)
# .claude/agents/
# .claude/commands/
# .claude/skills/
# .claude/rules/
# .claude/CLAUDE.md
```

### 3. Description 작성 가이드

```yaml
# ❌ 나쁜 예시
description: Does stuff with code

# ✅ 좋은 예시
description: |
  Analyze TypeScript code for security vulnerabilities.
  Use when: reviewing PRs, auditing codebases, or checking for
  common security issues like XSS, SQL injection, and auth bypasses.
```

### 4. 도구 제한 원칙

```yaml
# 최소 권한 원칙 적용
allowed-tools: Read, Grep, Glob    # 읽기 전용 작업
allowed-tools: Read, Write, Bash   # 수정 가능 작업

# 세부 제한
allowed-tools: Bash(git add:*), Bash(git commit:*)  # git 명령만 허용
```

### 5. 점진적 개선

1. **시작**: 간단한 Slash Command로 시작
2. **확장**: 자주 사용되면 Skill로 승격
3. **분리**: 독립 작업이 필요하면 Agent로 분리
4. **강화**: 실수 방지를 위해 Hookify Rule 추가

---

## 참고 자료

- [Claude Code 공식 문서](https://docs.anthropic.com/en/docs/claude-code)
- [Agent Skills 개요](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Subagents 문서](https://code.claude.com/docs/en/sub-agents)
- [Slash Commands 문서](https://code.claude.com/docs/en/slash-commands)
- [Output Styles 문서](https://code.claude.com/docs/en/output-styles)
- [Memory 관리 문서](https://code.claude.com/docs/en/memory)
- [Hooks 레퍼런스](https://code.claude.com/docs/en/hooks)
- [Hookify 플러그인](https://github.com/anthropics/claude-code/tree/main/plugins/hookify)

---

*이 문서는 2025년 1월 기준 Claude Code의 YAML frontmatter 사양을 정리한 것입니다. Claude Code는 빠르게 업데이트되므로 공식 문서를 함께 참조하세요.*
