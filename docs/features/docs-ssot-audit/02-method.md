---
feature: docs-ssot-audit
phase: method
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 02. Method — mechanical extraction plus targeted reading

P2 of [05-plan.md](./05-plan.md). Run from the repo root on `docs/docs-ssot-audit` (master 3301b506). Both scripts are read-only and live in [tools/](./tools/); nothing was added to `scripts/` (the extractor is one-off: its false-positive filters are hand-tuned to this tree).

## 1. SSOT dump

```bash
uv run python docs/features/docs-ssot-audit/tools/ssot_facts.py > "$SCRATCH/facts.json"
```

Prints JSON: version; counts (commands, agents, modes, MCP docs, output styles, skills, core files, rule modules, MCP registry, hook scripts); the rosters; `MCP_SERVERS` commands and methods; `COMPONENTS`; `hooks.json` registrations, events and scripts; `hook_dispatch.HOOKS`; every click command with its options and first help line; `context_loader` tables (`VALID_FLAGS`, `RETIRED_FLAGS`, `CC_NATIVE_PASSTHROUGH`, `RETIRED_COMMANDS`, cutoff, `TRIGGER_MAP` files, `COMPOSITE_FLAGS`); Makefile `.PHONY`; `test.yml` python matrix, triggers and jobs; core file lines and bytes, RULES.md token estimate and section tags; `tasks.yaml` arms and task count; dev extras; `docs/` subdirectories; every test file.

## 2. Reference extraction

```bash
uv run python docs/features/docs-ssot-audit/tools/extract_refs.py > "$SCRATCH/refs.txt" 2> "$SCRATCH/refs.err"
cut -f2 "$SCRATCH/refs.txt" | sort | uniq -c | sort -rn
```

Walks every doc in scope (01 §2; `docs/archive/` and `docs/features/` excluded, features checked for broken relative links only; `docs/index.html` with tags stripped) line by line and prints `file:line  kind  token  note` for each reference that does not resolve:

- `/sc:<name>` → `commands/<name>.md`; `/sc-<name>` → `skills/<name>/`.
- `superclaude <sub> [<sub2>] [--opt…]` → the click command set; `hook <name>` → `HOOKS`; `insight <sub>` and `context <sub>` → their subcommand sets; `--opt` → that command's click options (argparse commands are checked by hand, §4).
- `make <target>` → `.PHONY`.
- Backticked and link-target paths → the tree, with install-tree paths (`~/.claude/commands/sc/x.md`, `superclaude/core/x.md`, `agents/x.md`) mapped back to the source through `COMPONENTS`; placeholders (`<…>`, `{…}`, `*`, `NN`, `…`) skipped; runtime files (`settings.json`, `insights.jsonl`, `.superclaude_hooks/`) accepted.
- `--flag` in non-shipped docs and the shipped READMEs → `VALID_FLAGS ∪ RETIRED_FLAGS ∪ CC_NATIVE_PASSTHROUGH ∪` every command's `<flags>`/`<syntax>` `∪` click options, minus a list of other tools' flags.
- `[RNN Name]` and bare `RNN` in non-shipped docs → `RULES_QUALITY.md`.
- `SUPERCLAUDE_*`, `CLAUDE_CONTEXT_*`, `CLAUDE_CODE_*`, … env vars and backticked `snake_case` / `CONST` / `call()` identifiers → `grep -rw` over code, config and workflows.
- `<N> <commands|agents|modes|MCP servers|hooks|skills|…>` → the counts.
- `@agent` → `agents/`; retired MCP names in shipped content; "integration" next to "branch"; `tests/…/*.py` and `test_*.py` → the test tree.

Result: 443 candidate lines (216 path, 79 identifier, 49 sc-command, 29 flag, 18 count, 13 cli-option, 10 env-var, 16 test refs, 4 make, 9 other).

## 3. Triage

Each hit was read at its line. Discarded classes, with the count they explain:

| Class | Hits | Why not a defect |
|---|---|---|
| Placeholder or example (`/sc:command-name`, `docs/reports/API.md`, `tests/x.py`, `<scope>/`) | ~60 | names a shape, not a thing |
| Claude Code's own names (`CLAUDE_CODE_SUBAGENT_MODEL`, `MEMORY.md`, hook event fields, `--init`, `/btw`) | ~45 | external, 00 §What does not count |
| Dated research/analysis/plan docs quoting their day's artifacts (`/sc:prompt`, `/sc:sc`, 33 commands, `test_skill_canary.py`) | ~110 | records; listed once as D-25 |
| CHANGELOG entries describing a past release (`/sc:sc`, `MODE_Orchestration.md`, `--serena`, `make verify` under Removed) | ~40 | history; only a wrongly named current artifact counts (D-23) |
| MCP tool, API and npm names in `mcp/*.md`, `skills/sc-prompt/references/*` (`performance_start_trace`, `max_tokens`, `--slim`) | ~45 | external vocabulary |
| Other tools' flags and files (`--git-path`, `--no-print-directory`, `credentials.json`, `okf`) | ~30 | not this framework's |
| Resolver limits (HTML text joins like `/sc:brainstormExplore`, Korean suffix `/sc:review가`, `test_runner_hook.py` matched as a test file, argparse options the click introspection does not see) | ~25 | checked by hand, all resolve |
| Counts in a sentence that is not an inventory (`10 commands` lost a section, `2 hooks` in a 2026-03 note) | ~15 | not a count claim |

Surviving: 24 lines, folded into D-01–D-25 with the targeted findings.

## 4. Targeted reading (claims the extractor cannot see)

Read both sides for: every CLI help text (captured with `uv run superclaude <cmd> --help`, plus `context explain|reset`, `insight <sub> --help`); `make help`; `superclaude mcp --list`; `install --list` and `--list-all`; README sections Overview, Quick Installation, Uninstall, Workflows, What's new, Deep Research, References, Flags, All Commands; ARCHITECTURE in full; the eight shipped READMEs and `CLAUDE_SC.md`; `FLAGS.md` against README's flag tables; `RESEARCH_CONFIG.md` against README's research tables; `hooks.json` against `hooks/README.md` and `scripts/README.md`; `docs/README.md`, `PRD.md`, `UI-GUIDE.md`, ADR-0001, `ORCHESTRATION_COMMANDS.md`, `PROJECT_INDEX.md`, `docs/agents/*`; the codex README, 02, and the gate/test/make lines of 03–08; the six authoring rules' test and path references; the gotchas; `test.yml`; `pyproject.toml`; `evals/run_eval.py` ARMS and `evals/README.md` arms; `.gitignore` and `git check-ignore`; `gh repo view --json hasIssuesEnabled`; `git cat-file -t` for the seven commit hashes docs cite; roster set-diffs for `commands/README.md`, `agents/README.md`, `help.md` against the tree; CHANGELOG 4.30.x and 4.29.x entries that name current behaviour (`doctor` exclude check, `--remove-mcp` needs `claude`, retired modes gone, `pytest-cov` and `make verify` removed) against the code.

## 5. Reproduce

```bash
git checkout docs/docs-ssot-audit
SCRATCH=$(mktemp -d)
uv run python docs/features/docs-ssot-audit/tools/ssot_facts.py > "$SCRATCH/facts.json"
uv run python docs/features/docs-ssot-audit/tools/extract_refs.py > "$SCRATCH/refs.txt"
for c in install uninstall mcp update doctor verify-drift author-check; do uv run superclaude $c --help; done
make help
```

The scripts import the package, so they need the dev venv (`uv pip install -e ".[dev]"`); they write nothing.
