# SuperClaude Agents

Domain expert agents — AI agent defs for task-based auto-delegation.

## Content Delivery

Agents managed by Claude Code native delegation. Auto-pick from task keywords in `description` frontmatter. Install to `~/.claude/agents/` on `superclaude install`.

## Available Agents

### Research & Analysis

| Agent | Permission | Description |
|-------|------------|-------------|
| `deep-researcher` | acceptEdits | Web research, cross-check, citation-ready synthesis |
| `root-cause-analyst` | default | Systematic diagnosis via hypothesis test |
| `requirements-analyst` | default | Requirements via systematic discovery |
| `insight-analyst` | default | Surface project insights w/ contextual analysis |

### Architecture & Design

| Agent | Permission | Description |
|-------|------------|-------------|
| `system-architect` | plan | System design + long-term arch decisions |
| `backend-architect` | default | Backend, API design, data integrity |
| `frontend-architect` | acceptEdits | Frontend arch, a11y, UI patterns |
| `devops-architect` | default | Infra, CI/CD, deploy automation |

### Engineering Specialists

| Agent | Permission | Description |
|-------|------------|-------------|
| `python-expert` | acceptEdits | Python best practices, SOLID |
| `security-engineer` | plan | Security analysis, OWASP, threat modeling |
| `performance-engineer` | acceptEdits | Perf optimization + profiling |
| `quality-engineer` | acceptEdits | Test strategy + edge case detection |
| `refactoring-expert` | default | Code quality + tech debt reduction |

### Documentation & Education

| Agent | Permission | Description |
|-------|------------|-------------|
| `technical-writer` | default | Tech docs tailored to audience |
| `learning-guide` | acceptEdits | Progressive learning + practical examples |
| `socratic-mentor` | default | Teach via guided questioning |

### Project & Business

| Agent | Permission | Description |
|-------|------------|-------------|
| `project-initializer` | default | Interactive project setup for first-session onboarding |
| `project-manager` | default | Orchestration, workflow mgmt, continuous improvement |
| `business-panel-experts` | plan | Multi-lens biz strategy synthesis + debate |

### Philosophy & Discipline

| Agent | Permission | Description |
|-------|------------|-------------|
| `simplicity-guide` | plan | Complexity prevention via Orient-Step-Learn |

### Git & Workflow

| Agent | Permission | Description |
|-------|------------|-------------|
| `git-workflow` | default | Git ops w/ smart commits, PR workflow, safety enforcement |

### Code Quality

| Agent | Permission | Description |
|-------|------------|-------------|
| `self-review` | default | Post-impl validation + reflexion |
| `repo-index` | acceptEdits | Repo indexing + codebase briefing |

## Permission Framework

| permissionMode | Effect |
|---------------|--------|
| `acceptEdits` | File edits auto-approve; Bash/MCP prompt |
| `default` | Each tool prompts on first use |
| `plan` | Read-only; mods blocked till approved |

## Model Routing

11 agents pinned `model: sonnet` (exec/template), 12 inherit parent (judgment/synthesis).

| Tier | model: | Agents | Criteria |
|------|--------|--------|----------|
| Sonnet | `sonnet` | repo-index, git-workflow, project-initializer, technical-writer, learning-guide, socratic-mentor, quality-engineer, python-expert, performance-engineer, frontend-architect, insight-analyst | Procedural, template-driven, codegen |
| Opus | *(inherit)* | system-architect, deep-researcher, business-panel-experts, simplicity-guide, root-cause-analyst, requirements-analyst, backend-architect, security-engineer, project-manager, devops-architect, refactoring-expert, self-review | Design judgment, high reversal cost, multi-framework synthesis |

Override: set `model:` in agent frontmatter to change routing.

## Authoring Rules

See `.claude/rules/agent-authoring.md` for full authoring spec.

Validation: `uv run python -m pytest tests/unit/test_agent_structure.py -v`

## Agent Memory (v2.1.33)

Agents declare persistent memory surviving across convos via `memory` frontmatter. Source files ship `memory: project`; installer rewrites to match install scope so storage follows intent.

| Install scope | Installed `memory:` | Location | Rationale |
|---|---|---|---|
| `user` | `user` | `~/.claude/agent-memory/<name>/` | Global agent — no pollute foreign project cwds |
| `project` | `project` | `.claude/agent-memory/<name>/` | Team-shared, committed w/ repo |
| `local` | `local` | `.claude/agent-memory-local/<name>/` | Personal, gitignored by CC |

Rewrite happens during `install_component("agents", ..., scope=...)` via `_rewrite_agent_memory_scope`. Source files never modified.

When `memory` set, agent auto-gets Read/Write/Edit tools and first 200 lines of `MEMORY.md` inject into system prompt.

## Escalation Rules

1. **Uncertainty**: scope unclear → escalate to `ask_first`
2. **Cross-boundary**: action hits another agent domain → escalate
3. **Risk**: >10% chance of breaking change → escalate
4. **Context pressure**: context >85% → compress output, don't skip steps

## Cross-Agent Conflict Resolution

Agents give conflicting recs → resolve via:

| Conflict | Resolution | Rationale |
|----------|-----------|-----------|
| security-engineer vs performance-engineer | security wins | Security constraints non-negotiable |
| simplicity-guide vs system-architect | data decides — measure complexity vs scale | Neither overrides w/o evidence |
| refactoring-expert vs quality-engineer | quality-engineer sets coverage gate, refactoring-expert executes within | Tests define safe refactor boundaries |
| frontend-architect vs backend-architect | API contract negotiation — both propose, user decides | Interface boundaries need explicit agreement |
| python-expert vs system-architect | system-architect for cross-lang/service boundaries, python-expert within Python scope | Scope determines authority |
| devops-architect vs security-engineer | security-engineer for policy, devops-architect for impl | Policy before impl |

**General rule**: Domain specialist wins within domain; cross-domain conflicts escalate to user.

## Related

- `commands/` — Workflow entry points routing to agents
- `modes/` — Cognitive overlays shaping agent behavior
- `core/FLAGS.md` — Model routing + --p flag agent mapping