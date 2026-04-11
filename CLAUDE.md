# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

This project uses **UV** for all Python operations. Never use `pip` or `python -m pytest` directly.

```bash
# Tests
uv run pytest                              # Full suite
uv run pytest tests/unit/ -v               # Unit tests only
uv run pytest tests/integration/ -v        # Integration tests
uv run pytest -k "test_agent"              # By name pattern

# Test baseline
# 1,787 collected, ~1,628 passing (12 pre-existing failures, 6 collection errors)
# Tests are docs-change-safe: markdown-only changes carry no test risk

# Development workflow
uv pip install -e ".[dev]"                 # Install editable (RECOMMENDED)
uv run superclaude install --list-all      # Test CLI changes
make deploy                                # Deploy to global tool (recommended)
```

## Make Commands

```bash
make install       # uv pip install -e ".[dev]"
make deploy        # Deploy to global uv tool (editable, changes reflect immediately)
make test          # uv run pytest
make test-plugin   # Verify pytest plugin loads
make verify        # Full installation check
make lint          # ruff check
make format        # ruff format
make doctor        # Health check
make clean         # Remove artifacts
```

## Architecture

SuperClaude is a **content framework** — markdown files (commands, agents, modes, skills, MCP docs, core config) installed into `~/.claude/` to configure Claude Code's behavior. It also ships a CLI (`superclaude`) and a minimal pytest plugin for auto-markers.

**Full taxonomy:** See `src/superclaude/ARCHITECTURE.md` for directory roles, delivery pipelines, and content type definitions.

| Directory | Role | Delivery |
|-----------|------|----------|
| `core/` | Framework DNA — always-applied principles and rules | Always loaded (CLAUDE_SC.md @import) |
| `modes/` | Mindset overlay — situational cognitive frameworks | On-demand (context_loader) |
| `agents/` | Domain expert — specialized agent definitions | CC-native auto-delegation |
| `commands/` | Workflow entry — user-facing /sc:* slash commands | CC-native slash commands |
| `skills/` | Runtime hooks, safety, and reference knowledge — CC-native | CC-native (hooks, disable-model-invocation, auto-invocation) |
| `mcp/` | Tool reference — 9 MCP server docs + configuration | context_loader + install_mcp |
| `scripts/` | Hook infrastructure — Python/shell automation | hooks.json → settings.json |

### Content Installation Flow

```
src/superclaude/commands/  →  ~/.claude/commands/sc/       (33 slash commands)
src/superclaude/agents/    →  ~/.claude/agents/             (23 agent definitions)
src/superclaude/skills/    →  ~/.claude/skills/             (5 skills: 2 hook, 2 safety, 1 reference)
src/superclaude/core/      →  ~/.claude/superclaude/core/   (FLAGS, PRINCIPLES, RULES, BUSINESS_SYMBOLS)
src/superclaude/mcp/       →  ~/.claude/superclaude/mcp/    (MCP server documentation)
```

Install logic in `cli/`: `install_paths.py` (paths) → `install_settings.py` (hooks/CLAUDE.md) → `install_components.py` (orchestration) → `install_inventory.py` (listing) → `install_commands.py` (wiring).

### Key Decisions

- **Editable install**: `make deploy` uses `uv tool install --editable .` — changes in `src/` reflect immediately.
- **CLAUDE_SC.md import chain**: `@superclaude/CLAUDE_SC.md` → `core/FLAGS.md`, `PRINCIPLES.md`, `RULES.md`.
- **Hooks merge (not replace)**: `install_settings.py` preserves user hooks via marker-based identification.
- **Template variables**: `{{SCRIPTS_PATH}}` and `{{SKILLS_PATH}}` resolved at install time.

### Authoring Rules

`.claude/rules/` contains 4 authoring guides enforced by tests:
- `agent-authoring.md` — frontmatter, XML structure, memory_guide
- `command-authoring.md` — frontmatter, component type, bounds
- `skill-authoring.md` — YAML fields, archetypes, hooks
- `mode-authoring.md` — 4-axis requirement, no frontmatter

### Serena Integration

`.serena/` contains project configuration and session memories for the Serena MCP server. These are committed to the repo for cross-session context.

### Project Gotchas

Project-specific failure patterns live in `.claude/rules/gotchas/`. CC loads these natively.

    .claude/rules/gotchas/
    ├── general.md              # No paths: → always loaded
    └── <domain>.md             # paths: frontmatter → conditional loading

- **Format**: `- name: description` (one gotcha per line, same as framework `<gotchas>`)
- **Creation**: `/sc:init` task [h] creates `general.md`. Domain files are proposed by R19 on first correction.
- **paths: example**: `paths: ["**/models/**"]` → loads only when working on model files
- **Limits**: 50 lines per file, 100 lines total recommended
- **Gardening**: `# Last reviewed: YYYY-MM-DD` at top. `/sc:reflect` warns on 90-day+ staleness.
- **Layer priority**: Project gotcha (Layer 2) > Personal preference (Layer 3)

## Git Workflow

Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Package Info

- **Version**: 4.4.1+ajitta
- **Python**: >=3.10
- **Build**: hatchling (PEP 517)
- **Deps**: pytest>=7.0.0, click>=8.0.0, rich>=13.0.0, pyyaml>=6.0.0
- **Linting**: ruff (line-length 88, ignores E501)
