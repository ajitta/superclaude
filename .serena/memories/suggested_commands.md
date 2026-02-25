# Suggested Commands for SuperClaude Development

## System: Windows 11 (win32, bash shell in Claude Code)

## Package Management (UV only — never use pip)
```bash
uv pip install -e ".[dev]"          # Install editable with dev deps (RECOMMENDED)
uv tool install --force --editable . # Deploy as global uv tool
uv run superclaude --version         # Check version
uv run superclaude doctor            # Health check
uv run superclaude install           # Install content to ~/.claude/
uv run superclaude install --list-all # List all installable components
uv run superclaude uninstall         # Remove installed content
uv run superclaude mcp               # MCP server management
```

## Testing
```bash
uv run pytest                              # Full test suite (734 tests)
uv run python -m pytest                    # Alternative invocation
uv run pytest tests/unit/ -v               # Unit tests only
uv run pytest tests/integration/ -v        # Integration tests
uv run pytest tests/unit/test_confidence.py -v  # Single file
uv run pytest -m confidence_check          # By marker
uv run pytest -k "test_assess"             # By name pattern
uv run pytest --cov=src/superclaude        # With coverage
```

## Linting & Formatting
```bash
uv run ruff check .                # Lint (ruff, rules: E, F, I, N, W; ignores E501)
uv run ruff format .               # Format (black-compatible, line-length 88)
uv run mypy src/superclaude        # Type check (gradual typing)
```

## Make Shortcuts
```bash
make install       # uv pip install -e ".[dev]"
make deploy        # Deploy to global uv tool
make test          # uv run pytest
make test-plugin   # Verify pytest plugin loads
make verify        # Full installation check
make lint          # ruff check
make format        # ruff format
make doctor        # Health check
make clean         # Remove artifacts (__pycache__, .pytest_cache, etc.)
make build-plugin  # Build plugin artefacts to dist/
```

## Git
```bash
git status                    # Check working tree
git log --oneline -10         # Recent commits
git checkout -b feature/name  # New feature branch
# Commits: feat:, fix:, docs:, refactor:, test:, chore:
```

## Windows-specific Notes
- Claude Code uses bash shell on Windows (Unix syntax, forward slashes)
- Use `/c/Users/...` paths in bash, `C:\Users\...` in tool paths
- `uv run pytest` may show "Failed to canonicalize script path" — use `uv run python -m pytest` as fallback
