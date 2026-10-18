---
feature: context-budget-restore
phase: verification
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 01. Verification — context budget restore

Branch fix/context-budget-default from master d995aa1a. Intent commit a60b8d17; fix commit 9f0f6ce3. Headless behavioral sessions used: **0** (owner cap 0). All token figures are the loader's own estimate (`estimate_tokens`, chars/4) over the current tree.

## Change

| Site | Before | After |
|---|---|---|
| `src/superclaude/utils/__init__.py` | no default constant | `DEFAULT_CONTEXT_MAX_TOKENS = 12000` |
| `src/superclaude/scripts/context_loader.py:51` | `int_env("CLAUDE_CONTEXT_MAX_TOKENS", 8000)` | `int_env("CLAUDE_CONTEXT_MAX_TOKENS", DEFAULT_CONTEXT_MAX_TOKENS)` |
| `src/superclaude/cli/main.py` (`context explain`) | literal `8000` ("mirrors" comment) | the shared constant |
| `src/superclaude/ARCHITECTURE.md`, `src/superclaude/scripts/README.md` | "8K token budget" | "12K token budget (`DEFAULT_CONTEXT_MAX_TOKENS`)" |
| `CHANGELOG.md` `[Unreleased]` → `### Fixed` | — | regression entry naming v4.29.1 |

No file under `src/superclaude/core/`, `hooks.json` or `evals/` changed. The `CLAUDE_CONTEXT_MAX_TOKENS` override is unchanged.

## Measurement: `superclaude context explain`, default budget, before → after

`SUPERCLAUDE_PATH=src/superclaude`, env knob unset.

| Prompt | set size | 8,000 (v4.29.1) | 12,000 (this branch) |
|---|---|---|---|
| `/sc:analyze --delegate` | 8,297 | **drops RULES_DOCS** | 4 files, nothing dropped |
| `/sc:analyze --delegate --brainstorm` | 8,845 | drops RULES_DOCS | 5 files, nothing dropped |
| `/sc:analyze --delegate --all-mcp` | 8,593 | drops RULES_DOCS | 7 files, nothing dropped |
| `/sc:analyze --delegate --business-panel --uc` | 9,931 | drops RULES_DOCS | 6 files, nothing dropped |
| `/sc:analyze --delegate --vs` | 10,488 | drops RULES_DOCS | 5 files, nothing dropped |
| `/sc:task --delegate --research` | 6,801 | fits | fits |
| `/sc:analyze --delegate --vs --business-panel --uc` | 12,122 | drops RULES_DOCS | drops **RULES_INTERACTION** (282, P2) — recorded residual |

Reading: every priority-1 rule module a single-mode `/sc:` + `--delegate` prompt triggers is injected again. Prompts stacking three or more mode flags exceed 12,000 and lose the P2 interaction module first — never a P1 rule module — because `check_triggers` sorts by priority and the injection order was not changed (owner's Q1). The on-demand set routed by TRIGGER_MAP ∪ COMPOSITE_FLAGS is 14 files / 17,058 tokens; no budget short of that holds every conceivable stack.

Why 12,000 and not 10,000: at 10,000 the `--vs` combination still dropped RULES_DOCS (VS mode 2,191 is P1 and sorts ahead of the rule modules by TRIGGER_MAP order) and `--business-panel --uc` sat 69 tokens from re-flipping. The owner chose 12,000 after seeing this table.

## Deterministic evidence (red → green)

Implementation stashed (`git stash push -- src/superclaude/utils/__init__.py src/superclaude/scripts/context_loader.py src/superclaude/cli/main.py`), tests run, stash popped, tests run again.

| Test | With implementation stashed | With implementation |
|---|---|---|
| `tests/unit/test_context_loader.py::TestDefaultBudgetHoldsTheRuleModules::test_delegated_analysis_injects_every_rule_module` | **FAILED** — `core/rules/RULES_DOCS.md missing on the default budget`; output carried `<!-- ⚠️ Budget exceeded: skipped core/rules/RULES_DOCS.md -->` | passed |
| `tests/unit/test_context_loader.py::TestCoreLiteSplit::test_rule_modules_fit_the_default_budget_with_headroom` | FAILED (ImportError on the new constant; with an 8,000 default it would assert 8,297 + 2,191 + 500 = 10,988 > 8,000) | passed (10,988 ≤ 12,000, 1,012 spare) |
| `tests/unit/test_cli_context.py::TestContextExplain::test_it_reports_token_cost_against_the_loader_budget` | FAILED — `budget:  8000 tokens` | passed — `budget:  12000 tokens` |
| `tests/unit/test_cli_context.py::TestExplainBudgetParsing::test_a_malformed_budget_falls_back_instead_of_crashing` | FAILED — fell back to 8000 | passed — falls back to 12000 |

Test-design notes: `run_loader` gained `env_unset` so a developer shell that exports `CLAUDE_CONTEXT_MAX_TOKENS` cannot mask the default under test; the CLI default test now `delenv`s the same knob (it did not before). The drift guard takes the largest **routed** mode (TRIGGER_MAP ∪ COMPOSITE_FLAGS), not a `modes/` glob, so `modes/README.md` and `RESEARCH_CONFIG.md` cannot trip it. `BUDGET_HEADROOM = 500` ≈ nine edits the size of the one that shipped the regression (+56).

## Integration checks (repo root)

| Check | Result |
|---|---|
| `uv run --no-sync pytest tests/unit/test_context_loader.py tests/unit/test_cli_context.py -q` | 173 passed |
| `uv run --no-sync pytest -q` | 3655 passed, 4 skipped |
| `uv run --no-sync pytest tests/unit/scripts -o addopts=` (AGENTS.md rule for `src/superclaude/scripts/` changes) | 140 passed |
| `uv run --no-sync ruff format --check src tests` / `ruff check src tests` | clean |
| `git diff --name-only \| xargs file \| grep -i crlf` | empty |
| `superclaude verify-drift --scope local` | no drift (no content file changed) |
| Installed hook: PATH `superclaude hook context_loader` (editable uv tool → this checkout) on `/sc:analyze --delegate` | injects QUALITY, DELEGATION, DOCS, INTERACTION — 4 files, ~8,297 tokens, no "Budget exceeded"; no `superclaude install` needed |

## Closed by decision, not measurement

Lean-round `03-deferred-evidence.md` §7 left open "what a larger default budget would cost". This round answers it by decision (owner, 0 sessions): a busy `/sc:` prompt injects up to ~4K more tokens once per session per file against a 200K–1M context. No behavioral session was spent on it, and the behavioral effect of `RULES_DOCS.md` on a delegated analysis remains unmeasured by design (owner's Q1: restore, not measure).
