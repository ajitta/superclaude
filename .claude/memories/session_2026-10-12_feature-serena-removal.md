branch: feature/serena-removal @0bc2f52a

# Session 2026-10-12 — serena-removal re-review fixes + branch-scoped session records

## Where it stands
- Plan `docs/features/serena-removal/05-plan.md` status complete (Phases A-G); proofs in 05e, review fixes in 05f, branch records in 05g
- Not merged, not pushed

## Done
- 313d0f56: re-review W1 — writer test checks each memory key against its owner; the old OR-logic test passed with save.md's writes removed, the new one failed under that mutation
- c2856fb7: 3 suggestions — agent-authoring.md Non-code row lists the six real agents; MODE_Orchestration.md:14 "symbol-aware tool (LSP or code index)"; Session end regex no longer breaks on "e.g."
- 0bc2f52a: W1 Deviations line in 05f uses the user's requested wording
- Phase G (05g): `last_session.md`/`next_actions.md` removed; /sc:save writes one add-only `session_[date]_[branch-slug].md` per branch and date (header `branch: <name> @<sha>`, `## Next actions` inside); /sc:load reads pm_context + newest record of the current branch. Chosen over per-branch overwritten files ([1]+[2]) because nothing is overwritten, so no cleanup step and no conflicts

## Decisions
- Auto memory is one folder shared by every worktree of the repo (evidence: no worktree dir under `~/.claude/projects/`; `project_authoring-skill.md` saved from the worktree sits in the main folder) → name the branch in entries, Edit single MEMORY.md lines
- No legacy fallback for the old fixed names: the folder is new on this unmerged branch

## Problems hit
- A `/goal` stop-hook check kept demanding "test FAILs before the fix" ordering for W1, unsatisfiable because the fix is the test. Replayed break → fail → restore → pass on a temp copy; only `/goal clear` ends it. Local feedback draft queued, not sent

## Left untouched by instruction
- Review items S1, S3, S4, S6; guard-token expansion; docstring-test expansion

## Known residue (not in scope)
- Serena traces remain in CI workflow files, `.gitignore`, the tracked `.serena/` directory and CHANGELOG
- Live /sc:save → /sc:load behaviour unverified end-to-end (tests check instruction text only)

## Next actions
- [ ] User decision: merge `feature/serena-removal` into master and push
- [ ] Next version-bump commit: CHANGELOG lines from 05-plan.md "Release note"
- [ ] Optional: in a fresh session, `/sc:load` should pick this record by branch
- [ ] authoring-skill worktree: merge master (it will then use branch records too), then /sc:plan
- [ ] structured-output-style issue 01: needs name/scope/notation decisions
