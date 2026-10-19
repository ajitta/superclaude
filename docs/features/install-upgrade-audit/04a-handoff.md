---
feature: install-upgrade-audit
phase: handoff
status: open
created: 2026-10-19
revised: 2026-10-19
---

# 04a. Owner handoff: Windows (P8), backlog, open decisions

P0–P6 ran on Linux. What only the owner can do (Windows), what the round leaves for later (S3), and the judgement calls the P5 groups made that the owner should confirm. Evidence: [04-matrix-run2.md](./04-matrix-run2.md); findings: [03-findings.md](./03-findings.md).

## 1. Windows (P8, about 45 min)

Do it on a branch checkout with a healthy `.venv` (`uv pip install -e ".[dev]"`; AGENTS.md Tests). Use a scratch project, never the real `~/.claude`, for every step that installs.

### 1a. The `workflow_dispatch` job, once (Q2 d)

The `windows-scenarios` job in `.github/workflows/test.yml` runs only `tests/unit/test_install_upgrade_scenarios.py` on `windows-latest`, Python 3.13. The module needs no network, no git history and no asyncio. The job runs only when dispatched with the input set; PRs and `make ci` never start it.

1. Commit and push the branch (P6 left `test.yml` uncommitted).
2. Run `gh workflow run Tests --ref fix/install-upgrade-audit -f windows=true`.
3. Run `gh run watch`.

The job lives in the existing Tests workflow, not a new file: `workflow_dispatch` reaches only workflows that are already on the default branch (`stable`), and the run uses the file from `--ref`.

**Pass:** the module is green. **A failure:** a Windows-only defect (locale encoding, path form, `os.replace`). File it in `03-findings.md` with the failing test name.

### 1b. The PowerShell script

`scripts/install-audit-windows.ps1` runs the matrix scenarios U1, U4, I2 and E6, plus a W6 probe, each in a sandbox under `%TEMP%`.

- **Isolation.** It points `USERPROFILE`, `HOME` and `CLAUDE_CONFIG_DIR` into the sandbox. It aborts unless Python's `Path.home()` resolves there, and it compares the real `~\.claude` (`settings.json` hash, SC artifacts, `~\.claude.json` `mcpServers`) before and after each scenario.
- **Network.** The U1 and U4 old releases (`v4.29.5`, `19575ac4^`) are built with `uvx --from <git archive>`, which needs network.
- **Run it** from the checkout, once in Windows PowerShell 5.1 and once in `pwsh` 7: `powershell -ExecutionPolicy Bypass -File scripts\install-audit-windows.ps1`. `-Only E6` runs one scenario.
- **Output.** `results.md` in the printed sandbox root; paste it back.
- **Expected.** Every row PASS, except the rows marked S3 (C-17 in U4, C-20/C-21 in I2), which are tolerated.
- **Untested.** It was written on Linux, and no `pwsh` was available, so it has never been run. A script error is a script bug, not a finding: report it with the line.

### 1c. W1–W7 (plan [05a](./05a-plan-matrix.md) §3)

| W | Question | How | Decides |
|---|---|---|---|
| W1 | Does `os.replace` fail while Claude Code holds `settings.json`? | Open Claude Code in a scratch project with a local install, and run `superclaude update --scope local` from another shell while it runs | exit 0 and no `PermissionError` → none; else a finding (settings writes, C-21 area) |
| W2 | Does `rmtree` fail on read-only files? | In the scratch install, `attrib +r .claude\commands\sc\analyze.md`, then `superclaude uninstall --scope local -y` | removed, or a counted failure with exit 1; a traceback is a finding |
| W3 | Does drive or letter case break `same_dir` / `find_install_root`? | `cd c:\work\proj` vs `cd C:\Work\Proj`, then `superclaude doctor` in each | both name the same install and scope |
| W4 | `.exe` shim and GUI-launched PATH | Start Claude Code from the Start menu, then `! where superclaude`; check that the SessionStart banner appears | doctor's PATH check is a proxy (gotcha `doctor-path-probe-is-proxy`); a missing banner is a finding |
| W5 | Is `make sync-*` os error 5 still there? | On a scratch checkout: `make sync-local`. If it fails, `superclaude doctor --scope local` then `superclaude install --force --scope local` | updates gotcha `windows-make-sync-broken` (still true, or retire it) |
| W6 | Does Claude Code accept a UTF-8-BOM `settings.json`? What does PowerShell write by default? | The script's W6 rows give the `Out-File` / `Set-Content` default (`FF FE` = UTF-16). Then save a scratch `.claude\settings.local.json` **with** a BOM holding `"statusLine": {"type": "command", "command": "echo W6-BOM"}` and start Claude Code there | status line shows `W6-BOM` → Claude Code accepts a BOM, so Q16 can relax to reading `utf-8-sig` (plan Q16: "BOM acceptance waits for W6"); not shown → keep the refusal |
| W7 | Which `CLAUDE.md` and `settings.json` does Claude Code read with `CLAUDE_CONFIG_DIR` set? | Set `CLAUDE_CONFIG_DIR` to a scratch dir holding a `CLAUDE.md` with a marker sentence and a `settings.json` status line, start Claude Code, and ask what its user memory says | reads the variable's dir → input for the Q15 (a) ADR (honour it in `get_base_path`); today's warning (Q15 b) stays correct either way |

## 2. S3 backlog (Q5 a)

The four remaining matrix FAILs ([04 §4](./04-matrix-run2.md)):

| ID | Defect | Matrix |
|---|---|---|
| C-16 | the `19091b37` `python .claude/hooks/x.py` era: install says nothing, `session_init` runs twice, uninstall leaves 3 commands and `hooks/*.py`. Q14 (b) is met by the CHANGELOG upgrade note; an install-time line naming the 3 commands would close it | U6-19091b37 |
| C-17 | local and project hook state from `bd356afa` → `52b5517e` in `~/.claude/.superclaude_hooks/` is neither reached nor reported by a local or project uninstall | U4 |
| C-20 | CLAUDE file normalised: CRLF → LF, blank-line runs collapsed, edges stripped (`remove_claude_md_import`) | U10, E4 ×3, I2 ×3 |
| C-21 | settings writes leave mode 0600, re-serialise the file with no trailing newline, and replace a 0444 file with exit 0 | E2-ro-settings, I2 ×3 |
| W-1 | **fixed** (branch `fix/retired-skill-user-files`, [03 P7 section](./03-findings.md)). Was: a retired skill dir whose `SKILL.md` matches a shipped revision is removed whole (`rmtree`), so a file the user added inside it goes too. Now only files whose path and text match a shipped revision go; the rest and every symlink stay, dirs go once empty | `test_w1_retired_skill_loses_only_the_files_superclaude_shipped`, `test_w1_a_symlink_inside_a_retired_skill_is_kept_and_never_followed`, `test_w1_a_symlinked_retired_skill_directory_is_left_alone`, `test_w1_uninstall_dry_run_says_what_stays_and_changes_nothing`, `test_w1_a_second_install_removes_and_reports_nothing`, `test_w1_verify_drift_and_doctor_follow_what_install_removes`, `test_w1_skill_md_is_removed_last`, `test_w1_retired_skill_files_module_is_generated_from_the_fixture` |

Out of scope by Q1 (a), unchanged: the upstream E0 root files and CLAUDE block ([01 §3](./01-inventory.md)); MCP servers dropped from the registry that `--remove-mcp` cannot reach.

## 3. Open items from P5 (owner to confirm or decide)

| Item | Now | Options |
|---|---|---|
| **BOM in `info/exclude`** (p5-g1) | Refused like a BOM in settings or CLAUDE files (one rule for every file SC edits), although git honours it: P6 confirmed `git check-ignore` matches a BOM'd pattern line, and install exits 1 naming the BOM | keep; or accept a BOM in `info/exclude` only (strip it on read, keep it on write). W6 does not decide this one; git's behaviour already did |
| **Non-UTF-8 user agents** (p5-g1) | **Closed in P6**: not reproduced at U/P/L. The memory scans read only shipped names and catch `UnicodeDecodeError` (install_components.py:139-143, :228-234) | — |
| **Older Tavily registrations** (p5-g1) | Under Q12 (a), `--remove-mcp` removes only a server whose command matches today's registry. Tavily servers registered by older releases (`npx -y mcp-remote https://mcp.tavily.com/mcp`, `npx -y tavily-mcp@0.1.2`) are kept; the CHANGELOG says how to remove them by hand | keep; or add a historical-command list per server (fits the backlog item "MCP servers dropped from the registry") |
| **C-06 `update` deviation** (p5-g2) | Ruling (b) said "keep refusing, advise `update --scope project`", but `update` ran the same guard, so the advice would loop. Now a non-force install still refuses, and `update` passes when every foreign `memory:` value names a store outside this base, printing where agent memory moves. That is option (a)'s `update` half | confirm; or change the advice; or give `update` its own flag |
| **C-18, other direction** (p5-g2) | A project install replacing a worktree's local block is reported. A local install replacing another worktree's project block is not: the local block is a superset, so it hides that worktree's *uncommitted* project content from `git status`. The warning also does not name which worktree holds the install | report the other direction too; naming the worktree needs `git worktree list` plus scope detection |
| **C-15 scope** (p5-g2) | The `CLAUDE_CONFIG_DIR` warning is given only at user scope, the only base the variable replaces, and only by install and doctor (Q15 b). `uninstall` does not warn, and user-scope MCP servers in `$CLAUDE_CONFIG_DIR/.claude.json` are not covered | extend to uninstall and the MCP reader; otherwise this waits for the W7 answer and the Q15 (a) ADR |

Smaller judgement calls, recorded in the P5 reports. Each is a one-line follow-up if the owner wants it:

- `finishing-a-development-branch`, the retired agents and `using-superclaude` are pruned by name only. The ten process-skill names that obra/superpowers also uses go only on a shipped SKILL.md digest.
- The four retired serena-hooks commands are matched by sha256 prefix, because `test_shipped_content_server_neutral.py` forbids the server name under `src/`.
- verify-drift names `install --force --scope <s>`, while install and doctor name `update --scope <s>`. Both act on the right scope.
- doctor now runs verify-drift on every call. Its cost on a large `skills/` tree has not been measured.
- doctor fails a BOM'd CLAUDE file, to agree with install's refusal. Revisit with W6.

## 4. After P8

P7 (the independent diff verifier) and P9 (release) follow [05-plan.md](./05-plan.md) §6. A Windows finding from §1 is fixed (S1/S2) or added to §2 (S3) before P9.
