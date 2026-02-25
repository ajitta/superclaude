# Task Completion Checklist

When a coding task is completed, run these checks:

## 1. Lint
```bash
uv run ruff check .
```
Fix any issues before proceeding.

## 2. Format
```bash
uv run ruff format .
```

## 3. Tests
```bash
uv run pytest                    # Full suite (734 tests, v4.3.0)
uv run python -m pytest         # Windows fallback
uv run pytest tests/unit/ -v    # Unit tests if only Python changes
```
All tests must pass.

## 4. Type Check (if touching typed code)
```bash
uv run mypy src/superclaude
```

## 5. Plugin Verification (if touching plugin/CLI)
```bash
make test-plugin
```

## 6. Git
- Create feature branch if not on one
- Commit with conventional prefix: feat:, fix:, docs:, refactor:, test:, chore:
- Keep commits incremental and focused

## Quick One-Liner
```bash
uv run ruff check . && uv run ruff format . && uv run pytest
```
