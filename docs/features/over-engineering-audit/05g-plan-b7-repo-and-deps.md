---
status: complete
revised: 2026-10-03
---

# B7: Repo-level artifacts and dependency narrowing

Item specs for batch B7. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b7). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F01: okf/ mirror

`delete` · verdict **confirmed** · ~1,989 lines · owner decision: yes (see README)

okf/ is 90 tracked files / 1,979 markdown lines (agents 24, commands 37, core 9, modes 10, mcp 5, output-styles 2, plus index.md, architecture.md, log.md). Nothing in the repo generates, validates or reads it; it was hand-maintained by Claude (concept frontmatter says generated.by: claude/opus-5-5; log.md cites an external 'okf-validate'). It is declared on purpose by src/superclaude/ARCHITECTURE.md:189-193 and linked from five component READMEs. It is NOT dead-by-neglect: it was re-synced 2026-08-31, 2026-09-11 and 2026-09-30 (241cdd9, 0fb49b6).

**Decision:** okf/ is a declared, recently maintained artifact (ARCHITECTURE.md:189, three re-syncs in the last five weeks, last on 2026-09-30) and docs/codex 04/08 list 'restore or discard' as an open owner decision. Confirm it is discarded and that no outside consumer (an agent or Google OKF tooling pointed at this repo) reads it.

**Changes**

- `okf/` (delete): git rm -r okf (90 files). Directory then disappears.
- `src/superclaude/ARCHITECTURE.md` (edit): Delete lines 189-193 (heading '## Machine-Navigable Catalog (OKF)' through the 'Regenerate the bundle after adding a component...' paragraph) and the blank line before it, so the file ends after the XML Component Pattern section.
- `src/superclaude/agents/README.md` (edit): Delete bullet at line 143 (`okf/superclaude/agents/index.md` - OKF v0.1 catalog ...).
- `src/superclaude/commands/README.md` (edit): Delete bullet at line 92 (okf/superclaude/commands/index.md).
- `src/superclaude/core/README.md` (edit): Delete bullet at line 38 (okf/superclaude/core/index.md).
- `src/superclaude/mcp/README.md` (edit): Delete bullet at line 78 (okf/superclaude/mcp/index.md ... dev tree only).
- `src/superclaude/modes/README.md` (edit): Delete bullet at line 57 (okf/superclaude/modes/index.md).
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): Lines 57-60 'Derived delivery' block (okf row 59; plugin row 60 goes with F02): delete the whole block. Section '### 파생 catalog와 plugin artifact' (lines 186-196, okf bullet at 188) delete. Line 86 risk text 'architecture가 선언한 파생 catalog 경로의 미갱신' drop. Do not touch the section 1 snapshot table (counts only src/ .py and md globs, unaffected).
- `docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md` (edit): Lines 170-184 ('다른 파생 전달 경로' table + paragraph): remove the okf row (176) and, with F02, the two make rows (177-178) and the paragraph (180-184); if nothing is left drop the subsection and add one line 'okf/ and plugin build discontinued, see docs/features/over-engineering-audit'.
- `docs/codex/prompting_session_raw/05_quality_gate_catalog.md` (edit): Line 82 (source component <-> tracked OKF resource) delete; lines 154-155 reword to 'derived delivery paths: none'; line 254 row 'OKF/plugin delivery' delete.
- `docs/codex/prompting_session_raw/06_behavioral_eval_playbook.md` (edit): Line 159: 'wheel-installed invocation, OKF/plugin parity' -> 'wheel-installed invocation'.
- `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md` (edit): Mark F-015 (table row 38, section 320-343) and F-016 (row 39, section 345-360) as resolved by discontinuation (move under '해결된 finding', line 362) and drop backlog item 7 (line 399). README.md:72 mention of 'OKF 카운트' can lose the OKF word.

**Tests**

- No test reads okf/. Nothing to delete or update.

**Doc references**

- src/superclaude/ARCHITECTURE.md:189-193
- src/superclaude/agents/README.md:143
- src/superclaude/commands/README.md:92
- src/superclaude/core/README.md:38
- src/superclaude/mcp/README.md:78
- src/superclaude/modes/README.md:57
- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:57-60,86,186-196
- docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:170-184
- docs/codex/prompting_session_raw/05_quality_gate_catalog.md:82,154-155,254
- docs/codex/prompting_session_raw/06_behavioral_eval_playbook.md:159
- docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:38-39,320-360,399
- docs/codex/prompting_session_raw/README.md:72
- Leave as history: docs/features/sonnet-5-5-prompting/*, docs/features/opus-5-5-default-model/*, docs/analysis/content-deletion-test-audit-*, docs/archive/*, .serena/memories/session_2026-09-11_*

**Collateral**

- No src/**/*.py added or removed: codex-module-count trap (a) does not fire
- tests/unit/test_version_consistency.py scans src/superclaude/*/README.md for hardcoded counts; removing a bullet adds none, but run the suite
- hooks.json / HOOKS registry / install_settings untouched
- okf is not installed to ~/.claude (mcp/README.md:78 says dev tree only), so no installed-copy or verify-drift effect

**Verify**

```bash
test ! -d okf && git grep -n -i okf -- . ':!docs/archive' ':!docs/features' ':!docs/analysis' ':!.serena' ':!docs/codex/prompting_session_raw/08_current_findings_and_backlog.md' (expect no output) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- find okf -type f | wc -l = 90; git ls-files okf | wc -l = 90; cat of all okf md = 1979 lines
- Whole-repo grep -i okf (excluding okf/, .git, .venv, caches) hits only: 5 src/superclaude/*/README.md bullets, ARCHITECTURE.md:189-193, docs/codex/prompting_session_raw/{02,04,05,06,08,README}, docs/features/{sonnet-5-5-prompting,opus-5-5-default-model}, docs/analysis/content-deletion-test-audit-ajitta-2026-08-13.md:190-193, docs/archive/*, .serena/memories/session_2026-09-11_*.md:104. Zero hits in tests/, evals/, Makefile, pyproject.toml, .github/, hooks.json, hook_dispatch.py, install_settings.py, src/**/*.py
- grep -i 'knowledge-catalog|Open Knowledge Format|okf-validate' outside okf/ -> only ARCHITECTURE.md:191 (spec link). No generator script exists
- ARCHITECTURE.md is 193 lines; the OKF section is the last section (heading at 189, text 191-193) and says 'Regenerate the bundle after adding a component' with no command to do so
- git log: 12 commits touching okf/; latest 0fb49b6 and 241cdd9 (2026-09-30, hand re-sync of 14 concepts); docs/features/sonnet-5-5-prompting/09-followups.md:35-37 records the re-sync as a deliberate follow-up
- docs/codex/prompting_session_raw/08:399 backlog item 7 reads 'F-015/F-016 OKF/plugin derived delivery path: restore or discard'; 05:154-155 accepts 'support discontinued is stated' as a passing outcome; 04:182-184 forbids silently excluding the path before that decision is made

</details>

## F26: dead Makefile targets

`delete` · verdict **modified** · ~50 lines · owner decision: yes (see README)

The Makefile targets translate, build-plugin and sync-plugin-repo, the PLUGIN_* vars and their help lines are dead, as claimed (README-zh.md, README-ja.md, plugins/superclaude and ../SuperClaude_Plugin are all missing). The scope is wider: scripts/build_superclaude_plugin.py (101 lines) becomes fully orphaned and should go with them, and the codex backlog lists the plugin path as an open keep-or-abandon decision (F-016). No other Makefile target references these.

**Batch note:** Also carries F02-B: `scripts/build_superclaude_plugin.py` (see F02 in B2 for its spec).

**Decision:** The codex backlog F-016 asks you to decide whether the plugin build path is kept or abandoned. Abandon (remove build-plugin, sync-plugin-repo and scripts/build_superclaude_plugin.py) or restore plugins/superclaude/manifest and keep them? Also confirm `make translate` (a documented help entry that needs the neural-cli binary from the upstream author's ~/github/neural checkout) can go; README-zh/ja do not exist.

**Changes**

- `Makefile` (edit): Line numbers current; apply bottom-up. Delete help lines 181-187 ('Plugin Packaging' header, the two make lines, blank, 'Documentation' header, `make translate` line, blank). Delete lines 142-160 (translate comment, target and trailing blank). Delete lines 118-141 (PLUGIN_DIST, PLUGIN_REPO, `.PHONY: build-plugin`, build-plugin, `.PHONY: sync-plugin-repo`, sync-plugin-repo and trailing blank). Line 1: remove the tokens `build-plugin sync-plugin-repo` from .PHONY. About 50 lines removed.
- `scripts/build_superclaude_plugin.py` (delete): Delete (101 lines). After the Makefile cut nothing calls it, and it cannot run (needs plugins/superclaude/manifest/metadata.json). Do this only if the owner picks 'abandon' in decision_needed.
- `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md` (edit): Table row at line 39 (F-016) and section 345-358: mark resolved by abandonment or move to 'resolved findings'. Line 399 item 7: 'F-015/F-016 ... 복구 또는 폐기' reduce to F-015.
- `docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md` (edit): Lines 177-178 (table rows for `make build-plugin` and `sync-plugin-repo`) and the sentence at 181-184 about plugins/superclaude/manifest/metadata.json: remove.
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): Line 60 (scripts/build_superclaude_plugin.py tree entry) and line 190 (`make build-plugin`/`sync-plugin-repo` bullet): remove. Do NOT change the §1 module count (line 32); it only counts src/superclaude/*.py.
- `docs/codex/prompting_session_raw/05_quality_gate_catalog.md` (edit): Line 254 'OKF/plugin delivery | ... + `make build-plugin` clean artifact check': drop the build-plugin part, keep the OKF parity.

**Tests**

- None. No test references these targets (grep over tests/ is empty). tests/unit/test_codex_component_map.py only pins §1 component counts; its pins are unaffected by these doc edits.

**Doc references**

- Makefile:1, 118-141, 142-160, 181-187
- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:60, 190
- docs/codex/prompting_session_raw/04_runtime_and_distribution_playbook.md:177-178, 181-184
- docs/codex/prompting_session_raw/05_quality_gate_catalog.md:254
- docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:39, 345-358, 399
- .github/workflows/readme-quality-check.yml:55 (stale README-zh/ja/kr list; guarded by os.path.exists, harmless, outside this finding)

**Collateral**

- scripts/ is not under src/superclaude, so the codex §1 module-count test does not fire.
- `make lint` runs `ruff check .` over scripts/, so deleting the script also removes it from lint scope.
- The PLUGIN_REPO ?= override cannot be hiding a working path: build-plugin always fails first.
- Adjacent, not in scope: scripts/ab_test_workflows.py and analyze_workflow_metrics.py (see F36), and Makefile:50 `-m "not canary"` selects a marker no test registers (pytest accepts it).

**Verify**

```bash
grep -nE 'build-plugin|sync-plugin-repo|translate|PLUGIN_|neural-cli' Makefile   # no output. make -n help && make help   # help prints with no plugin or translate lines. head -1 Makefile   # .PHONY without the removed names. grep -rnI -E 'build-plugin|sync-plugin-repo|build_superclaude_plugin' . --include='*.md' --include='*.py' --include='*.yml' --include='Makefile' | grep -v docs/archive   # remaining hits only in places you decided to keep. uv run pytest   # exits 0 (docs are linted; codex doc edits must keep the suite green).
```

<details><summary>Evidence</summary>

- ls README-zh.md README-ja.md plugins dist ../SuperClaude_Plugin: all 'cannot find the file'. `.venv/Scripts/python.exe scripts/build_superclaude_plugin.py` prints 'Missing plugin sources: ...\plugins\superclaude' and exits 1 (make reports 2) before writing anything (script lines 50-52); git status stayed clean.
- Makefile:118-119 PLUGIN_DIST / PLUGIN_REPO; 121-124 build-plugin; 126-140 sync-plugin-repo (depends on build-plugin, so unreachable); 143-159 translate (installs a symlink to ~/github/neural/src-tauri/target/release/neural-cli, then writes README-zh.md and README-ja.md); help lines 181-187 ('Plugin Packaging' and 'Documentation' groups).
- Makefile:1 .PHONY lists build-plugin and sync-plugin-repo (translate is not in .PHONY). Other targets are clean: audit (`superclaude audit`, line 96-98) and uninstall-legacy (`bash scripts/uninstall_legacy.sh`, file exists, 196-199) reference none of the removed names.
- Repo-wide grep for build-plugin|sync-plugin-repo|build_superclaude_plugin|PLUGIN_DIST|PLUGIN_REPO|make translate|neural-cli|README-zh|README-ja|SuperClaude_Plugin|dist/plugins: only Makefile, the script's own docstring, readme-quality-check.yml:55 (a list of README names guarded by os.path.exists) and docs/codex/prompting_session_raw/{02,04,05,08}.
- Codex backlog 08_current_findings_and_backlog.md:345-358 (F-016 'plugin build 경로 실행 불가', P1 FAIL) already records that build-plugin exits 2 and lists 'plugin 경로를 유지할지 폐기할지 명시' as the first completion gate; line 399 lists 'F-015/F-016 ... 복구 또는 폐기' as backlog item 7. The cut is the 'abandon' branch of that open decision.
- plugins/ was removed in an earlier commit (git log shows b8cd144 refactor: remove pm_agent, dead code, and legacy directories), so nothing can restore the script's inputs without new work.

</details>

## F03: install.sh

`delete` · verdict **confirmed** · ~485 lines · owner decision: yes (see README)

install.sh (485 lines, tracked) is referenced by nothing in the repo: every 'install.sh' hit outside it is a third-party installer URL (astral uv, rtk, tavily) or lives under docs/archive/legacy-userdocs. It wraps `uv pip install -e ".[dev]"` plus `uv run superclaude install/doctor`, which README steps 1-2 and `make deploy` already cover. Caveat: it is not abandoned; it was edited 2026-07-06 (12cbcb4) and 2026-09-05 (b6be725, header comment about console-entry hooks).

**Decision:** install.sh is an undocumented but maintained user-facing entry point (touched 2026-09-05) and the only script that bootstraps uv. Confirm no external instructions (blog, upstream README, teammate notes) tell people to run ./install.sh.

**Changes**

- `install.sh` (delete): 485 lines. Replacement is already documented: `uv tool install --force --editable .` then `superclaude install [--scope user|project|local]`.

**Tests**

- None reference install.sh.

**Doc references**

- No live doc links to install.sh. Do not edit docs/archive/legacy-userdocs/*.

**Collateral**

- sdist/wheel contents unchanged (pyproject sdist include list does not name install.sh)
- No src/**/*.py change; hooks and README count tests unaffected
- install.sh is the only path that auto-installs uv when missing and is POSIX-bash only; the owner's own flow is `make deploy` / `make sync-*` (CLAUDE.md)

**Verify**

```bash
git grep -n -F './install.sh' (expect no output) && git grep -n 'install\.sh' -- . ':!docs/archive' (expect only the astral/rtk/tavily URL lines) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- grep -rIn 'install\.sh' (excluding archive/okf/caches): .github/workflows/{test,quick-check}.yml (astral uv URL), .github/workflows/README.md:110, README.md:225 (rtk URL), src/superclaude/mcp/README.md:43 (tavily URL), install.sh itself. docs/archive hits: legacy-userdocs/getting-started/installation.md, legacy-userdocs/reference/mcp-server-guide.md
- No hit in tests/, Makefile, pyproject.toml (MANIFEST.in only globs src/superclaude *.sh), src/**/*.py or any command .md
- install.sh:203-204 runs `uv pip install -e ".[dev]"`; :238 `uv run superclaude install --scope ...`; :277-282 `uv run superclaude --version` / `doctor`
- README.md lines 62-90 Quick Installation: step 1 `uv tool install --force --editable .`, step 2 `superclaude install` (--scope/--force/-i/--list)
- git log -- install.sh: last two edits 12cbcb4 (audit fix) and b6be725 (one-line comment sync)

</details>

## F36: unused and replaceable dependencies

`delete` · verdict **modified** · ~296 lines · owner decision: yes (see README)

Holds with three corrections. rich (zero imports), pytest-benchmark (no benchmark fixture) and black (no gate) are removable as stated. mypy is removable but it is the declared type-check direction of the codex backlog. scipy is removable only together with deleting scripts/ab_test_workflows.py, its sole importer (and that script cannot run: its input file has no writer). jmespath can be replaced with the reduce/getitem one-liner; I diffed both on 24 expressions and the only differences are jmespath-only syntax, so the documented --metric examples and every test metric behave identically. Use `except (KeyError, TypeError)`; IndexError is unreachable with str keys. pytest-asyncio must stay.

**Decision:** (1) rich: this closes the docs/PRD.md open question ('adopt it and rewrite docs/UI-GUIDE.md, or drop the dependency?') as 'drop'. (2) jmespath: removing it narrows the documented `--metric [jmespath]` flag to dotted keys; users lose x[0], length(x), projections and quoted identifiers. Are plain/dotted keys enough? (3) mypy: removing it (and [tool.mypy]) drops the baseline command behind codex backlog F-014; keep it until you decide on a mypy gate? (4) scipy: removing it deletes scripts/ab_test_workflows.py (an A/B significance tool with no data source); confirm it can go.

**Changes**

- `pyproject.toml` (edit): dependencies (lines 34-40): delete `"rich>=13.0.0",` (37) and `"jmespath>=1.0.0",` (38). dev extra (43-51): delete pytest-benchmark (45), scipy with its '# For A/B testing' comment (47), black (48), mypy (50, gated on the mypy decision). The 'test' extra and [tool.black]/[tool.mypy] are removed under F17. Resulting dev = pytest-cov, pytest-asyncio, ruff. Keep pytest-asyncio and pyyaml/click/pytest.
- `src/superclaude/scripts/auto_improve/eval_runner.py` (edit): Replace `import jmespath` (line 16) with `import functools` (top of stdlib block) and `import operator` (alphabetical: functools, json, operator, subprocess, time). Replace lines 77-80 with `try: value = functools.reduce(operator.getitem, metric_path.split("."), payload) / except (KeyError, TypeError): return None`. Keep the `if value is None: return None` and float coercion (81-86). Reword the module docstring line 3 ('applies a jmespath expression' -> 'follows a dotted key path').
- `src/superclaude/scripts/auto_improve/cli.py` (edit): Line 66: help='jmespath expression to extract metric' -> 'dotted key path to the metric in the JSON output (e.g. summary.passed)'.
- `src/superclaude/commands/auto-improve.md` (edit): Line 12 `--metric [jmespath]` -> `--metric [dotted.key]`. The installed copy .claude/commands/sc/auto-improve.md is untracked (git ls-files .claude/commands is empty) and is refreshed by `make sync-project`.
- `evals/README.md` (edit): Line 97 'single-jmespath-metric' -> 'single-metric' (comment-level; also evals/run_eval.py:28). Optional.
- `scripts/ab_test_workflows.py` (delete): Delete (290 lines). Required if scipy goes: it is scipy's only importer, has no caller, and reads docs/memory/workflow_metrics.jsonl which nothing writes. Leave scripts/analyze_workflow_metrics.py (stdlib only) for its own finding; same dead data source.
- `src/superclaude/agents/frontend-architect.md` (edit): Line 72 gotcha `rich-only: SC's frontend dep surface = Rich (terminal UI)` becomes false. Delete the line or change to 'SC prints plain click.echo; no UI deps'. No test constrains the gotchas count. The installed .claude/agents/frontend-architect.md copy is untracked and refreshed on sync.
- `CLAUDE.md` (edit): Line 13: 'uv sync prunes black, ruff, mypy and pytest-cov' -> list what is actually in dev afterwards (ruff, pytest-cov, pytest-asyncio). Same in docs/reports/PROJECT_INDEX.md:101 and :39, and the black remark in .claude/rules/gotchas/general.md:17.
- `docs/PRD.md` (edit): Lines 116-118: remove the 'rich' open question (decision: dropped). docs/UI-GUIDE.md:99: reword the table cell now that rich is not declared ('rich is not a dependency').
- `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md` (edit): Only if mypy is dropped: F-014 (lines 37, 295-316) and 08:15 and docs/codex/prompting_session_raw/README.md:72 (which cite mypy error counts).

**Tests**

- tests/unit/scripts/auto_improve/test_eval_runner.py: no assertion changes needed (every metric used is a dotted key). Optionally rename test_extracts_jmespath_from_json_stdout (line 27) and the module docstring (line 1) to say 'dotted-path'. Optionally add one test that an unsupported expression such as 'x[0]' returns metric_value None, to pin the narrowing.
- tests/unit/scripts/ is excluded from the default pytest run (Windows native crash) but runs in CI; run it via `make test-scripts` or the Linux CI.
- tests/integration/auto_improve/test_e2e_smoke.py and tests/unit/test_auto_improve_cli.py (default run) exercise the CLI path with metric 'passed'; unchanged.
- No test imports scipy, rich, black, mypy or benchmark.

**Doc references**

- CLAUDE.md:13
- docs/reports/PROJECT_INDEX.md:39, 101
- .claude/rules/gotchas/general.md:17
- docs/PRD.md:116-118
- docs/UI-GUIDE.md:99
- src/superclaude/agents/frontend-architect.md:72
- src/superclaude/commands/auto-improve.md:12
- src/superclaude/scripts/auto_improve/cli.py:66
- src/superclaude/scripts/auto_improve/eval_runner.py:3
- evals/README.md:97, evals/run_eval.py:28
- docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:15, 37, 295-316 and docs/codex/prompting_session_raw/README.md:72 (mypy only)
- docs/research/agent-native-design-ajitta-2026-05-31.md:39 (historical, leave)

**Collateral**

- Removing the scipy script is a .py outside src/superclaude (scripts/), so the codex module-count test does not fire; no .py under src/ is added or removed.
- uv.lock is gitignored: no lock diff, but the existing .venv keeps the removed packages and could mask a missing dependency. Rebuild it to prove the new dev set suffices: `rm -rf .venv && uv venv && uv pip install -e ".[dev]"` (CLAUDE.md procedure).
- Local `uv run` re-locks against pyproject (gotcha uv-run-reverts-pip-upgrade); expect a one-time lock update.
- CI installs get lighter (no scipy/numpy/black/mypy/benchmark); not timed.
- If frontend-architect.md changes, `make sync-project` refreshes the untracked .claude copy.
- scripts/cleanup.sh:61-63 still removes .mypy_cache/.black caches; harmless.

**Verify**

```bash
rm -rf .venv && uv venv && uv pip install -e ".[dev]" && uv run pytest   # exits 0 on a clean venv. grep -rnIE 'jmespath|import rich|from rich|scipy|pytest-benchmark|pytest_benchmark' src tests scripts evals pyproject.toml Makefile .github   # no output. make test-scripts   # (or CI) auto_improve tests green, including test_eval_runner.py. uv run ruff check src/ tests/   # imports changed in eval_runner.py. uv run python -m pytest tests/integration/auto_improve -q   # default-run smoke of the metric path. uv run superclaude --help   # exit 0.
```

<details><summary>Evidence</summary>

- rich: no `import rich` or `from rich` anywhere in src, tests, scripts or evals. With rich, scipy, black, mypy and pytest_benchmark blocked (`sys.modules[name]=None`), `superclaude --help` exits 0 and every module under superclaude.* still imports. docs/PRD.md:116-118 already records 'rich>=13.0.0 is a declared runtime dependency with no import anywhere ... Adopt it or drop the dependency? owner: maintainer', and docs/UI-GUIDE.md:99 says 'rich is currently declared but unused'.
- pytest-benchmark: `\bbenchmark\b` in tests/ has no hits (no fixture use); the only mentions are pyproject.toml:45 and the plugin's performance-marker text. No CI or Makefile passes --benchmark-*.
- black: no `black` or `.[...]` consumer except pyproject.toml:48 and [tool.black] (136-152); ruff format is the formatter (Makefile:106-108, test.yml:100). Gotcha general.md:17 already calls black 'a vestigial dev-extra'.
- mypy: pyproject.toml:50 and [tool.mypy] 162-170 only. docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:295-316 (F-014) pins `uv run mypy src/superclaude/cli src/superclaude/utils src/superclaude/hooks` (35 errors at 5b6dc5b) as the baseline for a future incremental gate.
- scipy: the only import in the repo is scripts/ab_test_workflows.py:20 (`from scipy import stats`), used once at line 84 (`stats.ttest_ind`). The script has no test, Makefile, CI or doc reference. It reads docs/memory/workflow_metrics.jsonl (line 271), which does not exist; the only writer was the PM Agent (git log -S workflow_metrics.jsonl: 882a0d8, bea4bfe, b2d52c3), removed in b8cd144. The sibling scripts/analyze_workflow_metrics.py (346 lines) reads the same dead file.
- jmespath: one use, src/superclaude/scripts/auto_improve/eval_runner.py:16 (import) and 77-80 (`jmespath.search` with `except jmespath.exceptions.JMESPathError`). Comparison script (`jm_cmp.py` in the session scratchpad) of the old and proposed `_extract_metric`: identical for summary.passed, missing, score, a.b.c, pass_rate, latency_p99, x, a boolean, a null, a nested dict, a list, scalar payload, '', 'a..b', '[invalid', 'a.' (all None or equal). Different only for x[0] (1.0 vs None), x[0].v (3.0 vs None), length(x) (3.0 vs None), a quoted identifier (4.0 vs None), a trailing space ('x ' 1.0 vs None) and a hyphenated key (None vs 4.0).
- Every documented or tested metric is a plain or dotted key: src/superclaude/commands/auto-improve.md:47,48,50 ('pass_rate', 'latency_p99', 'x'), cli.py:5 and cli/main.py:974,976 ('summary.passed', 'pass_rate'), tests/integration/auto_improve/test_e2e_smoke.py:50 and tests/unit/test_auto_improve_cli.py:113 ('passed'), tests/unit/scripts/auto_improve/test_eval_runner.py ('summary.passed', 'anything', 'missing', 'x', 'score', 'a.b.c').
- Narrowed surface is advertised in four places: src/superclaude/commands/auto-improve.md:12 `--metric [jmespath]`, auto_improve/cli.py:66 help 'jmespath expression to extract metric', eval_runner.py:3 docstring, and comments in evals/README.md:97 and evals/run_eval.py:28.
- pytest-asyncio must stay: 17 `@pytest.mark.asyncio` uses in tests/unit/scripts/parallel_ab/test_orchestrator.py (7) and test_runner.py (10); test.yml:54-56 runs that directory in CI and Makefile:56-58 as `make test-scripts`. test_test_runner_hook.py only quotes the name in a fixture string.
- uv.lock is gitignored (git check-ignore uv.lock), so there is no lock diff to review.

</details>
