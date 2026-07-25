---
paths: ["src/superclaude/scripts/**", "src/superclaude/hooks/**", "src/superclaude/utils/**", "src/superclaude/cli/**"]
---

# Project Gotchas — Hook Scripts & Path Resolution
# Last reviewed: 2026-07-25
# Python runtime traps in hook scripts + CLI. Content-authoring traps live in authoring.md.

- hook-path-scope: Hook scripts + hook-imported modules resolve `.claude` paths via `superclaude.utils` resolvers — `project_root()`, `claude_base()`, `hook_state_dir()`. `Path.home() / ".claude"` and `Path.cwd() / ".claude"` in that position are the bug, not the baseline: hook CWD is NOT guaranteed to be the project root (CC documented behavior), and hardcoded `$HOME` makes a local/project-scope install write state where `superclaude uninstall` cannot reach it. Three instances found 2026-07-25 (`context_loader`, `context_reset` + `hook_tracker`/`mcp_fallback`, `get_skill_directories`); commit `52b5517`. Symptom of the CWD variant is silent: from a subdirectory the skills banner reported 9 skills instead of 22 and the token estimate 55612 instead of 94011 — no error, just wrong scope.
- cli-vs-hook-cwd: Counterpart of the above — do NOT apply `project_root()` inside `cli/` modules. `install_paths.py:39` `Path.cwd() / ".claude"` is correct: the user types `superclaude install --scope local` from the project root, and `CLAUDE_PROJECT_DIR` exists only inside a CC session, so the resolver would make the CLI behave differently inside vs outside Claude Code. Hook code follows the install; CLI code follows the user's shell.
- hook-runtime-state-uninstall: New runtime state written by a hook goes under `claude_base()` so `uninstall_all()` reaches it — step 5a unlinks files, 5b rmtree's directories (`install_inventory.py`). State placed outside `base_path` survives uninstall silently and is invisible to `--list-all`.
