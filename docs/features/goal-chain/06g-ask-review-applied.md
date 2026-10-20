---
status: complete
revised: 2026-10-20
---

# Third review applied: `--ask`

The independent review of `v4.33.2..HEAD` ([06f-verify-ask.md](./06f-verify-ask.md)): PASS WITH FIXES, no Critical. It reproduced the gates (3770 passed) and one headless `--through --ask` run (3.7 min, fell back to plain `--through`, every row `delegated`).

| # | Severity | Finding | Applied |
|---|---|---|---|
| 1 | Important | "25 earlier `--through` runs" mixed in 10 hand-written-prompt runs; 154 and 8 could not be checked from the repo; CHANGELOG said "all of this kind" | 06e names the run set (runs 1–22, of which 1–10 hand-written, plus three unnumbered probe runs), says the 154 come from a script re-count of each branch's discovery table, and lists all 8 disagreements by run and decision: 6 about what the user gets, 2 on tag normalization (the border). CHANGELOG says the same |
| 2 | Important | "which behavior a case gets" let in what 06e calls build details (run 24 spent a slot on case matching); no ranking past four | The criterion now reads "what counts, which items a command returns or leaves out (matching rules included), what output holds and where it goes", names validation, storage, parsing and error wording as build details, and ranks past four: Done when / Proposed outcome first, then output and its destination. `checkpoint-creep` names the same build details |
| 3 | Minor | "D2 추천" in chat is confirmed by intent's wording but delegated by brainstorm's heuristic | An answer to a question, an Other text or a pick of the ★ makes that row `confirmed` even where the brainstorm Decision-mode tag step would say delegated |
| 4 | Minor | The Checkpoint is step 9 but runs inside step 8 | The Run step's chain now reads "/sc:brainstorm → (with --ask) the Checkpoint step → /sc:review …" |
| 5 | Minor | The form's limits (2–4 options) and a form that closes without an answer were undefined; under `/goal` a declined form may not be waited for | 2–4 options, ★ first; fewer than two recorded options stays delegated; a timeout continues as plain `--through`; README notes the `/goal` case |
| 6 | Minor | A dependent row left delegated kept options picked before the answer | Its options and ★ are re-picked under the answer |
| 7 | Minor | No probe runs `--ask`; the release gate never exercises the new text | New canary probe `intent-through-ask-headless`: the `intent-through-branch` task with `--ask`, plus a check that no discovery row comes out `confirmed`. `make canary-commands` picks it with the branch probe. Unit test: its checks extend the branch probe's, and the extra check fails on a `confirmed` row |
| 8 | Minor | `--audit-delegated` was always passed, even with no delegated row left | No delegated row left → the spec review runs without it |

Outside the branch, also applied: RULES_DOCS's `/sc:brainstorm -> /sc:design` gate names the `--through` request as the approval (with `--ask`, the Checkpoint answers). Left open: brainstorm's decision modes have no rule for an Other text outside `--through`.

Before the 4.34.0 release: `make canary-gates` passed all 7 hard-gate checks, and `make canary-commands` ran `intent-through-branch` (13/13, 3.7 min) and the new `intent-through-ask-headless` (14/14, 4.0 min).
