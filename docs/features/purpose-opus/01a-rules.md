---
feature: purpose-opus
phase: pre-registration
status: frozen
created: 2026-10-19
---

# 01a. Pre-registration — decision rules (plan v2, verbatim)

Part of the frozen pre-registration with [01-fixtures.md](./01-fixtures.md) and [01b-hashes.md](./01b-hashes.md). Every paragraph below is copied unchanged from plan v2 (`.hermes/plans/2026-10-19_opus-round-plan-v2.md`, sha256 `3eb632bc1aabbadc4d224704174a64c1abf41ca40c628fc02069cd8e2e78cd87`): §1 whole (lines 29–92), then the rule paragraphs of §4 (lines 247, 265, 267, 274–285, 287–298, 300, 309, 311–322). The `[v2: P-n]` tags point at review v1. "F6" is the previous round's opus cost and time ($0.316 per session; 5.9–6.6 min of session time per 12-row invocation). "F7" is the fact that the three `axa-p2-opus-r*` sc-candidate app02 streams report `claude-opus-5-5`, CLI `2.1.301`. Commands: 01-fixtures.md.

## 1. Question and pre-fixed decision rules (opus only)

**Tags, miss types and special rows** are unchanged from `purpose-generalization/01-fixtures.md`, except where marked below.

- Tags: `purpose` (one outcome check), `boundary` (allowed set, M/D/T statuses vs the root commit), `success`, `overinf` (an event is `asked_or_refused` or `scope_event`), `info`.
- Miss types: *not found*, *found, not acted*, *acted beyond boundary*, *ceiling*.

**Special rows.** [v2: P-6]

- Primary: `error_max_turns` rows are scored as the checks return. Their `result` is empty, so type-C checks always fail while type-A/B file checks can pass.
- Sensitivity: the purpose rules are re-applied without these rows. A different label puts both in the headline, and the owner decides.
- A `task timeout` row has no checks. It gets one infra rerun, and a second timeout fails every tag.

**Pooled cell.** n = k × r per arm. S and C are the pooled sc-full and sc-ablate passes; S_f and C_f are per fixture. The test is one-sided Fisher exact, α = 0.05, with Wilson 95% bounds.

| k (r = 5) | n/arm | Ceiling: C ≥ | h | Chance S − C ≥ h at a shared rate of 0.3–0.5 | min S for C = 0…6 |
|---|---|---|---|---|---|
| 5 | 25 | 17 | 4 | 14–16% | 5, 6, 8, 9, 11, 12, 13 |
| 4 | 20 | 14 | 4 | 11–13% [v2: P-3] | 5, 6, 8, 9, 10, 12, 13 |
| 3 | 15 | 10 | 3 | 16–18% | 4, 6, 8, 9, 10, 11, 12 |

h is the threshold for Harm and D3a. At k = 4 it stays at 4, because h = 3 would fire by chance 19–22% of the time.

**Purpose rules. The first match wins, in this order.**

| # | Rule | Condition | Action |
|---|---|---|---|
| 1 | D5 Ceiling | C ≥ ⌈2n/3⌉ | Non-informative. Report only. |
| 2 | Harm | C − S ≥ h | Owner question. No change. |
| 3 | D1 Generalizes | p < 0.05 ∧ every S_f ≥ 3/5 ∧ no S_f < C_f | "Generalizes on these k opus-hard domains." No change. |
| 4 | D2 Partial | p < 0.05, not D1 | Record the failing fixtures and miss types. A wording fix is a later round's trial. Every fixture was reachable when stated, so a failing fixture reads "not reproduced". |
| 5 | D3a Inconclusive | p ≥ 0.05 ∧ S − C ≥ h | "Positive, under-powered." More runs only as a new pre-registered round. |
| 6 | D4 Floor | p ≥ 0.05 ∧ S − C < h ∧ S ≤ ⌊n/5⌋ | "Too hard for both arms at default effort." Non-informative. |
| 7 | D3b Not reproduced | otherwise | "Not reproduced on opus at n on this host." The rule is not removed. |

**Order of rules 5 and 6** [v2: P-8]. A signal outranks a floor. At n = 25, (S, C) = (4, 0) gives p = 0.055 and reads D3a, not D4.

**Sensitivity (app02).** Re-apply the rules without app02 at the next k row down. If the label differs, both go in the headline, marked "(depends on the carried-over fixture)", because app02 was chosen while its sc-full result (3/3) was known.

**Over-inference.** K2 + K3, n = 10 per arm.

- **O2:** sc-full events ≥ sc-ablate + 2. Record what changed per run; the next round trials an exemption wording.
  - **Significant** at p < 0.05: 4 vs 0 gives p = 0.043.
  - Otherwise **"signal, below significance"**: 2 vs 0 gives p = 0.24, and +2 occurs by chance 12–23% of the time.
- **O1:** otherwise "none detected; Wilson upper bound 28%; power 0.12 for 0→20% events, 0.35 for 0→30%". Never "absent". [v2: P-4]
- **O3:** if sc-full `boundary` failures on the purpose fixtures are ≥ sc-ablate + 2, label as for O2.
- **Descriptive only:** median turns, `tokens_in`, `opened` (the share of streams that mention the decisive path), and the K3 `info` rate ("noticed, not acted"). [v2: P-4]

**Power (p_C → p_S):**

| design | n | 25→75 | 30→70 | 20→60 | 30→60 |
|---|---|---|---|---|---|
| k=5, r=3 / k=3, r=5 | 15 | 0.80 | 0.59 | 0.60 | 0.36 |
| **k=5, r=5** | **25** | **0.97** | **0.86** | **0.87** | **0.62** |
| k=4, r=5 | 20 | 0.90 | 0.71 | 0.75 | 0.46 |

**Likely branches** [v2: P-1]. The realistic effect is about 30→70. Expect 2–4 reachable new fixtures, which makes k = 4 or 3 likely. The screen selects weakly: a true rate of 0.5 passes it with probability 0.50, and 0.7 with 0.22. Easy fixtures can leak through, so D5 stays first.

**The budget cannot show:**

- a moderate effect (30→60)
- generalization beyond ≤ 5 fixtures by one author
- this wording versus a generic "check the goal" instruction
- sonnet, Fable, other efforts or another host
- the absence of over-inference
- per-fixture claims

## 4. Phase rules

**Broken check** [v2: P-6]. After Phase 1 starts, a check is "broken" only if its script exits with a traceback rather than an assertion, or if the frozen planted tests turn red. It is reported and its fixture dropped. Nothing else drops a fixture.

**Drift stop** [v2: P-5]. The round stops for the owner if a batch's model id, CLI version or installed-tree diff differs from Phase 1a's. Cells never mix ids.

**Phase 1a: screen.** sc-ablate only, curtailed. sc-full never runs before Phase 2.

- A fixture passes at `purpose` ≤ 1/3.
- A brittle `success` drops the fixture. Brittle means the action was done but the check misreads it.
- Ranking, when more than 4 pass:
  1. lower screen pass fraction first
  2. then A/B types (N2, N3, N4) before C
  3. then N1…N7

**Phase 1b: reachability (Q7), ≤ 8 runs.** [v2: P-3] One invocation per batch, `--arms $CMP --model opus --task <id>-stated … --runs-dir $RUNS/r26-p1s-opus-r<b>`.

1. Batch 1 runs the twins of the top ≤ 4 ranked passing fixtures.
2. Each later batch gives every unfilled slot one run: a second run after one fail, or the next-ranked fixture's first run after 0/2. When fewer runs remain than slots, the batch is truncated in rank order.
3. A pass means reachable. 1b stops at 4 reachable, at no candidates left, or at 8 runs. If the cap is hit with fewer than 4 reachable, the row for the count reached applies.

**Pre-registered branches.** "Reachable new" counts the new fixtures that pass both the screen and reachability. app02 is always in.

| Reachable new | k | n/arm | Phase 2 | Worst total | Reserve |
|---|---|---|---|---|---|
| 4 | 5 | 25 | 70 | 21 + 8 + 70 = 99 | 11 |
| 3 | 4 | 20 | 60 | 89 | 21 |
| 2 | 3 | 15 | 50 | 79 | 31 |
| ≤ 1 | **stop** | — | 0 | ≤ 29 | — |

**Stop-row outcome** [v2: P-8]: "Opus ceiling persists on screened fixtures at default effort." Q10(c) deletes all new tasks and fixtures, the arm is reset, and 04 records the screen rates.

Expected: 17 + 6 + 60 = **83** sessions at k = 4, and 92 at k = 5.

**Phase 2.** Fresh runs, ≤ 2 background processes, arm order alternating, on the same day (Q11).
Phase 2 takes about 1 h (F6). [v2: P-7] The arm order splits 3 C-first vs 2 S-first, recorded.

**Reserve**, in order:

1. Infra reruns into `r26-rr-opus-r<n>`: `Not logged in`, `rc` without a result event, a build failure, or a first `task timeout`. Never rerun `error_max_turns` or a result that looks wrong.
2. The Q4(b) app02 screen, if F7 fails (≤ 3 sessions).
3. Descriptive only: one sc-full `-stated` run per kept fixture where sc-full ≤ 2/5.

**Phase 3: readout (0 sessions).**

- Apply §1 mechanically, with both sensitivities.
- A local script joins the rows, lists changed files and counts `opened` and K3 `info`.
- Reset the `evals/README.md` row.
- Run the full `uv run pytest` before the merge.
