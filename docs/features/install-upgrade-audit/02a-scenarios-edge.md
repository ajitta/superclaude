---
feature: install-upgrade-audit
phase: matrix
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 02a. Scenario matrix, run 1 — scope, idempotency, detection, robustness

Second part of [02-scenarios.md](./02-scenarios.md): same harness, same columns. "fresh" means no old install; the current CLI installs first.

## X — scope isolation

| ID | Setup | Sequence | Expected (source) | Observed | Result |
|---|---|---|---|---|---|
| X1 | fresh local install | `update` (no `--scope`) | refuse, exit 1, name the local install; `~/.claude` untouched (Q4 a; `sync-scope-creates`) | "Updating … (scope: user)", exit 0, 100 files created in `~/.claude` (main.py:385, 408-413) | FAIL |
| X2 | local install; `commands/sc/analyze.md` edited; later its hooks dropped | `verify-drift` → run its remediation verbatim from the project; `doctor --verbose` → run its remediation | remediations stay local, carry `--scope` (Q4 a) | verify-drift prints `Run 'superclaude install --force' to re-sync` (main.py:559); followed, it creates a 100-file user install. Doctor's `run 'superclaude install --scope local' from <root>` (doctor.py:45-47) repairs the local install, `~/.claude` untouched | FAIL |
| X3 | project then local; same, project committed first; local then project | two installs | committed project refuses local (install_components.py:122-124); no doubled handler | uncommitted: both proceed by design (install_components.py:84-88), 14 identical commands in both files (Claude Code runs an identical handler once); committed: refused with "use --scope project"; local first: project refused (`memory: local`) | PASS ×3 |
| X4 | user install + C | `install`, `update`, `uninstall -y` at project | `~/.claude` byte-identical | identical | PASS |
| X5 | local install at `$HOME` | `doctor`, `verify-drift`, `--list-all`, `uninstall --scope local -y` from `$HOME` | all say `scope: local` (utils/__init__.py:377-379); uninstall removes it | as expected | PASS |
| X6 | main repo + linked worktree; local install in the worktree | `check-ignore` in the worktree; project install in main | block in the common dir, effective; replacement reported (install_git_exclude.py:36-41; plan X6) | block effective; the project install prints only "refreshed with SC project block", and the worktree's local content is no longer ignored (`check-ignore` exit 1) | FAIL |
| X7 | `CLAUDE_CONFIG_DIR=$SB/cc` | `install`, `doctor --verbose`, `uninstall -y` at user | both warn naming both paths; `$SB/cc` untouched (Q15 b) | no warning anywhere; `$SB/cc` untouched; install went to `$HOME/.claude` | FAIL |

## I — idempotency, uninstall completeness, MCP, interruption

| ID | Setup | Sequence | Expected (source) | Observed | Result |
|---|---|---|---|---|---|
| I1 | fresh, each scope | install ×2, `--force` ×2; ctime marks between runs | content identical each time; settings not rewritten when unchanged (install_settings.py:434-441) | identical. Second install rewrites only `hooks/hooks.json` (by design, install_components.py:365-369); second `--force` rewrites 98 files with the same bytes (copy2 keeps mtime), never the settings file | PASS ×3 |
| I2 | fresh + C, each scope | `install`, `seed post`, `uninstall -y`; diff against the pre-install snapshot | equal except memory file and insights (README:158; Q11 b) | the CLAUDE file differs (blank-line run collapsed; C-20); settings is semantically equal but re-serialised, with no trailing newline (C-21) | FAIL ×3 |
| I2-user-noC | fresh, no C | `install`, `uninstall -y` | nothing SC-made left (Q11 b) | `CLAUDE.md` holding only `# Claude Code Configuration`, empty `agent-memory/`, `settings.json` = `{}` | FAIL |
| I3 | install; the user's own `playwright` (`my-own-playwright --mine`) at each scope's MCP file | `uninstall -y --remove-mcp` | the user's server kept (Q12 a; README:158) | stub log: `claude mcp remove --scope <s> playwright` at user, project and local (install_mcp.py:601-637 matches by name) | FAIL ×3 |
| I3-noclaude | user install; stub `claude` removed | `uninstall -y --remove-mcp` | no traceback | `FileNotFoundError: 'claude'` from install_mcp.py:296 → :122. Everything else was already deleted and the summary never printed | FAIL |
| I4 | fresh, user and local; `i4.py` makes each step raise | interrupted run → `doctor` → re-run → `uninstall` | doctor never healthy mid-way; re-run reaches the clean-install tree; uninstall leaves nothing SC-made (plan I4) | every re-run converges (tree equals a clean install); uninstall re-runs complete. Doctor is healthy only after a local install interrupted at `add_git_exclude`, with nothing excluded (C-19). At user scope every uninstall leaves `CLAUDE.md` + `{}` settings (C-12) | FAIL |

## D — detection

| ID | Setup | Expected (source) | Observed | Result |
|---|---|---|---|---|
| D1-stale | v4.20.1 → `install` | doctor advisory (Q3 a); verify-drift reports it | doctor healthy; verify-drift 76 drifted, exit 1; every `--list-all` row ✅ | FAIL |
| D1-deleted | current install; `commands/sc/analyze.md`, one agent, `superclaude/modes/` deleted | doctor reports (Q3 a) | doctor healthy; verify-drift MISSING; `--list-all` ⬜ rows | FAIL |
| D1-scripts-gone | `66b37a7e^` → `install`; then `superclaude/scripts/` deleted (contrary to the ℹ️ notice) | doctor flags it (plan D1) | 2 legacy commands left (`skill_activator`, `Setup session_init`); with `python` on PATH, `echo '{}' \| <command>` exits **2** (`UserPromptSubmit` exit 2 blocks the prompt); doctor healthy; `--list-all` "Hooks [14/14] └─ 2 obsolete" with a ✅ icon (main.py:191-195) | FAIL |
| D1-duplicate | a second `~/.local/bin/superclaude hook loop_guard` on `PostToolUse` | `--list-all` reports it (install_inventory.py:83-114) | "1 duplicate" | PASS |

## E — robustness

| ID | Input | Sequence | Expected (source) | Observed | Result |
|---|---|---|---|---|---|
| E1 | settings with a trailing comma, each scope | `install` | refused before any write (Q16 a; plan E1) | settings untouched, but 100 files written: "82 installed, 1 failed", exit 1 | FAIL ×3 |
| E1-uninstall | installed scope, then a trailing comma | `uninstall -y` | no success claim while hooks remain (plan E1, T5) | "✅ No hooks in settings.json", exit 0; all 14 hooks kept; all content deleted (install_settings.py:476-479) | FAIL ×3 |
| E2 | user install, then edits; `analyze.md` 0444 / `agents/` 0555 / `~/.claude` 0555 | `update` | failure counted, exit 1, no half-written file | exit 1, each failure listed; no partial file | PASS ×3 |
| E2-ro-settings | `settings.json` 0444 | `update` | failure counted (plan E2) | exit 0; file replaced through `os.replace`, now mode 0600 (utils/__init__.py:97-104). Every settings write leaves 0600 | FAIL |
| E3 | `CLAUDE.md` (U) / `CLAUDE.local.md` (L) in cp949 or UTF-16 | `install`, `uninstall --dry-run` | no traceback, file untouched (plan E3; Q16 a) | file untouched; traceback at install_settings.py:597 after 100 files and the hooks were written; `--dry-run` traceback at install_inventory.py:497 | FAIL ×4 |
| E3-exclude | a cp949 comment in `.git/info/exclude`, L | `install`, `doctor` | no traceback; doctor not healthy | traceback at install_git_exclude.py:306 (last step); doctor healthy; `git status` lists `.claude/` and `CLAUDE.local.md` | FAIL |
| E4 | CRLF CLAUDE file, each scope | `install`, `doctor`, `uninstall -y` | line endings kept; no orphan heading; bytes restored (README:158) | whole file converted to LF on install (install_settings.py:597-604); no orphan `# superclaude\r`; after uninstall the LF version remains | FAIL ×3 |
| E5 | synthetic `C:\…\python.exe C:\…\.claude\superclaude\scripts\session_init.py` and quoted `"C:\…\superclaude.exe" hook loop_guard`, U | `install`, `uninstall -y` | legacy rewritten; pinned kept, not doubled; uninstall removes both (utils/__init__.py:257-301) | as expected | PASS |
| E6 | `settings(.local).json` in UTF-16, UTF-8-BOM, cp949 (with a non-ASCII value), each scope | each of `install`, `update`, `uninstall -y`, `doctor` on a fresh copy | no traceback; exit 1; nothing written or deleted (Q16 a) | **UTF-16, cp949**: traceback in all four (install/update install_settings.py:77, doctor doctor.py:163, uninstall install_settings.py:59). Install writes 100 files first; uninstall deletes 98 files first, leaving 14 hooks and a dangling import. **BOM**: install partial, exit 1; uninstall exit 0, "No hooks", hooks kept, content deleted; `update` and `doctor` refuse cleanly (here content was already current, so no bytes changed) | 6 PASS / 30 FAIL |

Extra code-read repros, run in the same harness (`P3a`, `P3b`):

- A user `CLAUDE.md` line `Our wiki lives at docs@superclaude/wiki and stays.` reads `Our wiki lives at docs` after install plus uninstall (C-07).
- `settings.json` = `[]` makes doctor raise `AttributeError` (doctor.py:171).
