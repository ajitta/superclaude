---
feature: over-engineering-audit
phase: planning
owner: ajitta
created: 2026-10-03
updated: 2026-10-03
---

# Over-Engineering Audit

A whole-tree audit for over-engineering, run with `/ponytail:ponytail-audit` on 2026-10-03 against
`master` at `57287b4`. It lists what can be deleted, replaced with the standard library or a
platform feature, or shrunk. Correctness, security and performance were out of scope.

52 findings survived adversarial verification, and none was refuted. The verifiers estimated about
9.9k removable lines across all 52.

The owner decisions were taken on 2026-10-03 (see [Decisions](#decisions)):

- 10 findings are kept or skipped.
- 4 are narrowed: F20, F29, F33 and F36.
- The other 38 are approved as specified.

By the verifiers' estimates, the approved cuts come to roughly 7.5k–8k lines and four
dependencies: rich, black, scipy and pytest-benchmark.

No code has changed yet. The cuts are carried out on branch `feature/over-engineering-audit`,
batch by batch, following [05-plan.md](./05-plan.md).

## Documents

- [03-analysis.md](./03-analysis.md): method, ranked findings with verdicts, withdrawn findings, corrections, limits
- [03a-analysis-open-points.md](./03a-analysis-open-points.md): what each verifier could not check, unedited
- [05-plan.md](./05-plan.md): ground rules, batch order B1–B7, cross-item constraints
- [05a-plan-b1-unreferenced.md](./05a-plan-b1-unreferenced.md): B1 specs, unreferenced files and test-only cleanup
- [05b-plan-b2-config-ci.md](./05b-plan-b2-config-ci.md): B2 specs, pytest and pyproject config, CI workflows, orphan scripts
- [05c-plan-b3-cli-internals.md](./05c-plan-b3-cli-internals.md): B3 specs, behavior-preserving CLI internals
- [05d-plan-b4-hook-internals.md](./05d-plan-b4-hook-internals.md): B4 specs, hook and script internals
- [05e-plan-b5-cli-surface.md](./05e-plan-b5-cli-surface.md): B5 specs, CLI surface removals
- [05f-plan-b6-hook-behavior.md](./05f-plan-b6-hook-behavior.md): B6 specs, hook and runtime behavior removals
- [05g-plan-b7-repo-and-deps.md](./05g-plan-b7-repo-and-deps.md): B7 specs, repo-level artifacts and dependencies

## Decisions

These were decided by the owner in an interview on 2026-10-03.

The first answer was that unknown users may install this public fork. That fact settled the rows
marked *derived*: upgrade paths, published env switches and shipped interfaces stay. A removed
CLI command fails loudly the moment someone runs it, while a removed hook prints an error at every
session start until the user reinstalls. So documented commands could still go, as long as the
README changes with them.

D15, D17 and D19 change implementation details only, not the result. They take the defaults the
audit proposed.

| # | Item | Decision | Basis |
|---|---|---|---|
| D01 | F01 `okf/` | **cut**; codex F-015 is closed as discarded | owner |
| D02 | F26, F02-B old plugin build path | **cut**; codex F-016 is closed as discarded. The root `.claude-plugin/` plan in runtime-behavior-audit Task 13 is a separate path and still stands. | owner |
| D03 | F03 `install.sh` | **keep** | derived: may be an outside entry point |
| D04 | F05 `superclaude audit`, `make audit` | **cut**; replaced by `make verify-drift` plus pytest | owner |
| D05 | F06 `context explain` | **keep** | owner |
| D06 | F07 skills banner | **cut** variant (b): the module, the banner and `CLAUDE_SHOW_SKILLS`. F07-a is skipped. | owner |
| D07 | F09 readme-quality-check.yml, `make translate` | **cut** both | owner |
| D08 | F11 publish-pypi.yml, .env.example | **cut** | the `+ajitta` local version cannot be uploaded, whoever the users are |
| D09 | F12 PR-status line | **keep** | owner |
| D10 | F13 `superclaude agents` | **cut** with the cascade: `hooks/inline_hooks.py` and its tests go too, so F35i is moot | owner |
| D11 | F14 memory_staleness | **keep** | derived: removing a hook breaks non-force upgraders every session |
| D12 | F15 migrations (a) and (b) | **keep** both; F15 leaves this branch | derived: upgrade paths |
| D13 | F17, F36 mypy | **keep** mypy and `[tool.mypy]`; the codex F-014 type-gate direction stands | owner |
| D14 | F18, F24 CI | **cut**: merge jobs, drop test-summary, the duplicate 3.10 run, the Codecov upload and quick-check.yml | owner |
| D15 | F23 jq | keep `query` pretty-printed (`json.dumps(indent=2)`) | default |
| D16 | F29 `update`, `version` | **keep** `update`, **cut** `version` | owner |
| D17 | F30 uninstall helper | **skip** F30 | default |
| D18 | F31 MCP picker | **keep** | owner |
| D19 | F33 `CURRENT_MCP_SERVERS` | **keep** the constant and its equality test; the other F33 sub-cuts go | default |
| D20 | F35b git line | **cut** | owner |
| D21 | F35c pytest markers | **keep** `hallucination` and `performance` | derived: the plugin auto-applies to any pytest run where superclaude is installed |
| D22 | F35f `.agent/` placeholder | **cut** (FUNDING.yml goes too) | owner |
| D23 | F20 env knobs | **keep** `CLAUDE_CONTEXT_INJECT` and `CLAUDE_CONTEXT_USE_INSTRUCTIONS`; F20's internal parts still go: the empty `FLAG_ALIASES`, the same-package import guards and the duplicate `_BEHAVIORAL_MCPS` | derived: published switches |
| D24 | F36 dependencies | **cut** rich, pytest-benchmark, black and scipy; **keep** jmespath, so the documented `--metric` syntax stays | owner |
