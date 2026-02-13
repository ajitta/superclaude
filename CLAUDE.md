# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

This project uses **UV** for all Python operations. Never use `pip` or `python -m pytest` directly.

```bash
# Tests
uv run pytest                              # Full suite
uv run pytest tests/unit/ -v               # Unit tests only
uv run pytest tests/integration/ -v        # Integration tests
uv run pytest tests/unit/test_confidence.py -v  # Single file
uv run pytest -m confidence_check          # By marker
uv run pytest -k "test_assess"             # By name pattern

# Development workflow
uv pip install -e ".[dev]"                 # Install editable (RECOMMENDED)
uv run superclaude install --list-all      # Test CLI changes
make deploy                                # Deploy to global tool (recommended)
```

## Make Commands

```bash
make install       # uv pip install -e ".[dev]"
make deploy        # Deploy to global uv tool (editable, changes reflect immediately)
make test          # uv run pytest
make test-plugin   # Verify pytest plugin loads
make verify        # Full installation check
make lint          # ruff check
make format        # ruff format
make doctor        # Health check
make clean         # Remove artifacts
make build-plugin  # Build plugin artefacts to dist/
```

## Architecture

SuperClaude is a **dual-purpose** project:

1. **Python package** — A pytest plugin + CLI tool (`superclaude`) providing PM Agent patterns (confidence checking, self-check, reflexion, parallel execution)
2. **Content framework** — Markdown files (commands, agents, modes, MCP docs, core config) that get installed into `~/.claude/` to configure Claude Code's behavior via CLAUDE.md injection

### Content Installation Flow

The CLI `superclaude install` copies content from the package to Claude Code's config directory:

```
src/superclaude/commands/  →  ~/.claude/commands/sc/       (31 slash commands)
src/superclaude/agents/    →  ~/.claude/agents/             (21 agent definitions)
src/superclaude/skills/    →  ~/.claude/skills/             (skill implementations)
src/superclaude/core/      →  ~/.claude/superclaude/core/   (FLAGS, PRINCIPLES, RULES)
src/superclaude/modes/     →  ~/.claude/superclaude/modes/  (8 behavioral modes)
src/superclaude/mcp/       →  ~/.claude/superclaude/mcp/    (MCP server documentation)
```

This mapping is defined in `src/superclaude/cli/install_paths.py` (the `COMPONENTS` dict). The install logic is split across submodules under `cli/`:
- `install_paths.py` — Path resolution (leaf dependency, no internal imports)
- `install_settings.py` — Settings, hooks, CLAUDE.md management (leaf dependency)
- `install_components.py` — Component installation orchestration (imports from paths + settings)
- `install_inventory.py` — Listing and uninstallation
- `install_commands.py` — Top-level command wiring (imports from all above)
- `install_skill.py` — Individual skill installation with `{{SKILLS_PATH}}` template resolution
- `install_mcp.py` — MCP server configuration into settings.json

### Key Architectural Decisions

- **Editable install via `make deploy`**: Uses `uv tool install --editable .` so changes in `src/` reflect immediately without reinstalling.
- **CLAUDE_SC.md import**: Installation adds `@superclaude/CLAUDE_SC.md` to the user's `~/.claude/CLAUDE.md`, which chains to `core/FLAGS.md`, `core/PRINCIPLES.md`, and `core/RULES.md`.
- **Hooks merge (not replace)**: `install_settings.py` merges SuperClaude hooks into existing `settings.json` using marker-based identification (`SUPERCLAUDE_HOOK_MARKERS`), preserving user hooks.
- **Template variables**: Skill manifests (`SKILL.md`) support `{{SCRIPTS_PATH}}` and `{{SKILLS_PATH}}` placeholders resolved at install time based on scope.

### Package Structure

```
src/superclaude/
├── __init__.py          # Exports ConfidenceChecker, SelfCheckProtocol, ReflexionPattern
├── pytest_plugin.py     # Entry point (auto-loaded via pyproject.toml entry-points.pytest11)
├── pm_agent/            # Core Python patterns
│   ├── confidence.py    # Pre-execution check (Protocol-based, extensible checks)
│   ├── self_check.py    # Post-implementation validation
│   ├── reflexion.py     # Cross-session error learning (JSONL storage)
│   ├── token_budget.py  # simple: 200, medium: 1000, complex: 2500
│   └── task_cleanup.py  # Stale task removal (24h threshold)
├── execution/
│   ├── parallel.py      # Wave→Checkpoint→Wave pattern
│   ├── reflection.py    # Meta-reasoning
│   └── self_correction.py
├── cli/                 # Click-based CLI (superclaude command)
│   └── main.py          # @click.group: install, uninstall, update, mcp, doctor, agents, skills, install-skill, version
├── hooks/
│   ├── hooks.json       # Hook definitions template (SessionStart, UserPromptSubmit, PostToolUse)
│   ├── hook_tracker.py  # once: true session tracking (24h TTL, state in ~/.claude/.superclaude_hooks/)
│   ├── inline_hooks.py  # YAML frontmatter parser for skills/agents/commands
│   └── mcp_fallback.py  # MCP server availability fallback handling
├── utils/               # Shared utilities (atomic_write_json)
├── commands/            # 31 slash command markdown files
├── agents/              # 21 agent definition markdown files
├── skills/              # Skill directories with SKILL.md manifests
├── modes/               # 8 behavioral mode markdown files
├── mcp/                 # MCP server docs + configs/
├── core/                # FLAGS.md, PRINCIPLES.md, RULES.md
└── scripts/             # Shell/Python utilities (context_reset.py, session_init.py, etc.)
```

## Pytest Plugin

Auto-loaded after `uv pip install -e .`. The plugin (`pytest_plugin.py`) provides:

**Fixtures** (from `pytest_plugin.py` and `tests/conftest.py`):
- `confidence_checker` → `ConfidenceChecker()` — pre-execution assessment
- `self_check_protocol` → `SelfCheckProtocol()` — post-implementation validation
- `reflexion_pattern` → `ReflexionPattern()` — error learning
- `token_budget` → `TokenBudgetManager(complexity)` — reads `@pytest.mark.complexity` marker
- `pm_context` → creates temp memory directory structure

**Hooks** (in `pytest_plugin.py`):
- `pytest_runtest_setup` — skips tests marked `@pytest.mark.confidence_check` if confidence < 70%
- `pytest_runtest_makereport` — records failures for `@pytest.mark.reflexion` tests
- `pytest_collection_modifyitems` — auto-adds `unit`/`integration` markers by path

**Custom markers** (pyproject.toml):
- `confidence_check`, `self_check`, `reflexion`, `complexity(level)`, `hallucination`, `performance`

## PM Agent Patterns

| Pattern | Class | Purpose | Threshold |
|---------|-------|---------|-----------|
| ConfidenceChecker | `pm_agent/confidence.py` | Pre-execution gate | ≥90% proceed, 70-89% alternatives, <70% stop |
| SelfCheckProtocol | `pm_agent/self_check.py` | Post-validation | Evidence required, no speculation |
| ReflexionPattern | `pm_agent/reflexion.py` | Error learning | Cross-session pattern matching (JSONL) |
| TokenBudgetManager | `pm_agent/token_budget.py` | Token allocation | simple/medium/complex |
| TaskCleanupManager | `pm_agent/task_cleanup.py` | Stale task removal | 24h threshold |

`confidence.py` uses a Protocol-based design (`ConfidenceCheck` protocol) with pluggable checks. Default checks (weights summing to 1.0):
- `NoDuplicatesCheck` (0.25) — searches for duplicate implementations
- `ArchitectureCheck` (0.25) — verifies tech stack compliance via CLAUDE.md/pyproject.toml/package.json
- `OfficialDocsCheck` (0.20) — confirms documentation exists
- `OssReferenceCheck` (0.15) — matches against known OSS patterns database
- `RootCauseCheck` (0.15) — validates root cause specificity

`PRStatusCheck` exists but is not in `DEFAULT_CHECKS` — must be registered manually. `ConfidenceResult` supports numeric comparison operators (`result >= 0.9`) via `__float__`.

## Hooks System

Located in `src/superclaude/hooks/`. Claude Code v2.1.0+ compatible.

**Frontmatter fields** (parsed by `inline_hooks.py` using `pyyaml`):
- `context: inline|fork` — execution context
- `agent: <name>` — agent type for skill
- `user-invocable: true|false` — visibility in menu
- `allowed-tools: [...]` — tool restrictions
- `hooks: {PreToolUse: [...]}` — inline hook definitions

**Session tracking** (`hook_tracker.py`):
- `once: true` support per session (prevents duplicate execution)
- State persisted in `~/.claude/.superclaude_hooks/`
- Auto-cleanup after 24h TTL

## Git Workflow

Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

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
- **Linting**: ruff (line-length 88, ignores E501)
- **Type checking**: mypy (gradual typing, `disallow_untyped_defs = false`)
