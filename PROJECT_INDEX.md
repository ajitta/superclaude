# Project Index: SuperClaude Framework

**Generated**: 2026-01-27
**Version**: 4.2.1+ajitta
**Description**: AI-enhanced development framework for Claude Code - pytest plugin with specialized commands, agents, and modes

---

## Project Structure

```
SuperClaude_Framework/
├── src/superclaude/          # Python package
│   ├── cli/                  # CLI commands (main.py, doctor.py, install_*.py x6)
│   ├── pm_agent/             # PM Agent core (confidence, self_check, reflexion, token_budget)
│   ├── execution/            # Execution patterns (parallel, reflection, self_correction)
│   ├── hooks/                # Hook system (hook_tracker, inline_hooks, mcp_fallback)
│   ├── utils/                # Shared utilities (thread safety, atomic writes)
│   ├── agents/               # 20 specialized agent definitions
│   ├── commands/             # 30 slash command definitions
│   ├── modes/                # 8 behavioral mode definitions (7 + INDEX)
│   ├── mcp/                  # 10 MCP server configs + 11 docs
│   ├── core/                 # Core configs (FLAGS, PRINCIPLES, RULES, RESEARCH_CONFIG, etc.)
│   ├── skills/               # Skills (confidence-check)
│   ├── scripts/              # Utility scripts
│   └── pytest_plugin.py      # Auto-loaded pytest integration
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests (9 files)
│   └── integration/          # Integration tests (1 file)
├── scripts/                  # Build and analysis tools
├── docs/                     # Extended documentation
└── .github/                  # CI/CD workflows (4 workflows)
```

---

## Framework Statistics

| Category | Count | Location |
|----------|-------|----------|
| Slash Commands | 30 | src/superclaude/commands/ |
| Agents | 20 | src/superclaude/agents/ |
| Modes | 7 (+INDEX) | src/superclaude/modes/ |
| MCP Servers | 10 | src/superclaude/mcp/configs/ |
| Core Configs | 7 | src/superclaude/core/ |
| Python Files | 44 | src/superclaude/ |
| Test Files | 14 | tests/ |
| Skills | 1 | src/superclaude/skills/ |

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

### Skills (1)
- **Confidence Check**: `src/superclaude/skills/confidence-check/`
  - Purpose: Pre-implementation confidence assessment (>=90% to proceed)

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
- >=90%: Proceed with implementation
- 70-89%: Present alternatives to user
- <70%: Ask clarifying questions

**Token Budget Levels**:
- Simple: 200 tokens
- Medium: 1,000 tokens
- Complex: 2,500 tokens

### Execution Patterns (src/superclaude/execution/)

| Module | Classes | Purpose |
|--------|---------|---------|
| parallel.py | TaskStatus, Task, ParallelGroup, ExecutionPlan, ParallelExecutor | Wave->Checkpoint->Wave (3.5x faster) |
| reflection.py | - | Post-execution analysis |
| self_correction.py | - | Automated error correction |

### CLI (src/superclaude/cli/)

| Module | Purpose |
|--------|---------|
| main.py | CLI entry point (click-based) |
| doctor.py | Health check diagnostics |
| install_skill.py | Individual skill installation |
| install_mcp.py | MCP server config installation |
| install_paths.py | Installation path resolution |
| install_settings.py | Settings management |
| install_commands.py | Command file installation |
| install_components.py | Component installation orchestration |
| install_inventory.py | Component inventory and listing |

### Hooks (src/superclaude/hooks/)

| Module | Purpose |
|--------|---------|
| hook_tracker.py | Session tracking (once:true, 24h TTL) |
| inline_hooks.py | Frontmatter hook parser |
| mcp_fallback.py | MCP unavailability fallback handling |

### Utils (src/superclaude/utils/)

| Module | Purpose |
|--------|---------|
| __init__.py | Shared utilities (thread safety, atomic writes) |

---

## Slash Commands (30)

Commands installed to `~/.claude/commands/sc/`:

| Category | Commands |
|----------|----------|
| Core | sc, help, recommend |
| Analysis | analyze, explain, troubleshoot |
| Implementation | implement, improve, cleanup |
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

## Modes (7 + INDEX)

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

---

## MCP Servers (10)

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
| chrome-devtools | Performance debug | --perf |

---

## Core Configs (7)

Located in `src/superclaude/core/`:

| File | Purpose |
|------|---------|
| FLAGS.md | Behavioral flags, MCP triggers, effort levels |
| PRINCIPLES.md | Engineering philosophy, SOLID, decisions |
| RULES.md | Behavioral rules, priorities, conflict resolution |
| RESEARCH_CONFIG.md | Deep research settings, hop config, credibility |
| ABBREVIATIONS.md | MCP and persona abbreviation mappings |
| BUSINESS_PANEL_EXAMPLES.md | Business panel usage examples |
| BUSINESS_SYMBOLS.md | Business domain symbols |

---

## Test Suite

### Structure
```
tests/
├── conftest.py                # Shared fixtures
├── unit/
│   ├── test_cli_install.py    # CLI installation tests
│   ├── test_confidence.py     # ConfidenceChecker tests
│   ├── test_hook_tracker.py   # Hook tracker tests
│   ├── test_hooks.py          # Hook system tests
│   ├── test_mcp_fallback.py   # MCP fallback tests
│   ├── test_parallel.py       # Parallel execution tests
│   ├── test_reflexion.py      # ReflexionPattern tests
│   ├── test_self_check.py     # SelfCheckProtocol tests
│   └── test_token_budget.py   # TokenBudgetManager tests
└── integration/
    └── test_pytest_plugin.py  # Plugin integration tests
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
- **Python**: >=3.10
- **Dependencies**: pytest>=7.0.0, click>=8.0.0, rich>=13.0.0, pyyaml>=6.0.0

### Entry Points
```toml
[project.scripts]
superclaude = "superclaude.cli.main:main"

[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"
```

---

## CI/CD (.github/workflows/)

| Workflow | Purpose |
|----------|---------|
| test.yml | Test suite execution |
| quick-check.yml | Fast validation checks |
| publish-pypi.yml | PyPI publishing |
| readme-quality-check.yml | README quality gate |

---

## Installation

```bash
# Option 1: Development (recommended)
uv pip install -e ".[dev]"
uv run superclaude install

# Option 2: Global tool
make deploy

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
| CONTRIBUTING.md | Contribution guidelines |
| SECURITY.md | Security policy |
| docs/developer-guide/ | Technical docs (architecture, testing, contributing) |
| docs/reference/ | User reference (commands, examples, troubleshooting) |
| docs/research/ | Research findings and analysis |

---

## Token Efficiency

### Index Performance
- **Before**: ~58,000 tokens (reading all files)
- **After**: ~3,000 tokens (reading this index)
- **Reduction**: 94%

### PM Agent ROI
- **Confidence check**: 100-200 tokens -> saves 5,000-50,000 tokens
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
| MCP fallback | hooks/mcp_fallback.py |
| Shared utils | utils/__init__.py |
| Slash commands | commands/*.md |
| Agent definitions | agents/*.md |
| Mode behaviors | modes/*.md |
| MCP configs | mcp/configs/*.json |
| Core rules | core/RULES.md |
| Flag reference | core/FLAGS.md |

### By File Extension

| Extension | Count | Purpose |
|-----------|-------|---------|
| .py | 44 | Python source |
| .md | 84+ | Documentation, commands, agents |
| .json | 15+ | Config files |

---

## Git Workflow

- **Branch**: master <- integration <- feature/*, fix/*, docs/*
- **Commits**: Conventional (feat:, fix:, docs:, refactor:, test:, chore:)
- **Current**: master (clean)

---

**For detailed docs**: See `docs/` or [GitHub](https://github.com/SuperClaude-Org/SuperClaude_Framework)
