---
feature: repo-hygiene
phase: verification
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 01. Verification — Makefile help, CI setup-uv

Branch fix/repo-hygiene from master b7ac6716. Commits: 2e043236 (intent), f40257cb (Makefile), cd9f7e63 (CI). Headless sessions: **0**. No CHANGELOG entry (internal: Makefile help text, CI install mechanism, tests).

## Item 2 — already closed before this round

`tests/unit/test_frontmatter_yaml.py` (commit 3286c3f8, 2026-10-15, prompt-content-audit; red proof in [08a-implementation-rules-commands.md](../prompt-content-audit/08a-implementation-rules-commands.md) §test) parametrizes all 73 frontmatter files under `src/superclaude/` and requires `yaml.safe_load` to yield a mapping; 73 passed on b7ac6716. The purpose-boundary handoff (`03-handoff.md:43`, 2026-10-18) recorded the gap three days after it was closed, and the mode-retire, harness-checker-hygiene, context-budget-restore and author-check-multiline handoffs carried the note. Nothing to add: `md_helpers.load_frontmatter` already offers the strict per-file read for the skill tests.

## Item 1b — Makefile help

Drift on b7ac6716: `.PHONY` 21 names, hand-written help 18 lines; missing `sync-user`, `sync-project`, `sync-local`; orphaned `# Show help` comment above `release:`.

| Check | Result |
|---|---|
| `tests/unit/test_makefile_help.py` on b7ac6716 (Makefile unchanged) | **2 failed** — 21 undocumented targets listed; no `##@` headers |
| same on f40257cb | 3 passed (`.PHONY` == documented rules == all rules; sections ≥ 3; no hand-written `@echo "  make` list) |
| `make help` | three sections in the original order (Quick Start → Development → Cleanup), 21 targets; the `uninstall-*` recipes moved below the Development block for that order, bodies unchanged |
| `make -n <target>` for all 21 `.PHONY` names | exit 0 (tabs intact) |
| `gawk --posix` running the recipe's awk program | identical section/target counts (5 / 12 / 4) — no gawk extension used (`FS=":.*##"`, `substr`, `sub`, `sprintf`) |
| `tests/unit/test_eval_harness.py` canary-gates regex | widened to `^canary-gates:[^\n]*\n\t(.+)$`; 79 passed across the three Makefile-reading test modules |
| CRLF | none |

Help descriptions must not contain `##` (it is the awk field separator); the `help` target's own text was reworded once for that.

## Item 1c — CI

| Check | Result |
|---|---|
| `.github/workflows/test.yml` | both `Install UV` steps → `astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0`, `enable-cache: false`; `$GITHUB_PATH` line dropped; `Verify UV installation` kept; main pytest step `pytest --color=yes` (`-v --tb=short` already in pyproject addopts); isolated scripts step unchanged |
| YAML parses; step order preserved (setup-python before setup-uv) | yes |
| `gh workflow run Tests --ref fix/repo-hygiene` → run [39151749108](https://github.com/ajitta/superclaude/actions/runs/39151749108) on cd9f7e63 | **success** — Test on Python 3.10: success; Test on Python 3.13: success; Lint, plugin and doctor checks: success. Log shows `Run astral-sh/setup-uv@1c37ad07…` resolving the uv version from `pyproject.toml` |
| `@v10` tag | `gh api repos/astral-sh/setup-uv/git/ref/tags/v10` → 404 (no major tags past v7), hence the SHA pin |

Not changed: `install.sh:166` and the archived user doc keep their own `curl | sh` (user install path, unrelated to CI); `.github/workflows/README.md` does not describe the install step.

## Integration checks (repo root)

| Check | Result |
|---|---|
| `uv run --no-sync pytest -q` | 3730 passed, 4 skipped |
| `ruff format --check src tests` / `ruff check src tests` | clean |
| CRLF grep over changed files | empty |

## Prior-round decisions touched

None reopened: over-engineering-audit D14 (CI cut) stands; the pytest-flag trim is the minimal variant `05b-plan-b2-config-ci.md:123` proposed, and the shared-variable version was withdrawn as YAGNI.
