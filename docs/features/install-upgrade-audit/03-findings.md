---
feature: install-upgrade-audit
phase: triage
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 03. Findings (P4 triage)

Matrix evidence: [02](./02-scenarios.md), [02a](./02a-scenarios-edge.md). Code-review coverage by axis: [03a-findings-review.md](./03a-findings-review.md). Every `file:line` was re-read on `master` @ 1dd9622c before filing.

- **Severity** (plan §4). S1: data lost, hooks blocking, another scope written, or uninstall half-done. S2: false health or a wrong end state. S3: cosmetic or doc.
- **Repro**: `harness/run-matrix.sh <ID>` in the audit scratch dir (sandbox only; [02 §1](./02-scenarios.md)).
- **Q**: the owner decision the fix follows ([00-intent.md](./00-intent.md)).
- **Order**: Q5 fixes S1 and S2 this round and sends S3 to the backlog. For each fix, write the regression test first, on the fixtures and builder in `tests/unit/test_install_upgrade_scenarios.py`, and watch it fail.

## Confirmed

| ID | Sev | Axis | Defect | Where | Repro | Q |
|---|---|---|---|---|---|---|
| C-01 | S1 | A3 A6 | uninstall deletes all content, then crashes on a UTF-16 or cp949 settings file: 14 hooks stay registered and CLAUDE.md keeps an import of a deleted file (T6) | install_inventory.py:298-443 run before :480 → install_settings.py:476 → :57-61 (catches only `JSONDecodeError`/`IOError`) | `E6` (`E6-user-utf-16-uninstall`) | Q16 a |
| C-02 | S1 | A3 A5 | uninstall over a malformed or UTF-8-BOM settings file says "✅ No hooks", exits 0, keeps every hook and deletes all content (T5) | install_settings.py:476-479 (`_load_settings` → `{}`) | `E1` (`E1-user-uninstall`), `E6` (`*-utf-8-sig-uninstall`) | Q16 a |
| C-04 | S1 | A4 | `update` with no `--scope`, run at a local-only install, creates a full user install in `~/.claude` (T4) | main.py:385 (`default="user"`), :408-413 | `X1` | Q4 a |
| C-05 | S1 | A4 | verify-drift's remediation `Run 'superclaude install --force'` has no `--scope`; followed verbatim from a local project, it writes a user install | main.py:559 | `X2` | Q4 a |
| C-06 | S1 | A1 A4 | a project install from the `memory: user` era (`d174e600` 2026-02-06 → `df5b8a35` 2026-02-24) can never be upgraded: install and `update` refuse, and the advice is `Install with --scope user, or run 'superclaude uninstall --scope user' first`. Followed, that writes or uninstalls the user scope and leaves the project untouched | install_components.py:103-104 (`user` never gated), :125-130 | `U11` (`U11-d174e600-project`) | **owner checkpoint** |
| C-07 | S1 | A2 | uninstall deletes user text: any line containing `@superclaude/` or `@.claude/superclaude/` loses everything from that point to the end of the line | install_settings.py:648-650 (unanchored) | P3a: `Our wiki lives at docs@superclaude/wiki and stays.` → `Our wiki lives at docs` | none needed |
| C-13 | S1 | A2 | `uninstall --remove-mcp` removes a user's own server that shares a registry name (`playwright` with the user's own command) at every scope; README:158 says user servers are preserved | install_mcp.py:601-637 (name match only), :216-226 | `I3` | Q12 a |
| C-03 | S2 | A6 A3 | No input preflight. With a malformed, BOM, UTF-16, cp949 or non-object settings file, or a non-UTF-8 CLAUDE file: install and `update` write all content before failing (exit 1, partial install, or a traceback at install_settings.py:77 / :597); doctor tracebacks; `uninstall --dry-run` tracebacks (T3) | install_settings.py:65-84, 596-597; doctor.py:162-171; install_inventory.py:497 | `E1`, `E3`, `E6`, P3b | Q16 a |
| C-08 | S2 | A1 A3 | retired agents `pm-agent.md`, `deep-research-agent.md` and the 11 `b933fd65` process skills survive install and uninstall; `using-superclaude` ("Loaded at session start") stays active after uninstall (R1) | install_paths.py:224-235 | `U8`, `U6` (`U6-19091b37`) | Q10 a |
| C-09 | S2 | A1 A3 | retired hook registrations kept by a non-force install: `Setup session_init`, `skill_activator`, `insight_writer pending-count`, the jq destructive blocker (in a committed project file too). The unmarked `[experimental]` echoes survive `--force`, `update` and uninstall. Legacy ones keep running `superclaude/scripts/` copies; with those gone they exit 2, which blocks `UserPromptSubmit` | install_settings.py:239-297, 333-340, 404-417; utils/__init__.py:304-319 | `U6`, `U8`, `U11`, `D1-scripts-gone` | Q13 a |
| C-10 | S2 | A5 | doctor says "healthy" with 76 drifted files (T1), with deleted commands, agents and modes, and with obsolete registrations whose scripts are gone. `--list-all` puts ✅ on a hooks row that names obsolete entries. A non-force upgrade from before v4.20.1 keeps `memory: project` on every old agent, so agent memory still lands in every project | doctor.py:67-80; main.py:191-195; install_components.py:212-214 | `U2`, `U9`, `D1` | Q3 a |
| C-11 | S2 | A5 | verify-drift marks the user's own agents and styles EXTRA, exit 1 forever (T1), yet does not see stale SC skill dirs | verify_drift.py:94-96, 129-145 | `U1`, `U3`, `U8` | Q9 a |
| C-12 | S2 | A3 | uninstall leaves SC-made state: an empty `agent-memory/`; a `~/.claude/CLAUDE.md` holding only `# Claude Code Configuration`; a `{}` `settings.json` the install created. A non-empty `agent-memory-local/` loses its exclude with no warning (T1, T2) | install_inventory.py:257-602 (no memory step); install_settings.py:504-525, 659-668 | `I2-user-noC`, `U4`, `I4` | Q11 b |
| C-14 | S2 | A6 | `uninstall --remove-mcp` with no `claude` on PATH tracebacks (`FileNotFoundError`) after deleting everything else, and never prints its summary | install_mcp.py:295-307 (catches `SubprocessError` only), :102-122 | `I3` (`I3-noclaude`) | none (A6) |
| C-15 | S2 | A4 A5 | with `CLAUDE_CONFIG_DIR` set elsewhere, install writes `~/.claude` and neither install nor doctor says so | install_paths.py:105-108; doctor.py:50-80 | `X7` | Q15 b |
| C-18 | S2 | A4 | a project install in a sibling worktree replaces the clone's local block; the worktree's local install becomes visible to git, and the only output is "refreshed with SC project block" | install_git_exclude.py:302-319 (documented at :36-41, never reported) | `X6` | none (report) |
| C-19 | S2 | A6 A5 | a non-UTF-8 `.git/info/exclude` crashes local install at its last step; doctor then says healthy while nothing is excluded (also any interruption at that step) | install_git_exclude.py:306 (catches `OSError` only); doctor.py:67-73 (no exclude check) | `E3-exclude`, `I4` | Q16 a |
| C-16 | S3 | A1 | the one-day `19091b37` era: `python .claude/hooks/x.py` is not recognised. `update` adds console `session_init` beside it (runs twice); uninstall leaves 3 commands and `hooks/*.py`; no note | utils/__init__.py:251-283 | `U6` (`U6-19091b37`) | Q14 b |
| C-17 | S3 | A3 A4 | local and project hook state from `bd356afa` → `52b5517e` sits in `~/.claude/.superclaude_hooks/`; a local or project uninstall neither reaches nor reports it | install_inventory.py:427-443 | `U4` | Q11 b (report) |
| C-20 | S3 | A2 A6 | CLAUDE file normalised: install and uninstall convert a CRLF file to LF (whole file); uninstall collapses blank-line runs and strips leading and trailing whitespace | install_settings.py:597-604, 640-670 | `E4`, `I2`, `U10` | none (A2) |
| C-21 | S3 | A2 A6 | every settings write (atomic temp file) leaves mode 0600, re-serialises the user's formatting with no trailing newline, and replaces a 0444 file with exit 0 | utils/__init__.py:97-104 | `E2-ro-settings`, `I2` | none |

## Regression test to write first (P5)

| ID | Red test |
|---|---|
| C-01 | install at U/P/L in `tmp_path`, re-encode settings as UTF-16 and cp949; `uninstall_all` returns `(False, msg naming the encoding)`, and `superclaude/`, `commands/sc/`, the hooks and the CLAUDE import are all still present |
| C-02 | same with a trailing comma and with a BOM: no `✅ No hooks`, success is False, nothing deleted |
| C-04 | CliRunner: local install, then `update` with no `--scope` → exit 1, output names the local install, `Path.home()/.claude` does not exist |
| C-05 | after any verify-drift output with drift, the remediation line contains `--scope <resolved scope>`; at local scope it is never a bare `install --force` |
| C-06 | `d174e600-project` fixture → `install_all(scope="project")`: the message never names `--scope user`; the owner's chosen option decides pass or refuse |
| C-07 | CLAUDE.md with `docs@superclaude/wiki` mid-line and a user line `see @.claude/superclaude/x` → `remove_claude_md_import` keeps both lines byte-identical and strips only the SC block |
| C-13 | stub `claude` on PATH, user `playwright` with a foreign command in `~/.claude.json`, `.mcp.json`, `projects[root]` → `uninstall_mcp_servers` issues no `remove` for it |
| C-03 | each bad input × `install_all`, `update`, doctor, `uninstall --dry-run`: no exception, exit 1, the tree's snapshot unchanged |
| C-08 | `b933fd65p-user` fixture → install then uninstall: none of the history's retired agent or skill names left; `my-skill/` kept. Plus the Q10 guard: every `shipped_now: false` name in `shipped_names_history.json` is on a retired list |
| C-09 | `66b37a7ep-user`, `d174e600-user`, `77b5821c-project` fixtures → non-force install: no `Setup`, `TeammateIdle`, `TaskCompleted`, `skill_activator`, `pending-count` or jq-blocker registration; the echoes are removed by exact command; `superclaude/scripts/` untouched. Plus the Q10 guard over `hook_ids` and `hook_events` |
| C-10 | `v4.20.1-user` fixture → install → `run_doctor`: passes with an advisory naming the drift count and `update --scope user`; a deleted command reads as an advisory or a failure, never as silent health |
| C-11 | a user agent and style next to a clean install → verify-drift clean (exit 0); a retired SC skill dir → reported `RETIRED`, exit 1 |
| C-12 | fresh U install → uninstall: no `agent-memory/` if empty, no SC-heading-only `CLAUDE.md`, no `{}` settings the install created; a non-empty `agent-memory-local/` → warning line |
| C-14 | PATH without `claude` → `uninstall_mcp_servers` reports a failure, raises nothing |
| C-15 | `CLAUDE_CONFIG_DIR` set to another dir → install output and doctor details name both paths |
| C-18 | worktree fixture (with `commondir`, `git-common-dir-paths`): local in the worktree, project in main → the second install warns that it replaces the local block |
| C-19 | cp949 bytes in `info/exclude` → `add_git_exclude` returns `(False, msg)`, no traceback; doctor fails while the block is missing at local scope |

## P5 status

Tests are in `tests/unit/test_install_upgrade_scenarios.py`; each was seen red before its fix.

| ID | Status | Regression test |
|---|---|---|
| C-01 | fixed (P5 group 1) | `test_c01_uninstall_refuses_undecodable_settings_before_deleting` |
| C-02 | fixed (P5 group 1) | `test_c02_uninstall_refuses_malformed_or_bom_settings` |
| C-03 | fixed (P5 group 1) | `test_c03_bad_input_refused_before_any_write` |
| C-19 | fixed (P5 group 1) | `test_c19_undecodable_exclude_refused_before_any_write`, `test_c19_add_git_exclude_reports_undecodable_exclude`, `test_c19_doctor_fails_while_local_exclude_block_missing` |
| C-07 | fixed (P5 group 1) | `test_c07_import_removal_keeps_user_lines` |
| C-13 | fixed (P5 group 1) | `test_c13_remove_mcp_keeps_a_foreign_server_of_the_same_name` |
| C-14 | fixed (P5 group 1) | `test_c14_remove_mcp_without_claude_reports_a_failure`, `test_c14_uninstall_remove_mcp_without_claude_deletes_nothing` |
| C-04 | fixed (P5 group 2) | `test_c04_update_refuses_a_scope_with_no_install`, `test_c04_update_from_a_subdirectory_names_the_install_above`, `test_c04_install_force_creating_a_scope_warns` |
| C-05 | fixed (P5 group 2) | `test_c05_drift_remediation_carries_the_scope`, `test_c05_every_command_install_prints_carries_the_scope` |
| C-06 | fixed (P5 group 2), ruling (b): non-force install refuses and advises `update --scope <this>`, which proceeds | `test_c06_memory_user_era_project_install_advises_update_in_scope`, `test_c06_update_rewrites_era_agents_to_the_project_store`, `test_c06_conflict_advice_never_names_another_base` |
| C-15 | fixed (P5 group 2), warning only at user scope | `test_c15_install_and_doctor_name_a_differing_config_dir`, `test_c15_no_warning_when_config_dir_is_the_default` |
| C-18 | fixed (P5 group 2), reported, not prevented | `test_c18_project_install_reports_replacing_a_worktree_local_block` |

## Owner checkpoint

**C-06 needs a decision not covered by Q1–Q16.** `find_agent_memory_conflict` gates `memory: project` on git tracking, so legacy user and local installs can upgrade (install_components.py:84-88). It does not gate `memory: user`, which every agent shipped from `d174e600` to `df5b8a35`, so a project install from that era is refused for good, and the advice names another scope.

- (a) Treat a uniform era `memory: user` at project scope like legacy `memory: project`: a non-force install proceeds (skip keeps the value); `update` rewrites it to the scope and says where agent memory moves from (`~/.claude/agent-memory/`) and to (`./.claude/agent-memory/`).
- (b) Keep refusing, but print advice that stays in this scope: `superclaude update --scope project` rewrites `memory:` and moves agent memory into the project. Make it a rule that conflict advice never names a scope whose base is not this one.
- (c) Status quo.

**Recommended: (b).** The refusal is the guard doing its job: where a team's agent memory lives is the team's call. The defect is advice that sends the user to another scope.

**Ruled (b)** ([00-intent.md](./00-intent.md)); fixed in P5 group 2. For the advice to work, a forced install (`update`) passes the guard when every foreign value names a store outside this install, and states the move.

## Not reproduced, or holds as designed

| Plan item | Outcome |
|---|---|
| T1 v4.20.1 stale + healthy; EXTRA; empty `agent-memory/` | reproduced → C-10, C-11, C-12 |
| T2 `19575ac4^` local: rewrite, `scripts/` notice, healthy with stale, exclude dropped | reproduced; the rewrite and the notice are correct (U4 hooks exact) → C-10, C-12 |
| T3 cp949 CLAUDE.md traceback at install_settings.py:597 after content and hooks | reproduced → C-03 |
| T4 local only + `update` | reproduced → C-04 |
| T5 trailing comma: "No hooks", 14 hooks remain | reproduced → C-02 |
| T6 UTF-16: doctor, update, uninstall traceback; uninstall deletes first | reproduced (cp949 too) → C-01, C-03 |
| R1 `b933fd65^` skills, agents, jq blocker | reproduced → C-08, C-09 |
| X3 doubled handler across `settings.json` + `settings.local.json` | not reproduced: identical commands, which Claude Code runs once; a committed project refuses local |
| X4, X5, U5, U7, E5, D1-duplicate, E2 (file, dir, base) | hold |
| I1 idempotency | holds; `hooks.json` rewritten by design, second `--force` rewrites identical bytes |
| I4 convergence | every interrupted install or uninstall converges on re-run; only C-12 and C-19 remain |
| U10 v4.1.9 "deletes nothing foreign" | holds (only C-20 whitespace) |
| c8e64bac-era `hooks/hooks.json` | handled: overwritten, then removed |
| U9 conflict guard on `ec6fa7e2^` user and local | holds as documented; the silent memory move is in C-10 |

Out of scope by Q1 (a), backlog: upstream E0 root files and CLAUDE block ([01 §3](./01-inventory.md)); MCP servers dropped from the registry that `--remove-mcp` cannot reach.
