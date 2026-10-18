---
feature: purpose-opus
phase: intent
status: approved
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — `purpose_before_action` on opus, with fixtures opus misses without it

## Original request

After the purpose-generalization readout (sonnet D3a, opus D5 ceiling, over-inference none detected) and its next-step list:

> 소넷은 포기하고 오퍼스에 집중. 너의 추천대로 진행

Plan v1 → independent review (APPROVE WITH CHANGES, P-1–P-8) → plan v2 with Q1–Q13, each with a recommended option, put to the owner in chat:

> 추천대로

## Question

On opus only: does the shipped `purpose_before_action` rule (`src/superclaude/core/RULES.md`) raise the purpose-served rate on unstated-purpose fixtures that opus misses without it, and does it raise over-inference on plain requests? Comparison sc-full vs sc-ablate (the `sc-candidate` arm restored from `82cbf3bb`), default effort.

## Decisions (all recommended options)

| Q | Decision |
|---|---|
| Q1 | Session cap **110** |
| Q2 | 5 runs per cell |
| Q3 | 7 hardened candidates (N1–N7); keep ≤ 4 + `app02-disk-alert` |
| Q4 | Reuse `app02-disk-alert`; its earlier opus sc-ablate runs count as screen evidence only if the preflight shows the same model id and CLI, otherwise a fresh curtailed screen |
| Q5 | Controls K2 `backup-disk-alert` (reused) + new K3 `api-hpa-maxreplicas` |
| Q6 | Screen failures follow the pre-registered table; no rework |
| Q7 | Reachability: `-stated` twins on sc-ablate, ≤ 2 per fixture, ≤ 8 runs |
| Q8 | No rule change ships this round |
| Q9 | Branch `feature/purpose-opus`, docs here |
| Q10 | After the readout keep the Phase-2 new tasks + K3 as canary-only probes; delete screen failures and `-stated` twins; reset the arm |
| Q11 | Phase 2 starts the same day automatically on a listed row, unless the drift stop fires |
| Q12 | Default effort |
| Q13 | New tasks `max_turns: 30`, `timeout: 900` |

Plan: `.hermes/plans/2026-10-19_opus-round-plan-v2.md` (v1 and the review alongside; local to this machine). Runs root `/home/ubuntu/.hermes/profiles/superclaude/cache/scratch/sc-evals/`.

## Constraints

No sonnet, no Fable; no edit to shipped content; no LLM judge; mechanical checks only; no release unless a rule changes (Q8: none).
