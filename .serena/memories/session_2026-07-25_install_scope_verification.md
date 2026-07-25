# Session 2026-07-25 — Local-scope install verification + hook path scoping

## Goal
Verify the local-scope SuperClaude install, then check `~/.claude/` for user-scope residue. Grew into fixing the path-resolution bugs that verification exposed.

## Verification result
Local scope (`superclaude install --list-all --scope local`): 8/9 components ✅. `src/superclaude/` vs `.claude/` diff clean — commands/core/modes/mcp identical; all 23 agents differ by exactly one line, `memory: project` → `memory: local`, which is the installer's intended local-scope rewrite. Hooks: 14 SC hook commands in `settings.local.json`, no marker duplication. Local scope confirmed (not project scope) via `.git/info/exclude` lines 20-52 carrying the SC block.

User scope was effectively clean: no `~/.claude/superclaude/`, no `~/.claude/CLAUDE.md`, zero `superclaude` matches in `settings.json` or its two `.bak` files. Residue removed: 13 stale `claude_context_*.txt` (oldest 2026-05-11) and 4 empty dirs holding only `.DS_Store` (`agents`, `commands`, `hooks`, `agent-memory`). `~/.claude.json` SC references are `githubRepoPaths`/`projects` bookkeeping — benign.

## Decisions
- **Scope hook state, don't just clean it.** `.superclaude_hooks` was hardcoded to `Path.home()` in 4 files, so cleaning was recurring maintenance rather than a fix. Routed all 4 through new resolvers instead. See `mem:project_overview` for where utils sits.
- **Anchor on `$CLAUDE_PROJECT_DIR`, not CWD.** `loop_guard.py:29` already did this and its state landed correctly under `./.claude/`; `.superclaude_hooks` was the outlier. Followed the existing precedent rather than inventing a mechanism.
- **Import `superclaude.utils` unconditionally in the two shipped hook scripts** (no try/except ImportError, unlike `mcp_fallback`). `utils` is stdlib-only and `{{PYTHON_BIN}}` resolves to the installer's own `sys.executable`, so the package is present by construction. A silent fallback would reintroduce the wrong-scope write the change exists to prevent.
- **Declined:** TTL prune for stale cache files. Different mechanism (no GC) from the scoping bug; scoped installs largely avoid accumulation by construction since the cache key is `md5(cwd)`.
- **Left as-is:** `install_paths.py:39` `Path.cwd()`. CLI context, not hook — CWD is correct there and `CLAUDE_PROJECT_DIR` only exists inside a CC session.

## Evidence that mattered
Three independent signals pointed at project-scope as the intended location before any code was written: `.gitignore:105` already listed `.claude/.superclaude_hooks/` (unused, so sediment from an earlier intent); uninstall step 5a's comment describes cleaning "hook runtime state files" but only reaches `base_path`; `install_components.py:307` already states `$CLAUDE_PROJECT_DIR` is the official project-root anchor.

Behavioral proof came from running the installed loader with CWD in a subdirectory (`src/superclaude/`): the skills banner went 9 → 22 skills and the token estimate 55612 → 94011 after the `get_skill_directories()` fix. That third instance was initially reported as out-of-scope and the user overrode — see the `feedback-same-root-cause-bundling` auto-memory.

## Shipped
Commit `52b5517` on master, pushed. 12 files, +252/-27. Branch `fix/hook-state-scope` created, ff-merged, deleted. `make sync-local` + `make deploy` done; deployed CLI verified to list `.superclaude_hooks` in `uninstall --scope local --dry-run`.

Tests 2062 → 2075 (13 new in `tests/unit/test_scope_paths.py`, including subdirectory regression cases). Baseline strings updated in CLAUDE.md, AGENTS.md, README.md.

## Open
`install_inventory.py:104` — `installed_count` for `skills`/`templates` counts every subdirectory of the shared target dir, so foreign skills inflate it and `--list-all` shows ⬜ `[13/5]` on a correct install. Same latent defect for `agents`/`commands`. Cosmetic; not fixed.

Proposed but not applied: a `.claude/rules/gotchas/` entry capturing the `Path.cwd()`-in-hooks trap (R19 capture).

## Next session
Hooks in the session that made the change were still running the pre-fix code — a Claude Code restart is required before the new resolvers take effect in a live session.
