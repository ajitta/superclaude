---
paths: ["src/superclaude/agents/**", ".claude/rules/agent-authoring.md"]
---

# Agent Authoring Rules

> **Decision gate:** Create an agent for **domain expertise** that CC auto-delegates on keyword match.
> - Agent = **WHO TO BE** (domain expert persona)
> - Command = **WHAT TO DO** (user-invoked workflow)
> - Skill = **WHICH CAPABILITY** (CC-native tool/hook)
> - Mode = **HOW TO THINK** (cognitive overlay)

## YAML Frontmatter (Official CC Fields Only)

```yaml
---
name: agent-name                           # required | lowercase-hyphens, matches filename
description: One-line purpose (triggers - kw1, kw2)  # required | used for auto-delegation
memory: project                            # required | source value always "project"; installer rewrites per scope (user/local)
color: blue|green|purple|yellow|orange|cyan # required | see role-group mapping below

model: opus|sonnet|haiku                   # optional | omit to inherit parent (recommended)
permissionMode: default|acceptEdits|plan|auto|dontAsk|bypassPermissions  # optional
tools: Read, Grep, Glob, Agent             # optional | allow-list (mutually exclusive with disallowedTools)
disallowedTools: Edit, Write, NotebookEdit # optional | deny-list
effort: low|medium|high|xhigh|max          # optional | omit by default; inherit from parent (v2.1.69+); xhigh requires CC 2.1.111+
maxTurns: 10-30                            # optional | positive integer turn limit
skills: [confidence-check]                 # optional | preload skills into agent session
mcpServers: [serena]                       # optional | scope MCP servers to this subagent
---
```

### Field Rules

**Forbidden**: `autonomy` (not an official CC field). Any field not documented in CC's agent spec.

**Tool access** — `tools` (allow-list) OR `disallowedTools` (deny-list), **never both**:

| Pattern | Field | Value | When |
|---------|-------|-------|------|
| Read-only + web | `tools` | `Read, Grep, Glob, Agent, WebSearch, WebFetch` | Plan/review/research agents (fails closed — **preferred**) |
| Read-only minimal | `tools` | `Read, Grep, Glob, Agent` | No web access needed |
| Execute-only | `disallowedTools` | `Edit, Write, NotebookEdit` | Runs commands, never edits files (e.g., git-workflow) |
| General | `disallowedTools` | `NotebookEdit` | Can edit code but not notebooks |
| Full access | *(omit both)* | — | Implementation agents |

**`effort`** (v2.1.69+) — **optional, omit by default.** Inherit from parent session unless you have measured evidence that a specific value materially changes output quality for this agent's domain. Must be a string (not number 1-5). Valid values: `low`, `medium`, `high`, `xhigh` (Opus 4.7 only, CC 2.1.111+), `max` (Opus 4.6/4.7 only).

Decision rule: start with no `effort` field. Add one only when omission demonstrably harms the agent's output on representative tasks.

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` env > frontmatter > session > model default.

**When `xhigh` is worth setting (Opus 4.7+):** Anthropic's prompting guidance recommends `xhigh` as the baseline for coding and agentic work — at `low`/`medium`, Opus 4.7 tends to under-think edge cases. Two safe paths:

1. **Session-level (preferred):** set `CLAUDE_CODE_EFFORT_LEVEL=xhigh` or choose `xhigh` at session start — applies uniformly to all agents and honors the user's cost-vs-quality choice.
2. **Agent-level override:** add `effort: xhigh` to a specific agent's frontmatter **only** when you have measured a quality regression for that agent at the session default.

Do not add `effort: xhigh` to an agent just because the domain "feels" coding-heavy — the session default covers that case. The framework's inherit-by-default policy (commit `8edd05d`) is intentional: it keeps cost control with the user, not the agent author.

**`maxTurns`** — turn-limit safety net:

| Category | maxTurns | When |
|----------|----------|------|
| Quick | 10 | Scanning, mechanical ops |
| Standard | 15-20 | Most agents |
| Extended | 25-30 | Deep research, complex debugging |
| Unlimited | *omit* | Orchestrators (project-manager) |

**`skills`** — preload cost ~500 tokens each. Name must match `src/superclaude/skills/` dir. Use for analytical agents that benefit from safety checks (e.g., `confidence-check`).

**`model` routing** — sonnet for execution/template/code, omit for design judgment/synthesis. Full list: `agents/README.md` Model Routing + `core/FLAGS.md` `<model_routing>`.

**`color`** — SSOT: `.claude/rules/schemas.yaml` (`agent_colors`). Role-group mapping:
`architecture` → blue | `engineering` → green | `research` → purple | `documentation` → yellow | `management` → orange | `indexing` → cyan

**`mcpServers`** — inherited from parent by default. Specify only to add servers not in parent or for explicit scoping. Most agents omit.

## XML Body Structure

```xml
<component name="agent-name" type="agent">
  <role>
    <mission>Single sentence matching description (without triggers)</mission>
    <mindset>Behavioral philosophy in 1-2 sentences</mindset>
  </role>

  <focus>
  - Category: specific capabilities (3-5 items)
  </focus>

  <actions>
  1. Verb: Description (4-5 numbered steps)
  </actions>

  <outputs>
  - Type: deliverables (3-4 items)
  </outputs>

  <tool_guidance>
  - Proceed: actions to do freely | Serena-First: prefer symbolic tools for code exploration
  - Ask First: actions requiring confirmation (with specific thresholds)
  - Never: actions the agent must never take
  </tool_guidance>

  <checklist note="Completion criteria">
    - [ ] Concrete, verifiable items (3-5)
  </checklist>

  <memory_guide>
  - CategoryName: what to remember (≤80 chars)
    <refs agents="related-agent1,related-agent2"/>
  </memory_guide>

  <examples>
  | Trigger | Output |
  |---------|--------|
  | "user input" | Expected agent response pattern |
  </examples>

  <handoff next="/sc:command1 /sc:command2"/>

  <gotchas>
  - pattern-name: Concrete failure + action instruction (2-5 items)
  </gotchas>

  <bounds should="core capabilities" avoid="out-of-scope actions" fallback="Escalation path"/>
</component>
```

### XML Rules

- `<mission>` — shares ≥30% significant words with `description`
- `<tool_guidance>` — no attributes, content only (Proceed/Ask First/Never)
- `<bounds>` — `should` + `avoid` required; `fallback` recommended (agents are long-lived; explicit recovery posture is high-leverage)
- `<handoff>` — 2-3 natural next commands
- `note=` attrs allowed only for: scope, safety ("do NOT"), version gate, reference location, quantified constraint. Remove if tag/content already conveys it

## Memory Guide (required)

**Placement**: after `<checklist>`, before `<examples>`.

**Format**:
```xml
<memory_guide>
- CategoryName: what to remember (1-line, ≤80 chars)
  <refs agents="related-agent1,related-agent2"/>
</memory_guide>
```

**Rules**:
- 3-5 categories, specific to the agent's domain
- PascalCase-Hyphenated names (e.g., `Debug-Patterns`, `API-Decisions`)
- `<refs agents="...">` — up to 3 related agents
- Source files always use `memory: project`. The installer rewrites this to match install scope: `user` → `memory: user`, `project` → unchanged, `local` → `memory: local`. This keeps agent memory storage aligned with where the agent is installed (see `cli/install_components.py::_rewrite_agent_memory_scope`).

## Code Exploration (Serena-First)

Agents that read source code should include a Serena directive in `<tool_guidance>`:

| Tier | Directive | When |
|------|-----------|------|
| Code-centric (architect, engineer, analyst) | Full: `get_symbols_overview → find_symbol → find_referencing_symbols` | Always |
| Code-adjacent (manager, writer, mentor) | Light: `prefer symbolic tools for code exploration` | When code may be read |
| Non-code (researcher, business) | — | Skip |

Rationale: symbol overview vs full-file Read = significant token savings + structural understanding (refs, types, inheritance).

## Checklist

1. Create `src/superclaude/agents/<name>.md`
2. `name` matches filename
3. Choose tool access pattern (`tools` vs `disallowedTools`, least privilege)
4. Set `maxTurns` (omit `effort` unless measured evidence justifies it)
5. Pick `color` by role group, `model` by cognitive complexity
6. Consider `skills: [confidence-check]` for analytical agents
7. Add `<memory_guide>` (required) and `<gotchas>` (recommended)
8. Run `uv run pytest tests/unit/test_agent_structure.py -v`
9. Update `src/superclaude/agents/README.md` table
10. Run `make deploy`
