# Repository Guidelines for AI Agents

SuperClaude is a Python-based pytest plugin and framework for Claude Code. It ships
PM Agent capabilities (confidence checks, reflexion, self-check, token budgeting)
plus configuration assets (agents, commands, modes, MCP configs).

## Serena Usage
- Use Serena tools for codebase navigation and edits whenever possible.
- Prefer symbol-level reads/edits over full-file reads; only read whole files when necessary.
- Use Serena search tools (`find_symbol`, `search_for_pattern`, `find_referencing_symbols`) before manual file scans.

## Project Structure
```
docs/                      # Documentation
plugins/                   # Plugin assets
scripts/                   # Repo utility scripts
skills/                    # Repo skill definitions
src/superclaude/           # Core package
  cli/                     # CLI commands (Click-based)
  pm_agent/                # Confidence, reflexion, self_check, token_budget
  execution/               # Parallel execution + self-correction
  agents/                  # Agent definition markdown files
  commands/                # Slash command markdown files
  modes/                   # Mode configuration files
  hooks/                   # Hook definitions + frontmatter parsing
  scripts/                 # Utility scripts
  mcp/                     # MCP server configurations
  skills/                  # Skill definitions
  pytest_plugin.py         # pytest plugin entry point
tests/
  unit/                    # Unit tests
  integration/             # Integration tests
  conftest.py              # Shared fixtures
```

## Build, Lint, and Test Commands
```bash
# Install and deploy (uv only, no pip)
make install               # uv pip install -e ".[dev]"
make deploy                # uv tool install --force --editable .

# Full test suite
make test                  # uv run pytest

# Subsets
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest -m unit
uv run pytest -m integration

# Single test file / single test
uv run pytest tests/unit/test_confidence.py -v
uv run pytest tests/unit/test_confidence.py::TestConfidenceChecker::test_high_confidence_scenario
uv run pytest -k "test_assess"

# Coverage
uv run pytest --cov=src/superclaude tests/

# Linting / formatting / typing
make lint                  # uv run ruff check .
uv run ruff check --fix .
make format                # uv run ruff format .
uv run mypy src/

# Build and packaging
make build-plugin          # build plugin artefacts into dist/
make sync-plugin-repo      # sync plugin artefacts to ../SuperClaude_Plugin

# Health and verification
make doctor                # uv run superclaude doctor
make verify                # end-to-end install check
make test-plugin           # verify pytest plugin auto-load

# Maintenance
make clean                 # remove build/test caches
make translate             # update README-zh.md and README-ja.md
make uninstall-legacy      # remove legacy ~/.claude files
```

## Testing Conventions
- Pytest config lives in `pyproject.toml` with `-v`, `--strict-markers`, `--tb=short`.
- Test discovery: `tests/`, `test_*.py`, `Test*`, `test_*`.
- Marker set (keep consistent with `pyproject.toml`):
  - `unit`, `integration`, `hallucination`, `performance`
  - `confidence_check`, `self_check`, `reflexion`
  - `complexity(level)` where level is `simple|medium|complex`

## Code Style Guidelines

### Python Version and Formatting
- Python 3.10+ only.
- Line length 88 chars; 4-space indentation.
- Formatter: Ruff (`uv run ruff format .`).
- Linter: Ruff with `E/F/I/N/W` selections, `E501` ignored (handled by formatter).

### Import Organization
Ruff sorts imports: stdlib, third-party, local.
```python
from pathlib import Path

import click

from superclaude import __version__
```

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `pytest_plugin.py` |
| Classes | CapWords | `ConfidenceChecker` |
| Functions | snake_case | `assess_confidence` |
| Constants | UPPER_SNAKE | `DEFAULT_CHECKS` |
| Context files | kebab-case | `deep-research.md` |

### Types and Protocols
- Add type hints to public functions and dataclasses.
- Use `typing` generics (`Dict`, `List`, `Tuple`, `Any`) and `Protocol` where needed.
- `check_untyped_defs = true`, `no_implicit_optional = true`, gradual typing allowed.
```python
from typing import Any, Dict, Protocol

class ConfidenceCheck(Protocol):
    name: str
    weight: float
    def evaluate(self, context: Dict[str, Any]) -> tuple[bool, str]: ...
```

### Docstrings
Use Google-style docstrings for public APIs.
```python
def get_recommendation(self, confidence: float) -> str:
    """Get recommended action based on confidence level.

    Args:
        confidence: Confidence score (0.0-1.0)

    Returns:
        Recommended action string.
    """
```

### Error Handling
- Prefer specific exceptions; avoid bare `except:`.
- Fail loudly on configuration issues; degrade gracefully on optional files.
```python
try:
    content = path.read_text(encoding="utf-8")
except (OSError, UnicodeDecodeError):
    return ""
```

### Dataclasses
Use `@dataclass` for data containers.
```python
@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    weight: float
```

## Architectural Patterns
- Protocol-based checks in `pm_agent/` keep behavior pluggable.
- Registry pattern for check discovery (`ConfidenceChecker.register_check`).
- Cache expensive detection with `@lru_cache`.

## Cursor/Copilot Rules
- No `.cursor/rules`, `.cursorrules`, or `.github/copilot-instructions.md` found.

## Commit Message Format
Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.

## Session Completion (When You Finish Work)
- File issues for remaining work.
- Run quality gates when code changed: `make test` and `make lint`.
- Push after commits: `git pull --rebase && git push`.
