# SuperClaude Skills

CC-native containers for hooks, safety, script exec, and auto-invoke ref knowledge.

## When to Use Skills (vs Commands/Agents)

| Need | Content Type | Why |
|------|-------------|-----|
| Lifecycle hooks (PreToolUse, Stop) | **Skill** | Only skills attach runtime hooks |
| Block auto-invocation | **Skill** | Only skills got `disable-model-invocation` |
| Tool restriction (allowed-tools) | **Skill** | Only skills whitelist tools at runtime |
| Script execution | **Skill** | Only skills got `{{SKILLS_PATH}}` resolution |
| Auto-trigger reference knowledge | **Skill** | CC matches skill descriptions to auto-load domain protocols |
| Workflow procedures | **Command** | Commands define WHAT TO DO |
| Domain expertise | **Agent** | Agents define WHO TO BE |
| Cognitive overlay | **Mode** | Modes define HOW TO THINK |

## Current Skills (5)

### Hook Skills
| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `confidence-check` | PreToolUse hook | Inject evidence-focus guidance on WebFetch/WebSearch |
| `simplicity-coach` | Stop hook + scripts | Run dependency audit at session end |

### Safety Skills
| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `ship` | disable-model-invocation | Protect destructive delivery workflow from auto-exec |
| `finishing-a-development-branch` | disable-model-invocation + allowed-tools | Protect branch completion; restrict to Bash, Read, Grep, Glob |

### Reference Skills
| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `verbalized-sampling` | Reference skill (auto-invocation) | Research-backed diverse response gen via distribution-level prompting |

## Skill Directory Structure

```
<skill-name>/
├── SKILL.md          ← Entry point (frontmatter + XML body)
├── scripts/          ← Execution scripts (Python, Bash)
├── references/       ← Documentation, reference materials
└── assets/           ← Templates, binaries
```

## Key Frontmatter Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | Auto-invoke trigger (critical) | Task keywords for detection |
| `allowed-tools` | Tool whitelist | `Read, Grep, Glob` |
| `disable-model-invocation` | Block Claude auto-exec | `true` for destructive workflows |
| `hooks` | Lifecycle hooks | `PreToolUse`, `Stop` |

## Skill Discovery

Skills found from (in order):
1. `~/.claude/skills/` — user-level
2. `.claude/skills/` — project-level
3. Nested `.claude/skills/` dirs (v2.1.6+)

Skills made or changed available immediately, no restart (hot reload).

## Authoring Guide

See `.claude/rules/skill-authoring.md` for full authoring spec.

**Key rule:** Make skill when need CC-native capability (hooks, safety, scripts) or auto-invoke ref knowledge (CC description matching). Workflow procedures go in `commands/`. Domain expertise go in `agents/`.

## Related

- `commands/` — Workflow entry points (most former skills now live here)
- `agents/` — Domain expert agents
- `hooks/` — Hook system skills integrate with