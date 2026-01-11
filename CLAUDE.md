# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

This project uses **UV** for all Python operations.

```bash
# Tests
uv run pytest                         # Full suite
uv run pytest tests/unit/ -v          # Unit tests only
uv run pytest tests/integration/ -v   # Integration tests only
uv run pytest tests/unit/test_confidence.py -v  # Single file
uv run pytest -m confidence_check     # By marker
uv run pytest -k "test_assess"        # By name pattern

# Development
uv pip install -e ".[dev]"            # Install editable (RECOMMENDED)
uv run superclaude install --list-all # Test CLI changes
uv tool install --force .             # Deploy to global tool
```

## Make Commands

```bash
make install      # uv pip install -e ".[dev]"
make test         # uv run pytest
make test-plugin  # Verify pytest plugin loads
make verify       # Full installation check
make lint         # ruff check
make format       # ruff format
make doctor       # Health check
make clean        # Remove artifacts
```

## Architecture

```
src/superclaude/
├── pytest_plugin.py     # Entry point (auto-loaded via pyproject.toml)
├── pm_agent/            # Pre/post implementation patterns
│   ├── confidence.py    # Pre-execution check (≥90% to proceed)
│   ├── self_check.py    # Post-implementation validation
│   ├── reflexion.py     # Cross-session error learning
│   └── token_budget.py  # simple: 200, medium: 1000, complex: 2500
├── execution/
│   ├── parallel.py      # Wave→Checkpoint→Wave (3.5x faster)
│   └── self_correction.py
├── cli/
│   ├── main.py          # superclaude command entry
│   ├── doctor.py        # Health checks
│   ├── install_skill.py # Skill installation
│   └── install_mcp.py   # MCP server configs
├── hooks/
│   ├── hook_tracker.py  # once: true session tracking
│   └── inline_hooks.py  # Frontmatter hook parser
├── agents/              # 20 agent definitions (.md)
├── commands/            # 30 slash commands (.md)
├── modes/               # 8 behavioral modes (.md)
├── mcp/                 # MCP server docs + configs/
└── skills/              # Skill implementations
```

## Entry Points (pyproject.toml)

```toml
[project.scripts]
superclaude = "superclaude.cli.main:main"

[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"
```

## Pytest Plugin

Auto-loaded after `uv pip install -e .`. Provides fixtures and markers.

**Fixtures**: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Auto-markers** (path-based):
- Tests in `tests/unit/` → `@pytest.mark.unit`
- Tests in `tests/integration/` → `@pytest.mark.integration`

**Custom markers** (pyproject.toml):
- `confidence_check` - Pre-execution assessment
- `self_check` - Post-implementation validation
- `reflexion` - Error learning
- `complexity(level)` - Token budget (simple/medium/complex)
- `hallucination` - Hallucination detection
- `performance` - Benchmarks

```python
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    context = {"test_name": "test_feature", "has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.7

@pytest.mark.complexity("medium")
def test_with_budget(token_budget):
    assert token_budget.limit == 1000
```

## PM Agent Patterns

| Pattern | Purpose | Threshold |
|---------|---------|-----------|
| ConfidenceChecker | Pre-execution gate | ≥90% proceed, 70-89% alternatives, <70% stop |
| SelfCheckProtocol | Post-validation | Evidence required, no speculation |
| ReflexionPattern | Error learning | Cross-session pattern matching |
| Parallel Execution | Wave→Checkpoint→Wave | 3.5x speedup |

## CLI Commands

```bash
# Installation
superclaude install              # Install to ~/.claude/
superclaude install --scope project  # Install to ./.claude/
superclaude uninstall            # Remove components
superclaude update               # Force reinstall

# Component info
superclaude agents --list        # List 20 agents
superclaude agents --info <name> # Agent details
superclaude skills --list        # List skills
superclaude skills --info <name> # Skill details

# MCP servers
superclaude mcp --list           # List 10 servers
superclaude mcp --servers tavily context7  # Install specific
superclaude mcp --scope local    # To .mcp.json

# Utilities
superclaude doctor               # Health check
superclaude install-skill <name> # Individual skill
```

## Hooks System

Located in `src/superclaude/hooks/`. Claude Code v2.1.0 compatible.

**Frontmatter fields**:
- `context: inline|fork` - Execution context
- `agent: <name>` - Agent type for skill
- `user-invocable: true|false` - Visibility in menu
- `allowed-tools: [...]` - Tool restrictions
- `hooks: {PreToolUse: [...]}` - Inline hook definitions

**Session tracking** (`hook_tracker.py`):
- `once: true` support per session
- State in `~/.claude/.superclaude_hooks/`
- Auto-cleanup after 24h TTL

## Git Workflow

Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

Parallel sessions: `git worktree add ../SuperClaude-feature feature/name`

## Key Files

| File | Purpose |
|------|---------|
| PLANNING.md | Architecture, design principles, absolute rules |
| TASK.md | Current tasks and priorities |
| KNOWLEDGE.md | Accumulated insights, troubleshooting |
| CHANGELOG.md | Version history |

## Package Info

- **Version**: 4.2.1+ajitta
- **Python**: >=3.10
- **Build**: hatchling (PEP 517)
- **Deps**: pytest>=7.0.0, click>=8.0.0, rich>=13.0.0, pyyaml>=6.0.0
