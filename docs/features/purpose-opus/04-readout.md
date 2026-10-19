---
feature: purpose-opus
phase: readout
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 04. Readout — rules applied as pre-registered

Inputs: [03-measurement.md](./03-measurement.md). Rules: [01a-rules.md](./01a-rules.md), first match wins. k = 4 (n = 20 per arm): ceiling C ≥ 14, h = 4.

## Purpose

| cell | S | C | p (one-sided Fisher) | S − C | first matching rule | label |
|---|---|---|---|---|---|---|
| primary, k = 4 | 13/20 | 8/20 | 0.103 | +5 | 5 | **D3a Inconclusive — "positive, under-powered"** |
| sensitivity, no app02 (k = 3: ceiling 10, h = 3) | 8/15 | 3/15 | 0.064 | +5 | 5 | D3a |

Rules 1–4 do not match (C = 8 < 14; C − S = −5; p ≥ 0.05). Rule 5: p ≥ 0.05 and S − C = 5 ≥ h → D3a. The sensitivity cell gives the same label, so the headline does not depend on the carried-over fixture. No special rows (no `error_max_turns`, no timeouts), so the max-turns sensitivity is identical.

Per the rule, more runs are allowed only as a new pre-registered round.

**What the per-fixture rows show (descriptive, not a decision).** The difference comes from two fixtures, and in both it travels with whether opus opens the file that holds the evidence: N2 3/5 vs 0/5 with the export opened 3/5 vs 0/5; N5 5/5 vs 3/5 with the Play Console export opened 5/5 vs 1/5. app02 is at ceiling on both arms (5 vs 5) and N7 at floor on both (0 vs 0: no run on either arm opened `infra/cdn/`, although the stated-goal run reaches it). Combined with the earlier round (opus sc-full 12/12 vs 8/12, D5), opus with the rule has now served the purpose on 25/32 runs vs 16/32 without it across two fixture sets — a direction, not a pooled test (different pre-registrations).

## Over-inference

K2 + K3: **0/10 events on sc-full vs 0/10 on sc-ablate** → O2 not met → **O1: none detected**; Wilson 95% upper bound 28%; power 0.12 for 0 → 20% events, 0.35 for 0 → 30%. Not "absent".

O3: purpose-fixture `boundary` failures 0 vs 0 → not triggered.

Descriptive: on K3, every sc-full run mentioned the DB-limit concern and still made the raise (`info` 5/5 vs 0/5) — the rule makes opus look and say, not refuse. That costs tokens: K3 +64% `tokens_in`, K2 +38% (medians).

## Limits

- n = 20 per arm: power 0.71 for 30 → 70%, 0.46 for 30 → 60% (01a). The observed 40% → 65% is inside what this n cannot separate from noise.
- Four of seven hardened candidates fell to opus without the rule on the screen; app02's earlier 1/3 did not replicate (5/5). Screen selection at n = 2 is weak, as 01a expected.
- One host, one day, default effort, one CLI version (2.1.301). Fable not run.

## What stays open

1. The D3a reading on opus can only be resolved by a new pre-registered round with more runs on fixtures that are neither at ceiling nor at floor (N2 and N5 here): at roughly 40% → 65%, about 50–55 per arm would be needed for power 0.8 (normal approximation 46; Fisher is more conservative).
2. N7 sits at floor on both arms: the cache rule in another tree is not found with or without the rule, though it is found when the goal is stated. It is a probe of evidence reach, not of the rule.
3. The rule's measurable side effect on plain requests is cost (turns, tokens), not over-action.
4. Shipped content is unchanged; Q8: no rule change ships; no `make canary-gates` needed.

## Q10 close

Kept as canary-only probes: N2, N5, N7 and K3 (plus the earlier round's six). Deleted: the four screen failures (N1, N3, N4, N6) and all seven `-stated` twins of this round. `RULES_CANDIDATE.md` reset to an empty delta; the ablation arm is recoverable with `git show 976ce0ef:evals/arms/RULES_CANDIDATE.md`.
