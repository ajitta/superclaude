# Agent Authoring Rules

When creating or modifying agent `.md` files in `src/superclaude/agents/`, follow these rules exactly.

## YAML Frontmatter (Official Claude Code Fields Only)

```yaml
---
name: agent-name                           # required | lowercase + hyphens, must match filename
description: One-line purpose (triggers - keyword1, keyword2)  # required | used for auto-delegation
model: opus|sonnet|haiku                   # required | see model routing below
permissionMode: plan|default|acceptEdits   # required | system-enforced permission level
memory: project                            # required | always "project" for SuperClaude agents
maxTurns: 15|25|50                         # required | must match permissionMode
disallowedTools: Edit, Write, NotebookEdit # optional | comma-separated, least privilege
color: blue|green|purple|yellow|orange|cyan # required | by role group
---
```

### Field Rules

**Forbidden fields** — never include in frontmatter:
- `autonomy` — not an official Claude Code field, silently ignored
- Any field not documented in Claude Code's agent specification

**permissionMode → maxTurns mapping** (strict):
| permissionMode | maxTurns | Use Case |
|---------------|----------|----------|
| `plan` | 15 | Analysis/planning only, no code modification |
| `default` | 25 | Moderate work, user confirms tool use |
| `acceptEdits` | 50 | Large implementation, file edits auto-approved |

**disallowedTools by role pattern**:
| Pattern | disallowedTools | When to use |
|---------|-----------------|-------------|
| Read-only (plan, review, research, indexing) | `Edit, Write, NotebookEdit` | Agent should never modify files |
| Execute-only (Bash but no file edits) | `Edit, Write, NotebookEdit` | Agent runs commands but never modifies files (e.g., git-workflow) |
| General work (default mode) | `NotebookEdit` | Agent can edit code but not notebooks |
| Full access (implementation) | *(omit field)* | Agent needs all tools |

**model routing heuristic**:
- `opus` — architecture, security, judgment, deep analysis, strategy
- `sonnet` — coding, documentation, analysis, testing, teaching
- `haiku` — mechanical scanning, indexing, low-complexity reads

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
- permissionMode → maxTurns consistency
- color in valid set
- No `autonomy` field
- XML structure (component, role, mission, mindset, tool_guidance, bounds)
- Mission ↔ description word overlap (≥30%)
- tool_guidance has content (Proceed/Ask First/Never)
- Non-empty sections

## Checklist for New Agents

1. Create `src/superclaude/agents/<name>.md` with frontmatter + XML body
2. Verify `name` matches filename (without `.md`)
3. Set `permissionMode` → `maxTurns` → `disallowedTools` following least privilege
4. Run `uv run pytest tests/unit/test_agent_structure.py -v`
5. Update `src/superclaude/agents/README.md` agent table
6. Run `make deploy`
