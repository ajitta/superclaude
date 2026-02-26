# SuperClaude Agents

Specialized AI agent definitions for domain-specific tasks.

## Overview

Agents are pre-configured personas with specialized knowledge and behaviors. They can be invoked via the `/sc:agent` command to get expert-level assistance in specific domains.

## Available Agents

### Research & Analysis

| Agent | Description |
|-------|-------------|
| `deep-research-agent` | Web research with cross-checking and citation-ready synthesis |
| `root-cause-analyst` | Systematic problem diagnosis |
| `requirements-analyst` | Requirements gathering and analysis |

### Architecture & Design

| Agent | Description |
|-------|-------------|
| `system-architect` | System design and architecture decisions |
| `backend-architect` | Backend systems and API design |
| `frontend-architect` | Frontend architecture and UI patterns |
| `devops-architect` | Infrastructure and deployment architecture |

### Engineering Specialists

| Agent | Description |
|-------|-------------|
| `python-expert` | Python best practices and optimization |
| `security-engineer` | Security analysis and hardening |
| `performance-engineer` | Performance optimization and profiling |
| `quality-engineer` | Quality assurance and testing strategies |
| `refactoring-expert` | Code refactoring and modernization |

### Documentation & Communication

| Agent | Description |
|-------|-------------|
| `technical-writer` | Technical documentation and guides |
| `learning-guide` | Educational content and tutorials |
| `socratic-mentor` | Teaching through guided questioning |

### Project & Business

| Agent | Description |
|-------|-------------|
| `pm-agent` | Self-improvement workflow: document implementations, analyze mistakes, maintain knowledge |
| `business-panel-experts` | Business strategy multi-expert panel |

### Philosophy & Discipline

| Agent | Description |
|-------|-------------|
| `simplicity-guide` | Complexity prevention through Orient-Step-Learn (Dave Thomas) |

### Code Quality

| Agent | Description |
|-------|-------------|
| `self-review` | Post-implementation validation and reflexion partner |
| `repo-index` | Repository indexing and codebase briefing assistant |

## Usage

### Via Command

```
/sc:agent python-expert "How should I structure this async code?"
/sc:agent security-engineer "Review this authentication flow"
/sc:agent system-architect "Design a scalable message queue"
```

### Direct Invocation

Agents can also be loaded directly for extended conversations:

```
/sc:load agents/backend-architect
```

## Agent Capabilities

Each agent includes:

- **Expertise Domain**: Specific knowledge area
- **Behavioral Guidelines**: How the agent approaches problems
- **Output Format**: Structured response patterns
- **Tool Preferences**: Recommended tools for the domain
- **Autonomy Level**: Permission boundaries for actions
- **Permission Mode**: Claude Code `permissionMode` enforced via frontmatter (v4.2)
- **Persistent Memory**: Cross-session learning via `memory` frontmatter (v2.1.33)

## Agent Memory (v2.1.33)

Agents can declare persistent memory that survives across conversations:

```yaml
---
name: agent-name
description: Agent description
memory: project
---
```

### Memory Scopes

| Scope | Location | Use Case |
|-------|----------|----------|
| `project` | `.claude/agent-memory/<name>/` | Project-specific knowledge, committable (SuperClaude default) |
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project learnings |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, gitignored |

When `memory` is set, the agent automatically gets Read/Write/Edit tools and the first 200 lines of its `MEMORY.md` are injected into the system prompt. All SuperClaude agents use `memory: project` for project-scoped, committable knowledge.

## Sub-Agent Restrictions (v2.1.33)

Agents can restrict which sub-agents they can spawn using `Task(agent_type)` syntax in the `tools` frontmatter field:

```yaml
---
name: orchestrator
description: Coordinates specialized agents
tools: Read, Grep, Task(code-reviewer), Task(debugger)
---
```

Without this restriction, an agent with Task access can spawn any available subagent. Use this for controlled multi-agent workflows. The `Task(AgentName)` deny pattern can disable specific agents in `disallowedTools`.

## Autonomy Framework

Agents operate under three autonomy levels that map to Claude Code's `permissionMode` for system-level enforcement:

### Level Definitions

| Level | permissionMode | Effect | User Interaction |
|-------|---------------|--------|------------------|
| **high** | `acceptEdits` | File edits auto-approved; Bash/MCP still require approval | Inform after completion |
| **medium** | `default` | Each tool prompted on first use | Confirm before execution |
| **low** | `plan` | Read-only; all modifications blocked until user approves | Confirm each major step |

### Autonomy by Agent

| Agent | Model | Autonomy | permissionMode | Rationale |
|-------|-------|----------|---------------|-----------|
| `deep-research-agent` | opus | high | acceptEdits | Read-only web research, no code changes |
| `python-expert` | sonnet | high | acceptEdits | Code generation/analysis, user reviews output |
| `frontend-architect` | sonnet | high | acceptEdits | UI patterns/components, no infrastructure changes |
| `quality-engineer` | sonnet | high | acceptEdits | Test strategy/analysis, non-destructive |
| `repo-index` | haiku | high | acceptEdits | Read-only indexing and briefing |
| `learning-guide` | sonnet | high | acceptEdits | Educational content, non-destructive |
| `performance-engineer` | sonnet | high | acceptEdits | Measurement/analysis, non-destructive |
| `backend-architect` | sonnet | medium | default | API contracts affect multiple systems |
| `pm-agent` | sonnet | medium | default | Orchestration decisions need oversight |
| `devops-architect` | sonnet | medium | default | Infrastructure changes are significant |
| `refactoring-expert` | sonnet | medium | default | Safe refactoring patterns with user review |
| `self-review` | opus | medium | default | Validation findings need user judgment |
| `socratic-mentor` | sonnet | medium | default | Teaching guidance affects learning path |
| `requirements-analyst` | opus | medium | default | Specification decisions need stakeholder input |
| `root-cause-analyst` | opus | medium | default | Investigation requiring careful judgment |
| `technical-writer` | sonnet | medium | default | Documentation with user-facing impact |
| `system-architect` | opus | low | plan | Architecture decisions have broad impact |
| `security-engineer` | opus | low | plan | Security policies require explicit review |
| `business-panel-experts` | opus | low | plan | Strategy decisions require business context |
| `simplicity-guide` | opus | low | plan | Simplification judgments require deep context |

### Tool Guidance Semantics

Each agent's `<tool_guidance>` section follows these rules:

```xml
<tool_guidance autonomy="level">
  <proceed conditions="read-only|analysis|non-binding|hypothesis">
    Actions that don't change state or make commitments
  </proceed>
  <ask_first conditions="state-change|binding-decision|cross-boundary">
    Actions that modify code, config, or affect other systems
  </ask_first>
  <never conditions="destructive|irreversible|unilateral">
    Actions that could cause data loss or bypass review
  </never>
</tool_guidance>
```

### Escalation Rules

1. **Uncertainty**: When unsure about scope → escalate to `ask_first`
2. **Cross-boundary**: When action affects another agent's domain → escalate
3. **Risk**: When action has >10% chance of breaking change → escalate
4. **Context pressure**: When context >85% → compress output, don't skip steps

### Cross-Agent Conflict Resolution

When agents give conflicting recommendations, resolve using this priority matrix:

| Conflict | Resolution | Rationale |
|----------|-----------|-----------|
| security-engineer vs performance-engineer | security wins | Security constraints are non-negotiable |
| simplicity-guide vs system-architect | data decides — measure complexity vs scale requirements | Neither overrides without evidence |
| refactoring-expert vs quality-engineer | quality-engineer sets coverage gate, refactoring-expert executes within it | Tests define safe refactoring boundaries |
| frontend-architect vs backend-architect | API contract negotiation — both propose, user decides | Interface boundaries require explicit agreement |
| python-expert vs system-architect | system-architect for cross-language/service boundaries, python-expert within Python scope | Scope determines authority |
| devops-architect vs security-engineer | security-engineer for policy, devops-architect for implementation | Policy before implementation |

**General rule**: Domain specialist wins within their domain; cross-domain conflicts escalate to user.

## For Developers

### Adding New Agents

1. Create a new `.md` file in this directory
2. Define the agent's persona, expertise, and behavior
3. Include example interactions
4. Update this README with the new agent
5. Test with `/sc:agent <name>`

### Agent File Structure

```yaml
---
name: agent-name
description: Brief description (triggers - keyword1, keyword2)
model: opus|sonnet|haiku                  # Sub-agent model routing (v4.2)
autonomy: high|medium|low                 # Permission boundaries (v2.1.37)
permissionMode: acceptEdits|default|plan  # Claude Code enforcement (v4.2)
memory: project                           # Persistent memory scope (v2.1.33)
---
```

```xml
<component name="agent-name" type="agent">
  <mcp servers="seq|c7"/>
  <tool_guidance autonomy="high|medium|low">
    ...
  </tool_guidance>
  <!-- Domain-specific sections -->
</component>
```
