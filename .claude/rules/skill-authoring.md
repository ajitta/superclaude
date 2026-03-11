# Skill Authoring Rules

When creating or modifying skill files in `src/superclaude/skills/`, follow these rules exactly.

## Directory Structure

```
src/superclaude/skills/
└── my-skill/
    ├── SKILL.md          ← 필수 (entrypoint)
    ├── scripts/          ← 실행 스크립트 (Python, Bash 등)
    ├── references/       ← 문서, 참조자료
    └── assets/           ← 템플릿, 바이너리
```

Install path: `src/superclaude/skills/ → ~/.claude/skills/`

## YAML Frontmatter

All fields are **top-level**. Source: `code.claude.com/docs/en/skills` (official Claude Code documentation).

The `metadata:` key is only for arbitrary user-defined key-value pairs (author, version, etc.) — NOT for nesting CC extension fields.

IDE warnings for `context`, `agent`, `hooks` are from the agentskills.io standard validator which doesn't recognize CC extension fields. These warnings are safe to ignore.

### Field Reference (all top-level)

```yaml
---
# Standard fields (agentskills.io cross-platform)
name: my-skill                    # 권장 | lowercase+hyphens, max 64자, 디렉토리명과 일치
description: |                    # 권장 | Claude 자동 invocation 판단 핵심, max 1024자
  What this skill does and when to trigger it.
  Include task keywords for better auto-detection.
license: MIT                      # 선택 | 라이선스 명시
compatibility:                    # 선택 | 환경 요구사항 (실험적)
  tools: [claude-code]
  requires: [python3]
allowed-tools: Read, Grep, Glob   # 선택 | 허용 툴 화이트리스트 (실험적)
disable-model-invocation: true    # 선택 | Claude 자동 호출 차단
metadata:                         # 선택 | author, version 등 부가 정보만
  author: team-name
  version: "1.0.0"

# Claude Code extension fields (CC에서만 동작, 다른 툴은 무시)
user-invocable: false             # 선택 | /menu 노출 여부 (UI only)
argument-hint: "[issue-number]"   # 선택 | slash command 자동완성 힌트
model: opus                       # 선택 | skill 활성 시 사용 모델
context: fork                     # 선택 | fork = subagent 격리 실행
agent: Explore                    # 선택 | subagent 타입 (context와 함께)
hooks:                            # 선택 | 생애주기 훅
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
---
```

### Field Placement Summary

| Field | Placement | Category | Source |
|-------|-----------|----------|--------|
| `name` | top-level | 표준 | agentskills.io |
| `description` | top-level | 표준 | agentskills.io |
| `license` | top-level | 표준 | agentskills.io |
| `compatibility` | top-level | 표준 (실험적) | agentskills.io |
| `allowed-tools` | top-level | 표준 (실험적) | agentskills.io |
| `disable-model-invocation` | top-level | 표준 | agentskills.io |
| `metadata` | top-level (container) | 표준 | agentskills.io |
| `user-invocable` | top-level | CC 전용 | code.claude.com |
| `argument-hint` | top-level | CC 전용 | code.claude.com |
| `model` | top-level | CC 전용 | code.claude.com |
| `context` | top-level | CC 전용 | code.claude.com |
| `agent` | top-level | CC 전용 | code.claude.com |
| `hooks` | top-level | CC 전용 | code.claude.com |

### Field Rules

**`description` 작성 원칙** — 가장 중요한 필드:
- 시작 시 모든 skill의 name+description만 시스템 프롬프트에 주입됨
- Claude는 이것만 보고 skill 활성화 여부를 결정
- SKILL.md 본문은 skill이 선택된 후에야 읽힘
- 구체적 태스크 + 트리거 키워드 명시, 모호한 설명 금지

```yaml
# Bad — too vague
description: 코드 관련 도움을 줍니다.

# Good — task + keywords + triggers
description: |
  PR 및 커밋된 코드의 품질, 보안, 유지보수성을 검토.
  코드 리뷰, PR 피드백, 버그 탐지 요청 시 사용.
```

**`disable-model-invocation` vs `user-invocable`** — 혼동 금지:
| 필드 | 효과 | 용도 |
|------|------|------|
| `disable-model-invocation: true` | Claude 자동 호출 완전 차단 + 시스템 프롬프트에서 description 제거 | 배포, 커밋 등 부작용 워크플로우 |
| `user-invocable: false` | `/menu` 미표시 (Claude 자동 실행은 가능, description은 context에 유지) | 배경 지식 skill |

**`context` + `agent`** — 의존 관계:
- `agent:` 필드는 `context: fork`일 때만 동작 — subagent 타입 지정
- `context: inline`이면 `agent:` 무시됨 — 불필요한 필드 포함 금지
- `context:` 미지정 시 기본값은 inline — 대부분의 skill은 `context`/`agent` 불필요
- `context: fork` 사용 시에만 `agent:` 추가 (예: `agent: Explore`)

```yaml
# WRONG — agent without context: fork is meaningless
context: inline
agent: general-purpose   # ← 무시됨, 제거해야 함

# CORRECT — agent with context: fork
context: fork
agent: Explore           # ← fork subagent 타입 지정

# CORRECT — inline skill needs neither
# (context/agent 필드 자체를 생략)
```

**`allowed-tools`** — 최소 권한:
- 읽기 전용: `Read, Grep, Glob`
- 분석 + 검색: `Read, Grep, Glob, WebSearch, WebFetch`
- 구현: `Read, Grep, Glob, Edit, Write, Bash`
- 미지정 시 전체 도구 상속

**`metadata`** — author, version 등 부가 정보 전용:
```yaml
# Correct — metadata for user-defined info only
metadata:
  author: backend-team
  version: "2.0.0"

# WRONG — do NOT nest CC fields under metadata
metadata:
  context: fork    # ← WRONG, must be top-level
  agent: Explore   # ← WRONG, must be top-level
```

**Template variables** — 스크립트 경로에 사용:
| 변수 | 해석 |
|------|------|
| `{{SKILLS_PATH}}` | 설치된 skills 루트 경로 (`~/.claude/skills/`) |
| `{{SCRIPTS_PATH}}` | 설치된 scripts 경로 |

**IDE warnings** — agentskills.io validator가 CC 전용 필드(`context`, `agent`, `hooks`)를 인식 못해 경고 표시. Claude Code에서 정상 동작하므로 무시.

## Body Structure (SuperClaude Convention)

Skill 본문은 agent와 동일한 XML `<component>` 패턴을 사용합니다.

```xml
<component name="skill-name" type="skill">

  <role>
    <mission>Single sentence purpose</mission>
  </role>

  <syntax>/skill-name [args] [--flags]</syntax>

  <flow>
    1. Step one
    2. Step two
    3. Step three
  </flow>

  <tools>
    - ToolName: purpose
  </tools>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/skill-name arg` | Expected result |
  </examples>

  <bounds will="core capabilities" wont="out-of-scope actions"/>

  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### Body Rules

- `<component type="skill">` — agent와 구분, `type="skill"` 필수
- `<syntax>` — slash command 사용법 명시
- `<flow>` — 번호 매긴 실행 순서
- `<bounds>` — `will`/`wont` 속성 필수
- 본문 500줄 이내, 세부 내용은 `references/`로 분리

## Three Archetypes

### ① Reference Skill (자동 invocation)
```yaml
---
name: api-conventions
description: |
  API 설계 패턴과 컨벤션 가이드.
  API 엔드포인트 작성, REST 설계, 에러 포맷 작업 시 자동 적용.
---
```
- `disable-model-invocation` 미설정 (Claude가 자동 호출)
- `user-invocable` 미설정 (기본 true)

### ② Workflow Skill (사용자 전용 호출)
```yaml
---
name: deploy
description: 프로덕션 배포 자동화.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[environment]"
context: fork
agent: general-purpose
---
```
- `disable-model-invocation: true` — 부작용 보호
- `context: fork` — top-level

### ③ Background Context Skill (Claude만 사용)
```yaml
---
name: legacy-auth-context
description: |
  레거시 인증 시스템 배경 지식.
  인증 관련 코드 수정 시 자동 로드.
user-invocable: false
---
```
- `user-invocable: false` — `/menu` 미표시
- Claude가 필요시 자동 활성화

## Validation Checklist

After creating/modifying a skill:

1. `name` matches directory name
2. `description` is specific (task + keywords), max 1024자
3. All CC extension fields (`context`, `agent`, `hooks`) are top-level (NOT under `metadata:`)
4. `metadata:` contains only user-defined info (author, version)
5. Side-effect skills have `disable-model-invocation: true`
6. Scripts use `{{SKILLS_PATH}}` template variable (not hardcoded paths)
7. Body under 500 lines
8. `<bounds>` has `will`/`wont` attributes
9. Run `make deploy` to install
10. Test with `/skill-name` to verify invocation

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| Nesting `context:` under `metadata:` | CC reads top-level only | Move to top level |
| Nesting `agent:` under `metadata:` | CC reads top-level only | Move to top level |
| Nesting `hooks:` under `metadata:` | CC reads top-level only | Move to top level |
| `agent:` without `context: fork` | `agent` is ignored when context is inline | Remove `agent:` or change to `context: fork` |
| `context: inline` explicitly set | inline is the default, redundant | Remove `context:` field entirely |
| Vague description | Claude won't auto-trigger | Add task + trigger keywords |
| Hardcoded script paths | Breaks on install | Use `{{SKILLS_PATH}}` |
| Body > 500 lines | Context bloat | Split to `references/` |
| Missing `disable-model-invocation` on deploy/push skills | Claude may auto-execute destructive actions | Add `disable-model-invocation: true` |
| Using `user-invocable: false` to block Claude | Only hides from `/menu`, Claude still auto-calls | Use `disable-model-invocation: true` instead |
