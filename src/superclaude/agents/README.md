# SuperClaude Agents

Domain expert personas — specialized AI agent definitions for task-based auto-delegation.

## Content Delivery

Agents are managed by Claude Code's native agent delegation system. Auto-selected based on task keywords in the `description` frontmatter field. Installed to `~/.claude/agents/` on `superclaude install`.

## Available Agents

### Research & Analysis

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `deep-researcher` | opus | acceptEdits | Web research with cross-checking and citation-ready synthesis |
| `root-cause-analyst` | opus | default | Systematic problem diagnosis through hypothesis testing |
| `requirements-analyst` | opus | default | Requirements gathering through systematic discovery |

### Architecture & Design

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `system-architect` | opus | plan | System design and long-term architecture decisions |
| `backend-architect` | sonnet | default | Backend systems, API design, data integrity |
| `frontend-architect` | sonnet | acceptEdits | Frontend architecture, accessibility, UI patterns |
| `devops-architect` | sonnet | default | Infrastructure, CI/CD, deployment automation |

### Engineering Specialists

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `python-expert` | sonnet | acceptEdits | Python best practices, SOLID principles |
| `security-engineer` | opus | plan | Security analysis, OWASP, threat modeling |
| `performance-engineer` | sonnet | acceptEdits | Performance optimization and profiling |
| `quality-engineer` | sonnet | acceptEdits | Testing strategies and edge case detection |
| `refactoring-expert` | sonnet | default | Code quality improvement and tech debt reduction |

### Documentation & Education

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `technical-writer` | sonnet | default | Technical documentation tailored to audiences |
| `learning-guide` | sonnet | acceptEdits | Progressive learning and practical examples |
| `socratic-mentor` | sonnet | default | Teaching through guided questioning |

### Project & Business

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `project-manager` | sonnet | default | Orchestration, workflow management, continuous improvement |
| `business-panel-experts` | opus | plan | Multi-lens business strategy synthesis and debate |

### Philosophy & Discipline

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `simplicity-guide` | opus | plan | Complexity prevention through Orient-Step-Learn |

### Git & Workflow

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `git-workflow` | sonnet | default | Git operations with intelligent commits, PR workflow, and safety enforcement |

### Code Quality

| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `self-review` | opus | default | Post-implementation validation and reflexion |
| `repo-index` | haiku | acceptEdits | Repository indexing and codebase briefing |

## Permission Framework

| permissionMode | Effect |
|---------------|--------|
| `acceptEdits` | File edits auto-approved; Bash/MCP prompted |
| `default` | Each tool prompted on first use |
| `plan` | Read-only; modifications blocked until approved |

Model routing: `opus` for architecture/security/judgment | `sonnet` for coding/analysis/docs | `haiku` for mechanical scanning

## Authoring Rules

See `.claude/rules/agent-authoring.md` for the complete authoring specification.

Validation: `uv run python -m pytest tests/unit/test_agent_structure.py -v`

## Agent Memory (v2.1.33)

Agents declare persistent memory that survives across conversations via the `memory` frontmatter field. All SuperClaude agents use `memory: project`.

| Scope | Location | Use Case |
|-------|----------|----------|
| `project` | `.claude/agent-memory/<name>/` | Project-specific knowledge, committable |
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project learnings |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, gitignored |

When `memory` is set, the agent automatically gets Read/Write/Edit tools and the first 200 lines of its `MEMORY.md` are injected into the system prompt.

## Escalation Rules

1. **Uncertainty**: When unsure about scope → escalate to `ask_first`
2. **Cross-boundary**: When action affects another agent's domain → escalate
3. **Risk**: When action has >10% chance of breaking change → escalate
4. **Context pressure**: When context >85% → compress output, don't skip steps

## Cross-Agent Conflict Resolution

When agents give conflicting recommendations:

| Conflict | Resolution | Rationale |
|----------|-----------|-----------|
| security-engineer vs performance-engineer | security wins | Security constraints are non-negotiable |
| simplicity-guide vs system-architect | data decides — measure complexity vs scale | Neither overrides without evidence |
| refactoring-expert vs quality-engineer | quality-engineer sets coverage gate, refactoring-expert executes within it | Tests define safe refactoring boundaries |
| frontend-architect vs backend-architect | API contract negotiation — both propose, user decides | Interface boundaries require explicit agreement |
| python-expert vs system-architect | system-architect for cross-language/service boundaries, python-expert within Python scope | Scope determines authority |
| devops-architect vs security-engineer | security-engineer for policy, devops-architect for implementation | Policy before implementation |

**General rule**: Domain specialist wins within their domain; cross-domain conflicts escalate to user.

## Related

- `commands/` — Workflow entry points that route to agents
- `modes/` — Cognitive overlays that shape agent behavior
- `core/FLAGS.md` — Model routing and persona index
