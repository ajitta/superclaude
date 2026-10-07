# GitHub Actions Workflows

## test.yml

**Triggers**: `make ci` and `make release` (both dispatch it on `origin/master` and wait), manual dispatch (`gh workflow run Tests --ref <branch>`), and pull requests to `master` except those that only change `.serena/` (session memories, which no test reads). A push does not run it: users get `stable`, the default branch, so `master` is checked when a release is cut.

**Jobs**:
- **test**: Python 3.10 and 3.13 (the oldest supported version and the newest)
  - Full test suite
  - `tests/unit/scripts` in a separate pytest process (the default run skips it through `--ignore` in pyproject addopts)
- **checks**: Python 3.10
  - `ruff check` and `ruff format --check` over `src/` and `tests/`
  - Pytest plugin loads (its `SuperClaude: ` report header)
  - `superclaude install --scope user` followed by `superclaude doctor`

`make release` runs `make ci` after its local checks and stops unless the run is green; a commit that already has a green run is not re-run.

**Status Badge**:
```markdown
[![Tests](https://github.com/ajitta/superclaude/actions/workflows/test.yml/badge.svg)](https://github.com/ajitta/superclaude/actions/workflows/test.yml)
```

## Local Testing

The same checks, run locally before pushing:

```bash
uv run pytest                                  # full suite
uv run pytest tests/unit/scripts -o addopts=   # scripts tests
make lint                                      # ruff check (format check runs in CI)
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
