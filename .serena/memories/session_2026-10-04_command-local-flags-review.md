# Session 2026-10-04 — command-local-flags review/refine, follow-up plan, flow-step guidance research

Goal set via `/goal`: review + refine the earlier command-local-flags work (8818fab8 hook, b6026ba2 33 `<flags>` sections). **Done.**

## Landed (verified)
- Review: hook code (`context_loader.py` `_command_dirs`/`flag_entries`/`_command_flags`/`_declared_flags`, directive skip) and tests clean; all `<flags>` value enums match `<syntax>`; all section pointers resolve except below.
- `eafd5e96` (merge `a0a8fd28`, pushed, master CI success) fixed three `<flags>` entries:
  - troubleshoot `--fix` pointed at "the rule in the command description" (frontmatter only; the flow ran Test/Fix unconditionally) → entry now states the gate: without --fix stop after Confirm and propose; approval-required tier still waits.
  - cleanup `--dry-run` read as docs-only → preview for any --type.
  - spec-panel `--focus` (own enum under a global name) had no entry → added, points at focus areas section.
- Suite at the time: 2716 passed, 1 skipped. Local scope re-synced; hook replays clean, control `--safe go` still gets the hint.
- Assumption (not verified this session): frontmatter `description` is not part of the command body the model reads at run time.

## Decided via interview (AskUserQuestion), recorded in the plan
- Step refs: label-based ("the Analyze step") + tests; label unlabeled flow steps (prompt 1-7, auto-improve 1/4) without changing sentences; test scope = `<flags>` + whole-body step refs + `<flags>` section/gotcha pointers.
- Global flag value-list test vs core/FLAGS.md → analyze `--focus` gets an entry (`rules` is outside the global enum).
- business-panel: normalize `<flags>`; `--focus domain` auto-picks experts only when `--experts`/`--all-experts` absent, else ignored.
- Doc location: `[f]` feature folder.

## Where it stands
- `docs/features/command-local-flags/05a-plan-pointer-checks.md` (status draft, 14.3KB) + folder `README.md` — **untracked on master**, meant to be committed in the plan's Phase 1.
- Plan gaps found after writing: `core/rules/RULES_DOCS.md:67` "brainstorm.md flow step 6" is a 30th numeric ref outside commands (plan test scope misses it); only prompt step 2 is referenced.
- **Blocked on a decision:** flow direction. Research (see auto-memory `reference_prescriptive-steps-guidance`) found Anthropic guidance against prescriptive step lists for judgment tasks, but no official source tying `<flow>` steps to dynamic-workflow failures. 05a entrenches flow labels, so decide flow direction first.
- Set aside: removing only the numbers from `<flow>` — no behavior gain (a bullet list is still a sequence), loses the order signal xml-prose-format assigns to numbered lists (10 gated flows depend on it), silently breaks 30 numeric refs. Real lever = rewrite judgment flows as goal + constraints + done criteria; unmeasured, documented check is A/B on real tasks.
- Flow census (heuristic grep): 36 command flows; 10 with approval/confirm gates; 21 with a Validate/Verify step (Opus 5 over-verification angle; review/troubleshoot verify steps are part of the deliverable).

## Open (to-dos live in claude-mem work_state list `command-local-flags`)
1. Decide flow direction. 2. Revise 05a. 3. `/sc:review --plan` then `/sc:implement --plan`. 4. Optional: `/sc:promote-feature command-local-flags`, delete merged local branch `docs/command-local-flags-refine`, `/sc:insight --review`.
