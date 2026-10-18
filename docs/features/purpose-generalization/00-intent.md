---
feature: purpose-generalization
phase: intent
status: approved
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — purpose-inference generalization (axis A)

## Original request

After the v4.29.3 review round closed with a numbered remaining-work list (item 4: the next-round axis from [test-exclusion-lift/02-handoff.md](../test-exclusion-lift/02-handoff.md), recommendation **A**, cap **90**):

> 남은 작업 중에 너의 추천이 있는 것들 진행

Plan v1 → independent review (APPROVE WITH CHANGES, P-1–P-16) → plan v2 with Q1–Q14, each with a recommended option, put to the owner in chat:

> 추천대로

## Question

Does the shipped `purpose_before_action` rule (`src/superclaude/core/RULES.md`, 4.29.0) generalize beyond the two fixtures it was piloted on ([reframing-anchoring/06-pilot.md](../reframing-anchoring/06-pilot.md)), and does it cause over-inference on plain requests?

## Decisions (all recommended options)

| Q | Decision |
|---|---|
| Q1 | Comparison arm **sc-ablate**: the shipped kernel minus `<purpose_before_action>` (via the `sc-candidate` mechanism), vs sc-full |
| Q2 | sonnet + opus, 3 runs per cell |
| Q3 | Build 5 purpose fixtures, keep 4 |
| Q4 | If all 5 pass the screen, drop P4 |
| Q5 | Twin controls K1 (clean) and K2 on both arms and both models |
| Q6 | Screen failure → replace with the fifth; two failures → k=3; three or more → stop |
| Q7 | Curtailed screen sampling |
| Q8 | Reachability: from the reserve after infra reruns, 1 `-stated` sc-full run per model on each fixture where that model's sc-full ≤ 1/3 |
| Q9 | `max_turns: 20` |
| Q10 | Branch `feature/purpose-generalization`, docs here |
| Q11 | After readout keep only the Phase-2 tasks as probes; delete the rest; reset `RULES_CANDIDATE.md` |
| Q12 | P3 with a vendored read-only logrotate mirror (tests the say-so branch; residual ambiguity stated) |
| Q13 | Host positive control: `action-vs-purpose-code` on sc-full ×1 per model |
| Q14 | Phase 2 starts automatically the same day when the screen lands on a pre-registered branch |

Session cap **90**. Runs root: `/home/ubuntu/.hermes/profiles/superclaude/cache/scratch/sc-evals/` (this VM's scratch dir, outside `~/.claude`). Plan: `.hermes/plans/2026-10-19_axis-a-plan-v2.md` (v1 and the review alongside; local to this machine).

## Constraints

No edit to shipped content during the round; no LLM judge; Fable not run (headless Fable bills usage credits); no release unless a rule changes (it does not this round).
