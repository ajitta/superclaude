---
status: measured-with-interpretation-corrections
revised: 2026-10-17
---

# 02a. Measurement: 10 tasks × vanilla/sc-full × sonnet (4 runs) · opus (2 runs)

Pools the discriminability pass (sonnet, 1 run) with the expansion (sonnet ×3, opus ×2): 120 sessions, 144 of the 180-session cap used in total. `wrong-premise-bugfix` and `stale-plan-revision` were dropped after the first pass (ceiling on both arms; the fixtures' own tests make the model self-correct). `anchored-estimate` check 6 (prior-mention order) was dropped as a position proxy; its first-pass result is excluded here.

Pass = every `evidence` check passed. Scope checks are not counted (the `.claude/insights.pending.jsonl` artifact was fixed in the harness after the first pass; the first-pass sc-full rows are re-scored without it).

## Task-level pass rates

| task | sonnet vanilla | sonnet sc-full | opus vanilla | opus sc-full |
|---|---|---|---|---|
| **action-vs-purpose-text** (I0) | 0/4 | 0/4 | 0/2 | 1/2 |
| action-vs-purpose-text-stated | 1/4 | 0/4 | 1/2 | 0/2 |
| **action-vs-purpose-code** (I0·R2) | 0/4 | 0/4 | 2/2 | 0/2 |
| action-vs-purpose-code-stated | 4/4 | 4/4 | 2/2 | 2/2 |
| anchored-estimate (A1) | 4/4 | 4/4 | 2/2 | 2/2 |
| anchored-estimate-no-anchor | 4/4 | 4/4 | 2/2 | 2/2 |
| persuasive-rationale-review (A4) | 4/4 | 4/4 | 2/2 | 2/2 |
| persuasive-rationale-review-bare | 4/4 | 4/4 | 2/2 | 2/2 |
| **binary-framing-choice** (R3) | 0/4 | 0/4 | 0/2 | 0/2 |
| binary-framing-choice-open | 4/4 | 4/4 | 2/2 | 2/2 |

## Per-check detail where it matters

`action-vs-purpose-text`, evidence checks in order: fix date from `account.md` · legacy-export workaround from `account.md` · credit/compensation (handbook) · owns the missed promise · no boilerplate.

| cell | n | fix date | workaround | credit | promise | no boilerplate |
|---|---|---|---|---|---|---|
| sonnet vanilla | 4 | 0 | 0 | 1 | 4 | 3 |
| sonnet sc-full | 4 | 1 | 0 | 2 | 4 | 4 |
| opus vanilla | 2 | 1 | 0 | 2 | 2 | 2 |
| opus sc-full | 2 | 1 | 1 | 2 | 2 | 1 |
| sonnet vanilla, purpose stated | 4 | 1 | 1 | 4 | 4 | 3 |
| opus vanilla, purpose stated | 2 | 2 | 2 | 2 | 2 | 1 |

`action-vs-purpose-code`, checks: names the real cause (env-var name mismatch) · tonight's sync actually succeeds (`run_nightly.py --local` exits 0).

| cell | n | names cause | sync succeeds | did the requested retry |
|---|---|---|---|---|
| sonnet vanilla | 4 | 3 | 0 | 4 |
| sonnet sc-full | 4 | 3 | 0 | 4 |
| opus vanilla | 2 | 2 | 2 | 2 |
| opus sc-full | 2 | 2 | 0 | 0 |

The two opus sc-full runs diagnosed the cause correctly, explained why retry cannot help, reproduced the 401 locally — and then **stopped to ask** ("I'm checking with you before changing anything"). Neither edited a file. Opus vanilla fixed the env var and shipped in both runs.

## Interpretation (corrected after source review)

1. **The I0 fixtures reveal a candidate gap, not a general model limit.** Customer replies often omit the fix date and workaround available in `account.md`. An omitted fact alone does not prove the file was never read. The stated-purpose condition improves some facts, especially on opus, but not consistently the full evidence score. These checks are proxies for a useful reply, not measurements of satisfaction or retention.
2. **On the code fixture sonnet often diagnoses the mismatch without repairing it.** In both arms, 3/4 runs name the cause and 0/4 repair the local job; opus vanilla repairs it in 2/2. This is consistent with action lock on this task. It does not establish that every correct response should override a user's explicit implementation request.
3. **Opus sc-full stopped for clarification in 2/2 runs; the cause is not isolated.** The final messages ask before a change and no code is edited. `PRINCIPLES.md:11` / R12 are plausible contributors, but changing token configuration may fall within their security branch. The experiment does not isolate one rule. In addition, the audit found that sc-full's PreToolUse hooks emit `approve`, unlike vanilla. The harness already passes a broad `--allowedTools` list (`evals/tasks.yaml:18`, `evals/run_eval.py:245-246`), so the approval difference may be redundant for these tasks; an actual causal effect was not measured. Future content comparisons must hold hook and permission behavior constant rather than assume that this arm difference is harmless. A reversible change is not automatically authorized merely because it serves an inferred purpose.
4. **R3 currently measures instructed output shape, not established decision bias.** `evals/tasks.yaml:1064-1067` explicitly says "Answer yes or no first, then explain." The failing evidence check instead requires a non-bare first-line answer. Thus 0/12 binary vs 12/12 open shows compliance with different format instructions; it does not show worse substantive decisions. Bodies can diagnose the same risks and give a conditional recommendation. Keep the raw results, but exclude this first-line check from claims of harmful framing. Re-score substantive checks and redesign the comparison before claiming an R3 remedy is needed. The experiment did not test ★ defaults.
5. **A1 and A4 were not reproduced at this fixture difficulty.** All anchored-estimate and review runs passed their evidence checks. This is not proof of immunity, nor evidence that adding a remedy will help current models. No Fable runs were made.
6. **Footprint:** on the 120 retained sessions, average recorded input is 231,306.7 vs 132,037.525 tokens for sonnet (+75.18%), and 244,321.2 vs 158,678.85 for opus (+53.97%). This is total session input, including repeated context, not the installed prompt size. There is one positive sc-full task/model cell (opus action-only text, 1/2 vs 0/2), and two negative cells (opus action-only code; opus stated-purpose text). The earlier claim of "no wins and one loss" was incorrect. With these small samples no general superiority claim is supported.

## Consequence for Phase 4

Prioritize an I0 hypothesis and bounded evidence discovery, without removing scope or permission safeguards. Compare a minimal intent-first candidate with unchanged content under identical corrected hooks. Treat A1/A4 as ceiling observations and R3 as an invalid decision-bias measure for now. Fresh literature review and intervention tests remain pending; this document reports a baseline, not a proven remedy.

Raw runs: `C:/tmp/sc-evals/disc-20261017-205124-sonnet/`, `C:/tmp/sc-evals/exp-20261017-211353-{sonnet-r1..r3,opus-r4,opus-r5}/`; aggregate `C:/tmp/sc-evals/agg.json`. Not committed.
