# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

**CRITICAL**: Use **UV** for all Python operations:

```bash
uv run pytest                          # Run tests
uv run pytest tests/unit/ -v           # Run specific directory
uv run pytest tests/unit/test_confidence.py::test_name -v  # Run single test
uv run pytest -m confidence_check      # Run by marker
uv run pytest --cov=superclaude        # With coverage
uv pip install package                 # Install dependencies
```

## Essential Commands

```bash
# Development setup
make install          # Install in editable mode with dev dependencies
make verify           # Verify installation (package, plugin, health)

# Testing and quality
make test             # Full test suite
make lint             # Run ruff linter
make format           # Format code with ruff
make doctor           # Health check diagnostics

# CLI commands
superclaude install              # Install slash commands to ~/.claude/commands/
superclaude install --list       # List installed commands
superclaude mcp --list           # List available MCP servers
superclaude mcp                  # Interactive MCP installation
superclaude mcp --servers tavily context7  # Install specific MCP servers
superclaude doctor               # Health check

# Plugin packaging (for v5.0 development)
make build-plugin     # Build plugin artifacts into dist/
make sync-plugin-repo # Sync artifacts to ../SuperClaude_Plugin
```

## Architecture Overview

SuperClaude is a **Python package** (v4.1.9) providing a pytest plugin and CLI for AI-enhanced development.

```
src/superclaude/                    # Main package
├── pytest_plugin.py                # Auto-loaded via entry point
├── pm_agent/                       # PM Agent patterns
│   ├── confidence.py               # Pre-execution confidence check (≥90% proceed, 70-89% investigate, <70% STOP)
│   ├── self_check.py               # Post-implementation validation (no hallucinations)
│   ├── reflexion.py                # Error learning and cross-session pattern matching
│   └── token_budget.py             # Token allocation (simple: 200, medium: 1000, complex: 2500)
├── execution/                      # Execution patterns
│   ├── parallel.py                 # Wave → Checkpoint → Wave (3.5x speedup)
│   ├── reflection.py               # Meta-reasoning
│   └── self_correction.py          # Error recovery
└── cli/                            # CLI tools
    ├── main.py                     # superclaude command entry point
    ├── doctor.py                   # Health checks
    ├── install_commands.py         # Slash command installation
    └── install_mcp.py              # MCP server installation

plugins/superclaude/                # Plugin source (v5.0 - builds to dist/)
├── commands/                       # 30 slash commands (.md files)
├── agents/                         # 16 specialized agent definitions (.md files)
├── modes/                          # 7 behavioral modes (.md files)
├── hooks/                          # Hook configurations (hooks.json)
├── skills/                         # Skill implementations
├── mcp/                            # MCP documentation and configs
│   └── configs/                    # JSON configs for each MCP server
└── core/                           # Core rules, flags, principles

tests/
├── unit/                           # Auto-marked @pytest.mark.unit
├── integration/                    # Auto-marked @pytest.mark.integration
└── conftest.py                     # Shared fixtures
```

## Pytest Plugin

Registered via `pyproject.toml` entry point `[project.entry-points.pytest11]`, automatically available after installation.

**Fixtures**: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Custom markers**: `@pytest.mark.confidence_check`, `@pytest.mark.self_check`, `@pytest.mark.reflexion`, `@pytest.mark.complexity("level")`

```python
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    """Skips if confidence < 70%"""
    context = {"duplicate_check_complete": True, "architecture_check_complete": True, ...}
    assert confidence_checker.assess(context) >= 0.7

@pytest.mark.complexity("medium")  # simple: 200, medium: 1000, complex: 2500
def test_with_budget(token_budget):
    assert token_budget.limit == 1000
```

## PM Agent Patterns

**ConfidenceChecker** (pre-execution): Assess before starting work

| Confidence | Action |
|------------|--------|
| ≥90% | Proceed with implementation |
| 70-89% | Present alternatives, continue investigation |
| <70% | STOP - ask questions, investigate more |

Confidence checks (weighted):
- No duplicate implementations (25%)
- Architecture compliance (25%)
- Official documentation verified (20%)
- Working OSS implementations referenced (15%)
- Root cause identified (15%)

**SelfCheckProtocol** (post-implementation): Validate with evidence
- Tests passing with output (not just "tests pass")
- All requirements met (list them)
- Assumptions verified against docs
- Evidence provided (test results, code changes)

**ReflexionPattern**: Error learning for cross-session pattern matching

## Git Workflow

**Branch structure**: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

```bash
git checkout -b feature/your-feature integration
# develop with tests
git commit -m "feat: description"  # conventional commits
# merge to integration → validate → merge to master
```

## Key Documentation

| File | Purpose |
|------|---------|
| PLANNING.md | Architecture, design principles, absolute rules |
| TASK.md | Current tasks and priorities |
| KNOWLEDGE.md | Accumulated insights and troubleshooting |

## MCP Servers (Optional)

8 MCP servers available for enhanced performance (2-3x faster, 30-50% fewer tokens):

| Server | Purpose |
|--------|---------|
| Tavily | Primary web search for Deep Research |
| Context7 | Official documentation lookup |
| Sequential-Thinking | Multi-step structured reasoning |
| Serena | Code understanding and memory |
| Playwright | Cross-browser automation |
| Magic | UI component generation |
| Morphllm | Context-aware code modifications |
| Chrome DevTools | Performance analysis |

Install via: `superclaude mcp --servers tavily context7`

## Version Info

- **Framework version**: 4.1.9 (VERSION file, user-facing)
- **Python package**: 0.4.0 (pyproject.toml, library semantic version)
- **Python**: >=3.10
- **Build**: hatchling (PEP 517)
- **Entry points**: CLI (`superclaude`), pytest plugin (auto-loaded)
