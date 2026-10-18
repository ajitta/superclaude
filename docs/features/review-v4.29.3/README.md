---
feature: review-v4.29.3
phase: closed
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# Independent review of v4.29.3 and its fixes

An independent reviewer (a separate `claude -p --model opus --effort high` run, read-only on a detached v4.29.3 worktree, $5.09) checked the latest release: release integrity, the changes since v4.29.1, an executed verification pass, and whole-framework consistency. Verdict: PASS WITH FIXES — one High finding (blank GitHub release notes) and seven Low ones. All eight are fixed on `fix/review-v4.29.3-findings`, plus one found while fixing R-1 (gh targeted the upstream repo on a fork clone).

## Status

Closed. Fixes merged into master at d56826ae (branch from 00e88353; full suite 3891 passed / 3 skipped). The v4.29.2 and v4.29.3 GitHub release notes were filled in from CHANGELOG (1943 / 365 chars, were 1 / 1). `make canary-gates` before release (R-7 touched core): all 7 hard gates passed, 13/13 checks, $0.50. Released as **v4.29.4** (49599e01; master = stable = tag) with `CANARY_OK=1 make release` from this VM — gh now targeted `ajitta/superclaude` through `GH_REPO` although this clone's gh default is the upstream; Tests run 39161327768 green; the v4.29.4 notes carry the 4.29.4 entry. No content install exists on this VM (doctor: none in user/project/local), so none was synced.

Follow-up (remaining-work items 1–2): `fix/mypy-clean` made `mypy src` clean (34 errors at 4.29.4 in a fresh env, 33 in the main `.venv`; 0 after, also on fresh 3.10/3.13 envs), turned `make typecheck` into plain `uv run mypy src` and added `mypy src` to CI `checks` (branch run 39163819326 green, all three jobs). Verifier PASS WITH FIXES; V-1 (codex backlog F-014 mypy block), V-2 (gotcha line), V-3 (CHANGELOG wording) applied. Unreleased — rides the next release.

## Documents

| File | Content |
|---|---|
| [00-review.md](./00-review.md) | The reviewer's report, verbatim (Korean, as requested in chat) |
| [01-fixes.md](./01-fixes.md) | Original request, finding → fix map, verification round, checks |
| [02-verification.md](./02-verification.md) | The diff verifier's report, verbatim (Korean) |
| [03-mypy-verification.md](./03-mypy-verification.md) | Follow-up `fix/mypy-clean` (mypy 33–34 → 0, CI gate): independent verifier's report, verbatim (Korean); V-1–V-3 applied |
