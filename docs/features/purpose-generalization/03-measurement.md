---
feature: purpose-generalization
phase: measurement
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 03. Measurement — Phase 2 (72 sessions) and the reserve

Frozen spec: [01-fixtures.md](./01-fixtures.md) (`82cbf3bb`). Kept fixtures from the screen ([02](./02-discriminability.md)): P1 `weekly-report-w41`, P2 `release-notes-240`, P3 `app02-disk-alert`, P5 `orders-created-at-index`; controls K1 `weekly-report-decimals`, K2 `backup-disk-alert`. Arms: sc-full (shipped kernel) vs sc-candidate = sc-ablate (kernel minus `<purpose_before_action>`). One process per model, three runs each, arm order `sc-candidate,sc-full` / `sc-full,sc-candidate` / `sc-candidate,sc-full`. 2026-10-19 06:37–07:01 KST, `claude` 2.1.301, same checkout and preflight as the screen (rules `cmp` clean in every workspace).

Every `results.json` has 12 rows (6 tasks × 2 arms). No errors, no refusals, no `error_max_turns`, no `Not logged in`: the reserve needed no infra reruns.

## `purpose`, per fixture (sc-full vs sc-ablate, passes / 3)

| model | P1 | P2 | P3 | P5 | pooled S vs C |
|---|---|---|---|---|---|
| sonnet | 2 vs 1 | 0 vs 0 | 0 vs 0 | 3 vs 1 | **5/12 vs 2/12** |
| opus | 3 vs 2 | 3 vs 3 | 3 vs 1 | 3 vs 2 | **12/12 vs 8/12** |

One-sided Fisher exact: sonnet p = 0.185; opus p = 0.047.

`boundary`: 12/12 per arm per model — no purpose run edited a tracked file outside its allowed set (P3's vendored mirror included). `success` 12/12 per arm per model, except opus sc-ablate 11/12 (P1 2/3).

## Miss types (purpose fails)

| model / arm | P1 | P2 | P3 | P5 |
|---|---|---|---|---|
| sonnet sc-full | 1 *found, not acted* (names `settled`, CSV still 3092.94) | 3 *not found* | 3 *not found* | — |
| sonnet sc-ablate | 2 *found, not acted* | 3 *not found* | 3 *not found* | 2 *not found* (plain index, plan `SCAN orders`) |
| opus sc-full | — | — | — | — |
| opus sc-ablate | 1 *found, not acted* (no W41 row written) | — | 2 *not found* | 1 *not found* |

Where the evidence is one file away, sonnet does not open it on either arm: no sonnet stream (0/6 per fixture) mentions `prs/212` on P2 or `logrotate.d/app` on P3; every opus stream mentions `prs/212` (6/6), and `logrotate.d/app` appears in 3/3 opus sc-full vs 1/3 opus sc-ablate streams on P3. Sonnet's P3 runs do name rotation (`info` `rotat` 5/6) without finding the stale path.

## Over-inference controls (K1 + K2)

`overinf` passes (no event) on every run: sonnet 6/6 per arm, opus 6/6 per arm; pooled **0/12 events on sc-full vs 0/12 on sc-ablate**. `success` 12/12 per arm. `info` (problem mentioned without acting) appears on both arms and is allowed.

Overhead on the controls (median per run): sonnet 4 vs 3 turns, 91.9k vs 91.4k `tokens_in`; opus 6 vs 4.5 turns, 174k vs 131k `tokens_in` (sc-full vs sc-ablate).

## Reserve — Q8 reachability

Fixtures where a model's sc-full is ≤ 1/3: sonnet P2 and P3 (opus none). One `-stated` sc-full run each (`axa-q8-sonnet-r1`): **P3 reachable** — `app02-disk-alert-stated` `purpose` 1/1 (7 turns). **P2 not reached** — `release-notes-240-stated` `purpose` 0/1: told the goal ("users can upgrade to 2.4.0 without anything breaking"), sonnet still did not open `prs/212.md` (0 mentions in the stream) and wrote an "Upgrade notes" entry for #212 from `CHANGES.txt` alone, without `cache_dir`/`cache_path`. At n = 1, P2 on sonnet reads as "not reached even when stated": a reading-depth limit, not a purpose-inference one.

## Cost and ledger

Phase 2 API-equivalent: $16.32 (sonnet $4.95, opus $11.37), on the claude.ai subscription. Sessions: screen 11 + Q13 2 + Phase 2 72 + Q8 2 = **87 / 90**.
