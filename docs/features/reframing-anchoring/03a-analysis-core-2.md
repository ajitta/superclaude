# 03a — Phase 2 content value classification: core/ (always-loaded chain + rules modules) — part 2 of 2

> Continuation of [part 1](./03a-analysis-core-1.md) (split by size; content unchanged).

## 3. Anchor-point map

Core files have no command flow of their own; the moments below are the points at which the always-loaded chain or a rules module governs what the model receives.

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| CLAUDE_SC → FLAGS/PRINCIPLES/RULES | user's first prompt | ACTION instruction (and any prompt-embedded number, cause, prior estimate) | **none** — nothing in the chain asks for the purpose or a purpose-derived criterion. Closest: RULES `<verification_before_completion>` "Before non-trivial work, state the concrete check that will prove \"done\"" — fires *after* the request is read and derives the check from the action, not the purpose. I0: **no step states the purpose before acting.** |
| RULES `<scope_discipline>` l.17 | user describes a problem instead of requesting a change | the user's PROBLEM DEFINITION (R1/R2 anchor) | none; the rule tells the model to answer inside that frame: "the deliverable is the assessment: report findings and stop" |
| RULES_QUALITY R13 | request with 2+ plausible targets | ambiguous action instruction | partial: "state in one sentence the interpretation being acted on, then proceed" — but explicitly "Skip for: single-file edits, explicit file paths", i.e. skipped in the I0 fixture shape |
| RULES_QUALITY R03 / PRINCIPLES directive | prompt names a suspected cause or number | A1 anchor | exhortation only: "falsify before confirm"; "Evidence > assumptions" |
| PRINCIPLES directive | model reads README/docstring/comments | A2 document | exhortation only: "Code reality > documentation" |
| RULES_QUALITY R21 | tool error / test red | invalidating signal (hard failure) | B: "⚠ failed ... hypothesis ... next" + "each with a different approach" — A3 only when a failure occurs; no trigger for silent plan invalidation |
| FLAGS `<modes>` l.7 | after compaction | model's own prior state (A3 re-entry) | partial: re-reads the MODE file ("When the flag was typed but its MODE text is not in context (e.g. after compaction), Read it") — restores mode text, not plan validity; no re-plan rule |
| RULES Intent Propagation / RULES_DELEGATION `<delegate_packet>` | main loop composes a delegate prompt | user request + (for reviewers) author rationale, prior verdicts | **B**: "not the author's rationale, self-assessment or verdicts"; "[prior verdict withheld]"; findings travel "with no claim that it is fixed" |
| RULES_DELEGATION `<delegate_return>` l.45 | before dispatch | main loop's own expectation (A3 self-anchor) | **B**: "writes down the evidence shape it expects and the check that will judge it ... never a predicted verdict" |
| RULES_DELEGATION `<delegate_return>` l.46 | delegate's summary returns | DELEGATE RESULT (document anchor) | **B**: "judges the summary against that check ... not by how confident it reads, and revalidates every cited file:line" |
| RULES_DELEGATION `<delegate_packet>` l.39 | alternatives exist for a delegate | option list | **B**: "side by side in one prompt, not as a follow-up" |
| RULES_DELEGATION `<workflow_delegation>` l.54 | Workflow resume-from-cache | cached prior result | gate: "must be re-validated against the current repo before acting" |
| RULES_INTERACTION `<selection_protocol>` | command step waits on user | OPTION LIST presented to the user | **anti-B**: "mark the recommended option with ★"; "[y/n] for yes/no" — produces the R3 shape measured today |
| RULES_DOCS slug resolution l.29 | file-producing command picks a folder | option list `[f]`/`[s]` | anti-B: "pre-selecting the command default" |
| RULES_DOCS `<workflow_gates>` /sc:intent | start of a feature flow | user's intent text | **B (opt-in)**: "User approves the intent text in their own words" — only if the user runs /sc:intent; no routing from an action request |
| RULES_DOCS `<workflow_gates>` brainstorm → review | spec approved, about to plan | PRIOR PLAN/SPEC (A3) | **B**: "Spec self-review mandatory ... approved specs can still carry reversed decisions" |
| FLAGS --loop | user typed --loop | iteration result | B (flag-gated): "state verifiable success criteria up-front ... self-eval vs criteria" |

**I0 verdict for scope:** no file in core/ makes the model state the purpose behind the request and derive a success criterion from it before acting. R20/`<verification_before_completion>` derive the check from the stated action ("add validation" → "tests for invalid inputs pass"), which is the action lock restated as a test. The only purpose-first gate (/sc:intent) is a separate opt-in command.

## 4. Totals per class

| Class | Sections (rows) | Approx. bytes | Share | Of which always-loaded (FLAGS+PRINCIPLES+RULES, 12,229 B) |
|---|---|---|---|---|
| A | 9 | ~2,000 | 4% | ~1,400 |
| B | 11 (3 caveated: flag-gated, partial, opt-in) | ~5,000 | 10% | ~1,200 (Intent Propagation + "state the concrete check" + --loop) |
| C | 44 | ~24,500 | 48% | ~5,900 |
| D | 38 | ~18,600 | 37% | ~3,800 (+ README 2,338 never delivered) |
| **Total** | 102 | ~50,100 (measured 50,764) | | |

Always-loaded chain breakdown: C ~5.9KB (mostly FLAGS routing + on_demand_modules map), D ~3.8KB, A ~1.4KB, B ~1.2KB. Roughly 42% of every session's core payload is A or D.

RULES_QUALITY.md alone carries ~10.3KB of D (examples table ~2.9KB, checklist_scaling, thresholds, verification_ladder, anti_over_engineering detail, duplicated pointers) against ~1.7KB of C and ~0.9KB of B.

## 5. Top 10 findings (ranked)

1. **I0 gap — no purpose-inference step anywhere in the always-loaded chain.** The only "criterion before acting" rule (`<verification_before_completion>`: "state the concrete check that will prove \"done\"", detailed in R20) derives the check from the action verb, so it formalizes the action lock instead of breaking it. A B-class step would have to make the model write *why the user wants this* and *what outcome proves the purpose met* — and look beyond the named file — before executing. Nothing in scope does this.
2. **R13 Intent Verification exempts the I0 case by design.** "Skip for: single-file edits, explicit file paths, continuation of confirmed plan" — the fixture ("draft a reply in thread.md") hits two of three skip conditions. If any rule is to become the purpose gate, this skip-list must be inverted for action instructions that name a file.
3. **RULES_INTERACTION `<selection_protocol>` prescribes the R3 failure.** "mark the recommended option with ★" and "[y/n] for yes/no" produce starred defaults and bare yes/no answers — exactly what today's measurement showed. Replace with: no default marker; yes/no questions answered as a conditional recommendation first, verdict last. RULES_DOCS slug resolution ("pre-selecting the command default") has the same shape.
4. **RULES_QUALITY.md ~10.3KB of D on every implement/test/review/debug turn.** Deletion candidates: `<core_rules>` `<examples>` table (~2.9KB), `<checklist_scaling>` (~0.8KB), `<thresholds>` (~0.8KB, pure pointers), `<verification_ladder>` (~1.2KB, A-candidate), `<anti_over_engineering>` examples + `<model_tendencies>` (~1.4KB), duplicated R06/R15/R18/R20 pointers.
5. **`<scope_discipline>` l.17 reinforces frame lock (R1/R2).** "the deliverable is the assessment: report findings and stop" tells the model to answer within the user's problem definition. Needs a premise-check clause (state the problem as understood *and* the one-layer-out alternative) or it works against the restructure principle.
6. **The real B content is all in RULES_DELEGATION `<delegate_packet>` + `<delegate_return>` (~2.6KB) and it is on-demand.** These are genuine isolation/ordering mechanisms for A4/A3/A2 — but they cover only the delegation path. Kernel `Intent Propagation` (always loaded) carries the A4 part; the A3 "write the check before dispatch, never a predicted verdict" rule has no kernel echo and no non-delegation analogue (the main loop never writes its own check before reading a document or a prior plan).
7. **A2 and A1 have exhortations only.** "Code reality > documentation" (PRINCIPLES directive), "falsify before confirm" (R03), "Evidence > assumptions" — none changes order or information flow. Candidate mechanism: before accepting a README/docstring/prompt-embedded number as a premise, record it as *claim* with a verifying command, in the same shape R21 uses for failures.
8. **A3 re-plan trigger exists only for hard failures.** R21 fires on "tool error, test red, missing target"; FLAGS l.7 re-reads MODE text after compaction. Neither covers "evidence contradicts the current plan" or "re-enter a plan after compaction: re-validate before continuing". Gap.
9. **PRINCIPLES.md is ~80% A/D (≈1.7KB of 2.2KB) and always loaded.** `<philosophy>` slogans, the examples table, `<thinking_strategy>`, `<decisions>` — all duplicates of RULES/RULES_QUALITY or generic practice. Only the Diagnosis pointer and the Assumption-Surfacing thresholds carry anything, and both exist elsewhere.
10. **Caveated B rows:** `--loop` is inert without the flag; the /sc:intent gate is opt-in; `<verification_before_completion>` "state the concrete check" is action-derived. Count as B only once a trigger fires on an ordinary action instruction.

Smaller deletions: FLAGS l.38 note, `<priority_rules>` Safety/Override, RULES `<priority_system>` legend + conflict chain, RULES_DOCS `Examples`, RULES_DELEGATION `<examples>`, core/README.md roadmap/evals sentence (repo-only, never delivered).

## 6. Not read

`~/.claude/`, repo `.claude/`, `docs/` (except writing this file), `CHANGELOG.md`, root `README.md`, `ARCHITECTURE.md`, `scripts/context_loader.py` (delivery facts came from file headers + core/README.md), `modes/`, `commands/`, `agents/`, `skills/`. No web search, tests, or `claude` runs.
