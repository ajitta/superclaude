# Agent Authoring Rules

When creating or modifying agent `.md` files in `src/superclaude/agents/`, follow these rules exactly.

## YAML Frontmatter (Official Claude Code Fields Only)

```yaml
---
name: agent-name                           # required | lowercase + hyphens, must match filename
description: One-line purpose (triggers - keyword1, keyword2)  # required | used for auto-delegation
model: opus|sonnet|haiku                   # optional | omit to inherit parent model (recommended)
permissionMode: default|acceptEdits|plan|auto|dontAsk|bypassPermissions  # optional | overridden by parent's auto/bypassPermissions
memory: project                            # required | always "project" for SuperClaude agents
disallowedTools: Edit, Write, NotebookEdit # optional | comma-separated, deny-list (see tool access below)
tools: Read, Grep, Glob, Agent             # optional | comma-separated, allow-list (see tool access below)
color: blue|green|purple|yellow|orange|cyan # required | by role group
effort: low|medium|high|max               # optional | reasoning depth (v2.1.69+, max is Opus 4.6 only)
maxTurns: 10-30                            # optional | turn limit safety net (positive integer)
skills:                                    # optional | preload skills into agent session
  - confidence-check
mcpServers:                                # optional | MCP servers scoped to this subagent
---
```

### Field Rules

**Forbidden fields** — never include in frontmatter:
- `autonomy` — not an official Claude Code field, silently ignored
- Any field not documented in Claude Code's agent specification

**Tool access** — use `tools` (allow-list) OR `disallowedTools` (deny-list), never both:

| Pattern | Field | Value | When to use |
|---------|-------|-------|-------------|
| Read-only (plan, review, research) | `tools` | `Read, Grep, Glob, Agent, WebSearch, WebFetch` | Agent should only read/search — **preferred** for restrictive agents |
| Read-only minimal | `tools` | `Read, Grep, Glob, Agent` | Agent should only read/search, no web access |
| Execute-only (Bash but no file edits) | `disallowedTools` | `Edit, Write, NotebookEdit` | Agent runs commands but never modifies files (e.g., git-workflow) |
| General work (default mode) | `disallowedTools` | `NotebookEdit` | Agent can edit code but not notebooks |
| Full access (implementation) | *(omit both)* | — | Agent needs all tools |

**Rule:** `tools` and `disallowedTools` are mutually exclusive. Use `tools` (allow-list) for restrictive agents — it fails closed when CC adds new tools. Use `disallowedTools` (deny-list) for permissive agents where listing allowed tools would be impractical.

**effort** (v2.1.69+) — adaptive reasoning depth:
| Value | Use for | Examples |
|-------|---------|----------|
| `low` | Mechanical/structured tasks | repo-index, git-workflow, technical-writer |
| `medium` | Standard design + analysis (default if omitted) | architects, engineers, mentors |
| `high` | Complex reasoning, deep debugging | system-architect, security-engineer, root-cause-analyst |
| `max` | Multi-perspective synthesis (**Opus 4.6 only**) | deep-researcher, business-panel-experts |

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` env > frontmatter `effort` > session setting > model default (medium).

**⚠ Values must be strings** (`low`/`medium`/`high`/`max`), not numbers. CC does not accept numeric effort values (1-5).

**maxTurns** — turn limit safety net:
| Category | maxTurns | When |
|----------|----------|------|
| Quick | 10 | Scanning, mechanical ops (repo-index, git-workflow) |
| Standard | 15-20 | Most agents — analysis + output |
| Extended | 25-30 | Deep research, complex debugging |
| Unlimited | *(omit)* | Orchestrators (project-manager) |

**skills** — preload skills into agent session:
- Use `skills:` to preload safety/validation skills (e.g., `confidence-check` for analytical agents)
- Token cost: ~500 tokens per preloaded skill — acceptable for safety improvement
- Each skill name must match an existing directory in `src/superclaude/skills/`

**model routing**:
- Sonnet-tier (11 agents): execution/template/code tasks → `model: sonnet` pinned in frontmatter
- Opus-tier (11 agents): design judgment/synthesis/security tasks → omit `model:` (inherit parent, typically Opus)
- New agents: assess cognitive complexity — procedural → sonnet, nuanced judgment → omit
- See `agents/README.md` Model Routing table and `core/FLAGS.md` `<model_routing>` for full list

**color by role group**:
| Group | color | Roles |
|-------|-------|-------|
| Architecture | `blue` | system design, frontend, backend, devops |
| Engineering | `green` | coding, security, performance, quality, refactoring |
| Research | `purple` | investigation, research, requirements |
| Documentation | `yellow` | writing, teaching, mentoring |
| Management | `orange` | orchestration, business, review, simplicity |
| Indexing | `cyan` | repository scanning |

## XML Body Structure

Every agent body follows this template order:

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

  <mcp servers="seq|c7|..."/>

  <tool_guidance>
  - Proceed: actions the agent should do freely | Serena-First: prefer symbolic tools for code exploration
  - Ask First: actions requiring user confirmation (with specific thresholds)
  - Never: actions the agent must never take
  </tool_guidance>

  <checklist note="Completion criteria">
    - [ ] Concrete, verifiable items (3-5)
  </checklist>

  <examples>
  | Trigger | Output |
  |---------|--------|
  | "user input" | Expected agent response pattern |
  </examples>

  <handoff next="/sc:command1 /sc:command2"/>

  <gotchas note="Recommended — project-specific failure patterns, placement: after handoff, before bounds">
  - pattern-name: Concrete failure + action instruction (2-5 items)
  </gotchas>

  <bounds should="core capabilities" avoid="out-of-scope actions" fallback="Escalation path"/>
</component>
```

### XML Rules

- `<tool_guidance>` — NO attributes. Behavioral rules only (Proceed/Ask First/Never)
- `<bounds>` — must include `should`, `avoid`, and `fallback` attributes
- `<mcp>` — only list servers the agent actually uses
- `<mission>` text must share 30%+ significant words with `description`
- `<handoff>` — list 2-3 natural next commands
- No decorative attributes — `note=` is allowed ONLY when it adds: scope/applicability ("all commands"), safety directives ("do NOT"), version gates ("2.1.37+"), reference locations ("see X.md"), or quantified constraints ("3-6", "strict call order"). Remove if tag name or content already conveys the same meaning.

## mcpServers Field

`mcpServers` is an official Claude Code frontmatter field for scoping MCP servers to a subagent:

```yaml
mcpServers:
  - serena                                 # string reference: uses parent's existing connection
  - custom-server:                         # inline definition: starts new server for subagent
      type: stdio
      command: npx
      args: ["-y", "@custom/mcp-server"]
```

**Note**: Sub-agents inherit all parent MCP tools by default. Use `mcpServers` only to add servers not in the parent session or for explicit scoping. Most agents should omit this field.

## Code Exploration Pattern

Agents that explore source code should include a Serena-first directive in `<tool_guidance>`:

| Agent Tier | Directive | When |
|-----------|-----------|------|
| Code-centric (architect, engineer, analyst) | Full: `get_symbols_overview → find_symbol → find_referencing_symbols` | Always |
| Code-adjacent (manager, writer, mentor) | Light: `prefer symbolic tools for code exploration` | When code may be read |
| Non-code (researcher, business) | None | Skip |

**Rationale**: Serena symbolic tools provide significant token reduction vs Read for code exploration (symbol overview vs full file read), plus structural understanding (references, types, inheritance).

**Note**: `<mcp servers="...">` is a documentation-only convention (no runtime effect). The official CC field `mcpServers` (frontmatter) provides actual MCP server scoping.

## Validation

After creating/modifying an agent, run:
```bash
uv run pytest tests/unit/test_agent_structure.py -v
```

This validates:
- All required frontmatter fields present and valid
- color in valid set
- No `autonomy` field
- XML structure (component, role, mission, mindset, tool_guidance, bounds)
- Mission ↔ description word overlap (≥30%)
- tool_guidance has content (Proceed/Ask First/Never)
- Non-empty sections
- `<gotchas>` presence (recommended, not required — no test failure if missing)
- Optional fields (if present): effort in `low|medium|high|max`, maxTurns is positive integer
- `tools` and `disallowedTools` are mutually exclusive
- `skills` references existing skill directories

## Checklist for New Agents

1. Create `src/superclaude/agents/<name>.md` with frontmatter + XML body
2. Verify `name` matches filename (without `.md`)
3. Set `permissionMode` → tool access (`tools` or `disallowedTools`) following least privilege
4. Set `effort` (low/medium/high/max) and `maxTurns` safety net
5. Consider `skills` preload (e.g., `confidence-check` for analytical agents)
6. Add `<memory_guide>` section (see below)
7. Add `<gotchas>` section (recommended — project-specific failure patterns, 2-5 items)
8. Run `uv run pytest tests/unit/test_agent_structure.py -v`
9. Update `src/superclaude/agents/README.md` agent table
10. Run `make deploy`

## Memory Guide (required)

Every agent must include a `<memory_guide>` section in the XML body.

**Placement:** After `<checklist>`, before `<examples>`.

**Format:**
```xml
<memory_guide>
- CategoryName: what to remember (1-line, max 80 chars)
  <refs agents="related-agent1,related-agent2"/>
</memory_guide>
```

**Rules:**
- 3-5 memory categories per agent, specific to the agent's domain
- Category names: PascalCase-Hyphenated (e.g., `Debug-Patterns`, `API-Decisions`)
- Each category: noun phrase + colon + what to remember (max 80 chars)
- `<refs>`: list agents whose memory may be relevant (max 3)
- All agents use `memory: project` scope

**Validation:** `test_agent_structure.py` checks:
- `<memory_guide>` section exists
- Contains at least 2 category entries (lines starting with `- `)
- Contains `<refs agents="..."/>` with valid agent names
