# SuperClaude Project Overview

## Purpose
SuperClaude is a **dual-purpose** project:
1. **Python package** — A pytest plugin + CLI tool (`superclaude`) providing PM Agent patterns (confidence checking, self-check, reflexion, parallel execution)
2. **Content framework** — Markdown files (commands, agents, modes, MCP docs, core config) installed into `~/.claude/` to configure Claude Code's behavior

## Version & Meta
- **Version**: 4.2.1+ajitta
- **Python**: >=3.10
- **Build**: hatchling (PEP 517)
- **License**: MIT
- **Package manager**: UV (never use pip directly)

## Tech Stack
- Python 3.10+, pytest, click, rich, pyyaml
- Linting: ruff (line-length 88, ignores E501)
- Formatting: ruff format (black-compatible)
- Type checking: mypy (gradual typing, `disallow_untyped_defs = false`)
- Build: hatchling
- Dev deps: pytest-cov, pytest-benchmark, pytest-asyncio, scipy, ruff, mypy

## Entry Points
- CLI: `superclaude = "superclaude.cli.main:main"` (click-based with subcommands: install, uninstall, mcp, update, install_skill, doctor, agents, skills, version)
- Pytest plugin: `superclaude = "superclaude.pytest_plugin"` (auto-loaded)

## Content Installation Flow
The CLI `superclaude install` copies content from the package to Claude Code's config directory:
```
src/superclaude/commands/  →  ~/.claude/commands/sc/     (30+ slash commands)
src/superclaude/agents/    →  ~/.claude/agents/          (20+ agent definitions)
src/superclaude/skills/    →  ~/.claude/skills/          (skill implementations)
src/superclaude/core/      →  ~/.claude/superclaude/core/  (FLAGS, PRINCIPLES, RULES)
src/superclaude/modes/     →  ~/.claude/superclaude/modes/ (7 behavioral modes)
src/superclaude/mcp/       →  ~/.claude/superclaude/mcp/   (MCP server docs + configs)
```
Mapping defined in `src/superclaude/cli/install_paths.py` (the `COMPONENTS` dict).

## Package Structure (key directories)
```
src/superclaude/
├── __init__.py          # Exports ConfidenceChecker, SelfCheckProtocol, ReflexionPattern
├── __version__.py       # Version string
├── pytest_plugin.py     # Pytest plugin entry (fixtures, hooks, markers)
├── pm_agent/            # Core Python patterns (confidence, self_check, reflexion, token_budget, task_cleanup)
├── execution/           # Parallel executor, self-correction, reflection
├── cli/                 # Click CLI (main, install_paths, install_components, install_settings, install_inventory, install_skill, install_mcp, install_commands, doctor)
├── hooks/               # Hook system (hook_tracker, inline_hooks, mcp_fallback, hooks.json)
├── commands/            # 30+ slash command markdown files
├── agents/              # 20+ agent definition markdown files
├── modes/               # 7 behavioral mode markdown files
├── mcp/                 # MCP server docs + configs/ directory with JSON configs
├── core/                # FLAGS.md, PRINCIPLES.md, RULES.md
├── skills/              # Skill implementations (confidence-check with SKILL.md)
├── scripts/             # Shell/Python utilities
├── utils/               # Utility modules
└── examples/            # Example workflows
```

## Tests
```
tests/
├── conftest.py                     # Shared fixtures
├── unit/                           # 10 unit test files
│   ├── test_confidence.py
│   ├── test_self_check.py
│   ├── test_reflexion.py
│   ├── test_token_budget.py
│   ├── test_parallel.py
│   ├── test_hooks.py
│   ├── test_hook_tracker.py
│   ├── test_mcp_fallback.py
│   └── test_cli_install.py
└── integration/
    └── test_pytest_plugin.py
```

## PM Agent Patterns
| Pattern | Class | Purpose | Threshold |
|---------|-------|---------|-----------|
| ConfidenceChecker | `pm_agent/confidence.py` | Pre-execution gate | >=90% proceed, 70-89% alternatives, <70% stop |
| SelfCheckProtocol | `pm_agent/self_check.py` | Post-validation | Evidence required |
| ReflexionPattern | `pm_agent/reflexion.py` | Error learning | Cross-session |
| TokenBudgetManager | `pm_agent/token_budget.py` | Token allocation | simple/medium/complex |

`confidence.py` uses Protocol-based design with pluggable checks: NoDuplicatesCheck, ArchitectureCheck, OfficialDocsCheck, OssReferenceCheck, RootCauseCheck, PRStatusCheck.

## Hooks System
- `hook_tracker.py`: `once: true` session tracking (24h TTL, state in `~/.claude/.superclaude_hooks/`)
- `inline_hooks.py`: Frontmatter parser for skill/command metadata (context, agent, user-invocable, allowed-tools, hooks)
- `mcp_fallback.py`: MCP server availability fallback handling

## Git Workflow
- Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`
- Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
