# 04. ponytail-audit — Python implementation (six axes) + verification of 04a — part 2 of 2

> Continuation of [part 1](./04-ponytail-audit-1.md) (split by size; content unchanged).

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
