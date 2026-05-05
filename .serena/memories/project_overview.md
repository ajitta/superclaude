# SuperClaude — Project Overview

## Purpose
SuperClaude is a **content framework** for Claude Code. It installs markdown files (commands, agents, modes, skills, MCP docs, core config) into `~/.claude/` to configure Claude Code's behavior. It also ships a CLI (`superclaude`) and a pytest plugin for auto-markers.

## Tech Stack
- **Language**: Python ≥ 3.10
- **Package manager**: UV (never use pip or python -m pytest directly)
- **Linting/formatting**: ruff (line-length 88, ignores E501)
- **Testing**: pytest via `uv run pytest`
- **CLI entry point**: `superclaude` (installed via `uv tool install --force --editable .`)

## Key Architecture Points
- Content lives in `src/superclaude/`: agents/, commands/, modes/, skills/, mcp/, core/, hooks/, scripts/, templates/, utils/
- `CLAUDE_SC.md` import chain: `@superclaude/CLAUDE_SC.md` → `core/FLAGS.md`, `PRINCIPLES.md`, `RULES.md`
- Hooks merge (not replace): `install_settings.py` preserves user hooks via marker-based identification
- Template variables `{{SCRIPTS_PATH}}` and `{{SKILLS_PATH}}` resolved at install time
- Full taxonomy: `src/superclaude/ARCHITECTURE.md`

## Test Baseline
- 1,628 passing / 1,807 collected — do not regress
- Markdown-only changes carry no test risk
