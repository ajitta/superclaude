# Phase 2 analysis 03b — modes/ and skills sc-author, sc-prompt — part 3 of 3

> Continuation of [part 1](./03b-analysis-modes-skills-1.md) (split by size; content unchanged).

## 5. Top 10 findings (ranked)

1. **I0 gap is total for the model's own behavior.** No mode or skill in scope contains a step that makes the model state the purpose behind the request and derive a success criterion before acting. The three nearest things are sc-prompt's Context targets ('Reason: why the work is asked for' — but it repairs the user's prompt for another session), RESEARCH_CONFIG's three-word gate 'planning: objectives+strategy+criteria' (never injected by the mode), and Brainstorming's example question 'Problem solved?' (asks the user, example only). MODE_Task_Management's own example takes 'Implement auth system' straight to Phase 1-4.

2. **MODE_Task_Management reinforces A3 instead of remedying it.** 'Orient to the current position (load context, identify the phase, resume) before acting', 'resume from the last checkpoint' and the bound 'never ... work outside the task list once one exists' tell the model to re-enter a prior plan without checking whether evidence has invalidated it. This is the one mode that governs re-entry after a session break and it has no re-plan trigger. Rewrite State-Aware as: re-read the goal, list evidence gathered since the plan, decide whether the plan survives, then resume.

3. **Post-compaction re-entry rule is missing where it belongs.** MODE_Token_Efficiency <compaction> defines the trigger (60 %) and the preserve list but says nothing about what the model does on the first turn after /compact. A3 fixtures need: restate purpose and criterion from the preserved summary, re-validate the open plan against current file state. Zero bytes exist for this.

4. **MODE_Token_Efficiency example works against R3.** Row three of <examples>: 'Listing all six options considered before the recommendation → The recommendation, and the one option that was close.' Under --uc this instructs exactly the compression the R3 fixture measured ('Decision: No' with the conditional buried). Replace with: keep every live option and its condition; drop the narration of how they were found.

5. **MODE_Introspection is 2.3 KB of exhortation in the one mode that should own A3.** Every section is D: 'State assumptions, then verify', 'Check against superclaude standards' (repo leak), emoji markers. Either delete the mode or rebuild it as the self-anchor remedy: a mandatory 'what would make my current plan wrong, and have I seen it' check with a re-plan rule.

6. **Largest A/D deletions (approx. 21 KB).** MODE_DeepResearch <example quoting-retrieved-sources> 1.1 KB (paraphrase policy, unrelated to research); MODE_Verbalized_Sampling paper provenance + research gotchas ~1.4 KB; quality.md Writing guidance 1.8 KB + Audit checklist 0.7 KB + provenance 1.4 KB; format-xml 'When tags help' 0.4 KB (A); every <role><mission> and <thinking> block across the eight modes ~3.6 KB; RESEARCH_CONFIG <replanning> + execution gate 0.7 KB (verbatim duplicates of the mode); sc-prompt invocation table 0.9 KB; the five 'Project format and language' restatements of the isolation rule in sc-author references ~2.0 KB; modes/README.md 3.0 KB (not injected, but carries a repo path and pytest command).

7. **Real B mechanisms worth keeping (6.6 KB total).** DeepResearch Source-Verification (≥2 sources, A2) and Replan (A3); RESEARCH_CONFIG <reflection> (A3); Verbalized Sampling 'set, not a ranking ... the user picks' and label-after-text (R3/A3); sc-author preamble isolation of in-context rules and project docs (A2) plus evidence-before-removal; sc-prompt Embedded-anchor row (A1: own estimate and criterion first, prior afterwards as one input), Verifiability switch (criterion stated first), Context targets Reason/Quality bar (I0), 'never use a recalled value in place of a read' (A2); Orchestration Schema-vs-Evidence (A4). Note that the only R3 mechanics (VS, Business Panel) are opt-in overlays and never reach a default session.

8. **Exhortations that read as remedies but are D.** Business Panel 'Assumption Surfacing: Make implicit assumptions explicit before concluding' (stated twice, no gate); DeepResearch <thinking> 'question each source and look for bias'; Introspection 'Hypothesis-Testing: State assumptions, then verify'; Orchestration 'Verification-First ... never assume correctness'; Brainstorming 'Discover constraints > assume them'; Business Panel 'skipping context gathering' in <never>. None changes ordering or what information reaches whom.

9. **sc-author has the success-criterion step in the wrong place.** Step 7 produces 'one or two [prompts] that should trigger the document and one similar that should not' — that is a success criterion for the document, generated after it is written. Moving it to Step 1 (before Resolve settles path/format) gives the skill an I0 gate: what behavior should this document change, and which prompt would show it. Also missing from Step 1: the purpose of the document, as opposed to its type.

10. **Five-fold and two-fold duplication of the few B rules.** VS post-hoc-label rule appears in <thinking>, <behaviors>, <output_format>, <gotchas> and <bounds>; Replan appears in MODE_DeepResearch and twice in RESEARCH_CONFIG; the sc-author isolation rule appears in the preamble, Step 3, format-xml and four type references. Keep one copy each at the point of use (the behaviors/steps), drop the rest: ~3 KB.

## 6. Not read

- ~/.claude/, the repo's .claude/, docs/, CHANGELOG.md, README.md (root), tests/, core/, agents/, commands/, mcp/, output-styles/ — excluded by the isolation rule.
- src/superclaude/ARCHITECTURE.md and scripts/context_loader.py — grepped only for mode delivery (on-demand whole-file injection, README skipped, RESEARCH_CONFIG not injected); not classified.
- core/rules/RULES_DELEGATION.md, core/FLAGS.md, commands/sc/save.md — pointed to by Orchestration/Token-Efficiency/Research sections; out of scope, so the duplicate/pointer judgments assume the SSOT exists there as stated.
- skills/sc-author/references/fields.yaml `tool_names` list and per-type field lists were not verified against Claude Code docs (web search forbidden); classified C on the assumption they are accurate.
