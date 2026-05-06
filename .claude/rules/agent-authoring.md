---
paths: ["src/superclaude/agents/**", ".claude/rules/agent-authoring.md"]
---

# Agent Authoring Rules

> **Decision gate.** Create an agent for **domain expertise** that CC auto-delegates on description match.
> - Agent = **WHO TO BE** (domain expert persona)
> - Command = **WHAT TO DO** (user-invoked workflow)
> - Skill = **WHICH CAPABILITY** (CC-native tool/hook)
> - Mode = **HOW TO THINK** (cognitive overlay)

> **What CC actually loads.** A subagent's session contains only the markdown body (system prompt) plus minimal environment context — *not* the parent's CC system prompt and *not* the parent's skills. Write the body to be self-contained. A subagent cannot spawn further subagents (only the main thread can, via `--agent` + `Agent` in `tools`); design every agent to return one summary, no nested delegation.

> **Don't recreate built-ins.** CC ships `Explore` (read-only codebase search, Haiku), `Plan` (read-only research for plan mode), `general-purpose` (full-tool multi-step), `statusline-setup`, and `Claude Code Guide`. New SuperClaude agents must add domain-specific value beyond what these provide; an agent that just "searches the codebase" or "researches before acting" duplicates `Explore`/`Plan` and bloats the registry.

> **Bodies run in two modes.** The same file can run as a delegated subagent (body = system prompt for an isolated session) OR as the whole session via `claude --agent <name>` (body replaces CC's default system prompt). Author the body to read coherently in both modes — avoid phrasing that assumes a parent ("when delegated to you", "the calling Claude") and prefer persona-defining statements ("Claude operates as …", "the agent's mission is …").

## YAML Frontmatter

CC requires only `name` and `description`. Everything else is optional and inherits from the parent session. SuperClaude additionally requires `memory` and `color` for installer integration.

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

CC reads `description` verbatim to decide delegation. Two pieces:

- **Persona** — a noun phrase identifying the expert ("Expert code reviewer", "Debugging specialist for errors and test failures").
- **Trigger phrase** — when to delegate, in CC's idiom: *"Use proactively for X."*, *"Use immediately after Y."*, *"Use when Z."*

Skip emoji, version tags, and colon-prefixed keyword lists — the description is a sentence read by the parent's classifier; write a sentence. The legacy `(triggers - kw1, kw2)` shorthand is parsed but classifies less reliably than a CC-idiomatic sentence. One to three sentences total; longer descriptions improve delegation accuracy and cost nothing at runtime.

Canonical patterns (from CC docs):
- `Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.`
- `Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.`
- `Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.`

#### Vocabulary cautions

The description sentence is read verbatim into the subagent's system prompt header — wording shifts measurably change behavior. Empirical findings from the agent-naming experiment series (107 trials, see `docs/research/2026-05-06-agent-naming-findings/`):

- **Avoid past-implying phrasing.** `following X practices`, `deep production experience`, `pragmatic tradeoff judgment` — these prime a "this is a continuation of prior work" frame and produced 5/5 and 3/3 context-hallucination rates on long-output tasks (subagents fabricating preexisting files, prior fixes, even narrating edits to their own definition file). The `engineer` and `senior-python-engineer` rename pairs broke from this alone, body unchanged.
- **Prefer forward-looking voice.** `learning to apply X`, `grounded in X`, `with deep mastery and seasoned judgment` — these did not trigger the failure mode (0/3 hallucinations).
- **Description is a lever for over-engineering.** Adding a Zen-of-Python clause ("simple is better than complex; values minimal solutions, the smallest abstraction; code that any junior can read") to the same agent name reduced over-engineering signals 25–73% (chars −25%, classes −58%, decorators −65%, TypeVar −100% across 15 trials). Use this lever before reaching for a rename if the goal is anti-overengineering.
- **`hypothesis`-style advanced patterns are sticky** — directive phrasing only reduced unprompted property-based test usage by ~20%. Some priors require explicit prohibition (`Do not use property-based testing libraries unless asked.`) rather than soft directives.

### Field reference

**Forbidden in source.** `autonomy` (not a CC field). Any field not in CC's documented agent spec.

**Tool access.** Five canonical patterns:

| Pattern | Field | Value | When |
|---------|-------|-------|------|
| Read-only + web | `tools` | `Read, Grep, Glob, Agent, WebSearch, WebFetch` | Plan/review/research (fails closed — **preferred**) |
| Read-only minimal | `tools` | `Read, Grep, Glob, Agent` | No web access needed |
| Execute-only | `disallowedTools` | `Edit, Write, NotebookEdit` | Runs commands, never edits files (e.g., git-workflow) |
| General | `disallowedTools` | `NotebookEdit` | Code edits OK, no notebook edits |
| Full access | *(omit both)* | — | Implementation agents |

CC permits both `tools` and `disallowedTools` together (deny applied first, then allow resolved against the remaining pool — a tool listed in both is removed). **SuperClaude convention: pick one form per agent for readability — never mix.**

**Spawn restrictions (orchestrators only).** `tools: Agent(worker, researcher)` allow-lists which subagent types can be spawned. Takes effect only when the agent runs as the main thread (`claude --agent <name>`); has no effect inside a regular subagent (subagents cannot spawn subagents). Bare `Agent` allows any; omitting `Agent` from `tools` disables spawning entirely.

**`effort`** (CC v2.1.69+) — **omit by default.** Inherit from parent unless measured evidence shows a specific value materially changes output for this agent's domain. String values only; `xhigh` requires Opus 4.7 + CC 2.1.111+; `max` requires Opus 4.6/4.7.

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` env > frontmatter > session > model default.

When `xhigh` is worth setting (Opus 4.7+): Anthropic recommends `xhigh` as baseline for coding/agentic work — at `low`/`medium`, Opus 4.7 under-thinks edge cases. Two safe paths:
1. **Session-level (preferred).** `CLAUDE_CODE_EFFORT_LEVEL=xhigh` or pick `xhigh` at session start — uniform, respects user's cost-vs-quality choice.
2. **Agent-level override.** `effort: xhigh` only when measured quality regression at the session default justifies it.

Don't add `effort: xhigh` because the domain "feels" coding-heavy — the session default covers that. Inherit-by-default keeps cost control with the user (commit `8edd05d`).

**`maxTurns`** — turn-limit safety net:

| Category | maxTurns | When |
|----------|----------|------|
| Quick | 10 | Scanning, mechanical ops |
| Standard | 15-20 | Most agents |
| Extended | 25-30 | Deep research, complex debugging |
| Unlimited | *omit* | Orchestrators (project-manager) |

**`skills`** — full skill body injected at startup (~500 tokens each). Subagents do **not** inherit skills from the parent — list explicitly. Cannot preload skills with `disable-model-invocation: true` (CC skips and warns to debug log). Name must match `src/superclaude/skills/` directory.

**`model`** — defaults to `inherit` (uses parent's model). Use `sonnet` for execution/template/code; omit (inherit) for design judgment / synthesis. Resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation > frontmatter > parent. Full routing list: `agents/README.md` Model Routing + `core/FLAGS.md` `<model_routing>`.

**`permissionMode`** — most agents inherit (omit). Use `plan` for read-only research agents that should never accept edits. `bypassPermissions` writes to `.git`, `.claude`, `.vscode` etc. without prompting — never set on a source-shipped agent. Parent `bypassPermissions` / `acceptEdits` / `auto` modes take precedence and override the subagent's setting.

**`color`** — SSOT: `.claude/rules/schemas.yaml` (`agent_colors`). CC accepts `red, blue, green, yellow, purple, orange, pink, cyan`. SuperClaude role-group mapping uses six of these:
`architecture` → blue | `engineering` → green | `research` → purple | `documentation` → yellow | `management` → orange | `indexing` → cyan
(`red`, `pink` are valid CC colors but not currently mapped to a SuperClaude role group.)

**`mcpServers`** — inherited from parent by default. Specify only to add a server absent from the parent or to scope an inline definition. To keep an MCP server out of the main conversation entirely (avoid its tool descriptions consuming parent context), define it inline here so it connects only when the subagent runs.

**`memory`** — required by SuperClaude. Source files always use `memory: project`; the installer rewrites at install time:
- `user` install → `memory: user`, files at `~/.claude/agent-memory/<agent>/`
- `project` install → unchanged, files at `.claude/agent-memory/<agent>/`
- `local` install → `memory: local`, files at `.claude/agent-memory-local/<agent>/`

When memory is enabled, CC auto-injects up to the first 200 lines / 25KB of `MEMORY.md` into the subagent's prompt and auto-enables Read/Write/Edit for memory file management. See `cli/install_components.py::_rewrite_agent_memory_scope`.

**Working directory.** Subagents start in the parent's CWD. `cd` does **not** persist between Bash/PowerShell tool calls within a subagent and never affects the parent. For repo-isolating tasks, set `isolation: worktree` and CC creates a temporary git worktree (cleaned up automatically if the subagent makes no changes).

## XML Body Structure

> Conforms to `.claude/rules/xml-prose-format.md`: single root, `snake_case` section tags, short-line lists (**Numbered** `1.` for ordered procedures, or `-` prefix as **Plain with checkbox**, **Labeled**, **Named** per item type), sub-tag form for fixed labeled slots (`<bounds>` → `<does>`/`<never>`/`<fallback>`), compact tables for dense lookups (`<examples>`), and standalone `<example>` for rich multi-line illustrations.

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

- `<mission>` — shares ≥30% significant words with `description`.
- All multi-word tag names use `snake_case` (`tool_guidance`, `memory_guide`).
- Short enums: **Numbered** (`1.` ordered procedures: `<actions>`), **Plain with checkbox** (`- [ ]` verification-pending criteria: `<checklist>`), **Labeled** (`- Label:` fixed-set labels: `<tool_guidance>` Proceed/Ask First/Never), **Named** (`- identifier-name:` per-item identifiers: `<focus>`, `<outputs>`, `<gotchas>`, `<memory_guide>`).
- `<examples>` — compact markdown table with minimal separators `|---|---|` for short uniform rows. For richer illustrations (code blocks, narrative, multi-turn prose), use a standalone `<example>` tag — its body is free-form prose, not locked to a `user:` / `assistant:` shape. `<examples>` and `<example>` are two distinct constructs (see xml-prose-format.md).
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each tag's body is a prose sentence). `<does>` + `<never>` required; `<fallback>` recommended (agents are long-lived; explicit recovery posture is high-leverage). Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>` (commit `S390` measured Claude conflating the two when both used `- Label:` lines).
- `<handoff>` — 2-3 natural next commands.
- `note=` attribute restricted to scope / safety / version / reference / quantified constraint (see xml-prose-format.md "Attributes vs. Body").
- **Voice — third person.** Write "Claude does X", "the agent avoids Y" — never "you" or "I". The body is the agent's full system prompt (not instructions addressed to a model), so it reads as a behavioral spec for the persona.

## Memory Guide (required)

**Placement.** After `<checklist>`, before `<examples>`.

**Format.**
```xml
<memory_guide>
- CategoryName-Hyphenated: what to remember (1-line, ≤80 chars). Related: agent-1, agent-2
</memory_guide>
```

**Rules.**
- 3-5 categories, specific to the agent's domain.
- PascalCase-Hyphenated names (e.g., `Debug-Patterns`, `API-Decisions`).
- Related-agent pointers (≤3) appended inline as "Related: agent-1, agent-2" — no nested `<refs>` tag (would violate xml-prose-format depth rule).

## Code Exploration (Serena-First)

Agents that read source code should include a Serena directive in `<tool_guidance>`:

| Tier | Directive | When |
|------|-----------|------|
| Code-centric (architect, engineer, analyst) | Full: `get_symbols_overview → find_symbol → find_referencing_symbols` | Always |
| Code-adjacent (manager, writer, mentor) | Light: `prefer symbolic tools for code exploration` | When code may be read |
| Non-code (researcher, business) | — | Skip |

Rationale: symbol overview vs full-file Read = significant token savings + structural understanding (refs, types, inheritance).

## Inherited from xml-prose-format.md

The following rules apply to all components and are not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs and model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when the illustration mirrors a real markdown artifact (report template, commit message, user document); the body-prose "no markdown headers" rule does not extend into `<example>` bodies.
- **Size target** — agent body ≤300 lines (hard ceiling 500); extract overflow into a referenced sibling file rather than inline-bloating the body.

## Authoring Checklist

1. Create `src/superclaude/agents/<name>.md` (`name` matches filename).
2. Write a 1-3 sentence `description` ending with a CC-idiomatic trigger ("Use proactively for…", "Use immediately after…", "Use when…").
3. Choose tool access pattern — one of `tools` or `disallowedTools`, never both.
4. Set `maxTurns`; omit `effort` unless measured evidence justifies it.
5. Pick `color` by role group; pick `model` by cognitive complexity (omit to inherit).
6. Consider `skills: [confidence-check]` for analytical agents.
7. Add `<memory_guide>` (required) and `<gotchas>` (recommended).
8. Run `uv run pytest tests/unit/test_agent_structure.py -v`.
9. Update `src/superclaude/agents/README.md` table.
10. Run `make deploy`.
