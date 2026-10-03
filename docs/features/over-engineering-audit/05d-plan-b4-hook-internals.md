---
status: complete
revised: 2026-10-03
---

# B4: Hook and script internals

Item specs for batch B4. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b4). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F10: hooks/hook_tracker.py

`delete` · verdict **confirmed** · ~630 lines · owner decision: no

hook_tracker.py is dead weight: nothing ever writes hook_executions.json, so cleanup_old_sessions always returns 0. Its only live consumer is the session_id-is-None arm in mcp_fallback, which never fires in production because the CC stdin session_id is always passed. One refinement: the cached id is not permanent. current_session.txt is swept after 7 days by prune_hook_state, so it rotates weekly at best, which a constant 'default' plus prune_fallback_ledger's 7-day age expiry reproduces.

**Changes**

- `src/superclaude/hooks/hook_tracker.py` (delete): Delete the file (196 lines).
- `src/superclaude/scripts/session_init.py` (edit): Delete init_hook_tracker (lines 64-86 incl. trailing blanks). In main() delete lines 287-289 ('# 1. Initialize hook tracker' comment + call + blank); optionally renumber the '# 2..# 6' comments. Delete module-docstring lines 7-9 ('v2.1.0 Features: Hook session tracking initialization / Old session cleanup (>24h)'). `sys` stays in use (sys.exit).
- `src/superclaude/hooks/mcp_fallback.py` (edit): Line 23: delete the hook_tracker import. Line 57: delete `_ensure_tracker_dir()` (atomic_write_json already does path.parent.mkdir(parents=True, exist_ok=True), utils:44). Lines 81-82: replace `if session_id is None: session_id = get_session_id()` with `session_id = session_id or "default"`. Docstring lines 4 and 14-15 and the arg doc at ~71-73: drop the hook_tracker mentions. Land together with F33, which rewrites the same function.
- `src/superclaude/hooks/hooks.json` (edit): Line 10 session_init _comment: drop 'hook session tracking, cleanup of sessions older than 24h,'. Keep the '[superclaude]' marker. Registration count and commands are unchanged.
- `src/superclaude/hooks/__init__.py` (edit): The _LAZY, TYPE_CHECKING and __all__ entries for get_session_id and cleanup_old_sessions point at the deleted module, so this file must change in the same commit. Do it as F27 (docstring-only __init__).
- `src/superclaude/utils/__init__.py` (edit): Keep the 'hook_executions' and 'current_session' prefixes in _PRUNABLE_PREFIXES for one release as the upgrade sweep for orphan files. Change the comment at :414 to 'orphan from removed hook_tracker; drop after one release'. Removing them now would strand current_session.txt on every existing install.
- `src/superclaude/scripts/README.md` (edit): Delete line 39 (`hooks/hook_tracker.py` related-file bullet).
- `src/superclaude/ARCHITECTURE.md` (edit): Line 86: remove 'hook tracker,' from the ephemeral-state list.
- `docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md` (edit): Line 71: remove 'tracker,' from 'context cache, tracker, loop counter, fallback ledger'.
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): Section 1 '전체 Python module' count -1 (57 -> 56 alone; 54 if F07-b and F14 also land).

**Tests**

- tests/unit/test_hook_tracker.py: delete the whole file (243 lines).
- tests/unit/test_hooks.py: delete class TestHookTracker (lines 14-52). Then remove the now-unused imports `Path`, `patch` and `pytest` (lines 8, 9, 11; TestInlineHooks uses none). Update the module docstring line 3.
- tests/unit/test_session_init.py: delete class TestInitHookTracker (lines 40-110, banner comment included). Remove `init_hook_tracker` from the import (line 20) and `MagicMock` from line 12 (unused after). Remove the 3-line `patch("superclaude.scripts.session_init.init_hook_tracker", return_value=None),` block from each TestMain test (around lines 444, 465, 489, 514, 536); they would raise AttributeError otherwise.
- tests/unit/test_mcp_fallback.py: in both temp_fallback_dir fixtures (lines ~21-33 and ~168-178) delete the two `patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR"...)` and `...SESSION_FILE...` patches. Keep the MCP_FALLBACK_FILE patch.
- tests/conftest.py: delete line 42 (`import superclaude.hooks.hook_tracker as hook_tracker`) and lines 47-53 (the three setattr calls on hook_tracker). Keep the mcp_fallback setattr.
- tests/unit/test_scope_paths.py:393-420 (test_the_sweep_collects_the_tracker_file): KEEP; it now pins the upgrade sweep. Refresh the class docstring to say the file is an orphan from a removed module.

**Doc references**

- src/superclaude/scripts/README.md:39
- src/superclaude/ARCHITECTURE.md:86
- docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:71
- src/superclaude/hooks/hooks.json:10
- src/superclaude/scripts/session_init.py:7-9
- src/superclaude/hooks/mcp_fallback.py:4,14-15,71-73
- src/superclaude/utils/__init__.py:414
- .claude/rules/gotchas/hooks.md:11 and docs/features/runtime-behavior-audit/* name hook_tracker as a dated historical fix: leave as record.

**Collateral**

- Module-count trap: one .py removed, so recompute the count in 02_component_and_delivery_map.md section 1 or test_documented_count_matches_source goes red.
- hooks.json is edited only in a _comment string: no change to the HOOKS registry or to install_settings marker handling. Non-force installs keep the old comment text, which is harmless.
- On-disk state: no migration. The orphan current_session.txt (and any hook_executions.json) is reaped by prune_hook_state after 7 days. Old ledger keys age out via prune_fallback_ledger.
- Behavior change: the id-less fallback key becomes the constant 'default' instead of the random cached id. Only manual runs and tests hit it. The shared-across-projects property in a user-scope state dir is unchanged, since current_session.txt was shared too.
- Import-time side effects shrink: the module-level hook_state_dir() and the SUPERCLAUDE_SESSION_TTL int() parse disappear from every context_loader run.
- Order with F27 and F33: land F10, F27 and F33 in one commit; mcp_fallback.py and hooks/__init__.py are touched by all three.

**Verify**

```bash
uv run pytest   # must exit 0
uv run ruff check src/ tests/
grep -rnE "hook_tracker|get_session_id|cleanup_old_sessions|init_hook_tracker|HookExecution|SUPERCLAUDE_SESSION_TTL|HOOK_TRACKER|_ensure_tracker_dir" src tests   # only the intentional utils/__init__.py:414 orphan-sweep comment remains
uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"   # matches section 1 of 02_component_and_delivery_map.md
```

<details><summary>Evidence</summary>

- hook_tracker.py: `_save_tracker_data` is called only at line ~195 inside cleanup_old_sessions, which loaded the same data (_load_tracker_data) just before. Nothing else in src writes the file. HookExecution( is constructed only in _load_tracker_data (line 106) and tests/unit/test_hook_tracker.py. SessionData is the same.
- On disk here, .claude/.superclaude_hooks/ holds current_session.txt (written by init_hook_tracker at every SessionStart) but NO hook_executions.json.
- SUPERCLAUDE_SESSION_TTL appears only at hook_tracker.py:26 (no docs, no tests, no Makefile).
- get_session_id callers: mcp_fallback.py:82 (fallback arm) and session_init.py:82 (return value discarded by main() at :288). cleanup_old_sessions caller: session_init.py:77 only.
- context_loader.py:1115-1128 _extract_session_id reads CC stdin session_id and passes it to check_mcp_and_notify at :729 and :938. The live ledger .claude/.superclaude_hooks/mcp_fallbacks.json holds only CC UUID keys (6c865169-..., 935e8402-...), never the 16-hex cached id fe4871fd28680e3f from current_session.txt, so the fallback arm is unused in prod.
- The env arm of get_session_id reads CLAUDE_SESSION_ID. This session's env has CLAUDE_CODE_SESSION_ID and no CLAUDE_SESSION_ID. Only the Bash tool env was inspected, not a hook process env.
- No registry or doc invokes the module: absent from hooks.json, HOOKS and pyproject. Mentioned in src/superclaude/scripts/README.md:39, ARCHITECTURE.md:86, docs/codex/.../04_runtime_and_distribution_playbook.md:71, and dated historical docs under docs/features/runtime-behavior-audit and docs/research.
- utils/__init__.py:411-419 _PRUNABLE_PREFIXES lists 'hook_executions' (:414) and 'current_session' (:415). prune_hook_state runs from context_reset.py:48 at SessionStart, so orphan files on existing installs are reaped after 7 days with no migration code.

</details>

## F27: hooks/__init__.py lazy re-exports

`yagni` · verdict **confirmed** · ~39 lines · owner decision: no

No code anywhere imports get_session_id, cleanup_old_sessions or parse_frontmatter from the package root; every importer uses the submodule. The PEP 562 lazy re-export machinery in hooks/__init__.py is unused, and no test pins it. A docstring-only __init__ keeps the perf property it was added for (importing one submodule loads no other).

**Changes**

- `src/superclaude/hooks/__init__.py` (edit): Replace the whole file (49 lines) with a docstring only, ~8 lines: 'SuperClaude hooks package: inline_hooks (frontmatter parsing) and mcp_fallback (once-per-session MCP hints). Import the submodule directly. This file deliberately re-exports nothing: it runs before any submodule, so an eager re-export would make mcp_fallback (every prompt) load inline_hooks -> yaml.' Delete TYPE_CHECKING, __all__, _LAZY, __getattr__ and __dir__.

**Tests**

- No test touches the package root, so none to delete or update.
- tests/unit/test_hook_dispatch.py:199 (no click/yaml on the hook path) should be re-run to prove the lazy property survives.

**Doc references**

- src/superclaude/hooks/__init__.py:1-14 (the docstring itself is rewritten)

**Collateral**

- No .py file added or removed, so no module-count change.
- Subtle: a docstring-only __init__ is still imported first, so no re-export is the only thing keeping `import superclaude.hooks.mcp_fallback` free of yaml. Do not later add an eager import here.
- Land with F10 and F33.

**Verify**

```bash
uv run pytest   # must exit 0 (test_hook_dispatch.py covers the no-yaml fast path)
uv run ruff check src/ tests/
uv run python -c "import sys, superclaude.hooks.mcp_fallback; assert 'yaml' not in sys.modules; print('ok')"
grep -rnE "_LAZY|__getattr__" src/superclaude/hooks/__init__.py   # no output
```

<details><summary>Evidence</summary>

- Whole-repo grep for `from superclaude.hooks import`, `import superclaude.hooks`, `superclaude.hooks.get_session_id`, `hooks.cleanup_old_sessions` and `hooks.parse_frontmatter` across *.py, *.md, *.toml and *.json (excluding archive): zero hits. Every importer uses a submodule: cli/main.py:14 and tests/unit/test_hooks.py:58,72,89 use inline_hooks, and context_loader.py:42 plus install_mcp.py:605 use mcp_fallback.
- No test references _LAZY, hooks.__all__ or __getattr__ on the package. The only yaml assertion is test_hook_dispatch.py:199, which a docstring-only __init__ also satisfies.
- Commit c4c6b83 added the laziness as a perf fix (62.8 -> 41.4 ms per prompt) and says: 'No caller imports these names from the package ... the names are kept only to preserve the documented API.' No md or doc in the repo documents such an API.
- Hard dependency on F10: two of the three _LAZY entries (hooks/__init__.py:32-33) and the TYPE_CHECKING import (:20) point at hook_tracker, which F10 deletes. __init__ must change in the same commit regardless.

</details>

## F33: mcp_fallback surplus

`delete` · verdict **confirmed** · ~135 lines · owner decision: yes (see README)

All five surplus items hold. get_fallback_for is called only by tests. format_fallback_notification and should_notify_fallback each have exactly one src caller (check_mcp_and_notify) and can be inlined. `_ensure_tracker_dir()` in _save_fallback_data is redundant because atomic_write_json already mkdirs. utils.CURRENT_MCP_SERVERS duplicates MCP_FALLBACKS keys (both are {context7, tavily, serena, playwright, devtools} today). The CURRENT_MCP_SERVERS removal reverses a documented design choice and needs a call-time import, so it is separable.

**Decision:** Only for the CURRENT_MCP_SERVERS sub-cut: it overrides the declared design in utils/__init__.py:425-428 ('stays dependency-free', with an equality test as the guard) in favor of a call-time import of MCP_FALLBACKS in prune_fallback_ledger. Accept the lazy import, or keep the constant and its test and drop only that sub-cut (the other four F33 items need no decision).

**Changes**

- `src/superclaude/hooks/mcp_fallback.py` (edit): Delete get_fallback_for (137-146) and format_fallback_notification (100-113). Collapse should_notify_fallback (64-97) into check_mcp_and_notify, roughly:
  session_id = session_id or "default"   # F10
  data = _load_fallback_data(); seen = data.setdefault(session_id, {})
  mcp_lower = mcp_name.lower()
  if mcp_lower in seen: return None
  seen[mcp_lower] = datetime.now().isoformat(); _save_fallback_data(data)
  return f"ℹ️ If {mcp_name} MCP is unavailable, fall back to: {MCP_FALLBACKS.get(mcp_lower, 'Native')}"
Keep the conditional wording and its docstring note ('the hook cannot check availability'). In _save_fallback_data delete `_ensure_tracker_dir()` (:57). Net -~50 lines.
- `src/superclaude/utils/__init__.py` (edit): Delete CURRENT_MCP_SERVERS and its 4-line comment (lines 425-432). In prune_fallback_ledger (~:509) replace `server in CURRENT_MCP_SERVERS` with `server in MCP_FALLBACKS`, with `from superclaude.hooks.mcp_fallback import MCP_FALLBACKS` as the first line of the function body. Only if the decision below is yes.

**Tests**

- tests/unit/test_mcp_fallback.py: delete test_should_notify_fallback_first_time (36-43), test_should_notify_fallback_second_time (44-55), test_format_fallback_notification (68-76), test_get_fallback_for_known_mcp (91-104), test_get_fallback_for_unknown_mcp (105-110) and test_session_id_passthrough_rotates_per_session (111-123, duplicate of test_check_mcp_and_notify_passes_session_id at 124-131). The first/second-time behavior stays covered by test_check_mcp_and_notify_returns_message (77-90).
- tests/unit/test_mcp_fallback.py: convert test_different_mcps_tracked_separately (56-67) and test_case_insensitive_mcp_names (132-142) to call check_mcp_and_notify (assert is not None / is None). Add `assert 'Tavily/WebSearch' in msg` to the context7 first-call test to keep the fallback-text check.
- tests/unit/test_mcp_fallback.py: delete test_roster_matches_the_fallback_table (273-282) if CURRENT_MCP_SERVERS is cut. The retired-server prune tests (241-270) must keep passing, since they now read MCP_FALLBACKS.
- The fixture patch changes are listed under F10.

**Doc references**

- src/superclaude/hooks/mcp_fallback.py docstring lines 1-16 ('Uses same session infrastructure as hook_tracker.py' and the get_session_id mention)
- utils/__init__.py:425-428 comment (goes with the constant)

**Collateral**

- No .py added or removed, so no module-count change.
- Behavior unchanged for production paths. The only visible difference: check_mcp_and_notify on an unknown name still returns the hint with 'Native', exactly as before.
- Tests lose the should_notify_fallback tuple seam; ~6 tests deleted or converted. Net test change is about -70 lines.
- Must land with F10 (shared import line and session_id fallback) and F27 (shared package).
- Hook-path scope: MCP_FALLBACK_FILE stays a module-level hook_state_dir() constant. tests/conftest.py still re-points it; that setattr must stay.

**Verify**

```bash
uv run pytest   # must exit 0
uv run ruff check src/ tests/
grep -rnE "get_fallback_for|format_fallback_notification|should_notify_fallback|_ensure_tracker_dir|CURRENT_MCP_SERVERS" src tests   # no output (or only CURRENT_MCP_SERVERS if that sub-cut is declined)
uv run pytest tests/unit/test_mcp_fallback.py tests/unit/test_scope_paths.py -q
```

<details><summary>Evidence</summary>

- Whole-repo grep: get_fallback_for is referenced only at tests/unit/test_mcp_fallback.py:91-109. should_notify_fallback and format_fallback_notification are called only from check_mcp_and_notify (mcp_fallback.py:116-134) plus tests/unit/test_mcp_fallback.py (should_notify_fallback at 36-65, 111-141; format_fallback_notification at 68-75).
- Production callers go through check_mcp_and_notify only: context_loader.py:729 (guarded by `if mcp_name in MCP_FALLBACKS`) and :938. So the 'Native' default for unknown names is never reached in prod.
- utils/__init__.py:44 atomic_write_json does path.parent.mkdir(parents=True, exist_ok=True), so mcp_fallback.py:57 `_ensure_tracker_dir()` is redundant. The import of it (line 23) goes away with F10.
- utils/__init__.py:425-431 CURRENT_MCP_SERVERS is used once, at :509 in prune_fallback_ledger. Its comment says it is 'kept here rather than imported from superclaude.hooks.mcp_fallback so this module stays dependency-free, and asserted equal by the test suite'. The equality test is tests/unit/test_mcp_fallback.py:273-282.
- mcp_fallback.py already imports from superclaude.utils (line 24), so utils cannot import it at module level (cycle). A call-time import inside prune_fallback_ledger works: prune_fallback_ledger is called only from context_reset.py:49, and context_loader already imports mcp_fallback on every prompt.
- Current sizes: should_notify_fallback 64-97, format_fallback_notification 100-113, check_mcp_and_notify 116-134, get_fallback_for 137-146.

</details>

## F35a: session_init multi-dir CLAUDE.md count

`delete` · verdict **confirmed** · ~126 lines · owner decision: no

get_additional_dirs_status (session_init.py:252-278) counts CLAUDE.md files under the hardcoded globs packages/*, apps/*, libs/*, services/*. It prints only when CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 is set. That variable is a Claude Code opt-in for CLAUDE.md in --add-dir directories (from memory, not verified here), which is unrelated to the monorepo globs the function scans, so the line is both opt-in and misleading. One caller (main :298-301), no doc mentions it beyond the module docstring.

**Changes**

- `src/superclaude/scripts/session_init.py` (delete): Delete get_additional_dirs_status (:252-279). In main() delete the '# 4. Check for additional directories' block (:298-301 plus blank). Docstring :11-13: delete the 'v2.2.0 Features' block entirely.

**Tests**

- tests/unit/test_session_init.py: delete class TestGetAdditionalDirsStatus with its banner (:362-430).
- Delete TestMain.test_main_prints_additional_dirs_when_present (:532-551) and the `patch('...get_additional_dirs_status', ...)` lines in the remaining TestMain tests (:451-454, :521-524). Remove `get_additional_dirs_status` from the import (:17) and update the module docstring (:5-6).

**Doc references**

- src/superclaude/scripts/session_init.py:11-13
- tests/unit/test_session_init.py:1-6 (module docstring)

**Collateral**

- No .py added or removed. Do this in the same session_init commit as F12, F35b and F35m.e (shared TestMain edits).
- No count test or README line mentions the multi-dir line.

**Verify**

```bash
uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rn "ADDITIONAL_DIRECTORIES\|Multi-dir\|get_additional_dirs_status" src tests (expect none).
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/session_init.py:252-278 (function), :298-301 (caller), :13 (docstring 'Multi-directory CLAUDE.md awareness').
- Whole-repo grep for ADDITIONAL_DIRECTORIES_CLAUDE_MD|Multi-dir|get_additional_dirs_status: only session_init.py and tests/unit/test_session_init.py. No md/doc/README/hooks.json/settings reference.
- The 2026-08 hook-performance analysis counted this scan among the unattributed ~250ms of session_init (docs/archive/features/hook-performance/03-analysis.md:224-236); it is gated by the env var so default sessions never run it.

</details>

## F35m.e: /context reminder print

`delete` · verdict **confirmed** · ~3 lines · owner decision: no

The static `print('💡 Use /context to confirm token budget.')` in session_init.main (:303-304) is a no-op for the model. /context is a user slash command the model cannot run, and no test pins the string (grep: only session_init.py and the unrelated command doc commands/agent.md:21). Delete it with the other session_init cuts.

**Changes**

- `src/superclaude/scripts/session_init.py` (delete): Delete the '# 5. Remind token budget' comment and print (:303-304 plus blank) and renumber the install-status comment.
- `src/superclaude/commands/agent.md` (edit): Optional: drop `- Remind: 💡 Use /context to confirm token budget` (:21). Not required, since it is the command's own instruction.

**Tests**

- None: no test asserts the line.

**Doc references**

- src/superclaude/commands/agent.md:21 (optional)

**Collateral**

- No .py added or removed. Same session_init commit as F12, F35a and F35b.

**Verify**

```bash
uv run pytest tests/unit/test_session_init.py && uv run pytest ; grep -rn 'confirm token budget' src tests (expect none, or only agent.md if left).
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/session_init.py:303-304.
- grep 'confirm token budget' over src, tests, docs: session_init.py:304 and commands/agent.md:21 (the command's own startup list, independent of the hook).

</details>

## F35d: loop_guard hand-rolled atomic write

`shrink` · verdict **modified** · ~27 lines · owner decision: no

All three loop_guard shrinks hold, with two caveats. (1) _save_state (:62-87) hand-rolls atomic_write_json, but it must stay as a 4-line fail-open wrapper because _handle_post calls it and tests/unit/test_safety_hooks.py calls it directly. atomic_write_json(path, data, indent=2) works with indent=None at runtime (the annotation says int and no mypy gate runs). Perf stays neutral: loop_guard already imports superclaude.utils, and tempfile is imported lazily inside atomic_write_json. (2) The NotebookEdit and generic arms in _input_fingerprint (:96-99) are unreachable under the shipped Edit|Write|Bash matcher (both Pre and Post in hooks.json:103, :134), but the generic arm would matter if someone hand-registers loop_guard on a broader matcher. `kind` is always 'error' (:151 appends it, :169-170 filters on it; git history shows only the initial commit ever wrote it).

**Changes**

- `src/superclaude/scripts/loop_guard.py` (edit): Import `atomic_write_json` alongside hook_state_dir and project_key (:24). Replace _save_state :62-87 with: `try: atomic_write_json(path, state, indent=None)` / `except OSError: pass  # fail open`. Delete the tempfile comment :26-29. `os` stays (main() uses os.environ).
- `src/superclaude/scripts/loop_guard.py` (edit): _input_fingerprint :94-100: after the isinstance guard, `key = 'command' if tool_name == 'Bash' else 'file_path'; return str(tool_input.get(key, '')).strip()[:120]`. Optional: drop `kind` (:151 `entries.append({'signature': sig, 'ts': now})`, :169-170 count on signature only). Entries already on disk have kind='error' and keep counting.
- `src/superclaude/utils/__init__.py` (edit): Optional tidy: line 30 `indent: int | None = 2` so the None call matches its annotation.

**Tests**

- tests/unit/test_safety_hooks.py:201: change glob('.loop_guard_*') to glob('*.tmp'), or assert `list(p.parent.iterdir()) == [p]`, so test_no_temp_file_left_behind keeps meaning something. Other TestLoopGuardAtomicWrite tests stay.
- tests/unit/test_loop_guard.py:243, :260 and test_safety_hooks.py:194, :207, :210: the 'kind' keys are optional cleanup (extra keys are harmless).
- Optional new test: a PostToolUse failure for tool 'Grep' does not collapse into one shared signature.

**Doc references**

- tests/unit/test_safety_hooks.py:8 docstring ('loop_guard._save_state atomic write') stays accurate

**Collateral**

- No .py added or removed. hooks.json, registry and install_settings are untouched.
- If a user hand-registers loop_guard on a broader matcher, removing the generic arm makes every non-Bash tool without file_path share one signature (for example 'Grep::'), which can false-block after 5 errors. Acceptable only because the shipped matcher is fixed.
- The state file keeps the name loop_guard_&lt;key>.json, so _PRUNABLE_PREFIXES is unaffected. Stray .tmp files after a hard crash were never pruned either.

**Verify**

```bash
uv run pytest tests/unit/test_loop_guard.py tests/unit/test_safety_hooks.py && uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; echo '{"hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{"command":"x"},"tool_response":{"exit_code":1}}' | superclaude hook loop_guard then confirm the state file is a single compact JSON line.
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/loop_guard.py:62-87 vs src/superclaude/utils/__init__.py:30-58: same temp file in the same dir plus os.replace, UTF-8, mkstemp. atomic_write_json adds newline='\n' and BaseException cleanup. Compact JSON has no newlines, so the on-disk bytes are identical with indent=None.
- Only the tmp prefix differs: loop_guard uses '.loop_guard_*.tmp', atomic_write_json uses 'tmp*.tmp'. tests/unit/test_safety_hooks.py:201 globs '.loop_guard_*' and would pass vacuously after the change.
- hooks.json:103 and :134 matcher 'Edit|Write|Bash'. NotebookEdit's input key is notebook_path, so its arm returned '' even if reached.
- tests/unit/test_loop_guard.py only seeds 'kind': 'error' (:243, :260). `grep _input_fingerprint tests` finds no direct test.
- Archived hook-performance plan lever 3 (tempfile deferred to _save_state) is preserved because the import now lives inside atomic_write_json.

</details>

## F35h: file_size_guard repeated approve

`shrink` · verdict **modified** · ~65 lines · owner decision: no

file_size_guard.main prints {'decision':'approve'} in 10 places (:97, :103, :115, :119, :126, :135, :140, :155, :159, :161), not ~8, and the block once. The larger finding: the small-file (<5KB) and config-extension exemptions are dead logic. The only way to block is size >= SIZE_THRESHOLD (30000), so every file under 30000 approves regardless of extension. SMALL_FILE_THRESHOLD (:23-24) and CONFIG_EXTENSIONS (:63-72) can be deleted along with the two branches (:133-141). The refactor is one pure function returning a block reason or None, with a single print. It must stay stdlib-only: tests run the file as a bare `python file_size_guard.py` subprocess and the archived plan notes it does not import superclaude.utils.

**Changes**

- `src/superclaude/scripts/file_size_guard.py` (edit): Add `def _block_reason(tool_input: dict) -> str | None:` that returns None for: limit or pages set, empty file_path, ext in BINARY_EXTENSIONS, not os.path.isfile, size < SIZE_THRESHOLD; otherwise `_block_message(size, ext)`. main(): honour the SUPERCLAUDE_SIZE_GUARD=0 opt-out, parse stdin inside try/except (json.JSONDecodeError, OSError) to a reason (None on any failure), then print once: `{'decision':'block','reason':reason}` if reason else `{'decision':'approve'}`. Keep the empty-stdin case as approve.
- `src/superclaude/scripts/file_size_guard.py` (delete): Delete SMALL_FILE_THRESHOLD (:23-24) and CONFIG_EXTENSIONS (:63-72, with its comment). Trim docstring :8-9 to 'Bypass: limit parameter, pages parameter (PDF), binary extensions, files under 30KB.'

**Tests**

- tests/unit/test_file_size_guard.py needs no deletion: every test stays valid, because the behaviour is unchanged.
- Add one test that invalid JSON on stdin yields approve. The existing run_guard helper always sends valid JSON, so the JSONDecodeError arm has no coverage.

**Doc references**

- src/superclaude/core/rules/RULES_QUALITY.md:16 (R16) says 'auto-exempt: <5KB, or config <30KB'. It stays true (both are under the 30KB threshold), but optional rewording to 'files under 30KB are never blocked' removes the false impression of a separate exemption tier.
- src/superclaude/scripts/README.md:23 (file_size_guard row) needs no change.

**Collateral**

- No .py added or removed. hooks.json (Read matcher), registry and install_settings untouched.
- Do not import superclaude.utils here (per the archived hook-performance plan lever notes and the bare-python test harness).

**Verify**

```bash
uv run pytest tests/unit/test_file_size_guard.py && uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -c 'decision.*approve' src/superclaude/scripts/file_size_guard.py (expect 1) ; echo 'not json' | superclaude hook file_size_guard prints {"decision": "approve"}.
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/file_size_guard.py:94-161: control flow is limit/pages -> approve; no file_path -> approve; binary ext -> approve; not a file -> approve; size < 5000 -> approve; config ext and size < 30000 -> approve; size >= 30000 -> block; otherwise approve. The 5000 and config branches only approve sizes below 30000, which the final branch would approve anyway.
- grep SMALL_FILE_THRESHOLD|CONFIG_EXTENSIONS across the repo: only file_size_guard.py. tests/unit/test_file_size_guard.py (27 tests) drives it by subprocess and only asserts the decision. test_code_file_between_5kb_and_30kb (:163-169) already asserts approve for a 15KB code file.
- The exceptions are OSError and JSONDecodeError, both fail-open. No test feeds invalid JSON on stdin.

</details>

## F23: insight_writer jq calls

`stdlib` · verdict **confirmed** · ~45 lines · owner decision: yes (see README)

insight_writer list/query/stats shell out to jq (cmd_list :222-243, cmd_query :246-264, cmd_stats :267-289, _require_jq :105-113). The stdlib replacement is straightforward: _read_pending(path) at :482-493 already takes a path and returns the parsed dicts with bad lines skipped, so `_read_pending(_insight_file())` serves all three, with collections.Counter for stats. This is a real usability bug, not just tidiness: /sc:insight's flow step 4 runs `superclaude insight list --limit 20` on every capture, which exits 1 on stock Windows without jq. No jq-specific query syntax is documented. `query` takes only key=value, and `tags` is a membership test. One correction: the only existing test is the jq-missing error test, so list/query/stats have no happy-path coverage and the replacement must bring its own tests.

**Decision:** Output shape of `query`: jq pretty-prints matches (indent 2), and the spec keeps that via json.dumps(indent=2), so nothing visible changes except that jq is no longer needed. Alternative: compact one-line JSONL, which is shorter for the model to read. Also decide whether to fix the insight.md '--stats top tags' claim (spec) or add a tags Counter (new feature, out of scope). The 'jq-required: no inline Python fallback' gotcha is a declared design line and is removed by this cut.

**Changes**

- `src/superclaude/scripts/insight_writer.py` (edit): Replace :219-289 with roughly: rows = _read_pending(_insight_file()); empty or missing file prints '(no insights yet)' and returns 0. list: `for d in rows[-args.limit:]: print(f"{d.get('ts')} [{d.get('author') or 'unknown'}] [{d.get('type')}] {d.get('insight')}")`. query: keep the existing '=' and isidentifier validation; match `value in (d.get('tags') or [])` when key == 'tags', else `d.get(key) == value`; print `json.dumps(d, ensure_ascii=False, indent=2)`. stats: `Counter(d.get('type') for d in rows if args.all or d.get('type') != 'annotation')`, print most_common() in the same layout. Optionally rename _read_pending to _read_jsonl (callers: cmd_review, cmd_promote, cmd_discard, cmd_pending_count).
- `src/superclaude/scripts/insight_writer.py` (delete): Delete _require_jq (:105-113) and `import shutil` (:38). Docstring: :6-8 drop '(jq required)'; delete the 'Read paths require jq...' paragraph :14-15; section header :219 '(jq)' goes.
- `src/superclaude/commands/insight.md` (edit): :18 step 6 becomes '--list/--query/--stats read insights.jsonl through the same script'. :29 outputs row `--stats`: 'Type distribution, total' (drop the 'top tags' claim the code never had). :71 'Read paths:'. Delete the gotcha at :100. :107 `jq queries` becomes `list/query/stats`.

**Tests**

- tests/unit/test_insight_writer.py: delete TestJqRequired (:552-566 plus the '# ---------- jq error path' banner) and `import shutil` (:12; otherwise ruff F401 fails CI).
- Add three small tests using the `workdir` fixture and _run_append: (1) cmd_list prints '&lt;ts> [&lt;author>] [feedback] &lt;text>' lines and honours --limit; (2) cmd_query type=feedback and tags=rules return only matching rows, and a non-identifier key returns 2; (3) cmd_stats counts types, excludes annotations by default and includes them with --all, and prints 'Total: N'. Also assert a malformed JSONL line is skipped rather than aborting.

**Doc references**

- src/superclaude/commands/insight.md:18, :29, :71, :100, :107
- src/superclaude/scripts/insight_writer.py:6-8, :14-15, :219 (docstring and header)
- src/superclaude/agents/insight-analyst.md:38, :53 run jq directly on the file, not through the script, and already carry a fallback. Leave them alone.

**Collateral**

- No .py added or removed. No hooks.json or registry change: list/query/stats are CLI-only, and the hook subcommands (harvest, pending-count, request, session-baseline) are untouched.
- tests/unit/test_command_structure.py:334-335 pins the never-bare-python rule in insight.md. Keep that gotcha text intact when deleting the jq-required line.
- The dev machine has jq (scoop shim), so the Windows failure never shows locally. The jq-less check must strip jq from PATH.
- The installed copy .claude/commands/sc/insight.md is gitignored and refreshes on sync.

**Verify**

```bash
uv run pytest tests/unit/test_insight_writer.py && uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rnIE "\bjq\b" src/superclaude/scripts/insight_writer.py src/superclaude/commands/insight.md (expect none) ; with jq off PATH: `superclaude insight list --limit 3`, `superclaude insight query type=decision` and `superclaude insight stats` all exit 0.
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/insight_writer.py:105-113 (_require_jq), :222-289 (the three cmds), :38 (`import shutil`, used only by _require_jq). `subprocess` stays: _git_user :95 and _status_lines :666 use it.
- tests/unit/test_insight_writer.py:552-566 (TestJqRequired.test_list_errors_when_jq_missing) is the only test touching list/query/stats. grep shows no other reference to cmd_list, cmd_query or cmd_stats in tests, evals, scripts or CI.
- src/superclaude/commands/insight.md:16 (dedup uses `insight list`), :18 (step 6 'shell to jq'), :71 ('Read paths (need jq)'), :100 (gotcha jq-required: 'no inline Python fallback'), :107 (`jq queries`). Query forms documented are only `type=feedback` and `tags=rules` (:73-74).
- insight.md:29 says --stats shows 'Type distribution, top tags, count', but cmd_stats prints only types plus a total. The script docstring :8 also says 'Type/tag distribution'. Docs and code already disagree.
- jq semantics to preserve: list prints '&lt;ts> [&lt;author // unknown>] [&lt;type>] &lt;insight>' for the last --limit rows. query uses `select(.key==$v)` with $v a string, so non-string fields never match, and for tags `index($v)`. stats counts .type and skips annotations unless --all. jq pretty-prints matches with indent 2.
- Precedent: destructive_guard was already rewritten in Python because stock Windows lacks jq (scripts/destructive_guard.py:4-6, scripts/README.md:25).

</details>

## F35k: _working_tree_changed

`delete` · verdict **modified** · ~8 lines · owner decision: no

insight_writer._working_tree_changed (:695-702) has zero src callers: it is `return bool(_status_lines())` and _session_changed_code already inlines that at :753. Deleting it is right, but its 5 tests (tests/unit/test_insight_writer.py:1209-1246) are NOT dead. They are the only direct coverage of the live _status_lines() filter that keeps _FRAMEWORK_OWNED_PATHS (.superclaude_hooks, pending file, agent-memory) from counting as a user change. Retarget them to _status_lines(); do not delete them.

**Changes**

- `src/superclaude/scripts/insight_writer.py` (delete): Delete _working_tree_changed (:695-702 including blank lines).

**Tests**

- tests/unit/test_insight_writer.py:1209, :1220, :1230: `assert iw._working_tree_changed() is False` becomes `assert iw._status_lines() == []`.
- tests/unit/test_insight_writer.py:1238, :1246: `assert iw._working_tree_changed() is True` becomes `assert iw._status_lines()`. Keep the five test names and the class docstring.

**Doc references**

- none

**Collateral**

- No .py added or removed. Same file as F23: do both in the insight_writer commit to avoid conflicting edits to tests/unit/test_insight_writer.py.

**Verify**

```bash
uv run pytest tests/unit/test_insight_writer.py tests/integration/test_readonly_session_is_quiet.py && uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rn _working_tree_changed src tests (expect none).
```

<details><summary>Evidence</summary>

- grep _working_tree_changed over py and md (excluding archive): def at src/superclaude/scripts/insight_writer.py:695 and the 5 assertions only. docs/features/runtime-behavior-audit/05b-plan-defect-remediation.md mentions it historically and needs no change.
- _status_lines (:659-692) is used by _tree_fingerprint (:704-709) and _session_changed_code (:743-754), both live. tests/integration/test_readonly_session_is_quiet.py imports _FRAMEWORK_OWNED_PATHS.

</details>

## F35m.b: double stdin JSON parse

`shrink` · verdict **confirmed** · ~8 lines · owner decision: no

The duplication is real but it lives in context_loader.py, not context_reset.py: _extract_prompt (:1106-1112) and _extract_session_id (:1115-1128) each json.loads the same stdin, called back to back at :1134-1135. A merged helper saves about 8 lines and incidentally fixes an AttributeError that _extract_prompt raises for non-dict JSON. The ripple is small but not zero: 5 tests import _extract_session_id. Recommended: low value, do only if touching this file anyway (F20 does).

**Changes**

- `src/superclaude/scripts/context_loader.py` (edit): Replace the two helpers with one `_parse_hook_input(stdin_data) -> tuple[str, str | None]`: json.loads once, `data if isinstance(data, dict) else {}`, prompt = data.get('prompt', stdin_data), session_id = the non-empty str or None. main() :1134-1135 becomes `prompt, session_id = _parse_hook_input(stdin_data)`.

**Tests**

- tests/unit/test_context_loader.py: retarget TestExtractSessionId (:37-54) to the new helper's second return value, and add one assertion for non-dict JSON returning the raw text. Update the import at :21.

**Doc references**

- none

**Collateral**

- No .py added or removed.

**Verify**

```bash
uv run pytest tests/unit/test_context_loader.py && uv run pytest && uv run ruff check src/ tests/ ; grep -rn '_extract_prompt\|_extract_session_id' src tests (expect none or the new name only).
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/context_loader.py:1106-1135.
- tests/unit/test_context_loader.py:21 (import) and :37-54 (5 tests of _extract_session_id).

</details>

## F35m.c: find_migration_reference

`stdlib` · verdict **confirmed** · ~11 lines · owner decision: no

find_migration_reference (context_loader.py:997-1025) hand-rolls newest-by-mtime with a stat try/except. `max(found, key=lambda p: p.stat().st_mtime, default=None)` is equivalent (first of equal mtimes wins in both). The only behavioural difference is a file vanishing between glob and stat, which now raises OSError. The only caller already catches OSError (_emit_prompt_command_reference :1071-1074) and falls to the 'no reference found' notice. Saves about 11 lines.

**Changes**

- `src/superclaude/scripts/context_loader.py` (edit): Replace :1018-1025 (newest/newest_mtime loop) with `return max(found, key=lambda p: p.stat().st_mtime, default=None)`.

**Tests**

- None to change; add nothing.

**Doc references**

- none

**Collateral**

- No .py added or removed. Same file as F20: batch the edits.

**Verify**

```bash
uv run pytest tests/unit/test_context_loader.py -k migration && uv run pytest && uv run ruff check src/ tests/
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/context_loader.py:1010-1025; caller :1071-1074 wraps in try/except OSError.
- tests/unit/test_context_loader.py:888, :905, :919, :924 cover newest-wins and none-found; they stay as is.

</details>

## F35m.d: hooks.json unused keys

`delete` · verdict **confirmed** · ~7 lines · owner decision: no

hooks.json top-level 'description' (:2) is read by nothing, not even a test. 'schema_version' (:3) is read only by a presence assertion (tests/integration/test_cross_directory_refs.py:193-196). Every real consumer reads only the 'hooks' key: install_components.py:331-336, install_inventory.py:86-92 and :159-161, install_settings.py:376, test_hook_dispatch.py:36 and test_codex_component_map.py:58. The file is not a plugin hooks.json: it is merged into settings, and the installed .claude/hooks/hooks.json copy is not read by Claude Code. .claude-plugin/marketplace.json lists only the two socratic plugins. Safe to drop both keys and the presence test.

**Changes**

- `src/superclaude/hooks/hooks.json` (delete): Delete lines 2-3 ("description" and "schema_version"). Keep the JSON valid (the `hooks` key then follows `{`).

**Tests**

- tests/integration/test_cross_directory_refs.py: delete test_hooks_json_schema_version_present (:193-196).

**Doc references**

- none

**Collateral**

- test_cli_install.py::test_the_installed_hooks_json_is_the_shipped_one_verbatim compares shipped vs installed bytes and stays green. If F12 is also applied, hooks.json is edited twice (line 10 comment too): one commit.
- No .py added or removed; registration count unchanged.

**Verify**

```bash
uv run pytest tests/integration/test_cross_directory_refs.py tests/unit/test_cli_install.py tests/unit/test_hook_dispatch.py tests/unit/test_codex_component_map.py && uv run pytest ; python -c "import json;json.load(open('src/superclaude/hooks/hooks.json',encoding='utf-8'))"
```

<details><summary>Evidence</summary>

- grep schema_version over py/md/json/toml/yml: hooks.json:3, the installed copy .claude/hooks/hooks.json:3 (gitignored), and test_cross_directory_refs.py:193-196.
- src/superclaude/hooks/hooks.json:2-3. install_settings.merge_hooks_to_settings uses hooks_config.get('hooks', {}) only (:376).

</details>

## F35m.a: context_reset.get_cache_file

`shrink` · verdict **modified** · ~7 lines · owner decision: no

context_reset.get_cache_file (:24-30) only delegates to utils.context_cache_file, but it has three kinds of consumers: context_reset.py itself (:52, :54), cli/main.py (:1405 import, :1418, :1420) and tests/unit/test_scope_paths.py (imports at :179, :194, :207, :223; calls at :186-231). The cut saves about 7 lines for a 3-file ripple. Recommended: skip, or fold into a batch that already touches those files.

**Changes**

- `src/superclaude/scripts/context_reset.py` (edit): Delete get_cache_file (:24-30). Use context_cache_file at :52 and :54. Drop `Path` from the imports if unused.
- `src/superclaude/cli/main.py` (edit): :1405 import `reset_context_cache` from context_reset and `context_cache_file` from superclaude.utils; :1418 and :1420 call context_cache_file.

**Tests**

- tests/unit/test_scope_paths.py: replace the four `from superclaude.scripts.context_reset import get_cache_file` imports with `from superclaude.utils import context_cache_file` and rename the calls at :186, :189, :200, :203, :211, :212, :229-231.

**Doc references**

- none

**Collateral**

- No .py added or removed.
- Net saving is tiny. This is the lowest-value item in F35m.

**Verify**

```bash
uv run pytest tests/unit/test_scope_paths.py tests/unit/test_cli_context.py && uv run pytest && uv run ruff check src/ tests/ ; grep -rn get_cache_file src tests (expect none).
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/context_reset.py:24-30; context_reset.py already imports context_cache_file at :18.
- src/superclaude/cli/main.py:1405-1420; tests/unit/test_scope_paths.py:179-231.

</details>
