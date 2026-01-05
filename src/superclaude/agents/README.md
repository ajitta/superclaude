# SuperClaude Agents

Specialized AI agent definitions for domain-specific tasks.

## Overview

Agents are pre-configured personas with specialized knowledge and behaviors. They can be invoked via the `/sc:agent` command to get expert-level assistance in specific domains.

## Available Agents

### Research & Analysis

| Agent | Description |
|-------|-------------|
| `deep-research` | Autonomous web research with parallel search |
| `deep-research-agent` | Extended deep research capabilities |
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
| `pm-agent` | Project management and planning |
| `business-panel-experts` | Business strategy multi-expert panel |

### Code Quality

| Agent | Description |
|-------|-------------|
| `self-review` | Automated code review and quality checks |
| `repo-index` | Repository indexing and context building |

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

## For Developers

### Adding New Agents

1. Create a new `.md` file in this directory
2. Define the agent's persona, expertise, and behavior
3. Include example interactions
4. Update this README with the new agent
5. Test with `/sc:agent <name>`

### Agent File Structure

```markdown
# Agent Name

## Expertise
- Domain knowledge areas

## Behavior
- How the agent approaches problems
- Communication style

## Guidelines
- Specific rules and constraints

## Output Format
- Expected response structure
```
