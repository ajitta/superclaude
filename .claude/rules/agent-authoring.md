---
paths: ["src/superclaude/agents/**", ".claude/rules/agent-authoring.md"]
---

# Agent Authoring Rules

> **Decision gate.** Create an agent when the work needs **domain expertise** that Claude Code should delegate to automatically when a request matches the agent's description.
> - Agent = **WHO TO BE** (domain expert persona)
> - Command = **WHAT TO DO** (user-invoked workflow)
> - Mode = **HOW TO THINK** (cognitive overlay)

> **What Claude Code loads.** A subagent session gets the agent's markdown body as its system prompt plus minimal environment context. It does not get the parent's Claude Code system prompt or the parent's skills; whether it gets CLAUDE.md (and through it the superclaude kernel) depends on Claude Code settings such as `omitClaudeMd`, and the on-demand rule modules never reach it. Write the body self-contained. A subagent cannot spawn further subagents (only a main thread can, via `--agent` with `Agent` in `tools`), so each agent returns one summary with no nested delegation.

> **No recreate built-ins.** CC ship `Explore` (read-only codebase search, Haiku), `Plan` (read-only research for plan mode), `general-purpose` (full-tool multi-step), `statusline-setup`, `Claude Code Guide`. New superclaude agent must add domain-specific value past these; agent that just "search codebase" or "research before act" duplicate `Explore`/`Plan` and bloat registry.

> **Body run two modes.** Same file run as delegated subagent (body = system prompt for isolated session) OR as whole session via `claude --agent <name>` (body replace CC default system prompt). Write body read coherent both modes — no phrasing that assume parent ("when delegated to you", "the calling Claude"); prefer persona statements ("Claude operates as …", "the agent's mission is …").

## YAML Frontmatter

CC need only `name` + `description`. Rest optional, inherit from parent. superclaude also need `memory` + `color` for installer.

```yaml
---
# Required by CC
name: agent-name                            # lowercase letters and hyphens; matches filename
description: <Domain> specialist for <distinguishing task>. Use when <signal no neighbor agent covers>. Not for <look-alike> — <neighbor>.

# Required by superclaude
memory: project                             # source value always "project"; installer rewrites to user/local per scope
color: blue                                 # role-group mapping below

# Optional — omit to inherit from parent session
model: sonnet                               # sonnet | opus | haiku | fable | full ID (e.g. claude-fable-5-1). Omit the field to inherit the session model (default); `inherit` is not a documented value
permissionMode: default                     # default | acceptEdits | auto | dontAsk | bypassPermissions | plan
tools: Read, Grep, Glob, Agent              # allow-list (comma-separated)
disallowedTools: Edit, Write                # deny-list (applied first, then `tools` resolved against remainder)
effort: high                                # low | medium | high | xhigh | max  (string, not 1-5)
skills: [some-installed-skill]              # full skill body injected at startup; subagent does NOT inherit parent skills
mcpServers: [playwright]                    # references to configured servers, or inline definitions

# Advanced — rarely set in superclaude agents
hooks:                                      # PreToolUse / PostToolUse / Stop scoped to this subagent (see CC hooks docs for structure)
background: false                           # always run as a background task
isolation: worktree                         # spawn in a temporary git worktree (isolated repo copy)
initialPrompt:                              # auto-submitted as first user turn when run as main session via --agent
---
```

### Description writing

CC read `description` verbatim to decide delegation. Two parts:

- **Persona** — noun phrase name the expert ("Expert code reviewer", "Debugging specialist for errors and test failures").
- **Trigger phrase** — the signal in a request that this agent covers and its neighbors do not: *"Use when Z."* Write *"Use proactively …"* or *"Use immediately after …"* only when the agent must run unasked, and name after what: when most agents claim proactivity the phrase stops separating them, and overlapping triggers fire several agents for one request (docs/features/prompt-content-audit/).
- **Negative gate** — when a neighbor shares the verb, add *"Not for <look-alike> — <neighbor>."* (verifier's description is the model).

Skip emoji, version tag, colon-prefix keyword list — description is sentence read by parent classifier; write sentence. Legacy `(triggers - kw1, kw2)` shorthand parse but classify less reliable than CC-idiom sentence. One to three sentences total; description sit in parent context every turn, so extra words must sharpen when-to-delegate (`content-quality.md` §1).

Patterns:
- `Debugging specialist for errors and test failures. Use when a test fails or a stack trace is pasted and the cause is unknown. Not for slow code — performance-engineer.`
- `Data analysis expert for SQL queries and BigQuery operations. Use when the request names a query, table or dataset. Not for schema design — backend-architect.`

#### Vocabulary cautions

Description sentence read verbatim into subagent system prompt header — word shift measurably change behavior. Empirical findings from agent-naming experiment series (107 trials, see `docs/research/2026-05-06-agent-naming-findings/`):

- **No past-implying phrasing.** `following X practices`, `deep production experience`, `pragmatic tradeoff judgment` — these prime "continuation of prior work" frame, produce 5/5 and 3/3 context-hallucination rates on long-output tasks (subagent fabricate preexisting files, prior fixes, even narrate edits to own definition file). `engineer` and `senior-python-engineer` rename pairs break from this alone, body unchanged.
- **Prefer forward-looking voice.** `learning to apply X`, `grounded in X`, `with deep mastery and seasoned judgment` — these no trigger failure mode (0/3 hallucinations).
- **Description is lever for over-engineering.** Add Zen-of-Python clause ("simple is better than complex; values minimal solutions, the smallest abstraction; code that any junior can read") to same agent name reduce over-engineering signals 25–73% (chars −25%, classes −58%, decorators −65%, TypeVar −100% across 15 trials). Use this lever before rename if goal is anti-overengineering.
- **`hypothesis`-style advanced patterns sticky** — directive phrasing only reduce unprompted property-based test usage ~20%. Some priors need explicit prohibition (`Do not use property-based testing libraries unless asked.`) not soft directive.

> **Enforced.** Forbidden exemplars (`following X practices`, `deep production experience`, `pragmatic tradeoff judgment`) + presence of a CC-idiom trigger are checked by `tests/unit/test_agent_structure.py::TestAgentDescriptionInterface` (deterministic, default `make test`). Add newly-proven exemplars to `FORBIDDEN_DESC_PATTERNS`.

### Field reference

**Forbidden in source.** `autonomy` (not CC field). Any field not in CC documented agent spec.

**Tool access.** Five canonical patterns:

| Pattern | Field | Value | When |
|---------|-------|-------|------|
| Read-only + web | `tools` | `Read, Grep, Glob, Agent, WebSearch, WebFetch` | Plan/review/research (fails closed) |
| Read-only minimal | `tools` | `Read, Grep, Glob, Agent` | No web access needed |
| Execute-only | `disallowedTools` | `Edit, Write, NotebookEdit` | Runs commands, never edits files |
| General | `disallowedTools` | `NotebookEdit` | Code edits OK, no notebook edits |
| Full access | *(omit both)* | — | Implementation agents |

A `tools` list drops every MCP tool it does not name: commit `672055ce` stripped `tools`/`disallowedTools` from all agents for that reason, so set one only when the agent needs no MCP. CC permit both `tools` and `disallowedTools` together (deny applied first, then allow resolved against remaining pool — tool listed in both is removed). **superclaude convention: pick one form per agent for readability — never mix.**

**Spawn restrictions (orchestrators only).** `tools: Agent(worker, researcher)` allow-list which subagent types can spawn. Take effect only when agent run as main thread (`claude --agent <name>`); no effect inside regular subagent (subagent no spawn subagent). Bare `Agent` allow any; omit `Agent` from `tools` disable spawning entirely.

**`effort`** — **omit by default.** Inherit from parent unless measured evidence show specific value materially change output for agent domain. String values only; `xhigh`/`max` availability and the default level depend on model + CC version — check current docs, not a pinned value.

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` env > frontmatter > session > model default.

When `xhigh` worth setting: reserve `xhigh` ('extra') / `max` for difficult tasks or long-running async work — not as a blanket coding baseline. If a session runs at `low`/`medium`, the model under-thinks edge cases; two safe paths to raise it:
1. **Session-level (preferred).** `CLAUDE_CODE_EFFORT_LEVEL=xhigh` or pick `xhigh` at session start — uniform, respect user cost-vs-quality choice.
2. **Agent-level override.** `effort: xhigh` only when measured quality regression at session default justify it.

No add `effort: xhigh` because domain "feels" coding-heavy — session default cover that. Inherit-by-default keep cost control with user (commit `8edd05d`).

**`skills`** — full skill body inject at startup (~500 tokens each). Subagent **not** inherit skills from parent — list explicit. No preload skills with `disable-model-invocation: true` (CC skip and warn to debug log). superclaude's `sc-author` skill sets `disable-model-invocation: true`, so it cannot be preloaded; names refer to skills installed in `~/.claude/skills/` or `.claude/skills/`.

**`model`** — omit it: no shipped agent pins a model, and an omitted field follows Claude Code's subagent resolution order. Resolution order and the Fable opt-in paths: `agents/README.md` Model Routing (SSOT).

**`permissionMode`** — most agents inherit (omit). Use `plan` for read-only research agents that no accept edits. `bypassPermissions` write to `.git`, `.claude`, `.vscode` etc. without prompt — never set on source-shipped agent. Parent `bypassPermissions` / `acceptEdits` / `auto` modes take precedence, override subagent setting.

**`color`** — SSOT: `.claude/rules/schemas.yaml` (`agent_colors`). CC accept `red, blue, green, yellow, purple, orange, pink, cyan`. superclaude role-group mapping use six of these:
`architecture` → blue | `engineering` → green | `research` → purple | `documentation` → yellow | `management` → orange | `indexing` → cyan
(`red`, `pink` are valid CC colors but not currently mapped to superclaude role group.)

**`mcpServers`** — inherit from parent by default. Specify only to add server absent from parent or to scope inline definition. To keep MCP server out of main conversation entirely (avoid its tool descriptions consuming parent context), define inline here so it connect only when subagent run.

**`memory`** — need by superclaude. Source files always use `memory: project`; installer rewrite at install time:
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
  - Proceed: actions to do freely.
  - Symbolic-First: full or light form (see Code Exploration below).
  - Ask First: actions requiring confirmation, with specific thresholds (run as a delegated subagent, the agent cannot ask: it stops before the action and reports it as needing confirmation).
  - Never: actions the agent must never take.
  </tool_guidance>

  <checklist>
  - [ ] Concrete, verifiable completion criterion stated as one line (3-5 items)
  </checklist>

  <memory_guide>
  MEMORY.md = prior lessons; verify against current state before acting on them.
  After task: append `- YYYY-MM-DD: Category-Name: lesson` (max 3 lines) only if a future run would act differently; consolidate at 150 lines.
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
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each tag body is prose sentence). `<does>` + `<never>` required; `<fallback>` recommended (agents long-lived; explicit recovery posture high-leverage). Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>`; Claude conflated the two when both used `- Label:` lines (xml-prose-format.md Sub-tag enumerations).
- `<handoff>` — 2-3 natural next commands.
- `note=` attribute restrict to scope / safety / version / reference / quantified constraint (see xml-prose-format.md "Attributes vs. Body").
- **Voice — third person.** Write "Claude does X", "the agent avoids Y" — never "you" or "I". Third person is this repo's convention for consistency across agents; the same body runs as a subagent and via `claude --agent`.

## Memory Guide (required)

**Placement.** After `<checklist>`, before `<examples>`.

**Format.**
```xml
<memory_guide>
MEMORY.md = prior lessons; verify against current state before acting on them.
After task: append `- YYYY-MM-DD: Category-Name: lesson` (max 3 lines) only if a future run would act differently; consolidate at 150 lines.
- CategoryName-Hyphenated: what to remember (1-line, ≤80 chars). Related: agent-1, agent-2
</memory_guide>
```

**Rules.**
- Protocol header (2 lines above, verbatim identical in every agent) precedes the category list. The protocol ships in every body so it holds when CLAUDE.md is omitted (`omitClaudeMd`) or superclaude is not installed. Capture triggers worth remembering: user corrections, decisions with rationale, recurring patterns (3+), unexpected discoveries.
- 3-5 categories, specific to agent domain.
- PascalCase-Hyphenated names (e.g., `Debug-Patterns`, `API-Decisions`).
- Related-agent pointers (≤3) append inline as "Related: agent-1, agent-2" — no nested `<refs>` tag (would violate xml-prose-format depth rule).

## Code Exploration (Symbolic-First)

Agents that read source code should include a Symbolic-First directive in `<tool_guidance>`:

| Tier | Directive | When |
|------|-----------|------|
| Reads and changes source (system/backend/frontend architects, python-expert, quality/performance/security engineers, refactoring-expert, root-cause-analyst, repo-index, self-review) | Full: `- Symbolic-First: with a symbol-aware tool connected (LSP or code index), query overview → definition → references before whole-file Read; without one, targeted Grep then Read of the matched range.` + optional agent-specific Grep sentence + `Read whole files only when small or non-code.` | Always |
| Touches code to configure, plan, document or teach (devops-architect, requirements-analyst, project-manager, project-initializer, technical-writer, learning-guide, socratic-mentor) | Light: `- Symbolic-First: prefer symbol-aware queries (when connected) or targeted Grep over whole-file Read when exploring code.` | When code may be read |
| Non-code (business-panel-experts, deep-researcher, git-workflow, insight-analyst, simplicity-guide, verifier) | — | Skip |

Rationale: symbol overview vs full-file Read = significant token savings + structural understanding (refs, types, inheritance). The on-demand rule modules never reach a subagent, so the line ships in the agent body.

## Format

Body-format rules (single root, list forms, quoting, cross-references, headers inside `<example>`, size targets) live in `.claude/rules/xml-prose-format.md`, which loads together with this file. They are not restated here.

## Authoring Checklist

1. Make `src/superclaude/agents/<name>.md` (`name` match filename).
2. Write a 1-3 sentence `description` ending with a trigger that separates the agent from its neighbors ("Use when…"; "Use proactively …" only for agents that must run unasked) and a "Not for …" gate when a neighbor shares the verb.
3. Pick tool access pattern — one of `tools` or `disallowedTools`, never both.
4. Omit `maxTurns` (removed from every agent in `2718f713`) and `effort` (unless measured evidence justifies it).
5. Pick `color` by role group; omit `model` (see the `model` field rule above).
6. `skills:` preloads an installed skill's body. superclaude ships none — only name one that is actually installed in the target scope.
7. Add `<memory_guide>` (required) and `<gotchas>` (recommended).
8. Run `uv run pytest tests/unit/test_agent_structure.py -v`.
9. Update `src/superclaude/agents/README.md` table.
10. Re-sync an existing install: run `superclaude doctor --scope <s>` first, because `install --force` creates an install where none exists (gotcha `sync-scope-creates`); `make deploy` reinstalls only the CLI.