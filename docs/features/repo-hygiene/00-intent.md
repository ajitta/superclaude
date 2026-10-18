---
feature: repo-hygiene
phase: intent
status: approved-for-plan
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — repo hygiene: Makefile help, CI setup-uv

## Original request

After the author-check-multiline round was released as v4.29.2:

> 다름 라운드 진행

Candidate table in chat (1a frozenset rewrites, 1b Makefile help from `##` comments, 1c CI `curl | sh` → setup-uv, 1d `tests/unit/scripts` exclusion, 1e in-function test imports, 2 frontmatter `yaml.safe_load` test, 3 stacked-mode budget residual, 4 `_is_multiline_tag` limit); recommendation 2 + 1b + 1c, cap 0:

> Q1 권고대로.
> Q2 권고 대로.

Reviewed plan v2 (item 2 found already closed; scope 1b + 1c):

> Q1 시작

## Problem

Two lean-round leftovers carried through four handoffs. (1b) `make help` is a hand-written list that already omits three `.PHONY` targets (`sync-user`, `sync-project`, `sync-local`); nothing fails when a target is added without a help line. (1c) CI installs uv with `curl -LsSf https://astral.sh/uv/install.sh | sh` in two jobs instead of the maintained `astral-sh/setup-uv` action.

A third candidate, the frontmatter `yaml.safe_load` test, turned out to be **already shipped** (`tests/unit/test_frontmatter_yaml.py`, commit 3286c3f8, 2026-10-15): the purpose-boundary handoff recorded the gap three days after it closed and later handoffs carried the stale note. This round records the closure instead of re-doing the work.

## Desired outcome

`make help` is generated from `## ` comments on each rule line and `##@ ` section headers, and a test fails when a `.PHONY` target lacks its comment (or a commented rule is not in `.PHONY`). CI uses `astral-sh/setup-uv`, SHA-pinned to v10.3.0 (the action publishes no major tags past v7), with the lock-file cache disabled because the install path ignores `uv.lock`; a `workflow_dispatch` run on the branch is green on both Python versions.

## Affected users and systems

- Contributors: `make help` output (same three sections, now complete); no target added, removed or renamed; no command changes.
- CI: install mechanism only; test and lint steps unchanged except the redundant `-v --tb=short` on the main pytest step (already in `pyproject` addopts).
- Nothing installed into `~/.claude` or a project changes; no CHANGELOG entry (the header scopes internal refactors and tests out); no release.

## Constraints and decisions

| Topic | Approved decision |
|---|---|
| Scope | 1b + 1c; item 2 recorded as closed by 3286c3f8; 1a/1d/1e, 3, 4 carried |
| Makefile | `.PHONY` line untouched; POSIX awk only in the help recipe (mawk on CI, gawk locally, BSD awk on macOS); orphaned `# Show help` comment removed; `tests/unit/test_eval_harness.py` canary-gates regex widened in the same commit |
| CI | `astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0`, `enable-cache: false`, step order kept (setup-python first); no shared pytest-flag variable |
| Branch | fix/repo-hygiene from master b7ac6716 |
| Sessions | 0 — tests, `make -n`, and a CI run are the oracles |
| Delivery | One commit per item; merge and push only on a later instruction; no release |

## Open questions

None blocking.

## Plan and review

Local working plan: .hermes/plans/2026-10-19_024500-repo-hygiene.md (reviewed v2; v1 beside it). The review found item 2 already shipped and the `@v10` action tag non-existent, and added the eval-harness regex, the real drift set, the POSIX-awk constraint and the cache setting.
