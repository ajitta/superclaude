branch: master @085a6cab (== origin/master; stable == v4.34.1 == 2e7fcc40; release held by the owner)

# Session 2026-10-21 — master (memory refresh, sandbox escape, test speed, run_shell, per-machine session records, review/reflect gap)

Session goal: none set via /sc:load. This record keeps the old name (`session_<date>_<branch>.md`): the installed /sc:save is still v4.34.1. From the release on, records are `session_<date>_<host>_<branch>.md`, and /sc:load reads both.

## Start here (next session)
1. `git fetch origin && git switch master && git pull --ff-only`, then read this file.
2. Open items in order: Next actions below. Item B needs owner decisions first.
3. Background for item B: `docs/analysis/review-reflect-gate-gap-ajitta-2026-10-21.md` on branch `docs/review-reflect-gate-gap` (pushed, not merged; rebase on master before working).

## What was done
- Memory stores refreshed to v4.34.1; merged branches and stale `origin/*` refs pruned.
- Sandbox escape fixed (merged 3a7ce9c9):
  - `test_c05_drift_remediation_carries_the_scope[user]` failed here because `sandbox()` put home and project side by side, so the install walk reached the real `~/.claude/superclaude` (pytest's temp folder is under the Windows profile).
  - Fix: project goes under the fake home, plus a per-scope decoy test. The gotchas `test-anchor-env` and `sandbox-escapes-home` are now in `gotchas/tests.md` (paths: tests/**).
- Test speed measured: Windows 340–540 s vs Linux CI ~85 s. Cause: process spawn + file I/O. Defender exclusions gave ~4 %. Auto memory note `test-suite-speed-windows`.
- `utils.run_shell` (merged b662d843): a shell-command timeout now kills the whole tree (Windows `taskkill /T`, POSIX killpg). Used by auto_improve eval/smoke and test_runner_hook. The 30 s test now takes 1.5 s.
- Per-machine session records (feature `docs/features/session-memory-multi-machine/`, plan `status: complete`, master 085a6cab):
  - /sc:save writes `session_<date>_<host-slug>_<branch>.md` and never edits another machine's record.
  - /sc:load filters by the `branch:` line, reads every machine's record of the newest date, and says which machine wrote each.
  - Sync step (both): prompt-free `git fetch`, count behind, ask [y/n] before `git pull --ff-only`. Every `@{u}` is quoted as a whole argument, because PowerShell breaks it otherwise.
  - Share step (save, last): commit only the written files (`git add -- <files>`, `git commit … -- <files>`). No commit offer on a detached HEAD or during a merge, cherry-pick or revert. Push offered only when not behind and `'@{u}...HEAD'` lists memory files only.
  - Independent review in 4 rounds (`06-review.md`) and /sc:reflect.
  - Final: full suite 3787 passed; canary-commands cmd-delegated-load 1/1, cmd-load-other-host 3/3, cmd-load-sync-behind 4/4, cmd-save-host-record 3/3 (`C:/sc-evals/smm-final2/report.md`, this computer).
- Review/reflect gap analysed: README Medium/Large chains end with /sc:reflect, RULES_DOCS `workflow_gates` end at `/sc:test -> done`, and the handoffs never name reflect; fixes were not re-reviewed. Item A (finish the feature) and item C (memory) are done; item B is open.

## Decisions
- Feature plans go on a `docs/*` or `feature/*` branch, never straight onto master (feedback `plan-docs-on-branch`).
- No bump or release until the plan is `complete`, the review has passed, fixes are re-reviewed and /sc:reflect has run (feedback `release-needs-complete-plan`).
- Post-release steps (release, install sync, two-computer check) live in the feature README "릴리스 뒤", not in the plan.
- Session filenames carry the `hostname` slug as is (public-repo exposure accepted). An SSH prompt during fetch is disclosed in CHANGELOG, not worked around (`GIT_SSH_COMMAND` would override `core.sshCommand`).
- Review rounds stop once what is left can be checked mechanically (grading, tests, canary).

## Problems hit
- I nearly committed the plan to master, and started the 4.34.2 bump while the plan was `implementing`. The owner stopped both.
- `'@{u}'...HEAD` (partly quoted) reaches git as two arguments in PowerShell (exit 129); quote the whole range.
- Headless `claude -p` refuses every Write under the workspace's `.claude/`, so the save probe grades the record name from the answer.
- A Python heredoc wrote a backspace into tasks.yaml (`\b`); `t.index("Result:")` hit an earlier mention and truncated the plan. Use Edit for regex text; use `rindex` with an anchored marker.

## Next actions
- [ ] Release (owner decides; held 2026-10-21): new bump branch (4.34.2) → full suite → merge/push → `CANARY_OK=1 make release`. Then both computers: `superclaude doctor --scope user` → `superclaude install --force --scope user`. Then the owner's two-computer same-day /sc:save check (feature README "릴리스 뒤").
- [ ] Item B, review/reflect gates (new branch, e.g. `fix/review-reflect-gates`; owner decisions first): where reflect goes (★ RULES_DOCS `workflow_gates` / handoffs / README optional); whether to add "re-review fixes that change shipped content" and when to stop. This changes `core/`, so `make canary-gates` before release; bundle with the release above to run canaries once.
- [ ] After the release: /sc:save in the new filename format; delete `C:/sc-evals/smm-final2`.
- [ ] Owner: remove the Defender exclusions (admin PowerShell `Remove-MpPreference -ExclusionPath "C:\Users\ajitta\Repos\ajitta\superclaude","C:\Users\ajitta\.claude\tmp"`); accept or decline the gotcha proposal `plan-docs-on-branch` for `gotchas/general.md`.
- [ ] Optional: pytest-xdist measurement or one cached install per session; decoy at pytest's temp root (other sandbox escapes); unexplained 26 s spike in `intent_through[correct]`; an interactive (tmux) run that answers [y/n] yes for Sync/Share; stale claude-mem `authoring-skill` list.
