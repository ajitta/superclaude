<div align="center">

# 🚀 superclaude

#### *A Claude Code content framework — fork-origin, now its own project*

<p>
  <img src="https://img.shields.io/badge/version-4.5.1+ajitta-blue" alt="Version">
  <a href="https://github.com/ajitta/superclaude/actions/workflows/test.yml">
    <img src="https://github.com/ajitta/superclaude/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

</div>

> **Origin & relationship to upstream.** `superclaude` started as a fork of [SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) (Kazuki Nakai, NomenAK, Mithun Gowda B). It has since diverged — different MCP set, procedural skills system, insight pipeline, scope-explicit install, tightened workflow gates — and is **no longer a downstream of upstream**. The two projects share neither roadmap nor maintainers.

---

<div align="center">

## 📊 **At a glance**

| Commands | Agents | Modes | MCP Servers | Skills |
|:--------:|:------:|:-----:|:-----------:|:------:|
| **33**   | **23** | **7** | **8**       | **5**  |
| Slash    | Domain-expert | Behavioral | Integrations | Procedural |

</div>

33 slash commands cover the development lifecycle from brainstorming to deployment. 5 procedural skills (`confidence-check`, `ship`, `simplicity-coach`, `verbalized-sampling`, `finishing-a-development-branch`) auto-load on matching prompts.

---

## 🎯 **Overview**

`superclaude` is a **content framework** for Claude Code: a directory of markdown (commands, agents, modes, MCP docs, core rules) plus a small CLI / pytest plugin that installs that content into Claude Code's content directories — `~/.claude/` (user), `./.claude/` (project), or `./.claude/` (local, gitignored).

Claude Code reads those files at session start, which is how the framework changes its behavior. There is no runtime engine, no daemon, no proxy.

> **Disclaimer.** This project is not affiliated with or endorsed by Anthropic, nor by the upstream SuperClaude Framework. Claude Code is built and maintained by [Anthropic](https://www.anthropic.com/).

---

## 📖 **For developers & contributors**

**Essential reading when working in this repo:**

| File | Purpose |
|------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Project-specific rules: env (UV), make targets, test baseline (1,628 passing), git workflow |
| [`src/superclaude/ARCHITECTURE.md`](src/superclaude/ARCHITECTURE.md) | Content-framework taxonomy — directory roles, delivery pipelines, content types |
| [`src/superclaude/CLAUDE_SC.md`](src/superclaude/CLAUDE_SC.md) | The always-loaded import chain → `core/FLAGS.md`, `PRINCIPLES.md`, `RULES.md` |
| [`.claude/rules/`](.claude/rules) | Authoring specs for agents/commands/skills/modes |
| [`.claude/rules/gotchas/`](.claude/rules/gotchas) | Project-specific traps (e.g. *do not Read sub-agent `*.output` files*) |
| [`SECURITY.md`](SECURITY.md) | Security disclosure policy |

> Claude Code auto-loads `CLAUDE.md` and the `core/` import chain at session start, so the rules apply to every interaction inside this repo.

## ⚡ **Quick Installation**

### **Current Stable Version (v4.5.1+ajitta)**

`superclaude` ships markdown content (commands, agents, modes, MCP docs, core rules, hooks, skills) plus a small CLI that copies it into Claude Code's content directories.

#### **1. Install the CLI**

```bash
git clone https://github.com/ajitta/superclaude.git
cd superclaude

# Editable uv tool install — `superclaude` becomes available globally.
make deploy
# Equivalent without make:
# uv tool install --force --editable .
```

#### **2. Install framework content with `superclaude install`**

```bash
superclaude install                    # default: --scope user (~/.claude/, global)
superclaude install --scope project    # team-shared, committed to ./.claude/
superclaude install --scope local      # personal-in-team-repo (./.claude/, gitignored,
                                       #   uses settings.local.json + CLAUDE.local.md)
superclaude install --force            # overwrite an existing install
superclaude install -i                 # interactive wizard (scope → preview → confirm)
superclaude install --list             # show available components, install nothing
superclaude install --list-all         # show every component + its install status
```

What gets installed (per scope):

```
<scope>/
├── commands/sc/        # 33 slash commands (/sc:plan, /sc:implement, …)
├── agents/             # 23 agent definitions
├── skills/             # 5 procedural skills
├── superclaude/        # core rules, modes, mcp docs, scripts
├── hooks/hooks.json    # SessionStart / PreCompact / SessionEnd / etc.
└── settings(.local).json  # framework hooks merged in (your existing hooks preserved)
```

#### **3. Install MCP servers (optional)**

```bash
superclaude mcp                        # interactive picker (default scope: user)
superclaude mcp --list                 # list available servers
superclaude mcp --servers tavily context7
superclaude mcp --scope project        # write to ./.mcp.json (team-shared)
superclaude mcp --scope local          # write to ~/.claude.json local block
```

#### **4. Verify**

```bash
superclaude install --list-all          # component-by-component status
superclaude doctor                      # health check
superclaude verify-drift                # detect drift between source and installed copy
superclaude version
```

Restart Claude Code, then try a few:

- `/sc:brainstorm` — Socratic discovery for vague requests
- `/sc:plan` — Detailed TDD implementation plans
- `/sc:implement` — Code implementation
- `/sc:review` — Multi-dimensional review (code/plan/design)
- `/sc:research` — Deep web research (Tavily-enhanced)
- `/sc:insight` — Capture structured session insights to JSONL
- `/sc` — List all 33 commands

#### **Update**

```bash
superclaude update                     # default: --scope user
superclaude update --scope project
superclaude update --force             # re-copy even unchanged files
```

#### **Uninstall**

```bash
superclaude uninstall --dry-run        # preview, no changes
superclaude uninstall                  # default: --scope user, asks to confirm
superclaude uninstall -y               # skip confirmation
superclaude uninstall --scope project  # remove from ./.claude/
superclaude uninstall --scope local    # also removes CLAUDE.local.md + cleans .gitignore
superclaude uninstall --keep-settings  # leave settings.json hooks alone
superclaude uninstall --remove-mcp     # also unregister framework-installed MCP servers
                                       #   (default keeps them — they're shared with other tools)
```

The uninstall is marker-based: it removes only the hooks and the `@superclaude` import that the installer wrote. User-added hooks, MCP servers, and CLAUDE.md content are preserved unless you explicitly opt out.

#### **CLI scope summary**

| Command | Scopes | Default |
|---------|--------|---------|
| `superclaude install` / `update` / `uninstall` | `user`, `project`, `local` | `user` |
| `superclaude install-skill` | `user`, `project` | `user` |
| `superclaude mcp` | `user`, `project`, `local` | `user` |

| Scope | Path | When to use |
|-------|------|-------------|
| `user` | `~/.claude/` | Personal global install (default — daily use) |
| `project` | `./.claude/` (committed) | Team-shared, checked into git |
| `local` | `./.claude/` (gitignored) | Personal install inside a team repo (uses `settings.local.json`, `CLAUDE.local.md`) |

**For contributors/developers:**
```bash
# Initial setup (editable mode for development)
uv pip install -e ".[dev]"

# Development cycle
uv run superclaude install --list-all  # Test changes immediately
uv run pytest tests/ -v                 # Run tests

# Deploy CLI as a global uv tool (editable). Content sync is a separate step.
make deploy

# Sync framework content to a scope (force-sync — for headless `claude -p`)
make sync-user      # → ~/.claude/        (global, recommended for daily use)
make sync-project   # → ./.claude/        (team-shared, committed)
make sync-local     # → ./.claude/        (local-only, gitignored)

# Verify installation
uv tool list              # List installed tools
which superclaude         # Check install path (Linux/Mac)
where superclaude         # Check install path (Windows)
```

| Stage | Command | Description |
|-------|---------|-------------|
| Dev/Test | `uv run superclaude ...` | Test in repo (editable) |
| Deploy CLI | `make deploy` | `uv tool install --force --editable .` |
| Sync content | `make sync-user` / `sync-project` / `sync-local` | Force-sync markdown/scripts to chosen scope |
| Use | `superclaude ...` | Run from anywhere |
| Uninstall | `make uninstall-user` / `uninstall-project` / `uninstall-local` | Scope-explicit removal |

### **Enhanced Performance (Optional MCPs)**

For **2-3x faster** execution and **30-50% fewer tokens**, optionally install MCP servers:

```bash
# Optional MCP servers for enhanced performance:
# - Serena: Semantic code understanding (2-3x faster symbol ops)
# - Sequential: Token-efficient multi-step reasoning (30-50% fewer tokens)
# - Tavily: Web search for Deep Research
# - Context7: Official documentation lookup
# - AST-Grep: Tree-sitter structural code search

# Note: Error learning available via built-in ReflexionMemory (no installation required)
# Source-of-truth for MCP docs: src/superclaude/MCP/MCP_*.md
```

**Performance Comparison:**
- **Without MCPs**: Fully functional, standard performance ✅
- **With MCPs**: 2-3x faster, 30-50% fewer tokens ⚡

### **Tavily Agent Skills (Optional CLI Enhancement)**

`superclaude` includes **Tavily MCP** for in-conversation web search. For advanced use cases (saving to local files, domain/time filtering, pipeline composition), optionally install the [Tavily Agent Skills](https://github.com/tavily-ai/skills):

```bash
# Install Tavily Agent Skills (requires Tavily CLI)
curl -fsSL https://cli.tavily.com/install.sh | bash
tvly login --api-key tvly-YOUR_KEY

# Install skills into Claude Code
npx skills add https://github.com/tavily-ai/skills
```

**When to use which:**

| Scenario | Tool | Why |
|----------|------|-----|
| In-conversation search | Tavily **MCP** (default) | Low latency, structured output, parallel queries |
| Agent-driven research (`/sc:research`) | Tavily **MCP** | Integrated with deep-researcher agent |
| Save docs to local files | Tavily **CLI** (`tvly crawl --output-dir`) | File output not available via MCP |
| Domain/time filtering | Tavily **CLI** (`tvly search --include-domains --time-range`) | Advanced filters CLI-only |
| Pipeline composition | Tavily **CLI** (`tvly search --json \| jq`) | Composable with shell tools |

> **Recommended setup:** Keep both — Tavily MCP handles 90% of searches automatically. The CLI activates only when its unique capabilities are needed.

---

## 🧭 **Workflows**

The framework's value comes from chaining commands. Each chain has gates: a step's output must be committed (or explicitly approved) before the next step runs. Pick the chain that matches the task's blast radius — don't pay `brainstorm`-level overhead for a typo, and don't skip `design` for a system rewrite.

#### By task size

| Tier | Trigger | Recommended chain |
|------|---------|-------------------|
| **Trivial** | Typo · 1-line fix · rename · obvious bug with known fix | Direct edit. No `/sc:*` needed. |
| **Small** | Single file · ≤ 50 added lines · clear scope | `/sc:implement` (or `/sc:improve`) **`--plan`** → `/sc:test` |
| **Medium** | 3–10 files · multi-purpose · clear requirements | `/sc:plan` → `/sc:implement --plan` → `/sc:test` → `/sc:reflect` |
| **Large** | > 10 files · cross-cutting · ambiguous scope · new system | `/sc:brainstorm` → `/sc:design` → `/sc:review` → `/sc:plan` → `/sc:implement --plan` → `/sc:test` → `/sc:reflect` |

#### The full chain (large tasks)

```text
/sc:brainstorm   →   /sc:design   →   /sc:review   →   /sc:plan   →   /sc:implement --plan   →   /sc:test   →   /sc:reflect
   discover           specify          gate              decompose       build (TDD)                 verify        learn
   (Socratic)         (architecture)   (multi-lens)      (phases)        (per task)                  (baseline)    (capture)
```

| Step | Output | Hard gate before next step |
|------|--------|----------------------------|
| `/sc:brainstorm` | `docs/specs/<topic>-discovery-…md` | User approves discovery spec |
| `/sc:design` | `docs/specs/<topic>-design-…md` | Design committed (components pass [R18] necessity test) |
| `/sc:review` | Multi-dimensional review of design/plan | Required — `/sc:brainstorm` hard-blocks `/sc:plan` until this runs |
| `/sc:plan` | `docs/plans/<topic>-…md` (phased TDD tasks, file paths, verify cmds) | Plan committed |
| `/sc:implement --plan` | Code + per-phase commits | Implementation complete |
| `/sc:test` | Test pass evidence (`42/42 pass, baseline 40`) | Real output, not predictions |
| `/sc:reflect` | Retrospective + insights captured to `.claude/insights.jsonl` | — |

#### Other common chains

| Goal | Chain |
|------|-------|
| **Investigate a bug** | `/sc:troubleshoot` → `/sc:analyze --focus <domain>` → `/sc:implement --plan` → `/sc:test` |
| **Performance work** | `/sc:analyze --focus perf --scope module` → `/sc:improve --loop --p=perf` → `/sc:test` |
| **Security audit** | `/sc:analyze --focus security` → `/sc:review` → `/sc:improve --p=sec` |
| **Refactor** | `/sc:analyze --focus quality` → `/sc:plan` → `/sc:improve --loop` → `/sc:test` |
| **External research** | `/sc:research --depth deep --tavily --c7` → `/sc:reflect` |
| **Codebase onboarding** | `/sc:load` → `/sc:index-repo` → `/sc:explain` |
| **Strategy / market** | `/sc:business-panel` → `/sc:reflect` |
| **End of branch** | `/sc:review` → `/sc:test` → `/sc:git` (commit) → `ship` skill (PR) |

#### Tips

- **Skip steps when the input already exists.** If you already have a written spec, jump straight to `/sc:plan`. The gates exist to prevent skipping *unfinished* work, not to force ceremony.
- **`--plan` flag** on `/sc:implement` makes it consume a committed plan document. Without `--plan`, it works from the latest message.
- **`/sc:review` runs many lenses in parallel** (correctness, scope, risk, alignment). Treat its output as a checklist, not a verdict.
- **`/sc:reflect` writes insights to `.claude/insights.jsonl`** which `/sc:load` later reads — over time the framework remembers what worked.

---

## 🙏 **Acknowledgements**

`superclaude` builds on the original [SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) by Kazuki Nakai, NomenAK, and Mithun Gowda B. To support that upstream project's authors directly, see their channels on the upstream repo — sponsorship goes to them, not to this fork.

This fork is a personal, opinionated reshape of the framework: different MCP set, skills system, insight pipeline, scope-explicit deploy, tightened workflow gates. It is **not** maintained by the upstream authors.

---

## 🎉 **What's new in v4.5+ajitta**

*Procedural skills, an insight pipeline, scope-explicit deployment, and tightened brainstorm → plan → implement → review workflow gates.*

<div align="center">
<table>
<tr>
<td width="50%">

### 🧩 **Procedural Skills System**
**5 auto-loaded skills** that fire on matching prompts:
- **confidence-check** → Pre-implementation validation gate
- **simplicity-coach** → Orient-Step-Learn discipline, anti over-engineering
- **verbalized-sampling** → Probability-weighted candidate generation (`--vs`)
- **ship** / **finishing-a-development-branch** → End-of-branch workflow

Skills live under `Skills/<name>/SKILL.md` and load via Claude Code's native skill loader — no boilerplate.

</td>
<td width="50%">

### 🤖 **Smarter Agent System**
**23 specialized agents** with domain expertise:
- New: **insight-analyst**, **repo-index**, **self-review**, **simplicity-guide**, **technical-writer**, **project-initializer**
- Deep Research agent for autonomous web research
- Security/performance/quality engineers catch real issues
- Frontend / backend / system architect for design work
- Single-trigger disambiguation matrix in RULES.md

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP Server Integration**
**8 curated servers** (lean default — no token bloat):

```bash
# List available MCP servers
superclaude mcp --list

# Install specific servers
superclaude mcp --servers tavily context7

# Interactive installation
superclaude mcp
```

**Available servers:**
- **Tavily** → Primary web search (Deep Research)
- **Context7** → Official documentation lookup
- **Sequential-Thinking** → Multi-step reasoning
- **Serena** → Session persistence & semantic code understanding
- **Playwright** → Cross-browser automation & E2E testing
- **Magic** → UI component generation (21st.dev)
- **Chrome DevTools** → Performance analysis (CLS, LCP)
- **AST-Grep** → Tree-sitter structural code search

> Removed in this fork: Morphllm, Mindbase, Airis-Agent (replaced by AstGrep + native ReflexionMemory).

</td>
<td width="50%">

### 🎯 **Behavioral Modes**
**7 adaptive modes** for different contexts:
- **Brainstorming** → Socratic discovery for vague requests
- **Business Panel** → Multi-expert strategic analysis
- **Deep Research** → Autonomous web research
- **Orchestration** → Efficient tool coordination
- **Token-Efficiency** → 30-50% context savings via symbol system
- **Task Management** → Systematic organization
- **Introspection** → Meta-cognitive analysis & error recovery

</td>
</tr>
<tr>
<td width="50%">

### 📓 **Insight Pipeline**
**`/sc:insight` + hook-driven harvest:**
- Per-project JSONL store at `.claude/insights.jsonl`
- Script-based writer (`scripts/insight_writer.py`) with append/promote
- PreCompact / SessionEnd hooks auto-harvest pending insights
- Empty/non-string entries rejected at the writer boundary
- Searchable for human and tool analysis across sessions

</td>
<td width="50%">

### 🚦 **Tightened Workflow Gates**
**Brainstorm → Plan → Implement → Review:**
- `/sc:brainstorm` hard-blocks `/sc:plan` until `/sc:review` runs
- Auto-trigger `/sc:review` on delegated decisions
- Plan default: phase framing; opt-in `--pr-bundle` for multi-PR
- `verified:` convention + SessionStart memory-staleness warning
- Per-skill canary manifests guard against trigger regressions

</td>
</tr>
<tr>
<td width="50%">

### 📦 **Scope-Explicit Deployment**
**Separate CLI deploy from content sync:**
- `make deploy` — installs the CLI only (`uv tool install --force --editable .`)
- `make sync-user` / `sync-project` / `sync-local` — force-sync markdown content to chosen scope
- `make uninstall-user` / `uninstall-project` / `uninstall-local` — mirror targets
- `superclaude install/uninstall/update --scope user|project` — consistent flag across CLI

</td>
<td width="50%">

### 🪝 **Hook Subsystem**
**Settings-merge install + targeted hooks:**
- `install_settings.py` preserves user hooks via marker-based identification
- `test_runner_hook` uses `python -m pytest` (avoids Windows uv canonicalize bug)
- SessionStart: git status + memory staleness warning
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
- **Unified**: Collaborative plan refinement (default)

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

### 🧠 **Case-Based Learning**
**Cross-session intelligence:**
- Pattern recognition and reuse
- Strategy optimization over time
- Successful query formulations saved
- Performance improvement tracking

</td>
</tr>
</table>

### **Research Command Usage**

```bash
# Basic research with automatic depth
/sc:research "latest AI developments 2026"

# Controlled depth — pass flags after the query
/sc:research "quantum computing breakthroughs" --depth exhaustive

# Strategy selection
/sc:research "market analysis" --strategy planning-only

# Domain-filtered research (uses Tavily MCP)
/sc:research "React patterns" --domains reactjs.org,github.com
```

### **Research Depth Levels**

| Depth | Sources | Hops | Time | Best For |
|:-----:|:-------:|:----:|:----:|----------|
| **Quick** | 5-10 | 1 | ~2min | Quick facts, simple queries |
| **Standard** | 10-20 | 3 | ~5min | General research (default) |
| **Deep** | 20-40 | 4 | ~8min | Comprehensive analysis |
| **Exhaustive** | 40+ | 5 | ~10min | Academic-level research |

### **Integrated Tool Orchestration**

The Deep Research system intelligently coordinates multiple tools:
- **Tavily MCP**: Primary web search and discovery
- **Playwright MCP**: Complex content extraction
- **Sequential MCP**: Multi-step reasoning and synthesis
- **Serena MCP**: Memory and learning persistence
- **Context7 MCP**: Technical documentation lookup
- **AST-Grep MCP**: Structural pattern search across discovered code samples

</div>

---

## 📚 **References**

> The legacy `docs/` tree is upstream-derived and **not maintained** in this fork. Treat the table below as the source of truth.

| Topic | Source of truth |
|-------|-----------------|
| Architecture & directory roles | [`src/superclaude/ARCHITECTURE.md`](src/superclaude/ARCHITECTURE.md) |
| Project rules, build & test loop | [`CLAUDE.md`](CLAUDE.md) |
| Project-specific gotchas | [`.claude/rules/gotchas/`](.claude/rules/gotchas) |
| Slash commands (33) | [`src/superclaude/Commands/`](src/superclaude/Commands) · `superclaude install --list-all` |
| Agents (23) | [`src/superclaude/Agents/`](src/superclaude/Agents) |
| Modes (7) | [`src/superclaude/Modes/`](src/superclaude/Modes) |
| MCP servers (8) | [`src/superclaude/MCP/`](src/superclaude/MCP) |
| Skills (5) | [`src/superclaude/Skills/`](src/superclaude/Skills) |
| Core rules (always-loaded) | [`FLAGS.md`](src/superclaude/core/FLAGS.md) · [`PRINCIPLES.md`](src/superclaude/core/PRINCIPLES.md) · [`RULES.md`](src/superclaude/core/RULES.md) |
| Authoring specs for new content | [`.claude/rules/`](.claude/rules) |
| Health & drift checks | `superclaude doctor` · `superclaude verify-drift` |

---

## 🚩 **Flags**

Flags are behavioral hints that any `/sc:*` prompt accepts. The model reads them inline — no setup, no separate config — and aliases (e.g. `--ultrathink` → `--seq`) are auto-corrected. SSOT: [`src/superclaude/core/FLAGS.md`](src/superclaude/core/FLAGS.md).

#### Modes — switch the conversational stance

| Flag | When to use | Effect |
|------|-------------|--------|
| `--brainstorm` | Vague request, "maybe", unclear scope | Collaborative discovery, probing questions before code |
| `--research` | Need evidence, citations, external knowledge | Systematic investigation, evidence-based reasoning |
| `--business-panel` | Strategy/market/competitive analysis | Multi-expert business analysis & synthesis |
| `--introspect` | Stuck, error recovery, "why is it doing X?" | Exposes thinking with 🤔🎯⚡📊💡 markers |
| `--task-manage` | >3 steps · >2 dirs · >3 files | Delegation + progressive enhancement |
| `--orchestrate` | Multi-tool, parallel, perf-sensitive | Tool-matrix optimization |
| `--token-efficient` / `--uc` | Context > 75 % or large ops | Symbol system, 30–50 % reduction |
| `--vs [standard\|cot\|multi]` | "Multiple perspectives", brainstorm options | Verbalized sampling — probability-weighted candidates. Sub-params: `[k:3-7] [tau:0.01-0.20] [turns:2-5] [no-synthesis]` |

#### MCP servers — opt in or out per turn

| Flag | Server | Use for |
|------|--------|---------|
| `--c7` / `--context7` | Context7 | Imports, frameworks, official docs |
| `--seq` / `--sequential` | Sequential | Complex debug, system design, multi-step reasoning |
| `--serena` | Serena | Symbol ops, project memory, semantic exploration |
| `--magic` | Magic (21st.dev) | UI components, design systems |
| `--play` / `--playwright` | Playwright | Browser testing, E2E, visual diffs |
| `--perf` / `--devtools` | Chrome DevTools | Perf audit, CLS, LCP, metrics |
| `--tavily` | Tavily | Web search, real-time info, parallel queries |
| `--sg` / `--ast-grep` | AST-Grep | Structural patterns, AST search, anti-patterns |
| `--frontend-verify` | Combined | Playwright + DevTools + Serena (UI debug) |
| `--all-mcp` / `--no-mcp` | — | Enable all / disable all (perf priority) |

#### Execution — control how work is done

| Flag | Effect |
|------|--------|
| `--delegate [auto\|files\|folders]` | Sub-agent parallel delegation. Auto-trigger: > 7 dirs, > 50 files, complexity > 0.8 |
| `--concurrency [n]` | Batch independent tool calls (1–15) into a single message |
| `--loop` | Iterative improvement — repeat until no meaningful improvement found |
| `--iterations [n]` | Fixed iteration count — exactly N cycles, with per-iteration delta report |
| `--plan` | 5-line plan (goal · approach · files · risks · verification) before execution |
| `--validate` | Pre-execution risk assessment (risk > 0.7, prod) |
| `--safe-mode` | Max validation, conservative behavior, auto `--uc` |
| `--fast` | Faster output, same model |
| `--p [abbr,…]` | Bias agent delegation: `sec`, `perf`, `qa`, `arch`, `fe`, `be`, `ops`, `refactor`, `root`, `py`, `research`, `review`, `simple`, `git`, `scribe`, `educator`, `mentor`, `index`, `insight` (multi-select with comma) |
| `--verbose-context` | Force full `.md` injection (bypass short-instruction map) |

#### Scope & focus

| Flag | Values |
|------|--------|
| `--scope` | `file` · `module` · `project` · `system` |
| `--focus` | `perf` · `security` · `quality` · `arch` · `a11y` · `testing` |

> **Priority when flags conflict:** `--safe-mode` > `--validate` > optimization · explicit user flags > auto-detection · `--no-mcp` overrides individual MCP flags.

> **Aliases auto-corrected at load time:** `--ultrathink` / `--think*` → `--seq` · `--parallel` / `--agent` → `--delegate` · `--sampling` / `--verbalized` → `--vs` · `--sea` → `--serena` · `--confidence-check` → `--validate`. Typos within Levenshtein ≤ 2 trigger a suggestion comment.

#### Examples

```bash
/sc:research "Rust async runtime tradeoffs" --depth deep --tavily --c7
/sc:implement "user export endpoint" --plan --p=be,sec --validate
/sc:analyze src/auth/ --focus security --scope module --seq
/sc:improve src/api/handlers.py --loop --iterations 3 --serena
/sc:brainstorm "should we migrate to gRPC?" --vs multi
```

---

## ⚖️ **License**

MIT — see [`LICENSE`](LICENSE).

---

## 📋 **All 33 Commands**

<details>
<summary><b>Click to expand full command list</b></summary>

### 🧠 Planning & Design (5)
- `/sc:brainstorm` — Structured brainstorming through Socratic dialogue
- `/sc:design` — System architecture, APIs, component interfaces
- `/sc:plan` — Detailed implementation plans with TDD tasks
- `/sc:estimate` — Time/effort estimation
- `/sc:spec-panel` — Multi-expert specification review

### 💻 Development (5)
- `/sc:implement` — Code implementation
- `/sc:build` — Build workflows
- `/sc:improve` — Code improvements
- `/sc:cleanup` — Refactoring & dead-code removal
- `/sc:explain` — Code explanation

### 🧪 Testing & Quality (5)
- `/sc:test` — Test generation
- `/sc:analyze` — Code analysis (quality, security, perf, arch)
- `/sc:troubleshoot` — Diagnose & resolve issues
- `/sc:reflect` — Task retrospectives
- `/sc:review` — Multi-dimensional review of work products

### 📚 Documentation (2)
- `/sc:document` — Doc generation
- `/sc:help` — Command help

### 🔧 Version Control (1)
- `/sc:git` — Git operations with intelligent commits

### 📊 Project Management (3)
- `/sc:pm` — Project management & sub-agent orchestration
- `/sc:task` — Task tracking
- `/sc:workflow` — Workflow automation

### 🔍 Research & Analysis (2)
- `/sc:research` — Deep web research
- `/sc:business-panel` — Multi-expert business analysis

### 🗂️ Session & Memory (3)
- `/sc:load` — Load session context (Serena + auto memory)
- `/sc:save` — Save session context
- `/sc:insight` — Capture structured insights to JSONL

### 🎯 Utilities (7)
- `/sc:agent` — AI agent dispatcher
- `/sc:init` — Interactive project environment setup
- `/sc:index` / `/sc:index-repo` — Repository indexing (94% token reduction)
- `/sc:recommend` — Command recommendation engine
- `/sc:select-tool` — Intelligent MCP tool selection
- `/sc:sc` — Show all commands

**Source files:** [`src/superclaude/Commands/`](src/superclaude/Commands) — each command is a single markdown file with frontmatter. After install, run `superclaude install --list-all` for a full inventory.

</details>
