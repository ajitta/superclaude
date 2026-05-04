---
paths: ["src/superclaude/skills/**", ".claude/rules/skill-authoring.md"]
---

# Skill Authoring Rules

> **House style note.** SuperClaude uses XML body for all authoring; this diverges from Anthropic's "no XML anywhere" guidance for skills. Decision rationale: `docs/research/rules-xml-conversion-ajitta-2026-04-14.md`. CC runtime accepts both forms; if redistributing a skill outside SuperClaude, prefer Markdown headings.

| Component | Role |
|-----------|------|
| Agent     | WHO TO BE |
| Command   | WHAT TO DO |
| Skill     | WHICH CAPABILITY |
| Mode      | HOW TO THINK |

> **Decision gate:** Create a skill when you need either:
> 1. **CC-native capability**: hooks, `disable-model-invocation`, `allowed-tools`, or script execution.
> 2. **Auto-invocation reference**: domain knowledge that should auto-trigger via CC description matching.
>
> Workflow procedures → `commands/`. Domain expertise → `agents/`. Cognitive overlays → `modes/`.

## Pick an Archetype First

| # | Archetype | Key fields | Use when |
|---|-----------|-----------|----------|
| ① | **Reference Skill** — auto-invoked | `description` (with trigger phrases folded in) | Domain knowledge should load when Claude sees matching keywords |
| ② | **Workflow Skill** — user-invoked | `disable-model-invocation: true`, optional `context: fork` + `agent:` | Workflow / explicit-invocation. Side-effect protection (deploy, release) OR delegation discipline (e.g., `simplicity-coach` reliably delegates to peer agent) |
| ③ | **Background Context** — Claude-only | `user-invocable: false` | Silent context injection, never shown in `/menu` |

```yaml
# ① Reference — minimal
---
name: api-conventions
description: >
  API 설계 패턴과 컨벤션 가이드. This skill should be used when working on
  REST endpoints, error formats, or API versioning.
---

# ② Workflow — side-effect protection
---
name: deploy
description: Production deployment automation.
disable-model-invocation: true
allowed-tools: Bash Read
argument-hint: "[environment]"
---

# ③ Background — silent
---
name: legacy-auth-context
description: Legacy auth system background knowledge.
user-invocable: false
---
```

## Directory Structure

```
src/superclaude/skills/my-skill/
├── SKILL.md          ← required (entrypoint)
├── scripts/          ← executable scripts (use {{SKILLS_PATH}} in command: strings)
├── references/       ← detailed content (progressive disclosure)
└── assets/           ← templates, binaries
```

Install paths (per `src/superclaude/cli/install_components.py:46-55`):
- `--scope user` (default): `src/superclaude/skills/ → ~/.claude/skills/` (absolute, posix-resolved).
- `--scope project` or `--scope local`: `src/superclaude/skills/ → ./.claude/skills/` (relative).

## YAML Frontmatter — Full Field Reference

All fields are **top-level**. `metadata:` is only for user-defined info (author, version) — never nest CC fields under it.

> *Annotations reflect actual usage as of 2026-04-25 across 5 shipped skills. Aspirational fields are kept for reference but marked.*

```yaml
---
# Identity
name: my-skill                    # recommended | lowercase+hyphens, ≤64 chars, matches directory name
description: >                    # recommended | ≤1024 chars (validator-friendly), ≤1,536 chars (CC listing cap, soft truncation)
  One-line purpose. This skill should be used when user mentions X, Y, Z.
  Front-load trigger phrases in the first ~200 chars.

# Invocation control
disable-model-invocation: true    # 3/5 shipped use this — block auto-invocation (side-effect skill)
user-invocable: false             # 0/5 shipped use this — hidden from /menu (Claude auto-invoke still possible)
argument-hint: "[arg]"            # 0/5 shipped use this — slash command autocomplete

# Execution
model: opus                       # 0/5 shipped use this — model override when skill active
effort: high                      # 0/5 shipped use this — low|medium|high|max; omit by default
allowed-tools: Read Grep Glob     # 1/5 shipped use this — space-separated permission-grant
paths: ["**/api/**"]              # 0/5 shipped use this — auto-load only on matching files
context: fork                     # 0/5 shipped use this — isolated subagent execution
agent: Explore                    # 0/5 shipped use this — only with context: fork

# Lifecycle hooks
hooks:                            # 2/5 shipped use this
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"

# Misc
metadata:                         # 0/5 shipped use this — user-defined info only (author, version, etc.)
  author: team-name
  version: "1.0.0"
---
```

> IDE가 `context`/`agent`/`hooks`에 경고를 표시해도 무시 — agentskills.io 표준 validator가 CC 확장 필드를 인식하지 못할 뿐 CC에서는 정상 동작.

## Field Rules (저작 시 가장 자주 틀리는 지점)

**1. `description` authoring pattern** — 가장 중요:
시작 시 모든 skill의 `name`+`description`이 시스템 프롬프트에 주입됨. 본문은 선택 후에야 읽힘.
- **Single field, third-person voice**: `description: <one-line purpose>. This skill should be used when <trigger contexts>.`
- **Trigger phrases first ~200 chars**: 자주 잘리므로 키워드는 앞쪽에.
- **Why one field, not two?** Anthropic의 canonical `skill-reviewer` 가 `when_to_use`를 deprecated 로 표시 (snake_case form). 프로젝트가 사용하던 hyphenated `when-to-use`는 CC parser 가 무시 (silent drop). 따라서 모든 트리거 키워드는 `description` 안으로 통합.

**2. Description budget** (CC runtime):
- 전체 skill/command description 합산: **1% of context window, fallback ~8,000 chars** (override via `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var)
- 개별 description: ≤1024 chars (agentskills.io validator-friendly), ≤1,536 chars (CC 2.1.105+ listing cap, soft truncation)
- 트리거 키워드는 첫 ~200 chars 안에 둘 것
- Anthropic 번들 skill 우선; custom skill이 먼저 잘림

**Naming taxonomy (parser literals — exact match required):**
- `kebab-case`: `disable-model-invocation`, `allowed-tools`, `user-invocable`, `argument-hint`
- `single-word`: `name`, `description`, `model`, `effort`, `version`, `paths`
- `snake_case`: only `when_to_use` — **deprecated by Anthropic, do not use**

CC parser uses literal key matching with mixed conventions; do not reflexively kebab-case everything.

**3. `disable-model-invocation` vs `user-invocable`** — 혼동 금지:

| 필드 | 효과 | 용도 |
|------|------|------|
| `disable-model-invocation: true` | Claude 자동 호출 차단 + 시스템 프롬프트에서 description 제거 | 배포/커밋 등 부작용 |
| `user-invocable: false` | `/menu` 미표시 (Claude 자동 실행은 가능) | 배경 지식 skill |

**4. `context: fork` + `agent:` 의존 관계**:
- `agent:`는 `context: fork`일 때만 동작 — `inline`이면 무시됨
- `context:` 기본값은 `inline` → 명시 불필요. `fork` 필요할 때만 둘 다 지정

**5. `allowed-tools` 최소 권한 템플릿** (space-separated; permission-grant, not access-restriction — non-listed tools remain callable but require user approval):
- 읽기 전용: `Read Grep Glob`
- 분석+검색: `Read Grep Glob WebSearch WebFetch`
- 구현: `Read Grep Glob Edit Write Bash`
- 생략 시 부모 전체 도구 상속

**6. Template variables** — 스크립트 경로는 반드시 사용 (in `command:` strings; `<references>` paths are project-relative and need no substitution):
- `{{SKILLS_PATH}}` → 설치된 skills 루트 (`~/.claude/skills/` user scope, `.claude/skills/` project/local scope)
- `{{SCRIPTS_PATH}}` → 설치된 scripts 경로
- `${CLAUDE_SKILL_DIR}` → Anthropic-portable runtime template var; expands to the skill's install dir regardless of how it was installed. Prefer this over `{{SKILLS_PATH}}` for skills redistributed via plugin marketplace, where install-time substitution may not fire.

**7. `name:` reserved words** — runtime fail:
- `name:` cannot contain `anthropic` or `claude`. Skills with reserved words silently fail to install. Per Anthropic's authoring guide.

## Body Structure (XML `<component>`)

> See top-of-file house-style note: this XML body convention diverges from Anthropic's guidance and is intentional.
> Conforms to `.claude/rules/xml-prose-format.md`: single root, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain**, **Labeled**, **Named** per item type), plural↔singular containers (`<examples><example>`) for multi-line items.

본문은 agent와 동일한 XML 패턴. 500줄 초과 시 `references/`로 분리.

```xml
<component name="skill-name" type="skill">

  <!-- Required tags: <role>, <gotchas>, <bounds>, <handoff> — appear in 5/5 shipped skills -->
  <!-- Optional tags: <references>, <syntax>, <flow>, <tools>, <examples> — skill-shape-dependent -->

  <role>                                                     <!-- required -->
    <mission>Single sentence purpose.</mission>
  </role>

  <references>                                               <!-- optional, load-on-demand -->
  - `references/file.md` — what it covers + when to load
  </references>

  <syntax>/skill-name [args] [--flags]</syntax>              <!-- optional -->

  <flow>                                                     <!-- optional -->
  1. Verb-leading description (≥2 steps; sequence is load-bearing).
  </flow>

  <tools>                                                    <!-- optional -->
  - ToolName: purpose
  </tools>

  <examples>                                                 <!-- optional -->
  | Trigger | Expected behavior |
  |---|---|
  | `/skill-name arg` | one-line response shape |
  | `/skill-name arg2` | another one-line shape |
  </examples>

  <gotchas>                                                  <!-- required -->
  - pattern-name: 구체적 실패 + 행동 지침 (2-5 items)
  </gotchas>

  <bounds>                                                   <!-- required -->
    <does>core capabilities described in prose (in-scope).</does>
    <never>out-of-scope actions described in prose.</never>
    <fallback>optional — skills are short-lived; implicit fallback is "skill ends, control returns to caller". Use only if the recovery posture is non-obvious.</fallback>
  </bounds>
  <handoff next="/sc:next1 /sc:next2"/>                      <!-- required -->
</component>
```

Required tags appear in 5/5 shipped skills. Optional tags are skill-shape-dependent.

### Body rules
- `type="skill"` 필수 (agent와 구분)
- All multi-word tag names use `snake_case`
- Short enums: **Numbered** (`1.` for ordered procedures: `<flow>`), **Labeled** (`- Label:` fixed-set labels: `<tool_guidance>` Proceed/Ask First/Never), **Named** (`- identifier-name:` per-item identifiers: `<references>`, `<tools>`, `<gotchas>`)
- `<examples>` — compact markdown table with minimal separators `|---|---|` for short uniform rows. For richer illustrations (code blocks, narrative, multi-turn prose), use a standalone `<example>` tag — its body is free-form prose, not locked to a `user:` / `assistant:` shape. `<examples>` and `<example>` are two distinct constructs (see xml-prose-format.md).
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each tag's body is a prose sentence). `<does>` + `<never>` required; `<fallback>` optional. Skills are short-lived — implicit fallback is "skill ends, control returns to caller". Use explicit `<fallback>` only if the recovery posture is non-obvious. Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>` (commit `S390` measured Claude conflating the two when both used `- Label:` lines).
- `<gotchas>` — **프로젝트 특유** 실패 패턴만 (force-push 금지 같은 일반론은 hooks로). 분기별 리뷰, 90일 미트리거 항목 제거
- 본문 ≤500 lines. 상세 내용은 `references/`로 분리

## Inherited from xml-prose-format.md

The following rules apply to all components and are not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs and model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when the illustration mirrors a real markdown artifact (report template, commit message, user document); the body-prose "no markdown headers" rule does not extend into `<example>` bodies.
- **Size target** — skill body ≤500 lines (matches Anthropic guidance); extract overflow into `references/` sibling files (progressive disclosure).

## Validation Checklist

1. `name` == 디렉토리명
2. `description` ≤1024 chars (validator-friendly) / ≤1,536 chars (CC listing cap), trigger phrases in first ~200 chars, third-person voice
3. CC 확장 필드(`context`/`agent`/`hooks`)는 top-level, metadata 아래 금지
4. 부작용 skill은 `disable-model-invocation: true`
5. 스크립트 경로는 `{{SKILLS_PATH}}` 사용 (하드코딩 금지)
6. `<bounds>` has `<does>` + `<never>` (legacy `<should>`/`<avoid>` rejected by structure tests)
7. 본문 ≤500 lines
8. `make deploy` 후 `/skill-name`으로 실제 호출 테스트

## Style Recommendations (optional / advisory)

- **Gerund naming.** Prefer `processing-pdfs` over `pdf-processor`. Anthropic's authoring guide leans gerund.
- **Reference-file ToC.** If a `references/*.md` file exceeds 100 lines, add a table-of-contents at the top.
- **Time-sensitive content.** Wrap "old patterns" in `<details>` collapsible blocks so they don't dominate context.

## Runtime Quirks (CC version-pinned)

<!-- last reviewed: 2026-04-25; verify quarterly, remove fixed issues -->

These are CC runtime bugs verified open as of 2026-04-25. They affect skill behavior at runtime, not authoring correctness. Re-verify quarterly.

- **#17688** — Skill-scoped hooks defined in SKILL.md frontmatter are not triggered within plugins. https://github.com/anthropics/claude-code/issues/17688
- **#40630** — Skill-scoped hooks not propagated to forked subagent when `context: fork` is set. https://github.com/anthropics/claude-code/issues/40630
- **#30874** — Skill-scoped PreToolUse hooks persist after the skill completes. https://github.com/anthropics/claude-code/issues/30874

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
| 장식용 XML `note=` 속성 | 미파싱 boilerplate, 토큰 낭비 | xml-prose-format.md "Attributes vs. Body" 참조 — scope/safety/version/reference/quantified constraint일 때만 허용 |
