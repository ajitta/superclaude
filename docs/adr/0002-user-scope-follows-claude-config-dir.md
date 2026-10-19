# ADR-0002: User scope follows CLAUDE_CONFIG_DIR

- **Status:** accepted (2026-10-19: Q1 a, Q2 a, Q3 4.31.0, Q4 a — the owner took every recommendation)
- **Date:** 2026-10-19
- **Deciders:** ajitta (owner)
- **Evidence:** [install-upgrade-audit 07-windows-run](../features/install-upgrade-audit/07-windows-run.md) W7; plan Q15 ([05-plan](../features/install-upgrade-audit/05-plan.md) item 15); C-15 in [04a-handoff §3](../features/install-upgrade-audit/04a-handoff.md)

## Context

Claude Code reads its user configuration from `$CLAUDE_CONFIG_DIR` when the variable is set, and from `~/.claude` otherwise. The docs say that "all settings, session history, and plugins are stored under this path" (code.claude.com/docs/en/env-vars). W7 confirmed this on Windows with Claude Code 2.1.303: user `settings.json` (its hooks ran), skills, agents, commands, output styles and the user `CLAUDE.md` were all read from the variable's directory, and Claude Code wrote `.claude.json`, `projects/` and `sessions/` there.

superclaude's user scope is hard-wired to `~/.claude`, so with the variable set a user-scope install is never loaded. Since v4.30.0 (Q15 b), `install` and `doctor` warn about this and do nothing else. `uninstall` gives no warning, and user-scope MCP servers in `$CLAUDE_CONFIG_DIR/.claude.json` are not covered.

## Decision

At user scope, superclaude uses the same directory Claude Code reads: `$CLAUDE_CONFIG_DIR` (with `~` expanded, then made absolute) when it is set and non-empty, else `~/.claude`. One resolver in `install_paths` answers this question, and every site below calls it instead of `Path.home() / ".claude"`:

| Site | Today | After |
|---|---|---|
| `install_paths.get_base_path("user")` | `~/.claude` | the resolver |
| `utils.claude_base()` fallback (hooks, content) | `~/.claude` | the resolver |
| `cli/main.py` content-root fallback | `~/.claude/superclaude` | resolver + `superclaude` |
| `install_mcp` user and project-key entries | `~/.claude.json` | `<config dir>/.claude.json` when the variable is set |
| `insight_writer._project_dir`, `memory_staleness.HOME_PROJECTS` | `~/.claude/projects` | `<resolver>/projects` (Claude Code writes transcripts and auto memory there) |
| `context_loader.migration_reference_roots` | searches both | unchanged (it already lists the variable's dir) |
| `install_paths.config_dir_warning` | the warning | replaced by the notices in Q2 below |

Shipped prose also names `~/.claude/` paths: 12 lines in 12 files, among them `commands/init.md`, `commands/save.md`, `commands/research.md`, `core/RULES.md` and `modes/MODE_DeepResearch.md`. These are instructions to the model, not resolved paths, so the model reads `~/.claude` literally. Q4 covers them.

## Decisions (owner, 2026-10-19)

| Q | Decision | Where it landed |
|---|---|---|
| Q1 | (a) document; doctor flags the scrub | `install_paths.config_dir_notices` (doctor advisory, install message); `utils.user_claude_dir` docstring |
| Q2 | (a) report, never move | `config_dir_notices`: names `~/.claude` and `uninstall --scope user` with the variable unset |
| Q3 | 4.31.0, no canary (no `core/` or `hooks.json` change) | release |
| Q4 | (a) prose unchanged | the 12 lines: `agents/README.md:7`, `agents/security-engineer.md:72`, `ARCHITECTURE.md:65`, `commands/init.md:77`, `commands/README.md:7`, `commands/research.md:25`, `commands/save.md:41`, `core/RULES.md:40`, `hooks/README.md:219`, `modes/MODE_DeepResearch.md:3`, `output-styles/README.md:7`, `skills/sc-author/SKILL.md:19` (under `src/superclaude/`) |

Resolver: `utils.user_claude_dir()` (and `utils.claude_json_path()` for `.claude.json`). Tests: `test_c15_*` in `tests/unit/test_install_upgrade_scenarios.py`; `tests/conftest.py` clears `CLAUDE_CONFIG_DIR` and the scrub variable for every test, so a developer's own setting never redirects a test's user scope into their real config.

End to end (Windows, Claude Code 2.1.303, 1 headless haiku session, login copied into the scratch config dir for the run and deleted right after): `install --scope user` with the variable set wrote only to that dir and printed no notice; the session reported `SessionStart:startup hook success: 🛠️ superclaude: 35 commands, 24 agents (user scope)` and listed `/sc:analyze`; `uninstall --scope user` removed it; the real `~/.claude` listing was unchanged.

## Open questions (owner) — as asked

- **Q1. Hooks under `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`.** The scrub removes `CLAUDE_CONFIG_DIR` from hook subprocesses (env-vars docs, "What the subprocess environment scrub removes"). A user-scope hook would then resolve `~/.claude` and find no content. Options: (a) document the limitation, and have doctor flag it when both variables are set; (b) when the variable is set, a user-scope install also writes `"env": {"SUPERCLAUDE_USER_DIR": "<dir>"}` into that settings file, and the resolver reads it as a fallback (the scrub keeps non-credential variables); (c) derive the directory from the hook payload's `transcript_path` (`<config>/projects/<name>/<id>.jsonl`), which only works for hooks that are given a payload. ★(a) for this round: the scrub is opt-in, and (b) writes a key into the user's settings that uninstall then has to own.
- **Q2. An existing `~/.claude` install when the variable is set.** After the upgrade, `install`/`update --scope user` go to the variable's dir, and the old install stays where Claude Code no longer reads it. Options: (a) report it (install, update and doctor name the other install and the command to remove it: `uninstall --scope user` with the variable unset); (b) move it automatically. ★(a): moving files between two user-chosen roots is the kind of silent change the audit spent its rounds removing.
- **Q3. Release.** ★Minor (4.31.0): user-scope behaviour changes for everyone with the variable set. `core/` and `hooks.json` do not change, so no canary gates are needed. One headless haiku session (with a temporary login copy, as in W7) confirms that a user-scope install under the variable loads end to end, with the SessionStart banner. If Q4 (b) touches `core/RULES.md`, `make release` needs `make canary-gates` (4 sessions).
- **Q4. `~/.claude/` in shipped prose.** Options: (a) leave it, since it is still the default and the variable is rare; (b) reword each line to "the user `.claude` directory (`~/.claude`, or `$CLAUDE_CONFIG_DIR` when set)". ★(a) for this round, with the 12 lines listed in the handoff: rewording `core/RULES.md` costs the 4 canary sessions, and the lines name a default that is still right for everyone who does not set the variable.

## Consequences

- With the variable set, a user-scope install loads in the Claude Code that the variable configures. Without it, nothing changes.
- Two Claude Code profiles (`~/.claude` and a `CLAUDE_CONFIG_DIR` profile) each get their own user-scope install; `superclaude` acts on whichever one the current shell's variable names.
- C-15's other half, the uninstall warning and MCP coverage, follows from the shared resolver instead of from more warnings.
