# Product Requirements — superclaude

> Working artifact, not user-facing product documentation (see `docs/README.md`).
> The product's own reference material is the shipped content under
> `src/superclaude/`; this file records what the project is *for* and what it
> deliberately is not, so scope arguments have somewhere to land.

## Goal

`superclaude` turns a team's Claude Code working agreements into installable
markdown — commands, agents, modes, core rules, hooks — so the same behavior
applies in every repository and every session, with no runtime to operate.

Claude Code reads the installed files at session start; that is the entire
delivery mechanism. There is no engine, daemon, or proxy in the loop.

## Target Users

- **Primary — a developer running Claude Code across several repos.** Installs
  once at `--scope user` (`~/.claude/`) and gets one behavioral baseline
  everywhere. Already knows Claude Code's native concepts (slash commands,
  sub-agents, skills, hooks, MCP); the framework ships content in exactly those
  shapes rather than teaching a new abstraction.
- **Secondary — a team sharing that baseline.** `--scope project` commits
  `.claude/` content and the hook registration (`settings.json`,
  `hooks/hooks.json`) to the repo — every hook command is
  `superclaude hook <name>`, so the files are identical on every checkout;
  `--scope local` gives one teammate a
  personal install inside a shared repo, gitignored, on `settings.local.json` +
  `CLAUDE.local.md`. Conventions assume multiple people and multiple repos —
  doc filenames carry a username for exactly this reason.
- **Tertiary — a contributor authoring framework content here.** Writes against
  `.claude/rules/*-authoring.md` and is held by the structural tests
  (`tests/unit/test_{agent,command,skill,mode}_structure.py`).

## Core Features

The load-bearing set. Anything not on this list is support for something on it.

1. **Scope-explicit lifecycle** — `install` / `update` / `uninstall` across
   `user | project | local`, idempotent, with `--dry-run`, `--list-all`, and an
   interactive wizard. Settings are *merged* by marker, never replaced.
2. **Always-loaded kernel + on-demand injection** — `CLAUDE_SC.md` imports the
   RULES/FLAGS/PRINCIPLES kernel; `scripts/context_loader.py` injects modes,
   MCP docs, and rule modules per prompt under a token budget, in three
   disclosure tiers.
3. **Gated `/sc:*` workflow chain** — brainstorm → design → review → plan →
   implement → test → reflect, where each gate demands committed output or real
   test evidence. The gates, not the prose, are what stop step-skipping.
4. **Domain agents and behavioral modes** — delegation targets and cognitive
   overlays, delivered through Claude Code's own agent/mode surfaces.
5. **Mechanically enforced safety** — three `PreToolUse` guards
   (`file_size_guard`, `destructive_guard`, `loop_guard`). These are the only
   guarantees in the framework; see
   `docs/adr/0001-hooks-are-the-enforcement-boundary.md`.
6. **Curated MCP registration** — `superclaude mcp` writes server entries at the
   chosen scope for a small managed set. Nothing is auto-enabled, and Serena's
   own CLI stays the user's responsibility.
7. **Session memory and insight capture** — `/sc:load` / `/sc:save`, plus
   hook-written `.claude/insights.jsonl` at SessionStart / PreCompact / Stop /
   SessionEnd, so what a session learned survives it.

## MVP Exclusions (Out of Scope)

- **No runtime engine, daemon, or proxy.** If a feature needs a process running
  next to Claude Code, it is out of scope by construction.
- **No model calls in the install path.** `install` / `update` / `uninstall` /
  `mcp` / `doctor` never invoke a model. The opt-in `superclaude auto-improve`
  and the `evals/` harness do, by shelling out to `claude -p`.
- **No upstream tracking.** The project began as a fork of
  SuperClaude_Framework and has diverged (different MCP set, skills system,
  insight pipeline, install scopes, workflow gates). Upstream changes are not
  merged back in.
- **No duplicated user prose docs.** The inherited `docs/user-guide/` tree was
  archived 2026-05-15 because it contradicted the live SSOT; content docs live
  next to the content in `src/superclaude/`.
- **No GitHub issue tracker.** The fork has issues disabled; work items are
  markdown under `.scratch/<feature>/` (`docs/agents/issue-tracker.md`).
- **No UI beyond terminal text.** See `docs/UI-GUIDE.md` for the one surface
  that does exist.

## Success Metrics

- **`uv run pytest` exits 0.** CI runs the suite on Python 3.10/3.11/3.12 for
  every push and PR to `master` and `integration`. A red test is a regression,
  never a known issue.
- **Install is reversible and non-destructive.** Re-install without `--force`
  skips; `uninstall` preserves user hooks, MCP servers, and CLAUDE.md content
  because removal is marker-scoped. Pinned by `test_cli_install.py`,
  `test_install_settings.py`, `test_verify_drift.py`.
- **Source and installed copy agree.** `superclaude verify-drift` reports no
  drift after a sync; `superclaude doctor` passes every check.
- **Behavioral claims are measured, not asserted.** `evals/run_eval.py` runs a
  4-arm × 7-task matrix; hard gates are safety invariants whose failure exits
  `2` regardless of soft-metric averages, and the gate set is pinned by
  `tests/unit/test_eval_harness.py`.
- **Docs do not drift silently.** Derived counts are pinned to the source tree
  by tests (`test_codex_component_map.py`, `test_version_consistency.py`),
  never to another doc copy.

## Non-Goals

- Not a replacement for Claude Code features — the framework supplies content
  to native surfaces and stops there.
- Not a general-purpose agent framework, model router, or prompt library.
- Not affiliated with or endorsed by Anthropic, nor by the upstream authors.
- Not a documentation site: `docs/` is working artifacts for development.
- Not single-user tooling — no convention may assume one person, one repo.

## Open Questions

- **`tests/unit/scripts/` is excluded from the default run** (`--ignore` in
  `pyproject.toml` addopts) after a native crash (exit `0xC0000409`) during
  collection. Root-cause and re-enable, or delete the suite? — owner:
  maintainer; decide before the next change to hook scripts.
- **`rich>=13.0.0` is a declared runtime dependency with no import anywhere in
  the tree.** CLI output is plain `click.echo`. Adopt it (and rewrite
  `docs/UI-GUIDE.md`) or drop the dependency? — owner: maintainer.
- **`/sc:init` task (g) writes project memory to `.claude/memory/`, which
  nothing loads.** The store actually read is the per-project auto-memory under
  `~/.claude/projects/<slug>/memory/`. Align the command spec to the live path,
  or make `.claude/memory/` real? — owner: maintainer.
- **ADR backlog.** Other load-bearing decisions — durability routing for
  derived values, scope-explicit installs, the fork divergence itself — are
  recorded only as prose spread across `RULES_DOCS.md` and `README.md`. Promote
  them to ADRs, or accept prose as the record? — owner: maintainer.
