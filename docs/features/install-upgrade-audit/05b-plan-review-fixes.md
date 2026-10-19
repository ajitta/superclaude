---
feature: install-upgrade-audit
status: implementing
revised: 2026-10-19
---

# Axis C plan v2 — §4–§5: code review, outputs and fix policy

Part of [05-plan.md](./05-plan.md) (plan v2, §4–§5).

## 4. Code review part

| Axis | Read |
|---|---|
| A1 | `install_all` (install_components.py:477-635, skip-if-exists :206-282); prune lists (install_paths.py:217-290); `_merge_hook_arrays` (install_settings.py:239-297), retired-event strip (:404-417), `_migrate_legacy_commands` (:325-347); hook identity (utils:251-319) [v2: P-1] |
| A2 | `_split_entry`, `_strip_sc_inner_hooks` (install_settings.py:175-209); CLAUDE import (:575-674); `_uninstall_shared_component` (install_inventory.py:196-254); `uninstall_mcp_servers` (install_mcp.py:229-262, 583-656); install_git_exclude.py:144-273 |
| A3 | no-change path (install_settings.py:434-441); `uninstall_all` order (install_inventory.py:257-602: content deleted before settings read, T6); `install_all` order (I4); `_pending_file` [v2: P-6, P-7] |
| A4 | install_paths.py:93-172; scope defaults (main.py:85-419; `update` → `"user"` :385; remediation :559); `_repair_command`; `find_agent_memory_conflict`; `detect_scope`, `claude_base`, `main_worktree_root` |
| A5 | `run_doctor` (doctor.py:50-250, binary `passed` :77); verify-drift EXTRA (:94-96) vs `_check_directory_component` (:129-145, blind to unshipped skill dirs) [v2: P-8]; install_inventory.py:83-114 |
| A6 | reads without a decode-error path; `_load_settings` catches only `JSONDecodeError`/`IOError` (install_settings.py:60) and is uninstall's only loader; `_unwritable_settings` (:384); `_safe_target_path`; CRLF regexes |

Each branch is tagged with the matrix ID that reaches it, or gets a synthetic scenario or a reason.

**A finding has:** ID `C-NN`, axis, severity (**S1** data lost, hooks blocking, another scope written, uninstall half-done; **S2** false health or wrong end state; **S3** cosmetic/doc); `file:line` re-read before filing; a repro; expected (citing a docstring, README or test) vs actual output; verdict CONFIRMED / BY-DESIGN (source) / REJECTED; scopes and eras. Without a source for the expected state, it is an observation.

## 5. Outputs and fix policy

**Docs:** `docs/features/install-upgrade-audit/`: `README.md`, `01-inventory.md`, `02-scenarios.md`, `03-findings.md`, `04-handoff.md`, and the plan [v2: P-9], committed already split: a `05-plan.md` index plus `05a-plan-matrix.md` (§1–§3) and `05b-plan-review-fixes.md` (§4–§5), with `{status, revised}` frontmatter (`RULES_DOCS.md` Size; `test_plan_checklist.py`). Cite sources, not counts (`stale-number-copies`).

**Fixtures [v2: P-5].** `tests/fixtures/legacy_installs/<era>.json`, captured from U2, U4, U6×3, U7, U8, U9, U11×2. Exact bytes for `agents/*.md`, `skills/*/SKILL.md`, settings, CLAUDE files, `info/exclude`, `.gitignore`: the memory guard, the agent scope compare, the auto-invocation flag and the heading strip all read content. sha256 plus a stub for the rest. Tokens: `$HOME`, `$PROJECT`, `$PYTHON` (including the uvx archive interpreter), `$UVCACHE`; a test rejects `/home/`, emails and `archive-v0`. `build_legacy_install(tmp_path, era, scope, customizations)` runs `git init` and writes `commondir` for worktrees (`git-common-dir-paths`); `HOME`/`CLAUDE_PROJECT_DIR` are monkeypatched (`test-anchor-env`). New module `tests/unit/test_install_upgrade_scenarios.py`, network-free, Python 3.10 and 3.13.

**Keystone guard (Q10) [v2: P-1, P-4].** `tests/fixtures/shipped_names_history.json` comes from full history; no fork tag holds the renamed agents or the 16 retired skills. Inputs: `git log --format= --name-only` over `src/superclaude/{agents,output-styles,skills}/` (re-checked: 3 agents, 16 skill dirs), plus any other dir an era's installer read (P1 checks `superclaude/`, `plugins/`); and hook ids and events from every `hooks.json` revision. A test requires every historical identity not shipped now to be on a retired list. The generator refuses a shallow clone; the release recipe says "full clone".

**Per defect:** red test → fix → module tests green. At merge, the full `uv run pytest` and `make format lint typecheck`. A preflight fix (Q16) also covers uninstall: validate before the first delete.

**CI [v2: self].** `test.yml` has no push trigger; it runs on PRs to `master`, on dispatch and in `make ci`. v1 Q6 said "every push", which was wrong.

**Release:** one at round end: patch 4.29.7, or minor 4.30.0 with an upgrade note if Q3/Q4/Q13/Q15/Q16 lands. `make canary-gates` only if `core/` or `hooks.json` changes (not expected: the retired lists live in `cli/`/`utils/`). A hook-identity change in `utils/__init__.py` also runs `test_hook_dispatch.py`.

