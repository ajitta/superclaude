---
feature: reframing-anchoring
phase: audit
owner: ajitta
created: 2026-10-17
updated: 2026-10-17
---

# 04. ponytail-audit — Python implementation (six axes) + verification of 04a

> Split by size into 2 files (part 1 of 2): [part 2](./04-ponytail-audit-2.md). Section boundaries and content unchanged.

Base: branch `feature/reframing-anchoring`, HEAD content = `master` `7a6f771f` (4.27.2) plus the
uncommitted work under `docs/features/reframing-anchoring/`, `evals/fixtures/*`, `evals/tasks.yaml`,
`evals/run_eval.py`, `tests/unit/test_eval_harness.py`. Nothing was changed except this file.

Scope: `src/superclaude/cli/`, `src/superclaude/scripts/` (incl. `auto_improve/`, `parallel_ab/`),
`src/superclaude/hooks/`, `src/superclaude/utils/`, `src/superclaude/pytest_plugin.py`,
`evals/run_eval.py`, `tests/` (73 `.py` files).

Commands run (all read-only): `rg`, `git grep`, Python counting scripts over `tests/`, four probe
scripts against sandboxed `HOME`/`CLAUDE_PROJECT_DIR` (findings 2, 3, 4, 7), and
`uv run python -m pytest tests/unit/scripts -o addopts=` (149 passed, 42 s). Claude Code's hook
behaviour was taken from the official reference `https://code.claude.com/docs/en/hooks` (fetched
2026-10-17), not from a live session.

---

## Section 1 — verification of 04a (recovered lean report)

Verdicts: **confirmed** = the fact holds under a whole-tree grep and the cut is possible;
**confirmed, corrected** = the cut holds but a number or detail in 04a is off (noted);
**wrong** = the fact or the estimate does not hold; **conflicts** = touches a 2026-10-03 owner
keep-decision (none of the 04a items did — the auditor had already excluded them).

Totals: big items 20 → 19 confirmed (4 with corrections), 1 wrong (estimate), 0 conflicts.
Small items 34 → 34 confirmed (2 with corrections), 0 wrong, 0 conflicts.

### Big items

| # | 04a item | Verdict | Evidence (command → result) | Lines |
|---|---|---|---|---|
| 1 | delete `docs/experiments/sc-prompt-opus55-probe-2026-09-23/` | confirmed | `rg -l "sc-prompt-opus55-probe" --glob '!docs/experiments/sc-prompt-opus55-probe-2026-09-23/**' .` → only `04a-ponytail-lean-recovered.md`. 41 files, 2,637 lines counted. `rg "^import anthropic" docs/experiments` → `down/api_probe.py:7`; `anthropic` absent from `pyproject.toml` and `uv.lock`. | −2,637 |
| 2 | shrink `SECURITY.md` to ~30 lines | confirmed | 758 lines; `rg "4\.1" SECURITY.md` → `| 4.1.x | ✅ Full support |` and `**Version**: 4.1.5`. Package is 4.27.2. | −720 |
| 3 | hoist in-function imports in tests | confirmed, corrected | Count script over 73 files: 383 indented `import`/`from … import` lines (04a: 381); 157 name a module already imported at the top of the same file (04a: 43, which counted exact duplicate lines); 103 are stdlib. Top files: `test_cli_install.py` 76, `test_insight_writer.py` 47, `test_install_git_exclude.py` 44. Caveat: a few are deliberate (import after `monkeypatch`); hoist the rest. | −250 |
| 4 | parametrize copy-paste tests | confirmed | `tests/unit/test_install_settings.py:23-70`: 6 tests, each one hook dict + `assert … is True`. `tests/unit/test_file_size_guard.py:58-110`: 8 tests, each `_create_file(name, size)` + `assert result["decision"] == "approve"`. `rg -c parametrize tests` → 64 uses already, so the pattern is established. | −233 |
| 5 | merge `parallel_ab/` into one module; drop dead fields | confirmed, corrected | `runner.py:44,257`: `ParsedResult.axes` is never assigned → always `{}`; `observation.py:53`: `files_touched` never set by the runner; `runner.py:106-114,146-152`: whole-JSON and `tools_used` branches exist although `_build_cmd` always requests `stream-json` (`runner.py:86-88`); `orchestrator.py:87-89` + `aggregator.py:29-36`: obs written to disk, re-read, re-validated. Correction: "one caller per module" is wrong — `observation` is imported by runner, orchestrator, aggregator; `spec_loader` by two. The merge still stands. See also finding 9 (the round trip hides a bug). | −210 |
| 6 | `GuardVerdict` + 4 guard classes → bool/functions | confirmed | `rg '\.reason\b' src/superclaude/scripts/auto_improve/ \| grep -v guards.py` → no hits; coordinator reads only `.pass_` (`coordinator.py:96,108,171,223,236,256`). `reason` is read in `tests/unit/scripts/auto_improve/test_guards.py` only. | −70 |
| 7 | drop `run_eval._detect_refusal` copy + pin test | confirmed | `evals/run_eval.py:311-336` is a copy of `src/superclaude/utils/__init__.py:302-334`; pinned by `tests/unit/test_eval_harness.py:538-558`. The harness already runs under `uv run` and requires `superclaude` on PATH (`run_eval.py:749`), so the package import is available. | −48 |
| 8 | shrink `.github/workflows/README.md` to 5–10 lines | **wrong (estimate)** | File is 54 lines. "Local Testing" (11 lines) and "Updating Python Versions" (5) repeat `Makefile`/`AGENTS.md`; the trigger policy (why a push does not run CI), the job list and the Windows troubleshooting note are not written anywhere else. Cuttable ≈ 20 lines, not 44. | −20 |
| 9 | 7 hook scripts each read stdin → one `read_hook_input()` | confirmed | `rg -c 'isatty\(\)' src/superclaude/scripts/*.py` → 7 files, 1 each (context_loader, context_reset, destructive_guard, file_size_guard, loop_guard, prettier_hook, test_runner_hook). Each pairs it with its own `json.loads` + error branch. | −30 |
| 10 | tests build a fake HOME although `sandbox_home` is autouse | confirmed, corrected | `tests/conftest.py:8-39`: `sandbox_home` autouse sets HOME/USERPROFILE. Sites that redo it: 15 `setenv("HOME"/"USERPROFILE")` + 23 `monkeypatch.setattr(Path, "home", …)` = 38 (04a: 29); `test_scope_paths.py` alone 19. Caveat: tests that need HOME to equal a specific `tmp_path` keep their own; the rest take `sandbox_home` by name. | −40 |
| 11 | `.gitignore` duplicates, `.black/` | confirmed | Parsed 164 non-comment entries: 19 duplicate occurrences (`*.tar.gz`, `.DS_Store`, `Thumbs.db`, `uv.lock`, `docs/memory/solutions_learned.jsonl`, …); `.black/` present; `rg black pyproject.toml` → nothing. Note: `.gitignore` carries an uncommitted 12-line diff on this branch — cut after that lands. | −30 |
| 12 | drop `pytest-cov` + `[tool.coverage.*]` | confirmed | `rg -n "pytest-cov\|--cov\|coverage" pyproject.toml Makefile .github AGENTS.md` → declared `pyproject.toml:44`, config `:95-116`; never invoked by `Makefile` or `test.yml`. Two prose mentions to edit: `AGENTS.md:13`, `.github/workflows/README.md:35-37`. Not on the keep-list (keep-list has `pytest-asyncio`, a different package). | −26, −1 dep |
| 13 | 7 frontmatter parsers in tests → `md_helpers` | confirmed | Regex/`split("---")` parse sites: `md_helpers.py`, `test_agent_structure.py`, `test_output_style_structure.py`, `test_plan_checklist.py`, `test_sc_author_skill.py:31-34`, `test_sc_prompt_skill.py:26-29`, `test_cross_directory_refs.py` = 7. The two `_frontmatter` helpers are byte-identical. | −30 |
| 14 | 3 git-repo fixtures → one `git_repo` | confirmed, corrected | Fixtures named `repo` that run `git init`: `tests/unit/scripts/auto_improve/test_coordinator.py`, `test_worktree.py`, `tests/integration/auto_improve/test_e2e_smoke.py`; plus `git_repo` in `test_install_git_exclude.py` and helpers `_isolated_repo` (`test_cli_install.py`), `_real_repo` (`test_install_git_exclude.py`), `_committed_repo` (`test_insight_writer.py`). Seven, not three — the cut is larger. `tests/conftest.py` has no `git_repo` yet. | −30 |
| 15 | `_resolve_git_exclude_file` → `git rev-parse --git-path info/exclude` | confirmed, corrected | `install_git_exclude.py:189-242` parses the `.git` file and `commondir` by hand (54 lines). `rev-parse --git-path info/exclude` returns the common-dir file for linked worktrees and fails (rc 128) for a stale pointer, which maps to the current `None`. The same module already shells out to git (`:434-441`), so no new dependency. Caveat: the docstring says "no git subprocess" on purpose; install is not a hot path, so the reason does not apply here (it does apply to `utils.main_worktree_root`, which stays). | −40 |
| 16 | doctor/install repeat the console-probe checks | confirmed | `doctor.py:101-166` and `install_components.py:421-461` both branch on `probe["path"] is None` / `not probe["has_hook"]` / `version != __version__` with the same three messages in different wording. | −30 |
| 17 | drop `make verify` | confirmed | `rg -n "make verify\b" --glob '!Makefile' .` → only `make verify-drift` hits (CHANGELOG, docs). `make verify` (`Makefile:70-88`) is referenced only by its own `install` target echo and the help list. | −21 |
| 18 | `insight_writer` `-from-hook` rebuilds argv for argparse | confirmed | `insight_writer.py:860-907`: reads stdin JSON, builds a `["request", "--session-id", …]` list, then `build_parser().parse_args(argv)` at `:909`. `cmd_request`/`cmd_harvest` already accept a plain `Namespace` (`_collect_answer_once` builds one at `:730-738`). | −20 |
| 19 | 3 JSONL read loops + 3 write loops in `insight_writer` | confirmed | Readers: `:194-201`, `:313-318`, `:448-453`. Writers: `:183-185`, `:428-430`, `:463-465`. `_read_pending(path)` already takes a path (`:443`) and is used for the insights file too (`:209,220,239`). | −20 |
| 20 | multi-line set literals → `frozenset("…".split())` | confirmed (cosmetic) | Set bodies: `file_size_guard.py` 33 lines, `test_runner_hook.py` 15+3, `context_loader.py` ~150 lines across 9 literals (`_EXTERNAL_RUNNERS` 34, `VALID_FLAGS` 31, …). Line count only; no behaviour. | −100 |

### Small items

| 04a bullet | Verdict | Evidence |
|---|---|---|
| test-only `_count_shipped_hooks`, `_count_registered_hooks` | confirmed | `rg -n "_count_(shipped\|registered)_hooks" src tests` → defined `install_inventory.py:62,78`; called only in `tests/unit/test_cli_install.py:186-204,549-554`. |
| `MCP_DOCS_SKIP` empty set | confirmed | `install_components.py:46` `= set()`, read at `:216`; no writer anywhere. |
| traces of removed `target` scope | confirmed | Docstrings `install_settings.py:335,347`, `install_components.py:521`; `_rewrite_agent_memory_scope` guard `:57` and `_AGENT_MEMORY_DIRS` comment `:63-64`. CLI `click.Choice` has no `target` (`main.py:88,250`). |
| unread result keys `source_path`, `passed`, `total_ok` | confirmed, corrected | `source_path`: written `install_inventory.py:188,201,215`, read nowhere (src or tests). `total_ok`: written `verify_drift.py:207`, read nowhere. `passed` (top level, `doctor.py:74`): read only by `tests/unit/test_doctor.py`; `main.py:473-484` recomputes it from the checks. |
| unused `author_check.TYPES`, `FORMATS` | confirmed, corrected | `rg -n "\bTYPES\b\|\bFORMATS\b" src/superclaude/cli/author_check.py` → only the definitions `:27-28`. `main.py:580-590` repeats both lists inline — the better cut is to reuse them there, not delete. |
| always-0 `skipped` return | confirmed | `install_hooks` (`install_components.py:357`) sets `skipped = 0` and never increments; caller discards it (`:594`). |
| `resolve_flags` returns `(corrected, notes)` with `corrected == prompt` | confirmed | `context_loader.py:400` `corrected = prompt`, never reassigned; returned at `:452`. 9 call sites unpack it. |
| `stop_hook_active` check in PostToolUse hooks | confirmed | `prettier_hook.py:43`, `test_runner_hook.py:207`. The field exists on Stop/SubagentStop input only (`src/superclaude/hooks/README.md:206`; official reference lists it under Stop). |
| `WorktreeManager.cleanup`, `init_results_tsv` | confirmed | `rg -n "\.cleanup(\|init_results_tsv(" src tests` → `tests/unit/scripts/auto_improve/test_worktree.py` only. `coordinator._teardown` (`:127-137`) keeps the worktree on purpose; the module docstring `:9` ("cleanup on exit") is stale. |
| `make test -m "not canary"` | confirmed | `rg -n "mark.canary\|\"canary\"" tests src pyproject.toml` → no marker registered or applied; only a YAML key `t.get("canary")` in `test_eval_harness.py:207`. |
| CI repeats addopts options | confirmed | `.github/workflows/test.yml:47` `pytest -v --tb=short --color=yes` while `pyproject.toml:81-83` already sets `-v --tb=short`. (`:55` uses `-o addopts=`, so there the flags are needed.) |
| `line_of` → `bisect` | confirmed | `author_check.py:425-434` is a hand-written binary search over `offsets`; `bisect.bisect_right(offsets, index) - 1` is the same answer. |
| `verify_drift` totals → `Counter` | confirmed | `verify_drift.py:170-202`: four running totals plus a 3-branch `if` for `CLAUDE_SC.md`. |
| hand-written dedup → `dict.fromkeys` | confirmed | `context_loader.py:970-974` and `:1005-1009` (`if x not in roots: roots.append(x)`). `main.py:1152` already uses `dict.fromkeys`. |
| `_now_iso` → `isoformat(timespec="seconds")` | confirmed | `insight_writer.py:83-87`: `strftime("%z")` then manual colon insert. `datetime.now().astimezone().isoformat(timespec="seconds")` yields the same `+09:00` form. |
| `check_claude_md_import` regex → `in` | confirmed | `install_settings.py:536-544` builds two escaped regexes for a literal; two `in` checks (slash and backslash variants) do the same. |
| `temp_dir` fixture → `tmp_path` | confirmed | `tests/unit/test_file_size_guard.py:42-46` defines `temp_dir` over `tempfile`; 12 tests take it. |
| `importlib.spec_from_file_location` → plain import | confirmed | `tests/unit/test_safety_hooks.py:27`, `test_memory_staleness.py:23`, `test_portable_skills.py:33`. The script modules are importable as `superclaude.scripts.<name>`; `test_portable_skills` loads a non-package file and stays. |
| CI `curl \| sh` for uv → `astral-sh/setup-uv` | confirmed | `.github/workflows/test.yml:30,72`. |
| one-caller wrappers/params: `_mask_secrets_in_args`, `max_age_days`, `verify_drift(verbose=)`, `roots=`/`search_bundled`, `RunnerCfg.cli`, `Mutator` class, `status_mode(config)` | confirmed | `_mask_secrets_in_args`: one call `install_mcp.py:439`. `max_age_days`: every caller uses the default (`context_reset.py:48-49`, tests). `verbose=`: only gates `"files"` in the dict (`verify_drift.py:187`). `roots=`: passed by tests only (`test_context_loader.py:1064,1100,1128,1154`). `RunnerCfg.cli`: `ALLOWED_RUNNER_CLI = {"claude -p"}` (`spec_loader.py:11`). `Mutator`: one instantiation `coordinator.py:275`. `status_mode(config)`: reads only `config.repo_root` (`coordinator.py:365`); `cli.py:97-101` builds a dummy config to call it. |
| `uninstall` calls `uninstall_all` twice | confirmed | `main.py:314-320` (dry run) and `:335-341` differ only in `dry_run=`. |
| impossible `except` branches in `session_init`/`loop_guard` | confirmed | `session_init.py:30-32,92,114`: `ImportError` on `superclaude.utils`, which every other hook imports at module top. `loop_guard.py:167-171`: inner `JSONDecodeError` handler under a `main()`-wide `except Exception` (`:180-182`) that does the same thing. |
| `results_tsv._coerce` | confirmed | `results_tsv.py:86-91` compares `type_hint` to both `int` and `"int"` because `from __future__ import annotations` (`:6`) makes `fields(cls)` types strings. |
| `run_eval._run` duplication, `_result_subtype` re-parse | confirmed | `run_eval.py:263-273` repeats `subprocess.run(…)` with the same arguments `_run` (`:121-134`) takes. `_result_subtype` (`:299-308`) re-walks the stream `_parse_stream` (`:348-408`) just walked. |
| Makefile help → generated from `##` comments | confirmed (option) | `Makefile:150-175` hand-lists 20 targets; standard `grep -E '^[a-z-]+:.*##'` pattern applies. |
| 18 path constants in tests, duplicate `_all_output` | confirmed, corrected | `^[A-Z_]+ = Path(__file__)` → 32 constants in 30 files (04a: 18). `def _all_output` in `test_auto_improve_cli.py:19` and `test_cli_entrypoints.py:24`. |

Items 04a dropped itself (`CLAUDE_CONTEXT_MAX_TOKENS`, the `{"decision":"approve"}` output, merging the
eval harnesses, `uninstall_legacy.sh`, documented env switches, auto-improve flags,
`pytest-asyncio`): agreed; none re-proposed here. The `approve` output is examined as a Risk
finding below (finding 1), which is what 04a asked for.

---
