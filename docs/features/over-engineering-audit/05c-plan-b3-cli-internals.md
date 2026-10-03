---
status: draft
revised: 2026-10-03
---

# B3: Behavior-preserving CLI internals

Item specs for batch B3. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b3). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F19: install_commands.py facade

`delete` · verdict **confirmed** · ~90 lines · owner decision: no

install_commands.py is a 45-line re-export facade imported only by main.py (3 lazy imports at 134, 314, 438), test_cli_install.py (top import 11-15 + inner import 192) and one patch target in test_install_interactive.py:30. The legacy install_commands() function (install_components.py:590-612) has zero production callers; its only references are the facade re-export and 10 call sites in tests/unit/test_cli_install.py.

**Changes**

- `src/superclaude/cli/install_commands.py` (delete): git rm the whole file.
- `src/superclaude/cli/install_components.py` (delete): Delete install_commands() (590-612) and the blank lines before it. Tuple/Path imports stay used.
- `src/superclaude/cli/main.py` (edit): install() (134-140): from .install_components import install_all; from .install_inventory import list_all_components, list_available_commands, list_installed_commands; from .install_paths import get_base_path, resolve_reporting_target. uninstall() (314): from .install_inventory import uninstall_all; from .install_paths import get_base_path. update() (438): from .install_components import install_all; from .install_paths import get_base_path. Keep every import INSIDE the function body: that is what lets a test patch install_components.install_all and have main.py see it.

**Tests**

- tests/unit/test_install_interactive.py:20-48 fixture mock_install_all: drop the install_commands patch (m2) and the _Either wrapper; become `with patch('superclaude.cli.install_components.install_all', return_value=ret) as m: yield m`. Every use (assert_called_once, assert_not_called, call_args.kwargs) is native Mock API. Fix docstring lines 22-26.
- tests/unit/test_cli_install.py:11-15: replace with `from superclaude.cli.install_components import install_all` and `from superclaude.cli.install_inventory import list_available_commands, list_installed_commands`.
- tests/unit/test_cli_install.py: convert each install_commands(target_path=tmp_path/'commands', force=X) at 34, 56, 60, 69, 81, 100, 139 to install_all(base_path=tmp_path, force=X); 115 -> base_path=tmp_path/'nested'; 169 -> base_path=tmp_path/'a'/'b'/'c'. Assertions on tmp_path/'commands'/'sc' and on 'installed'/'skipped' in the message stay valid (install_all's summary says both).
- tests/unit/test_cli_install.py: delete test_empty_target_directory_ok (176-183) and test_install_commands_creates_target_directory (109-120): they pin only the deleted target_path-to-base_path derivation and duplicate test_install_to_nonexistent_parent. Delete test_cli_integration (186-198), a facade smoke test that duplicates test_list_available_commands.
- Rename tests/classes that say 'install_commands' (TestInstallCommands etc.) only if desired; not required.

**Doc references**

- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:32 -> change the 전체 Python module row from 57 to 56 (recompute: uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))")
- No other doc, README, ARCHITECTURE.md or help text mentions install_commands.py

**Collateral**

- Do F19 BEFORE F35g: install_commands() is the only production caller that passes base_path=None into install_all
- README component counts (test_version_consistency) are not affected (they count content, not modules)
- Import-order/hook fast path unaffected: hook_dispatch.py never imported the facade or click
- tests/unit/scripts is untouched, so make test-scripts is not needed

**Verify**

```bash
git rm src/superclaude/cli/install_commands.py; grep -rn "cli.install_commands\|from .install_commands\|install_commands(" src tests --include=*.py   # expect no hits;  uv run pytest tests/unit/test_cli_install.py tests/unit/test_install_interactive.py tests/unit/test_codex_component_map.py -q;  uv run ruff check src/ tests/;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- grep -rn install_commands over the whole repo (hidden dirs included, docs/archive excluded): src/superclaude/cli/install_commands.py, install_components.py:590, main.py:134/314/438, tests/unit/test_install_interactive.py:25/30, tests/unit/test_cli_install.py:11-12/34/56/60/69/81/100/115/139/169/181/192 (10 calls); install.sh:213/435 is an unrelated shell function of the same name
- No pyproject/entry-point/Makefile/.github/evals/scripts reference; the only entry point is pyproject.toml:67 superclaude.cli.entry:main; no importlib/string use of 'superclaude.cli.install_commands'
- Facade exports (COMPONENTS, get_base_path, CLAUDE_SC_IMPORT, SUPERCLAUDE_HOOK_MARKERS, install_all, list_*, uninstall_all) all have real homes: install_paths (COMPONENTS, get_base_path), install_settings, install_components (install_all), install_inventory (list_*, uninstall_all); nothing imports COMPONENTS/CLAUDE_SC_IMPORT/SUPERCLAUDE_HOOK_MARKERS through the facade
- No test patches get_base_path or anything else on install_commands except install_all (test_install_interactive.py:30); test_verify_drift patches install_paths._get_package_root, unaffected
- install_commands() maps target_path.parent (when name == 'commands') to base_path and calls install_all(base_path=..., force=...), so each test call equals install_all(base_path=&lt;tmp_path or its ancestor>, force=...)
- tests/unit/test_codex_component_map.py counts src/superclaude/**/*.py: currently 57 (python check matches the doc), 56 after the file is deleted

</details>

## F35g: base_path=None fallbacks

`yagni` · verdict **confirmed** · ~25 lines · owner decision: no

The base_path=None -> Path.home()/'.claude' fallback exists at 9 sites and no production caller relies on it. The only bare calls are one test (test_cli_install.py:96 list_installed_commands()) and the legacy install_commands() shim (install_components.py:604-612, deleted by F19), which passes base_path=None into install_all. The fallback is also wrong for project/local scope (it would silently target ~/.claude), so it is a latent trap, not a feature. uninstall_all's own base_path=None branch (install_inventory.py:355) is scope-aware (get_base_path(scope)), is NOT in the list, and must stay.

**Changes**

- `src/superclaude/cli/install_paths.py` (edit): _get_target_dir(component, base_path: Path): remove the 2-line fallback (176-177) and the '(default: ~/.claude)' docstring text.
- `src/superclaude/cli/install_inventory.py` (edit): list_installed_commands(base_path: Path) and list_all_components(base_path: Path, scope='user'): remove fallbacks at 65-66 and 196-197 and the docstring defaults. Leave uninstall_all (355) alone.
- `src/superclaude/cli/install_settings.py` (edit): check_claude_md_import(base_path: Path, scope='user') and update_claude_md_import(base_path: Path, ...): remove fallbacks 551-552 and 595-596.
- `src/superclaude/cli/install_components.py` (edit): install_component(component, base_path: Path, force=False, scope='user'), install_claude_sc_md(base_path: Path, force=False), install_hooks(base_path: Path, force=False, scope='user'), install_all(base_path: Path, force=False, scope='user'): remove fallbacks at 120-121, 228-229, 278-279, 455-456 and the 'default: ~/.claude' docstring text. The `scope` docstring in install_all says 'or "target"' (stale) - leave.

**Tests**

- tests/unit/test_cli_install.py:90-107 test_list_installed_commands: pass base_path explicitly (install_all(base_path=tmp_path) first, then list_installed_commands(base_path=tmp_path) and assert the installed names), replacing the 'just verify it returns a list' bare call at 96.
- All other tests (test_cli_install, test_init_docs_scaffold, test_install_settings) already pass base_path.

**Doc references**

- Docstring lines 'Base installation path (default: ~/.claude)' in the touched functions

**Collateral**

- Sequence after F19 (install_commands() is deleted there) and merge with F32(c), which rewrites list_installed_commands/list_all_components too
- Changes the public signatures: omitting base_path raises TypeError instead of silently targeting ~/.claude; nothing outside this repo is known to import these (console entry is the only supported surface)
- Path import stays used in every touched module

**Verify**

```bash
uv run pytest tests/unit/test_cli_install.py tests/unit/test_init_docs_scaffold.py tests/unit/test_install_settings.py tests/unit/test_doctor.py -q;  grep -rn "Path.home() / \".claude\"" src/superclaude/cli   # expect only install_paths.get_base_path and main.py:1063;  uv run ruff check src/ tests/;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- Fallback sites: install_paths.py:176-177; install_inventory.py:65-66, 196-197; install_settings.py:551-552, 595-596; install_components.py:120-121, 228-229, 278-279, 455-456 (+ :611 in the legacy shim)
- Programmatic scan of every call to install_component/install_claude_sc_md/install_hooks/install_all/list_installed_commands/list_all_components/check_claude_md_import/update_claude_md_import/_get_target_dir across src, tests, scripts, evals: the only calls lacking base_path are tests/unit/test_cli_install.py:96 and docstring/comment mentions (test_init_docs_scaffold.py:48, install_interactive.py:7, install_paths.py:21)
- Production callers all pass it: main.py:197/222/246/445, install_interactive.py:103/143, install_components.py:124/488/506/523/530/534, install_inventory.py:205/280, install_settings.py:602, verify_drift.py:66, doctor.py:331
- tests/conftest.py:19 has an autouse sandbox_home fixture, so the bare test call currently reads a sandbox HOME, not the developer's

</details>

## F32: duplicated CLI helpers

`shrink` · verdict **modified** · ~55 lines · owner decision: no

Four sub-claims, graded separately. (a) _read_json_safe == _load_settings: CONFIRMED, exactly equivalent (both return {} on missing/invalid/OSError, both let UnicodeDecodeError through, both return a non-dict if the file holds one; _load_settings adds a redundant exists()). (b) _in_git_repo == _has_git: CONFIRMED, identical bodies. (c) README-filtered *.md glob: MODIFIED, the real count is 15 sites not ~12 and one of them (install_paths.shipped_md_names) is already the shared helper; _source_md_names(source_dir) is exactly shipped_md_names(component). Only verify_drift x4, install_inventory x3 and shipped_md_names are worth folding. (d) _get_source_dir -> _get_package_root()/component: TRUE that COMPONENTS[k][0]==k for all 7 rows (verified by importing), but NOT worth doing alone: it leaves a dead tuple column that 3 tests and 2 unpackers still read.

**Changes**

- `src/superclaude/cli/install_mcp.py` (edit): (a) Delete _read_json_safe (258-264) and `import json` (line 8). Add `from .install_settings import _load_settings` and call _load_settings(path) at line 293. install_settings is a leaf (imports only superclaude.utils) so no cycle; install_mcp is imported lazily from main.py and install_inventory.
- `src/superclaude/cli/main.py` (edit): (b) Delete _in_git_repo (34-39). At the one use (line 233) add `from .install_interactive import _has_git` as a function-local import just before it (install_interactive is bound only inside the wizard branch at line 157, so it cannot be reused unqualified) and call _has_git(Path.cwd()). Zero test changes. (Alternative: move the helper to install_paths as in_git_repo and update the two test calls; costs 2 test edits for a cleaner home.)
- `src/superclaude/cli/install_paths.py` (edit): (c) Add `def md_names(directory: Path) -> set: return {f.name for f in directory.glob('*.md') if f.stem.upper() != 'README'}` and make shipped_md_names(component) `return md_names(_get_source_dir(component))`.
- `src/superclaude/cli/verify_drift.py` (edit): (c) Use md_names: line 73-75 -> `source_files = md_names(source_dir)`; 87-92 -> drop the `if target_dir.exists()` guard, `for filename in sorted(md_names(target_dir) - source_files): results[filename] = EXTRA`; 97-113 -> `src_rules = md_names(rules_src)` / `md_names(rules_tgt)`, no exists() guards. Keep the `if not source_dir.exists(): return results` early exit at 69-70.
- `src/superclaude/cli/install_inventory.py` (edit): (c) Delete _source_md_names (141-145); at line 220 use `shipped_md_names(component)` (already imported). Rewrite list_available_commands (35-52) as `return sorted(Path(n).stem for n in md_names(_get_source_dir('commands')))` and list_installed_commands (55-78) likewise over base_path/'commands'/'sc'. Only behavior delta: a file literally named readme.md in commands/ is now excluded the same way install already excludes it.
- `src/superclaude/cli/install_paths.py` (edit): (d) RECOMMEND SKIP. If done anyway: `return _get_package_root() / component` in _get_source_dir (148-162) is ~4 lines saved but leaves COMPONENTS[k][0] decorative; removing the column means editing install_components.py:487, install_inventory.py:203, the 3 tests above and the COMPONENTS comment (20-25) for ~10 lines.

**Tests**

- No existing test pins _read_json_safe, _in_git_repo or _source_md_names; tests/unit/test_verify_drift.py and tests/unit/test_cli_install.py (list/--list-all) cover the md_names call sites.
- If (b) is done via install_paths instead of the private import: update tests/unit/test_install_interactive.py:141 and :146 to the new location.

**Doc references**

- None name these helpers; docs/codex/.../02 module count is unchanged (no file added or removed)

**Collateral**

- md_names lives in install_paths (leaf, no cli imports) so verify_drift/audit chain stays cycle-free
- Do (c) together with F35g: both rewrite list_installed_commands and list_all_components
- Hook scripts (context_loader, session_init, test_runner_hook) intentionally keep their own copies to stay off the cli import path

**Verify**

```bash
uv run pytest tests/unit/test_verify_drift.py tests/unit/test_cli_install.py tests/unit/test_install_interactive.py tests/unit/test_cli_reporting_scope.py -q;  grep -rn "_read_json_safe\|_in_git_repo\|_source_md_names" src tests --include=*.py   # expect none;  uv run ruff check src/ tests/   # catches the now-unused json import;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- (a) install_mcp.py:258-264 vs install_settings.py:39-56; _read_json_safe has exactly one caller, install_mcp.py:293, no test; `json` is imported at install_mcp.py:8 only for this function (lines 262-263), so the import becomes unused
- (b) main.py:34-39 _in_git_repo (one caller, main.py:233) vs install_interactive.py:28-32 _has_git (caller :55; tests/unit/test_install_interactive.py:137-146 call install_interactive._has_git). A third copy sits in scripts/test_runner_hook.py:171 (hook script, should not import cli)
- (c) README-filter sites: verify_drift.py:74, 89, 100, 110; install_inventory.py:49 and 75 (these two use case-sensitive `stem != 'README'`, the rest use .upper()), 145; install_paths.py:53; install_components.py:139, 169 (iterate Paths, leave); audit.py:36, 46, 65 (need stems/Paths, leave); scripts/context_loader.py:515 and scripts/session_init.py:47 (hook scripts, leave)
- (c) Path.glob() on a nonexistent directory returns an empty iterator on py>=3.10 (requires-python >=3.10; checked on 3.13), so the exists() guards in verify_drift.py:87/97-103/108 and in shipped_md_names/_source_md_names are redundant
- (d) COMPONENTS (install_paths.py:27-39): every row has source == key; COMPONENTS[...][0] is also read by tests/integration/test_cross_directory_refs.py:243, tests/unit/test_codex_component_map.py:42, tests/unit/test_verify_drift.py:42; 3-tuple unpacked at install_components.py:487 and install_inventory.py:203
- tests/unit/test_verify_drift.py:22-23 patches install_paths._get_package_root and verify_drift._get_package_root; unaffected as long as _get_source_dir keeps calling _get_package_root() through module globals

</details>

## F34: duplicated hook-ownership predicate

`shrink` · verdict **confirmed** · ~20 lines · owner decision: no

_is_superclaude_inner_hook (install_settings.py:157-172) is line-for-line the loop body of utils.is_superclaude_hook (utils/__init__.py:221-229): command markers, CONSOLE_HOOK_RE/is_legacy_hook_command, inner _comment markers, same order. _is_superclaude_hook (install_settings.py:147-154) is a pure alias with exactly 3 importers (install_components.py:27, install_inventory.py:27, doctor.py:236) plus one internal use (install_settings.py:239) and 2 test import sites.

**Changes**

- `src/superclaude/utils/__init__.py` (edit): Add `def is_superclaude_inner_hook(hook: dict) -> bool` holding the three checks (cmd markers, CONSOLE_HOOK_RE.search(cmd) or is_legacy_hook_command(cmd), hook _comment markers). Rewrite is_superclaude_hook (206-230) as: entry-level _comment marker check, then `return any(is_superclaude_inner_hook(h) for h in hook_entry.get('hooks', []))`. Keep the docstrings' content.
- `src/superclaude/cli/install_settings.py` (delete): Delete _is_superclaude_hook (147-154) and _is_superclaude_inner_hook (157-172). Import is_superclaude_inner_hook from superclaude.utils (line 15-22 block); use it at 186-187 and use is_superclaude_hook (already imported) at 239. CONSOLE_HOOK_RE, SUPERCLAUDE_HOOK_MARKERS, is_legacy_hook_command stay used (120, 183, 336/338).
- `src/superclaude/cli/install_components.py` (edit): Drop `_is_superclaude_hook` from the install_settings import (27); import is_superclaude_hook from superclaude.utils (line 14); line 403 call renamed.
- `src/superclaude/cli/install_inventory.py` (edit): Drop `_is_superclaude_hook` from the install_settings import (27); add is_superclaude_hook to the existing `from superclaude.utils import settings_filename` (line 13); line 105 call renamed.
- `src/superclaude/cli/doctor.py` (edit): Line 236 function-local `from .install_settings import _is_superclaude_hook` -> add is_superclaude_hook to the existing top-level `from superclaude.utils import settings_filename` (line 18); line 264 call renamed.

**Tests**

- tests/unit/test_install_settings.py:15-21 (TestIsSuperclaudeHook setup) and 1140-1144: import is_superclaude_hook from superclaude.utils instead of _is_superclaude_hook from install_settings; update the class docstring at 15 and the prose at 455.
- Optionally add one assertion that is_superclaude_inner_hook({'command': 'superclaude hook x'}) is True and a user command is False, since split-entry ownership (--force must keep a user's sibling command) is the behavior this predicate protects; existing tests already cover it via _split_entry.

**Doc references**

- install_settings.py module docstring is unaffected; no README/ARCHITECTURE mention of either private name

**Collateral**

- install_settings.py comment at 147-153 ('Kept as a name because this module's readers look for it here') documents the alias as deliberate; the owner accepts losing it with this cut
- Hook fast path unaffected: hook_dispatch.py does not import install_settings or doctor
- tests/unit/test_scope_paths.py exercises utils._has_superclaude_hooks via is_superclaude_hook; behavior is unchanged

**Verify**

```bash
grep -rn "_is_superclaude_hook\|_is_superclaude_inner_hook" src tests --include=*.py   # expect none;  uv run pytest tests/unit/test_install_settings.py tests/unit/test_doctor.py tests/unit/test_scope_paths.py tests/unit/test_cli_install.py -q;  uv run ruff check src/ tests/;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- utils/__init__.py:217-230 vs install_settings.py:165-172: identical predicates
- Callers of _is_superclaude_inner_hook: only _split_entry, install_settings.py:186-187; no test references it
- Callers of _is_superclaude_hook: install_components.py:403, install_inventory.py:105, doctor.py:264, install_settings.py:239, tests/unit/test_install_settings.py:19-21 and 1140-1144; no patch()/monkeypatch of either name anywhere
- Historical docs (docs/features/runtime-behavior-audit/03-analysis.md:250, 05b-plan-defect-remediation.md:217) and .claude/insights.jsonl mention the name; they are records, not references to maintain

</details>

## F35e: dead MCP registry keys

`delete` · verdict **confirmed** · ~37 lines · owner decision: no

No MCP_SERVERS entry sets api_key_in_url, api_key_url_param, post_install_note or env, and nothing reads 'required'; the four entries (serena, tavily, playwright, chrome-devtools) set only name, description, category, method, transport/command or plugin fields, and tavily alone sets api_key_env/api_key_description (live). check_prerequisites' selected_servers=None branch is reached only from one test. Extra dead code the audit missed: after the api_key_in_url branch goes, `_mask_secret(command, api_key)` at install_mcp.py:536 can never mask anything (command no longer gains the key), so it simplifies to `command`.

**Changes**

- `src/superclaude/cli/install_mcp.py` (delete): Delete `"required": False,` at lines 47, 60, 71, 78.
- `src/superclaude/cli/install_mcp.py` (edit): install_plugin_server: delete the two post_install_note blocks (410-412 and 432-434, 3 lines each).
- `src/superclaude/cli/install_mcp.py` (edit): install_mcp_server 484-502: collapse to `api_key_env = server_info.get('api_key_env'); if api_key_env: api_key = prompt_for_api_key(...); if api_key: env_args = ['--env', f'{api_key_env}={api_key}']`, deleting the api_key_in_url/api_key_url_param branch (493-499) and the 'elif'. Delete the static-env loop and its comment (518-520). Line 536 -> `safe_command = command`.
- `src/superclaude/cli/install_mcp.py` (edit): check_prerequisites (174-255): signature `selected_servers: List[str]` (no default, no Optional); `needs_node = any(_server_needs_node(s) for s in selected_servers)`; `needs_serena_tooling = 'serena' in selected_servers`; delete the 'With selected_servers=None' docstring sentence (181-183) and the legacy comment (219-220).

**Tests**

- tests/unit/test_install_mcp_prerequisites.py: delete test_no_selection_runs_every_check (about lines 108-117) and its docstring claim. Every other test passes selected_servers explicitly.

**Doc references**

- None: no md describes these registry keys or the None path

**Collateral**

- install_mcp_servers docstring ('None for interactive selection', line 653) is a different parameter and stays
- Adding an mcp-remote style URL-key server later means re-adding the url branch; there is no such server now

**Verify**

```bash
grep -n "api_key_in_url\|api_key_url_param\|post_install_note\|\"required\"\|get(\"env\"" src/superclaude/cli/install_mcp.py   # expect none;  uv run pytest tests/unit/test_install_mcp_prerequisites.py -q;  uv run ruff check src/ tests/;  uv run superclaude mcp --list   # smoke;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- install_mcp.py:33-88 registry: 'required': False at 47, 60, 71, 78 (x4); no other keys of the claimed names
- grep over repo (src, tests, docs, *.md, hooks.json): api_key_in_url, api_key_url_param, post_install_note appear only in install_mcp.py (410, 432, 493, 495); 'required' is read nowhere (only test_version_consistency.py:200, an unrelated tuple name); .get('env') only at install_mcp.py:519
- MCP_SERVERS has no external loader: consumers are install_mcp.py itself, tests/unit/test_install_mcp_prerequisites.py:59 and prose in mcp-authoring.md:122 / mcp/README.md:76, none of which describe these keys
- Sole production call of check_prerequisites passes a list: install_mcp.py:729; the None path is exercised only by tests/unit/test_install_mcp_prerequisites.py:112 (test_no_selection_runs_every_check)
- No tests/unit/test_install_mcp.py exists (only a stale .pyc), so no test pins install_mcp_server or install_plugin_server

</details>

## F35l: dead returns and params

`delete` · verdict **confirmed** · ~20 lines · owner decision: no

All three are dead. (a) _maybe_git_init returns True in every branch (install_interactive.py:54, 56, 84, 87, 90, 93), and the caller discards the note (`proceed, _note`, line 122) and tests the always-true `proceed` (123-125). (b) update_claude_md_import(force=) has one caller, install_components.py:534, which passes force=False; no test or doc calls it. (c) install_hooks initialises `skipped = 0` and never increments it (251-347), so hooks_skipped in install_all (506, 510, 515-516) is always 0.

**Changes**

- `src/superclaude/cli/install_interactive.py` (edit): (a) _maybe_git_init -> `-> None`, bare `return` in the two early exits, drop the returned notes in the three try/except/else tails (keep every click.echo), docstring 'Returns' sentence removed; remove `Tuple` from the typing import (line 14). In run_interactive_install replace lines 122-125 with a bare `_maybe_git_init(scope, project_root)`.
- `src/superclaude/cli/install_settings.py` (edit): (b) update_claude_md_import(base_path, scope='user'): remove the `force` parameter and docstring line 589; `if has_import: return True, status`; delete the `if force:` block (611-615 incl. comment).
- `src/superclaude/cli/install_components.py` (edit): (b) call at 534-536 becomes update_claude_md_import(base_path, scope=scope). (c) Smallest cut: in install_all drop `total_skipped += hooks_skipped` (510) and the `if hooks_skipped > 0:` block (515-516), and bind the unused element as `_` at 506. Keep install_hooks' 4-tuple so 11 test unpackings do not change. Optional larger cut: make install_hooks return a 3-tuple, delete `skipped = 0` and update the 11 test sites (not recommended: ~8 lines saved for 11 test edits).

**Tests**

- tests/unit/test_install_interactive.py: no change needed for (a); the existing TestGitInitPrompt cases keep passing because every echoed string is kept.
- tests/unit/test_cli_install.py: no change for (b) or the recommended form of (c).

**Doc references**

- None name these return shapes

**Collateral**

- install_interactive.py:62 prints 'Local scope writes a .gitignore block ... Without git, the block is written but untracked', which is stale (it writes .git/info/exclude, and without git add_git_exclude skips with 'Not a git repository'). Not over-engineering, so not part of this cut, but touch-adjacent: fix the wording in the same file if the owner wants
- Tuple import in install_components.py is still used by other signatures

**Verify**

```bash
grep -n "proceed\|_note\|hooks_skipped\|force=False" src/superclaude/cli/install_interactive.py src/superclaude/cli/install_components.py src/superclaude/cli/install_settings.py   # expect no proceed/_note/hooks_skipped and no force=False;  uv run pytest tests/unit/test_install_interactive.py tests/unit/test_cli_install.py tests/unit/test_install_settings.py -q;  uv run ruff check src/ tests/;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- install_interactive.py:48-93 all six return statements are (True, ...); only caller is run_interactive_install:122; no test references _maybe_git_init (tests drive it through the wizard and assert only the printed 'Git check' / 'Skipped git init' text and the git init subprocess call)
- install_settings.py:581-615: force used only at 604 (`if has_import and not force`) and 612-615 (the re.sub strip block); repo-wide grep of update_claude_md_import: install_components.py:32/534 and its definition only
- install_components.py:253 return type Tuple[int,int,int,List[str]]; `skipped` only assigned at 285; 11 test sites unpack the 4-tuple (test_cli_install.py:349, 372, 390, 838, 866, 950, 969, 986, 1008; others call without unpacking)

</details>

## F21: doctor Configuration check

`delete` · verdict **confirmed** · ~61 lines · owner decision: no

doctor's `_check_configuration` cannot fail: doctor.py:17 does `from superclaude import __version__` at module top, so a broken import dies before run_doctor exists, and an ImportError inside the function is unreachable. The pytest-plugin check (doctor.py:80-124) can also shrink to one importlib.metadata.entry_points(group='pytest11') lookup, at the price of a narrower guarantee (it checks the entry point is registered, no longer that every pytest11 plugin imports).

**Changes**

- `src/superclaude/cli/doctor.py` (delete): Delete the `_check_configuration()` entry at line 65 and the function at lines 127-152 (def through the blank lines after the except branch). `__version__` import at :17 stays (used by _check_console_entry).
- `src/superclaude/cli/doctor.py` (edit): Replace the body of `_check_pytest_plugin` (lines 80-124, ~45 lines) with ~10 lines: `from importlib.metadata import entry_points`; `found = any(ep.value.split('.')[0] == 'superclaude' for ep in entry_points(group='pytest11'))`; return the same {'name': 'pytest plugin loaded', 'passed': found, 'details': [...]} dicts for the pass/fail messages. Keep the check name so tests/CLI output stay stable.
- `src/superclaude/cli/main.py` (edit): doctor docstring line 471: delete the bullet '- Configuration files present' (already inaccurate: the check only imported the package).
- `tests/unit/test_doctor.py` (edit): Line 186: remove 'Configuration' from the `environment` set; docstring at 185 'the other three read the env' -> 'the other two'. Line 223: `== 6` -> `== 5`. Module docstring (lines 3-7) is historical narrative about the 4/6 score and can stay.

**Tests**

- tests/unit/test_doctor.py::TestRunDoctor::_disk_checks (docstring + set) and ::test_reports_every_check (== 6 -> == 5) -> update.
- tests/unit/test_cli_reporting_scope.py::TestDoctorResolvesTheInstall::test_is_healthy_on_a_correct_install -> unchanged; it runs the real doctor and must still be green with the entry_points check (needs an editable/installed superclaude, which `uv pip install -e .[dev]` provides).
- No test targets the pytest-plugin check directly; optionally add none (restraint).

**Doc references**

- src/superclaude/cli/main.py:471 (doctor docstring bullet)
- README.md:126 lists doctor as 'pytest plugin, hooks, CLAUDE_SC import, `superclaude` on PATH' -> already omits Configuration, no change.
- src/superclaude/cli/doctor.py:3-9 module docstring says 'four of the six' (historical narrative; leave)

**Collateral**

- No .py file added/removed -> codex module-count test unaffected.
- doctor output loses the verbose 'SuperClaude &lt;version> installed correctly' line; the version is still reported by `superclaude --version` and by the 'superclaude on PATH' check.
- Hooks/registry/install_settings: not involved. tests/unit/scripts not involved.

**Verify**

```bash
uv run pytest tests/unit/test_doctor.py tests/unit/test_cli_reporting_scope.py  # then full `uv run pytest` exit 0
uv run ruff check src/ tests/
uv run superclaude doctor --verbose  # 5 checks, 'pytest plugin loaded' passes
grep -rIn '_check_configuration\|"Configuration"' src tests  # expect no hits
```

<details><summary>Evidence</summary>

- doctor.py:17 `from superclaude import __version__` (module top, also used at :201,207) and main.py:13 imports the same name; doctor is only reachable through main.py. `_check_configuration` (127-150) does `import superclaude; superclaude.__version__` inside try/except ImportError -> never takes the failure branch.
- doctor.py:64-65 lists both `_check_pytest_plugin()` and `_check_configuration()` in run_doctor's checks list; the check's only visible output is the verbose line 'SuperClaude {version} installed correctly'.
- Read-only comparison with .venv python: importlib.metadata.entry_points(group='pytest11') -> [asyncio, benchmark, pytest_cov, superclaude -> superclaude.pytest_plugin]; the current check (pytest.Config.fromdictargs({}, []).pluginmanager.list_plugin_distinfo()) returns the same 4 but imports pytest_asyncio, pytest_benchmark, pytest_cov and superclaude.pytest_plugin to do it.
- pytest is a hard dependency (pyproject.toml dependencies: pytest>=7.0.0) and requires-python >=3.10 (entry_points(group=...) is available), so the `except ImportError: 'pytest not installed'` branch (doctor.py:~117-123) is unreachable in a valid install.
- tests/unit/test_doctor.py:186 `environment = {'pytest plugin loaded', 'Configuration', 'superclaude on PATH'}` and :223 `assert len(result['checks']) == 6`; no test imports `_check_pytest_plugin` or `_check_configuration` directly (grep).
- CI: .github/workflows/test.yml:163 runs `superclaude doctor --verbose --scope user`; plugin loading is separately verified at test.yml:124-125 (`pytest --trace-config | grep superclaude`), so the entry_points shrink does not remove the only plugin-load check in CI.

</details>

## F25: `mcp --status`

`delete` · verdict **modified** · ~56 lines · owner decision: no

`superclaude mcp --status` (show_mcp_status) has 0 tests and no docs beyond the --help example, and `mcp --list` already prints per-server install state, so the cut is safe. Correction: --status is not a strict subset of --list: it adds a 'Fallback' column and an 'N/M servers active' line. That column is already wrong for chrome-devtools (see evidence), and the same fallback data lives in hooks/mcp_fallback.py and surfaces through context_loader hints.

**Changes**

- `src/superclaude/cli/install_mcp.py` (delete): Delete lines 600-643 (`def show_mcp_status` through its last echo at 641 plus the two blank lines) so `def install_mcp_servers` (644) follows 2 blank lines after list_available_servers.
- `src/superclaude/cli/main.py` (edit): Delete the `--status` option (359-364), drop `show_status` from the signature at 376 (`def mcp(servers, list_only, scope, dry_run)`), delete docstring line 382 (`superclaude mcp --status`), delete `show_mcp_status,` at 390 from the import tuple, and delete the `if show_status:` branch 397-400.

**Tests**

- None exist for show_mcp_status or `mcp --status`; nothing to delete.
- tests/unit/test_install_mcp_prerequisites.py and tests/unit/test_mcp_fallback.py -> unaffected.

**Doc references**

- src/superclaude/cli/main.py:382 (docstring example) - only reference
- src/superclaude/cli/install_mcp.py:640-641 hint text goes away with the function (it was the only place suggesting 'choose 0 for all core servers').

**Collateral**

- No .py file added/removed -> codex module-count test unaffected.
- Hooks/registry/install_settings: not involved; hooks/mcp_fallback.py keeps MCP_FALLBACKS.
- Interacts with F31: both edit install_mcp.py (600-643 vs 672-723) and main.py's `mcp` command; apply F25 after F31 or bottom-up to keep line numbers valid.

**Verify**

```bash
uv run pytest  # exit 0
uv run ruff check src/ tests/
grep -rIn 'show_mcp_status\|mcp --status\|show_status' src tests README.md docs --exclude-dir=archive --exclude-dir=__pycache__  # expect no hits
uv run superclaude mcp --status; echo $?  # expect 'No such option' (exit 2)
uv run superclaude mcp --list  # still works
```

<details><summary>Evidence</summary>

- install_mcp.py:600-641 show_mcp_status; install_mcp.py:558-597 list_available_servers prints name, '✅ installed / ⬜ not installed', description and required API key per category. --status prints name, Active/—, Fallback, and a count.
- Fallback lookup `name.lower().replace('-', '')` (install_mcp.py:~626): MCP_FALLBACKS keys are context7, tavily, serena, playwright, devtools (hooks/mcp_fallback.py:30-36). For chrome-devtools the key becomes 'chromedevtools' (verified with python: False), so --status prints 'Native' for it instead of the Playwright fallback. The column is already wrong for 1 of 4 registered servers.
- grep show_mcp_status -> install_mcp.py:600 (def), main.py:390 (import), main.py:398 (call). grep '--status' / 'mcp --status' in README, docs (minus archive), tests, Makefile, .github -> only main.py:382 (docstring example). tests: no CliRunner call of `mcp` at all and no test of show_mcp_status.
- MCP_FALLBACKS stays live: hooks/mcp_fallback.py:79,146, scripts/context_loader.py:42,728, tests/unit/test_mcp_fallback.py:145-156,279-282. Only install_mcp.py:605-607 (the deleted function) reads it from the CLI side.
- README.md:112-117 and :358-364 document `mcp`, `--list`, `--servers`, `--scope`; `--status` is not documented.

</details>
