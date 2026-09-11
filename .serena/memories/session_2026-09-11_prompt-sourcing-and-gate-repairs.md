# Session 2026-09-11 — memory reconciliation; /sc:prompt fact sourcing, worktree excludes, the lint gate

Written by a Serena-memory cleanup pass that did no other work. The window `ba7f8d1..1fef6eb`
(2026-09-05 22:00 → 09-11, 16 commits, four working sessions) is reconstructed from the commit
log and bodies — nothing in it was observed live. Only "Tree state" below was run today.

## Tree state, verified today
`uv run pytest` → 2595 passed / 25 skipped / 0 failed. `ruff check src/ tests/` → clean.
`pyproject.toml` version `4.11.0+ajitta`. master clean, nothing unmerged.
These are today's readings, not baselines to defend — see the `stale-number-copies` gotcha.

## Landed since the previous save

### 2026-09-05 evening — the two calls the console-entry review left open
- `fe2cc0b` — unknown hook name and stray argument now exit **1**, not 2. Exit 2 is the code that
  blocks the tool call on PreToolUse and Stop, and a committed project-scope `settings.json` naming
  a hook newer than a teammate's installed package is indistinguishable from a typo: settings travel
  with the repo, the package does not. Exit 2 locked that teammate's whole session; exit 1 degrades
  to one absent hook. Bare `superclaude hook` keeps usage-error 2 (no registration is nameless).
- `f61dd8f` — `info/exclude` resolves through the git **common** dir, so the per-worktree
  `.git/worktrees/<name>/info/exclude` the resolver used to write was never read: install reported
  success while every installed file stayed untracked. `_resolve_git_exclude_file` now follows the
  gitdir's `commondir`; a pointer without one (submodule) keeps the gitdir. Consequences now stated
  in the module docstring and pinned by tests: one block per clone, a sibling at a different scope
  replaces it (last install wins), and a removal from any worktree un-excludes them all.
- `6d77259` 4.10.0+ajitta. `7e7e332` README realigned against the source tree — dead flags removed
  (`--p`, `--fast`, ReflexionMemory, `--c7`'s dropped workflow doc), the install tree no longer
  lists `scripts/` (not copied since the console entry), "gitignored" corrected to the per-clone
  `.git/info/exclude` it actually is.

### 2026-09-09 — /sc:prompt stops recalling facts it could read
One root cause, four commits. `<context_targets>` and `<fact_sourcing>` demanded facts that
`<tools>` declared no way to read, so memory was the only remaining source and a rewrite could ship
fabricated paths and git state wearing an evidence badge.
- `8835e76` — read-only Grep and Bash added to `<tools>`; environment facts get read or `[FILL:]`d,
  no third source; an addition with no source is deleted rather than reported. Also marked the three
  `<model_delta>` rows the CC harness already injects as `--target api` only (target defaults to cc,
  so they had been re-attaching harness text on every default run).
- `0e72787` — the shape captured as gotcha `demand-capability-mismatch` (`.claude/rules/gotchas/authoring.md`):
  a section that demands a class of facts the tool list cannot supply makes confabulation a **spec
  defect**, which is where to fix it.
- `1f8f895` + `63e0cda` — the `claude-api` skill read is gated on need (a release-current fact about
  to enter the rewrite), not on invocation; it had cost ~21K + ~61K tokens per run against a 120-line
  command body. The command globs for the reference — the skill's install root differs by machine and
  scope, so no fixed path.
- `b6a3642` — `<model_delta>` was a silent cache of that reference (all 11 axes restate it) that
  auto-updates on one side only. Now a labelled mirror with an owner; `context_loader` resolves the
  reference at invocation and injects path + the target's line ranges, anchored on
  `## Migrating to Claude <model>` then the first `### Behavioral shifts (prompt-tunable)` beneath it
  (a bare grep for that heading lands on Opus 4.7 — it occurs six times and names no model). Three
  states: located; absent (mirror is authoritative, report must say so); anchors-moved, which is free
  drift detection. Implemented as a branch in the already-registered UserPromptSubmit hook — no extra
  process, no `hooks.json` entry, no schema bump, no new module to drift the codex component count.
- `47b30e4` — `[project.urls]` points at this fork; Bug Tracker dropped (issues disabled, they live
  as local markdown under `.scratch/<feature>/`), `Upstream` added to keep the lineage visible.

### 2026-09-10 — the verifiability-switch row
`65ad846` adds the row: opinion framing on a deliverable that needs checkable facts is split into an
explain request (scope, depth, audience) plus a criterion-first judgment request, with
`[FILL: fact write-up / opinion piece]` when the prompt does not settle which. `bcd84ee` then amended
it: the split alone restores dated anchors on Fable (0 → 4) but not on Opus (0 → 0); only an explicit
"name the checkable facts, mark uncertain ones" line does (0 → 6), and rewrites had been adding that
line at their own discretion, so the row now requires it. `8c45658` records the answer-layer
re-verification (years 0 → 26 Opus, 0 → 33 Fable). Evidence lives in
`docs/analysis/game-experience-reasoning-vault-sc-prompt-chosh1179-2026-09-10.md`; cells are n=1 on
one topic. `01d8277` 4.11.0+ajitta.

### 2026-09-11 — the gate nobody was watching
- `16fbf41` — gotcha `stale-number-copies`: a count copied out of its source into an always-loaded
  doc goes stale silently because nothing compares the copy to reality and the gate stays green.
  Names the SSOT for four classes (version, component counts, test pass count, volatile queue state)
  so the fix is always "reference the source", never "update the copy".
- `1fef6eb` — five pre-existing ruff errors cleared. **`uv run pytest` green says nothing about the
  lint gate**: CI runs `ruff check src/ tests/` in both `quick-check.yml` and `test.yml`, and it had
  been red while the suite passed. The same five fired under ruff 0.14.10 and 0.16.5, so none of it
  was upgrade fallout. (`make lint` is `ruff check .` — a wider net than CI's.)

## What this pass changed in `.serena/memories/`
- Added this file.
- `suggested_commands.md`: dropped the `rtk` note (`~/.cargo/bin/rtk` does not exist and `rtk` is not
  on PATH) and the pointer at a CLAUDE.md "Make Commands" section that does not exist.
- `task_completion_checklist.md`: dropped the "markdown-only test exemption" — CLAUDE.md now states
  the opposite (markdown is linted, a docs-only change still needs the suite) — and the "test
  baseline" wording, deleted from the docs 2026-08-30. Added the lint gate.
- `style_and_conventions.md`: the authoring-rules list named a skill rule that went with the skills
  layer and omitted `mcp-authoring.md` / `content-quality.md`.
- `project_overview.md`: the baseline anecdote now points at the `stale-number-copies` gotcha that
  generalised it.
- Resolved open items marked in place on the 07-25 and 08-31 saves (verified against source today).

## Open
- Insight pending queue is non-empty (6 at session start) — `/sc:insight --review` to recount and triage.
- Feature folders untouched this window: `opus5-fable5-alignment` at phase analysis (updated 09-04),
  `hook-performance` and `runtime-behavior-audit` at planning since August.
- Carried from 2026-09-03, still open: the optional third CS-D measurement pair (~$4) to firm up a
  weak gate; `evals/tasks.yaml:17` still sets the global `max_turns: 12` while Fable 5.1 used 13 once
  on plan-routing.
- The verifiability-switch measurements are n=1 per cell on a single topic, non-blind. Treat the
  direction as established and the magnitudes as indicative.

## Later the same day — output styles become an installed component (uncommitted at save time)
- `src/superclaude/output-styles/plain-language.md` ships as a Claude Code output style; `COMPONENTS` gained `output-styles` → `<scope>/output-styles/`. `SHARED_TARGET_COMPONENTS = ("agents", "output-styles")` drives per-file uninstall (`_uninstall_shared_component`) and per-file local-scope exclude, replacing the agents-only special case.
- Style refined from the user's vault draft on external evidence (Wikipedia AISIGNS, Anthropic Fable 5.1/Opus 5 prompting pages, 국립국어원 번역투 paper, negation/density preprints) and A/B-probed on Opus 5 and Fable 5.1: `docs/research/plain-language-output-style-chosh1179-2026-09-11.md`. User rule during the session: the shipped file is global — no Korean text; `tests/unit/test_output_style_structure.py` fails on any non-Latin letter and requires `keep-coding-instructions: true`.
- New: `.claude/rules/output-style-authoring.md`, `okf/superclaude/output-styles/`, README/ARCHITECTURE/component-map rows. Verified: full suite green, lint clean, live local-scope install → uninstall round-trip in a throwaway repo (file lands in `.claude/output-styles/`, excluded via `.git/info/exclude`, removed with the directory once empty, a hand-written style survives).
- Behaviour change on a destructive path, found by independent review: the old agents-only uninstall built its removal set from the source glob including `README.md`, so a user's hand-written `.claude/agents/README.md` was deleted on uninstall; `shipped_md_names` excludes README and a parametrized test pins it for both shared directories. Also: the vault copy `~/ObsidianVault/.claude/output-styles/plain-language.md` was overwritten with the global version (bilingual original recoverable from the vault's git, `d23533f`).
