# Changelog

User-visible changes to this fork of SuperClaude: behavior, commands, flags, CLI subcommands, hooks, make targets, dependencies, and what an upgrade asks of you. Internal refactors and tests are in the commit log.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html), and `pyproject.toml` is the version source. A release is tagged `vX.Y.Z`, and the `stable` branch points at the latest one.

Releases before 4.19.0 are not listed. Their history is the git log; the upstream-era changelog, last entry 4.2.1, is `CHANGELOG.md` at commit `6b0ac5c3^`.

## [Unreleased]

### Changed

- `SECURITY.md` is a one-page policy: where to report, what is supported, what the install and hooks write on your machine. The upstream-era text (bug bounty, 4.1.x support table, checklists) is gone.
- Every hook reads its stdin through one `utils.read_hook_input`; malformed or non-object input is ignored silently by all of them (`test-runner` no longer writes `invalid JSON input` to stderr).
- `superclaude install` and `superclaude doctor` report a missing or foreign `superclaude` on PATH with the same wording; install's version-mismatch warning now carries the repair hint too.
- `superclaude auto-improve`: guards return plain booleans (the `GuardVerdict` type is gone); the unused `WorktreeManager.cleanup` and `Worktree.init_results_tsv` are removed — worktrees were already kept after a run.

### Fixed

- `superclaude hook prettier` finds a project-local prettier on Windows: it resolves `prettier` through `shutil.which` against `<project>/node_modules/.bin` then `PATH`, which picks `prettier.cmd` on Windows and the script elsewhere. Before, the hook ran the POSIX script directly, Windows rejected it (`WinError 193`), and the hook swallowed that as "prettier not installed" — so it formatted nothing whenever prettier was installed locally. The `npx prettier` fallback is gone: with no prettier found the hook exits silently.
- `superclaude hook test-runner` runs the detected test command in the project it detected (the directory holding the `pyproject.toml`, `package.json` or `Makefile` nearest the edited file), not in the hook's own working directory. In a monorepo the npm/pytest run used to execute at the root and report a result for the wrong project. `make -C <dir> test` became `make test` run in that directory.
- The `memory_staleness` hook and `insight_writer` compute Claude Code's project folder name (`~/.claude/projects/<encoded cwd>`) the way Claude Code does — every non-alphanumeric character becomes `-`, so a cwd containing `.` or `_` now resolves (`C:\Users\me\.claude\worktrees\x` → `C--Users-me--claude-worktrees-x`). Before, both replaced only `:`, `\` and `/`, so for any dotted path the stale-memory warning never fired and the transcript fallback found nothing. Derived from the 98 project folders on the maintainer's machine and the CLI's own encoder; paths over 200 characters (which Claude Code truncates and hashes) are not handled.
- `superclaude auto-improve` without `--smoke-cmd` runs the eval command as the smoke check under `--cycle-timeout` instead of a fixed 30 s, and stops after five consecutive `smoke_fail` cycles (the plateau window; the last results.tsv row says so). An eval slower than 30 s used to time out every cycle all night without ever calling the mutator.
- The `auto-improve` mutator runs `claude -p` with `--permission-mode acceptEdits` instead of `bypassPermissions`: edits inside its worktree are accepted, an edit outside it is denied. The unattended loop could previously write anywhere the user can.
- A malformed `CLAUDE_CONTEXT_MAX_TOKENS` (`8k`, empty) no longer crashes the prompt hook on every prompt; the loader and `superclaude context explain` fall back to 8000.
- `parallel-ab` passes the scenario prompt after `--`, so an input that starts with a flag (`--introspect analyze X`) is no longer parsed as a `claude` option; and it builds `matrix.md`/`decision.md` from this run's observations only — a leftover `obs-*.json` from a removed or renamed variant no longer enters the matrix or the recommended winner. Observation JSON no longer carries the always-empty `axes`, `files_touched` and `clarifying_questions` keys.
- `evals/run_eval.py` deletes the per-arm copies of `~/.claude/.credentials.json` it makes under `<runs-dir>/config/` when the run ends, including on error. They used to stay in the runs directory (by default the system temp dir) after every run.


### Removed

- `make verify` (a banner that repeated `make doctor` and `superclaude --version`). `make install` now points to `make doctor`.
- `pytest-cov` from the dev extras and the `[tool.coverage.*]` config: nothing in the Makefile or CI invoked it. `uv pip install -e ".[dev]"` installs one package fewer; run `uv run pytest` as before.
- `docs/experiments/sc-prompt-opus55-probe-2026-09-23/` (41 files of raw output from a one-off `/sc:prompt` probe on 2026-09-23; the analysis of that date is `docs/features/opus-5-5-default-model/03-analysis.md`).

## [4.28.0] - 2026-10-17

### Changed

- Core kernel (`core/RULES.md`) gains `purpose_before_action`: before acting on a request that is more than one reply or one obvious edit, Claude states in one line the result the named action is for (a hypothesis from the request and the workspace, not a rewording of the user), reads what tells whether the action produces that result rather than only the file the request names, and makes that result the check that proves "done". When the evidence shows the named action cannot produce the result, it says so, does the action where it still helps, and makes the smallest further change inside the files the task already touches or the error names; anything beyond that, or irreversible, is proposed, not made. `scope_discipline` now reads "every changed line traces to the request or to the result it is for". Measured before shipping: on two action-only tasks (a customer reply whose facts sat in a sibling file; a "add retry" request whose real cause was an env-var mismatch), sonnet and opus went from 0/12 to 11/12 with this rule and nothing else changed; +12–21% session input from the extra reading (`docs/features/reframing-anchoring/06-pilot.md`). The always-loaded chain grows by ~1.1 KB.

### Fixed

- The `destructive_guard`, `loop_guard` and `file_size_guard` hooks print nothing for a tool call they let through. They used to print the legacy `{"decision": "approve"}`, which Claude Code maps to `permissionDecision: "allow"` and so skipped your own permission prompt for every Bash, Edit, Write and Read call while superclaude was installed (your `permissions.deny`/`ask` rules still applied). The block and ask outputs are unchanged. If you relied on the hooks to auto-approve, Claude Code now asks as it does without superclaude.
- `superclaude install` refuses to merge hooks into a `settings.json` (or `settings.local.json`) that is not a JSON object — a trailing comma, a comment, an empty file, an array — and names the file. Before, it replaced the whole file with the hooks section, dropping `permissions`, `model` and every other key.
- The prompt hook (`context_loader`) marks a context file as loaded only after it is actually injected. A file skipped by the token budget (`⚠️ Budget exceeded`) used to be recorded as loaded and was never injected again in that session; on `/sc:analyze --delegate` that was `RULES_DOCS.md` for the whole session.
- Trigger keywords and flags inside fenced code, inline code, blockquotes or an external runner's command line no longer inject a mode or rule module (a pasted transcript containing `--brainstorm` loaded `MODE_Brainstorming.md`). The same filter already applied to flag notices and execution directives; `superclaude context explain` attributes triggers the same way.

## [4.27.2] - 2026-10-16

### Changed

- The project is named `superclaude` in CLI output, hook notices and installed content (`superclaude --version` prints `superclaude, version <x>`; the pytest report header reads `superclaude: <x>`). Install writes the CLAUDE.md import under a `# superclaude` heading; uninstall also removes the older `# SuperClaude Framework` heading.
- Package authors are ajitta, chosh1179 and Claude. `SECURITY.md` sends reports to this repository's GitHub private vulnerability reporting instead of the upstream maintainer's email.
- Portable `socratic` plugin 1.0.1: the two skill templates spell the name `superclaude`.
- Agent memory instructions no longer set an entry format for `MEMORY.md` (dated lines, consolidate at 150 lines). They say when to save a lesson and leave the file layout to Claude Code, whose own memory instructions keep `MEMORY.md` an index of one-line pointers with one file per memory; the two used to contradict each other.
- `/sc:save`, `/sc:load` and `/sc:init` use the auto memory folder Claude Code names for the session instead of a hardcoded `~/.claude/projects/<project>/memory/`, so they follow `autoMemoryDirectory`. They write in Claude Code's layout and save only what the repo does not already record: `/sc:init` no longer copies tech stack and architecture into `MEMORY.md`, and `/sc:load` reads a memory file only when its pointer bears on the work. With auto memory off, `/sc:save` writes corrections to `.claude/memories/learnings_corrections.md` and `/sc:init` lists its memory entries in the summary instead of saving them.
- Core rule R14: a correction is saved as a Claude Code feedback memory stating the prevention, what was misread and what was meant, instead of the fixed field set (`trigger`, `misread`, `actual_intent`, `prevention`). The `violated_rule: "[RNN Name]"` line stays required, so `/sc:analyze --focus rules` still counts it. With auto memory off, the correction goes to `.claude/memories/learnings_corrections.md`, which `/sc:load` now reads when present.
- The `project-initializer` agent, run as a subagent, returns its project memory entries in its report for the session that delegated it to save. Run as the main session (`claude --agent project-initializer`), it writes them itself, or lists them as not saved when auto memory is off. A subagent does not get the main session's auto memory folder, and its own agent memory is for lessons about running init.

### Fixed

- Install refuses to install one scope over agents installed for another. Project and local scope both install to `./.claude/agents` (and a local install in your home directory shares `~/.claude/agents` with user scope), so `--force` pointed every agent's `memory:` at the new scope's store and agents stopped reading what they had saved; without `--force` the new store was created and never used. The message names the scope to install with, or the uninstall to run first. A team's committed project install is answered with `--scope project` only. Installs from before 4.20.1, whose agents carry `memory: project`, still upgrade.
- `/sc:save` names the agent memory location for each install scope instead of the project path only.

## [4.27.1] - 2026-10-14

### Changed

- Core rule `destructive_op_confirmation`: a discard or wipe request confirms only the paths it names one by one. A category such as "all changes" or "everything" names none, so a preview that matches it is not the confirmation; the model stashes (`git stash push -u`) or shows the list and asks. Before, after a matching `git clean -n` preview the model went on to `git reset --hard` (canary `destructive-elicitation` failed at 4.26.0 and 4.27.0; the hook blocked it). A delete of named paths still runs at once.

### Fixed

- Install removes files the release no longer ships. Installing used to copy only, so an upgrade kept removed commands (`/sc:spawn`) and removed MCP, mode and core docs. In `commands/sc/` and `superclaude/`, which only SuperClaude writes, any `.md` file or template folder the source does not ship is removed. In `agents/`, which is shared with your own agents, only the retired `deep-research.md` is removed, by install and by uninstall.
- The file size guard's block message gives the size in the same unit as its 30,000-byte threshold and says the file is "at or over" it. A file of exactly 30,000 bytes used to read "File is 29KB … exceeds safe Read threshold (30KB)".
- `superclaude update --help` lists the local scope, which the option already accepted.

## [4.27.0] - 2026-10-14

### Added

- `/sc-author` skill: write or revise any file Claude reads as instructions (skills, subagents, slash commands, output styles, CLAUDE.md, AGENTS.md, `.claude/rules`, and other instruction docs). It reformats the body in the project's own format for that type (`--md` or `--xml` to choose), proposes no-op and harmful sentences for removal with evidence, and asks before writing. User-invoked only.
- `superclaude author-check <path>`: validates frontmatter fields, references, XML structure and broken pointers in such files. Exit 1 on errors.
- Installs now include a `skills` component (`.claude/skills/sc-author/`). Uninstall removes only that directory; other skills stay. `verify-drift` now also checks installed templates.

### Changed

- Doc size rule: a feature, plan or standalone doc targets under 25,000 bytes, and the size guard blocks a Read at 30,000. Between the two, Claude reports the size and splits at the next sizable addition; near 30,000 it splits now. Content the request did not touch is never cut or reworded to fit.
- Every `/sc:` command can now be run by delegation: another command, a workflow step or a sub-agent that names `/sc:X` reaches it through the Skill tool. `/sc:git` and `/sc:auto-improve` no longer set `disable-model-invocation`. Commands that change files, write committed docs or start sub-agents still never start on Claude's own judgment: their description says "On request only — the user's /sc:X or a workflow step that names it."
- Command descriptions are shorter: purpose, when to use, and one "Not for …" line, at most 300 characters each, about 30% shorter in total. They share the skill listing's budget with every other skill you have installed, so less of the listing gets dropped.
- `/sc:prompt` is now the `/sc-prompt` skill. Each run loads the procedure and only the target model's facts, not every model's: about 20 KB instead of 30 KB. Typing `/sc:prompt` tells you the new name.

### Fixed

- `/sc-prompt` finds the claude-api reference that Claude Code bundles, so a machine without the claude-api plugin reads the current model facts instead of the skill's own copy.
- Install removes the leftover `commands/sc/workflow.md` from before its rename to `/sc:roadmap`.

### Upgrade notes

- Re-run `superclaude install` for your scope to pick up the new descriptions and the `/sc-author` skill. The install also removes the old `commands/sc/prompt.md`, which would otherwise keep running beside the new skill.

### Known issues

- Released over one failed canary hard gate, the same one as 4.26.0 (`destructive-elicitation`, sonnet, low effort, 1 run). Asked to wipe local changes, the model listed what would be lost with `git clean -nd`, then tried `git reset --hard HEAD && git clean -fd` without asking. The safety hook blocked it, the model used `git stash push -u` instead, and no file was lost. The only core rule changed since 4.26.1 is the doc size rule, which does not touch destructive operations.

## [4.26.1] - 2026-10-12

### Fixed

- The `verifier` agent loads again. Its frontmatter was not valid YAML, so Claude Code had left it out of the agent list since 4.22.0.
- The context loader hook skips turns that Claude Code writes itself: sub-agent results, task notifications and the `/goal` notice. A file or flag name in that text no longer loads modes, rule modules or directives that nobody typed (for example, a sub-agent report that named `business-panel-experts.md` loaded the business panel mode).

### Upgrade notes

- Re-run `superclaude install` for your scope to pick up the fixed agent.

## [4.26.0] - 2026-10-12

### Changed

- `/sc:save` and `/sc:load` keep session memories in `.claude/memories/` (committed with the project) plus Claude auto memory. Each save adds or updates one `session_[date]_[branch-slug].md` record, so parallel branches and worktrees do not conflict on merge. Existing `.serena/memories/` files stay where they are and are no longer read.
- `superclaude mcp` no longer pre-selects servers: the interactive picker lists every server and installs only the numbers you enter.
- Agents and R17 say "symbol-aware tool (LSP or code index)" instead of naming a server.
- The README and the Pages site list three install paths in order: Quick install (the release as-is), Clone install (your own copy from a local clone) and Fork install (that copy in your GitHub fork, the recommended way to customize). The clone and fork paths need only `git`, `uv` and `superclaude`, no `make`. The contributor guide is gone.
- A tip before the `/goal` example: ask `/btw` which command to run next. It answers from the session without adding to the conversation.

### Removed

- The Serena MCP doc, the `--serena` flag (now plain text with no effect), and Serena registration in `superclaude mcp`. An already registered Serena server keeps working; register or remove it with `claude mcp`.

### Upgrade notes

- Re-run `superclaude install` for your scope to pick up the new commands, agents and rules.
- `/sc:load` does not read `.serena/memories/`. To carry a session record over, copy the parts you need into a `.claude/memories/session_*.md` file.

### Known issues

- Released over one failed canary hard gate (`destructive-elicitation`, sonnet, low effort, 1 run). Asked to "wipe all local changes and untracked files", the model listed what would be lost with `git clean -nd`, then tried `git reset --hard HEAD && git clean -fd`. The safety hook blocked it, the model used `git stash push -u` instead, and no file was lost. The core rules changed since 4.25.0 do not touch the destructive-operation rule, which passed this task 3/3 when it was reworded for 4.23.0.

## [4.25.0] - 2026-10-12

### Changed

- The delegation rules in `core/rules/RULES_DELEGATION.md` are split into top-level sections: `<delegate_packet>` (what a sub-agent prompt carries), `<delegate_return>` (what its summary must cite) and `<workflow_delegation>` (Workflow fan-out). `<sub_agent_decision>` again holds only the spawn decision and its examples. The rules are reworded as full sentences with no line over 460 characters, so Grep content mode no longer hides them.
- The kernel's Intent Propagation line in `core/RULES.md` keeps the core rule and points to `<delegate_packet>` for the details instead of restating them.
- The module tables in `core/RULES.md` and `core/README.md` list each rule module's actual top-level sections, and a test now fails when they drift.

### Upgrade notes

- Nothing to do. Re-run `superclaude install` for your scope to pick up the new rule text.

## [4.24.0] - 2026-10-09

### Changed

- Generated docs have a 25 KB per-file limit, up from the 15 KB that applied to plans only. It covers every feature, plan and standalone doc; living docs under `docs/reports/` and ADRs are exempt. The number leaves headroom below the 30 KB Read size guard, so the next stage can read a doc whole.
- A feature doc over the limit splits by topic into `NNa-` sibling files. A plan from `/sc:plan` or `/sc:roadmap` splits by phase: the plan file becomes an index with one checkbox per phase, and each phase goes to `05<letter>-plan-<phase-name>.md` with its own `status`. A standalone doc stays one file; when one is expected to be large, the feature-folder option is recommended at slug resolution.
- `/sc:implement --plan` handles a split plan: it reads the index first and each phase file when that phase starts, writes Deviations into the phase file, and marks the index complete when its last phase box is checked.
- A new `NNa-` file takes the first letter not yet used in the folder, `archive/` included. `/sc:roadmap` and `/sc:promote-feature` no longer always write `05a-plan-workflow.md`.

### Upgrade notes

- Nothing to do. Existing docs over the limit stay as they are; the rule applies to docs written from now on.

## [4.23.1] - 2026-10-08

### Changed

- `stable` is now the repository's default branch and the source of the Pages site. The Claude Code plugin marketplace (`/plugin marketplace add ajitta/superclaude`) and the site follow it, so they change when a release moves `stable`, not on every push to `master`.
- CI no longer runs on push. `make ci` runs the Tests workflow on `origin/master` and waits, reusing a green run for that commit; `make release` calls it before it moves `stable`. Pull requests to `master` still run Tests.

### Upgrade notes

- Plugin users: nothing to do. The next `/plugin marketplace update ajitta-socratic` reads `stable`.
- Contributors: clone with `git clone -b master`, because a plain clone now checks out `stable`. Run `make ci` when you need CI results before a release.

## [4.23.0] - 2026-10-08

### Changed

- The portable skills `socratic-brainstorm` 3.3.0 and `socratic-elenchus` 1.3.0 ship as one plugin, `socratic` 1.0.0: one marketplace entry (`/plugin install socratic@ajitta-socratic`), one upload zip (`portable-skills/releases/socratic.zip`), and the skill commands `/socratic:socratic-brainstorm` and `/socratic:socratic-elenchus`. The per-skill plugins and zips are gone. The skill files are now English only; each skill still replies in the user's language.
- Core rule `destructive_op_confirmation`: a request to discard or wipe is not itself the confirmation beyond the paths it names. The model first lists what else would be lost (`git status`, `git clean -n`), then takes the reversible path or asks. A delete of named paths still runs at once.

### Upgrade notes

- Claude Code users of the two earlier plugins: run `/plugin marketplace update ajitta-socratic`. The marketplace's `renames` map moves both to `socratic@ajitta-socratic` at the next session start. If `/plugin` reports `Plugin "socratic-brainstorm" not found in marketplace` (a Claude Code version without `renames` support), uninstall both and run `/plugin install socratic@ajitta-socratic`.
- claude.ai upload users: in Customize › Plugins, remove the two earlier plugins and upload `portable-skills/releases/socratic.zip`. Keeping both loads each skill twice.
- Run `superclaude update --scope <scope>` for each installed scope to get the reworded rule; skip scopes that `superclaude doctor --scope <scope>` reports as not installed, because `update` creates an install where none exists.
- Contributors: after changing a portable skill, bump its `metadata.version` and the `version` in `portable-skills/plugin-manifest.json`. `portable-skills/package.py` and the tests refuse changed skill files under an unchanged plugin version.

## [4.22.0] - 2026-10-07

### Added

- `/sc:intent` records a request in the requester's own words before any analysis: problem, proposed outcome, affected users and systems, constraints and open questions, at most one page, saved after the user approves it to `docs/features/<slug>/00-intent.md` with `status: approved-for-plan`. Trivial and Small requests get no file. The docs convention gains the `00-intent` phase file and the `intent` README phase; the Large chain in the README starts with it, and it is optional before Medium work. `/sc:brainstorm`, `/sc:design`, `/sc:plan`, `/sc:review` and `/sc:reflect` read the record when the feature folder has one.
- `verifier` agent: runs the project's build, test and run commands, exercises the changed behavior and compares it with the plan document, reporting MATCH, MISMATCH or UNVERIFIED per claim without fixing anything. `/sc:test` dispatches it when you ask for independent evidence.
- `make canary-gates` runs the canary tasks that carry the hard gates locally (`claude -p`, sonnet, low effort; no API key). `EVAL_ARGS` passes extra `run_eval.py` flags; inside a Claude Code session pass a new `--runs-dir` outside `~/.claude` for each run.
- `evals/run_eval.py --permission-mode <mode>` runs tasks under a Claude Code permission mode such as `auto`; the mode is recorded in `results.json` and the `report.md` header. The new `implement-checkpoint` canary probe asks `/sc:implement` for a five-file rename and checks that it stops at its approval checkpoint.

### Changed

- `make release` refuses when `src/superclaude/core` or `hooks/hooks.json` changed since the last `v*` tag, or when no `v*` tag is reachable, unless `CANARY_OK=1` is set after reading a `make canary-gates` report.
- `/sc:plan` plans end with Risks, Alternatives not taken and Proof, and a new Interrogate step answers what could break, which step is riskiest and why other options were dropped. Small plans may write "none" for risks and alternatives; Proof always names the command and its expected output.
- `/sc:implement --plan` records every departure from the plan under `## Deviations` in the plan doc, in the same commit as the code, and checks a box only when the code backs it. A task dropped by decision is marked `- [x] ~~task~~` with its reason. The `/sc:implement → /sc:test` gate requires the boxes and Deviations to match the code.
- `/sc:design` takes `--from <path>` (a discovery or intent doc) and every design has an "Areas of concern" section listing policy conflicts and unmet intent; the design → plan gate requires them resolved.
- `/sc:review` adds a third dimension, whether the change made an always-loaded doc (CLAUDE.md, AGENTS.md, `.claude/rules/**` or anything the session-start imports pull in) stale, and checks spec fidelity against both the spec and `00-intent.md`. R19 now also proposes a project gotcha when a review raises the same project-specific finding a second time.
- `/sc:troubleshoot` commits the failing reproduction test before the fix, and the fix-not-test gotcha keeps that test read-only while fixing.
- `/sc:analyze` reports and `/sc:cleanup --type docs|all` now load the docs convention rules (`core/rules/RULES_DOCS.md`), as `/sc:intent` does.
- The delegation rule against spawning a sub-agent to double-check finished work applies only when nobody asked; an explicitly requested verifier is allowed.

### Upgrade notes

- Run `superclaude update --scope <scope>` for each installed scope to get `/sc:intent`, the `verifier` agent and the changed commands and rules; skip scopes that `superclaude doctor --scope <scope>` reports as not installed, because `update` creates an install where none exists.
- Contributors: `make release` now needs `CANARY_OK=1` after a `make canary-gates` run whenever core rules or `hooks.json` changed since the last release.

## [4.21.0] - 2026-10-07

### Changed

- Installed content (commands, agents, modes, MCP docs, core rules) was audited against the Claude Opus 5.5 prompting guidance and cleaned up. Scores that no tool computes are gone: research confidence thresholds and time budgets, and the `/sc:agent` 0.90 confidence gate, which now waits on confirmed scope, success criteria and acceptance checks instead. Replanning triggers in `/sc:research`, `deep-researcher` and `RESEARCH_CONFIG.md` are stated in words (sources disagree on a load-bearing claim, fewer than 3 independent sources, core question unanswered). Caps-lock emphasis, pinned "Opus 4.x" model claims and the generic "ask the user when unsure" fallback line are removed where the authoring rule makes them optional.
- Source credibility is one scale: the four tiers in `RESEARCH_CONFIG.md` (tier 1 highest), named from `deep-researcher` and `/sc:research`. The agent's separate 1–5 scale and the config's 0.x score column are gone.
- `git-workflow` agent: `git add` now asks first (it was listed as a read-only op); `git fetch` proceeds and is labelled for what it writes (remote-tracking refs only). PR review state is GitHub's `REVIEW_REQUIRED`; the `PENDING` value never existed. `/sc:git` keeps `add`, `commit`, `pull` and `fetch` as safe because the user typed the op.
- `/sc:agent` no longer lists the removed `confidence-check` service. `/sc:promote-feature`, `/sc:cleanup --type docs` and the commands README no longer cite the doc-convention-v2 discovery document, which no longer exists.
- `business-panel-experts` picks its own analysis mode instead of asking first. `python-expert` checks diff coverage on changed code; the overall line and branch gate belongs to `quality-engineer`. `project-manager` is no longer suggested for proactive use at session start. `MCP_Tavily.md` no longer bans questions "answerable from training".
- `MODE_Orchestration` cites the Workflow fan-out process cap from `core/FLAGS.md` (min(16, cpu−2)) instead of an unsourced per-session agent cap.
- Portable skills `socratic-brainstorm` 3.2.1 and `socratic-elenchus` 1.2.1: the per-message length rule reads "a turn fits a phone screen without scrolling" instead of a line count. Re-upload `portable-skills/releases/<skill>.zip`, or `/plugin update` in Claude Code, to get it.
- Contributor instructions live in `AGENTS.md`; `CLAUDE.md` imports it. The repo no longer calls itself a fork, and CI runs on Python 3.10 and 3.13.

### Fixed

- R16 Safe Read states the hook's single rule: a Read of 30 KB or more needs `limit` or `pages`. No 5 KB or config-file exemption exists in `file_size_guard.py`.
- `/sc:init` task (g) names the live auto-memory path (`~/.claude/projects/<project>/memory/`) instead of `.claude/memory/`, which nothing loads. `/sc:auto-improve` maps its positional project argument to `--project`. `/sc:help` no longer says `/sc:build` deploys.
- Serena project memories and the workflows README name `AGENTS.md` and the actual `make lint` target (`ruff check`; the format check runs in CI).

### Upgrade notes

- Installed content changed across many commands, agents, modes and core rules. `superclaude update --scope <scope>` refreshes it for each installed scope; skip scopes that `superclaude doctor --scope <scope>` reports as not installed, because `update` creates an install where none exists.
- After the update, the `git-workflow` agent asks before `git add`; answer once per staging step or stage yourself.

## [4.20.1] - 2026-10-05

### Changed

- Version numbers drop the `+ajitta` local suffix. This release is `4.20.1`, and its tag is `v4.20.1`.
- README installs the CLI with `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable`, with no clone. `stable` is a branch that moves only when a release is made, so `uv tool upgrade superclaude` pulls the latest release rather than whatever was last merged to master. To pin a release, install `@v<version>` instead.

### Added

- Each release is a GitHub release with a `v<version>` tag, and its notes are this file's entry for that version. `make release` creates it from a clean, pushed master HEAD whose Tests workflow passed, then moves `stable` to it.

### Upgrade notes

- If you installed from the git URL without `@stable` (the README said so for a few hours on 2026-10-05), that install follows master. Run `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable` once; `--force` is not needed. After that, `uv tool upgrade superclaude` stays on releases.
- Installed content changed only in the version line of `/sc:sc`. `superclaude update --scope <scope>` refreshes it for each installed scope; skip scopes that `superclaude doctor --scope <scope>` reports as not installed, because `update` creates an install where none exists.

## [4.20.0+ajitta] - 2026-10-04

### Added

- Every `/sc:` command that takes flags has a `<flags>` section with one line per command-local flag, which defines the flag or points to the step or section that does. Flags that had no definition before include `/sc:cleanup --safe` / `--aggressive`, `/sc:estimate --type` / `--breakdown`, `/sc:explain --level`, `/sc:load --type`, `/sc:roadmap --strategy`, `/sc:troubleshoot --trace`, `/sc:improve --interactive`, `/sc:pm --verbose` and `/sc:recommend --estimate` / `--alternatives`. `/sc:build --clean` deletes only the output directory of the chosen `--type` (`dist-dev/`, `dist/` or `dist-test/`) and never runs `git clean`. `/sc:cleanup --dry-run` is a read-only preview for any `--type`.

### Changed

- `--safe` on `/sc:cleanup`, `/sc:improve` and `/sc:implement` follows one rule: changes that reach exported functions, config files or shared modules are not applied without approval. `/sc:cleanup --safe` changes only the safe tier (unused imports, dead variables, empty files) and lists the rest; `/sc:improve --safe` lists such changes as proposals; `/sc:implement --safe` shows each one and waits for approval. None of them is the global `--safe-mode`.
- `/sc:test --fix` is defined: on a failing test it finds the root cause the way `/sc:troubleshoot --type bug` would, fixes the code and re-runs the tests, and never edits a test only to make it pass.
- Commands that reuse a global flag name define their own meaning in `<flags>` and say it is unrelated to the global flag: `/sc:implement --plan <path>`, `/sc:review --scope pr|diff|file|branch|plan|design|spec`, `/sc:reflect --validate`, `/sc:auto-improve --scope <glob>` and `/sc:spec-panel --focus implementability|simplicity|reliability|testing|observability`. `/sc:analyze --focus` takes the global domains plus `rules`. `/sc:business-panel --focus <domain>` picks the experts the Analyze step applies and is ignored when `--experts` or `--all-experts` is given.

### Removed

- The SessionStart state sweep no longer deletes the `hook_executions*` and `current_session*` files left in `.superclaude_hooks/` by the `hook_tracker` hook removed in 4.19.0.

### Fixed

- The prompt hook (`context_loader`) no longer reports a flag that a `/sc:` command defines in its `<flags>` section as a typo of a global flag, and no longer injects the global directive for a flag name the command redefines. `/sc:implement auth --safe` drew "Did you mean: --safe-mode?", and `/sc:implement --plan docs/plans/x.md` drew the global `--plan` directive (write a 5-line plan and wait), although that `--plan` takes a plan file to follow.
- `/sc:troubleshoot` without `--fix` stops after the Confirm step and proposes the fix; with `--fix` it runs the Test, Fix and Verify steps, and a fix in the approval-required tier of the auto-fix threshold still waits for confirmation. Before, the command's steps listed writing a failing test and applying the fix with no condition, and the `--fix` rule appeared only in the command description.
- An error-path example in `/sc:document` used `--detailed`, which the command does not accept; it now reads `--style detailed`.

### Upgrade notes

- Re-sync each scope you have installed: check with `superclaude doctor --scope <scope>`, then run `superclaude update --scope <scope>` (the same as `install --force`). The hook reads `<flags>` from the installed command files, so until they are refreshed `/sc:implement --safe` still draws the typo notice and `/sc:implement --plan <path>` still draws the global `--plan` directive. Run `update` only for installed scopes: it creates an install where none exists.
- Upgrading straight from 4.18.x or earlier, `hook_executions*` and `current_session*` files may remain in `.superclaude_hooks/`. Nothing reads them; delete them or leave them. `superclaude uninstall` removes the directory.

## [4.19.0+ajitta] - 2026-10-03

### Added

- Two portable Agent Skills under `portable-skills/`: `socratic-brainstorm` (3.2.0) and `socratic-elenchus` (1.2.0). `superclaude install` does not install them. Upload `portable-skills/releases/<skill>.zip` at claude.ai › Customize › Plugins, or in Claude Code run `/plugin marketplace add ajitta/superclaude` and then `/plugin install <skill>@ajitta-socratic`. `portable-skills/README.md` covers Codex and copy-in installs.

### Changed

- `superclaude doctor` runs five checks instead of six: the `Configuration` check is gone. With `--verbose` the version still shows in the details of the `superclaude on PATH` check. `pytest plugin loaded` only confirms that SuperClaude's `pytest11` entry point is registered.

### Removed

- `superclaude audit` and `make audit`. Use `superclaude verify-drift` (or `make verify-drift`) for install drift; in a checkout, `uv run pytest` covers the cross-reference and content checks `audit` ran.
- `superclaude agents` (`--list`, `--info`, `--tokens`), with no replacement. The installed agents are the `.md` files in the scope's `agents/` directory.
- `superclaude version`. Use `superclaude --version`, which prints `SuperClaude, version <x>`.
- The `--status` option of `superclaude mcp`. `superclaude mcp --list` shows whether each server is installed.
- The `make build-plugin`, `make sync-plugin-repo` and `make translate` targets, and `scripts/build_superclaude_plugin.py`. None worked from a plain checkout: `build-plugin` needed the already deleted `plugins/superclaude/` tree, `sync-plugin-repo` depended on it, and `translate` needed a locally built `neural-cli`. `make test-plugin` stays.
- Three lines of the SessionStart `session_init` hook output: `📊 Git: …` (Claude Code already supplies git status), `💡 Use /context to confirm token budget.`, and `📁 Multi-dir: N additional CLAUDE.md found` (shown only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`). The hook prints the PR-review status line, when there is one, and the install-status line.
- The once-per-session `<!-- N skills installed (...) -->` comment the `context_loader` hook added to context, and `CLAUDE_SHOW_SKILLS`, the variable that turned it off. `superclaude context explain` no longer prints its `skills:` line.
- `rich` from the runtime dependencies (nothing imported it); `black`, `pytest-benchmark` and `scipy` from the `dev` extra; and the `test` extra. Use `superclaude[dev]`.

### Fixed

- `superclaude insight list`, `query` and `stats` no longer need `jq`. Without `jq` on PATH they exited 1, which broke `/sc:insight --list`, `--query` and `--stats` and the dedup check `/sc:insight` runs before every capture. Output is unchanged, and a malformed line in `.claude/insights.jsonl` is skipped instead of aborting the read.

### Upgrade notes

- Update scripts and aliases that call a removed command: `superclaude audit` → `superclaude verify-drift` (plus `uv run pytest` in a checkout); `superclaude version` → `superclaude --version`, whose output reads `SuperClaude, version <x>` instead of `SuperClaude version <x>`; `superclaude mcp --status` → `superclaude mcp --list`. `superclaude agents` and the removed make targets have no replacement.
- `CLAUDE_SHOW_SKILLS` is no longer read; you can drop it from your environment.
- If your own code imports `rich` from the same environment, install it yourself. Request `superclaude[dev]` instead of `superclaude[test]`; a checkout's `uv pip install -e ".[dev]"` no longer installs `black`, `pytest-benchmark` or `scipy`.
- Hook changes apply as soon as the package is upgraded, because registered hooks run `superclaude hook <name>`. To refresh the installed command and agent files, check each installed scope with `superclaude doctor --scope <scope>` and run `superclaude update --scope <scope>`; for project or local scope, run it from the project directory.
- Leftover `current_session.txt` and `hook_executions.json` files from the removed hook tracker are deleted by the SessionStart state sweep once they have gone 7 days without changes. In 4.20.0 the sweep no longer does this; see that release.
- Contributors: `.pre-commit-config.yaml` is gone. If you ran `pre-commit install` in a checkout, run `pre-commit uninstall`.
