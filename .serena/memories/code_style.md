# Code Style & Conventions

## Python
- **Line length**: 88 (ruff/black-compatible)
- **Target**: Python 3.10+
- **Type hints**: Gradual typing (mypy with `disallow_untyped_defs = false`)
- **Imports**: Sorted by ruff (isort rules via "I" selector)
- **Naming**: Standard Python (snake_case functions/variables, PascalCase classes)
- **Docstrings**: Not enforced but present on public APIs

## Linting Rules (ruff)
- Selected: E (pycodestyle errors), F (pyflakes), I (isort), N (pep8-naming), W (pycodestyle warnings)
- Ignored: E501 (line length handled by formatter)
- Excluded: `docs/` directory

## Design Patterns
- **Protocol-based**: `ConfidenceCheck` protocol with pluggable checks (see confidence.py)
- **Dataclass-heavy**: `CheckResult`, `ConfidenceResult`, `Task`, `ParallelGroup`, `ExecutionPlan`, `HookExecution`, `SessionData`
- **Click CLI**: Group-based command structure with decorators
- **Auto-discovery**: Pytest plugin via `pytest11` entry point
- **Frontmatter**: YAML frontmatter in markdown files parsed by `inline_hooks.py`

## Markdown Content Files
- Commands: YAML frontmatter with context, agent, user-invocable, allowed-tools fields
- Agents: Markdown definitions with trigger keywords and tool descriptions
- Modes: Behavioral mode definitions
- MCP: Server documentation with JSON configs in `configs/` subdirectory

## Test Conventions
- Test files: `test_*.py` in `tests/unit/` and `tests/integration/`
- Test classes: `Test*`
- Test functions: `test_*`
- Markers: confidence_check, self_check, reflexion, complexity, hallucination, performance
- Auto-markers: unit/integration added by path in `pytest_collection_modifyitems`
- Fixtures in `conftest.py` and `pytest_plugin.py`

## Anti-Patterns to Avoid
- Never use pip directly (always UV)
- Don't over-engineer — build only what's asked
- Bug fix ≠ cleanup opportunity
- Delete unused code completely (no commented-out remnants)
- Don't add docstrings/comments to unchanged code
