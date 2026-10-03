---
status: complete
revised: 2026-10-03
---

# B5: CLI surface removals

Item specs for batch B5. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b5). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F05: `superclaude audit`

`yagni` · verdict **confirmed** · ~375 lines · owner decision: yes (see README)

`superclaude audit` is a one-caller wrapper (run_audit, main.py:773) whose four check groups each have an identical test: drift = the `verify-drift` command, handoff = test_cross_references.py::TestHandoffIntegrity, usage = test_content_usage.py (4 tests). The trigger-uniqueness check and HANDOFF_SKIP are dead on both the audit and the test side, so no check is lost. `--format markdown` / `--out` have no tests, no docs/reports/AUDIT.md exists, and CI never runs audit. Cut = delete audit.py, the click command plus `_format_audit_markdown`, and the Makefile target.

**Decision:** `superclaude audit` and `make audit` are documented (README.md:555, Makefile help). Confirm the drop, with `make verify-drift` + `uv run pytest` as the replacement (every audit check has a test; the only non-test piece, drift, is `verify-drift`).

**Changes**

- `src/superclaude/cli/audit.py` (delete): Delete the whole file (184 lines). Its only import of verify_drift is a wrapper; verify_drift.py itself stays (the `verify-drift` command uses it).
- `src/superclaude/cli/main.py` (delete): Delete lines 731-904: the `@main.command()` + 4 `@click.option` decorators + `def audit` (731-842), `def _format_audit_markdown` (844-902) and the two trailing blank lines, so `@main.command(... insight` at 905 follows the 2 blank lines after verify_drift_cmd. Edit in a bottom-up order with the other main.py cuts (see unknowns).
- `src/superclaude/cli/main.py` (edit): Line 182 comment: 'the way doctor, verify-drift and audit do' -> 'the way doctor and verify-drift do'.
- `src/superclaude/cli/install_paths.py` (edit): Line 110 docstring: 'read-only commands: doctor, verify-drift, audit.' -> 'doctor, verify-drift.' (resolve_reporting_target keeps callers doctor, verify-drift, install --list).
- `Makefile` (edit): Remove token `audit` from the .PHONY line 1; delete lines 95-99 (the '# Run content integrity audit' comment, `audit:` target, its 2 recipe lines, trailing blank); delete help line 176 (`make audit - Run content integrity audit`).
- `README.md` (edit): Line 555 table row: drop ` · \`superclaude audit\`` -> '| Health & drift checks | `superclaude doctor` · `superclaude verify-drift` · `superclaude context explain` / `reset` |' (further trimmed by F06).
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): §1 row at line 32: '전체 Python module | 57' -> 56 (recount, see verify). Line 159: '설치·제거·목록·doctor·audit·drift' -> drop 'audit·'.
- `tests/unit/test_cli_reporting_scope.py` (delete): Delete class TestAuditResolvesTheInstall (lines 127-136 plus its trailing blank line 137): both tests drive `main audit`.
- `tests/unit/test_scope_paths.py` (edit): Docstring-only: line 486 'doctor, verify-drift and audit defaulted' -> 'doctor and verify-drift defaulted'; line 719 'doctor / verify-drift / audit walk up' -> 'doctor / verify-drift walk up'.

**Tests**

- tests/unit/test_cli_reporting_scope.py::TestAuditResolvesTheInstall (2 tests: test_reports_the_local_install_from_a_subdirectory, test_clean_install_passes) -> delete; they only exercise the deleted command.
- tests/unit/test_cross_references.py, tests/unit/test_content_usage.py, tests/unit/test_verify_drift.py -> keep unchanged; they are the replacement coverage.
- No test imports superclaude.cli.audit (grep 'cli.audit|run_audit' in tests -> 0).

**Doc references**

- README.md:555
- Makefile:1 (.PHONY), Makefile:95-98, Makefile:176 (help)
- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:32 (module count) and :159 (cli/ role)
- src/superclaude/cli/main.py:182 (comment), src/superclaude/cli/install_paths.py:110 (docstring)
- tests/unit/test_scope_paths.py:486,719 (docstrings)
- Leave alone: docs/archive/**, .claude/insights.jsonl(.bak) (historical entries), docs/codex 04 §8 / 08 F-004 ('drift/audit' used as a concept, not the command)

**Collateral**

- Trap (a): removing audit.py takes src/superclaude/**/*.py from 57 to 56 -> tests/unit/test_codex_component_map.py::test_documented_count_matches_source[전체 Python module] fails until 02_component_and_delivery_map.md §1 is set to 56 in the same commit. (If the F13 cascade also deletes hooks/inline_hooks.py the number is 55.)
- Trap (b): README component counts (commands/agents/modes/MCP servers) are the only counts test_version_consistency.py checks; a CLI-subcommand row edit does not touch them.
- Trap (c): audit is not a hook; hooks.json, hook_dispatch.HOOKS and install_settings markers are unaffected.
- Trap (d): nothing under tests/unit/scripts/ is touched; `make test-scripts` not required for this item.
- The `make audit` target and the `audit` command disappear together; no CI job or workflow calls either.

**Verify**

```bash
uv run pytest  # exit 0, incl. test_codex_component_map after the 57->56 edit
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
grep -rIn -E 'run_audit|cli\.audit|_format_audit_markdown|superclaude audit|make audit|AUDIT\.md' src tests Makefile README.md docs --exclude-dir=archive --exclude-dir=__pycache__  # expect no hits
uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"  # must equal the number written in 02 §1
uv run superclaude audit; echo $?  # expect 'No such command' (exit 2)
uv run superclaude verify-drift  # still works
```

<details><summary>Evidence</summary>

- grep run_audit across the whole repo (excluding pycache/archive) -> only src/superclaude/cli/audit.py:154 (def) and src/superclaude/cli/main.py:773 (sole caller)
- grep 'audit' in .github/ and pyproject.toml -> 0 hits; Makefile:1,95-98,176 is the only non-doc reference (`make audit` = `uv run superclaude audit --verbose`)
- Check-by-check vs tests: (1) drift: audit.py:~170 calls verify_drift(), the same function as `verify-drift` (main.py:650-702) and tests/unit/test_verify_drift.py + test_cli_reporting_scope.py::TestVerifyDriftResolvesTheInstall; (2) handoff targets: audit.py:50-58 vs tests/unit/test_cross_references.py:84-93 (same regex `<handoff\s+next=`, same dirs commands/agents/modes, same skip set); (3) trigger uniqueness: audit.py:60-93 vs test_cross_references.py:99-125 (same regex); (4) usage: audit.py:98-151 checks modes mapped / MCP docs mapped / TRIGGER_MAP dangling / COMPOSITE_FLAGS dangling == test_content_usage.py::TestModeMapping, TestMcpMapping, TestTriggerMapIntegrity.test_trigger_map_files_exist and .test_composite_flags_files_exist. Result: 0 checks without a test equivalent.
- Trigger check never fires: `grep -l -i -E 'triggers?\s*[-–—]\s*' src/superclaude/agents/*.md` -> 0 files; a python re-run of the exact audit regex over every agent frontmatter description -> 0 matches (5 files in dir = 4 agents + README by listing; 23 agents per README, glob counted 5 .md at that path level? see unknowns). The test copy (test_cross_references.py:114) uses the same regex, so the surviving test is equally vacuous.
- HANDOFF_SKIP = {'/sc:[command]'} (audit.py:30, used :58) can never match: help.md:89 has `<handoff next="/sc:recommend /sc:[command]"/>` but re.findall(r'/sc:([\w-]+)', ...) returns ['recommend'] only (verified with python) because `[` is not \w, so the captured token never equals '[command]'. Same dead set in tests/unit/test_cross_references.py:23-25,89.
- Read-only run at HEAD: audit._check_cross_refs(src) -> {'handoff': [], 'triggers': []} clean; audit._check_usage(src) -> clean. The audit currently catches nothing the tests do not.
- grep tests for '--format', 'markdown', '_format_audit_markdown' -> 0 hits. `ls docs/reports` -> PROJECT_INDEX.md only (no AUDIT.md). The only audit CLI tests are tests/unit/test_cli_reporting_scope.py:127-136 (scope resolution, text mode).
- docs: README.md:555 lists `superclaude audit`; docs/codex/prompting_session_raw/02_component_and_delivery_map.md:159 lists 'audit' in the cli/ role. docs/PRD.md and ARCHITECTURE.md do not mention it.

</details>

## F06: `superclaude context explain`

`yagni` · verdict **confirmed** · ~595 lines · owner decision: yes (see README)

`superclaude context explain` (stdout-marker regexes, _parse_loader_output, _attribute_triggers, _context_content_root, sandbox-subprocess _run_loader_isolated) has no caller in hooks, commands, Makefile or CI; it is documented only in README.md:555, src/superclaude/scripts/README.md:15 and exercised only by tests/unit/test_cli_context.py. It was added 2026-08-30 (35f8903). `context reset` shares only the group and the test file and stays.

**Decision:** `superclaude context explain` is a documented debugging tool (README.md:555, scripts/README.md:15; it is the only human-readable way to see which TRIGGER_MAP entry fires for a prompt and what it costs). Is it OK to remove it and keep only `context reset`?

**Changes**

- `src/superclaude/cli/main.py` (delete): Delete 1024-1031 (_CTX_*_RE), 1033-1272 (_context_content_root through _attribute_triggers incl. blank lines) and 1282-1375 (the `@context_group.command(name='explain'...)` decorator through the end of context_explain). Shrink the header comment 1009-1022 to the `reset`-only truth (it currently explains explain's subprocess design).
- `src/superclaude/cli/main.py` (edit): context_group docstring (1274-1280): drop the sentence about `explain`; e.g. 'Reset context_loader state. `reset` clears the dedup cache so contexts re-inject.' Keep @main.group(name='context') and `reset` so `superclaude context reset` (README:555, scripts/README.md:19) still works. If F13 also lands, `import re` (line 7) is then unused: remove it.
- `tests/unit/test_cli_context.py` (delete): Delete fixture `scoped_install` (56-87), helpers `_state_snapshot` (89-99) and `_run_loader_directly` (101-122), class TestContextExplain (132-251) and class TestContextContentRoot (253-304). Then drop now-unused imports (json, subprocess, sys, hook_state_dir) and the LOADER_SCRIPT constant (line 36) if ruff flags them; keep `project` fixture, TestContextReset (306+) and the README-guard tests (423-493).
- `tests/unit/test_cli_context.py` (edit): TestContextGroupRegistration (125-129): `assert set(group.commands) == {'reset'}` and rename to test_group_and_reset_are_registered. Line 437: drop `assert "superclaude context explain" in text` (keep the `context reset` assertion; rename test_both_subcommands_are_named -> test_reset_subcommand_is_named). Module docstring line 1: '`superclaude context explain` / ...reset' -> reset only. Parametrized id 'console-subcommand' (line 474 passage 'Dry run: `superclaude context explain "<p>"`') is only regex test data; swap to `superclaude context reset` or leave.
- `src/superclaude/scripts/README.md` (edit): Line 15: drop ' Dry run: `superclaude context explain "<prompt>"`' from the context_loader.py row.
- `README.md` (edit): Line 555: '`superclaude context explain` / `reset`' -> '`superclaude context reset`'.

**Tests**

- tests/unit/test_cli_context.py::TestContextExplain (11 tests) -> delete.
- tests/unit/test_cli_context.py::TestContextContentRoot (4 tests) -> delete.
- tests/unit/test_cli_context.py::TestContextGroupRegistration -> update expected set to {'reset'}.
- tests/unit/test_cli_context.py::TestScriptsReadmeDocumentsTheConsoleEntries::test_both_subcommands_are_named -> drop the explain assertion.
- tests/unit/test_cli_context.py::TestContextReset, test_bare_script_prescription_discriminates -> keep.

**Doc references**

- README.md:555
- src/superclaude/scripts/README.md:15
- src/superclaude/cli/main.py:1009-1022 (design comment), 1274-1280 (group docstring), 1302-1303 (examples, deleted with the command)
- tests/unit/test_cli_context.py:1,36,56-122,437,474

**Collateral**

- No .py file added or removed -> test_codex_component_map module count unaffected by this item.
- Hooks untouched: hooks.json, HOOKS registry and install_settings not involved; `superclaude hook context_loader` and `superclaude hook context_reset` still resolve.
- Cross-finding: main.py `import re` is used only by `agents` (line 582) and the _CTX_*_RE / explain code; with F06 AND F13 both applied, `import re` must be removed or ruff F401 fails.
- docs/UI-GUIDE.md:108 cites `main.py:196` for `install --list-all`; every cut here is below line 196, so it only moves via the F13/F06 top-of-file import removals (see F13).
- Dropping explain also removes the only consumer of context_loader's stdout marker format outside the hook runtime, i.e. one fewer thing that silently breaks when those markers change.

**Verify**

```bash
uv run pytest tests/unit/test_cli_context.py tests/unit/test_context_loader.py  # then full `uv run pytest` exit 0
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
grep -rIn -E 'context explain|_run_loader_isolated|_parse_loader_output|_attribute_triggers|_context_content_root|_CTX_' src tests README.md docs --exclude-dir=archive --exclude-dir=__pycache__  # expect no hits
uv run superclaude context --help  # lists only `reset`
uv run superclaude context reset  # still runs
```

<details><summary>Evidence</summary>

- grep -F 'context explain' over src, tests, docs (minus archive), README.md, Makefile, .github, scripts, evals, .claude, .serena -> main.py docstrings (1302-1303), src/superclaude/scripts/README.md:15, README.md:555, tests/unit/test_cli_context.py:1,437,474 only. No hooks.json / commands/*.md / Makefile / workflow hit.
- grep for the helper names (_packaged_loader, _context_content_root, _run_loader_isolated, _parse_loader_output, _attribute_triggers, _CTX_*) outside main.py -> only docstring mentions in tests/unit/test_cli_context.py:60,256; nothing imports them.
- main.py layout: header comment 1009-1022, _CTX_*_RE 1024-1031, _context_content_root 1034-1076, _packaged_loader 1079-1086, _run_loader_isolated 1089-1140, _parse_loader_output 1143-1246, _attribute_triggers 1249-1270, context_group 1273-1280, context_explain 1282-1374, context_reset_cmd starts 1376.
- git log -S context_explain -> 35f8903 2026-08-30 'route script entry points through superclaude subcommands' (same commit as auto-improve/parallel-ab/insight console entries).
- test_context_loader.py has its own run_loader harness and covers budget and directive behaviour independently of explain (grep: lines 365-380, 627-724).
- token_estimator.py is NOT orphaned by this cut: context_loader.py:31,601 still imports it. `superclaude.scripts.context_loader` COMPOSITE_FLAGS/TRIGGER_MAP imports from _attribute_triggers disappear, harmlessly.
- .claude/rules/gotchas/hooks.md:9 `script-needs-console-entry` says a script with BOTH a hook path and a human path needs a console subcommand; context_loader.py keeps only its hook path after the cut, and context_reset keeps `context reset`, so the rule is not violated.

</details>

## F13: `superclaude agents`

`delete` · verdict **confirmed** · ~144 lines · owner decision: yes (see README)

`superclaude agents` (--list/--info/--tokens) is referenced only by its own docstring and one test (test_cli_reporting_scope.py:144); README, docs/, .claude/ and .serena/ never mention it. Its removal also orphans `parse_frontmatter` in hooks/inline_hooks.py (main.py:14 import is its only production consumer), which the audit did not list.

**Decision:** Cascade: after `agents` goes, hooks/inline_hooks.py (50 lines), its 3 tests in test_hooks.py and the lazy export in hooks/__init__.py have no production caller. hooks/__init__.py:9-12 says the names are 'kept only to preserve the documented API'. Delete them in this item (module count 55, doc recount) or leave as a separate finding?

**Changes**

- `src/superclaude/cli/main.py` (delete): Delete lines 514-649 (`@main.command()` + 4 options + `def agents` ... last click.echo at 647, plus the two blank lines) so verify-drift_cmd's decorator at 650 follows the 2 blank lines after doctor. Delete the import at line 14 (`from superclaude.hooks.inline_hooks import parse_frontmatter`). If F06 also lands, delete `import re` at line 7 as well.
- `tests/unit/test_cli_reporting_scope.py` (delete): Delete test_agents_lists_the_local_install (lines 143-148 incl. blank). Edit the class docstring at 141 ('agents and skills never write, so they follow the same rule.') -> '`install --list-all` reports on an install and never writes, so it follows the same rule.'; consider renaming the class (it now holds one test).
- `src/superclaude/hooks/inline_hooks.py` (delete): OPTIONAL cascade (see decision_needed): delete the module (50 lines); its only remaining caller is the removed command.
- `src/superclaude/hooks/__init__.py` (edit): OPTIONAL cascade: remove the `parse_frontmatter` entries from the TYPE_CHECKING import (line 21), __all__ (27-28 comment+name) and _LAZY (34), and the inline_hooks bullet in the docstring (line 4) and rationale paragraph (lines 9-12).
- `tests/unit/test_hooks.py` (delete): OPTIONAL cascade: delete class TestInlineHooks (lines 53-101, 3 tests) and fix the module docstring line 3 ('hook_tracker.py and inline_hooks.py').

**Tests**

- tests/unit/test_cli_reporting_scope.py::TestInventoryCommandsResolveTheInstall::test_agents_lists_the_local_install -> delete (keep test_list_all_reports_the_local_install).
- OPTIONAL cascade: tests/unit/test_hooks.py::TestInlineHooks (test_parse_frontmatter_basic, _with_lists, _with_lists_root_compat) -> delete with the module.

**Doc references**

- src/superclaude/cli/main.py:548-551 (docstring, deleted with the command)
- tests/unit/test_cli_reporting_scope.py:141 (class docstring)
- docs/UI-GUIDE.md:108 cites `src/superclaude/cli/main.py:196` for `install --list-all`: removing main.py:14 (and `import re` at :7) moves it to line 195 (194 with both). Update the cited line or drop the number.
- OPTIONAL cascade: src/superclaude/hooks/__init__.py:4,9-12 docstring; src/superclaude/cli/hook_dispatch.py:13 quotes '`import superclaude.cli.main` is ~40ms (click + yaml)' as a dated 2026-09-05 measurement and will read slightly stale (yaml likely no longer loaded by main.py) - leave as dated history.

**Collateral**

- Trap (a): the base cut adds/removes no .py file. If the optional cascade deletes hooks/inline_hooks.py the module count drops by 1 more (57 -> 56 with F05 alone, 55 with F05 + this cascade) and docs/codex/prompting_session_raw/02_component_and_delivery_map.md §1 line 32 must be recomputed in the same commit.
- tests/unit/test_hook_dispatch.py:199 `_NO_CLICK` asserts yaml/click/cli.main are NOT imported on the hook fast path; unaffected (entry.py dispatches before main).
- resolve_reporting_target keeps callers doctor, verify-drift and install --list, so install_paths.py needs no code change (docstring at :110 already covered by F05).
- Hooks/registry/install_settings: not involved.

**Verify**

```bash
uv run pytest  # exit 0
uv run ruff check src/ tests/  # catches a leftover unused `re` / parse_frontmatter import
uv run ruff format --check src/ tests/
grep -rIn -E 'superclaude agents|def agents|parse_frontmatter' src tests README.md docs --exclude-dir=archive --exclude-dir=__pycache__  # remaining hits must be only the local test copies (test_agent_structure/command_structure/cross_references) unless the cascade was skipped
uv run superclaude agents; echo $?  # expect 'No such command'
uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"  # must equal 02 §1 if the cascade deleted a module
```

<details><summary>Evidence</summary>

- grep -F 'superclaude agents' and 'agents --list' over README.md, docs (minus archive), src, tests, Makefile, .github, .claude, .serena -> only src/superclaude/cli/main.py:548-551 (the docstring examples).
- grep -n '"agents"' in tests -> tests/unit/test_cli_reporting_scope.py:144 `_run(['agents','--list'])` is the only test that invokes the command; other 'agents' hits are directory/component names.
- main.py:514-647 is the whole command; it is the only user of `parse_frontmatter` (main.py:620, 639; import at line 14) and one of two users of `re` for the frontmatter slice (line 582).
- `parse_frontmatter` from superclaude.hooks.inline_hooks: grep across src/tests -> main.py:14 (import), hooks/__init__.py:21,27,34 (lazy re-export), tests/unit/test_hooks.py:58,72,89 (3 tests). inline_hooks.py:2-3 docstring says 'consumed by the CLI'. Other `parse_frontmatter` definitions in tests are local copies.
- pyyaml stays a required dependency: scripts/parallel_ab/spec_loader.py:9 still imports yaml, so pyproject.toml is unchanged.

</details>

## F35i: HAS_YAML fallback

`delete` · verdict **confirmed** · ~14 lines · owner decision: no

The HAS_YAML fallback in hooks/inline_hooks.py (:13-19 try/except import, :37 branch, :43-50 hand parser) is dead: pyyaml>=6.0.0 is a hard dependency (pyproject.toml dependencies list) and nothing else tolerates its absence (scripts/parallel_ab/spec_loader.py:9 imports yaml unguarded). The only consumer is cli/main.py (:14, :620, :639). No test or code references HAS_YAML or simulates a missing yaml.

**Changes**

- `src/superclaude/hooks/inline_hooks.py` (edit): Replace the try/except block :13-19 with `import yaml` (alongside `import re`). In parse_frontmatter keep only: `try: return yaml.safe_load(frontmatter_text) or {}` / `except yaml.YAMLError: return {}`. Delete the 'Basic fallback parsing' loop :43-50.

**Tests**

- None to delete. tests/unit/test_hooks.py::TestInlineHooks (3 tests) keep covering the yaml path.

**Doc references**

- src/superclaude/hooks/inline_hooks.py:1-7 docstring (no change needed)

**Collateral**

- No .py added or removed. test_hook_dispatch import-graph test is unaffected because inline_hooks is outside the hook graph.

**Verify**

```bash
uv run pytest tests/unit/test_hooks.py tests/unit/test_hook_dispatch.py && uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rn HAS_YAML src tests (expect none).
```

<details><summary>Evidence</summary>

- pyproject.toml: dependencies include 'pyyaml>=6.0.0'.
- grep HAS_YAML over src, tests and docs: only inline_hooks.py:17, :19, :37.
- grep for sys.modules or None-patching of yaml in tests: none. tests/unit/test_hooks.py:56-99 exercise the yaml path.
- hooks/__init__.py:11-34 lazy-loads inline_hooks precisely because it pulls in yaml. Making the import unconditional does not change when yaml loads, and the hook fast path (`superclaude hook`) never imports inline_hooks.

</details>

## F29: `update` and `version` commands

`yagni` · verdict **confirmed** · ~50 lines · owner decision: yes (see README)

`superclaude update` is `install --force --scope X` with a different banner: it calls get_base_path(scope) then install_all(base_path, force=True, scope) (main.py:437-449), the same two calls `install --force` makes; the only differences are the banner text and that `install` prints a git-repo scope hint. `superclaude version` duplicates the `--version` that @click.version_option(main.py:18) already provides. Both have 0 tests. Caveat: `update` is a declared lifecycle verb in docs/PRD.md, so removing it is a decision.

**Decision:** `update` is a declared lifecycle verb: docs/PRD.md:40 lists it as part of core feature 1 ('install / update / uninstall') and README.md:141-146,167,423 document it. Remove it (and amend PRD + README), or keep it as the friendlier verb and cut only `version`?

**Changes**

- `src/superclaude/cli/main.py` (delete): Delete the `update` command: lines 416-452 (decorator through `sys.exit(1)` at 450 plus blank lines). Delete the `version` command: lines 1440-1445 (decorator, def, docstring, echo, 2 trailing blanks; keep 2 blank lines before `if __name__`). `__version__` stays imported (used by version_option at line 18).
- `src/superclaude/cli/__init__.py` (edit): Line 6: delete '    - superclaude version                  # Show version' (or change to '--version').
- `README.md` (edit): Line 128: replace `superclaude version` with `superclaude --version`. Lines 141-146 ('#### **Update**' block): remove, or rewrite as `superclaude install --force                   # re-sync content; add --scope project|local`. Line 167: `install` / `update` / `uninstall` -> `install` / `uninstall`. Line 423: 'install/uninstall/update --scope' -> 'install/uninstall --scope'.
- `docs/PRD.md` (edit): Line 40 ('`install` / `update` / `uninstall` across') and line 67 ('`install` / `update` / `uninstall` / `mcp` / `doctor`') - drop `update` (or reword as 'install --force'), if the owner accepts the cut.

**Tests**

- No tests invoke `update` or `version` (grep for ["update"] and CliRunner version invocations -> 0); nothing to delete.
- tests/unit/test_console_probe.py uses fake `--version` output only -> unaffected.
- Optionally add one assertion elsewhere that `superclaude --version` works; not required (Makefile:79 `verify` exercises it).

**Doc references**

- README.md:128, 141-146, 167, 423
- docs/PRD.md:40, 67
- src/superclaude/cli/__init__.py:6
- src/superclaude/cli/main.py:435-436 (update docstring examples, deleted with the command)
- docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:103 ('install/update가 idempotent다') - generic wording, optional touch

**Collateral**

- No .py file added/removed -> codex module-count test unaffected.
- README component-count tests (test_version_consistency.py) count commands/agents/modes/MCP servers, not CLI subcommands -> unaffected.
- Hooks/registry/install_settings: not involved; installers print 'use --force to reinstall' (install_components.py:242,582; install_settings.py:435) which already points at `install --force`, never at `update`.

**Verify**

```bash
uv run pytest  # exit 0
uv run ruff check src/ tests/
grep -rIn -E 'superclaude update|superclaude version|install/uninstall/update' src tests README.md docs Makefile .github --exclude-dir=archive --exclude-dir=__pycache__  # expect no hits (PRD wording per decision)
uv run superclaude update; echo $?  # expect 'No such command'
uv run superclaude --version  # still prints the version
make -n sync-user  # unchanged (uses install --force)
```

<details><summary>Evidence</summary>

- main.py:416-450 `update`: `get_base_path(scope)`, banner 'Updating SuperClaude to version X (scope: S)', `install_all(base_path=base_path, force=True, scope=scope)`, exit 1 on failure. main.py:107-253 `install --force`: --force is non-default so the wizard (`_all_defaults()`) is skipped, then the same get_base_path + install_all(force=True); extras are the banner 'Installing SuperClaude components' and the user-scope-in-a-git-repo hint (:229-236).
- Makefile:21,25,29 already implement 'update' as `uv run superclaude install --force --scope user|project|local` (sync-user/project/local). Nothing in src or Makefile calls `superclaude update`.
- grep -F 'superclaude update' -> main.py:435-436 (docstring) and README.md:144-145 only; README.md:167 `install` / `update` / `uninstall` scope table, README.md:423 'install/uninstall/update --scope'; docs/PRD.md:40 (core feature 1: 'install / update / uninstall across user|project|local') and :67 (MVP exclusions list `update`). tests: grep '"update"' -> 0 hits.
- README.md:145 comment '(update takes --scope only; use `install --force` to re-copy everything)' implies a difference that does not exist: both paths run install_all(force=True).
- `version` command: main.py:1440-1443 prints 'SuperClaude version X'; `--version` prints 'SuperClaude, version X' (click). Callers of the subcommand: README.md:128 and the cli/__init__.py:6 docstring only. The PATH probe (install_paths.py:265) and Makefile:79 use `--version`, never `version`; test_console_probe.py uses fake `--version` output. grep tests for the `version` command -> 0 hits.

</details>

## F31: single-item MCP picker

`yagni` · verdict **confirmed** · ~48 lines · owner decision: yes (see README)

In install_mcp_servers the interactive picker (install_mcp.py:672-723) offers one selectable item: only `serena` has category 'core' (MCP_SERVERS: serena core; tavily, playwright, chrome-devtools are 'plugin'), and the picker's '0 = all core' and '1 = serena' resolve to the same list. The comma-separated-index parser is therefore dead weight. The picker is reachable only via bare `superclaude mcp` (main.py:404 passes selected_servers=None), and README documents it as an 'interactive picker'.

**Decision:** README.md:112 and mcp/README.md:7,11 present `superclaude mcp` as an interactive picker with 'Core auto-suggested'. After the cut a bare `superclaude mcp` registers Serena with no prompt. Accept that (and the doc rewording), or keep a single click.confirm, or keep the picker because more core servers are expected?

**Changes**

- `src/superclaude/cli/install_mcp.py` (edit): Replace the `else:` branch at lines 672-723 (52 lines) with ~4 lines: `else:\n    # ponytail: one core server today; reintroduce a picker only if a second core server ships.\n    servers_to_install = [name for name, info in MCP_SERVERS.items() if info.get('category', 'core') == 'core']`. Optionally keep a 3-line plugin-server hint (`superclaude mcp --list` shows them). Update the docstring at 653 ('or None for interactive selection' -> 'or None for the core servers').
- `README.md` (edit): Line 112: 'interactive picker (default scope: user)' -> 'register the core server (Serena); default scope: user'. Lines 363-364: drop '# Interactive installation' / `superclaude mcp`, or relabel.
- `src/superclaude/mcp/README.md` (edit): Line 7: 'Core auto-suggested in interactive pick' -> 'Core installed by bare `superclaude mcp`'; line 11 heading '(auto-suggested by `superclaude mcp`)' -> '(installed by bare `superclaude mcp`)'.

**Tests**

- None cover the picker; nothing to delete.
- tests/unit/test_install_mcp_prerequisites.py::test_no_selection_runs_every_check (check_prerequisites(selected_servers=None)) -> unaffected (it calls check_prerequisites directly).

**Doc references**

- README.md:112, 363-364
- src/superclaude/mcp/README.md:7, 11
- src/superclaude/cli/install_mcp.py:653 (docstring), :673-674 (comment), :597 list_available_servers heading 'Core (auto-suggested)' (optional rename)
- src/superclaude/cli/install_interactive.py:148 hint stays valid

**Collateral**

- No .py file added/removed -> codex module-count test unaffected.
- mcp/README.md is under src/superclaude/mcp/ and checked by content-structure tests only for MCP_*.md files; README.md in that dir is excluded from counts (_count_md skips README.md), so wording edits are safe, but run the full suite since 'Markdown is linted too'.
- Hooks/registry/install_settings: not involved. Interacts with F25 (same file/command, see F25 collateral).
- Behaviour change: bare `superclaude mcp` stops prompting and registers Serena immediately (previously one Enter away).

**Verify**

```bash
uv run pytest  # exit 0
uv run ruff check src/ tests/
grep -rIn -E 'interactive pick|Install all core servers|Select servers to install' src README.md docs --exclude-dir=archive --exclude-dir=__pycache__  # expect no hits
uv run superclaude mcp --dry-run  # lists/dry-runs serena only, no prompt
uv run superclaude mcp --list  # unchanged
```

<details><summary>Evidence</summary>

- install_mcp.py:33-88 MCP_SERVERS categories: serena 'core' (:48), tavily 'plugin' (:60), playwright 'plugin' (:71), chrome-devtools 'plugin' (:79). Context7 is deliberately absent (comment :34-40).
- Picker output (install_mcp.py:675-711): '1. serena - ...', '0. Install all core servers', a footer listing the 3 plugin servers with `superclaude mcp --servers <name>` hints, then click.prompt(default='0'). Both '0' and '1' give servers_to_install == ['serena'] (:713-721).
- Only caller of install_mcp_servers is main.py:404 (grep); no test exercises the picker, click.prompt or selection parsing (grep tests for install_mcp -> only test_install_mcp_prerequisites.py, which tests check_prerequisites/_node_version_ok).
- Docs describing it: README.md:112 'superclaude mcp # interactive picker (default scope: user)', README.md:364 '# Interactive installation', src/superclaude/mcp/README.md:7 ('Core auto-suggested in interactive pick'), :11 ('Core (auto-suggested by `superclaude mcp`)'), docs/PRD.md:56 describes `superclaude mcp` as writing entries for 'a small managed set' (no picker claim), install_interactive.py:148 hint 'run `superclaude mcp` to set up MCP servers' (still true after the cut).
- install_mcp.py:673-674 comment: 'default offer is core servers only. Plugin servers must be opted into explicitly via --servers.' - the policy survives as 'bare `mcp` installs core servers'.

</details>

## F15: installer migrations for old releases

`delete` · verdict **confirmed** · ~260 lines · owner decision: yes (see README)

Both installer migrations are dead weight for anyone on a recent release. (a) .gitignore -> .git/info/exclude migration, introduced b85651c 2026-05-09 at 4.5.2, has no caller outside add_git_exclude/remove_git_exclude and the uninstall dry-run; (b) LEGACY_SKILL_NAMES/find_legacy_skills, introduced 910eabd 2026-08-31 at 4.8.0, is used only by the install prune and the uninstall step 4. Caveat the audit did not state: (b) is only 33 calendar days old (today 2026-10-03), although 10 minor versions back, so this cut drops upgrade support for anyone still on <=4.7.x.

**Decision:** Two user-visible cuts. (a) .gitignore migration: a user who installed local scope before 4.5.2 (2026-05-09) and has not reinstalled keeps the stale SC block in their team .gitignore. (b) Legacy skill prune: this is the one with a real consequence. A user upgrading straight from <=4.7.x (4.8.0 shipped only 2026-08-31, 33 days ago, 10 minor releases back) keeps the auto-invocable skills confidence-check and verbalized-sampling firing from ~/.claude/skills with no source to explain them; install_paths.py:183-189 documents exactly that failure as the reason the prune exists. Is this fork's install base all past 4.8.0 (then cut both), or keep (b) for another few releases and cut only (a)?

**Changes**

- `src/superclaude/cli/install_git_exclude.py` (delete): Delete has_legacy_gitignore_block (237-246) and _migrate_legacy_gitignore (259-283).
- `src/superclaude/cli/install_git_exclude.py` (edit): add_git_exclude (285-332): drop the legacy_msg call (306-309). 'messages' now holds at most one string, so replace the list/join with direct returns, keeping the two message strings verbatim: return True, f".git/info/exclude {action} with SC {scope} block: {exclude_file}" and return False, f"Failed to write {exclude_file}: {e}". Trim docstring sentence at 292-293 to 'Silent skip on non-git directories.'
- `src/superclaude/cli/install_git_exclude.py` (edit): remove_git_exclude (335-374): drop legacy_msg (343-347) and the 'if not messages:' guards at 351-353, 355-360, 366-368 (always true now); return the existing strings directly ('Not a git repository: ...', '.git/info/exclude not found (nothing to remove): ...', '.git/info/exclude had no SC block: ...', '... SC block removed: ...', 'Failed to update ...'). Keep wording verbatim: test_no_block_present_is_success matches on 'not found'. Drop docstring line 338.
- `src/superclaude/cli/install_git_exclude.py` (edit): Module docstring 26-30: delete the 'Backward-compat: ... migrated automatically' paragraph. Comment 54-60 cites _migrate_legacy_gitignore as precedent for _LEGACY_MARKER_PAIRS: reword so it no longer names the deleted function (keep the rationale 'old text would write (local scope) into every project-scope user's exclude file'). _LEGACY_MARKER_PAIRS code itself unchanged, per instruction.
- `src/superclaude/cli/install_inventory.py` (edit): Step 8 (562-595): dry-run branch imports only has_exclude_block; if has_exclude_block(project_root): append '[DRY-RUN] Would remove SC block from .git/info/exclude', removed += 1; else '⏭️  No SC block found in {project_root}', skipped += 1. Update comment at 563 (drop '(and migrate any legacy block from .gitignore ...)').
- `src/superclaude/cli/install_paths.py` (delete): Delete the comment block + LEGACY_SKILL_NAMES + find_legacy_skills (183-209).
- `src/superclaude/cli/install_components.py` (edit): Remove 'find_legacy_skills' from the install_paths import (line 22) and delete the 'Upgrade path: drop skills ...' block in install_all (471-484). shutil stays imported (copy2/copytree/rmtree used elsewhere).
- `src/superclaude/cli/install_inventory.py` (edit): Remove 'find_legacy_skills' from the install_paths import (line 21) and delete uninstall step 4 (425-447). Do NOT renumber later steps: .claude/rules/gotchas/hooks.md:17 cites 'step 5a'.
- `src/superclaude/cli/main.py` (edit): uninstall help text 303 ('+ clean .gitignore block') and example 309 ('cleans .gitignore') become false: change to 'remove the .git/info/exclude block' / '(removes the .git/info/exclude block)'.
- `docs/features/socratic-brainstorm-skill/04-design.md` (edit): Line 43 says 'install_paths.LEGACY_SKILL_NAMES prunes skill dirs on install'; reword to past tense or drop the clause so it does not cite a deleted symbol.

**Tests**

- tests/unit/test_install_git_exclude.py: delete test_legacy_gitignore_block_migrated (233-257), test_legacy_gitignore_block_also_removed (291-308), test_has_legacy_gitignore_block_true_when_present and test_has_legacy_false_when_no_gitignore (322-336; class TestHasFunctions keeps test_has_exclude_block_true_after_add). Edit module docstring line 4 to drop 'legacy .gitignore migration'.
- tests/unit/test_cli_install.py: delete class TestLegacySkillsArePrunedOnUpgrade (728-793, four tests, all exercise only the deleted prune).
- Keep untouched: test_install_git_exclude.py:191 (non-git dir creates no .gitignore) and the find_team_ignores tests that use .gitignore legitimately (test_cli_install.py:1133-1180, test_install_git_exclude.py:505-609).

**Doc references**

- src/superclaude/cli/main.py:303, 309 (uninstall help)
- src/superclaude/cli/install_git_exclude.py:26-29, 54-60 (docstring/comment)
- src/superclaude/cli/install_inventory.py:563 (comment)
- docs/features/socratic-brainstorm-skill/04-design.md:43
- No README/ARCHITECTURE/Makefile/CHANGELOG mention of either migration (grep-verified)

**Collateral**

- No .py added or removed: the codex module-count test is unaffected by F15 alone
- uninstall Summary 'N skipped' is one lower on installs without legacy skills (not pinned by any test)
- Console-entry migration (_LEGACY_MARKER_PAIRS, is_legacy_hook_command, _legacy_scripts_notice, hook-upgrade-live-session gotcha) deliberately left alone
- After the cut, a pre-4.5.2 local-scope user keeps a stale '# >>> superclaude >>>' block in their team .gitignore forever, and a pre-4.8.0 user keeps skills/confidence-check and skills/verbalized-sampling (both auto-invocable) in ~/.claude/skills

**Verify**

```bash
grep -rnE "legacy_gitignore|LEGACY_SKILL_NAMES|find_legacy_skills|pre-removal" src tests docs --include=*.py --include=*.md | grep -v docs/archive   # expect no hits;  uv run pytest tests/unit/test_cli_install.py tests/unit/test_install_git_exclude.py -q;  uv run ruff check src/ tests/;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- git log -S_migrate_legacy_gitignore -> b85651c 2026-05-09 (pyproject 4.5.2+ajitta at that commit); 59ff880 2026-09-05 only touched it
- git log -Sfind_legacy_skills / -SLEGACY_SKILL_NAMES -> 910eabd 2026-08-31 'delete the skills layer' (pyproject 4.8.0+ajitta); current pyproject.toml:7 = 4.18.1+ajitta
- Whole-repo grep (src, tests, scripts, evals, Makefile, .github, README, docs minus archive, all *.md): has_legacy_gitignore_block only in install_git_exclude.py:237, install_inventory.py:569/573 and test_install_git_exclude.py:322-336; _migrate_legacy_gitignore only in install_git_exclude.py:259/307/345 (+ comment :57); find_legacy_skills only install_paths.py:199, install_components.py:22/474, install_inventory.py:21/426; LEGACY_SKILL_NAMES only install_paths.py:190/208 plus a prose mention in docs/features/socratic-brainstorm-skill/04-design.md:43
- No string invocation, no hooks.json/HOOKS registry/command .md/Makefile/CI reference to any of these names
- install_inventory.py:562-595 dry-run branch is the only reader of has_legacy_gitignore_block; install_inventory.py:425-447 is uninstall step 4 (also increments skipped on the not-found path, so Summary 'skipped' drops by 1 once removed)
- _LEGACY_MARKER_PAIRS, _has_any_marker, _strip_block (install_git_exclude.py:54-70, 137-155) are still used by has_exclude_block/add/remove for the exclude file and are NOT touched

</details>

## F30: uninstall_all repetition

`shrink` · verdict **modified** · ~40 lines · owner decision: yes (see README)

uninstall_all has four near-identical exists/dry_run/try-remove/except blocks (superclaude/ 363-383, commands/sc 385-412, hooks.json 449-469, .superclaude_hooks 471-487; a fifth, legacy skills 425-447, goes away with F15), but they are NOT uniform, so the audit's single _remove(path, dry_run) is not behavior-preserving. Differences: (1) dry-run text carries '(N files)' for superclaude/ (rglob) and commands/sc (glob *.md) but not for hooks.json or state_dir; (2) commands/sc also rmdirs an empty parent commands/ with its own success message '(and empty commands/)'; (3) hooks.json is unlink() not rmtree and also rmdirs an empty hooks/ silently; (4) state_dir has no 'Not found' else branch, so it never increments skipped; (5) dir paths print with a trailing '/', the file does not. A lean helper is worth ~40 lines only if the owner accepts small output normalisation.

**Decision:** Accept small uninstall output normalisation (drop '(N files)' in dry-run, add a 'Not found' + skipped count for the hook-state dir, drop the '(and empty commands/)' suffix) in exchange for ~40 fewer lines? If no, skip F30: an exact-preserving helper is bigger than the duplication.

**Changes**

- `src/superclaude/cli/install_inventory.py` (edit): Do after F15(b). Add a private helper next to _uninstall_shared_component, e.g. `_remove_path(path, dry_run, messages) -> str` returning 'removed' | 'failed', that does: dry_run -> '[DRY-RUN] Would remove: {path}'; else rmtree if is_dir() else unlink; success '✅ Removed: {path}'; except OSError '❌ Failed to remove {path}: {e}'. Caller keeps the exists() test and the counters: `if p.exists(): status = _remove_path(...); removed/failed += 1 else: messages.append(f'⏭️  Not found: {p}'); skipped += 1`. Keep the two parent-dir cleanups (commands/ and hooks/ rmdir-if-empty) as explicit 3-line post-steps after the call instead of helper flags. Net change: ~87 lines of the four blocks -> ~45.
- `src/superclaude/cli/install_inventory.py` (edit): Behavior-preserving alternative if output must not change: do not extract; the helper would need 4 knobs (count suffix, parent cleanup, missing-reporting, unlink-vs-rmtree) for 4 callers, which is more code than it saves. In that case withdraw F30.

**Tests**

- Before refactoring add ONE characterization test in tests/unit/test_cli_install.py: install_all(base_path=tmp_path, scope='project', force=True) then uninstall_all(...) and assert superclaude/, commands/, hooks/hooks.json, .superclaude_hooks are gone and success is True; plus dry_run=True leaves them and prints '[DRY-RUN] Would remove'. Today nothing would fail if a site broke.
- No existing test needs editing unless the owner wants the '(N files)' dry-run counts kept.

**Doc references**

- .claude/rules/gotchas/hooks.md:17 cites 'step 5a ... 5b' of uninstall_all; keep the step comments/numbering so the pointer stays valid (5b does not exist today, already stale)

**Collateral**

- Summary line 'N removed, M skipped' changes by +1 skipped on installs with no .superclaude_hooks dir if the helper adds a Not found line for state_dir
- Dry-run lines lose '(N files)' for superclaude/ and commands/sc/ unless a count is re-added
- commands/sc success message loses '(and empty commands/)' unless kept as a special case

**Verify**

```bash
uv run pytest tests/unit/test_cli_install.py -q;  uv run ruff check src/ tests/;  uv run superclaude uninstall --dry-run --scope local   # eyeball output before/after;  uv run pytest  # exit 0
```

<details><summary>Evidence</summary>

- install_inventory.py:363-383 rmtree + rglob file count in dry-run + Not found -> skipped
- install_inventory.py:385-412 rmtree + glob('*.md') count + parent-commands cleanup + distinct message + Not found -> skipped
- install_inventory.py:449-469 unlink + parent hooks rmdir (no message change) + no count + Not found -> skipped
- install_inventory.py:471-487 rmtree, no Not found branch (no skipped++)
- All four use `except Exception`; shared-component helper _uninstall_shared_component (267-319) and the legacy-skills block use OSError
- Test coverage of these four sites is thin: tests only assert message fragments for the hooks count (test_cli_install.py:549-572) and for output-styles (1222-1275); no test pins the superclaude/commands/hooks/state messages or the Summary counts

</details>
