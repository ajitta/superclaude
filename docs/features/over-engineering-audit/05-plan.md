---
status: implementing
revised: 2026-10-03
---

# Over-Engineering Audit: Implementation Plan

**Goal:** Carry out the approved cuts from [03-analysis.md](./03-analysis.md) on branch
`feature/over-engineering-audit`. Each item lands as its own revertible commit, and the suite stays
green after every one.

**Done when:** every approved item is merged, the suite passes on Linux CI (including the isolated
`tests/unit/scripts` step), and `git grep` finds no removed symbol outside `docs/archive/` and this
folder.

**Inputs:** the item specs are in 05a–05g, one file per batch. All owner decisions were taken on
2026-10-03 ([README.md](./README.md#decisions)), and the batches below already reflect them. Where
a spec and a decision disagree, the decision wins.

**Kept or skipped, so do not implement them:**

- Kept by decision: F03, F06, F12, F14, F15, F31, F35c.
- Skipped: F30 (D17), F35m.a (low value).
- Moot: F35i. The F13 cascade deletes its file.

**Narrowed:**

- **F20:** the two env knobs stay.
- **F29:** only `version` goes.
- **F33:** `CURRENT_MCP_SERVERS` stays.
- **F36:** mypy and jmespath stay.

## Ground rules

1. **Baseline first.** `uv run pytest` must exit 0 on this branch before the first cut. CLAUDE.md allows no known failures, so a red test after a cut is that cut's regression.
2. **One commit per item**, or per item group where a batch below says so. Prefixes:
   - `refactor:` for code
   - `chore:` for repo files and CI
   - `test:` for test-only changes
   - `docs:` for doc-only changes
3. **Anchor on symbols, not line numbers.** Spec line numbers are from `57287b4` and drift after the first edit. Re-grep every reference a spec cites before deleting it. Specs are model output. For markdown sweeps, use files-with-matches mode (gotcha `grep-longline-blindspot`).
4. **Module count.** Any commit that removes a `.py` under `src/superclaude/` must also update the count in `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` §1, in the same commit. Compute it with `uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"`. Five items do this: F05, F07-b, F10, F13 (two modules: the cascade takes `inline_hooks.py` too) and F19. Revert them last-in-first-out.
5. **Checks after every commit:** `uv run pytest`, `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/`. For items that touch `auto_improve/` or `parallel_ab/`, `make test-scripts` also applies. It aborts on Windows, so Linux CI is the proof.
6. **Dependency removals:** rebuild the venv before testing: `rm -rf .venv && uv venv && uv pip install -e ".[dev]"`. Otherwise the old install hides a missing dependency.
7. **Session-start hook changes:** after a commit that changes what a hook prints, run `superclaude install --force --scope local` and `superclaude install --force --scope user` before judging the result in a new session. `make sync-*` can fail on Windows (gotcha `windows-make-sync-broken`). This branch removes no registered hook: F14 is kept.
8. **Large spec files:** four of the batch files are over 30 KB, so the Read size guard blocks reading them whole. Read one item at a time; `grep -n '^## F'` gives the offsets.

## Batches

Order runs from lowest risk to highest.

### B1

Unreferenced files and test-only cleanup. Specs: [05a](./05a-plan-b1-unreferenced.md).
Items: F04, F08, F16, F28, F35f (both halves, per D22), F22, F35j.

- No change under `src/superclaude/`.
- For F28, compare the `uv build` sdist and wheel file lists before and after the change.

### B2

Pytest and pyproject config, CI workflows, orphan root scripts. Specs: [05b](./05b-plan-b2-config-ci.md).
Items: F17, F18, F24, F09, F11, and the F02-A part of F02.

- **F17** drops `[tool.black]`, the `test` extra, the sdist exclude block, the pyproject `markers` list and the near-default `python_*` patterns.
  - **Keep `[tool.mypy]`** (D13).
  - **The `markers` list can still go.** F35c is kept, so the plugin's `pytest_configure` still registers all four markers.
- **One rewrite per shared file.** Make one rewrite each of `test.yml`, `.github/workflows/README.md` and `pyproject.toml`. F17's plugin-check comment fix belongs in the F18 rewrite.
- **F11 lands with F02-A**, because `scripts/README.md` describes the publish workflow.
- **F09:** `make translate` also goes, but in B7 with the other Makefile cuts.
- **Rebuild the venv** after scipy leaves (rule 6).

### B3

Behavior-preserving CLI internals. Specs: [05c](./05c-plan-b3-cli-internals.md).
Order: F19 → F35g with F32 (a)–(c) → F34 → F35e → F35l → F21 → F25.

- **F19 first.** It removes `install_commands.py`, which changes the module count (rule 4). F35g depends on it, because `install_commands()` is the only caller that passes `base_path=None`. F19 also rewrites the `from .install_commands import ...` lines in `install`, `uninstall` and `update`; `update` stays (D16).
- **Skip F32 (d).** F32 (c) excludes a literal lowercase `readme.md` from listings. Accept that, or keep the case-sensitive check.
- **F21:** the doctor check count drops from 6 to 5. The CI doctor job must still pass.

### B4

Hook and script internals. Specs: [05d](./05d-plan-b4-hook-internals.md).

1. **F10, F27 and F33 in one commit.** This deletes `hook_tracker.py` (module count), turns `hooks/__init__.py` into a docstring, and collapses `mcp_fallback`. Leave out F33's `CURRENT_MCP_SERVERS` sub-cut (D19).
   - Write the `hooks/__init__.py` docstring for `mcp_fallback` only, because B5's F13 cascade deletes `inline_hooks.py`.
   - Keep the `hook_executions` prune prefix in `utils` for one release.
   - Once `tests/unit/test_session_init.py` loses `TestInitHookTracker`, let ruff decide whether `MagicMock` stays imported.
2. **F35a, F35m.e, F35d, F35h.**
3. **F23 and F35k in one commit.** This is the stdlib `list`/`query`/`stats`, with `query` pretty-printed (D15). Retarget the `_working_tree_changed` tests to `_status_lines()`.
4. **F35m.b, F35m.c, F35m.d.**

F10, F35a and F35m.e rewrite the same `session_init` function, module docstring and `hooks.json` `_comment` that F35b touches in B6. The PR-status line stays (D09), so the final comment still names it.

### B5

CLI surface removals. Specs: [05e](./05e-plan-b5-cli-surface.md). Items, in order:

1. **F05:** `superclaude audit` and `make audit`.
2. **F13 with the cascade:** `superclaude agents`, `hooks/inline_hooks.py` and its tests in `tests/unit/test_hooks.py`. After B4's F10, that file has no test classes left, so delete the whole file.
3. **F29, narrowed to the `version` command.**

Notes:

- **`cli/main.py`:** edit bottom-up.
  - `import re` stays, because the `context explain` regexes still use it (F06 is kept).
  - The `parse_frontmatter` import goes with `agents` if nothing else uses it.
- **Module count:** F05 and F13 change it, and F13 counts two modules.
- **Docs move with the code:** the README.md rows for `version` (128) and `audit` (555), the `make help` audit line, and the `superclaude version` mention in the `src/superclaude/cli/__init__.py` docstring.

### B6

Hook and runtime behavior removals. Specs: [05f](./05f-plan-b6-hook-behavior.md).
Runs after B1 (F04). Order: F07-b → F20 (narrowed) → F35b.

- **F07-b** deletes `token_estimator.py`, the skills banner and `CLAUDE_SHOW_SKILLS`, plus `utils.get_skill_directories`.
  - **`context explain` is kept** (F06), so F07-b must also edit it: drop the skills disclosure line, and repoint the `estimate_tokens` import at `context_loader`. The spec marked those hunks as vanishing with F06; they now apply.
- **F20 (narrowed)** touches only `context_loader.py` and `.claude/rules/mcp-authoring.md`.
  - It removes the empty `FLAG_ALIASES` with its `resolve_flags` branch, the `MCP_FALLBACK_AVAILABLE` guard (it becomes a plain import), the same-package ImportError guards and `_BEHAVIORAL_MCPS`.
  - It keeps both env knobs and their code paths (D23): `INJECT_MODE`, `output_directive_mode` with its call branch, and `USE_INSTRUCTIONS`.
  - Skip the spec's `cli/main.py` hunk. `_CTX_LOAD_RE` and its parsing block read directive-mode output in `context explain`, and both of those stay.
  - Its edit inside `get_skill_estimates` disappears once F07-b has landed.
- **F35b** removes the git line.
  - `import subprocess` stays, because the PR-status line still uses it (D09).
  - Rule 7 applies.

### B7

Repo-level artifacts and dependencies. Specs: [05g](./05g-plan-b7-repo-and-deps.md). Each item is its own commit:

- **F01:** `okf/`, closing codex F-015.
- **F26 with F02-B:** `build-plugin`, `sync-plugin-repo`, the `PLUGIN_*` vars, `scripts/build_superclaude_plugin.py` and `make translate`, closing codex F-016. Keep `test-plugin`; it is the pytest-plugin check.
- **F36, narrowed:** remove rich, pytest-benchmark and black from the dependencies.
  - B2's F17 removed only `[tool.black]`; the black dependency itself goes here.
  - scipy already left in B2.
  - mypy and jmespath stay. Leave `eval_runner.py` untouched.
  - Rebuild the venv (rule 6).

Split the shared `docs/codex/prompting_session_raw/` edits (02, 04, 05, 06, 08) by decision: okf, plugin path and PyPI publish. The mypy backlog item F-014 stays open.

## Cross-item constraints

**Ordering**

- F04 before F07-b. F07-b edits the manual test that F04 deletes.
- F07-b before F20. F20 edits `get_skill_estimates`, which F07-b deletes.
- F19 before F35g.
- F02-A before F36.
- F17 before F36. Anchor the pyproject edits by key.
- F10 before F35a, F35b and F35m.e.
- F10 before F13. After both, `tests/unit/test_hooks.py` is empty and gets deleted.

**Same commit**

- F10 with F27 and F33.
- F11 with F02-A.
- F23 with F35k.

**Shared files.** Edit these once per batch, or anchor on symbols:

- `cli/main.py`: F05, F07-b, F13, F25, F29, F32.
- `hooks.json`: F10, F35b, F35m.d.
- `.github/workflows/README.md`: F09, F11, F18, F24.
- `pyproject.toml`: F02, F17, F36.
- The module count in doc 02 §1: F05, F07-b, F10, F13, F19.

## Collateral the specs missed

- **F10, F07-b:** `.claude/rules/gotchas/hooks.md` (`hook-path-scope`, `runtime-path-two-classes`) names `hook_tracker` and `get_skill_directories`. Reword those entries when the modules go. `memory_staleness` stays.
- **F13, F32:** `docs/UI-GUIDE.md:108` cites `src/superclaude/cli/main.py:196`. Recheck that line number after the `main.py` edits.
- **F26:** verify with `grep -E 'build-plugin|sync-plugin-repo|translate'` on `make help`, not with `grep plugin`, because `test-plugin` stays.
- **F17, F36:** when black goes, update the toolchain mentions in CLAUDE.md (the "Never `uv sync`" bullet) and in `.claude/rules/gotchas/general.md` (`lint-upgrade-attribution`). Leave the mypy mentions.
- **F18:** if F21 lands first, the doctor job must pass with 5 checks.
- **F01:** `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md` line 15 also names OKF.
- **F07-b:** `CLAUDE_SHOW_SKILLS` is documented as an opt-out. Remove it from the README and the hooks docs together with the banner.
