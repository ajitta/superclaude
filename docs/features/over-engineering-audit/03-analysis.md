---
status: draft
revised: 2026-10-03
---

# Analysis: over-engineering in the SuperClaude tree

## Method

Four passes on 2026-10-03, against `master` at `57287b4`:

1. **Audit.** `/ponytail:ponytail-audit` ran four parallel auditors over four areas: the CLI (`src/superclaude/cli/`); the hook scripts, `hooks/` and `utils/`; the eval and experiment tooling; and packaging, CI and tests. Each auditor tagged findings as `delete`, `stdlib`, `native`, `yagni` or `shrink`, and had to back every dead-code claim with a whole-repo grep. The eval-tooling auditor stalled, so that area was checked for reachability only (see [Not covered](#not-covered)).
2. **Spot-check.** The main session re-ran the evidence greps for the larger claims.
3. **Self-review.** A single review pass over the ranked report found two wrong findings ([Withdrawn findings](#withdrawn-findings)) and several overstated ones.
4. **Verification.** Six read-only verifiers, one per group, each tried to refute every finding and then wrote an implementation spec: the files to change, tests, doc references, collateral and a verify command. A critic pass read all six reports. It looked for ordering constraints, conflicting edits and missed collateral, and proposed the seven batches in [05-plan.md](./05-plan.md).

## Result

The audit kept 52 findings: F01–F34, the F35 nits split into F35a–F35m.e, and F36 for dependencies. Verification confirmed 41 and modified 11. It refuted none.

The line counts are verifier estimates, not measurements, and several of them include the tests that go with a cut. Together they come to about 9.9k lines. Items with no owner decision account for about 2.2k. The 26 items that need a decision are listed in [README.md](./README.md#decisions).

Up to six dependencies can go: rich, jmespath, black, mypy, scipy and pytest-benchmark. The `jq` binary can go too. mypy is tied to an open decision (D13).

## Ranked findings

Ranked by estimated lines removed. Each ID links to its spec.

| Rank | ID | Tag | Cut | Verdict | ~Lines | Owner decision |
|---|---|---|---|---|---|---|
| 1 | [F01](./05g-plan-b7-repo-and-deps.md#f01-okf-mirror) | `delete` | okf/ mirror | confirmed | 1,989 | yes |
| 2 | [F02](./05b-plan-b2-config-ci.md#f02-orphan-root-scripts) | `delete` | orphan root scripts/ | confirmed | 1,474 | yes |
| 3 | [F10](./05d-plan-b4-hook-internals.md#f10-hookshook_trackerpy) | `delete` | hooks/hook_tracker.py | confirmed | 630 |  |
| 4 | [F06](./05e-plan-b5-cli-surface.md#f06-superclaude-context-explain) | `yagni` | `superclaude context explain` | confirmed | 595 | yes |
| 5 | [F03](./05g-plan-b7-repo-and-deps.md#f03-installsh) | `delete` | install.sh | confirmed | 485 | yes |
| 6 | [F04](./05a-plan-b1-unreferenced.md#f04-testsmanual-tier-probe) | `delete` | tests/manual tier probe | confirmed | 377 |  |
| 7 | [F05](./05e-plan-b5-cli-surface.md#f05-superclaude-audit) | `yagni` | `superclaude audit` | confirmed | 375 | yes |
| 8 | [F12](./05f-plan-b6-hook-behavior.md#f12-session-start-pr-status-line) | `native` | session-start PR-status line | confirmed | 355 | yes |
| 9 | [F08](./05a-plan-b1-unreferenced.md#f08-todo-app-sample-output) | `delete` | todo-app/ sample output | confirmed | 316 |  |
| 10 | [F09](./05b-plan-b2-config-ci.md#f09-readme-quality-checkyml) | `delete` | readme-quality-check.yml | modified | 315 | yes |
| 11 | [F36](./05g-plan-b7-repo-and-deps.md#f36-unused-and-replaceable-dependencies) | `delete` | unused and replaceable dependencies | modified | 296 | yes |
| 12 | [F14](./05f-plan-b6-hook-behavior.md#f14-memory_staleness-hook) | `delete` | memory_staleness hook | confirmed | 280 | yes |
| 13 | [F15](./05e-plan-b5-cli-surface.md#f15-installer-migrations-for-old-releases) | `delete` | installer migrations for old releases | confirmed | 260 | yes |
| 14 | [F11](./05b-plan-b2-config-ci.md#f11-publish-pypiyml-and-envexample) | `delete` | publish-pypi.yml and .env.example | confirmed | 187 | yes |
| 15 | [F13](./05e-plan-b5-cli-surface.md#f13-superclaude-agents) | `delete` | `superclaude agents` | confirmed | 144 | yes |
| 16 | [F33](./05d-plan-b4-hook-internals.md#f33-mcp_fallback-surplus) | `delete` | mcp_fallback surplus | confirmed | 135 | yes |
| 17 | [F35b](./05f-plan-b6-hook-behavior.md#f35b-session_init-git-line) | `native` | session_init git line | confirmed | 132 | yes |
| 18 | [F35a](./05d-plan-b4-hook-internals.md#f35a-session_init-multi-dir-claudemd-count) | `delete` | session_init multi-dir CLAUDE.md count | confirmed | 126 |  |
| 19 | [F07](./05f-plan-b6-hook-behavior.md#f07-token_estimatorpy-and-skills-banner) | `delete` | token_estimator.py and skills banner | confirmed | 115 | yes |
| 20 | [F18](./05b-plan-b2-config-ci.md#f18-testyml-duplication) | `shrink` | test.yml duplication | confirmed | 100 | yes |
| 21 | [F20](./05f-plan-b6-hook-behavior.md#f20-context_loader-dead-knobs) | `delete` | context_loader dead knobs | confirmed | 100 | yes |
| 22 | [F16](./05a-plan-b1-unreferenced.md#f16-pre-commit-configyaml) | `delete` | .pre-commit-config.yaml | confirmed | 93 |  |
| 23 | [F19](./05c-plan-b3-cli-internals.md#f19-install_commandspy-facade) | `delete` | install_commands.py facade | confirmed | 90 |  |
| 24 | [F35h](./05d-plan-b4-hook-internals.md#f35h-file_size_guard-repeated-approve) | `shrink` | file_size_guard repeated approve | modified | 65 |  |
| 25 | [F21](./05c-plan-b3-cli-internals.md#f21-doctor-configuration-check) | `delete` | doctor Configuration check | confirmed | 61 |  |
| 26 | [F25](./05c-plan-b3-cli-internals.md#f25-mcp---status) | `delete` | `mcp --status` | modified | 56 |  |
| 27 | [F32](./05c-plan-b3-cli-internals.md#f32-duplicated-cli-helpers) | `shrink` | duplicated CLI helpers | modified | 55 |  |
| 28 | [F22](./05a-plan-b1-unreferenced.md#f22-duplicated-test-helpers) | `shrink` | duplicated test helpers | confirmed | 54 |  |
| 29 | [F24](./05b-plan-b2-config-ci.md#f24-quick-checkyml) | `delete` | quick-check.yml | confirmed | 54 | yes |
| 30 | [F17](./05b-plan-b2-config-ci.md#f17-unused-pyproject-config) | `delete` | unused pyproject config | confirmed | 51 | yes |
| 31 | [F26](./05g-plan-b7-repo-and-deps.md#f26-dead-makefile-targets) | `delete` | dead Makefile targets | modified | 50 | yes |
| 32 | [F29](./05e-plan-b5-cli-surface.md#f29-update-and-version-commands) | `yagni` | `update` and `version` commands | confirmed | 50 | yes |
| 33 | [F31](./05e-plan-b5-cli-surface.md#f31-single-item-mcp-picker) | `yagni` | single-item MCP picker | confirmed | 48 | yes |
| 34 | [F23](./05d-plan-b4-hook-internals.md#f23-insight_writer-jq-calls) | `stdlib` | insight_writer jq calls | confirmed | 45 | yes |
| 35 | [F28](./05a-plan-b1-unreferenced.md#f28-manifestin-and-setuppy) | `delete` | MANIFEST.in and setup.py | modified | 44 |  |
| 36 | [F30](./05e-plan-b5-cli-surface.md#f30-uninstall_all-repetition) | `shrink` | uninstall_all repetition | modified | 40 | yes |
| 37 | [F27](./05d-plan-b4-hook-internals.md#f27-hooks__init__py-lazy-re-exports) | `yagni` | hooks/__init__.py lazy re-exports | confirmed | 39 |  |
| 38 | [F35e](./05c-plan-b3-cli-internals.md#f35e-dead-mcp-registry-keys) | `delete` | dead MCP registry keys | confirmed | 37 |  |
| 39 | [F35d](./05d-plan-b4-hook-internals.md#f35d-loop_guard-hand-rolled-atomic-write) | `shrink` | loop_guard hand-rolled atomic write | modified | 27 |  |
| 40 | [F35g](./05c-plan-b3-cli-internals.md#f35g-base_pathnone-fallbacks) | `yagni` | base_path=None fallbacks | confirmed | 25 |  |
| 41 | [F35f](./05a-plan-b1-unreferenced.md#f35f-fundingyml-and-agent-placeholder) | `delete` | FUNDING.yml and .agent placeholder | confirmed | 22 | yes |
| 42 | [F34](./05c-plan-b3-cli-internals.md#f34-duplicated-hook-ownership-predicate) | `shrink` | duplicated hook-ownership predicate | confirmed | 20 |  |
| 43 | [F35l](./05c-plan-b3-cli-internals.md#f35l-dead-returns-and-params) | `delete` | dead returns and params | confirmed | 20 |  |
| 44 | [F35j](./05a-plan-b1-unreferenced.md#f35j-rules_schemas-fixture) | `delete` | rules_schemas fixture | confirmed | 16 |  |
| 45 | [F35i](./05e-plan-b5-cli-surface.md#f35i-has_yaml-fallback) | `delete` | HAS_YAML fallback | confirmed | 14 |  |
| 46 | [F35m.c](./05d-plan-b4-hook-internals.md#f35mc-find_migration_reference) | `stdlib` | find_migration_reference | confirmed | 11 |  |
| 47 | [F35c](./05b-plan-b2-config-ci.md#f35c-pytest-plugin-dead-markers) | `delete` | pytest plugin dead markers | confirmed | 10 | yes |
| 48 | [F35k](./05d-plan-b4-hook-internals.md#f35k-_working_tree_changed) | `delete` | _working_tree_changed | modified | 8 |  |
| 49 | [F35m.b](./05d-plan-b4-hook-internals.md#f35mb-double-stdin-json-parse) | `shrink` | double stdin JSON parse | confirmed | 8 |  |
| 50 | [F35m.a](./05d-plan-b4-hook-internals.md#f35ma-context_resetget_cache_file) | `shrink` | context_reset.get_cache_file | modified | 7 |  |
| 51 | [F35m.d](./05d-plan-b4-hook-internals.md#f35md-hooksjson-unused-keys) | `delete` | hooks.json unused keys | confirmed | 7 |  |
| 52 | [F35m.e](./05d-plan-b4-hook-internals.md#f35me-context-reminder-print) | `delete` | /context reminder print | confirmed | 3 |  |

## Withdrawn findings

The first report listed two findings that turned out to be wrong. They are not in the table.

- **`tests/unit/scripts/` never runs.** False. `pyproject.toml` excludes it only from the default run, because of a Windows-only native abort. CI runs it in a separate process (`.github/workflows/test.yml`, the "Run scripts tests (isolated)" step), and so does `make test-scripts` locally. `pytest-asyncio`, which those tests use, therefore stays.
- **`portable-skills/plugins/` and `releases/*.zip` are generated copies to gitignore.** False. `.claude-plugin/marketplace.json` uses `./portable-skills/plugins/<name>` as the plugin source. claude.ai's marketplace skips a folder that has no `.claude-plugin/plugin.json`, and the portable-skills README links the zips for upload. The `portable-skills/package.py` docstring explains why the skill folder itself cannot carry the manifest.

## Corrections from verification

Eleven findings hold only in part or at a different size. The full reasoning is in each spec.

- **F09:** the workflow is not inert. It runs on every push to master and passes vacuously, so deleting it removes a visible green check.
- **F25:** `mcp --status` adds a Fallback column that `--list` lacks. That column is already wrong for chrome-devtools.
- **F26:** the cut is wider than first stated. `scripts/build_superclaude_plugin.py` goes with the Makefile plugin targets.
- **F28:** MANIFEST.in is worse than reported. 15 of its 30 path entries are missing, not 5.
- **F30:** the four uninstall blocks differ in their messages and counters. A single helper changes the output, so F30 waits for a decision (D17).
- **F32:** the hand-rolled `*.md` glob appears at 15 sites, not ~12, and `shipped_md_names` is already the shared helper. Collapsing `_get_source_dir` alone is not worth doing.
- **F35d:** `_save_state` stays as a thin fail-open wrapper around `atomic_write_json`, because tests call it directly.
- **F35h:** there are 10 duplicated prints, not 8. The small-file and config-extension exemptions are also dead logic, because nothing under 30 KB can block.
- **F35k:** the tests for `_working_tree_changed` are the only direct coverage of `_status_lines()`. Retarget them; do not delete them.
- **F35m.a:** saving 7 lines would ripple across three files. Recommended: skip.
- **F36:**
  - jmespath can be replaced with a `functools.reduce` lookup. A diff over 24 expressions found differences only in jmespath-only syntax. Use `except (KeyError, TypeError)`.
  - mypy backs the codex F-014 baseline.
  - scipy goes only together with `scripts/ab_test_workflows.py`.

Two confirmed findings were also narrowed during the self-review:

- **F07:** four of the module's nine functions are uncalled. The remaining functions feed the skills banner, which is the only place a full-load token estimate appears.
- **F12:** the Claude Code footer PR badge exists (since v2.1.20; code.claude.com/docs/en/interactive-mode, "PR review status"), but only the human sees it. SessionStart output reaches the model.

## Not covered

- The internals of `src/superclaude/scripts/auto_improve/`, `scripts/parallel_ab/`, `evals/run_eval.py`, `portable-skills/package.py` and `docs/experiments/**/*.py`. These were checked for reachability only, and all are live: auto_improve and parallel_ab through their CLI subcommands and `/sc:auto-improve`, run_eval through `tests/unit/test_eval_harness.py`.
- Markdown content: the framework's commands, agents and modes (the product), `docs/` and `docs/archive/`.

## Limits of the evidence

- The verifiers were read-only. Nobody ran pytest, ruff or `uv build` for these specs, so every "suite stays green" expectation is a prediction until a batch lands.
- The GitHub, PyPI and Codecov facts come from the verifiers' own `gh` calls and were not re-checked: run counts, branch protection, rulesets and the Codecov token error.
- External consumers cannot be grepped from this repo:
  - tools or agents that read `okf/`
  - outside instructions to run `./install.sh`
  - a sibling `../SuperClaude_Plugin` repo
  - the removed env knobs set on other machines
  - users still on 4.7.x or older who rely on the legacy-skill prune
- Line numbers in the specs are from `57287b4`.

## Verifier open points

Each verifier also listed what it could not check and what argues against a cut. These are kept
unedited in [03a-analysis-open-points.md](./03a-analysis-open-points.md); read the group for a batch
before starting it.
