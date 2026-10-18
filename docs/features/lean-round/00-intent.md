---
status: approved-for-plan
revised: 2026-10-18
---

# Intent: verified lean changes without losing purpose inference

Author: ajitta. Decisions were accepted in chat on 2026-10-18.

## Problem

Original request:

> lean 라운드 Phase 0 시작, Q1–Q8 에 대해 결정사항을 대화로 결정하자

The prior audit left implementation simplifications, correctness fixes, content consolidation candidates, and public-component deletion proposals unapplied. A candidate list is not permission to delete: existing keep decisions, loading paths, and authorization boundaries still apply.

The owner's ultimate purpose, recorded in [the prior intent](../reframing-anchoring/00-intent.md), remains:

> 이게 나의 궁극적이며 최종적인 목적이다 '의도를 어떻게 인공지능이 인식하게 만드냐'

Lean work serves that purpose by removing verified waste, not by assuming every instruction describes something the model already knows.

## Proposed outcome

- Seed Phase 0 records and preserve all eight decisions before changing implementation or installed content.
- Execute B0–B4 with their specified checks, targeting patch 4.28.1 after B6 verification.
- Keep B5 public-content changes separate; record evidence before revisiting deferred deletions.
- Report actual diff size, regression-test results, and measured behavior; do not substitute estimated savings or static tests for behavioral evidence.

## Affected users and systems

- Python CLI, hooks, evaluation harness, and tests in this fork.
- Installed commands, agents, modes, and core rules affected by later approved batches.
- Maintainers relying on documentation links, version checks, installation paths, and the existing keep decisions.

## Constraints and decisions

The user's response to every recommendation was “권고대로.”

| Question | Accepted decision |
|---|---|
| Q1: headless session cap | 40 new sessions: 4 canary-gate + 12 I0 spot-check + 10 existing-canary + 14 spare. Sonnet and Opus only; no headless Fable. |
| Q2: scope and release order | B0–B4 first, target patch 4.28.1 after verification. B5 changes require separate commits and a separate release. Merge, push, and actual release remain separate actions on instruction. |
| Q3: delete `commands/sc.md` | Defer. Establish routing non-use before reconsidering; retain the dispatcher and its version/catalog dependencies. |
| Q4: `agents/git-workflow.md` | Consolidate PR table and gotchas into `commands/git.md`, retain the agent. Approved B5 work, not an addition to B4. |
| Q5: delete orchestration/task-management modes | Defer. B4 may remove the identified orchestration duplicate section, not the mode files themselves. Do not infer redundant behavior without measurement. |
| Q6: MCP-body reduction and research-config deletion | Evidence first, this round limited to evidence collection. Check manual-loading references and backing-file requirements; do not delete or shrink on assumption. |
| Q7: agent text, finding policy, init pair | Shorten common paragraphs only, retaining leaf safety semantics and Ask-First checks; no hoisting. Keep finding-policy copies until delivery through `delegate_packet` is proven. Compare user invocation versus native delegation authorization before deciding the init pair. Paragraph shortening remains separate B5 work. |
| Q8: branch | Create `fix/lean-round-2` from `master` `30a08be3`. Created during Phase 0. |

Additional constraints:

- Preserve prior keep decisions, scope rules, manual-loading paths, and native subagent safety delivery.
- Recheck deletion candidates across source, tests, fixtures, and string references on the current base.
- Leave existing `.gitignore`, `.ignore`, and unrelated `.hermes/` work untouched.
- Decisions are taken in chat, never through a long-answer form.
- Phase 0 records are uncommitted. No code change, content installation, new headless model session, merge, push, or release is part of this Phase 0 completion.

## Open questions

Q1–Q8 are settled. Evidence questions remain, not permission to delete:

- Are the manual MCP/research loading routes still used or required?
- Does `delegate_packet` actually deliver the finding-policy text to native subagents?
- How do `/sc:init` and project-initializer differ in authorization, flags, and handoffs?
- What behavioral effects will the later content consolidation checks show?

The next execution batch is B0, the content-preserving document split. Working plan: `.hermes/plans/2026-10-18_001500-lean-round.md` (v3).
