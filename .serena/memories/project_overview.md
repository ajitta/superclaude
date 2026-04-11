# SuperClaude Project Overview

## Purpose
SuperClaude is a **content framework** — markdown files (commands, agents, modes, skills, MCP docs, core config) installed into `~/.claude/` to configure Claude Code's behavior. It also ships a CLI (`superclaude`) and a minimal pytest plugin for auto-markers.

## Version & Meta
- **Version**: 4.4.1+ajitta
- **Python**: >=3.10
- **Build**: hatchling (PEP 517)
- **License**: MIT
- **Package manager**: UV (never use pip directly)

## Tech Stack
- Python 3.10+, pytest, click, rich, pyyaml
- Linting: ruff (line-length 88, ignores E501)
- Build: hatchling
- Dev deps: pytest-cov, ruff

## Entry Points
- CLI: `superclaude = "superclaude.cli.main:main"` (click-based with subcommands: install, uninstall, mcp, update, install_skill, doctor, agents, skills, version)
- Pytest plugin: `superclaude = "superclaude.pytest_plugin"` (auto-loaded)

## Content Installation Flow
```
src/superclaude/commands/  →  ~/.claude/commands/sc/       (33 slash commands)
src/superclaude/agents/    →  ~/.claude/agents/             (23 agent definitions)
src/superclaude/skills/    →  ~/.claude/skills/             (5 skills)
src/superclaude/core/      →  ~/.claude/superclaude/core/   (FLAGS, PRINCIPLES, RULES)
src/superclaude/modes/     →  ~/.claude/superclaude/modes/  (7 behavioral modes)
src/superclaude/mcp/       →  ~/.claude/superclaude/mcp/    (MCP server documentation)
```

## Package Structure
```
src/superclaude/
├── __init__.py          # Package root
├── __version__.py       # Version string
├── pytest_plugin.py     # Pytest plugin entry (auto-markers)
├── cli/                 # Click CLI (main, install_*, doctor)
├── hooks/               # Hook system (hook_tracker, inline_hooks, mcp_fallback)
├── commands/            # 33 slash command markdown files
├── agents/              # 23 agent definition markdown files + README
├── modes/               # 7 behavioral mode markdown files (MODE_*.md)
├── mcp/                 # MCP server documentation (8 docs)
├── core/                # FLAGS.md, PRINCIPLES.md, RULES.md, BUSINESS_SYMBOLS.md
├── skills/              # 5 skills with SKILL.md manifests
├── scripts/             # context_loader.py, session_init.py, token_estimator.py, skill_activator.py
└── utils/               # Shared utilities (atomic_write_json)
```

## Tests
- **~1,628 tests passing** (1 pre-existing failure)
- Location: tests/unit/, tests/integration/
- Run: `uv run pytest` or `python -m pytest`

## Git Workflow
- Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`
- Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
