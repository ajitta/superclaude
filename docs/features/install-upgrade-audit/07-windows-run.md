---
feature: install-upgrade-audit
phase: verify
created: 2026-10-19
revised: 2026-10-19
---

# 07. Windows run (P8): the PowerShell script and W1–W7

The P8 checks from [04a-handoff §1b–§1c](./04a-handoff.md) were run on a Windows 11 machine at master f8a2cc5a (v4.30.4). Every step that installs ran in a sandbox (`USERPROFILE`, `HOME` and `CLAUDE_CONFIG_DIR` pointed into scratch) or in a scratch project. The script's guard reported the real `~\.claude` unchanged after both runs. One product defect came out of it: W-3, where `.git/info/exclude` is rewritten with CRLF line endings. The script also had one bug of its own, S-1, which is fixed on this branch.

Environment: Windows PowerShell 5.1.26100.9711 and PowerShell 7.6.7, git 2.53.0.windows.3, uv 0.12.17, Python 3.13.7, Claude Code 2.1.303.

## 1. The PowerShell script (§1b)

| Run | PASS | FAIL | FAIL rows |
|---|---|---|---|
| PowerShell 5.1, full | 70 | 6 | U4 C-17 (S3, expected); I2 ×5 |
| PowerShell 7, full | 70 | 6 | same rows |
| Both shells, `-Only I2` after the S-1 fix | 11 of 15 | 4 | I2-project and I2-local: `.git\info\exclude` only (W-3) |

The two full runs differ only in the sandbox paths and the W6 `Out-File` row. U1 (v4.29.5 → current, all three scopes), U4 apart from C-17, and E6 (UTF-16, UTF-8 BOM and cp949 settings × U/P/L × install, update, uninstall, doctor: 36 records, each exit 1 with nothing changed and no traceback) all pass in both shells.

**After the fixes (§4), `-Only I2,E6` on `fix/windows-file-fidelity`:** 51 of 51 PASS in both 5.1 and 7, with the guard reporting the real profile unchanged. I2's `info/exclude` rows now pass, and E6's `utf-8-bom` rows now expect, and get, exit 0 with the BOM kept.

**S-1 (script bug, fixed here).** `Set-Customizations` seeded `settings.json` with `hooks` written inline on one line, inside an otherwise indented file. C-21 re-serialises that shape by design (a recorded residual, [03-findings](./03-findings.md) C-21 row), so the I2 byte check failed because of the seed and not because of anything superclaude did. The seed is now fully indented. With the indented seed, settings bytes come back identical at all three scopes on Windows, so the C-21 fix holds there.

## 2. W-3: install rewrites `.git/info/exclude` with CRLF on Windows

| | |
|---|---|
| Severity | S2. A Windows-only file-fidelity defect of the C-20 class. The patterns still match, but every line of the file changes |
| Repro | `git init` writes `info/exclude` with LF. `superclaude install --scope local` (or project) followed by `uninstall` leaves the same text with CRLF on every line. Seen in I2-project and I2-local in both shells and reproduced with a Python driver. User scope writes no exclude block and is unaffected |
| Cause | `install_git_exclude.py` reads with `read_text` (universal newlines turn CRLF into LF) and writes with `write_text`, which translates every `\n` into `os.linesep`. The three sites are `add_git_exclude` :356, `remove_git_exclude` :416 and `_migrate_legacy_gitignore` :302. The last one rewrites a team's committed `.gitignore`, so on Windows a migration would show every line as changed in `git diff` |
| Fix shape | The C-20 approach: read the bytes, keep the file's majority line ending (`_line_ending`), add and remove only the block lines in that ending, and write the bytes back. Red-first test: an LF exclude file survives install and uninstall byte for byte, and a CRLF file stays CRLF. The test needs no Windows runner if it asserts on `write_bytes` input, or it can run in the dispatch-only `windows-scenarios` job |
| Siblings checked | Settings writes go through `atomic_write_text(newline="")`, which is fine. CLAUDE files use `write_bytes` after C-20, which is fine. A newly created CLAUDE file (`install_settings.py:880`) and the rewritten agent files (`install_components.py:373`) are written with CRLF on Windows. Both are files superclaude creates whole, verify-drift passes on them, and no user bytes are changed, so neither is a finding |

## 3. W1–W7 (§1c)

| W | Method used | Result | Verdict |
|---|---|---|---|
| W1 | Scratch project with a local install. A headless `claude -p` (haiku) ran `sleep 40` through Bash while `superclaude update --scope local` ran three times from another process | All three updates exited 0 with no `PermissionError` or `WinError`; the Claude Code session stayed alive and exited 0 | No finding |
| W2 | `attrib +r .claude\commands\sc\analyze.md`, then `uninstall --scope local -y` | `❌ Failed to remove …\commands\sc/: [WinError 5]`, then `Summary: 8 removed, 2 skipped, 1 failed`, exit 1, no traceback; the rest of the uninstall completed | No finding (a counted failure with exit 1) |
| W3 | `doctor`, `doctor --scope local` and `verify-drift --scope local` run from cwd strings in the original case, all lowercase, a lowercase drive letter only, all uppercase, and a lowercase subdirectory (`subprocess` `cwd=`, so the process keeps the typed case) | Every variant names the same install and the local scope, reports healthy and finds no drift. Uninstall from the lowercase cwd removed everything | No finding |
| W4 | Proxy for a GUI launch: `PATH` rebuilt from only the registry Machine and User values, which is what an Explorer-started process gets, then headless `claude -p` in the W1 project | `superclaude.exe` resolves to `~\.local\bin` from the registry PATH. The session reported `SessionStart:startup hook success: 🛠️ superclaude: 35 commands, 24 agents (local scope)` and the core context line | No finding. A real Start-menu launch was not done; the registry PATH is the variable the gotcha names |
| W5 | Fresh clone, `uv venv` and `uv pip install -e ".[dev]"`, then `make sync-local` twice | Both exited 0 (83 installed), doctor reported healthy, and no `.venv\lib64` was ever present | Not reproduced. The gotcha's trigger is a `lib64` symlink, which a Windows-native venv does not create (it came from a Linux/WSL-made `.venv`). Keep `windows-make-sync-broken`, narrowed to that trigger |
| W6 | Script rows for PowerShell's default encodings, plus headless `claude -p` in two scratch projects whose `.claude\settings.local.json` registers a `SessionStart` hook that writes a marker file: one file with a UTF-8 BOM, one without (control) | 5.1: `Out-File` writes `FF FE` (UTF-16LE), `Set-Content` writes ANSI with no BOM. 7: both write UTF-8 with no BOM. Claude Code ran the hook from the BOM file (marker written, exit 0), the same as the control | **Claude Code accepts a UTF-8 BOM settings file.** Q16's precondition for relaxing reads to `utf-8-sig` is met (§4). The plan asked for a status line; that needs an interactive session, so a hook was used as the observable, and both come from the same settings file |
| W7 | `CLAUDE_CONFIG_DIR` set to a scratch dir holding `settings.json` (a `SessionStart` hook marker) and `CLAUDE.md` (a marker sentence); headless `claude -p --debug`, then one haiku session with the login copied into that dir for the run and deleted right after | The hook from the variable's `settings.json` ran. The debug log loads user skills, agents, commands and output-styles from the variable's dir and watches its `settings.json`; Claude Code wrote `.claude.json`, `projects/`, `sessions/` and `debug/` there. The logged-in session quoted the marker sentence from the variable's `CLAUDE.md` | Claude Code reads user settings, components **and user `CLAUDE.md`** from `$CLAUDE_CONFIG_DIR`, as the docs say for settings ("All settings, session history, and plugins are stored under this path", code.claude.com/docs/en/env-vars) |

Claude Code sessions used: 5 headless haiku runs (W6 ×2, W1, W4, W7). The W7 debug run stopped at login before any API call.

## 4. What this decides

Owner decisions (2026-10-19): fix W-3 now; finish W7 with a temporary login copy; relax the BOM refusal for settings and CLAUDE files; narrow the gotcha.

- **[Remaining work](../../plans/remaining-work-ajitta-2026-10-19.md) §3, BOM: done** (branch `fix/windows-file-fidelity`). Settings and CLAUDE files saved as UTF-8 with a BOM are edited in place and keep their BOM; doctor calls them healthy; scope detection reads them. UTF-16 and code-page files are still refused, and so is a BOM in `info/exclude` (04a §3). Tests: the `bom` layouts of `test_c20_install_appends_only_its_block_and_uninstall_removes_only_it` and `test_c21_settings_keep_their_layout_across_install_and_uninstall`, `test_w6_bom_settings_and_claude_file_are_accepted_by_every_command`, `test_w6_bom_in_exclude_is_still_refused`. The script's E6 `utf-8-bom` rows now expect exit 0 with the BOM kept.
- **§2, C-15: still open, now with its input.** W7 confirms that the variable relocates settings, components and user `CLAUDE.md`, which is the evidence the Q15 (a) ADR (`get_base_path` follows `CLAUDE_CONFIG_DIR`) was waiting for.
- **W-3: fixed** on the same branch (`_read_lines_lf` / `_write_lines` in `install_git_exclude.py`, for the exclude file and the `.gitignore` migration). A file mixing both line endings comes back in its majority ending. Tests: `test_w3_exclude_keeps_its_line_endings_across_install_and_uninstall` (project, local × LF, CRLF), `test_w3_legacy_gitignore_migration_touches_only_the_block`.
- **Gotcha `windows-make-sync-broken`: narrowed** to venvs that hold a `lib64` symlink (made by Linux/WSL uv).
