branch: master @bae01a8b (== origin/master; stable == v4.31.1 @47f791b5, master ahead by contributor-only changes: evals, tests, docs); worktree clean (untracked .hermes/, .ignore belong to other sessions)

# Session 2026-10-20 — master (pressure-probe readout, eval-arm isolation)

## Where it stands
- Pressure probes measured, vanilla vs sc-full, sonnet low (`docs/features/pressure-readout/`):
  - Hurry: sc-full 30/30 vs vanilla 20/30, one-sided Fisher p = 0.0004 (pre-registered rule 3, "SC helps under hurry"). All 10 vanilla misses were Edit, then DONE, with no run.
  - Control `probe-verify-claim`: 10/10 on both arms.
  - Dictated-fix and sunk-cost: both arms at ceiling.
- Harness faults fixed red-first:
  - Every arm loaded the claude.ai account's synced plugins (from the 2nd session), skills (often from the 1st) and connectors. Fixed with `--setting-sources project,local` + `ENABLE_CLAUDEAI_MCP_SERVERS=false`.
  - `sc-command-only` loaded the full core through `.claude/CLAUDE.md`. Fixed by removing that import with the installer's `remove_claude_md_import`.
  - `probe-verify-claim` now grades with the pressure-time-verify pattern.
- The verifier (headless opus high, `02-verify.md`) said PASS WITH FIXES; findings 1–7 applied. The purpose-generalization and purpose-opus 04 readouts carry a contamination caveat (no label flips).
- First isolated `make canary-gates`: 7/7 gates, 13/13 checks, 0 contaminated sessions.
- Full suite 4555 passed / 3 skipped; ruff, mypy clean. No release: nothing under `src/superclaude` changed, so the `[Unreleased]` entries go out with the next release.
- GitHub Actions was degraded on 2026-10-20: the branch CI runs sat queued. Master was pushed on a green local suite. Check `gh run list -R ajitta/superclaude --branch master -L 1` once Actions recovers.

## Decisions
- Eval runs from before 2026-10-20 carry account content that varied from session to session and between arms. They are not pooled with isolated runs; no rerun now.
- Pressure-probe readouts use one-sided Fisher with rules written before the data. This prereg was committed 58 s into batch B; its corrections section records that.

## Problems hit
- `git checkout -- .`, run from the repo cwd during a scratch check, threw away an uncommitted fix. Commit before running scratch checks from the repo dir.
- The gotcha budget is 320 chars per entry (`test_gotcha_budget.py`).

## Next actions
(full list: `docs/plans/remaining-work-ajitta-2026-10-19.md` §7)
- [ ] Confirm the master CI run is green once GitHub Actions recovers
- [ ] Dictated-fix / sunk-cost probes at ceiling: ★keep as regression guards; re-read at the next model canary
- [ ] Pressure probes on opus / auto mode: on hold
- [ ] `bugfix-scope-creep` (matrix task) still has the loose `pytest|python -m pytest` grader; align it when its comparability no longer matters
- [ ] Carried over from 2026-10-19: S3 C-16/C-17 on hold; axis B at the next model; split `docs-ssot-audit/06-verify.md` before a sizable addition; opus N2/N5 round and the "open the referenced file" wording trial on hold; `origin/fix/plain-language-structure` kept; Windows `0xC0000409` → `git revert 3e64dc82`
