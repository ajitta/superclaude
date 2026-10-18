<div align="center">

# 🚀 superclaude

#### *A Claude Code content framework — fork-origin, now its own project*

<p>
  <img src="https://img.shields.io/badge/version-4.29.5-blue" alt="Version">
  <a href="https://github.com/ajitta/superclaude/actions/workflows/test.yml">
    <img src="https://github.com/ajitta/superclaude/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</p>

</div>

> **Origin & relationship to upstream.** `superclaude` started as a fork of [SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) (Kazuki Nakai, NomenAK, Mithun Gowda B). It has since diverged — different MCP set, insight pipeline, scope-explicit install, tightened workflow gates — and is **no longer a downstream of upstream**. The two projects share neither roadmap nor maintainers.

---

<div align="center">

## 📊 **At a glance**

| Commands | Agents | Modes | MCP Servers |
|:--------:|:------:|:-----:|:-----------:|
| **35**   | **24** | **6** | **3**       |
| Slash    | Domain-expert | Behavioral | Integrations |

</div>

35 slash commands cover the development lifecycle from brainstorming to deployment. 6 behavioral modes auto-load on matching flags and keywords.

---

## 🎯 **Overview**

`superclaude` is a **content framework** for Claude Code: a directory of markdown (commands, agents, output styles, modes, MCP docs, core rules) plus a small CLI / pytest plugin that installs that content into Claude Code's content directories — `~/.claude/` (user), `./.claude/` (project, committed), or `./.claude/` (local, personal — kept out of git through the clone's `.git/info/exclude`).

Claude Code reads those files at session start, which is how the framework changes its behavior. There is no runtime engine, no daemon, no proxy.

> **Disclaimer.** This project is not affiliated with or endorsed by Anthropic, nor by the upstream SuperClaude Framework. Claude Code is built and maintained by [Anthropic](https://www.anthropic.com/).

---

## ⚡ **Quick Installation**

### **Current Stable Version (v4.29.5)**

There are three ways to install, from quickest to most customizable:

1. **Quick install** (this section) runs the release as-is.
2. **[Clone install](#-clone-install)** runs your own copy from a local clone, so you can edit the commands, agents, modes and rules.
3. **[Fork install](#-fork-install-recommended)** is a clone install whose copy lives in your own GitHub fork. It is the recommended way to make the framework your own.

`superclaude` ships markdown content (commands, agents, modes, MCP docs, core rules, hooks) plus a small CLI that copies it into Claude Code's content directories.

#### **1. Install the CLI**

```bash
uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable
```

No clone needed. `stable` is the latest release; to pin one, replace `@stable` with its tag, `@v<version>` (see [Releases](https://github.com/ajitta/superclaude/releases)). If your shell then can't find `superclaude`, run `uv tool update-shell` and open a new terminal.

#### **2. Install framework content with `superclaude install`**

```bash
superclaude install                    # default: --scope user (~/.claude/, global)
superclaude install --scope project    # team-shared, committed to ./.claude/
superclaude install --scope local      # personal-in-team-repo (./.claude/, kept out of git via
                                       #   .git/info/exclude; settings.local.json + CLAUDE.local.md)
superclaude install --force            # overwrite an existing install
superclaude install -i                 # interactive wizard (scope → preview → confirm)
superclaude install --list             # show available components, install nothing
superclaude install --list-all         # show every component + its install status
```

What gets installed (per scope):

```
<scope>/
├── commands/sc/        # 35 slash commands (/sc:plan, /sc:implement, …)
├── agents/             # 24 agent definitions
├── output-styles/      # output styles (pick one via /config → Output style)
├── superclaude/        # core rules, modes, mcp docs
├── hooks/hooks.json    # SessionStart / PreCompact / SessionEnd / etc.
└── settings(.local).json  # framework hooks merged in (your existing hooks preserved)
```

Every hook command is `superclaude hook <name>` — no interpreter path, no script copy — so a project-scope `settings.json` is the same bytes on every machine and can be committed. A reinstall over an older release rewrites its `<python> …/<script>.py` registrations to that form. Runtime state (`.claude/.superclaude_hooks/`, pending insights) stays out of git through the clone's `.git/info/exclude`, never your `.gitignore`.

#### **3. Install MCP servers (optional)**

```bash
superclaude mcp                        # interactive picker (installs only what you pick; default scope: user)
superclaude mcp --list                 # list available servers
superclaude mcp --servers tavily playwright
superclaude mcp --scope project        # write to ./.mcp.json (team-shared)
superclaude mcp --scope local          # per-project block inside ~/.claude.json
```

#### **4. Verify**

```bash
superclaude install --list-all          # component-by-component status
superclaude doctor                      # pytest plugin, hooks, CLAUDE_SC import, `superclaude` on PATH
superclaude verify-drift                # detect drift between source and installed copy
superclaude --version
```

Restart Claude Code, then try a few:

- `/sc:brainstorm` — Socratic discovery for vague requests
- `/sc:plan` — Detailed TDD implementation plans
- `/sc:implement` — Code implementation
- `/sc:review` — Multi-dimensional review (code/plan/design)
- `/sc:research` — Deep web research (Tavily-enhanced)
- `/sc:insight` — Capture structured session insights to JSONL
- `/sc:help` — List all 35 commands

Not sure what to run next? Ask a side question with [`/btw`](https://code.claude.com/docs/en/interactive-mode). It answers from the conversation so far, works while Claude is still busy, and never enters the conversation history. It has no tools, so it answers only from what the session already holds:

```
/btw based on what we just did, which /sc command should I run next, and why?
```

To keep a command running until a result holds, put it in a [`/goal`](https://code.claude.com/docs/en/goal). `/goal` sets a completion condition, and Claude keeps working turn after turn until a separate model judges it met. The condition is also Claude's first instruction, so a command named in it runs as part of the goal:

```
/goal sc:review the current diff, fix every finding, and review again until it reports none
```

Run `/goal` alone to check progress, or `/goal clear` to stop early.

#### **Update**

```bash
uv tool upgrade superclaude            # pull the latest release
superclaude update                     # default: --scope user
superclaude update --scope project     # (update takes --scope only; use `install --force` to re-copy everything)
```

#### **Uninstall**

```bash
superclaude uninstall --dry-run        # preview, no changes
superclaude uninstall                  # default: --scope user, asks to confirm
superclaude uninstall -y               # skip confirmation
superclaude uninstall --scope project  # remove from ./.claude/
superclaude uninstall --scope local    # also removes CLAUDE.local.md + its .git/info/exclude block
superclaude uninstall --keep-settings  # leave settings.json hooks alone
superclaude uninstall --remove-mcp     # also unregister framework-installed MCP servers
                                       #   (default keeps them — they're shared with other tools)
uv tool uninstall superclaude          # finally, remove the CLI itself
```

The uninstall is marker-based: it removes only the hooks and the `@superclaude/CLAUDE_SC.md` import that the installer wrote. User-added hooks, MCP servers, and CLAUDE.md content are preserved unless you explicitly opt out.

#### **CLI scope summary**

| Command | Scopes | Default |
|---------|--------|---------|
| `superclaude install` / `update` / `uninstall` | `user`, `project`, `local` | `user` |
| `superclaude mcp` | `user`, `project`, `local` | `user` |

| Scope | Path | When to use |
|-------|------|-------------|
| `user` | `~/.claude/` | Personal global install (default — daily use) |
| `project` | `./.claude/` (committed) | Team-shared, checked into git |
| `local` | `./.claude/` (kept out of git via `.git/info/exclude`) | Personal install inside a team repo (uses `settings.local.json`, `CLAUDE.local.md`) |

### **Optional MCP servers**

The framework is fully functional without any MCP server. Each one adds a capability its flag switches on:

- **Tavily** — web search / extract / crawl / map / research. Recommended as Agent Skills (Tavily CLI `tvly init`, or `npx skills add https://github.com/tavily-ai/skills`); the MCP server is the optional in-conversation alternative (`--tavily`)
- **Context7** — official documentation lookup, enabled as a claude.ai connector rather than through `superclaude mcp` (`--c7`)
- **Playwright**, **Chrome DevTools** — browser automation and performance audits (`--play`, `--perf`)

Source of truth for each server's usage: `src/superclaude/mcp/MCP_*.md` and `src/superclaude/mcp/README.md`.

## 📥 **Clone install**

Run your own copy from a local clone of this repository and edit it. No GitHub account is needed, and every step needs only `git`, [uv](https://docs.astral.sh/uv/getting-started/installation/) and the `superclaude` CLI. To keep your copy on GitHub, use [Fork install](#-fork-install-recommended) instead.

#### **1. Clone the repository**

```bash
git clone -b stable https://github.com/ajitta/superclaude.git
cd superclaude
```

`stable` is the latest release.

#### **2. Set up the environment**

```bash
uv venv -p 3.13
uv pip install -e ".[dev]"
```

Don't run `uv sync`: it removes the dev tools installed above, and the tests stop running.

#### **3. Run the CLI from your clone**

```bash
uv tool install --force --editable .
```

`superclaude` now reads your clone, so later edits need no reinstall. Moving or deleting the clone breaks the CLI and its hooks. If you installed the release before, this replaces it. If your shell can't find `superclaude`, run `uv tool update-shell` and open a new terminal.

#### **4. Install the content**

```bash
superclaude install --scope user       # or, inside a project: --scope project / --scope local
```

The scopes are explained in the [CLI scope summary](#cli-scope-summary). Restart Claude Code afterwards.

#### **5. Edit, then sync**

Change the files under `src/superclaude/` (commands, agents, modes, rules, output styles), copy them into the scope you use, and restart Claude Code:

```bash
superclaude update --scope user
```

#### **6. Run the tests**

The markdown is tested too (counts, cross-references, structure), so run them after content edits as well:

```bash
uv run pytest
```

#### **7. Pull in new releases**

Commit your edits first. Then merge the new release, resolve any conflicts with your changes, reinstall the CLI in case dependencies changed, and refresh each scope you installed:

```bash
git pull --no-rebase origin stable
uv tool install --force --editable .
superclaude update --scope user
```

To remove everything, see [Uninstall](#uninstall). If you have `make`, `make deploy`, `make sync-user` and `make test` wrap these commands; see the `Makefile`.

**Files to read before you customize:**

| File | Purpose |
|------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Project-specific rules: env (UV), make targets, how to run the tests, git workflow |
| [`src/superclaude/ARCHITECTURE.md`](src/superclaude/ARCHITECTURE.md) | Content-framework taxonomy — directory roles, delivery pipelines, content types |
| [`src/superclaude/CLAUDE_SC.md`](src/superclaude/CLAUDE_SC.md) | The always-loaded import chain → `core/FLAGS.md`, `PRINCIPLES.md`, `RULES.md` |
| [`.claude/rules/`](.claude/rules) | Authoring specs for agents/commands/modes |
| [`.claude/rules/gotchas/`](.claude/rules/gotchas) | Project-specific traps (e.g. *do not Read sub-agent `*.output` files*) |
| [`SECURITY.md`](SECURITY.md) | Security disclosure policy |

> Claude Code auto-loads `CLAUDE.md` and the `core/` import chain at session start, so the rules apply to every interaction inside this repo.

## 🍴 **Fork install (recommended)**

A clone install whose copy lives in your own GitHub fork: your edits are backed up, and you can use the same copy on every machine. Follow [Clone install](#-clone-install) with these changes:

1. Before step 1, [fork the repository](https://github.com/ajitta/superclaude/fork) on GitHub. Copying only the `stable` branch, the default, is enough.
2. In step 1, clone your fork instead:

   ```bash
   git clone https://github.com/<your-account>/superclaude.git
   cd superclaude
   ```

3. After committing your edits, push them to your fork with `git push`.
4. In step 7, add this repository as `upstream` once, then pull new releases from it:

   ```bash
   git remote add upstream https://github.com/ajitta/superclaude.git   # once
   git pull --no-rebase upstream stable
   uv tool install --force --editable .
   superclaude update --scope user
   ```

---

## 🧭 **Workflows**

The framework's value comes from chaining commands. Each chain has gates: a step's output must be committed (or explicitly approved) before the next step runs. Pick the chain that matches the task's blast radius — don't pay `brainstorm`-level overhead for a typo, and don't skip `design` for a system rewrite.

#### By task size

| Tier | Trigger | Recommended chain |
|------|---------|-------------------|
| **Trivial** | Typo · 1-line fix · rename · obvious bug with known fix | Direct edit. No `/sc:*` needed. |
| **Small** | Single file · ≤ 50 added lines · clear scope | Direct request (or `/sc:improve`) with the global **`--plan`** (5-line plan, approve) → `/sc:test` |
| **Medium** | 3–10 files · multi-purpose · clear requirements | `/sc:plan` → `/sc:implement --plan` → `/sc:test` → `/sc:reflect` (optional: `/sc:intent` first) |
| **Large** | > 10 files · cross-cutting · ambiguous scope · new system | `/sc:intent` → `/sc:brainstorm` → `/sc:review --scope spec` → `/sc:design` → `/sc:plan` → `/sc:implement --plan` → `/sc:test` → `/sc:reflect` |

#### The full chain (large tasks)

```text
/sc:intent   →   /sc:brainstorm   →   /sc:review --scope spec   →   /sc:design   →   /sc:plan   →   /sc:implement --plan   →   /sc:test   →   /sc:reflect
   capture          discover           specify          gate              decompose       build (TDD)                 verify        learn
   (own words)      (Socratic)         (architecture)   (multi-lens)      (phases)        (per task)                  (baseline)    (capture)
```

| Step | Output | Hard gate before next step |
|------|--------|----------------------------|
| `/sc:intent` | `docs/features/<slug>/00-intent.md` — problem, proposed outcome, affected users and systems, constraints, open questions, in the requester's words | User approves the wording; committed before analysis starts |
| `/sc:brainstorm` | `docs/features/<slug>/01-discovery.md` (one-off: `docs/specs/<slug>-discovery-<user>-<date>.md`) | User approves discovery spec |
| `/sc:design` | `docs/features/<slug>/04-design.md` (one-off: `docs/specs/…-design-…md`) | Design committed (components pass the [R18] necessity test; Areas of concern resolved) |
| `/sc:review` | Multi-dimensional review of design/plan | Required — `/sc:brainstorm` hard-blocks `/sc:plan` until this runs |
| `/sc:plan` | `docs/features/<slug>/05-plan.md` (one-off: `docs/plans/…md`) — phased TDD tasks, file paths, verify cmds | Plan committed |
| `/sc:implement --plan` | Code + per-phase commits | Implementation complete; plan checkboxes and Deviations match the code |
| `/sc:test` | Test pass evidence (`42/42 pass, baseline 40`) | Real output, not predictions |
| `/sc:reflect` | Retrospective + insights captured to `.claude/insights.jsonl` | — |

#### Other common chains

| Goal | Chain |
|------|-------|
| **Investigate a bug** | `/sc:troubleshoot` → `/sc:analyze --focus <domain>` → `/sc:plan` → `/sc:implement --plan` → `/sc:test` |
| **Performance work** | `/sc:analyze --focus perf --scope module` → `/sc:improve --loop --focus perf` → `/sc:test` |
| **Security audit** | `/sc:analyze --focus security` → `/sc:review` → `/sc:improve --focus security` |
| **Refactor** | `/sc:analyze --focus quality` → `/sc:plan` → `/sc:improve --loop` → `/sc:test` |
| **External research** | `/sc:research --depth deep --tavily --c7` → `/sc:reflect` |
| **Codebase onboarding** | `/sc:load` → `/sc:index-repo` → `/sc:explain` |
| **Strategy / market** | `/sc:business-panel` → `/sc:reflect` |
| **End of branch** | `/sc:review` → `/sc:test` → `/sc:git` (commit + PR) |

#### Tips

- **Skip steps when the input already exists.** If you already have a written spec, jump straight to `/sc:plan`. The gates exist to prevent skipping *unfinished* work, not to force ceremony.
- **`--plan` flag** on `/sc:implement` makes it consume a committed plan document. Without `--plan`, it works from the latest message.
- **`/sc:review` scores two dimensions** — fidelity to the spec and quality of the artifact — and groups findings as Critical / Important / Suggestion. Treat its output as a checklist, not a verdict. `--audit-delegated` re-examines only the decisions the model made on your behalf.
- **`/sc:reflect` writes insights to `.claude/insights.jsonl`** which `/sc:load` later reads — over time the framework remembers what worked.

---

## 🙏 **Acknowledgements**

`superclaude` builds on the original [SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) by Kazuki Nakai, NomenAK, and Mithun Gowda B. To support that upstream project's authors directly, see their channels on the upstream repo — sponsorship goes to them, not to this fork.

This fork is a personal, opinionated reshape of the framework: different MCP set, insight pipeline, scope-explicit deploy, tightened workflow gates. It is **not** maintained by the upstream authors.

---

## 🎉 **What's new in this fork**

*An insight pipeline, scope-explicit deployment, and tightened brainstorm → plan → implement → review workflow gates.*

<div align="center">
<table>
<tr>
<td width="50%">

### 🛡️ **Hook-Enforced Safety**
Rules that must hold are enforced by hooks, not prose:
- **destructive_guard** → blocks force-push to `main`/`master`, asks on `reset --hard` / `clean -f` / `branch -D`
- **file_size_guard** → blocks unbounded `Read` on files ≥30KB
- **loop_guard** → circuit breaker on repeated failing edits

Every hook runs as `superclaude hook <name>` (a console entry, dispatched before the CLI loads), so hooks cost ~20 ms and `settings.json` carries no machine-specific bytes. Hooks merge into your `settings.json` — your existing hooks are preserved. See `docs/adr/0001-hooks-are-the-enforcement-boundary.md`.

</td>
<td width="50%">

### 🤖 **Smarter Agent System**
**24 specialized agents** with domain expertise:
- New: **insight-analyst**, **repo-index**, **self-review**, **simplicity-guide**, **technical-writer**, **project-initializer**, **verifier**
- Deep Research agent for autonomous web research
- Security/performance/quality engineers catch real issues
- Frontend / backend / system architect for design work
- Routing-overlap table ("Cross-Agent Conflict Resolution") in src/superclaude/agents/README.md

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP Server Integration**
**Curated and lean by default** (no token bloat):

```bash
# List available MCP servers
superclaude mcp --list

# Install specific servers
superclaude mcp --servers tavily playwright

# Interactive installation
superclaude mcp
```

**Available servers:**
- **Tavily** → Web search, extract, crawl, map, research (Deep Research). Recommended: **Agent Skills** via the Tavily CLI (`tvly init` installs them; skills only: `npx skills add https://github.com/tavily-ai/skills`) ([tavily-ai/skills](https://github.com/tavily-ai/skills) · [agent-skills docs](https://docs.tavily.com/documentation/agent-skills)). The `--tavily` MCP server is an optional in-conversation alternative exposing the same five operations as tools.
- **Context7** → Official documentation lookup. Enabled as a **claude.ai connector** (claude.ai → Settings → Connectors), not via `superclaude mcp` — `--c7` stays as an inline directive in `core/FLAGS.md`; no MCP doc ships for it.
- **Playwright** → Cross-browser automation & E2E testing (Microsoft official). MCP: [`microsoft/playwright-mcp`](https://github.com/microsoft/playwright-mcp); CLI + skill alternative preferred for coding agents: [`microsoft/playwright-cli`](https://github.com/microsoft/playwright-cli)
- **Chrome DevTools** → Performance, Lighthouse, accessibility, and memory profiling (CLS, LCP). Installed as Claude plugin from [`ChromeDevTools/chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp)

> Removed in this fork: Morphllm, Mindbase, Airis-Agent, Magic, AST-Grep (native Grep/Edit cover it), Sequential-Thinking (Claude 5-family models reason natively between tool calls — see [`docs/archive/codex/sequential-thinking-validity-2026-08-22/`](docs/archive/codex/sequential-thinking-validity-2026-08-22/)).

</td>
<td width="50%">

### 🎯 **Behavioral Modes**
**6 adaptive modes** for different contexts:
- **Brainstorming** → Socratic discovery for vague requests
- **Business Panel** → Multi-expert strategic analysis
- **Deep Research** → Autonomous web research
- **Token-Efficiency** → selective omission under context pressure (`--uc`): drop what does not change the next action, never compress what stays
- **Introspection** → Meta-cognitive analysis & error recovery
- **Verbalized Sampling** → Probability-weighted candidate distributions (`--vs`)

</td>
</tr>
<tr>
<td width="50%">

### 📓 **Insight Pipeline**
**`/sc:insight` + hook-driven harvest:**
- Per-project JSONL store at `.claude/insights.jsonl`
- `superclaude insight` CLI (append/list/query/stats/review/promote/discard)
- PreCompact / SessionEnd hooks auto-harvest pending insights
- Empty/non-string entries rejected at the writer boundary
- Searchable for human and tool analysis across sessions

</td>
<td width="50%">

### 🚦 **Tightened Workflow Gates**
**Brainstorm → Plan → Implement → Review:**
- `/sc:brainstorm` hard-blocks `/sc:plan` until `/sc:review` runs
- `/sc:review --audit-delegated` re-examines the decisions the model made on your behalf
- Plan default: phase framing; opt-in `--pr-bundle` for multi-PR
- `verified:` convention + SessionStart memory-staleness warning

</td>
</tr>
<tr>
<td width="50%">

### 📦 **Scope-Explicit Deployment**
**Separate CLI deploy from content sync:**
- `make deploy` — installs the CLI only (`uv tool install --force --editable .`)
- `make sync-user` / `sync-project` / `sync-local` — force-sync markdown content to chosen scope
- `make uninstall-user` / `uninstall-project` / `uninstall-local` — mirror targets
- `superclaude install/uninstall/update --scope user|project|local` — consistent flag across CLI

</td>
<td width="50%">

### 🪝 **Hook Subsystem**
**Settings-merge install + targeted hooks:**
- `install_settings.py` preserves user hooks via marker-based identification and rewrites a previous release's `<python> …/<script>.py` registrations to `superclaude hook <name>`
- `superclaude doctor` checks that the `superclaude` on PATH has the `hook` subcommand — the package whose hooks actually run
- `test_runner_hook` runs `uv run python -m pytest` (avoids the Windows uv canonicalize bug)
- SessionStart: install-status line, PR-review status and memory staleness warning
- PreCompact / SessionEnd: insight harvest
- Hooks are additive — your existing config survives reinstall

</td>
</tr>
</table>

</div>

---

## 🔬 **Deep Research**

*Autonomous web research aligned with the DR agent architecture — adaptive planning, multi-hop reasoning, confidence-scored synthesis.*

<div align="center">
<table>
<tr>
<td width="50%">

### 🎯 **Adaptive Planning**
**Three intelligent strategies:**
- **Planning-Only**: Direct execution for clear queries
- **Intent-Planning**: Clarification for ambiguous requests
- **Unified**: Collaborative plan refinement (without --strategy, the strategy is chosen by query clarity: clear → planning, ambiguous → intent, complex → unified)

</td>
<td width="50%">

### 🔄 **Multi-Hop Reasoning**
**Up to 5 iterative searches:**
- Entity expansion (Paper → Authors → Works)
- Concept deepening (Topic → Details → Examples)
- Temporal progression (Current → Historical)
- Causal chains (Effect → Cause → Prevention)

</td>
</tr>
<tr>
<td width="50%">

### 📊 **Quality Scoring**
**Confidence-based validation:**
- Source credibility assessment (0.0-1.0)
- Coverage completeness tracking
- Synthesis coherence evaluation
- Minimum threshold: 0.6, Target: 0.8

</td>
<td width="50%">

### 🧠 **Cross-Session Memory**
**Research memory across sessions:**
- Findings and query formulations saved with `/sc:save`
- Recalled by `/sc:load` at the next session start
- Reflection after every hop: assess quality, find gaps, replan
- Saved to `.claude/memories/` (committed) and Claude auto memory

</td>
</tr>
</table>

### **Research Command Usage**

```bash
# Basic research with automatic depth
/sc:research "latest AI developments 2026"

# Controlled depth — pass flags after the query
/sc:research "quantum computing breakthroughs" --depth exhaustive

# Strategy selection: planning | intent | unified (default: chosen by query clarity)
/sc:research "market analysis" --strategy planning

# Pick the sources explicitly
/sc:research "React patterns" --tavily --c7
```

### **Research Depth Levels**

| Depth | Sources | Hops | Time | Confidence target | Best For |
|:-----:|:-------:|:----:|:----:|:-----------------:|----------|
| **Quick** | 10 | 1 | ~2min | 0.6 | Quick facts, simple queries |
| **Standard** | 20 | 3 | ~5min | 0.7 | General research (default) |
| **Deep** | 40 | 4 | ~8min | 0.8 | Comprehensive analysis |
| **Exhaustive** | 50+ | 5 | ~10min | 0.9 | Academic-level research |

Profiles are defined in [`modes/RESEARCH_CONFIG.md`](src/superclaude/modes/RESEARCH_CONFIG.md).

### **Integrated Tool Orchestration**

The Deep Research system intelligently coordinates multiple tools:
- **Tavily** (Agent Skills; MCP optional): Primary web search and discovery
- **Playwright MCP**: Complex content extraction
- **Context7** (claude.ai connector): Technical documentation lookup

</div>

---

## 📚 **References**

> `docs/archive/` holds the upstream-derived legacy tree and is not maintained. The rest of `docs/` — `features/`, `adr/`, `research/`, `agents/` — is this project's own. The table below names the source of truth per topic.

| Topic | Source of truth |
|-------|-----------------|
| Architecture & directory roles | [`src/superclaude/ARCHITECTURE.md`](src/superclaude/ARCHITECTURE.md) |
| Project rules, build & test loop | [`CLAUDE.md`](CLAUDE.md) |
| Project-specific gotchas | [`.claude/rules/gotchas/`](.claude/rules/gotchas) |
| Slash commands (35) | [`src/superclaude/commands/`](src/superclaude/commands) · `superclaude install --list-all` |
| Orchestration commands — `/sc:agent` vs `/sc:pm` vs `/sc:task` | [`docs/reports/ORCHESTRATION_COMMANDS.md`](docs/reports/ORCHESTRATION_COMMANDS.md) |
| Agents (24) | [`src/superclaude/agents/`](src/superclaude/agents) |
| Modes (6) | [`src/superclaude/modes/`](src/superclaude/modes) |
| MCP servers (3) | [`src/superclaude/mcp/`](src/superclaude/mcp) |
| Hooks (registry + scripts) | [`src/superclaude/cli/hook_dispatch.py`](src/superclaude/cli/hook_dispatch.py) · [`src/superclaude/hooks/hooks.json`](src/superclaude/hooks/hooks.json) · [`src/superclaude/scripts/`](src/superclaude/scripts) |
| Architecture decisions | [`docs/adr/`](docs/adr) |
| Feature work (discovery → plan → retrospective) | [`docs/features/`](docs/features) |
| Agent conventions (issue tracker, triage labels, domain docs) | [`docs/agents/`](docs/agents) |
| Core rules (always-loaded) | [`FLAGS.md`](src/superclaude/core/FLAGS.md) · [`PRINCIPLES.md`](src/superclaude/core/PRINCIPLES.md) · [`RULES.md`](src/superclaude/core/RULES.md) |
| Authoring specs for new content | [`.claude/rules/`](.claude/rules) |
| Health & drift checks | `superclaude doctor` · `superclaude verify-drift` · `superclaude context explain` / `reset` |

---

## 🚩 **Flags**

Flags are behavioral hints that any `/sc:*` prompt accepts. The model reads them inline — no setup, no separate config. SSOT: [`src/superclaude/core/FLAGS.md`](src/superclaude/core/FLAGS.md).

#### Modes — switch the conversational stance

| Flag | When to use | Effect |
|------|-------------|--------|
| `--brainstorm` | Vague request, "maybe", unclear scope | Collaborative discovery, probing questions before code |
| `--research` | Need evidence, citations, external knowledge | Systematic investigation, evidence-based reasoning |
| `--business-panel` | Strategy/market/competitive analysis | Multi-expert business analysis & synthesis |
| `--introspect` | Stuck, error recovery, "why is it doing X?" | Surfaces decision logic, assumptions and alternatives (🎯⚡📊💡 markers) |
| `--token-efficient` / `--uc` | Context ≥ 60 % or large ops (auto with `--safe-mode`) | Selective omission — drop what does not change the next action; never compress what stays |
| `--vs [standard\|cot\|multi]` | "Multiple perspectives", brainstorm options | Verbalized sampling — probability-weighted candidates. Sub-params: `[k:3-7] [tau:0.01-0.20] [turns:2-5] [no-synthesis]` |

#### MCP servers — opt in or out per turn

| Flag | Server | Use for |
|------|--------|---------|
| `--c7` / `--context7` | Context7 | Imports, frameworks, official docs |
| `--play` / `--playwright` | Playwright | Browser testing, E2E, visual diffs |
| `--perf` / `--devtools` | Chrome DevTools | Perf audit, CLS, LCP, metrics |
| `--tavily` | Tavily | Web search, real-time info, parallel queries |
| `--frontend-verify` | Combined | Playwright + DevTools (UI debug) |
| `--all-mcp` / `--no-mcp` | — | Enable all / disable all (perf priority) |

#### Execution — control how work is done

| Flag | Effect |
|------|--------|
| `--delegate [auto\|files\|folders]` | Sub-agent parallel delegation. Decision matrix: [`RULES_DELEGATION.md`](src/superclaude/core/rules/RULES_DELEGATION.md) `<sub_agent_decision>` |
| `--concurrency [n]` | Batch independent tool calls (1–15) into a single message |
| `--loop` | Iterative improvement — repeat until no meaningful improvement found |
| `--iterations [n]` | Fixed iteration count — exactly N cycles, with per-iteration delta report |
| `--plan` | 5-line plan (goal · approach · files · risks · verification) before execution |
| `--validate` | Pre-execution risk assessment (production, irreversible/destructive, migrations, shared infra) |
| `--safe-mode` | Max validation, conservative behavior, auto `--uc` |
| `--verbose-context` | Force full `.md` injection (bypass short-instruction map) |

#### Scope & focus

| Flag | Values |
|------|--------|
| `--scope` | `file` · `module` · `project` · `system` |
| `--focus` | `perf` · `security` · `quality` · `arch` · `a11y` · `testing` |

> **Priority when flags conflict:** `--safe-mode` > `--validate` > optimization · explicit user flags > auto-detection · `--no-mcp` overrides individual MCP flags.

> **Retired flags** (`--think*`, `--parallel`, `--seq` / `--sequential`) get a redirect notice rather than a rewrite. An unrecognized flag is matched by difflib similarity — not edit distance — first against retired names (cutoff 0.8), then against valid ones (cutoff 0.6), and the closest become a suggestion comment. Nothing is silently rewritten: `context_loader.py` ships an empty alias table.

#### Examples

```bash
/sc:research "Rust async runtime tradeoffs" --depth deep --tavily --c7
/sc:implement --plan docs/features/user-export/05-plan.md --validate --delegate auto
/sc:analyze src/auth/ --focus security --scope module
/sc:improve src/api/handlers.py --loop --iterations 3
/sc:brainstorm "should we migrate to gRPC?" --vs multi
```

---

## ⚖️ **License**

MIT — see [`LICENSE`](LICENSE).

---

## 📋 **All Commands**

<details>
<summary><b>Click to expand full command list</b></summary>

### 🧠 Planning & Design
- `/sc:intent` — Capture a request in the requester's own words before analysis
- `/sc:brainstorm` — Structured brainstorming through Socratic dialogue
- `/sc:design` — System architecture, APIs, component interfaces
- `/sc:plan` — Detailed implementation plans with TDD tasks
- `/sc:estimate` — Relative effort sizing (S/M/L/XL)
- `/sc:spec-panel` — Multi-expert specification review
- `/sc:roadmap` — Phased implementation workflow from a PRD or feature doc

### 💻 Development
- `/sc:implement` — Code implementation
- `/sc:build` — Build workflows
- `/sc:improve` — Code improvements
- `/sc:cleanup` — Refactoring & dead-code removal
- `/sc:explain` — Code explanation

### 🧪 Testing & Quality
- `/sc:test` — Run tests with coverage and quality reporting
- `/sc:analyze` — Code analysis (quality, security, perf, arch)
- `/sc:troubleshoot` — Diagnose & resolve issues
- `/sc:reflect` — Task retrospectives
- `/sc:review` — Multi-dimensional review of work products

### 📚 Documentation
- `/sc:document` — Doc generation
- `/sc:promote-feature` — Consolidate standalone docs into a feature folder
- `/sc:help` — Command help

### 🔧 Version Control
- `/sc:git` — Git operations with intelligent commits

### 📊 Project Management
- `/sc:pm` — Project management & sub-agent orchestration
- `/sc:task` — Task tracking
- `/sc:auto-improve` — Autonomous metric-driven improvement loop

> `/sc:pm`, `/sc:task` and `/sc:agent` overlap on "analyze → delegate → track". Which one to use, with examples: [Orchestration commands: `/sc:agent` vs `/sc:pm` vs `/sc:task`](docs/reports/ORCHESTRATION_COMMANDS.md).

### 🔍 Research & Analysis
- `/sc:research` — Deep web research
- `/sc:business-panel` — Multi-expert business analysis

### 🗂️ Session & Memory
- `/sc:load` — Load session context (`.claude/memories/` + auto memory)
- `/sc:save` — Save session context
- `/sc:insight` — Capture structured insights to JSONL

### 🎯 Utilities
- `/sc:agent` — Session controller: investigate → implement → review orchestration ([vs `/sc:pm` / `/sc:task`](docs/reports/ORCHESTRATION_COMMANDS.md))
- `/sc:init` — Interactive project environment setup
- `/sc:index` / `/sc:index-repo` — Project docs and a compact repo index for cheap navigation
- `/sc:recommend` — Command recommendation engine
- `/sc:select-tool` — Intelligent MCP tool selection

### ✍️ Skills
- `/sc-author` — Write or revise a file Claude reads as instructions (skill, subagent, command, output style, CLAUDE.md, `.claude/rules`, and others). It follows your project's existing documents, proposes no-op and harmful sentences for removal with evidence, and writes only after you approve the diff. The body follows your project's format for that type; `--md` or `--xml` chooses one. User-invoked only; installed to `.claude/skills/sc-author/`.
- `superclaude author-check <path>` — The validator `/sc-author` runs: frontmatter fields, references, XML structure, broken pointers; `--with <file>` adds the documents loaded together for conflict and duplicate checks. Exit 1 on errors.
- `/sc-prompt` — Rewrite a prompt for Claude Opus 5.5 / Sonnet 5.5 / Opus 5 / Fable 5.1: strip folklore that degrades the target, apply its model-specific deltas, mark missing context as `[FILL: …]` placeholders. Replaces the `prompt` slash command of earlier releases. On an Opus 5.5 or Sonnet 5.5 session, pass a prompt that asks for written-out reasoning as a file path: pasted inline, it can be declined before the skill runs. Installed to `.claude/skills/sc-prompt/`.

**Source files:** [`src/superclaude/commands/`](src/superclaude/commands) — each command is a single markdown file with frontmatter. After install, run `superclaude install --list-all` for a full inventory.

</details>
