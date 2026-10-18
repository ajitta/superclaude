branch: master @a49e1207 (== origin/master); stable = v4.29.3 @d61d79cd; worktree clean (untracked .hermes/, .ignore belong to other sessions)

# Session 2026-10-19 — master (five hygiene rounds, two releases)

## Where it stands
- Five rounds closed in one session, each plan-first → independent reviewer → v2 → per-phase commits → merge: context-budget-restore (loader budget 8K→12K, RULES_DOCS back on `/sc:analyze --delegate`), author-check-multiline (format inference + N4 read multiline openers), repo-hygiene (Makefile help from `##` comments, CI setup-uv SHA-pinned), test-exclusion-lift (`tests/unit/scripts` back in the default run after 8/8 clean Windows runs; Dependabot), plus releases v4.29.2 and v4.29.3
- Default `uv run pytest` is now 3870 passed / 4 skipped (was 3655 at session start); ruff clean; local-scope install synced and drift-free at 4.29.3
- Current handoff: `docs/features/test-exclusion-lift/02-handoff.md` — carries the four next-round axes (A purpose-inference generalization / B model-generation re-audit / C install path / D docs consistency) with the chat recommendation A, cap 90. **Owner has not chosen**; the next session asks axis + cap first
- Dependabot (`github-actions`, monthly, grouped, target master) is active since v4.29.3 moved `stable` onto the file — GitHub reads dependabot.yml from the default branch

## What changed (merges on master, oldest first)
- 08d7a741 context-budget-restore: `superclaude.utils.DEFAULT_CONTEXT_MAX_TOKENS = 12000` shared by loader and `context explain`; regression + headroom tests
- 37a6501b author-check-multiline: `_is_multiline_tag` placement rule for `infer_format`/`_sentences`; 559-file whole-tree finding diff = 0
- 1f57aa62 v4.29.2 (Removed dev-only eval checks + Fixed ×3; no canary — core/hooks unchanged)
- e57e003a repo-hygiene: Makefile `##`/`##@` help + `test_makefile_help.py`; CI `astral-sh/setup-uv@1c37ad07… # v10.3.0`, `enable-cache: false`
- 09ea2e74 test-exclusion-lift: `--ignore=tests/unit/scripts` removed across 9 sites; `.github/dependabot.yml`
- d61d79cd v4.29.3 (Changed: contributor note on the lift)

## Decisions
- Budget 12,000 (not 10,000): `--vs` + `--delegate` still dropped RULES_DOCS at 10K; stacked ≥3 mode flags exceed 12K and lose only P2 INTERACTION — recorded residual, injection order unchanged
- Multiline span is a tag only when it starts a line and continuation lines are attribute-shaped (structural scan's placement rule) — prevents Markdown `<term ` … `>` swallows
- Lift rule fixed before runs: 6 sequential + 2 concurrent full suites all rc 0 → lift; revert = `git revert 3e64dc82`; bisect target `tests/unit/scripts/parallel_ab/` (only asyncio tests)
- In-function test imports (207 by `grep "^    from superclaude\|^        from superclaude" tests/unit/*.py`) carried with no guard; `frozenset` cosmetic item dropped
- Patch versions by repo precedent (4.29.1 carried a Removed section as a patch)

## Problems hit
- Plan v1 of repo-hygiene scheduled `test_frontmatter_yaml.py`, which had shipped four days earlier (3286c3f8); handoffs carried a stale "gap" note since purpose-boundary. Rule: grep `tests/` and `git log -S` before planning any "add a test" handoff row
- `astral-sh/setup-uv@v10` does not resolve — no major tags past v7; SHA-pin
- Makefile `## ` comments broke `test_eval_harness.py`'s `^canary-gates:` regex (widened); help descriptions must not contain `##` (awk FS)
- Reviewer wrongly predicted one "control" test would be red; keep the red/control split honest from the actual run, not the review
- Anthropic billing scare: pool order was already OAuth-first (`claude_code` priority 0, `ANTHROPIC_API_KEY_2` fill_first backup); console charges were from before the 10-18 pool cleanup

## Next actions
- [ ] Owner picks the next audit axis and session cap (table in test-exclusion-lift/02-handoff.md; recommendation A, cap 90)
- [ ] If A: Phase 0 maps reframing-anchoring + purpose-boundary, designs 4–5 domain fixtures + 2 plain-request controls, discriminability pass before the expansion
- [ ] Watch for the first Dependabot PR (grouped, targets master, read-only token CI)
- [ ] If a Windows `0xC0000409` abort ever recurs: `git revert 3e64dc82`, bisect parallel_ab under concurrent load, record pytest-asyncio version
