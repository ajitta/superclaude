# SuperClaude Agents

Domain expert agents — AI agent defs for task-based auto-delegation.

## Content Delivery

Agents managed by Claude Code native delegation. Auto-pick from task keywords in `description` frontmatter. Install to `~/.claude/agents/` on `superclaude install`.

## Available Agents

### Research & Analysis

| Agent | Description |
|-------|-------------|
| `deep-researcher` | Web research, cross-check, citation-ready synthesis |
| `root-cause-analyst` | Systematic diagnosis via hypothesis test |
| `requirements-analyst` | Requirements via systematic discovery |
| `insight-analyst` | Surface project insights w/ contextual analysis |

### Architecture & Design

| Agent | Description |
|-------|-------------|
| `system-architect` | System design + long-term arch decisions |
| `backend-architect` | Backend, API design, data integrity |
| `frontend-architect` | Frontend arch, a11y, UI patterns |
| `devops-architect` | Infra, CI/CD, deploy automation |

### Engineering Specialists

| Agent | Description |
|-------|-------------|
| `python-expert` | Python best practices, SOLID |
| `security-engineer` | Security analysis, OWASP, threat modeling |
| `performance-engineer` | Perf optimization + profiling |
| `quality-engineer` | Test strategy + edge case detection |
| `refactoring-expert` | Code quality + tech debt reduction |

### Documentation & Education

| Agent | Description |
|-------|-------------|
| `technical-writer` | Tech docs tailored to audience |
| `learning-guide` | Progressive learning + practical examples |
| `socratic-mentor` | Teach via guided questioning |

### Project & Business

| Agent | Description |
|-------|-------------|
| `project-initializer` | Interactive project setup for first-session onboarding |
| `project-manager` | Orchestration, workflow mgmt, continuous improvement |
| `business-panel-experts` | Multi-lens biz strategy synthesis + debate |

### Philosophy & Discipline

| Agent | Description |
|-------|-------------|
| `simplicity-guide` | Complexity prevention via Orient-Step-Learn |

### Git & Workflow

| Agent | Description |
|-------|-------------|
| `git-workflow` | Git ops w/ smart commits, PR workflow, safety enforcement |

### Code Quality

| Agent | Description |
|-------|-------------|
| `self-review` | Post-impl validation + reflexion |
| `repo-index` | Repo indexing + codebase briefing |

## Permission Framework

No shipped agent sets `permissionMode` — all inherit the session's permission mode (frontmatter field stripped in 672055c as unreliable). CC-native values remain available for local overrides:

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
| Inherit | *(inherit)* | system-architect, deep-researcher, business-panel-experts, simplicity-guide, root-cause-analyst, requirements-analyst, backend-architect, security-engineer, project-manager, devops-architect, refactoring-expert, self-review | Design judgment, high reversal cost, multi-framework synthesis — resolves to the parent session model (current flagship, e.g. Fable 5) |

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
- `core/FLAGS.md` — Behavioral flags + execution modes (Model Routing lives in this README's section above)
- `okf/superclaude/agents/index.md` — OKF v0.1 catalog: 23 agents as concept docs, resource-linked to source (repo-root bundle)