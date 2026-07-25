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
| `ship` | disable-model-invocation + PreToolUse hook | Protect destructive delivery workflow from auto-exec; hook blocks force push |
| `finishing-a-development-branch` | disable-model-invocation + allowed-tools + PreToolUse hook | Protect branch completion; restrict to Bash, Read, Grep, Glob; hook blocks destructive git ops |

### Safety Skills
| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `simplicity-coach` | disable-model-invocation + scripts | Explicit OSL coaching; dependency audit via in-session script (no Stop hook) |

### Reference Skills
| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `confidence-check` | Reference skill (auto-invocation) | Validate assumptions w/ evidence before plan/design/spec/impl |
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

## Related

- `commands/` — Workflow entry points (most former skills now live here)
- `agents/` — Domain expert agents
- `hooks/` — Hook system skills integrate with
- `okf/superclaude/skills/index.md` — OKF v0.1 catalog: 5 skills as concept docs, resource-linked to source (repo-root bundle)