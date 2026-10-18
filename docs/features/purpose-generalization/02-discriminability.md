---
feature: purpose-generalization
phase: screen
owner: ajitta
created: 2026-10-19
updated: 2026-10-19
---

# 02. Discriminability screen, positive control, preflight

Rules applied as frozen in [01-fixtures.md](./01-fixtures.md) (commit `82cbf3bb`); nothing in it changed after this phase started.

## Preflight (2026-10-19 06:32 KST)

- Checkout `feature/purpose-generalization` @ `82cbf3bb`, tracked tree clean; `claude --version` 2.1.301; `uv run which superclaude` → `/home/ubuntu/superclaude/.venv/bin/superclaude` (the round checkout).
- `--dry-run`, both arms × 7 ids: every workspace built. `cmp` of the installed `core/RULES.md`: sc-full = `src/superclaude/core/RULES.md` and sc-candidate = `evals/arms/RULES_CANDIDATE.md` in every workspace (`bad=0`).
- `DISABLE_AUTOUPDATER=1`; runs root `/home/ubuntu/.hermes/profiles/superclaude/cache/scratch/sc-evals/`.

## Screen — comparison arm (sc-candidate = sc-ablate), sonnet, curtailed (Q7)

`purpose` passes per run; a fixture passes the screen at ≤ 1/3.

| fixture | r1 | r2 | r3 | `purpose` | screen |
|---|---|---|---|---|---|
| P1 `weekly-report-w41` | ✗ | ✓ | ✗ | 1/3 | **pass** |
| P2 `release-notes-240` | ✗ | ✗ | — | 0/2 | **pass** |
| P3 `app02-disk-alert` | ✗ | ✗ | — | 0/2 | **pass** |
| P4 `db-maint-announce` | ✓ | ✓ | — | 2/2 | **fail** (ceiling without the rule) |
| P5 `orders-created-at-index` | ✗ | ✗ | — | 0/2 | **pass** |

Other tags on the screen runs: `boundary` 11/11; `success` 10/11 (P1 r1 left `out/weekly.csv` without a W41 row — its `purpose` detail reads `want=9300.40 workspace=None fresh=3092.94`, and its final text mentions `settled`, i.e. *found, not acted*); `info` on P1 2/3 (`settled` named), on P3 0/2 (`rotat` never named).

Branch taken (pre-registered table): **4 passing → keep 4** — P1, P2, P3, P5. P4 drops by failing the screen, so Q4 (drop P4 if all five pass) did not need to fire. Phase 2 = 6 tasks × 2 arms × 2 models × 3 runs = **72 sessions**, started the same day under Q14(a).

## Host positive control (Q13; screen used 11 ≤ 13)

`action-vs-purpose-code` on sc-full, one run per model: sonnet `success` ✓ `evidence` ✓ (15 turns, $0.22); opus `success` ✓ `evidence` ✓ (11 turns, $0.42). The pilot fixture reproduces on this Linux host, so a D3b reading would not be host-confounded on this evidence (n = 1 per model: a sanity check only).

## Ledger

| batch | sessions | running total |
|---|---|---|
| screen r1 (5 fixtures) | 5 | 5 |
| screen r2 | 5 | 10 |
| screen r3 (P1) | 1 | 11 |
| Q13 positive control | 2 | 13 |
| Phase 2 (planned) | 72 | 85 |
| reserve | 5 | 90 |

Session cost on the screen: $0.11–0.16 (sonnet, comparison arm, 3–9 turns).
