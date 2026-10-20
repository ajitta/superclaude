---
paths: ["src/superclaude/agents/**", ".claude/rules/agent-authoring.md"]
---

# Agent Authoring Rules

> **Decision gate.** Create an agent only for a recurring job that needs what only a subagent gives: a context of its own (the job reads far more than it returns — a web sweep, a whole-repo scan), tools restricted to the job (read-only review, run-but-never-edit), or a fresh view that has not seen the author's reasoning (independent review, verification). Domain expertise alone is not a reason: the model already has it, and an expert persona changes tone, not accuracy (`docs/research/persona-anchoring-framing-audit-chosh1179-2026-09-14.md` F1). Put a domain checklist in the command or rule that uses it, where the main session or a `general-purpose` delegate applies it. A job that must talk with the user mid-task (teaching, interactive menus, confirm-each-step) is a command, not an agent: a subagent returns one summary and cannot ask. Keep the roster small — every description competes for delegation, and a sprawling roster makes automatic delegation less reliable (Anthropic, "How and when to use subagents"). The 2026-10 audit cut 24 agents to 5 on this gate: `docs/features/agent-roster-audit/`.
> - Agent = **WHO DOES ISOLATED WORK** (own context, restricted tools or a fresh view)
> - Command = **WHAT TO DO** (user-invoked workflow)
> - Mode = **HOW TO THINK** (cognitive overlay)

> **What Claude Code loads.** A subagent session gets the agent's markdown body as its system prompt plus minimal environment context. It does not get the parent's Claude Code system prompt or the parent's skills; whether it gets CLAUDE.md (and through it the superclaude kernel) depends on Claude Code and on the agent frontmatter field `omitClaudeMd`, and the on-demand rule modules never reach it. Write the body self-contained. A subagent whose tool pool includes `Agent` can spawn subagents of its own, up to three layers below the main conversation by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); a reviewer that must stay read-only omits `Agent`, because a spawned `general-purpose` delegate can edit. A body still names no sibling agent to hand work to: open items go back to the main session, which decides what runs next.

> **Don't recreate built-ins.** CC ships `Explore` (read-only codebase search, Haiku), `Plan` (read-only research for plan mode), `general-purpose` (full-tool multi-step), `statusline-setup`, and `Claude Code Guide`. A new superclaude agent must add domain-specific value beyond these; an agent that just "searches the codebase" or "researches before acting" duplicates `Explore`/`Plan` and bloats the registry.

> **Bodies run in two modes.** The same file runs as a delegated subagent (body = system prompt for an isolated session) OR as the whole session via `claude --agent <name>` (body replaces CC's default system prompt). Write the body to read coherently in both modes — no phrasing that assumes a parent ("when delegated to you", "the calling Claude"); prefer persona statements ("Claude operates as …", "the agent's mission is …").

## YAML Frontmatter

CC requires only `name` and `description`. The rest are optional and inherit from the parent. superclaude also requires `memory` and `color` for the installer.

```yaml
---
# Required by CC
name: agent-name                            # lowercase letters and hyphens; matches filename
description: <Job> for <distinguishing task>. Use when <signal no neighbor covers>. Not for <look-alike> — <neighbor>.

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
omitClaudeMd: true                          # subagent starts without CLAUDE.md (and so without the superclaude kernel)
---
```

### Description writing

CC reads `description` verbatim to decide delegation. Three parts:

- **Job** — a noun phrase naming the work the agent does in isolation ("Report-only verification runner", "Web-research specialist for cross-checked synthesis"), not an identity ("senior Python engineer").
- **Trigger phrase** — the signal in a request that this agent covers and its neighbors do not: *"Use when Z."* Write *"Use proactively …"* or *"Use immediately after …"* only when the agent must run unasked, and name the event it follows: when most agents claim proactivity the phrase stops separating them, and overlapping triggers fire several agents for one request (docs/features/prompt-content-audit/).
- **Negative gate** — when a neighbor shares the verb, add *"Not for <look-alike> — <neighbor>."* (verifier's description is the model).

Skip emoji, version tags, and colon-prefixed keyword lists — the description is a sentence read by the parent's classifier; write a sentence. The legacy `(triggers - kw1, kw2)` shorthand is parsed but classifies less reliably than a CC-idiomatic sentence. One to three sentences total; the description sits in the parent's context every turn, so extra words must sharpen when-to-delegate (`content-quality.md` §1).

Patterns:
- `Read-only reviewer of SQL migrations for lock and rollback risk. Use when a diff adds or edits a migration file. Not for query tuning — /sc:analyze --focus perf.`
- `Log-triage runner that reads large CI logs and returns only the failing steps with their error lines. Use when a CI run failed and its log is too long to read in the main session. Not for fixing the failure — /sc:troubleshoot.`

#### Vocabulary cautions

The description sentence is read verbatim into the subagent's system prompt header — wording shifts measurably change behavior. Empirical findings from the agent-naming experiment series (107 trials, see `docs/research/2026-05-06-agent-naming-findings/`):

- **No past-implying phrasing.** `following X practices`, `deep production experience`, `pragmatic tradeoff judgment` — these prime a "continuation of prior work" frame and produced 5/5 and 3/3 context-hallucination rates on long-output tasks (subagents fabricated preexisting files and prior fixes, and even narrated edits to their own definition file). The `engineer` and `senior-python-engineer` rename pairs broke from this alone, body unchanged.
- **Prefer forward-looking voice.** `learning to apply X`, `grounded in X`, `with deep mastery and seasoned judgment` — these did not trigger the failure mode (0/3 hallucinations).
- **Description is a lever for over-engineering.** Adding a Zen-of-Python clause ("simple is better than complex; values minimal solutions, the smallest abstraction; code that any junior can read") to the same agent name reduced over-engineering signals 25–73% (chars −25%, classes −58%, decorators −65%, TypeVar −100% across 15 trials). Use this lever before a rename if the goal is anti-overengineering.
- **`hypothesis`-style advanced patterns are sticky** — directive phrasing only reduced unprompted property-based test usage by ~20%. Some priors need an explicit prohibition (`Do not use property-based testing libraries unless asked.`), not a soft directive.

> **Enforced.** Forbidden exemplars (`following X practices`, `deep production experience`, `pragmatic tradeoff judgment`) and the presence of a CC-idiom trigger are checked by `tests/unit/test_agent_structure.py::TestAgentDescriptionInterface` (deterministic, default `make test`). Add newly-proven exemplars to `FORBIDDEN_DESC_PATTERNS`. Pairwise overlap with the other agents (description minus the "Not for" gate, stemmed TF-IDF cosine without the names, fail at 0.70) is checked by `tests/unit/test_description_overlap.py`; on a failure, sharpen the distinguishing task, never the threshold.

### Field reference

**Forbidden in source.** `autonomy` (not a CC field). Any field not in CC's documented agent spec.

**Tool access.** Five canonical patterns:

| Pattern | Field | Value | When |
|---------|-------|-------|------|
| Read-only + web | `tools` | `Read, Grep, Glob, WebSearch, WebFetch` | Plan/review/research (fails closed) |
| Read-only minimal | `tools` | `Read, Grep, Glob` | No web access needed |
| Execute-only | `disallowedTools` | `Edit, Write, NotebookEdit` | Runs commands, never edits files |
| General | `disallowedTools` | `NotebookEdit` | Code edits OK, no notebook edits |
| Full access | *(omit both)* | — | Implementation agents |

A `tools` list drops every MCP tool it does not name: commit `672055ce` stripped `tools`/`disallowedTools` from all agents for that reason, so set one only when the agent needs no MCP. CC permits both `tools` and `disallowedTools` together (deny is applied first, then allow is resolved against the remaining pool — a tool listed in both is removed). **superclaude convention: pick one form per agent for readability — never mix.**

**Spawn restrictions (orchestrators only).** `tools: Agent(worker, researcher)` allow-lists which subagent types can be spawned. The type list takes effect only when the agent runs as the main thread (`claude --agent <name>`). In a subagent definition, `Agent` in `tools` lets the subagent spawn subagents within the depth limit, and any type list in parentheses is ignored. Bare `Agent` allows any type; omitting `Agent` from `tools` (or listing it in `disallowedTools`) disables spawning entirely, which is how a read-only reviewer stays read-only.

**`effort`** — **omit by default.** Inherit from the parent unless measured evidence shows a specific value materially changes output for the agent's domain. String values only; `xhigh`/`max` availability and the default level depend on the model and CC version — check current docs, not a pinned value.

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` env > frontmatter > session > model default.

When `xhigh` is worth setting: reserve `xhigh` ('extra') / `max` for difficult tasks or long-running async work — not as a blanket coding baseline. If a session runs at `low`/`medium`, the model under-thinks edge cases; two safe paths to raise it:
1. **Session-level (preferred).** `CLAUDE_CODE_EFFORT_LEVEL=xhigh` or pick `xhigh` at session start — uniform, and respects the user's cost-vs-quality choice.
2. **Agent-level override.** `effort: xhigh` only when measured quality regression at the session default justifies it.

Don't add `effort: xhigh` because the domain "feels" coding-heavy — the session default covers that. Inherit-by-default keeps cost control with the user (commit `8edd05d`).

**`skills`** — the full skill body is injected at startup (~500 tokens each). Subagents do **not** inherit skills from the parent — list them explicitly. Do not preload skills with `disable-model-invocation: true` (CC skips them and warns to the debug log). superclaude's `sc-author` skill sets `disable-model-invocation: true`, so it cannot be preloaded; names refer to skills installed in `~/.claude/skills/` or `.claude/skills/`.

**`model`** — omit it: no shipped agent pins a model, and an omitted field follows Claude Code's subagent resolution order. Resolution order and the Fable opt-in paths: `agents/README.md` Model Routing (SSOT).

**`permissionMode`** — most agents inherit (omit). Use `plan` for read-only research agents that do not accept edits. `bypassPermissions` writes to `.git`, `.claude`, `.vscode` etc. without prompting — never set it on a source-shipped agent. Parent `bypassPermissions` / `acceptEdits` / `auto` modes take precedence and override the subagent's setting.

**`color`** — SSOT: `.claude/rules/schemas.yaml` (`agent_colors`). CC accepts `red, blue, green, yellow, purple, orange, pink, cyan`. The superclaude role-group mapping uses six of these:
`architecture` → blue | `engineering` → green | `research` → purple | `documentation` → yellow | `management` → orange | `indexing` → cyan
(`red`, `pink` are valid CC colors but not currently mapped to a superclaude role group.)

**`mcpServers`** — inherited from the parent by default. Specify it only to add a server absent from the parent or to scope an inline definition. To keep an MCP server out of the main conversation entirely (avoid its tool descriptions consuming parent context), define it inline here so it connects only when the subagent runs.

**`memory`** — required by superclaude. Source files always use `memory: project`; the installer rewrites it at install time:
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
  - Category: specific capabilities (usually 3-5 items; fewer when the domain is narrow)
  </focus>

  <actions>
  1. Verb-leading description of the step (as many steps as the procedure has; sequence is load-bearing).
  </actions>

  <outputs>
  - Type: deliverable purpose (one item per deliverable the agent produces)
  </outputs>

  <tool_guidance>
  - Proceed: actions to do freely.
  - Symbolic-First: full or light form (see Code Exploration below).
  - Ask First: actions requiring confirmation, with specific thresholds. A delegated subagent cannot ask mid-task: where this file says to ask or confirm, stop there and return the proposed action and the question. The task text confirms only a reversible action it names with its target; a destructive or irreversible one needs the user's approval quoted in the task.
  - Never: actions the agent must never take.
  </tool_guidance>

  <checklist>
  - [ ] Concrete, verifiable completion criterion stated as one line (usually 3-5; fewer when the domain is narrow)
  </checklist>

  <memory_guide>
  MEMORY.md = prior lessons; verify against current state before acting on them.
  After task: save a lesson only if a future run would act differently, in the file layout Claude Code's memory instructions give.
  - CategoryName-Hyphenated: ≤80 chars description. Related: agent-1, agent-2 (optional, ≤3)
  </memory_guide>

  <examples>
  | Trigger | Expected behavior |
  |---|---|
  | short trigger phrase | one-line response shape |
  | another trigger | another one-line shape |
  </examples>

  <gotchas>
  - pattern-name: concrete failure + action instruction (only failures known for this domain; no filler entries)
  </gotchas>

  <bounds>
    <does>core capabilities described in prose (in-scope).</does>
    <never>out-of-scope actions described in prose.</never>
    <fallback>what goes back to the main session as an open item, and when to stop and ask; never name a sibling agent to hand work to — the main session decides what runs next.</fallback>
  </bounds>

  <handoff next="/sc:command1 /sc:command2"/>
</component>
```

### XML Rules

- `<mission>` — shares ≥30% significant words with `description`.
- All multi-word tag names use `snake_case` (`tool_guidance`, `memory_guide`).
- Short enums: **Numbered** (`1.` ordered procedures: `<actions>`), **Plain with checkbox** (`- [ ]` verification-pending criteria: `<checklist>`), **Labeled** (`- Label:` fixed-set labels: `<tool_guidance>` Proceed/Ask First/Never), **Named** (`- identifier-name:` per-item identifiers: `<focus>`, `<outputs>`, `<gotchas>`, `<memory_guide>`).
- `<examples>` — compact markdown table with minimal separators `|---|---|` for short uniform rows. For rich illustrations (code blocks, narrative, multi-turn prose), use a standalone `<example>` tag — its body is free-form prose, not locked to a `user:` / `assistant:` shape. `<examples>` and `<example>` are two distinct constructs (see xml-prose-format.md).
- `<bounds>` — sub-tag form: `<does>` / `<never>` / `<fallback>` (each tag's body is a prose sentence). `<does>` and `<never>` are required; `<fallback>` is recommended (agents are long-lived; an explicit recovery posture is high-leverage). Sub-tag form keeps `<bounds>` structurally distinct from `<tool_guidance>` (reason: xml-prose-format.md Sub-tag enumerations).
- `<handoff>` — 2-3 natural next commands.
- The `note=` attribute is restricted to scope / safety / version / reference / quantified constraint (see xml-prose-format.md "Attributes vs. Body").
- **Voice — third person.** Write "Claude does X", "the agent avoids Y" — never "you" or "I". Third person is this repo's convention for consistency across agents; the same body runs as a subagent and via `claude --agent`.
- **Ask First line.** End it with the template's delegated-subagent sentence, verbatim (`test_agent_structure.py::test_ask_first_states_subagent_behavior` pins it). A delegated subagent has no follow-up turn to ask in; without a stated behavior it either stops with nothing to show or assumes the answer and acts. The parent's task text is not the user: it confirms only a reversible action named with its target, so a parent's paraphrase cannot authorize what the kernel's destructive-op rule reserves for the user. Put an agent's core deliverable (a recommendation, a ranking, a plan) under Proceed, and only its application under Ask First, or every delegated run stops before producing it.
- **Interactive agents.** An agent whose procedure waits for the user (a menu, questions, a draft to approve) states the subagent case at that step: ``As a delegated subagent (one reply, no follow-up turns), Claude returns <the menu / the questions / the draft> and stops; the back-and-forth runs when the agent is the main session (`claude --agent <name>`).`` A delegated run gets one reply, read by the parent rather than the user, so an unstated case leaves the agent waiting for an answer that never comes or inventing one.
- **No R-ID tags.** State a rule's meaning in words, never as a `[Rnn Name]` tag: R-IDs are defined in `core/rules/RULES_QUALITY.md`, an on-demand module that never reaches a subagent, so the tag resolves to nothing (`test_agent_structure.py::test_body_has_no_rule_id_tags`).

## Memory Guide (required)

**Placement.** After `<checklist>`, before `<examples>`.

**Format.**
```xml
<memory_guide>
MEMORY.md = prior lessons; verify against current state before acting on them.
After task: save a lesson only if a future run would act differently, in the file layout Claude Code's memory instructions give.
- CategoryName-Hyphenated: what to remember (1-line, ≤80 chars). Related: agent-1, agent-2
</memory_guide>
```

**Rules.**
- Protocol header (2 lines above, verbatim identical in every agent; `test_memory_guide_has_protocol` enforces it) precedes the category list. The protocol ships in every body so it holds when CLAUDE.md is omitted (`omitClaudeMd`) or superclaude is not installed. Capture triggers worth remembering: user corrections, decisions with rationale, recurring patterns (3+), unexpected discoveries.
- The header says when to save, never how files are laid out. CC's injected memory instructions own the layout (`MEMORY.md` as an index of one-line pointers, one file per memory); an earlier entry format here (append dated lines to `MEMORY.md`, consolidate at 150 lines) contradicted them, and agents followed CC's.
- Usually 3-5 categories, specific to the agent's domain; fewer when the domain is narrow (`test_memory_guide_has_categories` requires at least 2).
- PascalCase-Hyphenated names (e.g., `Debug-Patterns`, `API-Decisions`).
- Related-agent pointers (≤3) are appended inline as "Related: agent-1, agent-2" — no nested `<refs>` tag (would violate xml-prose-format depth rule).

## Code Exploration (Symbolic-First)

Agents that read source code should include a Symbolic-First directive in `<tool_guidance>`:

| Tier | Directive | When |
|------|-----------|------|
| Reads source to index or review it (repo-index, self-review) | Full: `- Symbolic-First: with a symbol-aware tool connected (LSP or code index), query overview → definition → references before whole-file Read; without one, targeted Grep then Read of the matched range.` + optional agent-specific Grep sentence + `Read whole files only when small or non-code.` | Always |
| Touches code only in passing (none shipped today) | Light: `- Symbolic-First: prefer symbol-aware queries (when connected) or targeted Grep over whole-file Read when exploring code.` | When code may be read |
| Non-code or run-only (business-panel-experts, deep-researcher, verifier) | — | Skip |

Rationale: symbol overview vs full-file Read = significant token savings + structural understanding (refs, types, inheritance). The on-demand rule modules never reach a subagent, so the line ships in the agent body.

## Format

Body-format rules (single root, list forms, quoting, cross-references, headers inside `<example>`, size targets) live in `.claude/rules/xml-prose-format.md`, which loads together with this file. They are not restated here.

## Authoring Checklist

1. Create `src/superclaude/agents/<name>.md` (`name` matches the filename).
2. Write a 1-3 sentence `description` ending with a trigger that separates the agent from its neighbors ("Use when…"; "Use proactively …" only for agents that must run unasked) and a "Not for …" gate when a neighbor shares the verb.
3. Pick a tool access pattern — one of `tools` or `disallowedTools`, never both.
4. Omit `maxTurns` (removed from every agent in `2718f713`) and `effort` (unless measured evidence justifies it).
5. Pick `color` by role group; omit `model` (see the `model` field rule above).
6. `skills:` preloads an installed skill's body. superclaude ships none — only name one that is actually installed in the target scope.
7. Add `<memory_guide>` (required) and `<gotchas>` (recommended).
8. Run `uv run pytest tests/unit/test_agent_structure.py -v`.
9. Update `src/superclaude/agents/README.md` table.
10. Re-sync an existing install: run `superclaude doctor --scope <s>` first, because `install --force` creates an install where none exists (gotcha `sync-scope-creates`); when it reports an install, run `superclaude install --force --scope <s>`. `make deploy` reinstalls only the CLI.