# AGENTS.md

Guidance for coding agents (Codex, Claude Code) working in this repository. Claude Code reads this file through the `@AGENTS.md` import in `CLAUDE.md`; Claude-only notes go there, everything else goes here.

## Python Environment

This project uses **UV** for all Python operations. Never use `pip`, `python -m pytest`, or `uv sync` directly — the only exception is the last-resort Tests fallback below.

```bash
uv run superclaude install --list-all      # Test CLI changes
```

- **Never `uv sync`**: the dev toolchain is declared in `[project.optional-dependencies].dev`, not a default dependency group, so `uv sync` prunes ruff, mypy and pytest-asyncio and the suite stops running. `uv sync --dry-run` lists what it would remove. Install and repair with `uv pip install -e ".[dev]"`.
- **Tests**: the full `uv run pytest` must exit 0 at each integration point — before merging a branch into `master` and before pushing `master` (commits made directly on `master` are checked once, before their push). A commit on a feature branch runs only the tests for the area it changed: the `*-authoring.md` rule for that content type names them; for code, the test file of the changed module. Run each check once, not after every edit. Exempt: a commit whose changed files are all under `.claude/memories/` — no test reads their content. No known pre-existing failures — a red test is a regression from your change, never a known issue. It works on Windows when `.venv` is healthy; the `Failed to canonicalize script path` error means `.venv` is corrupt (often a broken `lib64` symlink) — rebuild it: `rm -rf .venv && uv venv && uv pip install -e ".[dev]"`. Last-resort fallbacks: `.venv/Scripts/python.exe -m pytest` → WSL → push the branch and run CI on it with `gh workflow run Tests --ref <branch>` (a push alone runs no CI; `make ci` checks `origin/master`). Markdown is linted too — content counts, cross-refs and doc structure have tests, so a `docs/` change still needs the full suite at the integration point.
- **Canary before a release**: `make release` refuses when `src/superclaude/core` or `hooks.json` changed since the last `v*` tag unless `CANARY_OK=1` — run `make canary-gates` (the hard-gate tasks, local `claude -p`, sonnet, low effort; no API key; inside a Claude Code session add `EVAL_ARGS="--runs-dir <new dir outside ~/.claude>"`) and read its report first. The full `--canary` suite is for model releases only, never with Fable (headless Fable bills usage credits). When a gotcha or insight records a behavior failure, add a canary probe for it in `evals/tasks.yaml` so the next model or prompt change cannot bring it back silently (`evals/README.md`).
- **Script tests are in the default run**: `uv run pytest` includes `tests/unit/scripts/` again (the `--ignore` workaround for a Windows native abort was retired after eight clean full runs — docs/features/test-exclusion-lift). `make test-scripts` runs only that directory. If a `0xC0000409` abort reappears on Windows, revert the lift commit and bisect `tests/unit/scripts/parallel_ab/` (the suite's only asyncio tests).

## Code Style

- Run `make format` and `make lint` before committing — CI fails on `ruff format --check` or `ruff check` over `src/` and `tests/`
- `make typecheck` (mypy, not in CI) must not exceed `MYPY_BASELINE` in the Makefile; lower the baseline when you fix errors, never raise it

## Developer Environment

- `make deploy` runs `uv tool install --force --editable .` (CLI editable) only. Content sync is a separate scope-explicit step: `make sync-user` / `sync-project` / `sync-local`. The `--force` in sync targets is intentional — needed for non-interactive headless `claude -p` test scenarios. For interactive dev sync use `superclaude install -i`.
- Hook commands are `superclaude hook <name>` (console entry; registry in `cli/hook_dispatch.py`) — no install-time template, no machine-specific bytes in a committed settings.json

## Architecture

superclaude is a **content framework** — markdown files (commands, agents, skills, modes, output styles, MCP docs, core config) installed into `~/.claude/` to configure Claude Code's behavior. Ships a CLI (`superclaude`) and a pytest plugin for auto-markers.

**Full taxonomy:** `src/superclaude/ARCHITECTURE.md` (directory roles, delivery pipelines, content types).

- **CLAUDE_SC.md import chain**: `@.claude/superclaude/CLAUDE_SC.md` → `core/FLAGS.md`, `PRINCIPLES.md`, `RULES.md` (path after install or sync)
- **Hooks merge (not replace)**: `install_settings.py` preserves user hooks via marker-based identification
- Authoring rules live in `.claude/rules/`: one `*-authoring.md` per content type, plus `content-quality.md` and `xml-prose-format.md`. Claude Code auto-loads them; other agents read the matching file before editing that content type.
- Session memories live in `.claude/memories/` (committed, written by `/sc:save`, read by `/sc:load`)

## Gotchas

Project-specific traps: `.claude/rules/gotchas/general.md` (+ domain files with `paths:` frontmatter). Claude Code auto-loads them; other agents read `general.md` before starting work. Format: `- name: description`. Top trap: do **not** Read sub-agent `*.output` files — wait for the returned summary.

## Git Workflow

Branch: `stable` (release channel and GitHub default branch, moved only by `make release`; the plugin marketplace and Pages serve it) ← `master` (development; clone with `-b master`) ← `feature/*`, `fix/*`, `docs/*`

Release: version-bump branch merged and green on master → `make release`

Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Agent skills

### Issue tracker

Issues live as local markdown under `.scratch/<feature>/`, not GitHub issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary — label strings match canonical role names verbatim. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `docs/adr/` at repo root; the root `CONTEXT.md` is created lazily and may be absent. See `docs/agents/domain.md`.
