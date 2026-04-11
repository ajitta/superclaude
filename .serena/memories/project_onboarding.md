# SuperClaude Framework - Project Onboarding

## Overview
SuperClaude v4.4.0+ajitta is a content framework for Claude Code with 33 slash commands, 23 agents, 5 skills, and 7 behavioral modes.

## Key Entry Points
- **CLI**: `superclaude` → `src/superclaude/cli/main.py:main`
- **CLI subcommands**: install, uninstall, update, mcp, doctor, agents, skills, install-skill, version
- **Pytest Plugin**: Auto-loaded via pyproject.toml entry point (auto-markers only)

## Core Modules (src/superclaude/)

### CLI Install Architecture
- install_paths.py — Path resolution, COMPONENTS dict (leaf dependency)
- install_settings.py — Settings/hooks/CLAUDE.md management (leaf dependency)
- install_components.py — Orchestration (imports paths + settings)
- install_commands.py — Top-level command wiring
- install_skill.py — Skill install with {{SKILLS_PATH}} template resolution
- install_mcp.py — MCP server configuration (hardcoded MCP_SERVERS dict)

Key behaviors:
- Hooks merge (not replace) into settings.json via SUPERCLAUDE_HOOK_MARKERS
- CLAUDE_SC.md import added to ~/.claude/CLAUDE.md, chains to core/FLAGS+PRINCIPLES+RULES
- make deploy uses `uv tool install --editable .` for instant changes

### Hooks System
- `hook_tracker.py`: `once: true` session tracking (24h TTL, state in `~/.claude/.superclaude_hooks/`)
- `inline_hooks.py`: Frontmatter parser for skill/command metadata
- `mcp_fallback.py`: MCP server availability fallback handling

## Directory Structure
- agents/: 23 specialized agent definitions (.md) + README
- commands/: 33 slash command definitions (.md) + README
- modes/: 7 behavioral mode definitions (MODE_*.md)
- mcp/: MCP server docs (8 documentation files)
- core/: FLAGS.md, PRINCIPLES.md, RULES.md, BUSINESS_SYMBOLS.md
- skills/: 5 skill directories with SKILL.md manifests
- hooks/: Hook definitions, session tracking, frontmatter parser, MCP fallback
- utils/: Shared utilities (atomic_write_json)
- scripts/: context_loader.py, session_init.py, token_estimator.py, skill_activator.py

## Testing
- Framework: pytest>=7.0.0
- Location: tests/unit/, tests/integration/
- **~1,628 tests passing** (1 pre-existing failure)
- Run: `uv run pytest` or `python -m pytest`

## Development Workflow
```bash
uv pip install -e ".[dev]"  # Install editable
uv run superclaude install  # Install commands
uv run pytest               # Run tests
make deploy                 # Deploy as global tool (editable)
make lint                   # ruff check
make format                 # ruff format
```

## Key Files
- CLAUDE.md: Claude Code instructions (authoritative project reference)
- CHANGELOG.md: Version history
- pyproject.toml: Package configuration (hatchling, Python >=3.10)

## Agent Frontmatter (v4.4.0)
All 23 agents have:
- `name`, `description`, `memory: project`
- `permissionMode` field
- `color` by role group
- `<bounds should="..." avoid="..."/>` sections
- 15/23 agents have `<gotchas>` sections for critical rule reinforcement
