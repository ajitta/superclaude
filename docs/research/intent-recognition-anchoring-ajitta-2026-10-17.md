---
status: in-progress
revised: 2026-10-17
---

# Intent recognition, anchoring and framing on current models: evidence and measurement

What this records: the evidence behind the `reframing-anchoring` round — the owner's claim that current models execute an action instruction well but do not infer the unstated result it is for — and the measurements this repo made of it. Prior round: `persona-anchoring-framing-audit-chosh1179-2026-09-14.md` (S1–S18, applied P1–P5); those sources are not repeated here. Measurement details: `docs/features/reframing-anchoring/02a-measurement.md`; synthesis and limits: `03-analysis.md`; alternatives and decisions: `05-options.md`.

## 1. New sources (2026), verified against the arXiv abstract text by exact-string search

| # | Source | Level | What it establishes |
|---|---|---|---|
| T1 | "Instructions Are Evidence, Not Objectives: Measuring Outcome Alignment of Agents", arXiv 2610.17757, submitted 13 Oct 2026 | B (abstract; body not read) | 100 SWE-chat trajectories: "56% of initial instructions omit requirements that later emerge as necessary, and 52% of the useful follow-up requirements could have been inferred from the project." Defines **outcome alignment**: "treat the instruction as evidence rather than as the objective, inferring the true requirements from the instruction and the environment." Benchmark TiGanEval; eight frontier models "lose 53 to 67 points of success rate when moving from the full specification to the partial instruction." Quoted limit: "a plan-mode harness cannot compensate for the missing ability of the model itself." |
| T2 | "Implicit Intelligence — Evaluating Agents on What Users Don't Say", arXiv 2602.20424, submitted 23 Feb 2026 | B (abstract) | 16 models, 205 scenarios with "apparent simplicity in user requests, hidden complexity in correct solutions, and discoverability of constraints through environmental exploration"; best model 48.3% scenario pass rate. |
| T3 | "Ask or Assume? Uncertainty-Aware Clarification-Seeking", arXiv 2603.26233 (2026) | C (search snippet) | Clarification-seeking scaffolds for underspecified SE tasks; not read. Relevant to the ask-vs-proceed boundary, not to inference itself. |

Search was bounded to two queries on 2026-10-17; this is not a systematic review. Older prompting advice was not consulted as evidence (standing rule: stale for current models).

## 2. What the sources add to the owner's hypothesis

- **The gap is named and measured elsewhere, on frontier models, in the same shape this repo's fixtures use**: a partial instruction whose missing requirement is discoverable from the environment (T1, T2). T1's "instruction as evidence, not objective" is the owner's "행위 지시 뒤의 궁극 목적" in benchmark terms. This raises the prior that the I0 fixtures measure something real rather than an artifact of two synthetic tasks.
- **A harness-level fix is not expected to close it** (T1: plan mode did not). That is the main caution for this round: a kernel rule is weaker than a plan-mode harness. The pilot therefore tests a narrow claim — does one rule move two fixtures on sonnet/opus — not "the framework can install outcome alignment."
- **Neither source measured Claude Sonnet 5.5 / Opus 5.5 / Fable 5.1 specifically** (model lists not read beyond the abstracts). Transfer to this repo's models is assumed, not shown.

## 3. This repo's measurements (2026-10-17, headless `claude -p`, sonnet and opus, Fable excluded)

From `02a-measurement.md`, 120 retained sessions:

- Action-only customer reply: the two facts in `account.md` (fix date, workaround) appear in 0–1 of 4 sonnet runs and 1 of 2 opus runs per arm; stating the result in the prompt lifts opus to 2/2 on both facts, sonnet to 1/4. Omission is a proxy — the harness does not record whether the file was read.
- Action-only code fix: sonnet names the real cause in 3/4 runs per arm and repairs it in 0/4; opus vanilla repairs it 2/2; opus with the shipped framework stopped to ask 2/2. Cause of the stop not isolated (R12 and the security branch of Assumption-Surfacing are both plausible; hook auto-approval was a confound and has since been removed from the hooks).
- Prompt-embedded estimate anchor and persuasive author rationale: no failure at this fixture difficulty (12/12 each). Not reproduced, not disproved.
- Yes/no framing: the first-line check contradicted the prompt's own "answer yes or no first"; the substantive checks passed in every run. Not evidence of decision bias.
- Shipped framework vs vanilla: no I0 improvement; +75% (sonnet) / +54% (opus) recorded session input.

## 4. Pilot result (2026-10-17, 24 sessions)

`docs/features/reframing-anchoring/06-pilot.md`: with one kernel rule (`purpose_before_action`, +1,056 bytes) and everything else identical, the two action-only I0 tasks went from 0/6 (shipped kernel) to 11/12 (candidate) across sonnet and opus; the candidate changed only files the task or the error named; +12% (sonnet) / +21% (opus) session input from the extra reading. One rule, two synthetic tasks — the harness-level caution from T1 stands for tasks whose purpose is not discoverable in the workspace.

## 5. Open

- Ship decision for `core/RULES.md` and `make canary-gates` (4 sessions) before release; 12 sessions remain of 180.
- T1 body: which eight models; whether any intervention short of training moved the score; TiGanEval task shapes to compare with this repo's fixtures.
- Harder A1/A4 fixtures before claiming either effect is absent on current models.
- Harm on ordinary requests (over-reading, slower one-line edits) under the rule: unmeasured.
