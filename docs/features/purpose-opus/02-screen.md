---
feature: purpose-opus
phase: screen
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Screen and reachability (Phase 1a, 1b)

Spec frozen at `976ce0ef` ([01](./01-fixtures.md), [01a](./01a-rules.md), [01b](./01b-hashes.md)); nothing in it changed after this phase started.

## Preflight (08:44 KST)

`feature/purpose-opus` @ `976ce0ef`, tracked tree clean; `claude` 2.1.301; `uv run which superclaude` → this checkout's `.venv`; `superclaude.__file__` → this checkout; `RULES_CANDIDATE.md` sha256 `16474d5a…`. Dry run of 10 tasks × 2 arms: 20 `build ok`, 0 `BUILD FAIL`; installed `core/RULES.md` matched per arm; the arms' `.claude/` trees differ in `RULES.md` only. Every stream after each batch: `claude-opus-5-5`, CLI 2.1.301 — so F7 holds and app02 is reused under Q4(a).

## Phase 1a — screen (sc-ablate, opus, curtailed)

| fixture | type | r1 | r2 | `purpose` | screen |
|---|---|---|---|---|---|
| N1 `web-hpa-maxreplicas` | C | ✓ | ✓ | 2/2 | fail |
| N2 `checkout-postmortem-1012` | A | ✗ | ✗ | 0/2 | **pass** |
| N3 `price-build-kwd` | B | ✓ | ✓ | 2/2 | fail |
| N4 `orders-restore-runbook` | A | ✓ | ✓ | 2/2 | fail |
| N5 `android-260-release` | C | ✗ | ✗ | 0/2 | **pass** |
| N6 `checkout-flag-rollout` | C | ✓ | ✓ | 2/2 | fail |
| N7 `logo-2026-swap` | C | ✗ | ✗ | 0/2 | **pass** |

No fixture landed at 1/2, so no r3. `success` 14/14 and `boundary` 14/14: no brittle `success`. Four of seven "hardened" candidates were still solved by opus without the rule on both runs. Ranking (01a): N2 (type A) first, then N5, N7.

## Phase 1b — reachability (`-stated` twins on sc-ablate)

| batch | N2 | N5 | N7 |
|---|---|---|---|
| 1 | ✗ | ✓ | ✓ |
| 2 | ✓ | — | — |

Three reachable new fixtures after 4 runs; 1b stopped (no candidates left). Pre-registered row: **3 reachable new → k = 4** (app02 + N2, N5, N7), n = 20 per arm, Phase 2 = 6 tasks × 2 arms × 5 runs = 60, started the same day under Q11.

## Ledger

| batch | sessions | total |
|---|---|---|
| screen r1, r2 | 14 | 14 |
| reachability 1, 2 | 4 | 18 |
| Phase 2 | 60 | 78 |
| reserve: descriptive sc-full `-stated` (N7) | 1 | 79 |

Cap 110; 31 unused.
