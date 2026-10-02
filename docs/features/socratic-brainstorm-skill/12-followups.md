---
status: complete
revised: 2026-10-03
---

# 12 — Follow-ups

Closes the open items listed after [11](./11-plugin-upload.md).

## 1. Historical banners

`02`, `03`, `04` and `08` were written when this was one skill. Each now opens with a one-line banner: which parts still hold, and where the current state lives.

## 2. Probes that were thin

**Codex multi-turn after the split** (`gpt-6.1-sol`, sandbox bypassed because bwrap fails on this VM, 09 §7):

- `$socratic-brainstorm`, retro, 6 turns:
  - One ask per turn.
  - "너라면 어떻게 할 거야?" got one guiding question plus an offer to jump ahead.
  - On "아이디어 단계로 넘어가자" it asked for the user's options first.
  - It built on each of the user's three options.
  - It ended **open**, with every option attributed to the user, and one next step.
  - It did not add model options, because the user ended before Step 3.3.
- `$socratic-elenchus`, retro, 5 turns:
  - Asked "무엇을 위한 시간이야?".
  - Built the contradiction from the user's own "아무것도 안 바뀌면 의미 없지".
  - Asked "어떻게 고쳐 말할까?" without proposing a definition.
  - Named the shift, then tested the revision from the too-broad side.
  - Ended **stopped before testing** with the full record template.

**Ambiguous routing** (Claude Sonnet 5.5, both skills installed, 3 runs per prompt):

| Prompt | brainstorm | elenchus |
|---|---|---|
| 소크라테스식으로 해줘: 점심 앱 | 3 | 0 |
| 소크라테스처럼 질문해줘: 코딩 교실 | 1 | 2 |
| socratic method on my idea: lunch app | 1 | 2 |
| 내 아이디어를 질문으로 검증해줘: 카페 창업 | 3 | 0 |

Generic "Socratic" wording is a coin flip between the two. Tuning the descriptions for a phrase that carries both meanings would only move the coin. Instead, both skills now handle a misroute: if the request only says "Socratic" in general, the first message names the style in one line and points to the other skill, then continues (3.1.0 / 1.1.0).

Re-run (n = 6):

- The two ambiguous prompts, 2 runs each, all loaded elenchus. All 4 runs carried the pointer line ("…선택지와 실행 계획까지 필요하면 `socratic-brainstorm`을 요청하세요" / "If you'd rather have questioning that ends in options and a plan, ask for `socratic-brainstorm`").
- Explicit prompts still routed correctly (B1 → brainstorm, E1 → elenchus).
- E1 ("소크라테스 대화법으로 따져줘") also showed the pointer line, although "대화법" names the dialogue. That is harmless over-firing of one line.

## 3. Distribution

- **Self-hosted marketplace** in this repo: `.claude-plugin/marketplace.json` named `ajitta-socratic`, with relative sources into `portable-skills/`. `claude plugin validate .` passes. Install with `/plugin marketplace add ajitta/superclaude`, then `/plugin install socratic-elenchus@ajitta-socratic`.
- **Catalog**: ajitta/claude-plugins lists both through `git-subdir` sources pointing at this repo.
- A test pins the marketplace entries to the skill folders and their `plugin.json` names. A rename that leaves a stale entry would install nothing, yet `validate` would still pass (claude-plugin-distribution skill, "Drift guard").
- **Codex marketplace: not added.** The OpenAI portable plugin layout wants skills under `skills/<name>/` with a root `plugin.json` (developers.openai.com/plugins/build/plugins, "Create a plugin manually"). That conflicts with the single-skill-at-root layout claude.ai and Claude Code use here. Codex users copy the folder into `.agents/skills/` (unchanged). Revisit if Codex distribution is wanted.

## 4. Branch cleanup

Merged remote branches deleted: `feature/socratic-brainstorm-skill`, `feature/socratic-elenchus`, `feature/two-socratic-skills`, `fix/plugin-upload-manifest`.

## 5. Independent review

See §6 (filled after the run).
