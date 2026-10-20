---
status: complete
revised: 2026-10-20
---

# Follow-ups: interactive run, design status, release gate, second review

The four follow-ups after 4.33.1, and how the second independent review ([06c-verify-round2.md](./06c-verify-round2.md)) was applied.

## Interactive run (run 22)

Every earlier run was headless. One run in an interactive Claude Code session (2.1.303, sonnet, `--permission-mode auto`, the default `~/.claude` login) in tmux, on the todo repo with a local remote, typing the five lines after `/sc:intent --through` on one line:

- Done in 4 min 28 s with no permission prompt or question on screen.
- Nine commits on `feature/todo-due-dates`; `main` and the remote at baseline; clean tree.
- The report listed the six items and two delegated readings to confirm. Reflect proposed one memory note and wrote nothing, as 4.33.1 asks.
- It also said "nothing in the chain moves a design out of draft", the gap fixed below.
- After the run, the input box held Claude Code's greyed suggestion `merge feature/todo-due-dates into main`. It is a suggestion, not a queued message, and was not sent.

## Design status

`/sc:plan`'s Save step now moves the design doc the Load step read (`04-design.md` or a `docs/specs/*-design-*.md`) from `draft` to `approved-for-plan`, edited in the same Save as the plan. Its Areas of concern section keeps any concern the user planned past, and the RULES_DOCS `/sc:design -> /sc:plan` gate names planning past them as the owner's call. The second review's live probe run showed it: the design moved to `approved-for-plan` in the plan's commit, with its Areas of concern kept.

## Release gate for command bodies

`make release` refuses when a command body under `src/superclaude/commands/` changed since the last tag (README and `__init__.py` excluded) unless `CANARY_OK=1`. `make canary-commands` runs the canary probes `evals/changed_command_probes.py` picks: a probe counts for a command its prompt names (`/sc:<name>`), a `skill_called` check expects, or its `covers:` list holds. `intent-through-branch` covers the whole Large chain.

## Second review: findings and what changed

Verdict: PASS WITH FIXES, no Critical. The reviewer rebuilt all 12 rows of the probe mutation table, ran the gate lines under dash in a scratch clone with fake tags, and ran the probe live (12/12).

| # | Severity | Finding | Applied |
|---|---|---|---|
| 1 | Important | `make canary-commands` printed a traceback, then "no probe", and exited 0 when there was no tag to diff against | The script catches the git error and exits 2; the target stops on it (`\|\| exit 1`); `BASE=<ref>` sets the base by hand |
| 2 | Important | The picker missed probes that check a command only through `skill_called` (`cmd-delegated-load`, `cmd-delegated-git`) | `commands_of()` also reads `skill_called` patterns; `skill_not_called` still does not count |
| 3 | Minor | plan.md assumed a commit outside `--through`, left "design doc" open, and the RULES_DOCS gate did not know "plan anyway" | "edited in the same Save as the plan so both land in the plan's commit"; scope is `04-design.md` or `docs/specs/*-design-*.md`; the gate adds "or planned past by the owner at the /sc:plan Load step" |
| 4 | Minor | A user already on `feature/<slug>` was stopped, while the Branch step said "stay" | The branch condition applies only "while the current branch is a default branch" |
| 5 | Minor | The Save step and two gotchas did not mention the `--through` stop conditions | The Save step points to them; `existing-intent` ends the run under `--through`; `through-on-default` says "a default branch (the Branch step)" |
| 6 | Minor | Unit tests pinned 6 of 12 end states and nothing in `changed_commands`/`main` | One parametrized test asserts the full pass/fail vector for 13 end states; a tmp-repo test covers README-only, a command change, no tag and a bad ref |
| 7 | Minor | The probe passed a run that left the last step uncommitted; `overdue` was checked by exit code only | New clean-tree check (`git status --porcelain` empty; the three live runs ended clean); evals/README states the exit-code limit |
| 8 | Minor | One `CANARY_OK=1` clears both gates; the no-tag message named only `canary-gates` | The message names both targets. One variable stays: AGENTS.md asks for both reports |

A mutation spot check after the change: making the "main at baseline" check always pass turns the `main fast-forwarded` case of the parametrized test red.

Before the 4.33.2 release: `make canary-gates` passed all 7 hard-gate checks (RULES_DOCS changed), and the new `make canary-commands` picked `plan-draft-spec-gate` (4/4) and `intent-through-branch` (13/13, 4.0 min).
