---
feature: install-upgrade-audit
phase: matrix
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 02. Scenario matrix, run 1

P0 and P2 of [05-plan.md](./05-plan.md), against `master` @ 1dd9622c (v4.29.6) on Linux. The U-series is below; X, I, D and E are in [02a-scenarios-edge.md](./02a-scenarios-edge.md). The findings each failed check maps to are in [03-findings.md](./03-findings.md).

## 1. Harness (P0)

Kept outside the repo, in the audit's scratch directory (`harness/`). Nothing in it imports the code under test, except `i4.py`, which has to call `install_all` to inject faults.

| Piece | What it does |
|---|---|
| `lib.sh` | `sb_new` builds `sandbox/p2/<id>/{home,proj (git repo),bin,snaps,out}`. `sbx` runs a command under `env -i HOME=$SB/home CLAUDE_CONFIG_DIR=$SB/home/.claude UV_CACHE_DIR=~/.cache/uv PATH=$SB/bin:/usr/bin:/bin`, from `$SB/proj`, with stdin `/dev/null`. An inner check exits 99 if `$HOME` resolves to the real home, and `_assert_sandbox` refuses any path outside `sandbox/`. `$SB/bin` holds `uv`/`uvx` links, a `superclaude` shim (`uv run --no-sync --project <repo> superclaude`, so the probe in install_paths.py:300-349 finds the CLI under test and never syncs the venv), and a stub `claude` that logs argv and answers `mcp list` / `plugin list` from files. |
| `guard` | Real-HOME guard, run before and after every batch: `~/.claude/settings.json` md5 unchanged, no SC artifact (`CLAUDE.md`, `superclaude/`, `commands/`, `agents/`, `output-styles/`, `hooks/`, `agent-memory/`, `.superclaude_hooks/`, `skills/sc-*`), `~/.claude.json` MCP keys unchanged. It does not use `find -newer` over all of `~/.claude`: the live Claude Code session writes there, including `skills/synced/`. |
| `old-install.sh <id> <ref> <scope>` | `git archive <ref>`, then `uvx --offline --from <extract> superclaude install --scope <s> </dev/null`. It reads the ref's `install --help` and refuses a scope that ref does not offer. All the refs built, in 0.7–1.2 s. |
| `seed-C.sh <id> <scope> pre\|post` | Customizations C. `pre`: settings with `model`, `permissions`, `statusLine` and a user `PreToolUse` hook; `my-agent.md`, `my-style.md`, `skills/my-skill/`, `commands/mine.md`; CLAUDE text with a run of 3 blank lines; `.gitignore` and `info/exclude` lines. `post`: a user hook inside an SC entry, an agent-memory file, both insights files. |
| `snap.py` | `snap`: {path → sha256, mode} over the whole sandbox, plus each settings file classified by its own hook table (console, legacy-scripts, legacy-template, legacy-dothooks, jq-blocker, experimental-echo, user). `diff`: added, removed and changed paths. |
| `matrix.py`, `scen_u.py`, `scen_x.py`, `run_matrix.py`, `run-matrix.sh [ID…]` | One function per scenario. Each records every command with its exit code, output tail and traceback flag, and every check as (expected source, observed, pass), to `sandbox/p2/results/<id>.json` plus `summary.md`. |
| `i4.py` | Fault injection for I4: `mock.patch` on each `install_all` / `uninstall_all` step, run with the repo venv inside the sandbox env. |
| `capture_fixtures.py`, `gen_shipped_names.py` | Fixture capture (§4) and the Q10 history generator ([01a](./01a-inventory-history.md) §3). |

Sanity runs: a fresh current-CLI user install (`sanity1`: 83 installed, doctor healthy, drift clean, 14 console hooks) and a v4.20.1 install plus C (`sanity2`). Both kept the guard clean. Full pass: about 2 minutes. The guard was clean after every batch. It tripped once, mid-P2, on `skills/synced/<uuid>/manifest.json`, which is Claude Code's own skill sync; the guard was narrowed to SC artifacts, and nothing of SC's reached the real home.

## 2. Result table

99 records. The 36 E6 records collapse to one row.

| ID | Result | Failed checks → finding |
|---|---|---|
| U1-user/project/local | FAIL | verify-drift exit 1 on `my-agent.md`, `my-style.md` EXTRA → C-11 |
| U2 | FAIL | no "N files differ" note; doctor healthy with 76 drifted, 2 extra → C-10 |
| U3 | FAIL | verify-drift EXTRA → C-11 |
| U4 | FAIL | `~/.claude/.superclaude_hooks` not reported → C-17; no warning when the non-empty `agent-memory-local/` loses its exclude → C-12 |
| U5 | PASS | — |
| U6-77b5821c, U6-ec6fa7e2p | FAIL | jq blocker kept beside `destructive_guard` → C-09 |
| U6-19091b37 | FAIL | no Q14 note; `session_init` runs twice; uninstall leaves 3 commands → C-16 |
| U7 | PASS | — |
| U8 | FAIL | 11 process skills and 2 renamed agents survive install and uninstall → C-08; jq blocker → C-09 |
| U9-user, U9-local | FAIL | `update` moves `memory:` silently; after a non-force install 23 agents keep `memory: project` → C-10 |
| U10 | FAIL | uninstall collapses the user's blank-line run → C-20 |
| U11-66b37a7ep-user/project | FAIL | `Setup session_init` and `skill_activator` kept by non-force install → C-09 |
| U11-d174e600-user | FAIL | unmarked echo hooks survive install, `update` and uninstall → C-09 |
| U11-d174e600-project | FAIL | install refused: `memory: user` "conflict", with `--scope user` advice → C-06 (Q13 could not be tested at P) |
| X1 | FAIL | `update` created a 100-file user install → C-04 |
| X2 | FAIL | verify-drift remediation `install --force`, followed verbatim, created a user install → C-05 |
| X3 ×3, X4, X5 | PASS | — |
| X6 | FAIL | block replaced by a sibling worktree's install, not reported → C-18 |
| X7 | FAIL | no `CLAUDE_CONFIG_DIR` warning from install or doctor → C-15 |
| I1-user/project/local | PASS | — |
| I2-user/project/local | FAIL | CLAUDE file whitespace changed → C-20; settings re-serialised → C-21 |
| I2-user-noC | FAIL | `CLAUDE.md` (SC heading only), empty `agent-memory/`, `{}` `settings.json` left → C-12 |
| I3-user/project/local | FAIL | the user's own `playwright` removed → C-13 |
| I3-noclaude | FAIL | traceback after content deletion → C-14 |
| I4 | FAIL | the 12 failures are U-scope "uninstall leaves `CLAUDE.md` + `{}` settings" (C-12) and local "interrupted at `add_git_exclude`: doctor healthy" (C-19) |
| D1-stale, D1-deleted, D1-scripts-gone | FAIL | doctor healthy → C-10 |
| D1-duplicate | PASS | — |
| E1-user/project/local | FAIL | partial install before the refusal → C-03 |
| E1-*-uninstall | FAIL | "No hooks", exit 0, hooks kept, content deleted → C-02 |
| E2-ro-file, ro-dir, ro-base | PASS | — |
| E2-ro-settings | FAIL | a 0444 settings file is replaced, exit 0 → C-21 |
| E3 ×4 | FAIL | traceback (install_settings.py:597; install_inventory.py:497 on `--dry-run`) after 100 files → C-03 |
| E3-exclude | FAIL | traceback at install_git_exclude.py:306; doctor healthy → C-19 |
| E4 ×3 | FAIL | CRLF converted to LF on install and uninstall → C-20 |
| E5 | PASS | — |
| E6 ×36 | 6 PASS / 30 FAIL | UTF-16 and cp949: traceback in all four commands; uninstall deletes 98 files first → C-01. BOM: install partial, uninstall exits 0 with hooks left → C-02, C-03. BOM `update` and `doctor` pass. |

## 3. U-series (upgrades from real old installs)

Each scenario runs `seed-C pre` (if C), then the old install, then `seed-C post`, then the listed current-CLI commands. "Expected" cites the code, README or owner decision the end state comes from.

| ID | Source / scope / C | Sequence | Expected (source) | Observed | Result |
|---|---|---|---|---|---|
| U1 | v4.29.5 / each / C | `update --scope S`, `verify-drift`, `doctor` | C intact, 14 hooks once each (install_settings.py:212-297); verify-drift 0 (Q9 a) | C intact, hooks exact, doctor healthy; verify-drift exit 1 (2 EXTRA, the user's files) | FAIL |
| U2 | v4.20.1 / U / C | `install`, `verify-drift`, `doctor` | install names stale files, doctor advisory, exit 0 (Q3 a) | 34 commands, 23 agents, 1 style "skipped"; verify-drift 76 drifted 2 extra; doctor "healthy" | FAIL |
| U3 | v4.20.1 / U / C | `update`, `verify-drift --verbose`, `uninstall -y` | no EXTRA for user files (Q9 a) | `my-agent.md: EXTRA`, `my-style.md: EXTRA`, exit 1 | FAIL |
| U4 | `19575ac4^` / L / C, plus a `~/.claude/.superclaude_hooks/` file (bd356afa→52b5517e era) | `install`, `doctor`, `update`, `uninstall -y` | legacy commands rewritten once; uninstall = snapshot − Q11 keeps; era state reported (plan U4); warning on the lost exclude (Q11 b) | hooks exact after install and update; doctor healthy; state dir not mentioned; `agent-memory-local/` kept, its exclude removed, no warning | FAIL |
| U5 | `19575ac4^` / P / committed | `install` | no machine path in committed settings.json (install_settings.py:303-317; README:91) | clean; hooks exact | PASS |
| U6 | `77b5821c` P, `ec6fa7e2^` L, `19091b37` U | `install` (+ `update`) | each legacy form rewritten once; `19091b37` per Q14 (b) | 6 rewritten; jq blocker kept (2 destructive blockers); `19091b37`: 0 rewritten, console `session_init` added beside `python .claude/hooks/session_init.py`, no note; after uninstall the 3 commands, `hooks/*.py` and the 2 renamed agents are left | FAIL |
| U7 | `b85651c0^` / L / `.gitignore` lines | `install` | block moved to `info/exclude`; `.gitignore` byte-identical (install_git_exclude.py:250-323) | identical; `check-ignore` hits | PASS |
| U8 | `b933fd65^` / U / C | `install`, `verify-drift`, `doctor`, `--list-all`, `uninstall -y` | stale SC skills and agents removed, `my-skill/` kept; uninstall leaves no SC item (plan U8; main.py:277-286) | 11 skills plus `pm-agent.md` and `deep-research-agent.md` kept by both; doctor healthy; `--list-all` "Skills [2/2]", "Hooks [14/14] └─ 1 obsolete" | FAIL |
| U9 | `ec6fa7e2^` / U, L | `install`, `update` | install proceeds (install_components.py:84-88); no silent move (plan U9) | install proceeds; 23 agents keep `memory: project` plus 1 new; `update` rewrites all to the scope with no message | FAIL |
| U10 | v4.1.9 / U / C | `install`, `uninstall -y` | nothing foreign deleted (plan U10; README:158) | removed only `commands/sc/{sc,spawn,workflow}.md`; C files intact; CLAUDE blank-line run collapsed | FAIL |
| U11 | `66b37a7e^`, `d174e600` / U, P | `install`, `update`, `uninstall -y` | no retired registration after the first install (Q13 a) | `66b37a7e^`: `Setup session_init` and `skill_activator` kept until `update`. `d174e600` U: echo hooks kept through uninstall. `d174e600` P: install exit 1 (C-06) | FAIL |

## 4. Fixtures (plan §5)

`tests/fixtures/legacy_installs/<era>.json` was captured once by `capture_fixtures.py` from fresh old installs with no C. There are 12 eras: `v4.20.1-user`, `19575ac4p-local`, `19575ac4p-project`, `77b5821c-project`, `ec6fa7e2p-local`, `ec6fa7e2p-user`, `19091b37-user`, `b85651c0p-local`, `b933fd65p-user`, `66b37a7ep-user`, `d174e600-user`, `d174e600-project`. Each file lists every path under `$HOME` and `$PROJECT` (the latter `.git/` excluded, except `info/exclude`).

- **Exact text** is kept for `agents/*.md`, `skills/*/SKILL.md`, `settings(.local).json`, `CLAUDE(.local).md`, `.git/info/exclude` and `.gitignore`, and (since the W-1 fix, which removes a retired skill file by file) every file of a retired skill. Each is stored once, by digest, in `_blobs.json`, because the same agent text recurs across eras.
- **sha256 + size** for everything else; the builder writes a `stub <sha256>` file there.
- **Tokens** replace machine paths: `$PYTHON` (any interpreter under the uv cache, which is where the uvx archive interpreter lives), `$UVCACHE`, `$PROJECT`, `$HOME`.
- **Data, not code:** `tests/fixtures/shipped_names_history.json` is the Q10 input ([01a](./01a-inventory-history.md) §3).

`tests/unit/test_install_upgrade_scenarios.py` is network-free and history-free.

- **Builder:** `build_legacy_install(tmp_path, era, monkeypatch)` git-inits the project and monkeypatches `HOME`, `USERPROFILE` and `CLAUDE_PROJECT_DIR` (`test-anchor-env`).
- **Leak test:** rejects `/home/`, `/Users/`, `archive-v0` and email addresses. It scans decoded strings, so `\n@pytest.mark` inside a blob is not read as an address. A planted path, address and `archive-v0` were caught, then removed.
- **Behaviour tests (current code passes):** every era builds; the history lists every name shipped now; U5 (committed settings lose their machine paths); U6 (`77b5821c` commands become exactly the shipped console set); U7 (`.gitignore` block moved).

No worktree fixture was captured, so the builder does not write `commondir` yet; the X6 regression test in P5 adds it.
