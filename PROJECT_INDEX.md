# Project Index: SuperClaude Framework

**Generated**: 2026-01-03
**Version**: 4.1.9+ajitta
**Description**: AI-enhanced development framework for Claude Code - pytest plugin with specialized commands, agents, and modes

---

## Project Structure

```
SuperClaude_Framework/
├── src/superclaude/          # Python package
│   ├── cli/                  # CLI commands (main.py, doctor.py, install_*.py)
│   ├── pm_agent/             # PM Agent core (confidence, self_check, reflexion, token_budget)
│   ├── execution/            # Execution patterns (parallel, reflection, self_correction)
│   ├── agents/               # 20 specialized agent definitions
│   ├── commands/             # 30 slash command definitions
│   ├── modes/                # 8 behavioral mode definitions
│   ├── mcp/                  # 11 MCP server configs and docs
│   ├── core/                 # Core configs (FLAGS, PRINCIPLES, RULES, RESEARCH_CONFIG)
│   ├── hooks/                # Git/session hooks
│   ├── skills/               # TypeScript skills (confidence-check)
│   ├── scripts/              # Utility scripts
│   └── pytest_plugin.py      # Auto-loaded pytest integration
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests (5 files)
│   └── integration/          # Integration tests (1 file)
├── .claude/                  # Claude Code runtime configuration
│   ├── agents/               # Installed agents (20 files)
│   ├── commands/sc/          # Installed slash commands (30 files)
│   ├── skills/               # Installed skills
│   ├── superclaude/          # Core configs (FLAGS, PRINCIPLES, RULES, etc.)
│   └── settings.json         # Claude Code settings
├── docs/                     # Extended documentation
├── plugins/                  # Plugin staging (for v5.0)
└── scripts/                  # Build and analysis tools
```

---

## Framework Statistics

| Category | Count | Location |
|----------|-------|----------|
| Slash Commands | 30 | src/superclaude/commands/ |
| Agents | 20 | src/superclaude/agents/ |
| Modes | 8 | src/superclaude/modes/ |
| MCP Servers | 11 | src/superclaude/mcp/ |
| Core Configs | 6 | src/superclaude/core/ |

---

## Entry Points

### CLI
- **Command**: `superclaude`
- **Source**: `src/superclaude/cli/main.py:main`
- **Subcommands**: install, mcp, update, install-skill, doctor, version

### Pytest Plugin
- **Auto-loaded**: Yes (via `pyproject.toml` entry point)
- **Source**: `src/superclaude/pytest_plugin.py`
- **Fixtures**: confidence_checker, self_check_protocol, reflexion_pattern, token_budget, pm_context

### Skills
- **Confidence Check**: `.claude/skills/confidence-check/`
- **Purpose**: Pre-implementation confidence assessment

---

## Core Modules

### PM Agent (src/superclaude/pm_agent/)

| Module | Class | Purpose | Key Methods |
|--------|-------|---------|-------------|
| confidence.py | ConfidenceChecker | Pre-execution assessment | assess(), get_recommendation() |
| self_check.py | SelfCheckProtocol | Post-implementation validation | validate(), format_report() |
| reflexion.py | ReflexionPattern | Error learning | get_solution(), record_error() |
| token_budget.py | TokenBudgetManager | Token allocation | allocate(), use(), remaining() |

**Confidence Thresholds**:
- ≥90%: Proceed with implementation
- 70-89%: Present alternatives to user
- <70%: Ask clarifying questions

**Token Budget Levels**:
- Simple: 200 tokens
- Medium: 1,000 tokens
- Complex: 2,500 tokens

### Execution Patterns (src/superclaude/execution/)

| Module | Classes | Purpose |
|--------|---------|---------|
| parallel.py | TaskStatus, Task, ParallelGroup, ExecutionPlan, ParallelExecutor | Wave→Checkpoint→Wave (3.5x faster) |
| reflection.py | - | Post-execution analysis |
| self_correction.py | - | Automated error correction |

---

## Slash Commands (30)

Commands installed to `~/.claude/commands/sc/`:

| Category | Commands |
|----------|----------|
| Core | sc, help, recommend |
| Analysis | analyze, explain, troubleshoot |
| Implementation | implement, improve, cleanup, refactoring |
| Planning | brainstorm, design, estimate, workflow, spawn |
| Documentation | document, index, index-repo |
| Quality | test, build, reflect |
| Research | research, spec-panel, business-panel |
| Session | load, save, agent, task |
| Git | git |
| Tools | select-tool, pm |

---

## Agents (20)

Specialized agents installed to `~/.claude/agents/`:

| Category | Agents |
|----------|--------|
| Architecture | backend-architect, devops-architect, frontend-architect, system-architect |
| Quality | quality-engineer, security-engineer, performance-engineer |
| Development | python-expert, refactoring-expert, requirements-analyst |
| Analysis | root-cause-analyst, deep-research-agent, deep-research |
| Education | learning-guide, socratic-mentor, technical-writer |
| Workflow | pm-agent, repo-index, self-review, business-panel-experts |

---

## Modes (8)

Behavioral modes in `src/superclaude/modes/`:

| Mode | Trigger | Purpose |
|------|---------|---------|
| Brainstorming | --brainstorm | Collaborative discovery, probing questions |
| DeepResearch | --research | Systematic evidence-based investigation |
| Orchestration | --orchestrate | Multi-tool optimization, parallel ops |
| TaskManagement | --task-manage | Hierarchical org, delegation |
| TokenEfficiency | --uc | Symbol communication, 30-50% reduction |
| Introspection | --introspect | Meta-cognition, pattern detection |
| BusinessPanel | business, panel | Multi-expert analysis |
| Unified | (default) | Combined reference |

---

## MCP Servers (11)

Configurations in `src/superclaude/mcp/configs/`:

| Server | Purpose | Flag |
|--------|---------|------|
| context7 | Official docs lookup | --c7 |
| tavily | Web search | --tavily |
| sequential | Extended thinking | --seq |
| serena | Symbol ops, memory | --serena |
| morphllm | Bulk pattern edits | --morph |
| magic | UI components (21st.dev) | --magic |
| playwright | Browser automation | --play |
| airis-agent | Confidence, indexing | - |
| mindbase | Semantic memory | - |

---

## Core Configs (6)

Located in `src/superclaude/core/`:

| File | Purpose |
|------|---------|
| FLAGS.md | Behavioral flags, MCP triggers, effort levels |
| PRINCIPLES.md | Engineering philosophy, SOLID, decisions |
| RULES.md | Behavioral rules, priorities, conflict resolution |
| RESEARCH_CONFIG.md | Deep research settings, hop config, credibility |
| BUSINESS_PANEL_EXAMPLES.md | Business panel usage examples |
| BUSINESS_SYMBOLS.md | Business domain symbols |

---

## Test Suite

### Structure
```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_cli_install.py  # CLI installation tests
│   ├── test_confidence.py   # ConfidenceChecker tests
│   ├── test_reflexion.py    # ReflexionPattern tests
│   ├── test_self_check.py   # SelfCheckProtocol tests
│   └── test_token_budget.py # TokenBudgetManager tests
└── integration/
    └── test_pytest_plugin.py # Plugin integration tests
```

### Markers
- `unit`: Unit tests (auto-applied in `/unit/`)
- `integration`: Integration tests (auto-applied in `/integration/`)
- `confidence_check`: Pre-execution tests
- `self_check`: Post-implementation tests
- `reflexion`: Error learning tests
- `complexity`: Task complexity (simple, medium, complex)

### Commands
```bash
uv run pytest                         # All tests
uv run pytest tests/unit/ -v          # Unit tests only
uv run pytest -m confidence_check     # By marker
uv run pytest --cov=superclaude       # With coverage
```

---

## Configuration

### Python Package (pyproject.toml)
- **Build**: hatchling (PEP 517)
- **Python**: ≥3.10
- **Dependencies**: pytest≥7.0.0, click≥8.0.0, rich≥13.0.0

### Entry Points
```toml
[project.scripts]
superclaude = "superclaude.cli.main:main"

[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"
```

---

## Installation

```bash
# Option 1: pipx (recommended)
pipx install superclaude
superclaude install

# Option 2: Development
uv pip install -e ".[dev]"
uv run superclaude install

# Verify
superclaude doctor
superclaude install --list
```

---

## Key Documentation Files

| File | Purpose |
|------|---------|
| CLAUDE.md | Claude Code integration instructions |
| README.md | Project overview, quick start |
| PLANNING.md | Architecture, design principles |
| TASK.md | Current tasks, priorities |
| KNOWLEDGE.md | Accumulated insights |
| CONTRIBUTING.md | Contribution guidelines |
| CHANGELOG.md | Version history |

---

## Token Efficiency

### Index Performance
- **Before**: ~58,000 tokens (reading all files)
- **After**: ~3,000 tokens (reading this index)
- **Reduction**: 94%

### PM Agent ROI
- **Confidence check**: 100-200 tokens → saves 5,000-50,000 tokens
- **ROI**: 25-250x token savings

---

## Cross-Reference Index

### By Functionality

| Need | File(s) |
|------|---------|
| CLI entry | cli/main.py |
| Pytest fixtures | pytest_plugin.py |
| Confidence assessment | pm_agent/confidence.py, skills/confidence-check/ |
| Post-validation | pm_agent/self_check.py |
| Error learning | pm_agent/reflexion.py |
| Token management | pm_agent/token_budget.py |
| Parallel execution | execution/parallel.py |
| Slash commands | commands/*.md |
| Agent definitions | agents/*.md |
| Mode behaviors | modes/*.md |
| MCP configs | mcp/configs/*.json |
| Core rules | core/RULES.md |
| Flag reference | core/FLAGS.md |

### By File Extension

| Extension | Count | Purpose |
|-----------|-------|---------|
| .py | 30+ | Python source |
| .md | 80+ | Documentation, commands, agents |
| .json | 15+ | Config files |
| .ts | 1 | TypeScript skill |
| .sh | 3 | Shell scripts |

---

## Git Workflow

- **Branch**: master ← integration ← feature/*, fix/*, docs/*
- **Commits**: Conventional (feat:, fix:, docs:, refactor:, test:, chore:)
- **Current**: master (clean)

---

**For detailed docs**: See `docs/` or [GitHub](https://github.com/SuperClaude-Org/SuperClaude_Framework)
