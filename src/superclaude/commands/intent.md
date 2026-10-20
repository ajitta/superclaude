---
description: Record a request in the requester's own words (problem, outcome, affected users, constraints, open questions) as docs/features/<slug>/00-intent.md. On request only — the user's /sc:intent or a workflow step that names it. Not for ideas mentioned in passing — answer directly or use /sc:brainstorm.
---
<component name="intent" type="command">

  <role command="/sc:intent">
    <mission>Capture a request as an intent record in the requester's own words — problem, proposed outcome, affected users and systems, constraints, open questions — before any analysis</mission>
  </role>

  <syntax>/sc:intent [request] [--through]</syntax>

  <flow>
  1. Capture: Keep the user's request verbatim as the seed. No rewording.
  2. Fill: Ask only about the items of the five the seed leaves empty — one question per item, five at most. Stop when the user says it is enough.
  3. Draft: Fill the five items quoting the user's wording; a field the user never addressed reads "not stated". A completion signal the user stated (how they will know it worked) goes under Proposed outcome as a quoted `Done when:` line; none stated → no line, never inferred and never asked for. No solutions, alternatives, architecture, or added scope. One page at most.
  4. Approve: Show the draft; the user corrects the sentences. Nothing is written without confirmation.
  5. Save: feature path `docs/features/<slug>/00-intent.md` — slug resolution (zero match → new feature folder; intent has no standalone path), frontmatter `status: approved-for-plan` (the Approve step, or with --through the request itself, precedes the write) + `revised: <today>`, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`; a folder created here gets its README with `phase: intent`. With --through, the stop conditions in the --through flag line apply before this write.
  6. Handoff: An open solution space or several affected systems → /sc:brainstorm; a clear direction → /sc:plan (/sc:design for interface or architecture work); each takes 00-intent.md as input.
  7. Branch (--through only, in place of the Handoff step): on the default branch (main, master, or the branch `origin/HEAD` names) create and switch to `feature/<slug>`; on any other branch stay. Note the default branch's sha for the Report step, then commit the Save step's files on that branch.
  8. Run (--through only): call /sc:brainstorm → /sc:review --scope spec --audit-delegated → /sc:design → /sc:plan → /sc:implement --plan → /sc:review --scope branch → /sc:test → /sc:reflect in that order through the Skill tool, and commit what each command writes on that branch; /sc:reflect's result goes to `06-reflect.md` in the feature folder. The --through request is the user's approval at every step: ask nothing, take the ★ option and record it as delegated. Where a command would ask without a ★: open Areas of concern → plan anyway and list them in the Report step; branch review findings → fix the Critical and Important ones once, then re-run the Proof; reflect's Persist → propose, write nothing. Stop and report instead when a choice cannot be undone or reaches other people, or when a Critical finding or a red Proof remains after one fix round.
  9. Report (--through only): end with (1) `git log --oneline` for the branch (2) the `status:` line of each doc in the feature folder (3) the plan's `Result:` line (4) the last full test run's exit code and summary line (5) the branch review's Critical count (6) `06-reflect.md`'s gap against Done when, then the branch name, the default branch's sha before the run, and the steps left to the user (merge, push).
  </flow>

  <flags>
  - --through: skips the Fill step (an empty field reads "not stated") and the Approve step (the request is the approval), saves, then runs the rest of the Large chain on a feature branch to the end: the Branch step, the Run step and the Report step. Before the Save step writes, an existing 00-intent.md in the folder, a slug that only partly matches a folder, or an existing `feature/<slug>` branch while the current branch is a default branch ends the run with nothing written: report which one and stop.
  </flags>

  <outputs>
  - `docs/features/<slug>/00-intent.md`: the record, in the shape of the intent-skeleton example below.
  </outputs>

  <tools>
  - Glob: slug match over docs/features/
  - Read: existing feature folder + README check
  - Write: 00-intent.md and, for a new folder, its README
  - Edit: an existing folder's README entry
  - Bash: `git config user.name` for the Author line; with --through, the branch switch and commits
  - Skill: with --through, each command the Run step calls
  - AskUserQuestion: the Fill step
  </tools>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:intent 'exports time out for big customers'` | Two questions (affected systems, constraints) → `docs/features/export-timeouts/00-intent.md` |
  | `/sc:intent 'hook output must not block the prompt'` with `docs/features/hook-latency/` present | Exact slug match: `00-intent.md` added to that folder, its README gets the entry |
  | `/sc:intent 'rename this variable'` | Settled by one small change: no file; says the request needs no intent record and answers it directly |
  | `/sc:intent --through 'Problem: no due dates … Done when: overdue lists only past-due todos'` on main | `feature/todo-due-dates` created; 00-intent through reflect committed there with every choice delegated; the Report step's six items, nothing merged or pushed |

  <example name="intent-skeleton">
# Intent: title in the requester's words

Author: username.

## Problem
What cannot be done today, quoted from the requester.

## Proposed outcome
What better looks like, quoted from the requester.

Done when: how the requester will know it worked, in their words. Omitted when they named none.

## Affected users and systems
Who and what the change touches, as the requester named them.

## Constraints
Limits the requester stated. Out-of-scope items go here too.

## Open questions
What the requester could not answer.
  </example>
  </examples>

  <gotchas>
  - solution-creep: a proposal slips into the draft → delete it and move the underlying question to Open questions.
  - invented-criterion: a `Done when:` line the user never said (a metric, a test, a threshold) → delete the line.
  - rephrase-drift: the user's wording gets smoothed into cleaner prose → restore the quoted original.
  - question-flood: questions continue after every item is filled → go to the Draft step; five is a ceiling, not a target.
  - through-on-default: --through commits land on a default branch (the Branch step) → create `feature/<slug>` at the current commit, switch to it and continue there; the Report step says the default branch also holds those commits and gives its sha from before the run, so the user can move it back.
  - existing-intent: the folder already holds 00-intent.md → show it first; the user picks revising it in place (bump `revised`, no second README entry) or moving it to archive/ per RULES_DOCS Superseded versions; with --through, the run ends instead (the --through flag).
  </gotchas>

  <bounds>
    <does>captures the request verbatim, asks only about the empty items, and saves after approval; with --through, runs the named commands in order on a feature branch and commits each step.</does>
    <never>proposes solutions, alternatives or architecture, widens scope, saves before approval (with --through, the request is the approval), runs discovery in brainstorm's place, or, with --through, merges, pushes, deploys, deletes or sends anything outside.</never>
    <fallback>a request settled by one small change or one reply (a rename, a one-file fix, a question with one answer) gets no file — say so and answer it directly; with --through, that also ends the run: no branch, no commit.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:plan /sc:design"/>
</component>
