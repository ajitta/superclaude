# GitHub Actions Workflows

## test.yml

**Triggers**: push and pull request to `master`, manual dispatch

**Jobs**:
- **test**: Python 3.10 and 3.13 (the oldest supported version and the newest)
  - Full test suite
  - `tests/unit/scripts` in a separate pytest process (the default run skips it through `--ignore` in pyproject addopts)
- **checks**: Python 3.10
  - `ruff check` and `ruff format --check` over `src/` and `tests/`
  - Pytest plugin loads (its `SuperClaude: ` report header)
  - `superclaude install --scope user` followed by `superclaude doctor`

`make release` refuses to release a commit whose `Tests` run is not green, so this workflow is part of the release path.

**Status Badge**:
```markdown
[![Tests](https://github.com/ajitta/superclaude/actions/workflows/test.yml/badge.svg)](https://github.com/ajitta/superclaude/actions/workflows/test.yml)
```

## Local Testing

The same checks, run locally before pushing:

```bash
uv run pytest                                  # full suite
uv run pytest tests/unit/scripts -o addopts=   # scripts tests
make lint                                      # ruff check + format check
uv run pytest --collect-only -q | grep "^SuperClaude: "   # plugin loads
uv run superclaude doctor --verbose
```

CI does not run coverage. To view it locally:
```bash
uv run pytest --cov=superclaude --cov-report=html
```

## Troubleshooting

### Tests fail locally but pass in CI (or vice versa)
- CI runs on Linux; local development is often on Windows, where `tests/unit/scripts` only runs when invoked separately
- Check the Python version: CI covers 3.10 and 3.13 only
- Reinstall dependencies: `uv pip install -e ".[dev]"` (never `uv sync`, see AGENTS.md)

### Plugin check fails in CI
- Verify the entry point in `pyproject.toml`: `[project.entry-points.pytest11]`

## Updating Python Versions

1. Edit `matrix.python-version` in `test.yml`
2. Update `requires-python` and the classifiers in `pyproject.toml`
3. Test locally with the new version first
