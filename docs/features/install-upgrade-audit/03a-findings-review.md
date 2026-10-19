---
feature: install-upgrade-audit
phase: triage
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 03a. Code review (P3), axes A1–A6

The companion to [03-findings.md](./03-findings.md). Read in full on `master` @ 1dd9622c: `cli/install_{paths,components,settings,inventory,git_exclude,mcp}.py` (install_mcp.py for its uninstall and scope paths), `cli/verify_drift.py`, `cli/doctor.py`, the `install`/`uninstall`/`update`/`doctor`/`verify-drift` commands in `cli/main.py`, and the hook-identity block in `utils/__init__.py`. Each branch below is tagged with the matrix ID that reaches it, a synthetic repro, or the reason it needs none. Every line was re-read before filing. Read-only subagents were not used for P3; one ran the P1 git archaeology, and its citations were spot-checked (`49286ed4` body, `v4.0.9:setup/components/core.py`, `385baaf2` vs `ec6fa7e2` ancestry, `12cbcb4f` hooks.json).

## A1 Upgrade migration

| Code | Behaviour | Reached by | Verdict |
|---|---|---|---|
| install_components.py:491-537: memory guard, legacy-skill prune, `find_unshipped` before content | prunes only listed names and SC-only dirs | U8, U10, D1 | correct for what is listed; the lists are incomplete → C-08 |
| :206-282 skip-if-exists (non-force) | existing content kept, drift unreported | U2, U9 | by design (Q3 a); the report is missing → C-10 |
| install_settings.py:239-297 non-force merge: existing entries authoritative, missing shipped ids appended | correct for shipped ids | U1, U4, U6 | holds |
| :300-347 `_migrate_legacy_commands` | rewrites only when a console replacement exists | U5, U6, E5 | holds; ids with no replacement stay → C-09 |
| :404-417 retired-event strip, `--force` only | non-force never visits `Setup` and friends | U11 | → C-09 |
| utils/__init__.py:251-319 identity: anchored markers, console regex, legacy path regex | unmarked echoes and `.claude/hooks/x.py` are not SC | U11, U6-19091b37 | → C-09, C-16 |
| install_components.py:74-132 `find_agent_memory_conflict` | `project` gated on git tracking; `user`/`local` never gated | U9, X3, U11-d174e600-project | → C-06 |

## A2 Preservation

| Code | Behaviour | Reached by | Verdict |
|---|---|---|---|
| install_settings.py:175-209 `_split_entry` / `_strip_sc_inner_hooks` | a user hook inside an SC entry stays where it was | `seed-C post` in every U and I2 run | holds |
| :575-619 CLAUDE import append | whole-file rewrite in text mode | E4 | LF conversion → C-20 |
| :622-674 CLAUDE import removal | unanchored `@superclaude/[^\n]+` and `@\.claude/superclaude/[^\n]+`, `\n{3,}` collapse, `strip()` | P3a, I2, U10 | → C-07 (S1), C-20 |
| install_inventory.py:196-254 shared-dir uninstall | shipped names only; dir removed when empty | U3, I2 | holds |
| install_git_exclude.py:144-186, 250-365 block strip, migrate | marker-keyed; user lines intact | U7, I2 | holds |
| install_mcp.py:583-656 `uninstall_mcp_servers` | name match only | I3 | → C-13 |
| utils/__init__.py:82-110 `atomic_write_json` | mkstemp 0600, `json.dump` re-serialises | E2, I2 | → C-21 |

## A3 Idempotency, uninstall completeness, interrupted runs

| Code | Behaviour | Reached by | Verdict |
|---|---|---|---|
| install_settings.py:434-441 no-change path | settings untouched when the hooks are equal | I1 | holds |
| install_components.py:365-380 `hooks.json` always rewritten | identical bytes, new ctime | I1 | by design (the comment there) |
| install_inventory.py:257-602 order: content (:298-443), then settings (:445-486), CLAUDE (:488-516), exclude (:518-551), MCP (:553-574) | every delete precedes the first read of user input | E1, E6, I3-noclaude | → C-01, C-02, C-14 |
| uninstall has no memory-dir step; install_settings.py:504-525 keeps `{}` at U | leftovers | I2-user-noC | → C-12 |
| install_all order: memory dir → prune → components → hooks → CLAUDE_SC → CLAUDE import → exclude | a failure late in the order leaves content without its import or exclude | I4 | converges on re-run; doctor misses a missing exclude → C-19 |

## A4 Scope isolation

| Code | Behaviour | Reached by | Verdict |
|---|---|---|---|
| main.py:85-90, 247-252, 383-388 `--scope` default `user` for install, uninstall, update | `update` never checks that an install exists | X1 | → C-04 |
| main.py:559 verify-drift remediation | bare `install --force` | X2 | → C-05 |
| doctor.py:27-47 `_repair_command` | carries scope and directory | X2 | holds |
| install_paths.py:93-172 `get_base_path`, `find_install_root`, `resolve_reporting_target` | writes follow the CWD, reports walk up and stop at `$HOME` | X5, X2 | holds |
| install_paths.py:105-108 user base ignores `CLAUDE_CONFIG_DIR` | silent | X7 | → C-15 |
| install_git_exclude.py:31-41 one block per clone, last install wins | not reported | X6 | → C-18 |
| install_inventory.py:427-443 state dir under this scope's base only | pre-`52b5517e` L/P state in `~/.claude` unreachable | U4 | → C-17 |

## A5 Detection truthfulness

| Code | Behaviour | Reached by | Verdict |
|---|---|---|---|
| doctor.py:67-80 binary `passed` over five checks; `_check_hooks_installed` needs one SC entry per event | no drift, missing-content, obsolete-hook or exclude check | U2, D1, E3-exclude | → C-10, C-19 |
| verify_drift.py:94-96 EXTRA for any unshipped `.md` in shared `agents/`, `output-styles/` | user files read as drift | U1, U3 | → C-11 |
| verify_drift.py:129-145 EXTRA only inside shipped skill dirs | stale SC skill dirs invisible | U8 | → C-11 |
| install_inventory.py:83-114 hook identity report | missing, obsolete and duplicate are correct | D1-duplicate, D1-scripts-gone | holds; main.py:191-195 shows ✅ beside "obsolete" → C-10 |

## A6 Robustness, platform

| Code | Behaviour | Reached by | Verdict |
|---|---|---|---|
| install_settings.py:57-61 `_load_settings`, :75-79 `_unwritable_settings`: `JSONDecodeError`/`IOError` only (`UnicodeDecodeError` is a `ValueError`) | traceback on UTF-16 and cp949 | E6 | → C-01, C-03 |
| doctor.py:162-171: same catch; `settings.get` on a list | traceback | E6, P3b | → C-03 |
| install_settings.py:596-597, install_inventory.py:497, install_git_exclude.py:306: reads with no decode guard | traceback | E3, E3-exclude | → C-03, C-19 |
| install_settings.py:563-565 `check_claude_md_import` catches `UnicodeDecodeError` | then the writer at :597 reads the same file unguarded | E3 | → C-03 |
| install_mcp.py:295-307 `check_plugin_installed` misses `FileNotFoundError` | traceback | I3-noclaude | → C-14 |
| install_components.py:161-175 `_safe_target_path` | symlink escape refused for directory components | none run | not exercised: the matrix has no symlinked skill dir. Read only, no defect seen |
| utils/__init__.py:265-283 Windows forms (backslash, `.exe`, quoted) | recognised | E5 (synthetic) | holds on Linux; W1–W7 stay owner-run |
