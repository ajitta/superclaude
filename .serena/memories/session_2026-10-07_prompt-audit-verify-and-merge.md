# Session 2026-10-07 — prompt-audit branch verified, refined, merged, released as 4.21.0

Continuation of the same-day audit sessions (Opus 5.5 prompt-audit over the prompt surface,
interview decisions, patch applied as `da2909d5` on `docs/prompt-audit-2026-10-07`). This session
ran under a `/goal`: verify that commit, refine it, use an independent agent where useful. Then the
user asked for a version bump and release. Everything below was observed live in this session.

## Tree state at the end
master = `4f8f420a` (merge of `chore/version-4.21.0`), pushed; `stable` → `4f8f420a`; GitHub release
`v4.21.0` (notes = CHANGELOG 4.21.0 section, three headings). Tests workflow on that SHA: 3.10, 3.13,
"Lint, plugin and doctor checks" all success (run 37600963280). Local: `uv run pytest` 2863 passed /
1 skipped, `tests/unit/scripts` 149 passed, ruff check + format clean, `superclaude --version` 4.21.0.
Local-scope install was re-synced after the audit merge (`make sync-local`, 84 installed; it did NOT
hit `windows-make-sync-broken` this time) but NOT after the version bump — the installed `/sc:sc`
meta still says 4.20.1 until the next sync. Remote branches `docs/prompt-audit-2026-10-07` and
`chore/version-4.21.0` left in place.

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
- `eff25031` — this record plus two earlier session records (2026-10-05 plugin-install plan,
  2026-10-07 ci-trim) that had never reached git: a Beads `bd init` block in this clone's
  `.git/info/exclude` (`**/SESSION*.md`) matched `session_*.md` under `core.ignorecase=true`, so
  `git status` hid them. A root-`.gitignore` negation was added, then reverted in `00dc848a` once the
  user said Beads is no longer used; the bd-init block (`.beads/`, `**/RECOVERY*.md`,
  `**/SESSION*.md`) was deleted from the local exclude file instead. `tests/unit/test_install_git_exclude.py`
  uses `.beads/` only as a foreign-line fixture.
- `decf6d27` → `4f8f420a` — version bump: package 4.20.1 → 4.21.0 (pyproject, `__init__`, README
  badge + heading, `/sc:sc` meta, CHANGELOG entry); portable skills socratic-brainstorm 3.2.0 → 3.2.1,
  socratic-elenchus 1.2.0 → 1.2.1 (SKILL.md metadata.version, plugin-manifests/*.json, docs feature
  README; `package.py` regenerated plugins/ and releases/*.zip). `make release` then created the
  GitHub release and moved `stable`.

## Decisions by the user (interview after the report)
1. Branch: push, CI, merge to master — done.
2. Local scope re-sync after merge — done.
3. Keep the effort/xhigh de-pin in agent-authoring; drop the unsourced frontend aesthetic additions
   (user answered "(a)"; read as keep (a) only).
4. git-workflow split as refined (fetch Proceed / add Ask First; `/sc:git` safe list kept with note).
5. Credibility: align on the four RESEARCH_CONFIG tiers, remove score numbers.
6. Beads is no longer used in this repo (user statement; bd-init leftovers removed).
7. Bump version and release: minor bump 4.21.0 (content behavior changed framework-wide), patch
   bumps for the two portable skills (wording-only rule change).

## Not verified (no repo source) — accepted as de-pinned
agent-authoring effort/xhigh availability wording; xml-prose-format "Current Claude models".

## Lessons
- After any scripted content patch, sweep by concept, not by hunk: grep each removed concept
  (numeric thresholds, dead doc citations, generic `<fallback>`, renamed enum values) across the
  install tree, `.claude/rules/`, `.serena/memories/`, `evals/` before calling it done. Tests and
  lint stayed green through 13 leftover files.
- A "saved" Serena session record is only saved once `git status` shows it; when a new file under
  `.serena/memories/` does not appear, run `git check-ignore -v <file>` before assuming it is staged.
- Release path that worked: bump branch → `git checkout master && git merge --no-ff …` in one command
  → push → `gh run list --commit <sha> --workflow Tests` green → `make release`. Branch-only CI needs
  `gh workflow run test.yml --ref <branch>`.
See `mem:project_overview` for the canonical sources.
