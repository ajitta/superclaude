---
feature: install-upgrade-audit
status: implementing
revised: 2026-10-19
---

# Axis C plan v2 — §1–§3: inventory, axes, scenario matrix

Part of [05-plan.md](./05-plan.md) (plan v2, §1–§3).

## 1. Upgrade-path inventory

### 1a. Install methods (all reach `install_all`)

`uv tool install git+…@stable` + `install`/`update` (README:136-141); editable clone and `make deploy`; `make sync-*` (always `--force`; never here); the wizard (CWD-based); `install.sh` (venv-only console script); pipx (upstream era, `CONSOLE_SCRIPT_FIX` hint). Out of scope: the marketplace (socratic skills only). `superclaude mcp` is separate.

### 1b. What the current version writes

| Artifact | user (`~/.claude`) | project (committed) | local (personal) | Ownership / uninstall |
|---|---|---|---|---|
| `commands/sc/`, `superclaude/{CLAUDE_SC.md,core,modes,mcp,templates}` | ✓ | ✓ | ✓ | SC-only; `find_unshipped` prunes; uninstall rmtrees |
| `agents/` (`memory:` rewritten), `output-styles/`, `skills/sc-*` | ✓ | ✓ | ✓ | Shared; shipped names plus `RETIRED_AGENT_FILES` / `LEGACY_SKILL_NAMES` |
| `hooks/hooks.json`; hook merge | `settings.json` | `settings.json` | `settings.local.json` | Per inner hook; user hooks stay in place |
| CLAUDE import | `~/.claude/CLAUDE.md`, created with `# Claude Code Configuration` if absent [v2: P-7] | `./.claude/CLAUDE.md` | `./CLAUDE.local.md` | `# superclaude` block; uninstall strips it, keeps the file |
| Agent memory | `agent-memory/` | `agent-memory/` | `agent-memory-local/` | Never removed (T1, T2) |
| `.git/info/exclude` block | — | 2 runtime entries | full list | Marker-keyed |
| `hook_state_dir()/.superclaude_hooks/` | ✓ | ✓ | ✓ | Removed on uninstall |
| `insights.pending.jsonl` [v2: P-7] | every project's `.claude/` (insight_writer.py:64), never excluded | excluded | excluded | **Never removed** (no "pending" in install_inventory.py) |
| `insights.jsonl` | project `.claude` | ✓ | ✓ | User data, kept |
| MCP (`superclaude mcp`) | `~/.claude.json` | `./.mcp.json` | `~/.claude.json` `projects[root]` | `--remove-mcp` matches **by name** |

`get_base_path` returns `Path.home()/.claude` for user scope (install_paths.py:105-108) and ignores `CLAUDE_CONFIG_DIR`; only context_loader.py:997 reads it. Claude Code docs: with it set, "Claude Code then stores your settings, session history, and plugins there instead" (settings page, fetched 2026-10-19). Such a user gets an install Claude Code never reads, and doctor still says healthy [v2: P-7].

### 1c. What older versions wrote

v4.1.9 is the fork root and an ancestor; v4.2.0/v4.3.0 are not [v2: P-11]. Versions are `pyproject.toml` at that commit.

| Legacy artifact | Era | Current handling | Status |
|---|---|---|---|
| `python .claude/hooks/x.py` + copies in `<base>/hooks/` [v2: P-3] | 19091b37 (4.1.9), one day | Not recognised (`superclaude[/\\]scripts` regex, utils:272). `update` adds console `session_init` beside it (runs twice); uninstall leaves 3 commands + 6 files | Q14 |
| c8e64bac era ("native hooks.json auto-loading instead of settings.json merge") [v2: P-3] | 2026-01-02 → ? | P1 checks what it wrote | open |
| `python {{SCRIPTS_PATH}}/x.py`, `python3 …`, `{{PYTHON_BIN}} $CLAUDE_PROJECT_DIR/…/superclaude/scripts/x.py`, with the uvx archive interpreter baked in [v2: P-5] | → 77b5821c (4.4.1) → 19575ac4 | `_migrate_legacy_commands` | R1: 5 and 6 rewritten; T2 ✓ |
| `<base>/superclaude/scripts/` copies | until 19575ac4 | Kept with a notice (install_components.py:444-476) | T2 ✓ |
| **Retired events** `Setup` (→ 66b37a7e), `TeammateIdle`/`TaskCompleted` (→ d7fd7850) [v2: P-1] | 2026-02 | Only `--force` strips them (install_settings.py:404-417) | Q13 |
| **Unmarked `[experimental]` echo hooks** on those two events [v2: P-1] | d174e600 → d7fd7850 | No marker, no script path → `is_superclaude_hook` False (utils:304-319): survive `--force`, `update` **and** uninstall | Q13 |
| **Retired entry points** `skill_activator`, `skill` [v2: P-1] | → bd683233 | No shipped replacement → never rewritten (:333-340); non-force keeps them | Q13 |
| **Inline jq blocker** `… 'BLOCKED: destructive …' && exit 2` [v2: P-1] | 66b37a7e → 79032ccc | Identified, but non-force keeps it, also in a committed project settings.json | Q13 |
| Legacy skills (5) | 910eabdd | `LEGACY_SKILL_NAMES` | tested |
| **11 process skills**, written by the `skills` component (`b933fd65^:…/cli/install_paths.py:18`) and `install-skill` (`install_skill.py`, deleted 910eabdd) [v2: P-11] | → b933fd65 | **Not listed.** 9 of 11 lack `disable-model-invocation` [v2: P-5] | R1 ✓ |
| `pm-agent.md`, `deep-research-agent.md` | renamed 2026-03-18 | **Not in `RETIRED_AGENT_FILES`** | R1 ✓ |
| `deep-research.md`; unshipped commands, modes, MCP docs, core | — | Listed; `find_unshipped` | tested; T1 ✓ |
| `memory: project` at user/local | before v4.20.1 | `find_agent_memory_conflict` (reads content + git tracking) | tested |
| Local/project hook state in `~/.claude/.superclaude_hooks/` [v2: P-7] | bd356afa → 52b5517e | Unreachable by a local/project uninstall | U4 |
| `.gitignore` block, `(local scope)` marker | before b85651c0 | Migrated to `info/exclude` | unit-tested |
| Per-worktree `info/exclude`; `# SuperClaude Framework` heading | before f61dd8f9; before v4.27.2 | Not cleaned (dead file); stripped | note; T1 ✓ |
| Upstream v4.0.x `setup/` root-level `~/.claude/*.md` | 2025 | Nothing handles it | Q1 |
| Old-registry MCP servers; version stamp | ≤ v4.26.0; never | Kept by design; unknowable | note; Q3 |

**Must survive** (A2): non-`hooks` settings keys; user hooks (own or shared entries, order, matcher, timeout); unchanged formatting; user agents, styles, skills, commands; CLAUDE file text; non-SC exclude/`.gitignore` lines; agent memory; both insights files; user MCP servers (a user `playwright` too); pinned console commands.

## 2. Audit axes (six)

| # | Axis | Question | Candidates |
|---|---|---|---|
| A1 | Upgrade migration | Does old → new reach the shipped state with no leftovers? | R1, retired hooks, T1 |
| A2 | Preservation | Does every user-owned item survive install, `--force`, `update`, uninstall? | shared dirs, CLAUDE.md, MCP names |
| A3 | Idempotency, uninstall completeness | Is a second run a no-op? Does uninstall restore the snapshot minus documented keeps? Does an interrupted run converge? | T1, T2, T5, T6, R1 |
| A4 | Scope isolation | Does scope X write only X? Co-existence, worktrees, `CLAUDE_CONFIG_DIR`? | T4, remediation (main.py:559) |
| A5 | Detection truthfulness | Do doctor, verify-drift, `--list-all` match reality? | T1, R1 |
| A6 | Robustness, platform | Malformed, non-UTF-8, BOM, read-only inputs; Windows forms, CRLF | T3, T5, T6 |

A6 merges error handling and platform: same test shape. Claude Code docs: "If you define the same handler in more than one settings file, it runs once" (hooks reference, re-fetched 2026-10-19). Only a legacy or pinned variant beside the console form runs twice; a doubled `loop_guard` trips at half its threshold (X3).

## 3. Scenario matrix

**Building old refs [v2: P-2].** `77b5821c`, `b85651c0^` and `ec6fa7e2^` hold a stray gitlink (`.claude/worktrees/lucid-kalam`; re-checked with `git ls-tree -r <ref> | awk '$2=="commit"'`), so `uvx --from git+file://…` fails there. `old-install.sh` always extracts: `git -C $REPO archive <ref> | tar -x -C $SB/src-<ref>`, then `uvx --offline --from $SB/src-<ref> superclaude install --scope <s> </dev/null`. Re-checked on `ec6fa7e2^` local: 0.7 s, exit 0. Local scope exists only from bd356afa (2026-04-19); the script reads the ref's `click.Choice` and refuses a missing scope. A ref that will not build within 10 min falls back to the fixture builder (§5).

**Run environment [v2: P-10].** `env HOME=$SB/home CLAUDE_CONFIG_DIR=$SB/home/.claude UV_CACHE_DIR=~/.cache/uv PATH=$SB/bin:/usr/bin:/bin`. `$SB/bin` holds `uv`/`uvx` links (both live in `~/.local/bin`, which stays off PATH) and a `superclaude` shim for the CLI under test, so `probe_console_script` never runs the real tool. `CLAUDE_CONFIG_DIR` equals the default; only X7 moves it [v2: P-7]. The current CLI runs as `uv run --project $REPO superclaude …` with CWD `$SB/proj`. No `uv cache clean`: old installs' hooks name a uv-cache interpreter.

**Customizations C** (seeded before the old install): settings.json with `model`, `permissions`, a user entry and a user hook inside an SC entry; user agent, output style, `my-skill/`, `commands/mine.md`; CLAUDE.md text; `.gitignore` and `info/exclude` lines. After the old install: an agent-memory file and both insights files.

**Checker:** `snap.py` ({path → sha256, mode} plus parsed settings, CLAUDE, exclude) over all of `$SB`; each scenario asserts expected-diff = actual-diff. A real-HOME guard (`find ~/.claude ~/.claude.json -newer $MARK`) runs per batch.

| ID | Source (why) | Scope | Action → expected | Check |
|---|---|---|---|---|
| U1 | v4.29.5 (everyday) | each | `update` → drift clean, C intact, 14/14 hooks | snap, verify-drift 0 |
| U2 | v4.20.1 (first fork release) | user | non-force install → per Q3 | T1 recipe |
| U3 | v4.20.1 | user | `update` → user agent not EXTRA (Q9) | exit code |
| U4 | `19575ac4^` (last legacy hooks) | local | non-force → `update` → uninstall → snapshot minus Q11 keeps; era state dir in `~/.claude` reported [v2: P-7] | T2 recipe |
| U5 | `19575ac4^` | project | teammate install → committed settings hold no machine path | `git diff` grep |
| U6 [v2: P-2, P-3] | `77b5821c` (project), `ec6fa7e2^` (local): `{{PYTHON_BIN}}`; `19091b37` (user) | as listed | each form rewritten once; `19091b37` per Q14 | count per hook id |
| U7 | `b85651c0^` (`.gitignore` era) | local | block moved; user lines byte-identical | snap |
| U8 [v2: P-7] | `b933fd65^` (skills, agents, jq blocker) | user | install → stale items removed, `my-skill/` kept; **uninstall** → no SC skill, agent or hook left | files, hook ids |
| U9 | `ec6fa7e2^` (pre-`memory:` rewrite) | user, local | conflict guard as documented; no silent move | stdout, grep |
| U10 [v2: P-11] | v4.1.9 (fork root) | user | install/uninstall delete nothing foreign | snap |
| U11 [v2: P-1] | `66b37a7e^` (`Setup`, `skill_activator`), `d174e600` (echoes) | user, project | non-force → `update` → uninstall: no retired registration after the first install (Q13) | hook ids per event |
| X1 | local only | — | `update`, no `--scope` → refuse (Q4); `~/.claude` untouched | snap |
| X2 | local, drifted | — | remediation line verbatim → stays local | snap |
| X3 | project + local in one tree, both orders | — | conflict guard; no doubled handler | handler count |
| X4 | user + project | — | project install, update, uninstall: `~/.claude` byte-identical | snap |
| X5 | local at `$HOME` | — | `detect_scope`, doctor, uninstall agree | doctor line |
| X6 | linked worktree local; sibling project | — | exclude in common dir; "last install wins" reported | `git check-ignore -v` |
| X7 [v2: P-7] | user sets `CLAUDE_CONFIG_DIR=$SB/cc` | user | install, doctor, uninstall per Q15; `$SB/cc` untouched | stdout, snap |
| I1 | fresh | each | install ×2, `--force` ×2 → 0 bytes written, mtime unchanged | snap |
| I2 [v2: P-7] | fresh + C | each | install → uninstall → snapshot minus keeps (CLAUDE.md per Q11, pending insights kept) | snap |
| I3 | stub `claude` | each | `--remove-mcp` with a user `playwright` per Q12 | stub log |
| I4 [v2: P-7] | fresh, U4 state | each | fault at each `install_all`/`uninstall_all` step → re-run reaches I1; uninstall cleans; doctor never "healthy" mid-way | pytest |
| D1 | U2/U4/U11 ends + deleted files, deleted `scripts/` under legacy commands, duplicates | — | doctor, verify-drift, `--list-all` each report it, or why not | exit, rows |
| E1 | malformed settings.json | each | install refuses unchanged; **uninstall must not claim success** (T5) | exit, hooks |
| E2 | read-only file, dir, settings | user | failure counted, exit 1, no half-write | snap |
| E3 | cp949 / UTF-16 CLAUDE files | user, local | no traceback; untouched (T3) | bytes |
| E4 | CRLF CLAUDE.md | each | detected; no orphan `# superclaude\r` | bytes |
| E5 | synthetic `C:\…\python.exe …\scripts\x.py`, quoted `…\superclaude.exe hook x` | user | recognised, rewritten or kept pinned | hook id |
| E6 [v2: P-6] | settings(.local).json as UTF-16, UTF-8-BOM, cp949 | each | all four commands: no traceback, **nothing written or deleted before refusing** (T6), exit 1 | snap |

Run time: 1–3 s per scenario, about 70 runs, ≈ 5 min per pass.

**Windows (owner-run):** W1 `os.replace` while Claude Code holds settings.json; W2 `rmtree` on read-only files; W3 drive or letter case in `same_dir`/`find_install_root`; W4 `.exe` shim, GUI-launched PATH; W5 `make sync-*` os error 5. W6 [v2: P-6]: does Claude Code accept a UTF-8-BOM settings.json, and does PowerShell 5.1 `Out-File` write UTF-16? W7 [v2: P-7]: which CLAUDE.md and settings.json does Claude Code read with `CLAUDE_CONFIG_DIR` set? The round ships a PowerShell script for U1, U4, I2 and E6 (~25 min).

