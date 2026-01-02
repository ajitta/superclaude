# Repository Guidelines

SuperClaude is a Python-based framework and pytest plugin, plus a set of
configuration assets (agents, commands, modes, MCP configs) used by Claude
Code. Use this guide to navigate the repo and align contributions with project
standards. For current priorities and architecture, skim `PLANNING.md`,
`TASK.md`, `KNOWLEDGE.md`, and `CONTRIBUTING.md`.

## Project Structure & Module Organization
- `src/superclaude/`: Core package (CLI in `cli/`, pytest plugin in
  `pytest_plugin.py`, context files in `agents/`, `commands/`, `modes/`, `mcp/`).
- `tests/`: Pytest suites, split into `tests/unit` and `tests/integration`.
- `plugins/` and `scripts/`: Plugin packaging assets and automation scripts
  (e.g., `scripts/build_superclaude_plugin.py`).
- `docs/`: Documentation and developer guides.
- `skills/`: Codex/Claude skill definitions used by the framework.
- `pyproject.toml`: Python packaging metadata.

## Build, Test, and Development Commands
- `make install`: Development install via `uv pip install -e ".[dev]"`.
- `make test`: Run the pytest suite (`uv run pytest`).
- `make lint`: Lint with Ruff (`uv run ruff check .`).
- `make format`: Format with Ruff (`uv run ruff format .`).
- `make test-plugin`: Verify pytest plugin auto-discovery.
- `make doctor` / `make verify`: Health checks for local setup.
- `make build-plugin`: Build plugin artefacts into `dist/plugins/`.

## Coding Style & Naming Conventions
- Python 3.10+; 4-space indentation.
- Format with Ruff (line length 88); lint with Ruff’s `E/F/I/N/W` rules.
- Use `snake_case` for modules/functions and `CapWords` for classes.
- Context file names under `src/superclaude/{agents,commands,modes}` use
  lowercase or kebab-case (e.g., `security-engineer.md`, `implement.md`).

## Testing Guidelines
- Pytest is configured in `pyproject.toml`; tests live in `tests/`.
- Naming: `test_*.py`, classes `Test*`, functions `test_*`.
- Use markers like `unit`, `integration`, `hallucination`, `performance`:
  `uv run pytest -m unit`.
- Add tests for new behavior, especially CLI or plugin changes.

## Commit & Pull Request Guidelines
- Follow Conventional Commits seen in history:
  `feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `chore: ...`.
- Keep summaries imperative and scoped when helpful (e.g., `feat(mcp): ...`).
- PRs should include a concise description, testing notes, and related issues.
- Update relevant docs if you change commands, agents, or user-facing behavior.
