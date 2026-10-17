---
feature: reframing-anchoring
phase: audit
owner: ajitta
created: 2026-10-17
updated: 2026-10-17
---

# 04. ponytail-audit — Python implementation (six axes) + verification of 04a

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

## Section 2 — ponytail-audit (bug, risk, scale, missing test, speed, plus lean items 04a missed)

**What this repo does:** `superclaude` is a Python package that installs a set of Markdown
instruction files (commands, agents, modes, rules) into a Claude Code `.claude/` folder and
registers ten small Python "hook" scripts that Claude Code runs on events (session start, every
prompt, before and after every tool call). It also ships three headless test harnesses that drive
`claude -p`: an eval harness (`evals/run_eval.py`), a parallel A/B runner and an overnight
"auto-improve" loop. Load assumed: one developer's machine; Claude Code runs the hooks dozens of
times per session (three hook processes per Bash call); the harnesses run occasionally, by hand.
Nothing here serves many users or shares state across machines.

### Must fix

**1. Three hooks auto-approve every Bash, Edit, Write and Read call**
(`src/superclaude/scripts/destructive_guard.py:101,107,131,135`,
`src/superclaude/scripts/loop_guard.py:34-35,159,164,170,179,182`,
`src/superclaude/scripts/file_size_guard.py:110`; registered in
`src/superclaude/hooks/hooks.json:85-115`)
- What this is: a PreToolUse hook is a script Claude Code runs before a tool call; it can allow,
  deny, or ask. These three print `{"decision": "approve"}` on every call they do not block —
  including when disabled by env var, when stdin is empty, and when the input is malformed.
- Problem: per the official hooks reference, the deprecated `"approve"` maps to
  `permissionDecision: "allow"`, which "skips the permission prompt"; a hook that wants the normal
  flow must print nothing ("staying silent doesn't approve it"). `destructive_guard` and
  `loop_guard` both match `Bash`, so every shell command that is not `rm -rf /` or a force-push to
  main runs with no permission prompt — `rm -rf ~/projects`, `curl … | sh`, `git push`. Edit/Write
  are approved by `loop_guard`; Read of any file on disk (e.g. `~/.ssh/id_rsa`, normally prompted
  because it is outside the project) is approved by `file_size_guard`. The user's own
  `permissions.ask/deny` rules still apply; the default "ask me" behaviour for everything else is
  gone while superclaude is installed. The warn tier's `"ask"` survives only because `ask` outranks
  `allow` when hooks disagree.
- Fix: replace every `print(json.dumps({"decision": "approve"}))` (and `_approve()`) with
  `return` — exit 0, no output. Keep the `block` and `ask` outputs. Update the tests that assert
  `"approve"` (`test_file_size_guard.py` 17 sites, `test_loop_guard.py` 24, `test_safety_hooks.py`
  5) to assert empty stdout, and add one test per hook: "a normal input prints nothing". About −15
  lines in the hooks.
- If we skip it: the permission system is off for Bash/Edit/Write/Read on every machine with
  superclaude installed, and project-scope installs ship that to every teammate via the committed
  `settings.json`.

**2. `install` replaces a settings file it cannot parse with hooks only**
(`src/superclaude/cli/install_settings.py:40-57,357-411`)
- What this is: `_load_settings` returns `{}` when `settings.json` exists but is not valid JSON (or
  cannot be read). `merge_hooks_to_settings` then adds the hooks to that `{}` and writes it back.
- Problem: a trailing comma or a comment in `~/.claude/settings.json` turns a routine
  `superclaude install` into the loss of every `permissions`, `env`, `model`, `statusLine` entry.
  Reproduced: a settings file `{"permissions": {...}, "model": "opus",}` → after merge the file
  holds only `hooks`, and the command reports `Hooks merged to …`. No test covers an invalid file
  (`rg -n "invalid|JSONDecodeError" tests/unit/test_install_settings.py` → nothing).
- Fix: in `merge_hooks_to_settings`, if the file exists and `json.load` fails, return
  `(False, f"{settings_file} is not valid JSON; fix it or move it aside")` and write nothing.
  Same guard in `_mcp_servers_in_scope` is not needed (it only reads). One test: invalid file →
  untouched, failure message. About +6 lines.
- If we skip it: one typo in a hand-edited settings file destroys the user's Claude Code
  configuration silently.

**3. A context dropped by the token budget is marked "loaded" and never injected again**
(`src/superclaude/scripts/context_loader.py:637-658,791-804`)
- What this is: `check_triggers` records every matched context in the per-session cache
  (`mark_as_loaded`) before `output_inject_mode` decides whether it fits the 8,000-token budget or
  whether its file exists.
- Problem: a prompt like `/sc:implement --delegate … write the plan` matches RULES_QUALITY (~3,400
  tokens), RULES_DELEGATION (~2,200), RULES_DOCS (~2,600) and RULES_INTERACTION; the last one(s)
  exceed the budget, print `Budget exceeded: skipped …`, and are already in the cache. Reproduced
  with `CLAUDE_CONTEXT_MAX_TOKENS=300`: all three modes skipped, all three in the cache, the next
  prompt naming one of them injects nothing. The session never gets those rules.
- Fix: move `mark_as_loaded` out of `check_triggers` into `output_inject_mode` (and
  `output_directive_mode`), after a context has actually been printed. One test: budget-skipped
  context is not in the cache. Net ≈ 0 lines.
- If we skip it: the rule modules the framework exists to inject are silently withheld for the
  rest of the session exactly on the busiest prompts.

**4. Trigger matching ignores the "mentioned, not used" filter the flag code already has**
(`src/superclaude/scripts/context_loader.py:628-654` vs `302-322,401,886,1204`)
- What this is: `scannable_prompt` blanks fenced code, inline code, quotes and lines that start
  with an external runner, so a quoted `--plan` or `--verbose-context` does not fire. Flag notices,
  execution directives, `--verbose-context` and `--no-mcp` all use it. `check_triggers` (TRIGGER_MAP
  and COMPOSITE_FLAGS) matches the raw prompt.
- Problem: the same rule, applied in one place and not the other. Reproduced: a review prompt
  containing ```` ```\nsc --brainstorm --play\n``` ```` injects the full `MODE_Brainstorming.md`
  (tier 2, ~1,000 tokens) and the Playwright hint. A sub-agent report that quotes `--business-panel`
  injects a behavioural mode nobody asked for — the exact failure the 2026 fix for flags described.
  `main.py:985-1006` (`context explain`) mirrors the raw-prompt matching, so it also disagrees once
  this is fixed (finding 14).
- Fix: `contexts = check_triggers(scannable_prompt(trigger_prompt))` in `main()` (`:1200`), and the
  same inside `check_triggers` for `--no-mcp`. One test: a fenced `--brainstorm` triggers nothing;
  a typed one still does. +1 line.
- If we skip it: pasted text and harness turns keep changing how the session behaves.

**5. Auto-improve's smoke fallback has a hard 30-second cap and no stop on repeated failure**
(`src/superclaude/scripts/auto_improve/guards.py:82,96-98`,
`src/superclaude/scripts/auto_improve/coordinator.py:95-110`)
- What this is: without `--smoke-cmd`, `SmokeGate` runs `eval_cmd` with `FALLBACK_TIMEOUT_S = 30`
  regardless of `--cycle-timeout`. The loop records `smoke_fail` and `continue`s; only the budget
  guard can end it.
- Problem: an eval that takes 45 s (any real pytest suite) passes the baseline (600 s timeout), then
  every cycle times out at 30 s → `smoke_fail` → next cycle. An 8-hour run writes ~900 `smoke_fail`
  rows, never calls the mutator, and the morning `--status` shows "not running" with a flat metric.
  `test_guards.py:109-119` only covers the fast-pass case.
- Fix: use `self.timeout` for the fallback too (delete `FALLBACK_TIMEOUT_S`), and stop the loop
  after `plateau_window` consecutive `smoke_fail` rows (reuse `_consecutive_refusals`' pattern).
  One test: three smoke failures end `run()`. About −2 lines net.
- If we skip it: the overnight tool spends the night and the eval budget doing nothing, and the
  user cannot tell from the summary.

**6. Both Claude Code project-folder encoders miss `.` (and `_`)**
(`src/superclaude/scripts/memory_staleness.py:32-43`, `src/superclaude/scripts/insight_writer.py:102-111`)
- What this is: Claude Code stores transcripts and auto-memory under
  `~/.claude/projects/<encoded cwd>/`. Two helpers rebuild that name; both replace only `:`, `\`
  and `/` with `-`.
- Problem: Claude Code also replaces `.` (and other non-alphanumerics) — on this machine the path
  `C:\Users\ajitta\.claude\…` is stored as `C--Users-ajitta--claude-…`, and none of the 98 project
  folders contains a `.` or `_`. Any project whose path has a dot — including this repo's own
  `.claude/worktrees/<name>` worktrees — resolves to a folder that does not exist. Then
  `memory_staleness` scans nothing and never warns (a hook the owner decided to keep), and
  `insight_writer`'s transcript fallback finds no transcript. Two copies of one wrong rule.
- Fix: one helper in `superclaude.utils`: `re.sub(r"[^A-Za-z0-9-]", "-", path)`; both scripts call
  it; one test with a dotted path. About −8 lines.
- If we skip it: the stale-memory warning is silently absent for every dotted project path.

**7. The prettier hook never runs a project-local prettier on Windows**
(`src/superclaude/scripts/prettier_hook.py:19-31,55,66-67`)
- What this is: `_find_prettier` returns `node_modules/.bin/prettier` when that file exists, then
  `subprocess.run([that, "--write", file])`. The docstring says cross-platform.
- Problem: on Windows `node_modules/.bin/prettier` is a POSIX shell script; `CreateProcess`
  raises `OSError: [WinError 193] not a valid Win32 application` (reproduced), which the hook
  swallows as "prettier not installed". So on the project's primary baseline (stock Windows) the
  hook formats nothing whenever prettier is installed locally — the common case. The path is also
  relative to the hook's CWD, which `utils/__init__.py:11-13` calls a bug in hook code.
- Fix: `shutil.which("prettier", path=str(project_root() / "node_modules" / ".bin") + os.pathsep +
  os.environ["PATH"])` — `which` picks `prettier.cmd` on Windows and the script elsewhere; drop the
  manual branches. About −6 lines. One test with a fake `.bin/prettier.cmd`.
- If we skip it: a shipped hook is a no-op on the platform the project targets, and nobody sees it
  because the failure is silent by design.

**8. test_runner_hook runs pytest/npm in the hook's CWD, not in the project it detected**
(`src/superclaude/scripts/test_runner_hook.py:149-174,220-226`)
- What this is: `detect_test_command` walks up from the edited file to find `pyproject.toml`,
  `package.json` or a `Makefile`. For `make` it returns `make -C <that dir> test`; for pytest and
  npm it returns a bare `uv run python -m pytest …` / `npm test --silent`, and `main()` runs the
  string with no `cwd`.
- Problem: edit `packages/api/src/x.ts` in a monorepo (root has no test script, `packages/api`
  does) → the hook finds `packages/api/package.json`, confirms the script exists, then runs
  `npm test` in the repo root → "Missing script" or the wrong suite, reported to Claude as a
  result for `x.ts`. Same for a Python sub-project without a Makefile.
- Fix: return `(command, cwd)` from `detect_test_command` and pass `cwd=` to `subprocess.run`;
  drop the `-C` quoting (`_quote_path`) since `cwd` replaces it. About −8 lines. One test: edited
  file in a subproject → command runs there.
- If we skip it: the test result Claude reacts to can be for a different project.

**9. parallel-ab aggregates leftover observation files from earlier runs**
(`src/superclaude/scripts/parallel_ab/aggregator.py:28-37`,
`src/superclaude/scripts/parallel_ab/orchestrator.py:84-90`)
- What this is: each runner writes `obs-<variant>.json` into the output folder (default: the spec
  file's folder); `aggregate` then globs `obs-*.json` and builds the matrix and decision from
  everything it finds.
- Problem: rename or remove a variant and rerun → the old `obs-c.json` is still there and still
  counted; the "recommended winner" can be a variant that is no longer in the spec. The runner
  already returns every `Observation` (`orchestrator.py:87`); the disk round trip is what lets
  stale files in.
- Fix: `aggregate(out, observations)` taking the list `gather` returned; keep writing the files for
  the human. This is also 04a item 5's "obs round trip". About −10 lines. One test: a stray
  `obs-old.json` is not in the matrix.
- If we skip it: an A/B decision can be made on a run that never happened.

### Should fix

**10. The eval harness copies live credentials into every runs folder and leaves them there**
(`evals/run_eval.py:148-151,753-770`)
- What this is: to isolate each arm, the harness points `CLAUDE_CONFIG_DIR` at
  `<runs-dir>/config/<arm>/` and copies `~/.claude/.credentials.json` (the OAuth token) into it.
- Problem: nothing deletes the copies. `make canary-gates EVAL_ARGS="--runs-dir C:/tmp/sc-evals/gate-<ts>"`
  is the documented release step, so a new folder with a token copy accumulates per release;
  the default location is the system temp dir. A backup, a shared machine, or a `C:/tmp` the user
  later commits somewhere exposes a working login.
- Fix: wrap the arm loop in `try/finally: shutil.rmtree(runs_dir / "config", ignore_errors=True)`.
  +3 lines. One test: after `main()` returns, no `.credentials.json` under `runs_dir`.
- If we skip it: credential copies pile up outside any folder the user thinks of as sensitive.

**11. The overnight mutator runs with `bypassPermissions` and can write outside its worktree**
(`src/superclaude/scripts/auto_improve/mutator.py:81-84`, `src/superclaude/scripts/auto_improve/worktree.py:1-4`)
- What this is: the mutator is `claude -p` with tools Edit/Write/Read, `--permission-mode
  bypassPermissions`, `--add-dir <worktree>`, run unattended for hours. The design note says the
  main working tree "must remain unmodified".
- Problem: `bypassPermissions` removes the one check that enforces that: an Edit/Write with an
  absolute path two levels up (the main repo is the worktree's grand-parent) is executed with no
  prompt. The rollback (`coordinator.py:303-321`) only cleans the worktree, so such an edit survives
  every cycle.
- Fix: `--permission-mode acceptEdits`. In `-p` mode an edit outside the cwd/add-dir is then denied
  (no one can answer the prompt), edits inside are auto-accepted — the intended contract. 1-line
  change; the existing mutator tests cover the command shape.
- If we skip it: an unattended model has write access to everything the user can write.

**12. The default test run skips 149 tests, and the reason may be gone**
(`pyproject.toml:85-90`, `Makefile:46-56`, `.github/workflows/test.yml:51-55`)
- What this is: `addopts` carries `--ignore=tests/unit/scripts` because of a Windows native crash
  "temporarily". `make test` and a plain `uv run pytest` therefore never run the 11 files under
  `tests/unit/scripts` (parallel_ab, auto_improve); CI runs them in a second process on Linux.
- Problem: on this machine `uv run python -m pytest tests/unit/scripts -o addopts=` passes 149 tests
  in 42 s with no crash. A developer who breaks `coordinator.py` sees a green `uv run pytest`.
- Fix: delete the `--ignore` line and the `test-scripts` target, or — if the crash still appears
  under memory pressure — make `test:` depend on `test-scripts` so one command runs both. −3 to −8
  lines.
- If we skip it: the only tests for two of the three harnesses are run by CI alone, and the
  repo's own "verify before done" rule (`uv run pytest -q`) does not see them.

**13. parallel-ab passes the prompt as a bare trailing argument; run_eval had to add `--` for the same bug**
(`src/superclaude/scripts/parallel_ab/runner.py:94-95` vs `evals/run_eval.py:251-255`)
- What this is: `_build_cmd` appends `"<input> <flag> <extra>"` as the last argv item.
- Problem: a scenario whose input starts with a flag (`--introspect analyze X`, which is how SC
  flags are typed) is parsed by `claude` as an option and the run dies before a turn. `run_eval.py`
  fixed exactly this with `"--"` and a comment; the sibling harness did not get the fix.
- Fix: insert `"--"` before the prompt in `_build_cmd`. +1 line; update the two command-shape tests.
- If we skip it: an A/B spec testing a flag-first prompt fails in a way the matrix reports as
  "error" for every variant.

**14. `context explain` keeps a second copy of the trigger-matching rule**
(`src/superclaude/cli/main.py:985-1006`, mirrors `src/superclaude/scripts/context_loader.py:645-654`)
- What this is: `_attribute_triggers` re-walks `COMPOSITE_FLAGS` and `TRIGGER_MAP` against the
  lower-cased raw prompt to say *why* a file was injected. The comment says it "mirrors
  check_triggers".
- Problem: two copies of one rule. After finding 4 the loader matches the filtered prompt and
  `explain` the raw one, so `explain` will attribute a file the loader did not inject. (The
  `context explain` command itself is an owner keep-decision; this is about its internals.)
- Fix: have `check_triggers` return `(context_file, priority, matched_text)` and let `explain` read
  the third field from the loader's own output (print it in the `<context-inject …>` tag). About
  −20 lines in `main.py`.
- If we skip it: the dry-run tool can contradict the hook it explains.

**15. Lean cuts confirmed in Section 1**
(see the Section 1 tables for file:lines)
- What this is: 19 big items and 34 small ones from 04a, re-verified above with grep evidence.
- Problem: about 5,000 lines (2,600 of them an old experiment folder and a boilerplate
  `SECURITY.md`) and one unused dev dependency (`pytest-cov`) that must be read, linted and kept
  in sync for no return.
- Fix: cut in the order 04a proposed (1, 2, 12, 11 first — pure deletes with zero references), then
  the code items; items 5 and 9 overlap findings 9 and 1 here, so do those together.
- If we skip it: every future audit, grep and test run pays for them again.

### Nice to have

**16. `context_reset.get_cache_file` only forwards to `utils.context_cache_file`**
(`src/superclaude/scripts/context_reset.py:24-30`)
- What this is: a one-line wrapper with the same signature, used by `main.py:1149-1151` and tests.
- Problem: a pass-through layer; two names for one function.
- Fix: import `context_cache_file` where it is used, delete the wrapper. −7 lines.
- If we skip it: nothing breaks; one more name to learn.

**17. A bad `CLAUDE_CONTEXT_MAX_TOKENS` value crashes the prompt hook at import**
(`src/superclaude/scripts/context_loader.py:45-47`, mirrored at `src/superclaude/cli/main.py:1045`)
- What this is: `int(os.environ.get(...))` at module level. The knob itself is an owner keep.
- Problem: `CLAUDE_CONTEXT_MAX_TOKENS=8k` (or an empty string) → `ValueError` before `main()`
  runs, on every prompt; Claude Code shows a hook error each time and no context is injected.
- Fix: one helper `_int_env(name, default)` with `try/except ValueError`, used in both places.
  +4 lines.
- If we skip it: a typo in a shell profile disables the loader until found.

**18. `loop_guard` loses counts when parallel tool calls run its hook at once**
(`src/superclaude/scripts/loop_guard.py:115-131`)
- What this is: PostToolUse reads the state file, appends one entry, writes it back (atomically).
  Claude Code runs hooks for parallel tool calls concurrently.
- Problem: two concurrent failures load the same list and each writes it with one entry added;
  one entry is lost. Under sub-agent fan-out the breaker trips later than 5 failures or not at
  all. Fail-open, so no harm beyond a weaker guard.
- Fix: none worth its weight at one developer's load; if it ever matters, append one line per
  event to a `.jsonl` and prune on read instead of rewriting the list. Noted so nobody expects
  an exact count.
- If we skip it: the breaker is approximate under parallel calls, which is acceptable.

Left out as smaller (4): `install_mcp` passes the API key on the command line (visible in process
lists for the seconds the `claude mcp add` call runs); `insight_writer._write_pending` rewrites
the pending file non-atomically; `_tree_fingerprint` hashes only `git status` paths, so a session
that edits a file that was already dirty is "no change"; `find_unshipped` deletes any user `.md`
placed in `commands/sc/` or `superclaude/modes/` on install (documented as intended, tested).

**Verdict:** Correct in the main install/uninstall paths and well commented, but the hooks turn
Claude Code's permission prompt off for every shell command and file write, `install` can wipe a
settings file over one typo, and the prompt hook silently drops rule modules on busy prompts —
fix 1–4 before anything else; the rest is one evening of small, tested changes.

**Lean:** −5,000 lines, −1 dependencies possible (Section 1 items, re-estimated), plus about −40
lines from findings 6, 7, 8, 9, 14, 16.

**Not checked:** `src/superclaude/cli/author_check.py` (816 lines, read-only linter) and
`install_interactive.py` were skimmed, not read; `tests/` were read for structure, counts and the
fixtures named in 04a, not test by test; `evals/tasks.yaml` and `evals/fixtures/*` content;
the Markdown content under `commands/`, `agents/`, `modes/`, `core/`; `.github/workflows/test.yml`
beyond grep; no `claude -p` run, no live Claude Code session — the permission behaviour in finding
1 rests on the official hooks reference, not on observing a session; the full `uv run pytest`
suite was not run (only `tests/unit/scripts`).
