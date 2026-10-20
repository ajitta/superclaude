---
status: complete
revised: 2026-10-20
---

# `--through --ask`: one decision checkpoint

## Why

Across 25 earlier `--through` runs, all 154 discovery decisions were `delegated`. They fell into two kinds:

- **What the user gets or sees** (2–4 per run): does a todo due today count as overdue, do done todos show, does `list` show the date, AND or OR for several tags, CSV to a file or to stdout.
- **How it is built** (the rest): date parsing, storage shape, bad-input handling, tag normalization.

The independent audit disagreed with 8 of the 154 (6 of them in the two multi-module runs), almost all of the first kind. The runs that asked the user to confirm readings after the fact (runs 16 and 22) also asked about the first kind. The audit compares one model's choice with another's, so it cannot tell what this user wants. `--ask` moves only those questions to the user, once, and leaves the rest unattended.

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

All four: every commit on `feature/<slug>`, main and the local remote at baseline, clean tree, `Result:` line, tests green.

Run 24 is how the "declined form" rule came about: the model stopped and waited without the command telling it to, and the chat answers worked. The Checkpoint step now says so explicitly.

## Limits

- Four runs, sonnet only. In run 24 the cap of four left one question of the first kind (do finished todos appear in a filtered export) delegated, while a case-sensitivity question took a slot.
- No canary probe: a headless probe cannot answer a form, and the headless fallback is the plain `--through` path the `intent-through-branch` probe already covers.
