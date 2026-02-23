# SuperClaude Framework - Project Onboarding

## Overview
SuperClaude v4.2.1+ajitta is an AI-enhanced development framework for Claude Code with pytest plugin, 31 slash commands, 21 agents, and 8 behavioral modes.

## Key Entry Points
- **CLI**: `superclaude` → `src/superclaude/cli/main.py:main`
- **CLI subcommands**: install, uninstall, update, mcp, doctor, agents, skills, install-skill, version
- **Pytest Plugin**: Auto-loaded via pyproject.toml entry point
- **Fixtures**: confidence_checker, self_check_protocol, reflexion_pattern, token_budget, pm_context

## Core Modules (src/superclaude/)

### PM Agent Pattern
| Module | Class | Purpose |
|--------|-------|---------|
| pm_agent/confidence.py | ConfidenceChecker | Pre-execution assessment (≥90% proceed) |
| pm_agent/self_check.py | SelfCheckProtocol | Post-implementation validation |
| pm_agent/reflexion.py | ReflexionPattern | Error learning, cross-session patterns (JSONL) |
| pm_agent/token_budget.py | TokenBudgetManager | Token allocation (200/1000/2500) |
| pm_agent/task_cleanup.py | TaskCleanupManager | Stale task removal (24h threshold) |

### Execution
- execution/parallel.py: Wave→Checkpoint→Wave (3.5x faster)
- execution/reflection.py: Meta-reasoning
- execution/self_correction.py: Error recovery

### Confidence Checks (confidence.py)
Protocol-based design with pluggable checks. DEFAULT_CHECKS (5):
- NoDuplicatesCheck (0.25), ArchitectureCheck (0.25), OfficialDocsCheck (0.20), OssReferenceCheck (0.15), RootCauseCheck (0.15)
- PRStatusCheck exists but must be registered manually (not in DEFAULT_CHECKS)
- ConfidenceResult supports numeric comparison via __float__

## CLI Install Architecture
- install_paths.py — Path resolution, COMPONENTS dict (leaf dependency)
- install_settings.py — Settings/hooks/CLAUDE.md management (leaf dependency)
- install_components.py — Orchestration (imports paths + settings)
- install_commands.py — Top-level command wiring
- install_skill.py — Skill install with {{SKILLS_PATH}} template resolution
- install_mcp.py — MCP server configuration

Key behaviors:
- Hooks merge (not replace) into settings.json via SUPERCLAUDE_HOOK_MARKERS
- CLAUDE_SC.md import added to ~/.claude/CLAUDE.md, chains to core/FLAGS+PRINCIPLES+RULES
- make deploy uses `uv tool install --editable .` for instant changes

## Directory Structure
- agents/: 21 specialized agent definitions (.md)
- commands/: 31 slash command definitions (.md)
- modes/: 8 behavioral mode definitions (.md)
- mcp/: MCP server docs + configs/
- core/: FLAGS.md, PRINCIPLES.md, RULES.md
- skills/: Skill directories with SKILL.md manifests (confidence-check, simplicity-coach)
- hooks/: Hook definitions, session tracking, frontmatter parser, MCP fallback
- utils/: Shared utilities (atomic_write_json)
- scripts/: Shell/Python utilities (context_reset.py, session_init.py, etc.)

## Testing
- Framework: pytest≥7.0.0
- Location: tests/unit/ (10 files), tests/integration/ (1 file)
- Run: `uv run pytest`
- Custom markers: confidence_check, self_check, reflexion, complexity(level), hallucination, performance

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
- PLANNING.md: Architecture, design principles, absolute rules
- TASK.md: Current tasks and priorities
- KNOWLEDGE.md: Accumulated insights, troubleshooting
- CHANGELOG.md: Version history
- pyproject.toml: Package configuration (hatchling, Python >=3.10)
