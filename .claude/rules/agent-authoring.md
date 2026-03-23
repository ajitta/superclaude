# Agent Authoring Rules

When creating or modifying agent `.md` files in `src/superclaude/agents/`, follow these rules exactly.

## YAML Frontmatter (Official Claude Code Fields Only)

```yaml
---
name: agent-name                           # required | lowercase + hyphens, must match filename
description: One-line purpose (triggers - keyword1, keyword2)  # required | used for auto-delegation
model: opus|sonnet|haiku                   # optional | omit to inherit parent model (recommended)
permissionMode: plan|default|acceptEdits   # required | system-enforced permission level
memory: project                            # required | always "project" for SuperClaude agents
disallowedTools: Edit, Write, NotebookEdit # optional | comma-separated, least privilege
color: blue|green|purple|yellow|orange|cyan # required | by role group
---
```

### Field Rules

**Forbidden fields** — never include in frontmatter:
- `autonomy` — not an official Claude Code field, silently ignored
- Any field not documented in Claude Code's agent specification

**disallowedTools by role pattern**:
| Pattern | disallowedTools | When to use |
|---------|-----------------|-------------|
| Read-only (plan, review, research, indexing) | `Edit, Write, NotebookEdit` | Agent should never modify files |
| Execute-only (Bash but no file edits) | `Edit, Write, NotebookEdit` | Agent runs commands but never modifies files (e.g., git-workflow) |
| General work (default mode) | `NotebookEdit` | Agent can edit code but not notebooks |
| Full access (implementation) | *(omit field)* | Agent needs all tools |

**model routing**:
- Default: omit `model:` field — agent inherits parent session's model (recommended)
- Override: set `model:` explicitly only when a specific model is required regardless of user's session choice
- Use sparingly — explicit `model:` overrides the user's cost/speed preference

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
  - Proceed: actions the agent should do freely
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

  <bounds will="core capabilities" wont="out-of-scope actions" fallback="Escalation path"/>
</component>
```

### XML Rules

- `<tool_guidance>` — NO attributes. Behavioral rules only (Proceed/Ask First/Never)
- `<bounds>` — must include `will`, `wont`, and `fallback` attributes
- `<mcp>` — only list servers the agent actually uses
- `<mission>` text must share 30%+ significant words with `description`
- `<handoff>` — list 2-3 natural next commands

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

## Checklist for New Agents

1. Create `src/superclaude/agents/<name>.md` with frontmatter + XML body
2. Verify `name` matches filename (without `.md`)
3. Set `permissionMode` → `disallowedTools` following least privilege
4. Add `<memory_guide>` section (see below)
5. Run `uv run pytest tests/unit/test_agent_structure.py -v`
6. Update `src/superclaude/agents/README.md` agent table
7. Run `make deploy`

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
