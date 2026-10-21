branch: master @b662d843 (== origin/master; stable == v4.34.1 == 2e7fcc40)

# Session 2026-10-21 — master (memory refresh, branch cleanup, sandbox escape fix, test speed, run_shell)

Session goal: none set via /sc:load.

## What was done
- Memory stores refreshed to v4.34.1:
  - claude-mem: work_state `release` closed, new `remaining-work` list, snapshot #17415.
  - Auto memory: 7 project notes updated, `project_remaining-work.md` added.
- Branch cleanup:
  - `git fetch --prune` dropped 10 stale `origin/*` refs.
  - Deleted local `chore/version-4.28.0`, `docs/superclaude-weakness-research`, `fix/sandbox-home-walk`, `fix/shell-timeout-tree` (all merged).
- Plan `docs/features/session-memory-multi-machine/` (README + 05-plan), on branch `docs/session-memory-multi-machine` @8b4f004a:
  - Problem: two computers on master save into the same `session_[date]_[branch].md`.
  - Owner chose (b) machine name in the filename (hostname as is) + (a) Sync step (fetch, ask before pull) and Share step (ask before commit and push).
- Sandbox escape (merged 3a7ce9c9):
  - Symptom: `test_c05_drift_remediation_carries_the_scope[user]` failed on this machine.
  - Cause: `sandbox()` put home and project side by side, so `find_install_root` walked past the fake `$HOME`. pytest's temp folder is under the Windows profile, so the walk reached the real `~/.claude/superclaude` (created 2026-10-21 13:43) and reported it as a project install. Linux CI stayed green.
  - Fix: project goes under the fake home. Per-scope decoy test `test_sandbox_walk_stops_at_the_fake_home`. `_edited_file()` no longer hard-codes `tmp_path / "project"`.
  - Gotchas `test-anchor-env` + `sandbox-escapes-home` moved to the new `gotchas/tests.md` (paths: tests/**). Runbook step 5 names it.
  - Real CLI per scope in a scratch HOME: every scope reports its own install; the old layout + user scope reproduces the escape.
- Test speed investigation:
  - Windows ~340–540 s per full run (varies with machine load); Linux CI ~85 s for the same suite.
  - uv overhead ~0.1 s, collection 0.77 s, no `--cov` in addopts.
  - Time goes to subprocess- and file-heavy tests: install scenarios ~137 s, eval_harness ~76 s, eval_purpose fixtures ~62 s.
  - Defender path exclusions (owner added them): 401 → 385 s, ~4 %, not the cause.
  - `intent_through[correct]` once took 26–27 s twice, then 3–4 s on reruns; unexplained.
- run_shell (merged b662d843):
  - Bug: `subprocess.run(shell=True, timeout=...)` kills only the shell. On Windows the call waited for the child anyway (1 s timeout on a 6 s child: 6.1 s); on POSIX it returned but left the child running (WSL check).
  - Fix: `superclaude.utils.run_shell` kills the process tree (`taskkill /F /T`; POSIX `start_new_session` + `killpg`). Used by auto_improve `eval_runner`, `SmokeGate`, `test_runner_hook`.
  - `test_enforces_timeout_kills_subprocess` 30.1 s → 1.5 s. CHANGELOG `[Unreleased]` `### Fixed` entry.
- Master after merges: full suite 3776 passed / 12 skipped; ruff, mypy clean; pushed dbff080b..b662d843.

## Decisions
- Feature plans go on a `docs/*` or `feature/*` branch, never straight onto master (owner correction; feedback memory `plan-docs-on-branch`).
- Session filenames carry the hostname slug as is (public repo exposure accepted).
- run_shell fix covers all three call sites, not only eval_runner (owner choice).
- No product change for the install walk escaping when the project is outside home (rare).

## Problems hit
- Committing the plan onto master was about to happen; the branch was made only after the owner asked why.
- First per-scope assert `"missing" not in output` was wrong: the summary line always says `0 missing`. Assert the exact summary line instead.
- Git Bash: no `/usr/bin/time` or `bc`; use bash `time` with `TIMEFORMAT`. `wsl.exe` paths need `MSYS_NO_PATHCONV=1`.
- The caveman hook compresses long tool output; recover with `caveman_retrieve` when lines are elided.

## Next actions
- [ ] Owner: remove the Defender exclusions in admin PowerShell: `Remove-MpPreference -ExclusionPath "C:\Users\ajitta\Repos\ajitta\superclaude","C:\Users\ajitta\.claude\tmp"`.
- [ ] Implement `docs/features/session-memory-multi-machine/05-plan.md` on `feature/session-memory-multi-machine` (from the plan branch); `make canary-commands` before release.
- [ ] Release both fixes as one version (run_shell + per-machine session records), then sync installs on both computers (`superclaude doctor --scope user` → `superclaude install --force --scope user`).
- [ ] Optional speed work: pytest-xdist measurement; one fresh install per session copied into each test.
- [ ] Optional: decoy at pytest's temp root to find other tests escaping the fake home (conftest `mktemp("home")`).
- [ ] Gotcha proposal `plan-docs-on-branch` for `gotchas/general.md`: unanswered.
