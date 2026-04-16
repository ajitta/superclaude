# Skill Authoring Rules

> **Decision gate:** Create a skill when you need either:
> 1. **CC-native capability**: hooks, `disable-model-invocation`, `allowed-tools`, or script execution.
> 2. **Auto-invocation reference**: domain knowledge that should auto-trigger via CC description matching.
>
> Workflow procedures → `commands/`. Domain expertise → `agents/`. Cognitive overlays → `modes/`.

## Pick an Archetype First

| # | Archetype | Key fields | Use when |
|---|-----------|-----------|----------|
| ① | **Reference Skill** — auto-invoked | `description` + `when-to-use` | Domain knowledge should load when Claude sees matching keywords |
| ② | **Workflow Skill** — user-invoked | `disable-model-invocation: true`, optional `context: fork` + `agent:` | Side-effect operations (deploy, release). Protect from auto-trigger |
| ③ | **Background Context** — Claude-only | `user-invocable: false` | Silent context injection, never shown in `/menu` |

```yaml
# ① Reference — minimal
---
name: api-conventions
description: API 설계 패턴과 컨벤션 가이드.
when-to-use: >
  REST 엔드포인트 작성, 에러 포맷, API 버전 관리 시 자동 적용.
---

# ② Workflow — side-effect protection
---
name: deploy
description: 프로덕션 배포 자동화.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[environment]"
---

# ③ Background — silent
---
name: legacy-auth-context
description: 레거시 인증 시스템 배경 지식.
user-invocable: false
---
```

## Directory Structure

```
src/superclaude/skills/my-skill/
├── SKILL.md          ← 필수 (entrypoint)
├── scripts/          ← 실행 스크립트 (use {{SKILLS_PATH}} in refs)
├── references/       ← 세부 내용 (progressive disclosure)
└── assets/           ← 템플릿, 바이너리
```

Install path: `src/superclaude/skills/ → ~/.claude/skills/`.

## YAML Frontmatter — Full Field Reference

All fields are **top-level**. `metadata:` is only for user-defined info (author, version) — never nest CC fields under it.

```yaml
---
# Identity
name: my-skill                    # 권장 | lowercase+hyphens, ≤64자, 디렉토리명과 일치
description: One-line purpose.    # 권장 | ≤1,536 chars (CC 2.1.105+ listing cap, 초과 시 기동 경고)
when-to-use: >                    # 권장 | 트리거 키워드/시나리오
  When user mentions X, Y, Z.

# Invocation control
disable-model-invocation: true    # 자동 호출 완전 차단 (부작용 skill)
user-invocable: false             # /menu 미표시 (Claude 자동 실행은 가능)
argument-hint: "[arg]"            # slash command 자동완성

# Execution
model: opus                       # skill 활성 시 모델 override
effort: high                      # low|medium|high|max 추론 깊이
allowed-tools: Read, Grep, Glob   # 최소 권한 화이트리스트
context: fork                     # subagent 격리 실행
agent: Explore                    # fork 시 subagent 타입

# Lifecycle hooks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"

# Misc
metadata:                         # author/version 등 부가 정보 전용
  author: team-name
  version: "1.0.0"
---
```

> IDE가 `context`/`agent`/`hooks`에 경고를 표시해도 무시 — agentskills.io 표준 validator가 CC 확장 필드를 인식하지 못할 뿐 CC에서는 정상 동작.

## Field Rules (저작 시 가장 자주 틀리는 지점)

**1. `description` vs `when-to-use` 분리** — 가장 중요:
시작 시 모든 skill의 name+description+when-to-use가 시스템 프롬프트에 주입됨. 본문은 선택 후에야 읽힘.
- `description`: "무엇" (한 줄 요약)
- `when-to-use`: "언제" (트리거 키워드 집중)

**2. Description budget** (CC runtime):
- 전체 skill/command description 합산 ~15,000 chars (`SLASH_COMMAND_TOOL_CHAR_BUDGET`)
- 개별 description은 listing에서 ~1,536 chars로 잘림 (CC 2.1.105+, 이전 cap 250) — 트리거 키워드는 여전히 첫 100 chars 안에 두는 것이 권장
- Anthropic 번들 skill 우선, custom skill이 먼저 잘림

**3. `disable-model-invocation` vs `user-invocable`** — 혼동 금지:

| 필드 | 효과 | 용도 |
|------|------|------|
| `disable-model-invocation: true` | Claude 자동 호출 차단 + 시스템 프롬프트에서 description 제거 | 배포/커밋 등 부작용 |
| `user-invocable: false` | `/menu` 미표시 (Claude 자동 실행은 가능) | 배경 지식 skill |

**4. `context: fork` + `agent:` 의존 관계**:
- `agent:`는 `context: fork`일 때만 동작 — `inline`이면 무시됨
- `context:` 기본값은 `inline` → 명시 불필요. `fork` 필요할 때만 둘 다 지정

**5. `allowed-tools` 최소 권한 템플릿**:
- 읽기 전용: `Read, Grep, Glob`
- 분석+검색: `Read, Grep, Glob, WebSearch, WebFetch`
- 구현: `Read, Grep, Glob, Edit, Write, Bash`
- 생략 시 부모 전체 도구 상속

**6. Template variables** — 스크립트 경로는 반드시 사용:
- `{{SKILLS_PATH}}` → 설치된 skills 루트 (`~/.claude/skills/`)
- `{{SCRIPTS_PATH}}` → 설치된 scripts 경로

## Body Structure (XML `<component>`)

본문은 agent와 동일한 XML 패턴. 500줄 초과 시 `references/`로 분리.

```xml
<component name="skill-name" type="skill">

  <role>
    <mission>Single sentence purpose</mission>
  </role>

  <references note="Load on demand — progressive disclosure">
  - `references/file.md` — What + when to read
  </references>

  <syntax>/skill-name [args] [--flags]</syntax>

  <flow>
    1. Step one
    2. Step two
  </flow>

  <tools>
    - ToolName: purpose
  </tools>

  <gotchas>
  - pattern-name: 구체적 실패 + 행동 지침 (2-5 items)
  </gotchas>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/skill-name arg` | Expected result |
  </examples>

  <bounds should="core capabilities" avoid="out-of-scope actions"/>
  <handoff next="/sc:next1 /sc:next2"/>
</component>
```

### Body rules
- `type="skill"` 필수 (agent와 구분)
- `<bounds>` — `should`/`avoid` 속성 필수
- `<gotchas>` — **프로젝트 특유** 실패 패턴만 (force-push 금지 같은 일반론은 hooks로). 분기별 리뷰, 90일 미트리거 항목 제거
- 본문 ≤500 lines. 상세 내용은 `references/`로 분리

## Validation Checklist

1. `name` == 디렉토리명
2. `description` + `when-to-use` 분리, 합쳐서 ≤1,536 chars (CC 2.1.105+ listing cap)
3. CC 확장 필드(`context`/`agent`/`hooks`)는 top-level, metadata 아래 금지
4. 부작용 skill은 `disable-model-invocation: true`
5. 스크립트 경로는 `{{SKILLS_PATH}}` 사용 (하드코딩 금지)
6. `<bounds>` has `should` + `avoid`
7. 본문 ≤500 lines
8. `make deploy` 후 `/skill-name`으로 실제 호출 테스트

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| `context`/`agent`/`hooks`를 `metadata:` 아래 중첩 | CC는 top-level만 읽음 | top-level로 이동 |
| `agent:` without `context: fork` | inline에서는 무시됨 | `agent:` 제거 또는 `context: fork` 추가 |
| `context: inline` 명시 | 기본값이라 redundant | 필드 제거 |
| Vague description | Claude 자동 트리거 실패 | 핵심 작업 + 트리거 키워드 first 100 chars |
| Hardcoded script paths | 설치 후 깨짐 | `{{SKILLS_PATH}}` |
| Body > 500 lines | Context bloat | `references/`로 분리 |
| Deploy/push skill에 `disable-model-invocation` 누락 | Claude 자동 실행 위험 | `disable-model-invocation: true` |
| `user-invocable: false`로 Claude 차단 시도 | /menu만 가림, 자동 호출은 여전히 가능 | `disable-model-invocation: true`로 교체 |
| 모든 내용 SKILL.md 인라인 | Level 2 로딩 시 bloat | `<references>` + `references/` |
| 일반론 gotcha ("force-push 금지") | gotcha 신호 낭비 | 일반 안전규칙은 hooks, gotcha는 프로젝트 특유만 |
| 장식용 XML `note=` 속성 | 미파싱 boilerplate, 토큰 낭비 | `note=`는 scope/safety/version/reference/quantified constraint일 때만 허용 |
