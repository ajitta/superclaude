---
status: complete
revised: 2026-10-20
---

# `--through --ask`: one decision checkpoint

## Why

The source set is the 25 one-prompt chain runs in this folder: runs 1–22 ([06-run-record](./06-run-record.md), [06b](./06b-verify-applied.md), [06d](./06d-followups-applied.md); runs 1–10 were hand-written prompts, 11–22 `--through`) plus three unnumbered probe runs (the 4.33.1 live probe, the second review's live run, the 4.33.2 `canary-commands` run). A script re-counted the Resolved Decisions tables of each run's `01-discovery.md` on its branch: 154 rows, every one `delegated`, 4 to 9 per run.

The decisions fell into two kinds:

- **What the user gets or sees:** does a todo due today count as overdue, do done todos show, does `list` show the date, AND or OR for several tags, CSV to a file or to stdout.
- **How it is built:** date parsing, storage shape, bad-input handling.

The independent audit marked 8 of the 154 as differing. Run 16 (opus) and run 9 differed once each, on whether `list` shows the due date. Run 18 differed on D2 (a `tag` command for existing todos), D5 (where export writes) and D6 (tag normalization). Run 19 differed on Q5 (where export writes), Q6 (tag normalization) and Q7 (the CSV tag separator). So 6 are clearly of the first kind, and 2 (tag normalization, which decides whether `Work` matches `work`) sit on the border. Runs 16 and 22 asked the user afterwards to confirm two readings each, all of the first kind (done todos in `overdue`, a todo due today). The audit compares one model's choice with another's, so it cannot tell what this user wants. `--ask` moves only those questions to the user, once, and leaves the rest unattended.

## What it does

The Checkpoint step (`commands/intent.md`, inside the Run step, after brainstorm and before the spec review):

- It picks from brainstorm's Resolved Decisions the ones that change what the user gets or sees, up to four, and asks them in one AskUserQuestion form with the ★ option first.
- An answer turns that row `confirmed` and rewrites the spec sections that follow from it; the other rows stay `delegated` for the spec review's audit.
- A declined form waits for the user's reply and applies answers given in chat.
- With no way to ask (headless), the run continues as plain `--through`.
- The Report step says which decisions the user answered.

## Runs (sonnet, 4.33.2 + this change)

| # | Mode | Task | Checkpoint | Result |
|---|---|---|---|---|
| 23 | interactive tmux | todo due dates | One form, 4 questions (due today, done todos, where the date shows, order). All four are about what the user gets; bad-date handling and date format stayed delegated. Answered 3 against ★: due today counts, date shown in `list` too, order by id | 6 min 12 s; rows D1, D2, D3, D6 `confirmed`, D4–D5 `delegated`; a separate commit "record checkpoint answers in discovery"; on a scratch todos.json the built `overdue` listed the item due today, hid the done one, kept id order, and `list` showed dates |
| 24 | interactive tmux | multi-module tags + CSV (Korean) | One form, 4 questions (several tags, case, where export writes, CSV columns). The form was dismissed by a stray key ("User declined to answer questions") and the session waited; the answers were then typed in chat: "D1 OR, D2 추천, D3 기타: 항상 파일(todos.csv)로 쓰고 --out으로 경로만 바꿈, D5 추천. 계속 진행" | 5 min 12 s; D1 `confirmed: any one tag (OR)`, D3 `confirmed: other — always the file todos.csv; --out changes only the path`, D2/D5 confirmed on ★, D4/D6/D7 delegated; the built CLI matched: OR filter, case-insensitive match, `export` wrote `todos.csv` with a BOM and the `note` column, `--out w.csv` wrote there |
| 25 | headless `-p` | todo due dates | No AskUserQuestion call | Continued as plain `--through`; all 7 rows `delegated` |
| 26 | headless `-p` | same | "AskUserQuestion isn't available in this session, so the Checkpoint can't ask. I'm continuing as plain `--through`" | All 6 rows `delegated`; the report says none were confirmed because the checkpoint could not ask |
| 27 | interactive tmux, opus | todo due dates | One form, 4 questions (due today, done todos, order, `list` view); 3 answered against ★ (due today counts, id order, `list` shows the date) | 6 min 14 s; D3, D4, D6, D8 `confirmed`, five build rows `delegated`; the built CLI matched all four answers |
| 28 | interactive tmux, opus | multi-module tags + CSV (Korean) | One form, 4 questions: several tags, done todos in filtered output (the question run 24 left out), CSV columns, where export writes; all 4 answered against ★ (OR, open only, Korean headers, always a file) | 12 min 29 s; four rows `confirmed`; the built CLI matched: OR filter without done todos, `todos.csv` with a BOM and headers `번호,할 일,완료,태그`. The self-review agent left an untracked `.claude/agent-memory/`; the run asked whether to delete it instead of deleting it |

All six: every commit on `feature/<slug>`, main and the local remote at baseline, clean tree, `Result:` line, tests green.

Run 24 is how the "declined form" rule came about: the model stopped and waited without the command telling it to, and the chat answers worked. The Checkpoint step now says so explicitly.

## Limits

- Six runs, two models, two tasks. In run 24 the cap of four left one question of the first kind (do finished todos appear in a filtered export) delegated, while a case-sensitivity question took a slot; opus asked it in run 28. The Checkpoint step now ranks what to keep when more than four qualify.
- A headless probe cannot answer a form. `intent-through-ask-headless` covers the fallback (no `confirmed` row, no stop to wait); the form is checked by hand.
- Outside `--ask`: the self-review agent's memory folder lands untracked in the user's repo (run 28). Left for its own round.
