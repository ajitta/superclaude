# SuperClaude Agents

Domain expert personas — specialized AI agent definitions for task-based auto-delegation.

## Content Delivery

Agents are managed by Claude Code's native agent delegation system. Auto-selected based on task keywords in the `description` frontmatter field. Installed to `~/.claude/agents/` on `superclaude install`.

## Available Agents

### Research & Analysis

| Agent | Permission | Description |
|-------|------------|-------------|
| `deep-researcher` | acceptEdits | Web research with cross-checking and citation-ready synthesis |
| `root-cause-analyst` | default | Systematic problem diagnosis through hypothesis testing |
| `requirements-analyst` | default | Requirements gathering through systematic discovery |

### Architecture & Design

| Agent | Permission | Description |
|-------|------------|-------------|
| `system-architect` | plan | System design and long-term architecture decisions |
| `backend-architect` | default | Backend systems, API design, data integrity |
| `frontend-architect` | acceptEdits | Frontend architecture, accessibility, UI patterns |
| `devops-architect` | default | Infrastructure, CI/CD, deployment automation |

### Engineering Specialists

| Agent | Permission | Description |
|-------|------------|-------------|
| `python-expert` | acceptEdits | Python best practices, SOLID principles |
| `security-engineer` | plan | Security analysis, OWASP, threat modeling |
| `performance-engineer` | acceptEdits | Performance optimization and profiling |
| `quality-engineer` | acceptEdits | Testing strategies and edge case detection |
| `refactoring-expert` | default | Code quality improvement and tech debt reduction |

### Documentation & Education

| Agent | Permission | Description |
|-------|------------|-------------|
| `technical-writer` | default | Technical documentation tailored to audiences |
| `learning-guide` | acceptEdits | Progressive learning and practical examples |
| `socratic-mentor` | default | Teaching through guided questioning |

### Project & Business

| Agent | Permission | Description |
|-------|------------|-------------|
| `project-initializer` | default | Interactive project environment setup for first-session onboarding |
| `project-manager` | default | Orchestration, workflow management, continuous improvement |
| `business-panel-experts` | plan | Multi-lens business strategy synthesis and debate |

### Philosophy & Discipline

| Agent | Permission | Description |
|-------|------------|-------------|
| `simplicity-guide` | plan | Complexity prevention through Orient-Step-Learn |

### Git & Workflow

| Agent | Permission | Description |
|-------|------------|-------------|
| `git-workflow` | default | Git operations with intelligent commits, PR workflow, and safety enforcement |

### Code Quality

| Agent | Permission | Description |
|-------|------------|-------------|
| `self-review` | default | Post-implementation validation and reflexion |
| `repo-index` | acceptEdits | Repository indexing and codebase briefing |

## Permission Framework

| permissionMode | Effect |
|---------------|--------|
| `acceptEdits` | File edits auto-approved; Bash/MCP prompted |
| `default` | Each tool prompted on first use |
| `plan` | Read-only; modifications blocked until approved |

## Model Routing

All agents inherit the parent session's model by default — no `model:` field in frontmatter.
To pin a specific model, add `model: opus|sonnet|haiku` to frontmatter (not recommended — overrides user's choice).

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
