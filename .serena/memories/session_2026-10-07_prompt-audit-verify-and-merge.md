# Session 2026-10-07 — prompt-audit branch verified, refined, merged

Continuation of the same-day audit sessions (Opus 5.5 prompt-audit over the prompt surface,
interview decisions, patch applied as `da2909d5` on `docs/prompt-audit-2026-10-07`). This session
ran under a `/goal`: verify that commit, refine it, use an independent agent where useful. Everything
below was observed live in this session.

## Tree state at the end
master = `f9b421d2` (merge commit), pushed. CI run 37599499697 on that push: Test 3.10, Test 3.13,
"Lint, plugin and doctor checks" all success. Local: `uv run pytest` 2863 passed / 1 skipped,
`tests/unit/scripts` 149 passed, ruff check + format clean. Local-scope install re-synced right after
the merge (`superclaude doctor --scope local` healthy, `make sync-local` 84 installed / 0 failed; it
did NOT hit the `windows-make-sync-broken` failure this time). Remote branch
`docs/prompt-audit-2026-10-07` left in place, not deleted.

## What verification found
Every factual claim in `da2909d5` matched its source of truth (Makefile `lint` = `ruff check .`
only, format check lives in test.yml; single `superclaude` console script; `auto-improve --project`;
`file_size_guard.py` `SIZE_THRESHOLD = 30_000` with `>=` and limit/pages bypass; index-repo budgets
~3KB/<5KB; `<fallback>` optional per command-authoring; zips and plugin copies byte-identical to the
SKILL.md sources; `run_eval.py` copies the RULES_KERNEL arm verbatim so the header strip is inert;
GitHub `reviewDecision` enum confirmed by GraphQL introspection: CHANGES_REQUESTED | APPROVED |
REVIEW_REQUIRED).

The defect class was **sibling inconsistency**, not wrong facts: the scripted patch removed a concept
only in the files the audit cited. Found by grepping per removed concept across src/, .claude/,
.serena/, evals/ — a green suite catches none of this. An `unknowns:independent-reviewer` agent
(commit-only view, 82 hunks, no narrative from me) produced an overlapping list plus six more.

## Landed
- `5d9ffe6a` leftover sweep, 20 files — numeric confidence thresholds still in RESEARCH_CONFIG
  (`confidence: 0.7`, `execution: confidence≥0.6`, `low_confidence`), MODE_DeepResearch
  ("confidence thresholds" pointer, "Confidence score mandatory"), /sc:agent ("Log confidence score",
  "📊 Confidence: 0.82"); dangling doc-convention-v2 refs in the promote-feature description, the
  commands README row and /sc:cleanup's Q2/Q5 clauses (`docs/features/doc-convention-v2/` does not
  exist); six more generic `<fallback>Ask user when unsure` lines (brainstorm, build, help,
  research, select-tool, spec-panel); git-workflow `fetch` back under Proceed, `add` stays Ask
  First, PENDING → REVIEW_REQUIRED; `/sc:git` `<safe>` scoped by note to the op the user typed;
  MODE_Orchestration's unsourced "per-session lifetime agent cap" replaced by the FLAGS.md fan-out
  process cap min(16, cpu-2); R16 restated as the hook's single 30KB rule (no 5KB/config exemption
  exists); the two remaining "recent Opus models" in xml-prose-format de-pinned; hooks gotcha
  "fallback" → project/local branch; insight gotcha interpreter wording; PRD open question on
  `/sc:init` task (g) closed by the init.md change.
- `4b45f678` — frontend-architect's audit-added forbidden defaults (italic accent words, decorative
  monospace labels, pill-shaped buttons) reverted: no source in the repo.
- `35df2b26` — one credibility scale: RESEARCH_CONFIG's four tiers (1 best), score column dropped;
  deep-researcher's five-point scale (five places) and /sc:research "Credibility score" → tier 1–4.
- `f9b421d2` merge to master. Branch CI was triggered by `gh workflow run test.yml --ref <branch>`
  because test.yml fires only on master push, PRs to master, or workflow_dispatch.

## Decisions by the user (interview after the report)
1. Branch: push, CI, merge to master — done.
2. Local scope re-sync after merge — done.
3. Keep the effort/xhigh de-pin in agent-authoring; drop the unsourced frontend aesthetic additions
   (user answered "(a)"; read as keep (a) only).
4. git-workflow split as refined (fetch Proceed / add Ask First; `/sc:git` safe list kept with note).
5. Credibility: align on the four RESEARCH_CONFIG tiers, remove score numbers.

## Not verified (no repo source) — accepted as de-pinned
agent-authoring effort/xhigh availability wording; xml-prose-format "Current Claude models".

## Lesson
After any scripted content patch, sweep by concept, not by hunk: grep each removed concept
(numeric thresholds, dead doc citations, generic `<fallback>`, renamed enum values) across the
install tree, `.claude/rules/`, `.serena/memories/`, `evals/` before calling it done. Tests and
lint stayed green through 13 leftover files. See `mem:project_overview` for the canonical sources.
