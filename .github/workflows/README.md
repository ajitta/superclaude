# GitHub Actions Workflows

This directory contains CI/CD workflows for SuperClaude Framework.

## Workflows

### 1. **test.yml** - Comprehensive Test Suite
**Triggers**: Push/PR to `master` or `integration`, manual dispatch
**Jobs**:
- **test**: Run tests on Python 3.10, 3.11, 3.12
  - Install UV and dependencies
  - Run full test suite
- **checks**: Lint, plugin and doctor checks on Python 3.10
  - Run ruff linter and format checker
  - Verify the pytest plugin loads (report header)
  - Run `superclaude doctor` health check

**Status Badge**:
```markdown
[![Tests](https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml/badge.svg)](https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml)
```

### 2. **publish-pypi.yml** (Existing)
**Triggers**: Manual or release tags
**Purpose**: Publish package to PyPI

### 3. **readme-quality-check.yml** (Existing)
**Triggers**: Push/PR affecting README files
**Purpose**: Validate README quality and consistency

## Local Testing

Before pushing, run these commands locally:

```bash
# Run full test suite
uv run pytest -v

# Run with coverage
uv run pytest --cov=superclaude --cov-report=term

# Run linter
uv run ruff check src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Auto-fix formatting
uv run ruff format src/ tests/

# Verify plugin loads
uv run pytest --trace-config | grep superclaude

# Run doctor check
uv run superclaude doctor --verbose
```

## CI/CD Pipeline

```
┌─────────────────────┐
│   Push/PR Created   │
└──────────┬──────────┘
           │
    ┌──────▼─────────┐
    │  Full Test     │
    │   Matrix       │
    │                │
    │ • Python 3.10  │
    │ • Python 3.11  │
    │ • Python 3.12  │
    │ • Lint         │
    │ • Plugin check │
    │ • Doctor check │
    │                │
    │ ~5-8 min       │
    └────────────────┘
```

## Coverage Reporting

CI does not run coverage. To view coverage locally:
```bash
uv run pytest --cov=superclaude --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Workflow fails with "UV not found"
- UV is installed in each job via `curl -LsSf https://astral.sh/uv/install.sh | sh`
- If installation fails, check UV's status page

### Tests fail locally but pass in CI (or vice versa)
- Check Python version: `python --version`
- Reinstall dependencies: `uv pip install -e ".[dev]"`
- Clear caches: `rm -rf .pytest_cache .venv`

### Plugin not loading in CI
- Verify entry point in `pyproject.toml`: `[project.entry-points.pytest11]`
- Check plugin is installed: `uv run pytest --trace-config`

## Maintenance

### Adding a New Workflow
1. Create new `.yml` file in this directory
2. Follow existing structure (checkout, setup-python, install UV)
3. Add status badge to README.md if needed
4. Document in this file

### Updating Python Versions
1. Edit `matrix.python-version` in `test.yml`
2. Update `pyproject.toml` classifiers
3. Test locally with new version first

### Modifying Test Strategy
- **test.yml**: For comprehensive validation (full matrix)

## Best Practices

1. **Keep workflows fast**: Use caching, parallel jobs
2. **Clear names**: Job and step names should be descriptive
3. **Version pinning**: Pin action versions (@v4, @v5)
4. **Matrix testing**: Test on multiple Python versions
5. **Manual triggers**: Add `workflow_dispatch` for debugging

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Pytest Documentation](https://docs.pytest.org/)
- [SuperClaude Testing Guide](../../CLAUDE.md) (Python Environment + Make Commands sections)
