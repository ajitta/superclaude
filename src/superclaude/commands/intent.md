---
description: Capture a request as an intent record in the requester's own words — problem, proposed outcome, affected users and systems, constraints, open questions — before any analysis. Use ONLY when user explicitly types `/sc:intent` — writes docs/features/<slug>/00-intent.md, so a wrong fire creates a file unasked. Do NOT auto-trigger on "I want X" statements, feature ideas mentioned in passing, or requests to explore or design — those get a direct answer or /sc:brainstorm.
---
<component name="intent" type="command">

  <role command="/sc:intent">
    <mission>Capture a request as an intent record in the requester's own words — problem, proposed outcome, affected users and systems, constraints, open questions — before any analysis</mission>
  </role>

  <syntax>/sc:intent [request]</syntax>

  <flow>
  1. Capture: Keep the user's request verbatim as the seed. No rewording.
  2. Fill: Ask only about the items of the five the seed leaves empty — one question per item, five at most. Stop when the user says it is enough.
  3. Draft: Fill the five items quoting the user's wording; a field the user never addressed reads "not stated". No solutions, alternatives, architecture, or added scope. One page at most.
  4. Approve: Show the draft; the user corrects the sentences. Nothing is written without confirmation.
  5. Save: feature path `docs/features/<slug>/00-intent.md` — slug resolution (zero match → new feature folder; intent has no standalone path), frontmatter `status: approved-for-plan` (the Approve step precedes the write) + `revised: <today>`, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`; a folder created here gets its README with `phase: intent`.
  6. Handoff: Large work goes to /sc:brainstorm, Medium to /sc:plan (tiers per core/rules/RULES_QUALITY.md `<checklist_scaling>`), each with 00-intent.md as input.
  </flow>

  <outputs>
  - `docs/features/<slug>/00-intent.md`: the record, in the shape of the intent-skeleton example below.
  </outputs>

  <tools>
  - Glob: slug match over docs/features/
  - Read: existing feature folder + README check
  - Write: 00-intent.md and, for a new folder, its README
  - Edit: an existing folder's README entry
  - Bash: `git config user.name` for the Author line
  - AskUserQuestion: the Fill step
  </tools>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:intent 'exports time out for big customers'` | Two questions (affected systems, constraints) → `docs/features/export-timeouts/00-intent.md` |
  | `/sc:intent 'hook output must not block the prompt'` with `docs/features/hook-latency/` present | Exact slug match: `00-intent.md` added to that folder, its README gets the entry |
  | `/sc:intent 'rename this variable'` | Trivial: no file; says the request needs no intent record and answers it directly |

  <example name="intent-skeleton">
# Intent: title in the requester's words

Author: username.

## Problem
What cannot be done today, quoted from the requester.

## Proposed outcome
What better looks like, quoted from the requester.

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
  - rephrase-drift: the user's wording gets smoothed into cleaner prose → restore the quoted original.
  - question-flood: questions continue after every item is filled → go to the Draft step; five is a ceiling, not a target.
  - existing-intent: the folder already holds 00-intent.md → show it first; the user picks revising it in place (bump `revised`, no second README entry) or moving it to archive/ per RULES_DOCS Superseded versions.
  </gotchas>

  <bounds>
    <does>captures the request verbatim, asks only about the empty items, and saves after approval.</does>
    <never>proposes solutions, alternatives or architecture, widens scope, saves before approval, or runs discovery in brainstorm's place.</never>
    <fallback>a Trivial or Small request (a rename, a one-file fix, a question with one answer) gets no file — say so and answer it directly.</fallback>
  </bounds>

  <handoff next="/sc:brainstorm /sc:plan /sc:design"/>
</component>
