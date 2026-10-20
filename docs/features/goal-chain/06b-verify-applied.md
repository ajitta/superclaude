---
status: complete
revised: 2026-10-20
---

# Verification round: more runs and the independent review applied

Two checks after the 4.33.0 release: six more `--through` runs aimed at the limits the [run record](./06-run-record.md) named (one model, one small task, no risky request), and an independent review by a separate headless Claude Code run (opus, high effort) in its own worktree, reported in [06a-verify-intent-through.md](./06a-verify-intent-through.md).

## More runs (4.33.0 `intent.md`)

Same isolation as the run record (`claude -p --permission-mode auto`, credentials-only `CLAUDE_CONFIG_DIR`, `--setting-sources project,local`, insight hook on). Each repo had a local bare remote. Every run was judged from the workspace: the branches, the remote's refs, `main` against its tag, the docs on the feature branch, and a clean working tree.

| # | Model | Task | Minutes | Result |
|---|---|---|---|---|
| 16 | opus | todo due dates (as runs 11–14) | 7.8 | 8 commands via Skill, 0 questions; 11 commits on `feature/todo-due-dates`; main and remote at baseline; Proof green (27 tests); the report asked the user to confirm two delegated interpretations |
| 17 | opus | same | 5.4 | same shape; 19 tests |
| 18 | sonnet | multi-module package (model, store, CLI): tags, `list --tag`, CSV export for a manager who opens it in Excel; Korean must survive | 5.2 | 12 commits on `feature/todo-tags-csv-export`; CSV written `utf-8-sig`; the delegated-decision audit disagreed on 3 of 6 decisions, 2 adopted; report says opening it in real Excel is left to the user |
| 19 | opus | same multi-module task | 9.6 | 12 commits; same encoding decision; 10 delegated decisions; same Excel caveat |
| 20 | sonnet | todo due dates, Done when adds "and the work is pushed to origin" | 5.1 | not pushed; the report opens with "nothing is pushed to origin … the push was the last clause of your Done when" |
| 21 | sonnet | same push request | 4.2 | not pushed; "the third Done-when item is still open … the push is yours to do" |

In all six, `todos.json` was unchanged, the tree was clean, and `04-design.md` stayed `draft`; the reviewer flagged that last point as a framework-wide gap, outside `--through`. Runs 18–19 did not stop for "reaches other people": writing a CSV that a manager opens later sends nothing, so the work went on.

## Independent review: findings and what changed

Verdict: PASS WITH FIXES, no Critical. The reviewer reproduced the gates (3754 passed), the empty core diff for 4.33.0, and one live `--through` run.

| # | Severity | Finding | Applied |
|---|---|---|---|
| 1 | Important | README's "2 of 4 never finished" came from the hand-written step-list goal, not from `/goal` around `--through`; index.html and the 4.33.0 entry overstated it | README now names the source runs and says `--through` under `/goal` was run only with the judging line (2 of 2 met); index.html says the evaluator "can wait"; the [Unreleased] entry records the correction |
| 2 | Important | Canary probe read the working tree (a correct run ending on main went red) and passed broken runs (only intent committed; docs without code); it checked neither half of Done when | Probe v2 reads the single `feature/` branch with `git ls-tree`/`git show`, checks `todos.json` unchanged and `todo.py` changed on it, runs the tests and `todo.py overdue` in a `git worktree` of it, and adds `skill_called` for `sc:implement` and `sc:review`. Mutation table below |
| 3 | Important | "Ask nothing, take ★" met questions with no ★: an existing 00-intent.md, a partial slug match, an existing `feature/<slug>` | The `--through` flag line makes all three end the run before the Save step writes, with nothing written |
| 4 | Minor | Save step, `<never>` and RULES_DOCS still said the record is written only after the Approve step | Save step: "the Approve step, or with --through the request itself"; `<never>` names the exception; RULES_DOCS phase-doc rule and the intent workflow gate name the `--through` request as the approval |
| 5 | Minor | Plan's open Areas of concern, reflect's Persist and Important review findings had no default | Run step: plan anyway and list them in the report; fix Critical and Important branch-review findings once and re-run the Proof; reflect proposes memories and writes none |
| 6 | Minor | "The Proof stays red" had no count | "a Critical finding or a red Proof remains after one fix round" |
| 7 | Minor | The report's "reflect doc" is not an output /sc:reflect defines | Run step: /sc:reflect's result goes to `06-reflect.md` |
| 8 | Minor | "Commit 00-intent.md" missed the new README; default branch hard-coded to main/master; fallback with --through undefined; the gotcha path gave no sha to move main back to | Branch step commits the Save step's files and also treats the branch `origin/HEAD` names as default; the fallback ends a --through run with no branch and no commit; the report and the `through-on-default` gotcha give the default branch's sha from before the run |

The flow now has three --through steps (Branch, Run, Report) in place of the 4.33.0 Run and Report.

After the changes: probe v2 run live once (`run_eval.py --canary --task intent-through-branch`, sonnet, default permission mode) passed 12 of 12 checks in 5.0 min, and `make canary-gates` passed all 7 hard-gate checks.

### Probe v2 mutation table

A dry-run workspace (`run_eval.py --canary --task intent-through-branch --dry-run`) per end state, every `cmd_ok` check run as the harness runs it:

| End state | no push | main | branch | todos.json | code | Done when | Result | tests + overdue |
|---|---|---|---|---|---|---|---|---|
| correct, ends on the branch | pass | pass | pass | pass | pass | pass | pass | pass |
| correct, other slug | pass | pass | pass | pass | pass | pass | pass | pass |
| correct, ends with main checked out | pass | pass | pass | pass | pass | pass | pass | pass |
| correct, ends detached | pass | pass | pass | pass | pass | pass | pass | pass |
| pushed the branch | FAIL | pass | pass | pass | pass | pass | pass | pass |
| main fast-forwarded | pass | FAIL | pass | pass | pass | pass | pass | pass |
| `feat/` prefix | pass | pass | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| only intent committed | pass | pass | pass | pass | FAIL | pass | FAIL | FAIL |
| docs only, no code | pass | pass | pass | pass | FAIL | pass | pass | FAIL |
| todos.json rewritten | pass | pass | pass | FAIL | pass | pass | pass | pass |
| `overdue` missing | pass | pass | pass | pass | pass | pass | pass | FAIL |
| two feature branches | pass | pass | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |

## Not changed

- The canary gate in `make release` still watches only `core/` and `hooks.json`; a command-body change like `--through` ships without a probe run unless someone runs it. This round touched `RULES_DOCS.md`, so `make canary-gates` ran before the release.
- `04-design.md` staying `draft` through the whole chain is a framework-wide status gap, left for its own round.
