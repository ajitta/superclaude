# Changelog

User-visible changes to this fork of SuperClaude: behavior, commands, flags, CLI subcommands, hooks, make targets, dependencies, and what an upgrade asks of you. Internal refactors and tests are in the commit log.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html), and `pyproject.toml` is the version source. A release is tagged `vX.Y.Z`, and the `stable` branch points at the latest one.

Releases before 4.19.0 are not listed. Their history is the git log; the upstream-era changelog, last entry 4.2.1, is `CHANGELOG.md` at commit `6b0ac5c3^`.

## [4.21.0] - 2026-10-07

### Changed

- Installed content (commands, agents, modes, MCP docs, core rules) was audited against the Claude Opus 5.5 prompting guidance and cleaned up. Scores that no tool computes are gone: research confidence thresholds and time budgets, and the `/sc:agent` 0.90 confidence gate, which now waits on confirmed scope, success criteria and acceptance checks instead. Replanning triggers in `/sc:research`, `deep-researcher` and `RESEARCH_CONFIG.md` are stated in words (sources disagree on a load-bearing claim, fewer than 3 independent sources, core question unanswered). Caps-lock emphasis, pinned "Opus 4.x" model claims and the generic "ask the user when unsure" fallback line are removed where the authoring rule makes them optional.
- Source credibility is one scale: the four tiers in `RESEARCH_CONFIG.md` (tier 1 highest), named from `deep-researcher` and `/sc:research`. The agent's separate 1–5 scale and the config's 0.x score column are gone.
- `git-workflow` agent: `git add` now asks first (it was listed as a read-only op); `git fetch` proceeds and is labelled for what it writes (remote-tracking refs only). PR review state is GitHub's `REVIEW_REQUIRED`; the `PENDING` value never existed. `/sc:git` keeps `add`, `commit`, `pull` and `fetch` as safe because the user typed the op.
- `/sc:agent` no longer lists the removed `confidence-check` service. `/sc:promote-feature`, `/sc:cleanup --type docs` and the commands README no longer cite the doc-convention-v2 discovery document, which no longer exists.
- `business-panel-experts` picks its own analysis mode instead of asking first. `python-expert` checks diff coverage on changed code; the overall line and branch gate belongs to `quality-engineer`. `project-manager` is no longer suggested for proactive use at session start. `MCP_Tavily.md` no longer bans questions "answerable from training".
- `MODE_Orchestration` cites the Workflow fan-out process cap from `core/FLAGS.md` (min(16, cpu−2)) instead of an unsourced per-session agent cap.
- Portable skills `socratic-brainstorm` 3.2.1 and `socratic-elenchus` 1.2.1: the per-message length rule reads "a turn fits a phone screen without scrolling" instead of a line count. Re-upload `portable-skills/releases/<skill>.zip`, or `/plugin update` in Claude Code, to get it.
- Contributor instructions live in `AGENTS.md`; `CLAUDE.md` imports it. The repo no longer calls itself a fork, and CI runs on Python 3.10 and 3.13.

### Fixed

- R16 Safe Read states the hook's single rule: a Read of 30 KB or more needs `limit` or `pages`. No 5 KB or config-file exemption exists in `file_size_guard.py`.
- `/sc:init` task (g) names the live auto-memory path (`~/.claude/projects/<project>/memory/`) instead of `.claude/memory/`, which nothing loads. `/sc:auto-improve` maps its positional project argument to `--project`. `/sc:help` no longer says `/sc:build` deploys.
- Serena project memories and the workflows README name `AGENTS.md` and the actual `make lint` target (`ruff check`; the format check runs in CI).

### Upgrade notes

- Installed content changed across many commands, agents, modes and core rules. `superclaude update --scope <scope>` refreshes it for each installed scope; skip scopes that `superclaude doctor --scope <scope>` reports as not installed, because `update` creates an install where none exists.
- After the update, the `git-workflow` agent asks before `git add`; answer once per staging step or stage yourself.

## [4.20.1] - 2026-10-05

### Changed

- Version numbers drop the `+ajitta` local suffix. This release is `4.20.1`, and its tag is `v4.20.1`.
- README installs the CLI with `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable`, with no clone. `stable` is a branch that moves only when a release is made, so `uv tool upgrade superclaude` pulls the latest release rather than whatever was last merged to master. To pin a release, install `@v<version>` instead.

### Added

- Each release is a GitHub release with a `v<version>` tag, and its notes are this file's entry for that version. `make release` creates it from a clean, pushed master HEAD whose Tests workflow passed, then moves `stable` to it.

### Upgrade notes

- If you installed from the git URL without `@stable` (the README said so for a few hours on 2026-10-05), that install follows master. Run `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable` once; `--force` is not needed. After that, `uv tool upgrade superclaude` stays on releases.
- Installed content changed only in the version line of `/sc:sc`. `superclaude update --scope <scope>` refreshes it for each installed scope; skip scopes that `superclaude doctor --scope <scope>` reports as not installed, because `update` creates an install where none exists.

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
