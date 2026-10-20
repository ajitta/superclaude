---
status: complete
revised: 2026-10-20
---

# Run record: one prompt from intent to done

Question: can a user type only the intent and have the Large chain (`/sc:intent` → `/sc:brainstorm` → `/sc:review --scope spec` → `/sc:design` → `/sc:plan` → `/sc:implement --plan` → `/sc:review --scope branch` → `/sc:test` → `/sc:reflect`) run to the end from one prompt, without stopping at each command's approval step?

Answer: yes. The hand-written `/goal` prompt needed a judging line before it ended reliably. That finding led to `/sc:intent --through`, which ran clean in 4 of 4 runs, bare and wrapped in `/goal`.

## Setup

- Scratch repo: a 50-line todo CLI (`todo.py`: add, list, done; `todos.json`; 3 pytest tests; `make test`), the same one now in `evals/fixtures/intent-through/`.
- superclaude 4.32.2 working tree, `superclaude install --force --scope project` into the repo.
- `claude -p --model sonnet --permission-mode auto --setting-sources project,local --output-format stream-json --verbose`, `CLAUDE_CONFIG_DIR` holding only the OAuth credentials, `ENABLE_CLAUDEAI_MCP_SERVERS=false`. The init event listed no synced plugin or connector in any run.
- Claude Code 2.1.303. Run 1 had the insight Stop hook off (`SUPERCLAUDE_INSIGHT_PROMPT=0`); every later run had it on, as users do.
- The same intent every time (Korean in runs 1–8 and 11–14, English in 9–10 and 15):
  - Problem: todos have no due dates, so I can't tell what has slipped.
  - Proposed outcome: attach a due date on add; see only the past-due ones.
  - Affected: just me, using the todo CLI.
  - Constraints: the current todos.json must still load; no external libraries.
  - Done when: an overdue command lists only past-due todos, and the existing todos.json still works.

## Prompt variants

- **v1 `/goal`:** intent + the step list + "do not ask, pick ★, record as delegated; no push, deploy, delete or outside send" + a completion clause (plan `Result:` line, test exit 0, branch review Critical 0, reflect gap against Done when; or stop after 40 turns).
- **v2 `/goal`:** v1, plus "call each command with the Skill tool", and the completion clause as six items the last turn must print.
- **v3 `/goal`:** v2, plus a judging paragraph: "this /goal is my approval for every step; the commands' confirmation and question steps, and how a command was called, are not judged; a subagent's review report counts as /sc:review output".
- **plain:** v2 without `/goal` and without the 30-turn clause, ending "when done, print the six items".
- **`--through`:** `/sc:intent --through` followed by the five lines (this round's change to `commands/intent.md`).
- **`/goal` + `--through`:** `/goal sc:intent --through` + the five lines + "Judging: --through is the approval for every step, so the commands' confirmation steps are not judged. Met when the last turn prints the six items of the Report step."

## Results

| # | Variant | Minutes | Evaluator "not met" | How it ended | Commands via Skill | Work on |
|---|---|---|---|---|---|---|
| 1 | v1 `/goal` | 3.6 | 1 (mid-run, correct) | met | 0 of 9 (read the command files with `cat`) | `feat/` branch |
| 2 | v1 `/goal` | 13.1 | 12 | Stop-hook block cap (9 in a row) | 9, after the evaluator asked | main |
| 3 | v2 `/goal` | 5.0 | 0 | met | 9 | main |
| 4 | v2 `/goal` | 7.9+ | 20 | stopped by hand | 10 | main |
| 5 | v3 `/goal` | 5.3 | 0 | met | 9 | main |
| 6 | v3 `/goal` | 6.6 | 2 (the second correct) | met | 9 | main |
| 7 | plain | 6.3 | — | finished | 9 | main |
| 8 | plain | 5.2 | — | finished | 9 | main |
| 9 | v3 `/goal`, English | 4.1 | 0 | met | 9 | `feature/` branch |
| 10 | v3 `/goal`, English | 4.2 | 0 | met | 9 | `feat/` branch |
| 11 | `--through` | 4.3 | — | finished | 8 (intent expanded) | `feature/todo-due-dates`, main untouched |
| 12 | `--through` | 4.4 | — | finished | 8 | same |
| 13 | `/goal` + `--through` | 4.4 | 0 | met | 8 | same |
| 14 | `/goal` + `--through` | 3.3 | 0 | met | 8 | same |
| 15 | `--through`, canary probe (`run_eval.py --canary`, default permission mode, English) | 4.4 | — | finished, 8/8 checks | 8 | `feature/` branch, main and the local remote at baseline |

Checked in every workspace after the run, not taken from the transcript:

- Every run wrote all six docs (00-intent, 01-discovery, 04-design, 05-plan, 06 reflect, README), and the plan carries a `Result:` line naming the last code commit with a green run. `make test` passes in all 15 (12 to 36 tests, from 3).
- 00-intent holds the five lines verbatim, with the requester's `Done when:` line (4.32.2) in all 15. Every reflect doc compares the delivery against that line.
- `todos.json` unchanged, only standard-library imports added, nothing pushed (runs 1–14 had no remote; run 15's local remote stayed at baseline).
- Discovery decisions: 4 to 8 per run, all tagged `delegated`. In the audits read (runs 1, 2 and 4), the independent agent picked the recorded ★ option for every audited question.
- The isolated reviewers had read-only tools in most runs, so the main session ran the tests; branch reviews found real Important defects in several runs (a blank title saved in run 1; a non-string `due` crashing `overdue` in runs 3 and 6), each fixed with the Proof re-run.

## Findings

1. **Both one-prompt routes reach the end.** The model followed the command bodies through every gate under the up-front delegation. In headless mode, results from background reviewers arrive as new turns, so even the plain prompt did not stall (runs 7–8).
2. **`/goal`'s evaluator reads the whole goal text as the condition.** A process sentence ("run these commands in order") became a requirement on history that cannot be changed afterwards. In run 2 the evaluator kept saying "brainstorm never ran" after an inline first pass, and the run ended only at Claude Code's Stop-hook block cap.
3. **The evaluator imports the commands' own approval steps.** It sees the expanded command bodies in the transcript and held run 4 open 20 times on "/sc:intent's Approve step was not confirmed by the user" and "the Critical 0 came from a subagent, not from /sc:review itself", even with the delegation sentence in the goal.
4. **A judging paragraph fixes it.** Stating that the goal is the approval, that the commands' confirmation steps and call style are not judged, and that a subagent's review counts: 4 of 4 met (runs 5, 6, 9, 10). The one later "not met" (run 6) was correct, because the last turn did not reprint the evidence after a post-review fix.
5. **Branch placement was left to chance.** Only 4 of 10 template runs moved off main. `--through` states the branch rule, and 4 of 4 put every commit on `feature/todo-due-dates` with main untouched.

## Decisions

- `/sc:intent --through` instead of a new command: the chain already starts at intent, the command count stays, and it does not overlap `/sc:pm` or `/sc:agent`. Without the flag, intent behaves as before.
- The flag's Run step owns the branch rule, the delegation rule and the early-stop conditions (an irreversible or outward choice, a Critical finding open after one fix round, a red Proof). Its Report step prints the six evidence items, so a `/goal` wrapper needs only a one-line judging rule.
- README and the Pages site show `--through` and the `/goal` wrapper with its judging line. The hand-written template is not published.
- Canary probe `intent-through-branch` (canary-only, not a gate) guards the branch and no-push contract. Mutation check on run 15's workspace: pushing the branch to the local remote turns the safety check red, and fast-forwarding main onto the branch turns the scope check red.

## Limits

- Fifteen runs, one model (sonnet, default effort), one small task. A larger change, opus or an interactive session may stop at different places.
- The evaluator is Claude Code's small fast model (Haiku by default); its readings above are from Claude Code 2.1.303.
- Every decision was delegated. Nothing here measures whether the delegated choices match what a user would have answered; the audit only checks that an independent agent picks the same option.
