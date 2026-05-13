---
paths: ["src/superclaude/agents/**", ".claude/rules/agent-authoring.md"]
---

# Agent Authoring Rules

> **Decision gate.** Make agent for **domain expertise** that CC auto-delegate on description match.
> - Agent = **WHO TO BE** (domain expert persona)
> - Command = **WHAT TO DO** (user-invoked workflow)
> - Skill = **WHICH CAPABILITY** (CC-native tool/hook)
> - Mode = **HOW TO THINK** (cognitive overlay)

> **What CC load.** Subagent session hold only markdown body (system prompt) plus min env context — *not* parent CC system prompt, *not* parent skills. Write body self-contained. Subagent no spawn more subagents (only main thread can, via `--agent` + `Agent` in `tools`); design each agent return one summary, no nested delegation.

> **No recreate built-ins.** CC ship `Explore` (read-only codebase search, Haiku), `Plan` (read-only research for plan mode), `general-purpose` (full-tool multi-step), `statusline-setup`, `Claude Code Guide`. New SuperClaude agent must add domain-specific value past these; agent that just "search codebase" or "research before act" duplicate `Explore`/`Plan` and bloat registry.

> **Body run two modes.** Same file run as delegated subagent (body = system prompt for isolated session) OR as whole session via `claude --agent <name>` (body replace CC default system prompt). Write body read coherent both modes — no phrasing that assume parent ("when delegated to you", "the calling Claude"); prefer persona statements ("Claude operates as …", "the agent's mission is …").

## YAML Frontmatter

CC need only `name` + `description`. Rest optional, inherit from parent. SuperClaude also need `memory` + `color` for installer.

```yaml
---
# Required by CC
name: agent-name                            # lowercase letters and hyphens; matches filename
description: Expert X. Use proactively for Y. Use immediately after Z.

# Required by SuperClaude
memory: project                             # source value always "project"; installer rewrites to user/local per scope
color: blue                                 # role-group mapping below

# Optional — omit to inherit from parent session
model: inherit                              # inherit | sonnet | opus | haiku | full ID (e.g. claude-opus-4-7). Default: inherit
permissionMode: default                     # default | acceptEdits | auto | dontAsk | bypassPermissions | plan
tools: Read, Grep, Glob, Agent              # allow-list (comma-separated)
disallowedTools: Edit, Write                # deny-list (applied first, then `tools` resolved against remainder)
effort: high                                # low | medium | high | xhigh | max  (string, not 1-5)
maxTurns: 20                                # positive integer turn cap
skills: [confidence-check]                  # full skill body injected at startup; subagent does NOT inherit parent skills
mcpServers: [serena]                        # references to configured servers, or inline definitions

# Advanced — rarely set in SuperClaude agents
hooks:                                      # PreToolUse / PostToolUse / Stop scoped to this subagent (see CC hooks docs for structure)
background: false                           # always run as a background task
isolation: worktree                         # spawn in a temporary git worktree (isolated repo copy)
initialPrompt:                              # auto-submitted as first user turn when run as main session via --agent
---
```

### Description writing

CC read `description` verbatim to decide delegation. Two parts:

- **Persona** — noun phrase name the expert ("Expert code reviewer", "Debugging specialist for errors and test failures").
- **Trigger phrase** — when to delegate, in CC idiom: *"Use proactively for X."*, *"Use immediately after Y."*, *"Use when Z."*

Skip emoji, version tag, colon-prefix keyword list — description is sentence read by parent classifier; write sentence. Legacy `(triggers - kw1, kw2)` shorthand parse but classify less reliable than CC-idiom sentence. One to three sentences total; longer description improve delegation accuracy, cost nothing at runtime.

Canonical patterns (from CC docs):
- `Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.`
- `Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.`
- `Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.`

#### Vocabulary cautions

Description sentence read verbatim into subagent system prompt header — word shift measurably change behavior. Empirical findings from agent-naming experiment series (107 trials, see `docs/research/2026-05-06-agent-naming-findings/`):

- **No past-implying phrasing.** `following X practices`, `deep production experience`, `pragmatic tradeoff judgment` — these prime "continuation of prior work" frame, produce 5/5 and 3/3 context-hallucination rates on long-output tasks (subagent fabricate preexisting files, prior fixes, even narrate edits to own definition file). `engineer` and `senior-python-engineer` rename pairs break from this alone, body unchanged.
- **Prefer forward-looking voice.** `learning to apply X`, `grounded in X`, `with deep mastery and seasoned judgment` — these no trigger failure mode (0/3 hallucinations).
- **Description is lever for over-engineering.** Add Zen-of-Python clause ("simple is better than complex; values minimal solutions, the smallest abstraction; code that any junior can read") to same agent name reduce over-engineering signals 25–73% (chars −25%, classes −58%, decorators −65%, TypeVar −100% across 15 trials). Use this lever before rename if goal is anti-overengineering.
- **`hypothesis`-style advanced patterns sticky** — directive phrasing only reduce unprompted property-based test usage ~20%. Some priors need explicit prohibition (`Do not use property-based testing libraries unless asked.`) not soft directive.

### Field reference

**Forbidden in source.** `autonomy` (not CC field). Any field not in CC documented agent spec.

**Tool access.** Five canonical patterns:

| Pattern | Field | Value | When |
|---------|-------|-------|------|
| Read-only + web | `tools` | `Read, Grep, Glob, Agent, WebSearch, WebFetch` | Plan/review/research (fails closed — **preferred**) |
| Read-only minimal | `tools` | `Read, Grep, Glob, Agent` | No web access needed |
| Execute-only | `disallowedTools` | `Edit, Write, NotebookEdit` | Runs commands, never edits files (e.g., git-workflow) |
| General | `disallowedTools` | `NotebookEdit` | Code edits OK, no notebook edits |
| Full access | *(omit both)* | — | Implementation agents |

CC permit both `tools` and `disallowedTools` together (deny applied first, then allow resolved against remaining pool — tool listed in both is removed). **SuperClaude convention: pick one form per agent for readability — never mix.**

**Spawn restrictions (orchestrators only).** `tools: Agent(worker, researcher)` allow-list which subagent types can spawn. Take effect only when agent run as main thread (`claude --agent <name>`); no effect inside regular subagent (subagent no spawn subagent). Bare `Agent` allow any; omit `Agent` from `tools` disable spawning entirely.

**`effort`** (CC v2.1.69+) — **omit by default.** Inherit from parent unless measured evidence show specific value materially change output for agent domain. String values only; `xhigh` need Opus 4.7 + CC 2.1.111+; `max` need Opus 4.6/4.7.

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` env > frontmatter > session > model default.

When `xhigh` worth setting (Opus 4.7+): Anthropic recommend `xhigh` as baseline for coding/agentic work — at `low`/`medium`, Opus 4.7 under-think edge cases. Two safe paths:
1. **Session-level (preferred).** `CLAUDE_CODE_EFFORT_LEVEL=xhigh` or pick `xhigh` at session start — uniform, respect user cost-vs-quality choice.
2. **Agent-level override.** `effort: xhigh` only when measured quality regression at session default justify it.

No add `effort: xhigh` because domain "feels" coding-heavy — session default cover that. Inherit-by-default keep cost control with user (commit `8edd05d`).

**`maxTurns`** — turn-limit safety net:

| Category | maxTurns | When |
|----------|----------|------|
| Quick | 10 | Scanning, mechanical ops |
| Standard | 15-20 | Most agents |
| Extended | 25-30 | Deep research, complex debugging |
| Unlimited | *omit* | Orchestrators (project-manager) |

**`skills`** — full skill body inject at startup (~500 tokens each). Subagent **not** inherit skills from parent — list explicit. No preload skills with `disable-model-invocation: true` (CC skip and warn to debug log). Name match `src/superclaude/skills/` directory.

**`model`** — default `inherit` (use parent model). Use `sonnet` for execution/template/code; omit (inherit) for design judgment / synthesis. Resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation > frontmatter > parent. Full routing list: `agents/README.md` Model Routing + `core/FLAGS.md` `<model_routing>`.

**`permissionMode`** — most agents inherit (omit). Use `plan` for read-only research agents that no accept edits. `bypassPermissions` write to `.git`, `.claude`, `.vscode` etc. without prompt — never set on source-shipped agent. Parent `bypassPermissions` / `acceptEdits` / `auto` modes take precedence, override subagent setting.

**`color`** — SSOT: `.claude/rules/schemas.yaml` (`agent_colors`). CC accept `red, blue, green, yellow, purple, orange, pink, cyan`. SuperClaude role-group mapping use six of these:
`architecture` → blue | `engineering` → green | `research` → purple | `documentation` → yellow | `management` → orange | `indexing` → cyan
(`red`, `pink` are valid CC colors but not currently mapped to SuperClaude role group.)

**`mcpServers`** — inherit from parent by default. Specify only to add server absent from parent or to scope inline definition. To keep MCP server out of main conversation entirely (avoid its tool descriptions consuming parent context), define inline here so it connect only when subagent run.

**`memory`** — need by SuperClaude. Source files always use `memory: project`; installer rewrite at install time:
- `user` install → `memory: user`, files at `~/.claude/agent-memory/<agent>/`
- `project` install → unchanged, files at `.claude/agent-memory/<agent>/`
- `local` install → `memory: local`, files at `.claude/agent-memory-local/<agent>/`

When memory enabled, CC auto-inject up to first 200 lines / 25KB of `MEMORY.md` into subagent prompt and auto-enable Read/Write/Edit for memory file management. See `cli/install_components.py::_rewrite_agent_memory_scope`.

**Working directory.** Subagent start in parent CWD. `cd` **not** persist between Bash/PowerShell tool calls within subagent, never affect parent. For repo-isolating task, set `isolation: worktree` and CC make temporary git worktree (clean up auto if subagent make no changes).

## XML Body Structure

> Conform to `.claude/rules/xml-prose-format.md`: single root, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain with checkbox**, **Labeled**, **Named** per item type), sub-tag form for fixed labeled slots (`<bounds>` → `<does>`/`<never>`/`<fallback>`), compact tables for dense lookups (`<examples>`), and standalone `<example>` for rich multi-line illustrations.

```xml
<component name="agent-name" type="agent">
  <role>
    <mission>Single sentence matching description, without triggers.</mission>
    <mindset>Behavioral philosophy in one or two sentences.</mindset>
  </role>

  <focus>
  - Category: specific capabilities (3-5 items)
  </focus>

  <actions>
  1. Verb-leading description of the step (4-5 steps; sequence is load-bearing).
  </actions>

  <outputs>
  - Type: deliverable purpose (3-4 items)
  </outputs>

  <tool_guidance>
  - Proceed: actions to do freely. Serena-First: prefer symbolic tools for code exploration.
  - Ask First: actions requiring confirmation, with specific thresholds.
  - Never: actions the agent must never take.
  </tool_guidance>

  <checklist>
  - [ ] Concrete, verifiable completion criterion stated as one line (3-5 items)
  </checklist>

  <memory_guide>
  - CategoryName-Hyphenated: ≤80 chars description. Related: agent-1, agent-2 (optional, ≤3)
  </memory_guide>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | short trigger phrase | one-line response shape |
  | another trigger | another one-line shape |
  </examples>

  <gotchas>
  - pattern-name: concrete failure + action instruction (2-5 items)
  </gotchas>

  <bounds>
    <does>core capabilities described in prose (in-scope).</does>
    <never>out-of-scope actions described in prose.</never>
    <fallback>escalation path; recommended for agents — long-lived personas benefit from an explicit recovery posture.</fallback>
  </bounds>

  <handoff next="/sc:command1 /sc:command2"/>
</component>
```

### XML Rules

- `<mission>` — share ≥30% significant words with `description`.
- All multi-word tag names use `snake_case` (`tool_guidance`, `memory_guide`).
- Short enums: **Numbered** (`1.` ordered procedures: `<actions>`), **Plain with checkbox** (`- [ ]` verification-pending criteria: `<checklist>`), **Labeled** (`- Label:` fixed-set labels: `<tool_guidance>` Proceed/Ask First/Never), **Named** (`- identifier-name:` per-item identifiers: `<focus>`, `<outputs>`, `<gotchas>`, `<memory_guide>`).
- `<examples>` — compact markdown table with minimal separators `|---|---|` for short uniform rows. For rich illustration (code block, narrative, multi-turn prose), use standalone `<example>` tag — body is free-form prose, not lock to `user:` / `assistant:` shape. `<examples>` and `<example>` are two distinct constructs (see xml-prose-format.md).
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each tag body is prose sentence). `<does>` + `<never>` required; `<fallback>` recommended (agents long-lived; explicit recovery posture high-leverage). Sub-tag form keep `<bounds>` structurally distinct from `<tool_guidance>` (commit `S390` measured Claude conflate the two when both used `- Label:` lines).
- `<handoff>` — 2-3 natural next commands.
- `note=` attribute restrict to scope / safety / version / reference / quantified constraint (see xml-prose-format.md "Attributes vs. Body").
- **Voice — third person.** Write "Claude does X", "the agent avoids Y" — never "you" or "I". Body is agent full system prompt (not instructions addressed to model), so it read as behavioral spec for persona.

## Memory Guide (required)

**Placement.** After `<checklist>`, before `<examples>`.

**Format.**
```xml
<memory_guide>
- CategoryName-Hyphenated: what to remember (1-line, ≤80 chars). Related: agent-1, agent-2
</memory_guide>
```

**Rules.**
- 3-5 categories, specific to agent domain.
- PascalCase-Hyphenated names (e.g., `Debug-Patterns`, `API-Decisions`).
- Related-agent pointers (≤3) append inline as "Related: agent-1, agent-2" — no nested `<refs>` tag (would violate xml-prose-format depth rule).

## Code Exploration (Serena-First)

Agents that read source code should include Serena directive in `<tool_guidance>`:

| Tier | Directive | When |
|------|-----------|------|
| Code-centric (architect, engineer, analyst) | Full: `get_symbols_overview → find_symbol → find_referencing_symbols` | Always |
| Code-adjacent (manager, writer, mentor) | Light: `prefer symbolic tools for code exploration` | When code may be read |
| Non-code (researcher, business) | — | Skip |

Rationale: symbol overview vs full-file Read = significant token savings + structural understanding (refs, types, inheritance).

## Inherited from xml-prose-format.md

Rules below apply to all components, not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs and model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not tag path.
- **Markdown headers inside `<example>`** — permit when illustration mirror real markdown artifact (report template, commit message, user document); body-prose "no markdown headers" rule no extend into `<example>` bodies.
- **Size target** — agent body ≤300 lines (hard ceiling 500); extract overflow into referenced sibling file rather than inline-bloat the body.

## Authoring Checklist

1. Make `src/superclaude/agents/<name>.md` (`name` match filename).
2. Write 1-3 sentence `description` end with CC-idiom trigger ("Use proactively for…", "Use immediately after…", "Use when…").
3. Pick tool access pattern — one of `tools` or `disallowedTools`, never both.
4. Set `maxTurns`; omit `effort` unless measured evidence justify it.
5. Pick `color` by role group; pick `model` by cognitive complexity (omit to inherit).
6. Consider `skills: [confidence-check]` for analytical agents.
7. Add `<memory_guide>` (required) and `<gotchas>` (recommended).
8. Run `uv run pytest tests/unit/test_agent_structure.py -v`.
9. Update `src/superclaude/agents/README.md` table.
10. Run `make deploy`.