# Changelog

User-visible changes to this fork of SuperClaude: behavior, commands, flags, CLI subcommands, hooks, make targets, dependencies, and what an upgrade asks of you. Internal refactors and tests are in the commit log.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with a `+ajitta` local suffix, and `pyproject.toml` is the version source.

Releases before 4.19.0 are not listed. Their history is the git log; the upstream-era changelog, last entry 4.2.1, is `CHANGELOG.md` at commit `6b0ac5c3^`.

## [4.20.0+ajitta] - 2026-10-04

### Added

- Every `/sc:` command that takes flags has a `<flags>` section with one line per command-local flag, which defines the flag or points to the step or section that does. Flags that had no definition before include `/sc:cleanup --safe` / `--aggressive`, `/sc:estimate --type` / `--breakdown`, `/sc:explain --level`, `/sc:load --type`, `/sc:roadmap --strategy`, `/sc:troubleshoot --trace`, `/sc:improve --interactive`, `/sc:pm --verbose` and `/sc:recommend --estimate` / `--alternatives`. `/sc:build --clean` deletes only the output directory of the chosen `--type` (`dist-dev/`, `dist/` or `dist-test/`) and never runs `git clean`. `/sc:cleanup --dry-run` is a read-only preview for any `--type`.

### Changed

- `--safe` on `/sc:cleanup`, `/sc:improve` and `/sc:implement` follows one rule: changes that reach exported functions, config files or shared modules are not applied without approval. `/sc:cleanup --safe` changes only the safe tier (unused imports, dead variables, empty files) and lists the rest; `/sc:improve --safe` lists such changes as proposals; `/sc:implement --safe` shows each one and waits for approval. None of them is the global `--safe-mode`.
- `/sc:test --fix` is defined: on a failing test it finds the root cause the way `/sc:troubleshoot --type bug` would, fixes the code and re-runs the tests, and never edits a test only to make it pass.
- Commands that reuse a global flag name define their own meaning in `<flags>` and say it is unrelated to the global flag: `/sc:implement --plan <path>`, `/sc:review --scope pr|diff|file|branch|plan|design|spec`, `/sc:reflect --validate`, `/sc:auto-improve --scope <glob>` and `/sc:spec-panel --focus implementability|simplicity|reliability|testing|observability`. `/sc:analyze --focus` takes the global domains plus `rules`. `/sc:business-panel --focus <domain>` picks the experts the Analyze step applies and is ignored when `--experts` or `--all-experts` is given.

### Removed

- The SessionStart state sweep no longer deletes the `hook_executions*` and `current_session*` files left in `.superclaude_hooks/` by the `hook_tracker` hook removed in 4.19.0.

### Fixed

- The prompt hook (`context_loader`) no longer reports a flag that a `/sc:` command defines in its `<flags>` section as a typo of a global flag, and no longer injects the global directive for a flag name the command redefines. `/sc:implement auth --safe` drew "Did you mean: --safe-mode?", and `/sc:implement --plan docs/plans/x.md` drew the global `--plan` directive (write a 5-line plan and wait), although that `--plan` takes a plan file to follow.
- `/sc:troubleshoot` without `--fix` stops after the Confirm step and proposes the fix; with `--fix` it runs the Test, Fix and Verify steps, and a fix in the approval-required tier of the auto-fix threshold still waits for confirmation. Before, the command's steps listed writing a failing test and applying the fix with no condition, and the `--fix` rule appeared only in the command description.
- An error-path example in `/sc:document` used `--detailed`, which the command does not accept; it now reads `--style detailed`.

### Upgrade notes

- Re-sync each scope you have installed: check with `superclaude doctor --scope <scope>`, then run `superclaude update --scope <scope>` (the same as `install --force`). The hook reads `<flags>` from the installed command files, so until they are refreshed `/sc:implement --safe` still draws the typo notice and `/sc:implement --plan <path>` still draws the global `--plan` directive. Run `update` only for installed scopes: it creates an install where none exists.
- Upgrading straight from 4.18.x or earlier, `hook_executions*` and `current_session*` files may remain in `.superclaude_hooks/`. Nothing reads them; delete them or leave them. `superclaude uninstall` removes the directory.

## [4.19.0+ajitta] - 2026-10-03

### Added

- Two portable Agent Skills under `portable-skills/`: `socratic-brainstorm` (3.2.0) and `socratic-elenchus` (1.2.0). `superclaude install` does not install them. Upload `portable-skills/releases/<skill>.zip` at claude.ai › Customize › Plugins, or in Claude Code run `/plugin marketplace add ajitta/superclaude` and then `/plugin install <skill>@ajitta-socratic`. `portable-skills/README.md` covers Codex and copy-in installs.

### Changed

- `superclaude doctor` runs five checks instead of six: the `Configuration` check is gone. With `--verbose` the version still shows in the details of the `superclaude on PATH` check. `pytest plugin loaded` only confirms that SuperClaude's `pytest11` entry point is registered.

### Removed

- `superclaude audit` and `make audit`. Use `superclaude verify-drift` (or `make verify-drift`) for install drift; in a checkout, `uv run pytest` covers the cross-reference and content checks `audit` ran.
- `superclaude agents` (`--list`, `--info`, `--tokens`), with no replacement. The installed agents are the `.md` files in the scope's `agents/` directory.
- `superclaude version`. Use `superclaude --version`, which prints `SuperClaude, version <x>`.
- The `--status` option of `superclaude mcp`. `superclaude mcp --list` shows whether each server is installed.
- The `make build-plugin`, `make sync-plugin-repo` and `make translate` targets, and `scripts/build_superclaude_plugin.py`. None worked from a plain checkout: `build-plugin` needed the already deleted `plugins/superclaude/` tree, `sync-plugin-repo` depended on it, and `translate` needed a locally built `neural-cli`. `make test-plugin` stays.
- Three lines of the SessionStart `session_init` hook output: `📊 Git: …` (Claude Code already supplies git status), `💡 Use /context to confirm token budget.`, and `📁 Multi-dir: N additional CLAUDE.md found` (shown only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`). The hook prints the PR-review status line, when there is one, and the install-status line.
- The once-per-session `<!-- N skills installed (...) -->` comment the `context_loader` hook added to context, and `CLAUDE_SHOW_SKILLS`, the variable that turned it off. `superclaude context explain` no longer prints its `skills:` line.
- `rich` from the runtime dependencies (nothing imported it); `black`, `pytest-benchmark` and `scipy` from the `dev` extra; and the `test` extra. Use `superclaude[dev]`.

### Fixed

- `superclaude insight list`, `query` and `stats` no longer need `jq`. Without `jq` on PATH they exited 1, which broke `/sc:insight --list`, `--query` and `--stats` and the dedup check `/sc:insight` runs before every capture. Output is unchanged, and a malformed line in `.claude/insights.jsonl` is skipped instead of aborting the read.

### Upgrade notes

- Update scripts and aliases that call a removed command: `superclaude audit` → `superclaude verify-drift` (plus `uv run pytest` in a checkout); `superclaude version` → `superclaude --version`, whose output reads `SuperClaude, version <x>` instead of `SuperClaude version <x>`; `superclaude mcp --status` → `superclaude mcp --list`. `superclaude agents` and the removed make targets have no replacement.
- `CLAUDE_SHOW_SKILLS` is no longer read; you can drop it from your environment.
- If your own code imports `rich` from the same environment, install it yourself. Request `superclaude[dev]` instead of `superclaude[test]`; a checkout's `uv pip install -e ".[dev]"` no longer installs `black`, `pytest-benchmark` or `scipy`.
- Hook changes apply as soon as the package is upgraded, because registered hooks run `superclaude hook <name>`. To refresh the installed command and agent files, check each installed scope with `superclaude doctor --scope <scope>` and run `superclaude update --scope <scope>`; for project or local scope, run it from the project directory.
- Leftover `current_session.txt` and `hook_executions.json` files from the removed hook tracker are deleted by the SessionStart state sweep once they have gone 7 days without changes. In 4.20.0 the sweep no longer does this; see that release.
- Contributors: `.pre-commit-config.yaml` is gone. If you ran `pre-commit install` in a checkout, run `pre-commit uninstall`.
