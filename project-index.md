# SuperClaude Project Index

> Architecture documentation for SuperClaude v4.1.9 / v5.0

## Overview

SuperClaude is a Python package providing a pytest plugin and CLI for AI-enhanced development workflows. It implements PM Agent patterns for pre/post implementation validation, parallel execution, and cross-session learning.

| Property | Value |
|----------|-------|
| Version | 4.1.9 (stable), 5.0 (development) |
| Python | >=3.10 |
| Build | hatchling (PEP 517) |
| License | MIT |

---

## Directory Structure

```
superclaude/
├── src/superclaude/          # Active Python package (v4.1.9)
│   ├── pm_agent/             # Core PM Agent patterns
│   ├── execution/            # Parallel execution patterns
│   ├── cli/                  # CLI implementation
│   ├── mcp/configs/          # MCP server configurations
│   ├── agents/               # Agent definitions
│   ├── skills/               # Skill implementations
│   └── pytest_plugin.py      # Pytest plugin entry
│
├── plugins/superclaude/      # Plugin source (v5.0)
│   ├── commands/             # 31 slash commands
│   ├── agents/               # 21 agent definitions
│   ├── modes/                # 8 behavioral modes
│   └── mcp/configs/          # 9 MCP configs
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
│
├── docs/                     # Documentation (90+ files)
│   ├── user-guide/           # English guide
│   ├── user-guide-jp/        # Japanese
│   ├── user-guide-kr/        # Korean
│   └── user-guide-zh/        # Chinese
│
├── scripts/                  # Build and analysis tools
└── .claude/                  # Claude Code configuration
```

---

## Key Entry Points

### CLI Entry Point
```toml
# pyproject.toml
[project.scripts]
superclaude = "superclaude.cli.main:main"
```

**Commands:**
- `superclaude install` - Install slash commands to `~/.claude/commands/`
- `superclaude mcp` - Install/manage MCP servers
- `superclaude doctor` - Health check diagnostics
- `superclaude install-skill` - Install individual skills

### Pytest Plugin Entry Point
```toml
# pyproject.toml
[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"
```

**Fixtures:** `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Markers:** `@pytest.mark.confidence_check`, `@pytest.mark.self_check`, `@pytest.mark.reflexion`, `@pytest.mark.complexity("level")`

---

## Core Components

### PM Agent Patterns (`src/superclaude/pm_agent/`)

| File | LOC | Purpose |
|------|-----|---------|
| `confidence.py` | 272 | Pre-execution confidence assessment (≥90% proceed, 70-89% investigate, <70% STOP) |
| `self_check.py` | 249 | Post-implementation evidence-based validation |
| `reflexion.py` | 344 | Error learning and cross-session pattern matching |
| `token_budget.py` | 85 | Token allocation by complexity (simple: 200, medium: 1000, complex: 2500) |

**Confidence Checks (weighted):**
- No duplicate implementations (25%)
- Architecture compliance (25%)
- Official documentation verified (20%)
- Working OSS implementations referenced (15%)
- Root cause identified (15%)

### Execution Patterns (`src/superclaude/execution/`)

| File | LOC | Purpose |
|------|-----|---------|
| `parallel.py` | 337 | Wave→Checkpoint→Wave pattern (3.5x speedup) |
| `reflection.py` | 400 | Post-execution meta-reasoning |
| `self_correction.py` | 425 | Automated error detection and recovery |

### CLI (`src/superclaude/cli/`)

| File | LOC | Purpose |
|------|-----|---------|
| `main.py` | 257 | Entry point with subcommand routing |
| `install_mcp.py` | 403 | MCP server installation logic |
| `install_commands.py` | 162 | Slash command installation |
| `doctor.py` | 147 | Health diagnostics |
| `install_skill.py` | 150 | Skill installation |

---

## Dual Architecture

### v4.1.9 (Active)
- **Location:** `src/superclaude/`
- **Type:** Python package
- **Status:** Production-ready
- **Distribution:** PyPI (`pip install superclaude`)

### v5.0 (Development)
- **Location:** `plugins/superclaude/` + `src/superclaude-v5/`
- **Type:** Claude Code plugin system
- **Status:** Scaffolding phase (branch: `feat/superclaude-v5`)
- **Components:** 31 commands, 21 agents, 8 modes, 9 MCP configs

---

## Plugin Components (v5.0)

### Slash Commands (`plugins/superclaude/commands/`)

| Command | Purpose |
|---------|---------|
| `/sc` | Help and command reference |
| `/sc:research` | Deep investigation |
| `/sc:analyze` | Code analysis |
| `/sc:build` | Build/implementation |
| `/sc:explore` | Brainstorming/design |
| `/sc:plan` | Estimation/specification |
| `/sc:agent` | Agent invocation |
| `/sc:test` | Test execution |
| `/sc:git` | Git operations |
| `/sc:save` | Session save |
| `/sc:load` | Session load |
| `/sc:document` | Documentation |
| `/sc:troubleshoot` | Problem diagnosis |
| `/sc:reflect` | Self-reflection |

### Agents (`plugins/superclaude/agents/`)

| Agent | Focus |
|-------|-------|
| `pm-agent.md` | Project management patterns |
| `deep-research-agent.md` | Comprehensive investigation |
| `system-architect.md` | System design |
| `backend-architect.md` | Backend architecture |
| `frontend-architect.md` | UI/frontend |
| `python-expert.md` | Python development |
| `security-engineer.md` | Security analysis |
| `quality-engineer.md` | Testing/QA |
| `technical-writer.md` | Documentation |
| `refactoring-expert.md` | Code improvement |
| `socratic-mentor.md` | Teaching/learning |

### Modes (`plugins/superclaude/modes/`)

| Mode | Trigger | Effect |
|------|---------|--------|
| Brainstorming | `--brainstorm` | Creative exploration |
| Deep Research | `research\|investigate` | Structured investigation |
| Orchestration | `multi-tool\|parallel` | Multi-tool coordination |
| Business Panel | `business\|stakeholder` | Multi-stakeholder analysis |
| Introspection | internal | Self-analysis |
| Task Management | internal | Todo tracking |
| Token Efficiency | `--uc` | Compact output |

---

## MCP Server Integration

| Server | Purpose | Config |
|--------|---------|--------|
| **Tavily** | Web search (primary) | `tavily.json` |
| **Context7** | Documentation lookup | `context7.json` |
| **Sequential** | Multi-step reasoning | `sequential.json` |
| **Serena** | Code understanding | `serena.json` |
| **Playwright** | Browser automation | `playwright.json` |
| **Magic** | UI component generation | `magic.json` |
| **Morphllm** | Context-aware editing | `morphllm.json` |

**Installation:** `superclaude mcp --servers tavily context7`

---

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_confidence.py   # ConfidenceChecker
│   ├── test_reflexion.py    # ReflexionPattern
│   ├── test_self_check.py   # SelfCheckProtocol
│   ├── test_token_budget.py # TokenBudgetManager
│   └── test_cli_install.py  # CLI tests
└── integration/
    └── test_pytest_plugin.py # Full integration
```

**Run tests:**
```bash
uv run pytest                      # Full suite
uv run pytest tests/unit/ -v       # Unit only
uv run pytest --cov=superclaude    # With coverage
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python package config, dependencies, entry points |
| `Makefile` | Development commands |
| `VERSION` | Version string (4.1.9) |
| `CLAUDE.md` | Claude Code project instructions |
| `PLANNING.md` | Architecture and design principles |
| `KNOWLEDGE.md` | Accumulated insights |
| `TASK.md` | Current tasks and priorities |

---

## Development Workflow

### Setup
```bash
make install        # Install with UV (editable + dev deps)
make verify         # Verify installation
```

### Daily Commands
```bash
make test           # Run tests
make lint           # Check code style
make format         # Auto-format
make doctor         # Health check
```

### Plugin Development
```bash
make build-plugin     # Build to dist/
make sync-plugin-repo # Sync to ../SuperClaude_Plugin
```

### Git Workflow
```
master ← integration ← feature/*, fix/*, docs/*
```

---

## Architecture Flow

```
1. Pre-Execution (confidence_checker)
   ├── Assess readiness (≥90% → proceed)
   ├── Check: duplication, architecture, docs, OSS, root cause
   └── Decision: proceed / investigate / STOP

2. Execution (execution/parallel.py)
   ├── Wave→Checkpoint→Wave pattern
   ├── Dependency analysis
   └── 3.5x speedup vs sequential

3. Post-Execution (self_check_protocol)
   ├── Validate: tests, requirements, assumptions
   └── Evidence: test output, code changes

4. Learning (reflexion_pattern)
   ├── Record errors
   └── Cross-session pattern matching
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Install package | `uv pip install -e ".[dev]"` |
| Install commands | `superclaude install` |
| Install MCP | `superclaude mcp --servers tavily` |
| Run tests | `uv run pytest` |
| Health check | `superclaude doctor` |
| Format code | `make format` |
| Build plugin | `make build-plugin` |

---

## Statistics

| Metric | Count |
|--------|-------|
| Python source files | 20+ |
| PM Agent LOC | 969 |
| Execution LOC | 1,389 |
| CLI LOC | 1,131 |
| Slash commands | 31 |
| Agent definitions | 21 |
| Behavioral modes | 8 |
| MCP configurations | 9 |
| Test files | 10 |
| Documentation files | 90+ |

---

*Generated: 2025-12-21*
