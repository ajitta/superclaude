---
status: complete
revised: 2026-10-02
---

# 04 — Design

## 1. Shape

One skill, `socratic-brainstorm`, instruction-only:

```
portable-skills/socratic-brainstorm/
├── SKILL.md                      # 109 lines: rules, Steps 0-5, pitfalls
├── references/question-bank.md   # six types, tactics, optional lenses (KO/EN)
├── references/brief-template.md  # verdict + brief sections
└── agents/openai.yaml            # Codex: explicit-only, display name
```

The dialogue runs **Frame → Thesis (steelman) → Probe (elenchus) → Diverge (user first) → Converge (by questions) → Verdict + brief**, covering R1-R19 of [03-analysis.md](./03-analysis.md) §2.

Sources, per step:

| Step | Taken from |
|---|---|
| Frame: mode/depth inferred, pick stated with reason | socratic-method Setup turn; obra "say the classification out loud" |
| Thesis: steelman + confirm | socratic-method Phase 1; obra write-back |
| Probe: six types, tactics, switch on no movement | socratic-method; Socrates mutation guard; `/sc:brainstorm` analysis-loop |
| Necessity check | requirements-analyst R18 |
| Diverge: user first, model ≤3 labeled options, edges | MODE_Brainstorming; socratic-mentor; mhylle lenses |
| Converge: criteria questions; decisions confirmed/delegated | MODE_Brainstorming; `/sc:brainstorm` decision_modes |
| Verdict: sharpened / open / refuted | socratic-method |
| Never implement | `/sc:brainstorm` error-path; obra HARD-GATE |

## 2. Decisions

**D1 — Where the skill lives.** (a) top-level `portable-skills/`, outside the installed package ★; (b) `src/superclaude/skills/`, installed by `superclaude install`.
Chose (a). Commit `910eabd` removed the skills layer from the package for good reasons, and `install_paths.LEGACY_SKILL_NAMES` prunes skill dirs on install. The goal here is portability *beyond* Claude Code, and the install CLI only targets `~/.claude`. Re-adding a package skills layer would reopen that decision for no gain. `.gitignore` already ignores `skills/` and `.agents/` (Tavily install artifacts, `0d834f7`), which also rules out those names.

**D2 — Manual vs auto invocation.** (a) explicit-only by wording + Codex `allow_implicit_invocation: false` ★; (b) `disable-model-invocation: true`.
Chose (a). (b) makes the claude.ai upload fail (02 §3), which removes the mobile path, the main requirement.

**D3 — Elenchus only vs elenchus + diverge.** (a) both, model ideas after the user's and labeled ★; (b) questions only (socratic-method).
Chose (a). The user asked for *brainstorming*; a questions-only skill ends without options. The no-advice rule still holds until Step 3, and the user can skip Step 3.

**D4 — Output.** (a) brief in the message; file only on request when a filesystem exists ★; (b) always write a file.
Chose (a). Mobile chat has no repo, and a file write in a shared repo can leak personal reasoning (socratic-method privacy check).

**D5 — Structured brief schema + validator CLI.** Rejected for v1: it needs Python on the client (02 §3), and a fixed section order in the template carries most of the value.

## 3. Rejected

- Using `AskUserQuestion` chips: Claude Code only, and chips anchor elenchus answers. Numbered text options instead.
- Spawning research subagents mid-dialogue: no user turn inside a subagent; no tools in chat.
- Ending with a model `## Recommendation` (upstream skill): contradicts the user-as-author stance. A pick is given only on explicit request (Step 4.3).

## 4. Deferred

- **ChatGPT mobile chat (non-Codex)**: needs a published plugin in the OpenAI plugin directory (02 §3). Trigger: the user wants it in plain ChatGPT, not Codex.
- **Marketplace distribution** (ajitta/claude-plugins catalog, Codex `.agents/plugins/marketplace.json`): wait until v1 has been used for real; the zip + copy paths cover all surfaces now.
