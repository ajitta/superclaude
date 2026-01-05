# Repository Guidelines for AI Agents

SuperClaude is a Python-based pytest plugin and framework for Claude Code, providing
PM Agent capabilities (confidence checks, reflexion, self-check, token budgeting)
plus configuration assets (agents, commands, modes, MCP configs).

## Project Structure
```
src/superclaude/           # Core package
  cli/                     # CLI commands (Click-based)
  pm_agent/                # PM Agent: confidence, reflexion, self_check, token_budget
  execution/               # Parallel execution, reflection, self-correction
  agents/                  # Agent definition markdown files
  commands/                # Slash command markdown files
  modes/                   # Mode configuration files
  hooks/                   # Hook definitions (hooks.json)
  scripts/                 # Utility scripts (session_init, context_loader)
  mcp/                     # MCP server configurations
  skills/                  # Skill definitions
  pytest_plugin.py         # pytest plugin entry point
tests/
  unit/                    # Unit tests
  integration/             # Integration tests
  conftest.py              # Shared fixtures
```

## Build, Test, and Lint Commands
```bash
# Installation
make install              # Dev install: uv pip install -e ".[dev]"

# Running Tests
make test                 # Run all tests: uv run pytest
uv run pytest tests/unit  # Run only unit tests
uv run pytest -m unit     # Run tests marked 'unit'
uv run pytest -m integration  # Run integration tests

# Run a single test file
uv run pytest tests/unit/test_confidence.py

# Run a single test function
uv run pytest tests/unit/test_confidence.py::TestConfidenceChecker::test_high_confidence_scenario

# Run with verbose output
uv run pytest -v tests/unit/test_confidence.py

# Run with coverage
uv run pytest --cov=src/superclaude tests/

# Linting and Formatting
make lint                 # uv run ruff check .
make format               # uv run ruff format .
uv run ruff check --fix . # Auto-fix lint issues
uv run mypy src/          # Type checking (gradual typing)

# Verification
make verify               # Full installation verification
make doctor               # Health check: uv run superclaude doctor
make test-plugin          # Verify pytest plugin auto-discovery
```

## Code Style Guidelines

### Python Version and Formatting
- **Python 3.10+** required
- **Line length**: 88 characters (Ruff/Black)
- **Indentation**: 4 spaces
- **Formatter**: Ruff (`uv run ruff format .`)
- **Linter**: Ruff with rules `E/F/I/N/W` (ignore E501)

### Import Organization
Imports are sorted by Ruff (isort-compatible). Order:
1. Standard library
2. Third-party packages
3. Local imports

```python
import sys
from pathlib import Path

import click

from superclaude import __version__
```

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `pytest_plugin.py`, `token_budget.py` |
| Classes | CapWords | `ConfidenceChecker`, `CheckResult` |
| Functions | snake_case | `assess_confidence`, `get_recommendation` |
| Constants | UPPER_SNAKE | `DEFAULT_CHECKS`, `VAGUE_TERMS` |
| Context files | kebab-case | `deep-research.md`, `security-engineer.md` |

### Type Hints
- Use type hints for function signatures
- Use `Dict`, `List`, `Tuple`, `Any` from `typing` module
- Protocol classes for duck typing (`ConfidenceCheck`, `AsyncConfidenceCheck`)
- Gradual typing allowed (`disallow_untyped_defs = false` in mypy)

```python
from typing import Any, Dict, List, Protocol, Tuple

def assess(self, context: Dict[str, Any]) -> ConfidenceResult:
    ...
```

### Docstrings
Use triple-quoted docstrings for modules, classes, and public functions:
```python
def get_recommendation(self, confidence: float) -> str:
    """
    Get recommended action based on confidence level.

    Args:
        confidence: Confidence score (0.0 - 1.0)

    Returns:
        str: Recommended action
    """
```

### Error Handling
- Use specific exception types when possible
- Catch `OSError`, `PermissionError` for file operations
- Use `try/except` with specific handling, not bare `except`

```python
try:
    content = file_path.read_text(encoding="utf-8")
except (OSError, UnicodeDecodeError):
    pass  # Handle gracefully
```

### Dataclasses
Use `@dataclass` for data containers with type hints:
```python
@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    weight: float
```

## Testing Guidelines

### Test Structure
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use fixtures from `conftest.py`

### Pytest Markers
```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.asyncio        # Async tests
@pytest.mark.confidence_check  # Confidence-related tests
```

## Commit Message Format
Follow Conventional Commits:
```
feat(scope): add new feature
fix(scope): fix bug description
docs: update documentation
chore: maintenance task
refactor(scope): code restructuring
test(scope): add or update tests
```

## Key Architectural Patterns

### Protocol-based Design
```python
@runtime_checkable
class ConfidenceCheck(Protocol):
    name: str
    weight: float
    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]: ...
```

### Registry Pattern
```python
checker = ConfidenceChecker(register_defaults=False)
checker.register_check(CustomCheck())
```

### LRU Caching
Use `@lru_cache` for expensive operations:

```python
@lru_cache(maxsize=32)
def _cached_detect_tech_stack(project_root_str: str) -> tuple:
    ...
```
