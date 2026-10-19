---
feature: docs-ssot-audit
phase: inventory
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 01. Inventory — docs in scope, their claim types, the SSOT each maps to

P1 of [05-plan.md](./05-plan.md). Base `master` @ 3301b506 (v4.30.2). Counts are not copied here (`stale-number-copies`): `tools/ssot_facts.py` prints them.

## 1. Claim types and their SSOT

| Type | Example shape | SSOT | How checked |
|---|---|---|---|
| Component count | "35 slash commands", "24 agents", "14 hooks" | `src/superclaude/<dir>/*.md` minus README; `hooks.json` registrations | `ssot_facts.py` counts; `extract_refs.py` COUNT regex |
| Command / skill name | `/sc:plan`, `/sc-author` | `commands/<name>.md`, `skills/<name>/` | set membership |
| CLI subcommand, option, help | `superclaude update --scope`, help docstrings | click app (`cli/main.py`) by introspection; argparse `--help` for `insight`, `hook`, `auto-improve`, `parallel-ab` | captured help text, option sets |
| Hook name / registration | `superclaude hook session_init`, event lists | `cli/hook_dispatch.HOOKS`, `hooks/hooks.json` | set membership; README list vs json |
| Make target | `make deploy` | `Makefile` `.PHONY` | set membership |
| Flag | `--uc`, `--think`, command-local flags | `context_loader.VALID_FLAGS`, `RETIRED_FLAGS`, `CC_NATIVE_PASSTHROUGH`; each command's `<flags>`/`<syntax>`; click options | union membership, then manual read |
| MCP server | tavily, playwright, chrome-devtools; retired names | `install_mcp.MCP_SERVERS`; CHANGELOG removals | registry; retired-name grep over shipped content |
| Path | `docs/x.md`, `tests/unit/test_x.py`, `~/.claude/commands/sc/` | file tree; install paths mapped back to source via `install_paths.COMPONENTS` | resolver in `extract_refs.py` |
| Rule citation | `[R18 Necessity Test]` | `core/rules/RULES_QUALITY.md` definitions | name match (shipped content already tested) |
| Env var, identifier | `SUPERCLAUDE_LOOP_GUARD`, `DEFAULT_CONTEXT_MAX_TOKENS` | `grep -w` over `src/`, `tests/`, `scripts/`, `evals/`, `Makefile`, `.github/` | grep |
| Threshold / constant | 30KB, 12K tokens, 15 min, 5 errors, 0.8/0.6 cutoffs, ~20 ms | the script or module that holds it | targeted read |
| Behaviour claim | "`/sc:reflect` writes insights", "`doctor` checks X", "`uninstall` removes Y" | the command file or CLI code | targeted read of both sides |
| Process claim | CI matrix and triggers, branch model, release gate, dev deps | `test.yml`, `AGENTS.md`, `Makefile`, `pyproject.toml` | targeted read |
| Directory listing | "docs/ holds specs/, troubleshooting/" | `ls docs/` | `ssot_facts.py` `docs_dirs` |
| Git fact | cited commits, branch names | `git cat-file -t`, `git branch -a` | command |
| External claim | Claude Code hook events, npm versions, model prices, GitHub settings | none in repo | out of scope unless the repo pins a re-check |

## 2. Documents in scope

| Doc | Claim types it makes | Notes |
|---|---|---|
| `README.md` | counts, commands, CLI, flags, hooks, MCP, research numbers, workflow gates, file pointers | counts and roster guarded (§3) |
| `AGENTS.md`, `CLAUDE.md` | uv rules, tests, make targets, branch model, hook form, rules dir layout, memories | every claim checked; one wording hit (D-24) |
| `src/superclaude/ARCHITECTURE.md` | directory roles, delivery, token budgets, test table, skills delivery | |
| `src/superclaude/*/README.md` (commands, agents, modes, mcp, output-styles, hooks, scripts, core) | rosters, install paths, validation commands, hook lists, kernel size | `*/README.md` is in the no-expiry test but not count-guarded |
| `src/superclaude/CLAUDE_SC.md`, `core/*.md`, `core/rules/*.md` | imports, flags, rule ids, thresholds | citations guarded |
| `src/superclaude/commands/*.md`, `agents/*.md`, `modes/*.md`, `mcp/*.md`, `skills/**/*.md` | CLI calls, paths, flags, other components | structure guarded; references checked mechanically |
| `docs/README.md`, `docs/PRD.md`, `docs/UI-GUIDE.md`, `docs/adr/0001`, `docs/reports/*.md`, `docs/agents/*.md`, `docs/good-skills.md` | layout, CI, tests, guards, CLI output, branch model, tracker | |
| `docs/codex/prompting_session_raw/0[1-8]*.md`, `README.md` | inventory (guarded), gates, make targets, test files, arms | Korean working guides, `last_verified: 2026-08-22` |
| `docs/research/*`, `docs/analysis/*`, `docs/plans/*`, `docs/experiments/*` | dated records | dead-reference check only (D-25) |
| `docs/index.html` | install steps, plugin names, commands | text extracted from HTML |
| `.claude/rules/*.md`, `gotchas/*.md`, `schemas.yaml` (via its test) | tests, paths, identifiers, env vars, fields | |
| `CHANGELOG.md` | current artifacts named in recent entries | 4.29.0–4.30.2 spot-checked against code |
| CLI help (12 subcommands, `context explain|reset`) | self-description, scopes, mechanisms | captured 2026-10-19 |
| `Makefile` `##` help | target descriptions | listing guarded |

## 3. Existing guard tests (do not duplicate)

| Test | Guards |
|---|---|
| `tests/unit/test_version_consistency.py` | pyproject is the version source; README version and badge table; every README count shape; README "All Commands" roster = command files; `/sc:help` `<commands>` block = command files; no pass count in README/CLAUDE/AGENTS; CHANGELOG leads with the pyproject version; install URLs name a release; no expiring claim (`as of <date>`, `verify quarterly`, `last reviewed`, `## Current … (N)`) in README, CLAUDE, AGENTS, `.claude/rules/*.md` (not gotchas), `core/**`, `src/superclaude/*/README.md` |
| `tests/unit/test_codex_component_map.py` | codex `02_component_and_delivery_map.md` §1 counts = source tree; its hook-registration note = `hooks.json` |
| `tests/unit/test_install_docs.py` | README and `docs/index.html` install sections: order Quick → Clone → Fork, no contributor path, no `make` in clone/fork steps |
| `tests/unit/test_makefile_help.py` | every `.PHONY` target has a `##` line; help is generated |
| `tests/unit/test_release_recipe.py` | release notes come from the CHANGELOG entry; `GH_REPO` from origin |
| `tests/unit/test_cross_references.py` | shipped content: `<handoff next>` targets exist; `[RNN Name]` citations match `RULES_QUALITY.md`; kernel pointers resolve; agent trigger uniqueness |
| `tests/unit/test_content_usage.py` | every mode and MCP doc is in `TRIGGER_MAP`/`COMPOSITE_FLAGS`; those paths exist |
| `tests/unit/test_{agent,command,mode,output_style,content}_structure.py`, `test_sc_author_skill.py`, `test_sc_prompt_skill.py`, `test_author_check*.py` | shipped component structure, descriptions, flags blocks, step labels, skill references |
| `tests/unit/test_gotcha_budget.py` | gotcha entry length; budget stated in the gotchas README |
| `tests/unit/test_plan_checklist.py` | a `status: complete` plan has no open checkbox |
| `tests/unit/test_hook_dispatch.py` | `hooks.json`, the registry and `scripts/` agree; no click import on the hook path |
| `tests/unit/test_context_loader.py` `TestCoreLiteSplit` | kernel token budget; module ↔ routing sync |
| `tests/unit/test_session_memory_folder.py`, `test_shipped_content_server_neutral.py` | save/load name `.claude/memories/`; no retired server tool names in shipped content |
| `tests/unit/test_rules_schemas.py` | `schemas.yaml` parses; role groups |
| `tests/integration/test_cross_directory_refs.py` | the core import chain |

Not guarded today, and where the findings sit: hook lists in `hooks/README.md` and `scripts/README.md` vs `hooks.json`; CLI help text vs the mechanisms it names; `docs/README.md` and `PROJECT_INDEX.md` directory listings vs `docs/`; test-file paths named in docs; PRD process claims (CI, dev deps, eval arms); behaviour claims README makes about commands (`/sc:reflect`, `/sc:research` numbers); two docs stating the kernel size.
