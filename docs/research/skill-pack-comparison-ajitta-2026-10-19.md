---
status: complete
revised: 2026-10-19
---

# superclaude next to three skill packs: Matt Pocock, Addy Osmani, pstack

What this settles: how superclaude differs from three widely used Claude Code skill packs, measured from their trees, and which of their practices superclaude took over (§4). Behavior was not compared across packs: no pack ran against another on the same tasks.

## 1. What was compared

Shallow clones of the default branch on 2026-10-19:

| Pack | Repo @ commit | Version | Shape |
|---|---|---|---|
| superclaude | ajitta/superclaude @ ed0dd74b | 4.30.5 | 35 commands, 24 agents, 6 modes, 2 skills, 14 hook registrations; installed by the `superclaude` CLI |
| Matt Pocock | mattpocock/skills @ 49dd158 | 1.3.1 | 27 plugin skills: 16 user-invoked orchestrators (`disable-model-invocation`), 11 model-invoked disciplines; no hooks, no agents, no evals |
| Addy Osmani | addyosmani/agent-skills @ aeac41d | 0.6.13 | 25 skills (all model-invoked), 9 commands, 4 reviewer personas, 7 checklists; hook scripts not wired into the plugin; three-tier evals |
| pstack (Lauren Tan) | cursor/plugins @ d457567, `harness/pstack/claude-code` | 0.15.28 | 56 skills (24 `principle-*`), 55 of them user-invoked only; one entry point `poteto-mode` with 23 playbooks; 2 agents; Cursor names mapped by an adapter doc |

## 2. Context cost

Description characters that enter the skill listing (description + `when_to_use`, entries without `disable-model-invocation`), from the trees:

- superclaude: 8,871 (35 commands + `sc-prompt`); agent descriptions 7,757 more; always-loaded core (`CLAUDE_SC.md` → FLAGS, PRINCIPLES, RULES) 13,264.
- Matt Pocock: 2,156. Addy Osmani: 9,680 (+754 agents). pstack: 275 (+524 agents); its cost lands on invoke (`poteto-mode` body 20,550 chars, plus the adapter, principle leaves and a playbook).

The listing budget was measured, not assumed. Claude Code 2.1.303 with `--debug-file` in a project-scope install on this VM logged `Skill listing over budget: 111 skills, 47748 chars > 30000 budget` for both `claude-haiku-5-5` and `claude-sonnet-5-5`, with the user's plugins loaded. With `--setting-sources project` (superclaude's 37 entries plus the bundled skills) no over-budget line was logged. The 8,000-character figure for a 200K window used in an earlier draft of this comparison does not hold for these models: superclaude alone fits, and an overflow comes from everything installed together. The README note under "All Commands" states this, and `test_readme_listing_figure_holds` keeps its figure true.

## 3. Verification each pack ships

- superclaude: hooks that block (destructive commands, reads ≥30 KB, repeated failures); the `evals/` harness with arms, canary probes and hard gates; statistics-backed rule changes.
- Addy Osmani: structural lint in CI; a deterministic routing tier (stemmed TF-IDF over descriptions: positive prompts must rank their skill, no two descriptions above 0.75 cosine); behavioral evals through headless `claude`, including pressure cases (time, sunk cost, authority).
- pstack: asks for proof inside its skills (`benchmark-checklist`, verification skills); no evals of the pack itself upstream.
- Matt Pocock: none.

## 4. Taken over, and what was not

1. **Description overlap check** (from agent-skills' routing tier). `tests/unit/test_description_overlap.py` compares every pair inside the skill listing and inside the agent list, fails at 0.70. It compares routing text only: the on-request tier sentence is identical in every on-request command, and the "Not for" gate names siblings on purpose. With the gate kept, /sc:agent and /sc:pm score 0.75; stripped, 0.21. Highest pairs on 4.30.5: /sc:load–/sc:save 0.55, quality-engineer–verifier 0.24. Mutation check: a /sc:load description rewritten to read like /sc:save scored 0.78 and failed the test. The prompt-ranking half of that tier was not taken: superclaude's routing is measured by the `cmd-*` canary probes against the real model instead.
2. **Pressure probes** (from agent-skills' behavioral tier, graded by mechanical checks instead of a judge). Three `canary_only` tasks in `evals/tasks.yaml`: `pressure-time-verify`, `pressure-authority-dictated-fix`, `pressure-sunk-cost-green`. Smoke on 2026-10-19 (sonnet, low effort, vanilla and sc-full, 2 runs each, $1.28): 11 of 12 runs passed; the one miss was vanilla on the hurry probe (edit, then DONE, no run). Three runs per arm is a smoke check, not a measurement; the probes guard against a regression and say nothing yet about a difference between arms. The first grader accepted only `pytest` and failed two runs that verified by direct `python -c` execution, which RULES.md counts as verification; the grader was widened to match the rule before commit.
3. **Glossary grilling** (Matt Pocock's `grill-with-docs`): not taken. `docs/agents/` already follows his issue-tracker and triage conventions, and `/sc:brainstorm` covers the interview.
4. **Listing cost**: documented in the README (§2) instead of changed. Every command stays model-invocable so delegated runs work (`.claude/rules/command-authoring.md`, Trigger Policy).
