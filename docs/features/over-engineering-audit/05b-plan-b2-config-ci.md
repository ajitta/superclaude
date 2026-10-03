---
status: draft
revised: 2026-10-03
---

# B2: Pytest and pyproject config, CI workflows, orphan root scripts

Item specs for batch B2. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b2). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F17: unused pyproject config

`delete` · verdict **confirmed** · ~51 lines · owner decision: yes (see README)

Every pyproject.toml item named is unused or a duplicate. [tool.black] and [tool.mypy] have no gate (no Makefile, CI, pre-commit or hook runs black or mypy). The 'test' extra is a strict subset of dev (pytest is already a main dependency) and nothing installs .[test]. The sdist exclude block is a no-op. The pytest markers list duplicates pytest_configure in the plugin. python_files/python_classes/python_functions give identical collection to pytest defaults. The --strict-markers interaction is safe because the plugin registers every marker any test uses. Only [tool.mypy] needs an owner decision.

**Decision:** [tool.mypy] (and the mypy dev dependency, see F36) is the config behind the baseline commands the codex backlog F-014 pins (`uv run mypy src/superclaude/cli src/superclaude/utils src/superclaude/hooks`, 35 errors, and its 'introduce an incremental gate' direction). Drop it and rewrite F-014, or keep [tool.mypy] until you decide on a mypy gate? Everything else in F17 is decision-free.

**Changes**

- `pyproject.toml` (edit): Line numbers are for the current file; apply bottom-up. Delete 161-170 ([tool.mypy] block plus its preceding blank; gated on the mypy decision, keep it if mypy stays). Delete 136-152 ([tool.black] block plus trailing blank). Edit 160 `ignore = ["E501"]  # Line too long (handled by black)` to drop or reword the comment, e.g. `# ruff format wraps`. Delete 106-111 (`markers = [...]`). Delete 95-97 (python_files, python_classes, python_functions); keep testpaths at 94 and addopts at 98-105 (including --strict-markers and the tests/unit/scripts --ignore). Delete 84-91 (sdist `exclude = [...]`); keep `include` at 77-83. Delete 52-58 (`test = [...]` extra plus blank).
- `src/superclaude/pytest_plugin.py` (edit): No edit for F17 itself, but the plugin must keep registering the unit and integration markers (lines 17-18) because they become the only registration. The hallucination and performance registrations (19-20) go with F35c.
- `.github/workflows/test.yml` (edit): Lines 129-131 (plugin-check step comment) say 'pyproject.toml also declares the markers, so only the header proves the plugin itself loaded'. That becomes false; reword to say the plugin is now the only marker declaration. Fold into the F18 rewrite of this file.

**Tests**

- No test deletes. Baseline collection is 2719 tests; it must stay 2719 after F17 alone (2718 after F35j).

**Doc references**

- docs/reports/PROJECT_INDEX.md:39 ('pytest/black/ruff/mypy config' -> reflect what remains)
- CLAUDE.md:13 and docs/reports/PROJECT_INDEX.md:101 and .claude/rules/gotchas/general.md:17 (the black/mypy toolchain wording; shared with F36, edit once)
- docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:295-316 (F-014 mypy baseline) only if the [tool.mypy] cut is approved

**Collateral**

- No .py under src/superclaude/ is added or removed, so the codex module-count test (test_documented_count_matches_source) is unaffected.
- README component counts and hooks (hooks.json, HOOKS registry, install_settings markers) are untouched.
- tests/unit/scripts: the isolated CI step uses `-o addopts=`, so strict markers is irrelevant there; its only custom marker is asyncio, registered by pytest-asyncio (stays). Only statically checked locally (see unknowns).
- Removing the 'test' extra drops `Provides-Extra: test` from package metadata. The version '4.18.1+ajitta' is a PEP 440 local version, which PyPI rejects, so no PyPI consumer of [test] can exist from this fork.
- Do F17 markers together with F35c so the two unused marker registrations are removed in one pass.

**Verify**

```bash
uv run pytest   # exits 0; then `uv run python -m pytest --collect-only -q -p no:cacheprovider | tail -1` shows the same count as before (2719; 2718 once F35j lands). grep -nE '^\[tool\.(black|mypy)\]|^(test|markers|python_files|python_classes|python_functions) = |^exclude = ' pyproject.toml returns nothing ([tool.coverage.report] uses exclude_lines, not exclude). `uv build --sdist --out-dir <tmp>` then compare `tar tzf` member lists before and after. `uv run pytest --markers | grep -E '^@pytest.mark.(unit|integration)'` still lists both. For a belt-and-braces check of the strict path, run `uvx --from pytest==8.4.2 --with pytest-asyncio --with pyyaml --with click --with jmespath --with-editable . pytest --collect-only -q`, which must still collect everything.
```

<details><summary>Evidence</summary>

- pyproject.toml:52-57 'test' extra = pytest-cov, pytest-asyncio, scipy, pytest; the first three are in dev (43-51) and pytest is in dependencies (35). grep for '.[test' / extras across yml, md, toml, Makefile, py, sh finds no installer. publish-pypi.yml installs only build/twine/toml.
- sdist exclude is a no-op: I built the sdist twice from a scratch copy (src, tests, README, LICENSE, pyproject, .gitignore), with and without the exclude block. Both gave 224 members and the sorted member lists were identical. The only dot-entry in either is .gitignore, which the '.git*' exclude fails to drop anyway. .gitignore:2,3,21,56,68 already carry __pycache__/, *.py[cod], *.egg-info/, .venv/, .DS_Store.
- Markers used by tests: unit (auto-added), integration (tests/integration/test_cross_directory_refs.py:27 pytestmark), asyncio (pytest-asyncio registers it), parametrize and skipif (builtin). Nothing uses hallucination, performance or canary. The plugin registers all four custom ones (src/superclaude/pytest_plugin.py:17-20).
- Simulation with ini markers blanked (`pytest -o markers= --collect-only -q`): local pytest 9.0.2 gives 2719 collected (baseline 2719). On pytest 8.4.2 (`uvx --from pytest==8.4.2 --with-editable . ...`) with the plugin on it also gives 2719. On 8.4.2 with `-p no:superclaude -o markers=` it fails with 'ERROR collecting tests/integration/test_cross_directory_refs.py'. So strict-markers is satisfied only because the plugin registers unit and integration; keep those two registrations.
- python_* equal defaults: `-o 'python_files=test_*.py *_test.py' -o python_classes=Test -o python_functions=test` gives 2719 collected (baseline 2719). find tests -name '*_test.py' returns nothing; grep for `def test[^_(]` and `class test` in tests returns nothing.
- black/mypy have no gate: grep over Makefile, .github/, .pre-commit-config.yaml (no python hooks), src/ and tests/ finds none. Remaining mentions are docs: CLAUDE.md:13, docs/reports/PROJECT_INDEX.md:39 and 101, .claude/rules/gotchas/general.md:17, scripts/cleanup.sh:61-63 (harmless rm of caches) and the codex F-014 mypy baseline commands (docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:295-316).

</details>

## F35c: pytest plugin dead markers

`delete` · verdict **confirmed** · ~10 lines · owner decision: yes (see README)

The 'hallucination' and 'performance'/'benchmark' branches of the pytest plugin's auto-markers never fire, and nothing selects those markers. They can be deleted along with the two matching marker registrations. Users of the plugin lose only path-based auto-marking for files whose path contains 'hallucination', 'performance' or 'benchmark', plus the two registered marker names; this fork is not on PyPI.

**Decision:** The pytest plugin is documented as shipping 'auto-markers' (CLAUDE.md, README.md:39, PROJECT_INDEX.md:10); this removes two of its four markers. Confirm no consumer of the plugin outside this repo relies on -m hallucination or -m performance (this fork is not on PyPI: its version has the +ajitta local label).

**Changes**

- `src/superclaude/pytest_plugin.py` (edit): Delete lines 19-20 (the hallucination and performance addinivalue_line registrations). In the pytest_collection_modifyitems docstring delete the bullets at 36-37. Delete lines 48-51 (the `if "hallucination" in test_path / elif performance or benchmark` block and its blank line). Collapse lines 40-41 to `normalized_path = str(item.fspath).replace("\\", "/")` since test_path is then used once. Keep unit and integration registrations (17-18) and pytest_report_header (23-27): CI's plugin check greps that header.
- `docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md` (edit): Line 219: 'unit/integration/hallucination/performance marker가' -> 'unit/integration marker가'.

**Tests**

- No existing test covers the plugin (codex F-011 says so). No test to delete. Optional: none needed.

**Doc references**

- docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:219
- docs/features/sonnet-5-5-prompting/09-followups.md:28 (historical record of an old CI step, leave)
- pyproject.toml:109-110 (the matching markers, removed under F17)

**Collateral**

- Do together with F17: after both, the plugin holds the only marker declarations (unit, integration) and strict-markers still passes (verified in F17).
- No .py is added or removed; no module-count, README-count or hook impact.
- CI plugin-check relies on the `SuperClaude: <version>` report header; do not touch it.

**Verify**

```bash
grep -nE 'hallucination|performance|benchmark' src/superclaude/pytest_plugin.py   # no output. uv run pytest --markers | grep -E '^@pytest.mark.(unit|integration)'   # both still listed; hallucination and performance gone. uv run python -m pytest --collect-only -q -p no:cacheprovider | tail -1   # same count (2719 before F35j). uv run pytest   # exits 0. uv run python -m pytest --collect-only -q | grep -c SuperClaude   # header check still matches in CI form: `pytest --collect-only -q -p no:cacheprovider | grep -q '^SuperClaude: '`.
```

<details><summary>Evidence</summary>

- find tests -ipath '*hallucination*' -o -ipath '*performance*' -o -ipath '*benchmark*' returns nothing, so neither branch (pytest_plugin.py:48-51) matches any test path.
- `pytest --collect-only -q -m 'hallucination or performance'` selects 0 of 2719 tests ('no tests collected (2719 deselected)').
- No `-m hallucination`, `-m performance` or `@pytest.mark.(hallucination|performance)` use in tests/, Makefile, .github/, scripts/, README or docs (grep). The only `pytest.mark.hallucination/performance` occurrences are the plugin's own lines 49 and 51.
- The plugin also reads `str(item.fspath)` (absolute path, line 40), so a checkout living under a directory with 'performance' or 'benchmark' in its name would mis-mark every test (side effect, out of scope).
- README.md:74-77,420 and CLAUDE.md say the fork installs as an editable uv tool; pyproject version '4.18.1+ajitta' is a PEP 440 local version PyPI rejects, so the pytest11 plugin has no external users from this fork.
- Docs still list the markers as expected behaviour: docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:219 ('unit/integration/hallucination/performance marker가 예상 item에 붙는다').

</details>

## F18: test.yml duplication

`shrink` · verdict **confirmed** · ~100 lines · owner decision: yes (see README)

All four sub-claims hold. (1) On Python 3.10 the full suite runs twice: once as 'Run tests' and again under --cov. (2) The Codecov upload has no token and fails every run, silently because fail_ci_if_error is false. (3) lint, plugin-check and doctor-check repeat the same checkout/python/uv/install preamble and can be one job. (4) test-summary adds nothing because no required check exists. Extra finding: plugin-check's first step (`pytest --trace-config | grep -q superclaude`) passes vacuously because the runner path itself contains 'superclaude'; the second step is the real check.

**Decision:** Merging jobs and dropping test-summary changes the visible check names. None is required today (gh api: master protected:false, no protection rule, rulesets [], no integration branch on origin), but confirm you have no external setup keyed on them, e.g. protection planned for the master <- integration <- feature flow or upstream PR checks. Also confirm you do not intend to add a CODECOV_TOKEN: the upload fails today with 'Token required - not valid tokenless upload', so the cut only removes an upload that never lands.

**Changes**

- `.github/workflows/test.yml` (edit): (a) Delete lines 58-70 (the 'Run tests with coverage' step and the 'Upload coverage to Codecov' step). Keep 46-48 'Run tests' and 50-56 the isolated scripts step untouched. (b) Delete line 44 (`python -c "import pytest_cov; ..."`), orphaned once the coverage rerun is gone; keep pytest-cov in dev for local --cov use. (c) Replace lines 72-163 (jobs lint, plugin-check, doctor-check) with one job, e.g. `checks` named 'Lint, plugin and doctor checks': checkout; setup-python 3.10; Install UV (same two lines as now); `uv pip install --system -e ".[dev]"`; then steps `ruff check src/ tests/`, `ruff format --check src/ tests/`, `pytest --collect-only -q -p no:cacheprovider | grep -q "^SuperClaude: "`, `superclaude install --scope user --force`, `superclaude doctor --verbose --scope user`. Drop the vacuous `--trace-config | grep` step (124-126). (d) Delete lines 165-190 (test-summary). Expected size 190 -> ~85 lines. (e) Fix the stale comment at 129-131 (see F17). Optionally drop the redundant `-v --tb=short` flags on line 48 since addopts already supplies them; leave the isolated step's flags, since `-o addopts=` clears them.
- `.github/workflows/README.md` (edit): Lines 10-18: remove the 'Generate coverage report / Upload to Codecov' bullets and the test-summary bullet; list the merged checks job instead of lint, plugin-check, doctor-check (15-17). Lines 97-105 'Coverage Reporting': drop the sentence that CI uploads to Codecov (99); keep the local --cov instructions (101-105; they match README.md:54). Lines 122-125 'Coverage upload fails' troubleshooting: delete. Line 14: delete. Also see F24 edits to the same file.

**Tests**

- No test files change. Nothing under tests/ reads .github/workflows (grep for '.github|test.yml|workflows/' in tests/ finds nothing).

**Doc references**

- .github/workflows/README.md:10-18, 97-105, 122-125
- README.md:9-10 badge points at workflows/test.yml as a whole, so it is unaffected (keep `name: Tests`)
- docs/features/socratic-brainstorm-skill/08-implementation.md:28 says 'all 7 jobs green' (historical record; leave)

**Collateral**

- Merging renames or removes check names: 'Lint and Format Check', 'Pytest Plugin Check', 'SuperClaude Doctor Check', 'Test Summary'. None is required today (see evidence).
- The real CI-minutes win is dropping the second 3.10 suite run (~28s of the 69s job). Merging jobs mostly saves ~85 lines of YAML and two redundant installs.
- A failure in an early `checks` step would skip the later steps unless they get `if: always()`; optional.
- If F36 lands, `uv pip install -e ".[dev]"` also gets lighter (scipy, numpy, black, mypy, pytest-benchmark gone). I did not time it.
- Trap (d): the isolated tests/unit/scripts step stays and still runs in CI; locally it is `make test-scripts`.
- No .py under src/ is touched, so the module-count and README-count traps do not fire.

**Verify**

```bash
python -c "import yaml; d=yaml.safe_load(open('.github/workflows/test.yml', encoding='utf-8')); print(list(d['jobs']))"   # expect ['test', 'checks']. grep -nE 'codecov|coverage.xml|--cov|test-summary|doctor-check|plugin-check|trace-config' .github/workflows/test.yml returns nothing; grep -n 'tests/unit/scripts -o addopts=' .github/workflows/test.yml still matches. uv run ruff check src/ tests/ && uv run pytest   # exits 0 (CLAUDE.md: docs changes still need the suite). After pushing the branch, `gh workflow run test.yml --ref <branch>` and check that the 3.10 leg runs 'passed' once and that the `checks` job is green.
```

<details><summary>Evidence</summary>

- gh run view 37034552979 (push to master, 2026-10-02) job 'Test on Python 3.10': '2694 passed, 25 skipped in 21.44s' at 16:32:20, then 149 passed for the isolated scripts step, then the --cov rerun '2694 passed ... in 28.14s' at 16:32:53. Job wall time 69s versus 30s and 34s for the 3.12 and 3.11 legs, which skip the rerun.
- Same run, Codecov step: 'Commit creating failed: {"message":"Token required - not valid tokenless upload"}', again for 'Report creating failed', and 'Branch `master` is protected but no token was provided'. gh api repos/ajitta/superclaude/actions/secrets returns total_count 0. test.yml:63-70 passes no `token:`. No README badge or doc depends on Codecov (only .github/workflows/README.md:14,99,124).
- The coverage rerun gates nothing: [tool.coverage.report] has no fail_under (pyproject.toml:122-133) and codex F-014 records 'coverage.report.fail_under가 없다'. coverage.xml is gitignored and unused.
- test.yml:72-163: lint, plugin-check and doctor-check each repeat lines checkout / setup-python 3.10 / install uv / `uv pip install --system -e ".[dev]"`. Durations 8s, 14s, 10s, so merging loses no meaningful parallelism.
- test.yml:165-190 test-summary: needs all four jobs with `if: always()` and only re-asserts their results. gh api repos/ajitta/superclaude/branches/master gives protected:false; branches/master/protection gives 404 'Branch not protected'; rulesets is []; branches/integration/protection gives 'Branch not found' (no integration branch exists on origin). No required check name exists to break.
- Plugin-check step 1 (test.yml:124-126) is vacuous: the CI checkout path is /home/runner/work/superclaude/superclaude, which already contains the string. Step 2 (test.yml:133, `grep -q "^SuperClaude: "` on the report header) is the real proof the plugin loaded.
- test.yml:50-56 isolated scripts step uses `pytest tests/unit/scripts -o addopts=` and must stay verbatim.

</details>

## F24: quick-check.yml

`delete` · verdict **confirmed** · ~54 lines · owner decision: yes (see README)

quick-check.yml is a strict subset of test.yml, and it has never run on this fork. Its trigger (pull_request on [master, integration], no path filters) is contained in test.yml's triggers (push and pull_request on [master, integration], plus workflow_dispatch). Every step duplicates a test.yml step: pytest tests/unit is a subset of the full run, ruff check and ruff format --check are identical to the lint job, and the plugin grep is the weaker twin of plugin-check step 1. The only differences are `-x` and a 10-minute timeout.

**Decision:** Do you open pull requests against master or integration on this fork, or plan to (CLAUDE.md documents master <- integration <- feature/*)? On this fork quick-check has never run and the branches it targets get no PR traffic (integration does not exist on origin). If PRs return, test.yml already covers them in about 30-70s.

**Changes**

- `.github/workflows/quick-check.yml` (delete): Delete the whole file (54 lines).
- `.github/workflows/README.md` (edit): Delete the '### 2. quick-check.yml' section (lines 25-35) and renumber 3 and 4. In the pipeline diagram (lines 72-95) remove the 'Quick Check (PR only)' box and the fork to it, leaving test.yml alone. Delete lines 139-141 ('Modifying Test Strategy' bullet naming quick-check.yml) and reword so it names only test.yml. Line 146 ('Fail fast: Use -x flag in pytest for quick-check') delete. Combine with the F18 README edits in one pass.

**Tests**

- None; no test reads .github/workflows.

**Doc references**

- .github/workflows/README.md:25-35
- .github/workflows/README.md:72-95
- .github/workflows/README.md:139-141
- .github/workflows/README.md:146
- .serena/memories/session_2026-09-11_prompt-sourcing-and-gate-repairs.md:74 (committed memory; leave as history)

**Collateral**

- No test, hook, README-count or module-count impact.
- Deleting the file removes the 'Quick Check' workflow from the repo's Actions list; its past runs are none, so no history is lost.
- If you later want a fast PR signal, test.yml's lint job already provides it in ~8s.

**Verify**

```bash
ls .github/workflows   # expect publish-pypi.yml, readme-quality-check.yml, test.yml, README.md. grep -rnI -E 'quick-check|Quick Check|quick-test' .github   # no output. uv run pytest   # exits 0 (docs are linted by tests).
```

<details><summary>Evidence</summary>

- .github/workflows/quick-check.yml:3-5 `on: pull_request: branches: [master, integration]`. test.yml:3-8 `on: push: branches: [master, integration]; pull_request: branches: [master, integration]; workflow_dispatch`. Neither has a paths: filter.
- quick-check steps (lines 31-45): `pytest tests/unit/ -v --tb=short -x`, `ruff check src/ tests/`, `ruff format --check src/ tests/`, `pytest --trace-config | grep -q superclaude`. The same ruff commands are test.yml:96 and 100; the grep is test.yml:126.
- It buys no speed: lint finished in 8s and the 3.11 and 3.12 test legs in 34s and 30s (run 37034552979), and they run in parallel with each other.
- `gh run list --workflow quick-check.yml` returns [] (zero runs ever); test.yml has 29 runs, 14 push and 15 workflow_dispatch, none pull_request. quick-check has no workflow_dispatch so it cannot even be run by hand.
- References: only .github/workflows/README.md:25-35, 82-94, 140, 146 and a committed memory .serena/memories/session_2026-09-11_prompt-sourcing-and-gate-repairs.md:74 (historical).

</details>

## F09: readme-quality-check.yml

`delete` · verdict **modified** · ~315 lines · owner decision: yes (see README)

The two facts hold (the checker lists README-zh/ja/kr.md, none of which exist; the pull_request path filter 'Docs/**/*.md' matches nothing because the directory is lowercase docs/). But the workflow is NOT inert: `push: branches [main, master, develop]` has no path filter and `README*.md` matches README.md, so it runs on every master push and has succeeded 14 of 14 runs. It passes vacuously: translation_sync is hard-set to 60 when any of the four READMEs is missing, structure consistency is 100 with one file, and the link check only HEADs github.com/pypi.org/npmjs.com URLs and tests local README links. No branch protection or ruleset requires it. The cut is still sound (311 lines, inline script with Chinese comments, scoring a README set that does not exist), but it removes a green Actions check, not dead YAML.

**Decision:** This deletes a CI check that shows green on every master push (currently vacuous). Confirm no lighter README link/structure check is wanted instead, and decide separately whether the Makefile `translate` target (which generates the README-zh/ja files this workflow expects) should go too.

**Changes**

- `.github/workflows/readme-quality-check.yml` (delete): 311 lines.
- `.github/workflows/README.md` (edit): Delete section '### 4. **readme-quality-check.yml** (Existing)' at lines 41-43 (and the blank line). Do this in the same edit as F11 (lines 37-43, sections 3 and 4).

**Tests**

- None reference the workflow.

**Doc references**

- .github/workflows/README.md:41-43

**Collateral**

- Last-run artifacts (readme-quality-report.json) are workflow artifacts only; nothing local
- No src change; trap (a), (b), (c) not triggered
- Same file edit as F11 in .github/workflows/README.md; apply together to avoid a conflict

**Verify**

```bash
test ! -e .github/workflows/readme-quality-check.yml && git grep -n 'readme-quality' -- . ':!docs/archive' (expect no output) && ls .github/workflows (expect quick-check.yml test.yml README.md [+ nothing else after F11]) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- .github/workflows/readme-quality-check.yml:3-10 (pull_request paths 'README*.md','Docs/**/*.md'; push branches main/master/develop; workflow_dispatch), :55 readme_files = README.md, README-zh.md, README-ja.md, README-kr.md
- git ls-files | grep README -> only README.md (plus src/**/README.md); `ls Docs` on Windows is case-insensitive, git ls-files shows lowercase docs/ only, so 'Docs/**' matches nothing on the Linux runner
- :146-156 check_translation_sync: if not all files exist -> score 60, status WARN; overall = mean of structure, link, translation; exit 1 only if overall < 70
- gh run list --workflow readme-quality-check.yml --limit 30 -> 14 runs, all 'success', event push, latest 2026-10-02 on master merges
- gh api repos/ajitta/superclaude/branches/master/protection -> 404 'Branch not protected'; gh api .../rulesets -> []
- .github/workflows/README.md:41-43 documents it as 'Validate README quality and consistency'
- Makefile:143-159 `translate` target writes README-zh.md/README-ja.md via author-local ~/github/neural, so the files would only appear if someone runs it and commits

</details>

## F11: publish-pypi.yml and .env.example

`delete` · verdict **confirmed** · ~187 lines · owner decision: yes (see README)

publish-pypi.yml (172 lines) and .env.example (11 lines) cannot work and have never run. Version is `4.18.1+ajitta` (pyproject.toml:7 and src/superclaude/__init__.py:7), a PEP 440 local version (packaging parses local='ajitta'); PyPI does not accept local versions. The PyPI project `superclaude`/`SuperClaude` already belongs to the upstream author (Kazuki Nakai, latest 4.3.0, links to SuperClaude-Org/SuperClaude_Framework). The repo has 0 Actions secrets and 0 runs of this workflow. .env.example holds only PYPI_API_TOKEN and TEST_PYPI_API_TOKEN, and no code loads a .env file.

**Decision:** Removes the declared PyPI release path. Confirm this fork will not publish to PyPI (it cannot under the current name or version). Re-adding later means a new name and a PEP 440 version without a local label.

**Changes**

- `.github/workflows/publish-pypi.yml` (delete): 172 lines.
- `.env.example` (delete): 11 lines.
- `.github/workflows/README.md` (edit): Delete section '### 3. **publish-pypi.yml** (Existing)' at lines 37-40 (shared edit with F09's lines 41-43, so delete 37-43 and the blank line before 'Local Testing').
- `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md` (edit): F-012 (section starting line 259, table row ~35) resolved by deletion; also the backlog item 'F-011/F-012 CLI/publish functional gate' (line ~401) drops the publish half.

**Tests**

- None reference either file. tests/unit/test_version_consistency.py checks pyproject vs __version__ vs README, not PyPI.

**Doc references**

- .github/workflows/README.md:37-40
- scripts/README.md:68-79 (deleted by F02)
- docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:259-275

**Collateral**

- Deleting the workflow does not change the wheel/sdist; build backend is hatchling
- If PyPI publishing is ever wanted it needs a different distribution name and a non-local version first; recreate the workflow then

**Verify**

```bash
test ! -e .github/workflows/publish-pypi.yml && test ! -e .env.example && git grep -n -E 'publish-pypi|PYPI_API_TOKEN|\.env\.example' -- . ':!docs/archive' ':!docs/codex/prompting_session_raw/08_current_findings_and_backlog.md' (expect no output) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- pyproject.toml:7 version = "4.18.1+ajitta"; python -c 'Version("4.18.1+ajitta").local' -> 'ajitta'
- curl https://pypi.org/pypi/SuperClaude/json -> name superclaude, version 4.3.0, author Kazuki Nakai, project_urls SuperClaude-Org/SuperClaude_Framework
- gh run list --workflow publish-pypi.yml -> no runs; gh api repos/ajitta/superclaude/actions/secrets -> total_count 0
- publish-pypi.yml:5-9 triggers release + workflow_dispatch; :106,:114 use secrets.TEST_PYPI_API_TOKEN / secrets.PYPI_API_TOKEN
- grep -rIn 'dotenv|load_dotenv|\.env\.example|PYPI_API_TOKEN|TWINE_' excluding archive -> only .env.example itself, publish-pypi.yml:106/114, scripts/README.md:78-79; .gitignore:149 ignores .env
- docs/codex/prompting_session_raw/08:259-275 (F-012) already lists this workflow's release-gate gaps and an entry-point name mismatch (SuperClaude vs superclaude)
- README.md has no PyPI install instructions; install path is uv tool install from a clone

</details>

## F02: orphan root scripts/

`delete` · verdict **confirmed** · ~1,474 lines · owner decision: yes (see README)

Root scripts/ holds 9 files / 1,562 lines; everything except uninstall_legacy.sh (118 lines, called by Makefile:198) is orphaned or broken. 1,444 lines go. Additional facts the audit missed: plugins/superclaude/ was deliberately deleted in b8cd144 (97 files), leaving build_superclaude_plugin.py and two Makefile targets orphaned; validate_instructions.py still runs but prints 'FAIL: 15 files without instructions'; compare_token_usage.py needs tiktoken, which is not a declared dependency; the metrics file analyze_workflow_metrics.py reads has no producer in the repo; scipy is declared in two extras (dev and test), and ab_test_workflows.py is its only importer.

**Batch note:** B2 takes the orphan scripts and `scipy` (F02-A). `build_superclaude_plugin.py` and the Makefile plugin targets (F02-B) belong to F26 in B7.

**Decision:** Removing build-plugin and sync-plugin-repo deletes two documented `make help` commands and the (already sourceless) route to ../SuperClaude_Plugin; docs/codex F-016 lists 'keep or discard the plugin path' as an open decision. Also drops the scipy dev dependency. Confirm the sibling SuperClaude_Plugin repo is not still fed from here by hand.

**Changes**

- `scripts/ab_test_workflows.py` (delete): 290 lines
- `scripts/analyze_workflow_metrics.py` (delete): 346 lines
- `scripts/compare_token_usage.py` (delete): 225 lines
- `scripts/validate_instructions.py` (delete): 151 lines
- `scripts/build_superclaude_plugin.py` (delete): 101 lines
- `scripts/publish.sh` (delete): 94 lines
- `scripts/cleanup.sh` (delete): 100 lines
- `scripts/README.md` (delete): 137 lines; documents only publish.sh and the missing build_and_upload.py
- `Makefile` (edit): Line 1: drop 'build-plugin sync-plugin-repo' from .PHONY. Delete lines 118-141 (PLUGIN_DIST, PLUGIN_REPO, both .PHONY lines, build-plugin and sync-plugin-repo targets and the trailing blank line). Delete help lines 181-184 (Plugin Packaging header, two entries, blank echo) keeping the blank echo at 180.
- `pyproject.toml` (edit): Delete line 47 ('scipy>=1.10.0',  # For A/B testing) from [project.optional-dependencies].dev and line 56 from .test. uv.lock is gitignored so no lock diff is committed.
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): Line 60 (scripts/build_superclaude_plugin.py) goes with the 'Derived delivery' block removal in F01; section 186-196 bullets 190-196 (make build-plugin/sync-plugin-repo) go too.
- `docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md` (edit): Lines 177-178 (make build-plugin / sync-plugin-repo rows) and 180-184 paragraph; see F01.
- `docs/codex/prompting_session_raw/05_quality_gate_catalog.md` (edit): Line 83 'source payload <-> plugin manifest/artifact' and 254 'make build-plugin clean artifact check' removed.
- `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md` (edit): Resolve F-016 (lines 345-360: cites scripts/build_superclaude_plugin.py and Makefile:121-139).

**Tests**

- No test references any file here. tests/unit/scripts/ (auto_improve, parallel_ab) is unaffected, nothing to delete.

**Doc references**

- Makefile:1,118-141,181-184
- scripts/README.md (deleted)
- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:60,190-196
- docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:177-184
- docs/codex/prompting_session_raw/05_quality_gate_catalog.md:83,254
- docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:345-360
- docs/archive/analysis/scripts-dead-code-audit-ajitta-2026-05-20.md already records these as orphan/broken and decided 'leave as-is'; leave the archive untouched

**Collateral**

- No src/**/*.py change: codex-module-count trap (a) does not fire
- make lint (ruff check .) and ruff format . cover scripts/; deleting shrinks their scope, nothing else changes
- Keep scripts/uninstall_legacy.sh and the Makefile uninstall-legacy target (Makefile:196-199)
- scripts/README.md:68-79 describes publish-pypi.yml and PYPI tokens: deleted with the file, pairs with F11
- portable-skills/package.py is a separate packaging mechanism (recent commits 68f6849, 7a31734) and does not use build_superclaude_plugin.py
- Makefile 'translate' target (143-159) is adjacent but not part of this finding

**Verify**

```bash
git grep -n -E 'build-plugin|sync-plugin-repo|build_superclaude_plugin|ab_test_workflows|analyze_workflow_metrics|compare_token_usage|validate_instructions|publish\.sh|cleanup\.sh|scipy' -- . ':!docs/archive' ':!docs/codex/prompting_session_raw/08_current_findings_and_backlog.md' (expect no output); ls scripts (expect only uninstall_legacy.sh); make help | grep -c plugin (expect 0); uv run pytest (exit 0); uv run ruff check src/ tests/; make test-scripts is optional (auto_improve/parallel_ab are not touched, but it is cheap).
```

<details><summary>Evidence</summary>

- grep -rIl for each script name (excluding archive/caches): ab_test_workflows, analyze_workflow_metrics, compare_token_usage, validate_instructions -> only the file itself (and docs/archive). cleanup.sh -> only docs/archive. publish.sh -> scripts/cleanup.sh:100, scripts/README.md, docs/archive. build_and_upload -> scripts/publish.sh:19, scripts/README.md, docs/archive; the file does not exist. build_superclaude_plugin -> Makefile:124, docs/codex/{02:60,08:350}, docs/archive
- ls plugins -> not found; git log --all -- plugins -> last touch b8cd144 'remove pm_agent, dead code, and legacy directories' (97 plugins/superclaude paths deleted); build_superclaude_plugin.py:16-17,53 requires plugins/superclaude/manifest/metadata.json and exits 'Missing plugin sources'
- uv run python scripts/validate_instructions.py -> 'FAIL: 15 files without instructions'; compare_token_usage.py --help -> 'Error: tiktoken not installed'
- grep workflow_metrics outside scripts/ -> only .claude/settings.local.json (personal permission line); no producer
- grep -rn scipy src tests evals (py) -> none; whole repo non-archive: pyproject.toml:47 (dev), :56 (test), scripts/ab_test_workflows.py:20, uv.lock (gitignored via .gitignore:214)
- extra 'test' is referenced nowhere (no '.[test]' in Makefile, .github, README, docs); CI installs '.[dev]'
- Makefile: .PHONY line 1 lists build-plugin and sync-plugin-repo; PLUGIN_DIST/PLUGIN_REPO at 118-119; targets at 121-124 and 126-140; help block at 181-184
- No test imports the root scripts (tests/unit/scripts/ covers only src/superclaude/scripts/{auto_improve,parallel_ab})

</details>
