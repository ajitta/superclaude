---
feature: review-v4.29.3
phase: fixes
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 01. Fixes — finding → change → check

## Original request

> ajitta/superclaude 최신 버전을 독립적인 리뷰를 진행하라

After the report (numbered remaining-work list, recommendation on each — 1 notes extraction, 2 fill the two blank releases, 3 R-2/3/6/8 batch, 4 R-7 (a) in this batch with canary, 5 R-5 (a) `make typecheck` with a baseline, 6 R-4 in the batch, 7 release v4.29.4):

> 너의 권고 추천대로 진행해

## Finding → change

| ID | Change | Check |
|---|---|---|
| R-1 High | `Makefile` release recipe: notes = the entry whose heading starts `## [<version>]`, up to the next `## [`; empty notes stop the recipe before `gh release create`. New `tests/unit/test_release_recipe.py` runs the recipe's own awk program (empty `[Unreleased]` above the version, next-version stop, missing version, version prefix, current version non-empty) and checks the guard precedes `gh`. | 6 tests red on the old Makefile, green on the new one. Extraction gives 1945 B (4.29.2) / 365 B (4.29.3). |
| R-1 follow-up | `gh release edit v4.29.2` / `v4.29.3 --notes-file` from the same extraction. | Bodies 1943 / 365 chars (were 1 / 1; gh trims the trailing newline). |
| new | `Makefile` exports `GH_REPO` from `git remote get-url origin` unless already set. On this VM `gh repo set-default --view` is `SuperClaude-Org/SuperClaude_Framework`, so `make ci`/`make release` would have dispatched Tests and created the release on the upstream. | `gh release view v4.29.1` via make → `ajitta/superclaude/...`; without `GH_REPO` → "release not found". Test asserts the export line. |
| R-2 Low | `_is_multiline_tag`: the first line's remainder after the tag name must be attribute-shaped too, like the continuation lines. | New test (`<draft notes for the team\n> quoted reply` → md, no X1/X2; control `<step note="a"\n other="b">` → xml) red on the old source, green on the new. Whole-tree corpus (570 tracked `*.md`, format + every finding) before/after: diff 0. |
| R-3 Low | `superclaude insight append`: annotation on `ref_ts 2026-10-04T23:01:46+09:00` marking it superseded by 3e64dc82. | Append-only, per `insight-analyst.md`. |
| R-4 Low | CHANGELOG header: tagging starts at 4.20.1; 4.19.0 and 4.20.0 predate it. | `test_version_consistency.py` green. |
| R-5 Low | `make typecheck` (+ `.PHONY`, `##` help): fails when mypy's error count exceeds `MYPY_BASELINE ?= 34`, or when mypy reports no result. AGENTS.md Code Style line: lower the baseline when errors are fixed, never raise it. Not in CI: the count differs by environment (33 in the main `.venv`, 34 in the review worktree's — `parallel_ab/runner.py` `var-annotated` only in one). | `make typecheck` → "33 errors (baseline 34)", rc 0; `MYPY_BASELINE=30` → rc 2. `test_makefile_help.py` green. |
| R-6 Low | The three authoring rules give `<scenarios><scenario>` as the plural↔singular example and say `<examples>`/`<example>` are distinct, matching `xml-prose-format.md:154-158`. | One script, each old string asserted to occur once. |
| R-7 Low | `RULES_QUALITY.md` `<verification_ladder>`: Level 0 trigger gains "that no test, build or linter reads"; the closing "Docs-only changes stay Level 0." becomes "never escalate to Level 4; one that a test, build or linter reads runs that check" — keeps the no-escalation intent of 9a247cb6 and matches `RULES.md:26`. | Core change → `make canary-gates` before release. Context-budget headroom tests green. |
| R-8 Low | `main.py` parallel-ab help example → `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml` (exists). | `ls` of the path. |

## Verification round (02-verification.md)

A second independent run (`claude -p --model opus --effort high`, $2.36, read-only worktree at ff562580) returned PASS WITH FIXES. All seven findings were taken:

| ID | Change |
|---|---|
| V-1 Medium | `make typecheck` keeps mypy's exit code; exit ≥ 2 (a blocking error, "errors prevented further checking", mypy missing) fails instead of reading as fewer errors. |
| V-2 Low | The comment above `release:` describes the version-keyed notes and the empty-notes stop. |
| V-3 Low | `_is_multiline_tag`: a bare `>`/`/>` continuation line with text after it on its line is a blockquote (`<draft` + `> quoted reply`, `<draft x=1` + `> quoted reply` → md). Controls `<step\n note="a"\n>` and `…\n/>` stay xml. Corpus (573 files, master code vs branch code on the same inputs): diff 0. |
| V-4 Low | The two string-only tests are behavioural now: the recipe's extract + guard lines run under `sh` (empty entry / empty version → non-zero, no notes file), the guard precedes `gh` and the stable push, the Makefile's own `sed` expression maps five https/ssh origin URLs to `o/r`, and `make typecheck` runs against a stub `uv` for six mypy outputs. Planted mutations (guard → `true`, broken sed, dropped exit-code check) each turn a test red. |
| V-5 Low | Commits regrouped so each message matches its diff. |
| V-6 Low | A second annotation names which of the five entries sharing `ref_ts 2026-10-04T23:01:46+09:00` is superseded. |
| V-7 Info | The awk test decodes output as UTF-8, not the locale encoding. |

## Checks at the branch tip

- `make format`, `make lint`, `ruff format --check src tests`, `ruff check src tests`: clean.
- `uv run pytest`: 3891 passed, 3 skipped (3871 + 20 new); `make typecheck` 33 errors (baseline 34).

## Not done

- mypy debt itself (33–34 errors) — the target only stops it growing.
- `make typecheck` in CI — waits until the count is environment-stable or zero.
