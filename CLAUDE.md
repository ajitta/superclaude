# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

This project uses **UV** for all Python operations to ensure consistent dependency management.

```bash
uv run pytest                    # Run tests
uv run pytest tests/pm_agent/ -v # Run specific directory
uv run pytest tests/test_file.py -v  # Run specific file
uv run pytest -m confidence_check    # Run by marker
uv pip install package           # Install dependencies
uv run python script.py          # Execute scripts
```

## Essential Commands

```bash
# Development
make install          # Install in editable mode (RECOMMENDED: uv pip install -e ".[dev]")
make verify           # Verify installation
make test             # Run full test suite
make lint             # Run ruff linter
make format           # Format code with ruff
make doctor           # Health check diagnostics
make clean            # Remove build artifacts

# Plugin Packaging (v5.0 prep)
make build-plugin     # Build plugin artefacts into dist/
make sync-plugin-repo # Sync artefacts into ../SuperClaude_Plugin
```

## Architecture

SuperClaude v4.2.1+ajitta is a Python package with pytest plugin, slash commands, and Claude Code v2.1.0 compatibility.

```
src/superclaude/
├── pytest_plugin.py     # Auto-loaded pytest integration (entry point)
├── pm_agent/            # Pre/post implementation patterns
│   ├── confidence.py    # Pre-execution confidence check (≥90% to proceed)
│   ├── self_check.py    # Post-implementation validation
│   ├── reflexion.py     # Error learning and cross-session patterns
│   └── token_budget.py  # Token allocation (simple: 200, medium: 1000, complex: 2500)
├── execution/
│   ├── parallel.py      # Wave→Checkpoint→Wave pattern (3.5x faster)
│   ├── reflection.py    # Meta-reasoning
│   └── self_correction.py
├── cli/
│   ├── main.py          # superclaude command entry point
│   ├── doctor.py        # Health checks
│   ├── install_skill.py # Skill installation
│   ├── install_commands.py
│   └── install_mcp.py   # MCP server installation
├── agents/              # Agent definitions (20 specialized agents)
├── commands/            # Slash command definitions (30 commands)
├── modes/               # Behavioral modes (8 modes)
└── mcp/                 # MCP server configurations
```

## Pytest Plugin

Registered via `pyproject.toml` entry point, auto-loaded after installation.

**Fixtures**: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Auto-markers**:
- Tests in `/unit/` → `@pytest.mark.unit`
- Tests in `/integration/` → `@pytest.mark.integration`

**Custom markers**: `confidence_check`, `self_check`, `reflexion`, `complexity`

```python
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    context = {"test_name": "test_feature", "has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.7

@pytest.mark.complexity("medium")  # simple: 200, medium: 1000, complex: 2500
def test_with_budget(token_budget):
    assert token_budget.limit == 1000
```

## PM Agent Patterns

**ConfidenceChecker**: Pre-execution assessment
- ≥90%: proceed
- 70-89%: present alternatives
- <70%: ask questions (ROI: 25-250x token savings)

**SelfCheckProtocol**: Post-implementation validation with evidence (no speculation)

**ReflexionPattern**: Error learning and cross-session pattern matching

**Parallel Execution**: Wave→Checkpoint→Wave (3.5x speedup)
```
[Read file1, file2, file3] → Analyze → [Edit file1, file2, file3]
```

## Git Workflow

**Branch structure**: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

**Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)

**Parallel Sessions**: Use git worktrees to avoid conflicts:
```bash
git worktree add ../SuperClaude_Framework-feature feature/pm-agent
```

## Installation

```bash
# Option 1: pipx (recommended for users)
pipx install superclaude
superclaude install

# Option 2: Development from repo
./install.sh
# or manually:
uv pip install -e ".[dev]"
uv run superclaude install
```

## Development Workflow

**For developers working on this codebase:**

```bash
# 1. Initial setup (once)
make install   # or: uv pip install -e ".[dev]"

# 2. Development cycle
# Edit code...
uv run superclaude install --list-all  # Test changes immediately (editable mode)
uv run pytest tests/ -v                 # Run tests

# 3. Deploy to global tool (use from any directory)
uv tool install --force .

# 4. Use from anywhere
cd /any/project
superclaude install
superclaude mcp --servers tavily
```

| Stage | Command | Location |
|-------|---------|----------|
| Dev/Test | `uv run superclaude ...` | This repo |
| Deploy | `uv tool install --force .` | This repo |
| Use | `superclaude ...` | Anywhere |

**Note**: Editable mode (`-e`) means code changes are reflected immediately in `uv run` without reinstalling. Global tool requires `uv tool install --force .` to update.

## Entry Points

Key entry points defined in `pyproject.toml`:

```toml
[project.scripts]
superclaude = "superclaude.cli.main:main"  # CLI command

[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"   # pytest auto-load
```

Verify installation: `uv tool list` or `which superclaude`

## Project-Specific Installation

To install SuperClaude to a specific project directory:

```bash
# Clone the repository
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# Install to current directory (./.claude/)
./install.sh --scope project

# Or non-interactive with force
./install.sh --scope project --yes --force
```

**CLI scope options (all commands use consistent --scope):**
| Command | Scopes | Default |
|---------|--------|---------|
| `superclaude install` | `user`, `project` | `user` |
| `superclaude uninstall` | `user`, `project` | `user` |
| `superclaude update` | `user`, `project` | `user` |
| `superclaude install-skill` | `user`, `project` | `user` |
| `superclaude mcp` | `local`, `project`, `user` | `user` |

| Scope | Path | Description |
|-------|------|-------------|
| `user` | `~/.claude/` | Global installation (default) |
| `project` | `./.claude/` | Current project only |
| `local` | `.mcp.json` | MCP servers only (Claude Code standard) |

## CLI Commands

The `superclaude` CLI provides management commands:

```bash
# Installation
superclaude install              # Install all components to ~/.claude/
superclaude install --scope project  # Install to ./.claude/
superclaude install --list-all   # Show installation status
superclaude uninstall            # Remove SuperClaude components
superclaude update               # Update to current version (--force install)

# Component Management (v2.1.0)
superclaude agents --list        # List all agents
superclaude agents --info <name> # Agent details
superclaude agents --tokens      # Token estimates for agents
superclaude skills --list        # List all skills
superclaude skills --info <name> # Skill details (v2.1.0 fields)
superclaude skills --tokens      # Token estimates for context budget

# MCP Servers
superclaude mcp --list           # List available MCP servers
superclaude mcp --servers tavily context7  # Install specific servers
superclaude mcp --scope local    # Install to .mcp.json

# Utilities
superclaude doctor               # Health check diagnostics
superclaude install-skill <name> # Install specific skill
```

## MCP Server Integration

Optional servers (7 available) for enhanced performance:
- **Tavily**: Web search (Deep Research)
- **Context7**: Official documentation lookup
- **Sequential-Thinking**: Token-efficient reasoning (30-50% reduction)
- **Serena**: Session persistence

```bash
superclaude mcp --list           # List available servers
superclaude mcp --servers tavily context7  # Install specific servers
```

## Key Documentation Files

| File | Purpose |
|------|---------|
| CHANGELOG.md | Version history and feature changes |
| PLANNING.md | Architecture, design principles, absolute rules |
| TASK.md | Current tasks and priorities |
| KNOWLEDGE.md | Accumulated insights and troubleshooting |

## Claude Code v2.1.0 Compatibility

SuperClaude supports Claude Code v2.1.0 skill/hook features:

**Frontmatter Schema Fields:**
- `context: inline|fork` - Execution context (inline default, fork for sub-agent)
- `agent: <agent-name>` - Optional agent type for skill execution
- `user-invocable: true|false` - Control visibility in slash command menu
- `allowed-tools: [...]` - Restrict tools available during skill execution
- `hooks: {PreToolUse: [...]}` - Inline hook definitions in frontmatter

**Hook Session Tracker:**
- `once: true` support for single-execution hooks per session
- State persistence in `~/.claude/.superclaude_hooks/`
- Auto-cleanup of old sessions (>24h TTL)

## Development Principles

1. **Evidence-Based**: Never guess - verify with official docs (Context7 MCP, WebFetch)
2. **Confidence-First**: Check confidence BEFORE starting (≥90% to proceed)
3. **Parallel-First**: Use Wave→Checkpoint→Wave pattern
4. **Token Efficiency**: Allocate based on complexity; confidence check ROI is 25-250x

## Package Info

- **Package**: `superclaude` v4.2.1+ajitta
- **Python**: >=3.10
- **Build**: hatchling (PEP 517)
- **Entry points**: CLI (`superclaude`), Pytest plugin (auto-loaded as `superclaude`)
- **Dependencies**: pytest>=7.0.0, click>=8.0.0, rich>=13.0.0, pyyaml>=6.0.0
