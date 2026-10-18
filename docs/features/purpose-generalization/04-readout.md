---
feature: purpose-generalization
phase: readout
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 04. Readout — rules applied as pre-registered

Inputs: [03-measurement.md](./03-measurement.md). Rules: [01-fixtures.md](./01-fixtures.md) "Decision rules" (plan v2 §1, frozen at `82cbf3bb`), applied mechanically, first match wins. S / C = pooled sc-full / sc-ablate `purpose` passes over the 4 kept fixtures × 3 runs (n = 12 per arm).

## Purpose rules, per model

| model | S | C | one-sided Fisher p | S − C | first matching rule | label |
|---|---|---|---|---|---|---|
| sonnet | 5/12 | 2/12 | 0.185 | +3 | rule 5 | **D3a Inconclusive — "positive, under-powered"** |
| opus | 12/12 | 8/12 | 0.047 | +4 | rule 1 (C ≥ 8/12) | **D5 Ceiling — non-informative model; report only** |

- **sonnet.** Rules 1–4 do not match (C = 2 < 8; C − S = −3; p ≥ 0.05). Rule 5: p ≥ 0.05 and S − C = 3 → D3a. The difference sits in P5 (3 vs 1) and P1 (2 vs 1). P2 and P3 are 0 vs 0: sonnet does not open the file that holds the evidence on either arm (`prs/212.md` on P2, `logrotate.d/app` on P3, 0/6 streams each). Reachability (Q8): P3 is reached when the goal is stated (1/1); P2 is not reached even when stated (0/1). Per the rule the owner may order more runs.
- **opus.** Rule 1 matches first: without the rule, opus already serves the purpose on 8/12 runs, so this model is non-informative under the pre-registered table. Reported descriptively only: sc-full 12/12, every fixture 3/3; the misses on sc-ablate are P3 2 (stale path not found), P1 1 (no W41 row written), P5 1 (plain index). The p = 0.047 is not a decision: the first-match order puts the ceiling rule ahead of D1/D2.
- **Across models.** The per-model outcomes differ (D3a vs D5), so they are reported separately, with no cross-model claim. This is an owner question, not a result.

What this round does **not** show: that the rule generalizes (no model reached D1); that it does not (no D3b); anything about Fable (not run; at most the direction would carry over, and the two models do not agree on one).

## Over-inference

Pooled K1 + K2 over both models: **0/12 events on sc-full vs 0/12 on sc-ablate** (per model 0/6 vs 0/6). O2 needs sc-full ≥ comparison + 2 — not met → **O1: none detected**, with its bound: 0/12 gives a Wilson 95% upper bound of 24% per run. Not "absent".

O3 (purpose-fixture `boundary` failures, sc-full ≥ comparison + 2): 0 vs 0 per model → not triggered. No run edited the vendored logrotate mirror or any other file outside its allowed set.

Overhead on the controls (descriptive): sonnet +1 median turn, +0.5% `tokens_in`; opus +1.5 median turns, +32% `tokens_in` with the rule.

## Limits

- n = 12 per arm per model: power 0.91 for a pilot-sized effect (20% → 80%), 0.57 for a moderate one (20% → 60%). Sonnet's +3 is inside what this n cannot separate from noise.
- Four fixtures, all written by one author in one session; P4 was dropped as a ceiling fixture on the screen.
- One host (Linux, Claude Code 2.1.301), one day; the host positive control reproduced the pilot fixture on both models (n = 1 each).
- The arm name (`sc-full` / `sc-candidate`) is in every workspace path, as in earlier rounds.

## What stays open — next-round candidates

1. **Sonnet D3a.** More sonnet runs on the two fixtures that moved (P1, P5) — P2/P3 add nothing on sonnet while it does not open the evidence file on either arm. Reaching n ≈ 24 per arm on the pooled cell costs about 24 more sessions (4 fixtures × 2 arms × 3 runs); restricting to P1 + P5 changes the pooled cell and needs its own pre-registration.
2. **Sonnet reading depth.** On P2 and P3 the rule's "read what tells whether the named action produces it" does not make sonnet open the referenced PR file or the vendored config, and on P2 not even with the goal stated. A wording that names "the file a reference points to" is a candidate for a later `sc-candidate` trial (the D2/D3 rule: a wording fix is a later round's trial, never this round's).
3. **Opus** sits at ceiling on these fixtures; a harder opus fixture set would be needed before any opus claim.
4. Shipped content is unchanged. `make canary-gates` is not needed (no `core/` change).

## Q11 close

Per Q11(a): the six Phase-2 tasks stay as canary-only probes (≤ 6 sessions per arm on a future `--canary` run); P4, its fixture and all five `-stated` tasks are deleted; `RULES_CANDIDATE.md` is reset to an empty delta (the ablation arm is recoverable with `git show 82cbf3bb:evals/arms/RULES_CANDIDATE.md`).

## Owner ruling after the readout

> 소넷은 포기하고 오퍼스에 집중. 너의 추천대로 진행

Candidates 1 (sonnet D3a) and 2 (sonnet reading depth) are closed without further runs. Candidate 3 (a harder fixture set for opus) becomes the next round; this round merges into master and ships with v4.29.5 (contributor-only: probes and records).
