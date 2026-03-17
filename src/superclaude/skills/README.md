# SuperClaude Skills

CC-native execution containers limited to capabilities that commands and agents cannot provide.

## When to Use Skills (vs Commands/Agents)

| Need | Content Type | Why |
|------|-------------|-----|
| Lifecycle hooks (PreToolUse, Stop) | **Skill** | Only skills can attach runtime hooks |
| Block auto-invocation | **Skill** | Only skills have `disable-model-invocation` |
| Tool restriction (allowed-tools) | **Skill** | Only skills whitelist tools at runtime |
| Script execution | **Skill** | Only skills have `{{SKILLS_PATH}}` resolution |
| Workflow procedures | **Command** | Commands define WHAT TO DO |
| Domain expertise | **Agent** | Agents define WHO TO BE |
| Cognitive overlay | **Mode** | Modes define HOW TO THINK |

## Current Skills (4)

| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `confidence-check` | PreToolUse hook | Injects evidence-focus guidance on WebFetch/WebSearch |
| `simplicity-coach` | Stop hook + scripts | Runs dependency audit at session end |
| `ship` | disable-model-invocation | Protects destructive delivery workflow from auto-execution |
| `finishing-a-development-branch` | disable-model-invocation + allowed-tools | Protects branch completion; restricts to Bash, Read, Grep, Glob |

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
| `description` | Auto-invocation trigger (critical) | Task keywords for detection |
| `allowed-tools` | Tool whitelist | `Read, Grep, Glob` |
| `disable-model-invocation` | Block Claude auto-execution | `true` for destructive workflows |
| `hooks` | Lifecycle hooks | `PreToolUse`, `Stop` |

## Skill Discovery

Skills are discovered from (in order):
1. `~/.claude/skills/` — user-level
2. `.claude/skills/` — project-level
3. Nested `.claude/skills/` directories (v2.1.6+)

Skills created or modified are immediately available without restarting (hot reload).

## Authoring Guide

See `.claude/rules/skill-authoring.md` for the complete authoring specification.

**Key rule:** Only create a skill when you need a CC-native capability (hooks, safety, scripts). Workflow procedures belong in `commands/`. Domain expertise belongs in `agents/`.

## Related

- `commands/` — Workflow entry points (most former skills now live here)
- `agents/` — Domain personas
- `hooks/` — Hook system that skills integrate with
