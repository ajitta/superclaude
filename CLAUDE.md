# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Python Environment

This project uses **UV** for all Python operations. Never use `pip` or `python -m pytest` directly.

```bash
uv run pytest                              # Full suite
uv run pytest tests/unit/ -v               # Unit tests only
uv run pytest tests/integration/ -v        # Integration tests
uv run pytest -k "test_agent"              # By name pattern

uv pip install -e ".[dev]"                 # Install editable
uv run superclaude install --list-all      # Test CLI changes
```

- **Test baseline**: 1,628 passing / 1,807 collected — do not regress. Markdown-only changes carry no test risk.

## Make Commands

```bash
make install       # uv pip install -e ".[dev]"
make deploy        # Deploy CLI (editable, uv tool install). Content sync is separate.
make sync-user     # Force-sync src/ content to ~/.claude/ (user scope) — for headless `claude -p` testing
make sync-project  # Force-sync to ./.claude/ (project scope, team-shared)
make sync-local    # Force-sync to ./.claude/ (local scope, gitignored)
make test          # uv run pytest
make test-plugin   # Verify pytest plugin loads
make verify        # Full installation check
make lint          # ruff check
make format        # ruff format
make doctor        # Health check
make clean         # Remove artifacts
```

## Code Style

- Python ≥3.10, ruff (line-length 88, ignores E501)
- Run `make format` before committing

## Developer Environment

- `make deploy` runs `uv tool install --force --editable .` (CLI editable) only. Content sync is a separate scope-explicit step: `make sync-user` / `sync-project` / `sync-local`. The `--force` in sync targets is intentional — needed for non-interactive headless `claude -p` test scenarios. For interactive dev sync use `superclaude install -i`.
- Template variables `{{SCRIPTS_PATH}}` and `{{SKILLS_PATH}}` resolved at install time
- Experimental Agent Teams: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

## Architecture

SuperClaude is a **content framework** — markdown files (commands, agents, modes, skills, MCP docs, core config) installed into `~/.claude/` to configure Claude Code's behavior. Ships a CLI (`superclaude`) and a pytest plugin for auto-markers.

**Full taxonomy:** `src/superclaude/ARCHITECTURE.md` (directory roles, delivery pipelines, content types).

- **CLAUDE_SC.md import chain**: `@superclaude/CLAUDE_SC.md` → `core/FLAGS.md`, `PRINCIPLES.md`, `RULES.md`
- **Hooks merge (not replace)**: `install_settings.py` preserves user hooks via marker-based identification
- Authoring rules live in `.claude/rules/` (agent, command, skill, mode — auto-loaded by CC)
- Serena session memories live in `.serena/` (committed for cross-session context)

## Gotchas

Project-specific traps: `.claude/rules/gotchas/general.md` (+ domain files with `paths:` frontmatter). Format: `- name: description`. Top trap: do **not** Read sub-agent `*.output` files — wait for the returned summary.

## Git Workflow

Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
