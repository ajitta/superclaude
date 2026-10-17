---
feature: lean-round
phase: implementation
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 04. Batches B1–B4 — what landed, what did not

Branch `fix/lean-round-2` on `master` `30a08be3` (v4.28.0). One commit per batch, as the plan specified. Figures are `git show --shortstat`; the net over the whole branch is `git diff --shortstat 30a08be3..HEAD`. Full `uv run pytest` and `tests/unit/scripts -o addopts=` were green after every batch; `ruff format --check` and `ruff check` clean; no CRLF written.

| Batch | Commit | Files | +/− lines | Content |
|---|---|---|---|---|
| B0 + Phase 0 | `002c3aff` | 30 | +2,026 / −1,767 | eight prior-round docs split under 25 KB ([02-b0-doc-split.md](./02-b0-doc-split.md)); this folder seeded |
| B1 | `5f7c205e` | 51 | +31 / −3,459 | zero-reference deletions: probe folder (41 files), `SECURITY.md` 757→20 lines, `pytest-cov` + coverage config, `make verify`, `MCP_DOCS_SKIP`, unread result keys, `target`-scope docstrings |
| B2 | `c46936c4` | 23 | +700 / −138 | seven defects, each with a red→green regression test (below) |
| B3 | `8a5b8c9b` | 62 | +1,282 / −1,697 | code and test lean (below) |
| B4 | `67215cd7` | 29 | +24 / −197 | routing-invariant content consolidation (below) |

Net at B4: 174 files, +4,053 / −7,248. The audit's estimate was −5,000 lines and −1 dependency; the branch removes one dependency (`pytest-cov`) and the +4,053 is dominated by the B0 split (the eight documents re-emitted as parts) and B2's tests.

## B2 — defects (audit `04-ponytail-audit-2.md` §2 numbering)

| # | Fix | Red evidence recorded |
|---|---|---|
| 5 | `SmokeGate` fallback uses `--cycle-timeout`; loop stops after `plateau_window` consecutive `smoke_fail` | `assert 30 == 45`; "smoke_fail streak did not stop the loop" |
| 6 | one `claude_projects_dir_name()` in `utils` (`[^A-Za-z0-9]` → `-`), rule derived from 98 real `~/.claude/projects/` names and the CLI's own encoder; >200-char truncation+hash not handled | `C--Users-ajitta-.claude-…` ≠ `C--Users-ajitta--claude-…` |
| 7 | prettier via `shutil.which` over `node_modules/.bin` + PATH (`prettier.cmd` on Windows); `npx` fallback dropped | WinError 193 reproduced on the absolute path; WinError 2 on the hook's relative literal — both swallowed before |
| 8 | `detect_test_command` → `(command, cwd)`; `make -C <dir>` → `make test` in that dir | `KeyError: 'cwd'`; e2e: `pwd` = `packages/api` |
| 10 | run_eval deletes `<runs>/config/<arm>/.credentials.json` in `finally` | copy present after `main()` |
| 11 | mutator `--permission-mode acceptEdits` | `'bypassPermissions' == 'acceptEdits'` |
| 17 | `utils.int_env` for `CLAUDE_CONTEXT_MAX_TOKENS` in loader and `context explain` | loader crash `invalid literal for int(): '8k'` |

## B3 — code and test lean

Done: parallel_ab (`aggregate(out, observations)` — defect 9; `--` before the prompt — defect 13; dead fields/branches; `_coerce` via `get_type_hints`; module merge skipped: 664 lines after cleanup, and `cli/main.py` imports the package); hooks (`utils.read_hook_input`/`read_hook_stdin` for seven scripts; `resolve_flags` returns notes only; `context_reset.get_cache_file` wrapper removed; unreachable `except` branches in `session_init`/`loop_guard`); auto_improve (`GuardVerdict` → `bool`; `cleanup`/`init_results_tsv` removed; `status_mode(repo_root)`); insight_writer (hook path builds the `Namespace` directly; one JSONL reader/writer; `isoformat`); run_eval (`superclaude.utils.detect_refusal`; `_parse_stream` returns the subtype; `_run` reused); cli (`_resolve_git_exclude_file` → `git rev-parse --git-path info/exclude`, install-time only, `.git` presence guard kept; one `console_script_problems()` helper for doctor and install; test-only hook counters moved to the test; `uninstall` single call with output proven byte-identical in six modes; `bisect`, `Counter`, `in` checks; `install_hooks` drops the always-0 `skipped`); tests (parametrize in `test_file_size_guard`/`test_agent_structure`/`test_portable_skills`; 16 of 18 redundant fake-HOME sites in `test_scope_paths` → `sandbox_home`; `md_helpers.split_frontmatter`/`load_frontmatter`/`markdown_body` replace seven parsers; `tmp_path`; `tests/unit/cli_helpers.all_output`).

Deviations from the audit, with reason: `author_check.TYPES`/`FORMATS` were deleted rather than reused in `main.py` — a module-level import of `author_check` pulls `yaml` and raised `import superclaude.cli.main` from ~70 ms to ~125 ms, and `main.py` is the fallback path for `superclaude hook`. The `context explain` matched-text refactor was excluded by the plan (contradiction already resolved).

In flight at the time of writing (separate commit when green): shared `git_repo` fixture (seven builders), safe in-function import hoists in tests, TRIGGER_MAP undocumented alternatives (04b #8) with positive/negative tests, dead `stop_hook_active` check in the PostToolUse hooks.

Not done, by decision or constraint: `.gitignore` duplicates and `.black/` (file held by another session), `frozenset("…".split())` rewrites (cosmetic), Makefile help generation, CI workflow edits (not in the plan), `tests/unit/scripts` default exclusion (04 §2 #12 — the native crash was not re-investigated).

## B4 — content

Done: `RULES_QUALITY.md` −453 B (the >3-files rule once; on `/sc:analyze --delegate` the loader now injects `RULES_DOCS.md`, and `RULES_INTERACTION.md` (~280 tokens) is the file that no longer fits — fitting all four needs ~1,100 more characters out of QUALITY, which is beyond duplicate removal); business-panel roster → `agents/business-panel-experts.md` as single source (`MODE_Business_Panel.md` −392 B, `core/BUSINESS_SYMBOLS.md` −7 B); `project-manager` memory path → what `/sc:save` writes; `roadmap` draft-spec stop; `<tools>` native-only lists removed in 10 commands and trimmed in 9; 33 flag-restating `<examples>` rows in 12 commands; `MODE_Orchestration.md` −218 B. Installed content delta 135,524 → 129,968 B. Local-scope install re-synced; `verify-drift` clean.

Skipped inside B4, each a decision rather than a consolidation: `memory_guide` header (04b #9 — `test_memory_guide_has_protocol` and `agent-authoring.md` pin it; the audit's "native" claim is unverified; this is the §5.1 hoist shape); `<role>`/`<does>` overlap with the description (04b #14 — the ≥30 % overlap is required by `test_content_structure`, i.e. spec'd). Deferred by Q3/Q5/Q6/Q7: see [03-deferred-evidence.md](./03-deferred-evidence.md).

## B6 so far

`core/` changed in B4 (`RULES_QUALITY.md`, `BUSINESS_SYMBOLS.md`), so `make canary-gates` is required before release; it was started after the B4 commit (4 sessions, sonnet, low effort). Result goes to `05-release-gate.md`. Spot check (I0 two tasks + existing canaries, Q1 budget) is pending.
