# SuperClaude Skills

Execution containers — reusable capabilities with hooks, tool restrictions, and optional subagent isolation.

## Content Delivery

Skills are managed by Claude Code's native skill system. Auto-detected via `description` keyword matching at startup (only `name` + `description` loaded initially, ~30-50 tokens each). Full `SKILL.md` loaded on invocation. Installed to `~/.claude/skills/` on `superclaude install`.

## Available Skills

### Process Skills (ported from superpowers)

| Skill | Description |
|-------|-------------|
| `executing-plans` | Execute implementation plans with structured tracking |
| `receiving-code-review` | Process and apply code review feedback |
| `requesting-code-review` | Generate structured code review requests |
| `finishing-a-development-branch` | Branch completion with quality gates |
| `using-git-worktrees` | Git worktree workflow for parallel development |
| `using-superclaude` | Meta-skill for SuperClaude framework usage |
| `dispatching-parallel-agents` | Parallel agent orchestration patterns |

### Development Skills

| Skill | Description |
|-------|-------------|
| `brainstorming` | Structured brainstorming with diverge/converge |
| `confidence-check` | Pre-execution confidence assessment |
| `ship` | Production deployment workflow |
| `simplicity-coach` | Complexity prevention guidance |
| `systematic-debugging` | Structured debugging methodology |
| `test-driven-development` | TDD workflow with red/green/refactor |
| `verification-before-completion` | Final verification gates |
| `writing-plans` | Implementation plan authoring |

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
| `context` | `inline` (default) or `fork` (subagent) | `context: fork` |
| `agent` | Subagent type (requires `context: fork`) | `agent: Explore` |
| `allowed-tools` | Tool whitelist | `Read, Grep, Glob` |
| `disable-model-invocation` | Block Claude auto-execution | `true` for destructive workflows |

## Context Modes

### `context: inline` (default)
- Executes in the current conversation context
- Shares memory and state with parent
- Lower overhead, faster execution

### `context: fork` (v2.1.0+)
- Executes in a forked sub-agent context
- Isolated memory and state, can use different model
- Progress visible in parent thread
- Note: `context: fork` + `agent:` via Skill tool may not be honored (GitHub #17283)

## Skill Discovery

Skills are discovered from (in order):
1. `~/.claude/skills/` — user-level
2. `.claude/skills/` — project-level
3. Nested `.claude/skills/` directories (v2.1.6+)
4. Additional directories via `--add-dir` flag (v2.1.20+)

Skills created or modified are immediately available without restarting (hot reload, v2.1.0+).

## Argument Syntax (v2.1.19+)

Skills accept arguments passed after the skill name:

| Syntax | Description |
|--------|-------------|
| `$ARGUMENTS` | Full argument string |
| `$ARGUMENTS[0]` / `$0` | First argument |
| `$ARGUMENTS[1]` / `$1` | Second argument |

Example: `/deploy my-app staging` → `Deploy my-app to the staging environment.`

## Token Budget (v2.1.32+)

Skill character budgets scale dynamically at ~2% of the context window:
- Only `name` + `description` loaded at startup (~30-50 tokens each)
- Full `SKILL.md` content loaded on invocation
- Keep SKILL.md under 1,500-2,000 words for optimal loading

## Authoring Rules

See `.claude/rules/skill-authoring.md` for the complete authoring specification (frontmatter reference, three archetypes, validation checklist).

## Related

- `commands/` — Workflow entry points that may invoke skills
- `agents/` — Domain personas that skills can fork to
- `scripts/skill_activator.py` — Skill activation logic
- `hooks/` — Hook system that skills integrate with
