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
| `insight-analyst` | Surface project insights with contextual analysis |

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
| `git-workflow` | Git ops with smart commits, PR workflow, safety enforcement |

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

Every agent omits `model:` and inherits the parent session model — no agent pins a tier.

Rationale mirrors the `effort:` removal in commit `8edd05d`: no hardcoded model without measured evidence. Pinning a tier overrides the user's cost-vs-quality choice for the session, and a pin written against one model generation silently misroutes after the next.

Resolution order: per-invocation `model` parameter > frontmatter `model:` > `CLAUDE_CODE_SUBAGENT_MODEL` > main conversation model (Claude Code v2.1.251+).

Moving work to Fable 5.1 is the user's call. Each path lasts a different length:

| Path | How long it lasts |
|---|---|
| `claude --model fable` | That session only (a later `--continue` or `--resume` of it restores Fable). The recommended "when needed" path, because it never changes the saved default |
| `/model fable` | Saved to user settings, so later sessions also start on Fable, until `/model default`; in `-p` mode it applies to that session only |
| `/model` picker, `s` on the Fable row | This session only; the saved default stays unchanged |
| Asking for one delegation on Fable | That delegation only: the Agent tool call carries `model: "fable"` |
| `CLAUDE_CODE_SUBAGENT_MODEL=fable` | Every subagent that no per-invocation parameter or frontmatter assigns a model (built-in Explore and Plan, and forks, excepted) |

When Fable 5.1: Anthropic's routing advice is "Most workloads start with Claude Opus 5.5"; move to Fable 5.1 when your evals at `xhigh` or `max` effort still fall short on demanding reasoning or long-horizon agentic work. Claude Code describes Fable as suited to "tasks larger than a single sitting". At list price Fable 5.1 costs 2.5× Opus 5.5 on input and output ($10/$50 against $4/$20 per MTok) and 1.25× on cache reads ($0.25 against $0.20), which Anthropic says "make up the majority of agentic and coding work costs". Where a plan bills Fable to usage credits, `-p` mode and the Agent SDK bill it without the consent prompt that interactive sessions show.

## Authoring Rules

See `.claude/rules/agent-authoring.md` for full authoring spec.

Validation: `uv run python -m pytest tests/unit/test_agent_structure.py -v`

## Agent Memory (v2.1.33)

Agents declare persistent memory via `memory` frontmatter. Source files ship `memory: project`; installer rewrites to match install scope. Full spec (scope→location table, `_rewrite_agent_memory_scope` mechanics, MEMORY.md injection): `.claude/rules/agent-authoring.md` § memory.

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
| simplicity-guide vs system-architect | data decides — measure complexity vs scale | Neither overrides without evidence |
| refactoring-expert vs quality-engineer | quality-engineer sets coverage gate, refactoring-expert executes within | Tests define safe refactor boundaries |
| frontend-architect vs backend-architect | API contract negotiation — both propose, user decides | Interface boundaries need explicit agreement |
| python-expert vs system-architect | system-architect for cross-lang/service boundaries, python-expert within Python scope | Scope determines authority |
| devops-architect vs security-engineer | security-engineer for policy, devops-architect for impl | Policy before impl |

**General rule**: Domain specialist wins within domain; cross-domain conflicts escalate to user.

## Related

- `commands/` — Workflow entry points routing to agents
- `modes/` — Cognitive overlays shaping agent behavior
- `core/FLAGS.md` — Behavioral flags + execution modes (Model Routing lives in this README's section above)
- `okf/superclaude/agents/index.md` — OKF v0.1 catalog: agents as concept docs, resource-linked to source (repo-root bundle)