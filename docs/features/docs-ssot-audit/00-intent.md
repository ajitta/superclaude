---
feature: docs-ssot-audit
phase: intent
status: approved-for-plan
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — docs ↔ SSOT consistency audit (axis D)

## Original request

Owner-approved brief (`fable-axis-d.md`, 2026-10-19), after axis C (install/upgrade) closed with v4.30.2:

> Find every place where a human- or model-facing document states something that the single source of truth (SSOT) contradicts, and classify it. Model the round on axis C. […] Read-only on everything except the new `docs/features/docs-ssot-audit/` files. No fixes to docs or code in this round. […] Phases 0–3, then stop.

## Question

Which sentences in the docs a reader or an agent is routed to (README, AGENTS/CLAUDE, ARCHITECTURE, `docs/`, `.claude/rules/`, CLI and Makefile help, the shipped content's descriptions of itself, CHANGELOG claims about current behaviour) are false against the SSOT today, and which of those shapes could a test have caught?

## What counts as a defect

- **Wrong claim**: the doc states a behaviour, default, path, flag, command, count or mechanism, and the SSOT does the opposite or does not have it (README's research confidence targets that no shipped file defines; a help text naming `.gitignore` where the code writes `.git/info/exclude`).
- **Dead reference**: a file, test, make target, subcommand, option, hook name, flag or branch that does not exist (`make verify`, `tests/unit/test_skill_structure.py`, the `integration` branch).
- **Stale count / version / path**: a number or location copied into a doc that the tree no longer matches, in a doc that is not a dated record.
- **Two live docs disagreeing**: both are current and routed to, and they state different things (`core/README.md` 0.9k-token kernel with four rule classes vs `ARCHITECTURE.md` 1.5k with five).
- **Wrong SSOT named**: a doc points the reader at a file that is not where the fact lives (`ARCHITECTURE.md` sending `cli/`, `hooks/`, `utils/` to `AGENTS.md`, which does not document them).

## What does not count

- Style, wording preference, tone, length.
- Claims about Claude Code, npm packages, model prices or other external systems: they have no SSOT in this repo. They are listed as out of scope in 03 and checked only when the repo pins them (a re-check command, a dated "last verified").
- Dated research, analysis and retrospective docs quoting the artifacts of their day (`/sc:prompt`, 33 commands, `/sc:sc`). RULES_DOCS keeps them in place as records; they are listed once, informationally (D-25), not as defects.
- A line-number reference that drifted by a few lines but still lands in the right function.
- Historical CHANGELOG entries describing what a past release did. A CHANGELOG line is a defect only when it names a current artifact wrongly (D-23).
- Values already pinned by a test (README counts, the codex inventory table): a stale one would be red, so they were re-run, not re-audited.

## Severities

- **S1**: following the doc performs a wrong or destructive action on the user's machine or repo (another scope written, user data removed, a branch force-moved), or an always-loaded doc states a contradicted rule that changes model behaviour on every prompt. None found.
- **S2**: a wrong claim about current behaviour, a dead reference in a doc a reader or agent is routed to, or two live docs disagreeing. The reader ends up with a wrong model of the system but no destructive action follows.
- **S3**: incomplete list, stale wording, a dead reference in a dated or working doc, a cosmetic self-description.

## Scope

Docs: `README.md`, `AGENTS.md`, `CLAUDE.md`, `src/superclaude/ARCHITECTURE.md`, `docs/**` except `docs/archive/` and `docs/features/*` (features: relative links checked only), `docs/index.html`, `.claude/rules/**`, `CHANGELOG.md` (current-behaviour claims), `superclaude --help` and every subcommand's help, Makefile `##` help, every `*.md` under `src/superclaude/` (READMEs, CLAUDE_SC.md, commands, agents, modes, MCP docs, core, skills).

SSOT: `src/superclaude/cli/**` (the click app by introspection, `hook_dispatch.HOOKS`, `install_mcp.MCP_SERVERS`, `install_paths.COMPONENTS`), `scripts/context_loader.py` flag tables, `utils` constants, the hook scripts' thresholds and env vars, `pyproject.toml`, `Makefile`, `hooks/hooks.json`, `.github/workflows/test.yml`, `evals/run_eval.py` and `tasks.yaml`, `.claude-plugin/marketplace.json`, the file tree, `git` (branches, cited commits) and, for one claim, `gh repo view`.

Rules: no fix in this round; branch `docs/docs-ssot-audit`, not merged, not pushed; never touch the real `~/.claude`; 0 headless sessions.
