---
status: complete
revised: 2026-10-02
---

# 03 — Analysis: what the skill must take, and from where

> **Historical (one-skill era).** This analysis produced v1, which mislabeled modern Socratic questioning as the Socratic method ([09](./09-elenchus-redesign.md) §1). It still describes what `socratic-brainstorm` 3.0.0 does. The strict method is in [09](./09-elenchus-redesign.md). The current state is in [README](./README.md).

## 1. Method synthesis

Two classical moves, both Socratic, map onto brainstorming's two halves:

| Move | Classical name | Brainstorm half | Model's role |
|---|---|---|---|
| Test the idea by questioning until assumptions and contradictions show | elenchus | converge / stress | examiner — questions only |
| Draw ideas out of the person who holds them | maieutics ("midwifery") | diverge / develop | midwife — the user generates first, the model adds labeled options after |

Published skills each pick one half (§02-2). The SuperClaude assets already encode the bridge: `MODE_Brainstorming` (diverge → converge, build → judge, never prescribe), `socratic-mentor` (the user states the idea, the model names it afterwards), `/sc:brainstorm` (approval gate, confirmed vs delegated decisions). The skill composes them into one dialogue:

```
0 Frame  → 1 Thesis (steelman, confirm) → 2 Probe (elenchus) → 3 Diverge (user first, then model)
         → 4 Converge (questions over options) → 5 Verdict + brief
```

## 2. Requirement list (each traced to a source)

| # | Requirement | Source |
|---|---|---|
| R1 | One question per message; adaptive to the last answer | obra; socratic-method; MODE_Brainstorming "ask q's > give answers" |
| R2 | Restate the idea (steelman) and get confirmation before the first probe | socratic-method Phase 1; obra write-back |
| R3 | Six-type question taxonomy; switch type when two probes don't move the thesis | socratic-method; Socrates mutation guard; `brainstorm.md` analysis-loop gotcha |
| R4 | Contradiction surfacing by quoting both answers verbatim; never invent quotes | socratic-method |
| R5 | No solutions before the diverge step; if asked "what would you do?", answer with a question once, offer to jump ahead | socratic-method guardrail; MODE_Brainstorming `<never>` |
| R6 | Diverge: user generates first; model options are added after and labeled "mine"; build-then-judge | MODE_Brainstorming thinking; socratic-mentor name-after-discovery |
| R7 | Converge by questions (criteria → trade-off), not by recommending | MODE_Brainstorming; upstream's `## Recommendation` is the anti-pattern |
| R8 | Honest verdict: sharpened / aporia / refuted (only from the user's own words) | socratic-method |
| R9 | Decisions tagged confirmed vs delegated | `/sc:brainstorm` decision_modes |
| R10 | Necessity gate on every requirement that lands in the brief | requirements-analyst R18 |
| R11 | Stop signals honored instantly (incl. "그만", "됐어", "정리해줘"); continue requests honored too | socratic-method; gupsammy saturation |
| R12 | Never implement inside the skill; handoff is the user's call | `/sc:brainstorm` error-path example; obra HARD-GATE |
| R13 | Optional lenses (premortem, expert lens questions) instead of running every framework | mhylle framework selection; panel `socratic` modes |
| R14 | Parking lot for tangents | mhylle |
| R15 | Mobile-sized turns: ≤ ~6 lines; choices numbered so a digit is a valid reply; no tables mid-dialogue | §02-3 consequences 3-4 |
| R16 | Works without any tool; files only when a filesystem exists and the user wants one | §02-3 consequence 4 |
| R17 | Reply in the user's language | user base is Korean-first; all surfaces |
| R18 | Spec-only frontmatter; name = folder; description ≤1024 chars with triggers front-loaded | §02-3 consequence 1 |
| R19 | Explicit-invocation bias: description says when **not** to fire; Codex `allow_implicit_invocation: false` | socratic-method manual-only; `/sc:brainstorm` description |

## 3. What is deliberately left out

- Multi-agent / subagent research during the dialogue (`/sc:brainstorm` step 2, mhylle phase 3): subagents can't talk to the user, need tools not present in chat, and break the turn rhythm on a phone.
- `/sc:review` hard gate and `docs/features/` writing: framework-specific. The brief's `next step` line can *suggest* them when the session runs inside a SuperClaude repo.
- A machine-validated brief schema (socratic-method's `idea-brief-v1` + CLI validator): adds a Python dependency that mobile chat can't run. The brief keeps a fixed section order instead.
- `AskUserQuestion` chips: Claude Code only, and chips anchor answers during elenchus (socratic-method). Numbered text options are used where choices help.

## 4. Size budget

socratic-method is 420 lines and still needed a reference file. Phone sessions and Codex's skill-list budget (~2% of context) argue for a short core: target SKILL.md ≤ 200 lines, with the question bank and brief template in `references/` (progressive disclosure is supported by Claude Code, claude.ai with code execution, and Codex).
