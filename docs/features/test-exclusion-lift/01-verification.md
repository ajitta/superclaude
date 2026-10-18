---
feature: test-exclusion-lift
phase: verification
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 01. Verification — lift the tests/unit/scripts exclusion; Dependabot

Branch fix/test-exclusion-lift from master fe3195c1. Commits: b54f21fb (intent), 10697cd1 (Dependabot), 3e64dc82 (lift). Headless sessions: **0**.

## Decision rule and reproduction record

Rule fixed in the plan before the runs finished: lift only if **eight** full-suite runs with `tests/unit/scripts/` included exit 0 — six sequential and two concurrent (two full-suite processes on the same host; "memory pressure" is the only trigger shape 7d61e9d7 recorded, and c97705c0 names no test).

Environment: Windows 11, git-bash, Python 3.13.7, pytest 9.0.2, pytest-asyncio 1.4.0 (`uv.lock` at c97705c0 had pytest-asyncio 1.3.0). Command: `uv run --no-sync pytest -q -o addopts= -p no:cacheprovider` (the `-o addopts=` clears the `--ignore` that was still in pyproject at the time).

| Run | Condition | Result |
|---|---|---|
| 1 | sequential | rc=0 3870 passed, 4 skipped in 105s (first attempt, before the loop) |
| 2 | sequential | rc=0 108s 3870 passed, 4 skipped in 103.19s (0:01:43) |
| 3 | sequential | rc=0 116s 3870 passed, 4 skipped in 110.94s (0:01:50) |
| 4 | sequential | rc=0 118s 3870 passed, 4 skipped in 111.60s (0:01:51) |
| 5 | sequential | rc=0 116s 3870 passed, 4 skipped in 112.05s (0:01:52) |
| 6 | sequential | rc=0 106s 3870 passed, 4 skipped in 101.99s (0:01:41) |
| 7 | concurrent pair | rc=0 3870 passed, 4 skipped in 116.81s (0:01:56) |
| 8 | concurrent pair | rc=0 3870 passed, 4 skipped in 116.85s (0:01:56) |

Logs: `$LOCALAPPDATA/hermes/cache/scratch/scripts-incl-run{1..8}.txt` (scratch, not committed). **8/8 clean → lifted.**

Limit: eight runs on one quiet-to-moderately-loaded developer machine do not prove the abort cannot recur; they show it is not reproducible under the recorded trigger with current versions. Revert path: `git revert 3e64dc82`. Bisect target if it returns: `tests/unit/scripts/parallel_ab/` (`test_runner.py`, `test_orchestrator.py` — the suite's only `@pytest.mark.asyncio` tests; Proactor-loop teardown on Windows is a known native-abort locus).

## The lift (3e64dc82) — every wiring site

| Site | Change |
|---|---|
| `pyproject.toml` addopts | `--ignore=tests/unit/scripts` and its comment removed |
| `Makefile` `test` | description "Run test suite" |
| `Makefile` `test-scripts` | kept as a convenience: `uv run python -m pytest tests/unit/scripts` — inherits addopts (the old `-o addopts=` would now silently drop `--strict-markers`); comment carries the history |
| `.github/workflows/test.yml` | isolated "Run scripts tests" step deleted (ubuntu never had the crash; the default run covers the dir) |
| `.github/workflows/README.md:10,29,38` | updated; troubleshooting entry names the revert and bisect path |
| `AGENTS.md:16` | rule flipped: the full run includes the directory; revert/bisect instruction |
| `docs/PRD.md` open question | struck through with the resolution pointer |
| `tests/unit/{test_auto_improve_cli,test_cli_entrypoints,test_hook_dispatch,test_cli_context}.py` | "filed at top level because scripts/ never runs" sentences removed; files stay |
| `CHANGELOG.md` `[Unreleased]` → `### Changed` | contributor-facing line |
| `.claude/insights.jsonl:174` | untouched (history) |

`git grep "ignore=tests/unit/scripts\|addopts="` over the tracked tree (excluding `docs/features`, `docs/archive`, `docs/codex`, `.claude`, `CHANGELOG.md`) → no hits.

## Checks

| Check | Result |
|---|---|
| Default `uv run --no-sync pytest -q -p no:cacheprovider` after the lift | **3870 passed, 4 skipped** (was 3730 with the exclusion; +140 = `pytest --collect-only tests/unit/scripts`) |
| `make -n test test-scripts` | exit 0 |
| `tests/unit/test_makefile_help.py`, `tests/unit/test_eval_harness.py` | 47 passed |
| `ruff format --check src tests` / `ruff check src tests` | clean |
| CRLF grep over changed files | empty |
| CI `gh workflow run Tests --ref fix/test-exclusion-lift` → run [39153742114](https://github.com/ajitta/superclaude/actions/runs/39153742114) on 3e64dc82 | **success** — Test on Python 3.10 / 3.13, Lint-plugin-doctor; 12 steps per test job (was 13) |

## Dependabot (10697cd1)

`.github/dependabot.yml`: `github-actions`, `directory: /`, monthly, `target-branch: master` (stable is the release channel; `test.yml` runs on `pull_request` to master), one grouped PR (`groups.actions.patterns: ["*"]`), prefix `chore(ci)`. YAML parses; schema fields are the documented ones. Dependabot PRs run with a read-only `GITHUB_TOKEN` — sufficient for the current workflow, which uses no secrets and writes nothing. Not verified from here: the repository's "Dependabot version updates" toggle (default on for public repos); confirm after merge under Insights → Dependency graph → Dependabot.

## Dropped

`frozenset("…".split())` rewrites — cosmetic since lean-round `04-batches.md:43`, carried through five handoffs with no reader, bug or measurement. Removed from the carried list; no code.
