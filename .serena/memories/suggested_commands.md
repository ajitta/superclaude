# Suggested Commands

## Testing
```
uv run pytest                              # Full suite
uv run pytest tests/unit/ -v               # Unit tests only
uv run pytest tests/integration/ -v        # Integration tests
uv run pytest -k "test_agent"              # By name pattern
```

## Installation & Deployment
```
make install       # uv pip install -e ".[dev]"
make deploy        # Deploy CLI (editable, uv tool install). Content sync separate.
make sync-user     # Force-sync src/ content to ~/.claude/ (user scope)
make sync-project  # Force-sync to ./.claude/ (project scope, team-shared)
make sync-local    # Force-sync to ./.claude/ (local scope, gitignored)
uv run superclaude install --list-all      # Test CLI changes
```

## Code Quality
```
make lint          # ruff check
make format        # ruff format (run before committing)
make verify        # Full installation check
make doctor        # Health check
make clean         # Remove artifacts
```

## Uninstall
```
make uninstall-user    # Uninstall from ~/.claude/ (interactive confirm)
make uninstall-project # Uninstall from ./.claude/ (project scope)
make uninstall-local   # Uninstall from ./.claude/ (local scope)
```

## Windows-compatible shell commands
- Use PowerShell: `Get-ChildItem`, `Select-String`, `$env:VAR`
- Git: standard git commands work fine
- `rtk` prefix available for token-optimized output (RTK tool)
