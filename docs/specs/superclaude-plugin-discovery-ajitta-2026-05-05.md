---
status: draft
revised: 2026-05-05
topic: superclaude-plugin-packaging
plans: ["A: flatten-to-skills", "B: marketplace-packaging-preserve-taxonomy", "C: ts-bun-rewrite-python-free"]
version: v4
---

# SuperClaude Plugin 패키징 — Discovery Spec (v4)

> **Status**: draft. v4 corrects modes/mcp delivery (ship in plugin tree) + surfaces hidden Python runtime dep in B. v3 resolved core-delivery (α). v2 added Plan C after Q3 clarification. v1 authored A and B.
> **Single remaining delegated decision**: Q' plan-choice (A vs B vs C). See §7 + §10.

## 0. Document Scope

Three **independently-detailed** plans for shipping SuperClaude as a Claude Code plugin:

- **Plan A** — Flatten 4 content types (commands/agents/modes/skills) into a unified skills-first plugin. Aggressive structural reshape. (~120-140h)
- **Plan B** — Preserve current 4-type taxonomy; add `.claude-plugin/plugin.json` + repo-level marketplace.json. Additive packaging. Pip retained. (~33-45h)
- **Plan C** — Rewrite all Python infrastructure (CLI, scripts, hooks, tests) in TypeScript with bun runtime; content tree unchanged. Plugin distribution like B. **Pip dependency eliminated.** (~217-280h)

v1 originally authored A and B. v2 added C after `/sc:review --audit-delegated` revealed user's Q3 was misread (user clarified pip removal acceptable if replaced by TS+bun). Recommendation in §6; final choice deferred to user.

---

## 1. Context

### 1.1 Current state

SuperClaude is a content framework distributed via pip (`uv tool install`). Repository version `4.5.1+ajitta`. Inventory:

- 33 commands (`src/superclaude/commands/`)
- 23 agents (`src/superclaude/agents/`)
- 7 modes (`src/superclaude/modes/`, incl. `RESEARCH_CONFIG.md` config)
- 5 skills (`src/superclaude/skills/`)
- 8 MCP server docs (`src/superclaude/mcp/`)
- Scripts/hooks (`src/superclaude/scripts/`, `hooks/`)
- Always-loaded core (`CLAUDE_SC.md` @import → `core/{FLAGS,PRINCIPLES,RULES}.md`)
- Python infrastructure: `superclaude` CLI + pytest11 plugin entry point

Install pipeline: `make deploy` (uv tool install editable) + `make sync-{user,project,local}` (content sync to `~/.claude/`). Install-time templates `{{SCRIPTS_PATH}}` and `{{PYTHON_BIN}}` are resolved by `superclaude install`. Hooks merged into `~/.claude/settings.json` via marker-based `install_settings.py` logic preserving user hooks.

### 1.2 Problem statement

User wants alignment with Claude Code plugin ecosystem standards. Plugin marketplace exists (Anthropic-managed `claude-plugins-official` + arbitrary self-hosted marketplaces). Standard install UX: `/plugin install <name>@<marketplace>`.

### 1.3 Constraints (clarified post-audit v2)

- Team size: 2-3 people
- No **user** migration burden (clarification 2026-05-05: original "마이그레이션 필요 없어" was about end-user migration, not codebase preservation; **pip dependency removal is acceptable** if replaced by TS+bun — see Plan C §4)
- npx skills channel out of scope — SC skills use CC-specific frontmatter fields (`hooks`, `agent`, `disable-model-invocation`) which neutralize npx's cross-tool value proposition; npx channel becomes redundant with plugin channel (audit I3 sharpening)
- R18 (Necessity Test): system is **not broken** without this. Motivation is ecosystem alignment + discoverability + (optionally) Python-free codebase. R18 weak; all plans must justify cost.

### 1.4 Verified facts (research-grounded)

- CC plugin format supports multi-type content natively at plugin root: `skills/`, `commands/`, `agents/`, `hooks/`, `mcp/` (per `code.claude.com/docs/en/plugins-reference`).
- Real multi-type plugins ship in production: `aws-dev-toolkit` (34 skills + 11 agents + 3 MCP), `cockroachdb` (3 agents + 32 skills). Multi-type is a **well-supported pattern with notable production examples** (audit I1 — softened from "canonical" given 2-example evidence base).
- Plugin runtime variable `${CLAUDE_PLUGIN_ROOT}` expands to plugin install dir; `${CLAUDE_SKILL_DIR}` for skill-internal paths. CC does NOT run the install-time `{{SCRIPTS_PATH}}` substitution.
- Plugin description budget: ~8000 chars total (1% of context); per-skill ≤1024/1536 char description (verified — see memory `cc-truncation-thresholds`).
- Known bug: CC issue #17688 — skill-scoped hooks declared in SKILL.md frontmatter do NOT trigger inside plugins. Currently 2 of 5 SC skills (`ship`, `finishing-a-development-branch`) use this field.

---

## 2. Plan A — Unified Skills Plugin

> **Premise.** Flatten all four SuperClaude content types (33 commands + 23 agents + 7 modes + 5 skills = 68 entities) into a single CC-native plugin where every entity is a skill (with limited agent retention for context isolation). Distributed via `/plugin install`. This makes Plan A as strong as it can be — including honest accounting of what is lost.

### 2.1 Architecture Overview

#### Core decision: collapse the naming trinity

`src/superclaude/ARCHITECTURE.md:124-137` documents the deliberate three-way split:

```
Domain: "Research"
  ├── modes/MODE_DeepResearch.md      → HOW TO THINK
  ├── agents/deep-researcher.md       → WHO TO BE
  └── commands/research.md            → WHAT TO DO
```

Plan A consolidates each domain trinity into **one skill** with three internal sections (`<mindset>` / `<persona>` / `<flow>`). 68 entities → **~28 skills + 11 agents** (49% reduction).

Justification: skills auto-trigger on description-keyword match. If `MODE_DeepResearch`, `deep-researcher`, and `/sc:research` all match the same keyword surface ("deep web research"), keeping them as three separately-loadable skills wastes the 1% (~8K char) global skill description budget on near-duplicate triggers. Merging keeps one description per domain, one body per domain.

#### Plugin tree

```
superclaude-plugin/
├── .claude-plugin/
│   └── plugin.json                       # name=sc OR superclaude (Open Q1), version=5.0.0
├── skills/                                # ~28 skills, plugin-namespaced
│   ├── brainstorm/                       # merged trinity: brainstorm cmd + requirements-analyst + MODE_Brainstorming
│   │   ├── SKILL.md                      # description + <mindset> + <persona> + <flow>
│   │   ├── canary.yaml                   # trigger regression
│   │   └── references/
│   │       ├── socratic-patterns.md
│   │       └── verbalized-sampling.md
│   ├── research/                         # research cmd + deep-researcher + MODE_DeepResearch
│   ├── design/, plan/, implement/, analyze/, improve/, test/, troubleshoot/, document/, git/
│   ├── ship/, confidence-check/, verbalized-sampling/, simplicity-coach/, finishing-a-development-branch/
│   ├── orchestration/, token-efficiency/, introspection/, task-management/, business-panel/
│   └── ... (~25-30 total)
├── agents/                               # 11 agents kept (orchestration targets)
├── commands/                             # 5 stub commands (top-used invocation preserved)
│   ├── brainstorm.md                     # 1-line: "Invoke /sc:brainstorm skill"
│   └── implement.md, plan.md, analyze.md, git.md
├── hooks/
│   └── hooks.json                        # session_start, prettier, file_size_guard, BLOCKED:destructive
├── scripts/                              # called by hooks
├── core/                                 # FLAGS, PRINCIPLES, RULES (always-loaded)
├── CLAUDE.md                             # plugin-shipped CLAUDE.md (CC auto-loads)
└── README.md
```

#### Entity count after consolidation

| Source | Count | Plan A destination |
|---|---|---|
| commands/ (33) | 33 | 28 skills (utility commands `help`, `sc`, `select-tool`, `recommend`, `init` collapse or stay) |
| agents/ (23) | 23 | 11 kept + 12 absorbed into skill bodies as `<persona>` |
| modes/ (7 incl. RESEARCH_CONFIG) | 7 | All absorbed; RESEARCH_CONFIG → `skills/research/references/research-config.md` |
| skills/ (5) | 5 | Unchanged, transplanted as-is |
| **Total** | **68** | **~28 skills + 11 agents = 39 entities** |

### 2.2 Conversion Mapping

#### Commands → Skills

| Source field | Plan A destination |
|---|---|
| `description` (frontmatter) | `description` rewritten with **trigger phrases first** per `.claude/rules/skill-authoring.md` |
| `<role command="/sc:X">` | Removed — skill identity is `name:` + `description:` |
| `<syntax>` | Kept as `argument-hint:` frontmatter |
| `<flow>` | Kept verbatim (XML body shape identical to skills) |
| `<outputs>`, `<tools>`, `<patterns>`, `<examples>`, `<gotchas>`, `<bounds>`, `<handoff>` | Kept verbatim |

#### Agents → ??? (load-bearing decision)

Three options evaluated. **Recommendation: hybrid — keep 11, absorb 12.**

| Option | Description | Verdict |
|---|---|---|
| Full absorb | All 23 → `<persona>` sections in skills | **Rejected** — kills CC's Agent-tool context isolation. `/pm`, `/task`, `/research --depth exhaustive` need isolated subagent execution |
| Skills with `allowed-tools: [Agent]` | Skills invoke `general-purpose` agent with persona-as-prompt | **Rejected** — engineering inversion of CC-native delegation; doubles description budget |
| **Hybrid** ★ | Keep 11 orchestration-target agents; absorb 12 single-domain personas | **Recommended** |

**Kept agents (11):** `deep-researcher`, `project-manager`, `business-panel-experts`, `system-architect`, `backend-architect`, `frontend-architect`, `devops-architect`, `security-engineer`, `performance-engineer`, `quality-engineer`, `refactoring-expert` (compound-domain delegation per RULES.md `<sub_agent_decision>` matrix).

**Absorbed agents (12):** `requirements-analyst`, `root-cause-analyst`, `simplicity-guide`, `socratic-mentor`, `learning-guide`, `technical-writer`, `python-expert`, `git-workflow`, `repo-index`, `insight-analyst`, `self-review`, `project-initializer`. Single-domain personas folded into matching skill bodies.

#### Modes → Skill `<mindset>` sub-section

7 modes (incl. RESEARCH_CONFIG) collapse into matching skill bodies. The `context_loader.py` 8K-budget hybrid-injection system is **fully replaced by CC's skill loader** — cheaper in steady state (only `name`+`description` loads at startup, ~150 chars each), more expensive on activation (full body loads).

Cross-cutting modes (Orchestration, Task_Management, Token_Efficiency, Introspection) become standalone skills triggered by `--orchestrate`, `--task-manage`, `--uc`, `--introspect` keywords in the description.

#### Skills → Skills

Three changes only:
- Plugin-namespaced invocation (`/superclaude:confidence-check` or `/sc:confidence-check`)
- Move `{{SKILLS_PATH}}` → `${CLAUDE_SKILL_DIR}` for portability
- **Issue #17688 workaround for `ship` and `finishing-a-development-branch`**: lift skill-scoped hooks into `plugin/hooks/hooks.json` with tool-matcher scoping (~1 day per skill)

#### Worked example: brainstorm trinity → one skill

**Sources:** `commands/brainstorm.md` (76 lines), `agents/requirements-analyst.md` (80 lines), `modes/MODE_Brainstorming.md` (41 lines). Total: 197 lines.

**Result:** `skills/brainstorm/SKILL.md` (~180 lines + references/ overflow per skill-authoring.md ≤500 line cap).

```yaml
---
name: brainstorm
description: >
  Interactive requirements discovery through Socratic dialogue. This skill
  should be used when the user says "brainstorm", "explore the idea", "let's
  discover requirements", or has an ambiguous concept ("maybe a tool that…",
  "I'm thinking about…") that needs collaborative shaping into a written spec.
  Do NOT trigger on bare "thinking about" in non-development contexts.
argument-hint: "[topic] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--vs]"
allowed-tools: Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch, Bash
---
<component name="brainstorm" type="skill">
  <role>
    <mission>Interactive requirements discovery through Socratic dialogue.</mission>
    <mindset>
    Diverge then converge. Quantity then quality. Edges then center.
    Exploration > efficiency | Understanding > solution | User's vision > best practice.
    </mindset>
    <persona>
    Claude operates as a requirements-analyst — turning ambiguous ideas into
    concrete specifications through systematic discovery.
    </persona>
  </role>
  <flow>
  1. Explore: Socratic dialogue
  2. Analyze: Multi-agent coordination via Agent tool when --parallel
  3. Validate: Feasibility assessment
  4. Specify: Write spec to docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md
  5b. Self-review (REQUIRED hard gate)
  6. Handoff: Route to /sc:review (mandatory) → then /sc:plan
  </flow>
  <delegate_to_agents note="When --parallel or --depth deep">
  - system-architect — feasibility check on system-spanning briefs
  </delegate_to_agents>
  ...
</component>
```

### 2.3 Trigger Reliability Analysis (load-bearing risk)

#### Today's invocation surface

`/sc:brainstorm` is **literal**. Hit rate: 100% by construction.

#### Plan A's invocation surface

`/sc:brainstorm` (literal) still works via stub commands for top-used skills. Auto-trigger requires:

1. CC's classifier sees the skill's `name`+`description` at session start (≤1024 chars per skill)
2. User utterance contains a phrase the classifier matches
3. No competing skill matches more strongly

#### Required canary coverage

Existing pattern in `src/superclaude/skills/confidence-check/canary.yaml` and `verbalized-sampling/canary.yaml`. For Plan A: **3 entries × 28 skills = 84+ canary entries** covering:

1. Direct keyword ("brainstorm a new auth flow")
2. Indirect phrasing ("I have a fuzzy idea")
3. Negative test (false-positive guard, modeled on verbalized-sampling's "X vs Y" disclaimer)

Total runtime at ~30 sec/`claude -p` invocation: ~42 minutes. Excluded from default `make test`; runs weekly via `pytest -m canary`.

#### Description budget math

CC global budget ~8000 chars. 28 skills × ~280 chars = 7840 chars (within budget but tight). 350 chars/skill = 9800 (over budget). Mitigation: cap descriptions ≤280 chars; rare keywords pushed to body.

#### Honest reliability estimate

| Phrasing | Hit rate |
|---|---|
| Direct phrase ("brainstorm X") | ~95% |
| Indirect phrase ("I have a fuzzy idea") | ~60-75% |
| Cross-domain phrase ("design and brainstorm") | unpredictable — two skills compete |

**Mitigation: stub-command escape hatch** — ship 5 thin commands in plugin's `commands/` dir for top-used skills. Each ~5 lines: "Invoke `/superclaude:<name>` skill." Cost: 5 × 200 chars = 1000 chars on top of skills budget. Skip stubs for niche commands (`/sc:select-tool`, `/sc:recommend`, `/sc:help`, `/sc:sc`, `/sc:spec-panel`).

### 2.4 Build Pipeline Impact

```
# Today
make deploy     → uv tool install --force --editable .
make sync-user  → copies src/superclaude/ to ~/.claude/

# Plan A
make deploy        → builds plugin tree at dist/superclaude-plugin/
make install-plugin → /plugin install ./dist/superclaude-plugin
```

**Python question:** keep `pyproject.toml`. The wheel becomes:
- Source: `src/superclaude/cli/`, `src/superclaude/pytest_plugin.py`, `src/superclaude/utils/`
- Plugin tree at `plugin/` (top-level, NOT under `src/`)
- `make build-plugin` produces `dist/superclaude-plugin/` (zip-distributable)
- `make build-wheel` produces Python wheel (CLI + pytest plugin only)

**Hooks distribution:** plugin hooks scoped to plugin per docs. User's `settings.json` is NOT touched. Marker-merge logic in `install_settings.py:70-94` becomes obsolete (~250 lines deleted).

**Test baseline:** 1,628 → ~1,800 (delete install_settings tests; add plugin validity + canary regression tests).

### 2.5 Risks (ranked)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | **Issue #17688 — skill-scoped hooks don't fire inside plugins** | Blocker | Lift `ship` + `finishing-a-development-branch` hooks to plugin `hooks/hooks.json` with tool-matcher scoping |
| 2 | Trigger collisions across 28 skills | High | 84+ canary entries with negative tests; pre-release `pytest -m canary` gate |
| 3 | Loss of `<sub_agent_decision>` routing matrix in RULES.md | High | Move matrix into `pm`, `task`, `implement` skill bodies; canary verify parallel delegation |
| 4 | Description budget overflow (28 × 300 ≈ 8400 > 8000 cap) | Medium | Cap ≤280 chars/skill; track via test_skill_structure |
| 5 | Loss of `--flag` system — skills take `$ARGUMENTS` differently | Medium | Skills accept flag strings as `$ARGUMENTS` text; flag-parser logic moves into skill body |
| 6 | Subagent isolation lost for 12 absorbed agents | Medium | Accepted — only single-domain personas absorbed; compound-task canaries verify orchestration with 11 kept agents |
| 7 | `make sync-local` workflow broken for headless dev | Medium | Replace with `make build-plugin && claude --plugin-dir ./dist/superclaude-plugin` |
| 8 | Namespace prefix `/superclaude:X` is verbose vs `/sc:X` | Low | Set `name: sc` in plugin.json → `/sc:brainstorm` (same UX) |
| 9 | Anthropic skill validator doesn't recognize CC extension fields | Low | Already documented in skill-authoring.md; ignore IDE warnings |
| 10 | Loss of `context_loader.py` 8K-budget injection | Low | CC skill loader replaces this; budget profile improves in steady state |

### 2.6 Work Estimate

| Item | Hours |
|---|---|
| Plugin tree scaffolding (plugin.json, layout, README) | 4 |
| Convert 33 commands → 28 skill bodies (16 trinity merges) | 30 |
| Absorb 12 agents into matching skill bodies | 12 |
| Modes → `<mindset>` sections (7 modes) | 6 |
| Lift skill-scoped hooks (issue #17688) for 2 skills | 4 |
| Rewrite 28 skill descriptions for trigger phrasing | 8 |
| Author 84+ canary entries | 10 |
| Update Makefile: build-plugin, retire sync-* | 4 |
| Delete install_components/install_settings sync logic | 6 |
| Migrate test_skill_canary.py + add plugin-validation tests | 8 |
| Documentation: CLAUDE.md, README, ARCHITECTURE, skill-authoring | 6 |
| Test pass: canary, manual smoke, headless regression | 8 |
| **Total (planned)** | **~106 hours** |
| **Total (realistic with collision tuning overrun)** | **120-140 hours** |

### 2.7 Plan A Open Questions

- **A-Q1**: Stub commands yes/no, and which? Recommendation 5 stubs for top-used. Stubs consume description budget and partly defeat auto-trigger goal.
- **A-Q2**: Namespace prefix `/sc:` (matches today) vs `/superclaude:` (more discoverable in `/plugin` listings)?
- **A-Q3**: Agent cut depth — keep 11 (current rec) vs aggressive 5 (deep-researcher, project-manager, business-panel-experts, system-architect, refactoring-expert)?
- **A-Q4**: MCP server install — ship `.mcp.json` (plugin-scoped, can't disable individually) vs keep `superclaude install --mcp` step (user-scoped, current behavior)?

---

## 3. Plan B — Multi-Type Plugin Packaging

> **Premise.** Preserve current 4-type taxonomy. Add `.claude-plugin/plugin.json` + repo-level self-hosted `marketplace.json`. Pip-side distribution stays alive for CLI + pytest plugin; plugin path is parallel channel for end-user content.

### 3.1 Layout Decision — B2 Mirrored Build (recommended over B1 in-place)

**Why not B1 (point plugin at `src/superclaude/`).** Anthropic plugin spec requires `commands/`, `agents/`, `skills/`, `hooks/`, `mcp/` at plugin root, not nested. CC has no path-rewrite mechanism. Pointing plugin source at `./src/superclaude/` would force the loader to know `cli/`, `utils/` are not plugin content (which it can't).

**B2 (mirrored).** Build script copies content directories into a flat tree. Separates Python distribution from content distribution cleanly.

#### Plugin tree (output of `make build-plugin`)

```
release/plugin/superclaude/                        ← committed (marketplace consumers need it)
├── .claude-plugin/
│   └── plugin.json                                ← rendered from manifest template
├── agents/                                        ← copied from src/superclaude/agents/ (23)
├── commands/                                      ← copied from src/superclaude/commands/ (33)
├── skills/                                        ← copied from src/superclaude/skills/ (5)
├── hooks/
│   └── hooks.json                                 ← rewritten — see §3.4
└── scripts/                                       ← copied from src/superclaude/scripts/

├── core/                                          ← (α) shipped — see §3.6
│   ├── FLAGS.md
│   ├── PRINCIPLES.md
│   └── RULES.md
├── CLAUDE.md                                      ← plugin CLAUDE.md @imports core/* → CC auto-loads in plugin context
├── modes/                                         ← v4: shipped (CC ignores native; context_loader reads via path lookup)
│   ├── MODE_DeepResearch.md
│   ├── MODE_Brainstorming.md
│   └── ... (7 files incl. RESEARCH_CONFIG.md)
└── mcp/                                           ← v4: shipped (same path-lookup mechanism)
    └── MCP_*.md (8 files)
```

#### Repo layout

```
superclaude/
├── .claude-plugin/                                ← NEW — repo-level marketplace
│   └── marketplace.json
├── plugins/                                       ← NEW — manifest templates
│   └── superclaude/manifest/
│       ├── plugin.template.json
│       └── marketplace.template.json
├── src/superclaude/                               ← unchanged (SSOT)
├── scripts/build_superclaude_plugin.py            ← scaffold exists; needs activation
└── release/plugin/superclaude/                    ← committed build output
```

#### `plugin.json` content (rendered)

```json
{
  "name": "superclaude",
  "version": "4.5.1",
  "description": "AI-enhanced development framework for Claude Code — 33 commands, 23 agents, 5 skills, hooks for session/safety/format",
  "author": {
    "name": "ajitta (fork) / SuperClaude-Org (upstream)",
    "url": "https://github.com/ajitta/superclaude"
  },
  "homepage": "https://github.com/ajitta/superclaude",
  "repository": "https://github.com/ajitta/superclaude",
  "license": "MIT",
  "keywords": ["framework", "automation", "agents", "commands", "skills"]
}
```

Note: `version` drops `+ajitta` local-version suffix (CC plugin SemVer-strict, no PEP 440). Fork identity moves into `author.name` and `description`.

### 3.2 `marketplace.json` Skeleton (self-hosted)

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "superclaude-marketplace",
  "description": "SuperClaude framework plugin distribution",
  "owner": {"name": "ajitta", "email": "ajitta@gmail.com"},
  "metadata": {"pluginRoot": "./release/plugin"},
  "plugins": [
    {
      "name": "superclaude",
      "description": "AI-enhanced development framework — commands, agents, hooks, skills",
      "source": "./release/plugin/superclaude",
      "category": "development",
      "version": "4.5.1",
      "tags": ["framework", "agents", "commands", "skills", "automation"],
      "author": {"name": "ajitta", "email": "ajitta@gmail.com"},
      "homepage": "https://github.com/ajitta/superclaude",
      "license": "MIT"
    }
  ]
}
```

**End-user install:**

```
/plugin marketplace add ajitta/superclaude
/plugin install superclaude@superclaude-marketplace
```

**Commit-vs-gitignore tradeoff:** marketplace consumers need `release/plugin/superclaude/` as committed artifact. Recommendation: `release/plugin/superclaude/` committed, `dist/plugins/` gitignored. Decouples build artifacts from distribution artifacts. Alternative: split to sibling `superclaude-plugin-dist` repo (see §3.7 R6).

### 3.3 Build Pipeline Impact (additive)

```
# Current (master) — UNCHANGED
make deploy             → uv tool install --force --editable .
make sync-user          → superclaude install --force --scope user
make sync-{project,local}

# NEW additive
make build-plugin       → python scripts/build_superclaude_plugin.py
                            ├── copy {agents,commands,skills,scripts}/ → release/plugin/superclaude/
                            ├── transform hooks.json:
                            │     {{SCRIPTS_PATH}} → ${CLAUDE_PLUGIN_ROOT}/scripts
                            │     {{PYTHON_BIN}}   → python3 (with shebang shim)
                            ├── render plugin.template.json → release/plugin/superclaude/.claude-plugin/plugin.json
                            └── render marketplace.template.json → .claude-plugin/marketplace.json
make publish-plugin     → git add release/.claude-plugin && commit && push
```

**Marketplace strategy: B-self only for v1.** B-public (PR to `anthropics/claude-plugins-official`) deferred until 5+ external users adopt self-hosted version. B-both deferred to post-stabilization (~6 months).

**What's added:**
- `scripts/build_superclaude_plugin.py` (scaffold exists; needs activation)
- `plugins/superclaude/manifest/{plugin,marketplace}.template.json`
- `release/plugin/superclaude/` build output
- `.claude-plugin/marketplace.json` at repo root
- `VERSION` file at repo root

**What's removed:** Nothing in v1. `install_settings.py` marker-merge stays for pip users.

**What stays:**
- All CLI commands (`superclaude install`, `uninstall`, `doctor`)
- `pytest_plugin.py` entry point (pip-only — no plugin mechanism for Python packages)
- All Python scripts (delivered via plugin's `scripts/` directory)

### 3.4 Hooks Resolution

Per Anthropic plugin spec: `hooks/hooks.json` at plugin root is auto-discovered. Plugin hooks layered alongside (not merged into) user's `~/.claude/settings.json`. They run when plugin is enabled.

**Concrete behavior:**
- User's `~/.claude/settings.json` NOT modified by `/plugin install`. Only `enabledPlugins` and `pluginConfigs[<plugin-id>].options` get touched.
- Plugin hooks coexist with user hooks; same event fires both. Order: roughly user-first, then plugins, but not contractually guaranteed.
- `${CLAUDE_PLUGIN_ROOT}` is the load-bearing variable — every command path must use it.

**Migration:**

```json
// Current (pip-installed)
{ "type": "command", "command": "{{PYTHON_BIN}} {{SCRIPTS_PATH}}/session_init.py" }

// Plugin-built
{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_init.py" }
```

**Side-effects on `install_settings.py`:** plugin path bypasses entirely. No code deleted in v1; documented behavior: "If a user has both pip-installed and plugin-installed SC, hooks fire twice. Pick one."

**Serena hooks:** declare both files in plugin.json `hooks` field (accepts string|array per spec): `["./hooks/hooks.json", "./hooks/serena-hooks.json"]`. Preserves the conditional-gating distinction without runtime detection (fails silently if Serena absent).

### 3.5 Template Variable Resolution

| Pre-plugin token | Plugin token | Where it appears |
|---|---|---|
| `{{SCRIPTS_PATH}}` | `${CLAUDE_PLUGIN_ROOT}/scripts` | hooks.json command strings |
| `{{SKILLS_PATH}}` | `${CLAUDE_SKILL_DIR}` (skill-internal) OR `${CLAUDE_PLUGIN_ROOT}/skills` (cross-skill) | SKILL.md scripts/, skill hooks |
| `{{PYTHON_BIN}}` | `python3` (with shebang shim) | hooks.json command strings |

**`{{PYTHON_BIN}}` resolution — three options:**

| Option | Pros | Cons |
|---|---|---|
| (a) Hardcode `python3` | Simple | Fails on Windows non-WSL, MSYS2 (per memory `1315`) |
| **(b) Shebang shim** ★ | Matches Anthropic house style; all scripts run directly | Requires execute-bit (Unix), `.py` association (Windows) |
| (c) Wrapper `_run.sh`/`_run.bat` | Cross-platform robust | Extra layer; bundle complexity |

**Recommendation: (b) shebang shim** — Windows non-WSL is rare for SC users (per gotcha `1315` confirms WSL/Git Bash is dominant Windows path).

### 3.6 CLI + pytest Plugin Fate

**Decision: pip path stays. Plugin path is content-only. No re-implementation, no drop.**

| Function | Channel |
|---|---|
| `superclaude` CLI (`install`, `uninstall`, `doctor`, `verify-drift`, `audit`, `auto-improve`) | pip / `uv tool install` |
| pytest plugin (auto-markers `canary`, `hallucination`) | pip (`[project.entry-points.pytest11]`) |
| 33 commands + 23 agents + 5 skills | **plugin** |
| Hooks + scripts | **plugin** (with pip fallback) |
| MCP server docs (8 files) | pip-only |
| modes/ (7 files) | pip-only |
| core/ (CLAUDE_SC.md, FLAGS, PRINCIPLES, RULES) | pip-only |

**Asymmetry resolved (v3, user picked α).** Plugin ships its own `CLAUDE.md` + `core/{FLAGS,PRINCIPLES,RULES}.md`. CC auto-loads the plugin's CLAUDE.md when the plugin is enabled; plugin CLAUDE.md `@import core/FLAGS.md`, `@import core/PRINCIPLES.md`, `@import core/RULES.md` fires the same chain that `~/.claude/CLAUDE.md → @superclaude/CLAUDE_SC.md` fires for pip users. **No CLI step, no user CLAUDE.md edit, no `/sc:enable-core` command needed.**

**Mitigation paths considered:**

| Option | Description | Verdict |
|---|---|---|
| **(α) Plugin-bundled CLAUDE.md + core/** ★ | Plugin's own `CLAUDE.md` @imports core/*; CC auto-loads in plugin context | **Selected (v3 user pick)** — zero user friction, structurally identical to Plan A's core handling |
| (β) Document "components only" + manual `@superclaude/CLAUDE_SC.md` add | Ugly UX | Rejected |
| (γ) Ship `/sc:enable-core` command | Idempotent CLAUDE.md edit, but adds explicit user step | Rejected in favor of α |

modes/ and mcp/ also ship in plugin tree (v4). CC plugin format doesn't have native "mode" or "MCP doc" types, but plugin format does NOT forbid arbitrary subdirs — they sit alongside `scripts/` and `context_loader.py` reads them via `${CLAUDE_PLUGIN_ROOT}/modes/*.md` and `${CLAUDE_PLUGIN_ROOT}/mcp/*.md`. Plugin-only users get full mode and MCP-doc coverage. **Hidden Python dependency**: context_loader.py still requires `python3 ≥3.10` on the user's system to execute as a hook — this is a real cost of Plan B that the plugin-vs-pip framing initially obscured. Plan C eliminates this via TS+bun rewrite.

### 3.7 Risks (ranked)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 🔴 | `${CLAUDE_PLUGIN_ROOT}` not substituted in non-`command:` contexts (skill `<references>` paths, agent file refs) | High | Build-time linter fails if `{{SCRIPTS_PATH}}` survives; audit all SKILL.md/agent files |
| R2 ✅ | ~~Core (FLAGS/PRINCIPLES/RULES) not delivered to plugin-only users~~ | Resolved (v3) | (α) selected — plugin ships own CLAUDE.md + core/; auto-loaded in plugin context. modes/ remain pip-only (residual). |
| R3 🔴 | Hooks fire twice if both pip + plugin installed | High | (a) Document. (b) `superclaude doctor` detects + warns. (c) Pip uninstall auto-detects plugin presence |
| R4 🟡 | Plugin install does not run `install_mcp.py` (no auto MCP registration) | Medium | v1: document manual MCP registration. v2: investigate `mcpServers` field in plugin.json |
| R5 🟡 | `{{PYTHON_BIN}}` shim breaks on Windows non-WSL | Medium | Shebang-shim approach; SessionStart self-test hook |
| R6 🟡 | `release/plugin/` git size — ~5MB per version | Medium | git-lfs OR sibling `superclaude-plugin-dist` repo |
| R7 🟡 | Test baseline (1,628 passing) at risk if build edits hooks.json in src/ | Medium | Build script read-only on `src/`; CI assertion `git diff --exit-code src/` |
| R8 🟢 | modes/ + mcp/ + core/ stay pip-only forever | Low | Accepted — additive plan honors "no migration burden" promise |
| R9 🟢 | CC plugin spec evolves; `${CLAUDE_PLUGIN_ROOT}` semantics change | Low | Pin via test suite asserting runtime resolution |
| R10 🟢 | Skill-scoped hook bug #17688 | Low | None of SC's 5 skills currently use SKILL.md `hooks:` (verified; cross-check during build) |

### 3.8 Work Estimate

| # | Item | Hours |
|---|---|---|
| 1 | Reactivate `scripts/build_superclaude_plugin.py` + manifest templates | 3 |
| 2 | hooks.json template-rewrite step | 4 |
| 3 | Python script shebangs + executable bits | 2 |
| 4 | `release/plugin/superclaude/` directory + .gitignore carve-out | 1 |
| 5 | Repo-root `.claude-plugin/marketplace.json` | 2 |
| 6 | ~~`/sc:enable-core` command (γ)~~ → (α) plugin CLAUDE.md + core/ wiring | 2 |
| 7 | `superclaude doctor` plugin-detection warning (R3) | 3 |
| 8 | Build-time linter: assert no `{{SCRIPTS_PATH}}` survives | 2 |
| 9 | CI: assert `make build-plugin` is read-only on src/ | 1 |
| 10 | Plugin install integration test (smoke: install/run/uninstall) | 6 |
| 11 | Documentation: README plugin-install section, plugin-vs-pip table | 4 |
| 12 | Serena-hooks split: declare both files in plugin.json `hooks` field | 1 |
| 13 | v4: ship `modes/` + `mcp/` in plugin tree, audit context_loader path-lookup | 2 |
| | **Total (planned)** | **~33 hours** |
| | **Total (realistic +30%)** | **~45 hours (~5-6 dev days)** |

### 3.9 Plan B Open Questions

- **B-Q1**: `release/plugin/superclaude/` commit strategy — accept ~5MB/version in this repo, or split to sibling `superclaude-plugin-dist` repo?
- ~~**B-Q2**: Core delivery — γ vs α?~~ **Resolved v3: (α) plugin-bundled CLAUDE.md + core/.**
- **B-Q3**: Marketplace identity — `superclaude-marketplace` (self-hosted, ajitta-fork-only), `superclaude` (preempts upstream namespace), or coordinate with upstream `SuperClaude-Org/SuperClaude_Framework` for shared marketplace?
- **B-Q4**: MCP server registration in plugin.json `mcpServers` field — investigate v1 or defer? Yes = ship inline configs, drop `superclaude install --mcp`. No = plugin users do separate manual MCP setup.

---

## 4. Plan C — TypeScript + bun Rewrite (Python-free)

> **Premise.** Rewrite all Python infrastructure (CLI, scripts, hooks runtime, test infra) in TypeScript with bun runtime. Content (33 commands + 23 agents + 7 modes + 5 skills + MCP docs) is Markdown — language-agnostic, untouched. Distribute as CC plugin (taxonomy-preserving, like Plan B). Eliminates pip dependency entirely.

**Why this plan exists.** Q3 audit (§7) revealed user's "마이그레이션 필요 없어" was misread; user clarifies they're open to pip removal — IF the alternative is TS+bun. Plan C is the **principled fulfillment** of that intent.

### 4.1 Scope

**Rewritten in TS:**
- `src/superclaude/cli/` (install, uninstall, doctor, audit, verify-drift, auto-improve, etc.)
- `src/superclaude/scripts/` (~13 hook runtime scripts; `auto_improve.py` is largest at 2765 lines per memory `3340`)
- `src/superclaude/utils/` (shared utilities)
- `tests/` (1,628 tests → bun test or vitest)

**Untouched:**
- All Markdown content (commands/agents/modes/skills/mcp/core) — language-agnostic
- Authoring rules (`.claude/rules/`)
- XML prose conventions (`xml-prose-format.md`)

**Removed:**
- `pyproject.toml`, `uv tool install` path, pytest11 entry point
- `{{PYTHON_BIN}}`, `{{SCRIPTS_PATH}}` install-time templates (replaced by `${CLAUDE_PLUGIN_ROOT}` runtime resolution)
- Python-specific gotchas (MSYS2/UV path canonicalization per memory `1315`)

### 4.2 Distribution & Runtime

```jsonc
// package.json (bun-compatible, no Node fallback)
{
  "name": "superclaude",
  "version": "5.0.0",
  "bin": {"superclaude": "./dist/cli.js"},
  "scripts": {"build": "bun build", "test": "bun test"},
  "engines": {"bun": ">=1.0"}
}
```

End-user flow:
```
bun add -g superclaude          # CLI install (or `bunx superclaude` for one-shot)
/plugin install superclaude     # Content install (same as Plan B)
```

Hook commands shift from `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/X.py` to `bun run ${CLAUDE_PLUGIN_ROOT}/scripts/X.ts` — bun runs TypeScript natively, no transpile step.

### 4.3 Why bun-only (not Node)

- **Single runtime**: avoids `node` vs `bun` confusion in hooks
- **Native TS execution**: no transpile, no build step at runtime
- **Faster cold start**: hook scripts fire on every session start; bun's startup latency is materially lower than Node's
- **Cross-platform consistency**: bun is Windows-native; eliminates the persistent UV/MSYS2 pain
- **Single lockfile**: `bun.lock` instead of `package-lock.json` / `pnpm-lock.yaml`

**Trade-off**: `bun ≥1.0` prerequisite locks out users with only Node installed. Mitigation: prominent install instruction (`curl -fsSL https://bun.sh/install | bash`); rejects partial Node-fallback build (doubles maintenance for marginal reach).

### 4.4 Content Tree

`release/plugin/superclaude/` layout matches Plan B (§3.1) — `agents/`, `commands/`, `skills/`, `hooks/`, `scripts/`, `core/`, `CLAUDE.md`, `modes/`, `mcp/`. The only difference vs Plan B: `scripts/` contains `.ts` files invoked via `bun run`, not `.py` invoked via `python3`. modes/ and mcp/ ship the same way (path-lookup by context_loader.ts via `${CLAUDE_PLUGIN_ROOT}/modes/*.md`).

### 4.5 Test Infrastructure Migration

| Current (pytest) | TS+bun replacement |
|---|---|
| pytest11 entry point auto-marker | bun test config + explicit imports (no auto-marker mechanism) |
| 1,628 tests (unit/integration/canary) | Rewrite to bun test syntax (~similar count, mechanical port) |
| `pytest -m canary` (skill trigger regression) | `bun test --filter canary` |
| pytest fixtures + conftest | bun test setup/teardown OR vitest if richer DI needed |
| scipy A/B testing (dev dep, used by auto-improve) | See §4.5 decision below |

**scipy decision (open):**
- **(α)** Keep A/B analysis as separate offline Python tool — still pip-free for end users
- **(β)** Replace with `simple-statistics` (TS) + custom tests
- **(γ)** Drop A/B testing infrastructure entirely (was added recently; possibly de-scopable)

### 4.6 Migration Path (4 phases, internal-only)

1. **Phase 1 (audit)**: catalog every Python file, classify (CLI / hook script / test / dev tool)
2. **Phase 2 (parallel)**: build TS implementation alongside Python in `src/typescript/`; content tree unchanged
3. **Phase 3 (cutover)**: switch `make build-plugin` to use TS scripts; `pyproject.toml` retired; `package.json` becomes SSOT
4. **Phase 4 (cleanup)**: delete `src/superclaude/{cli,scripts,utils}/`, `pyproject.toml`, Python tests; promote `src/typescript/` to repo top-level

Team of 2-3 with no end-user migration burden = these 4 phases run serially without preserving intermediate states publicly.

### 4.7 Risks (ranked)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| C1 🔴 | TS port of `context_loader.py` (load-bearing — flag detection, mode injection) introduces regressions | Blocker | Behavioral test suite (input prompt → expected injected files) ported FIRST; TS impl gates on this passing |
| C2 🔴 | `auto_improve.py` is 2765 lines — recent, complex, A/B optimization core | Blocker | Phase the rewrite: TS port simplest scripts first (loop_guard, format hooks); auto_improve last with full eval coverage |
| C3 🔴 | bun ≥1.0 prerequisite — Node-only users lose install path | High | Document prominent install instruction; reject Node-compat fallback build |
| C4 🟡 | scipy A/B test infra has no clean TS equivalent | Medium | Decision (α/β/γ) deferred to Phase 2 |
| C5 🟡 | pytest fixtures port — DI patterns differ in bun test | Medium | Use vitest if bun test DI insufficient; budget +20h |
| C6 🟡 | Python-era gotchas/memory entries become irrelevant — risk losing institutional knowledge | Medium | Archive to `docs/archive/python-era-gotchas.md` rather than delete |
| C7 🟡 | TS strict mode requires upfront types for currently-untyped Python code | Medium | Strict from start; ban `any` except at JSON parsing boundaries |
| C8 🟢 | Editor tooling shift (mypy → tsc, ruff → eslint+prettier) | Low | Standard TS toolchain |

### 4.8 Work Estimate

| # | Item | Hours |
|---|---|---|
| 1 | Repo scaffolding: `package.json`, `tsconfig.json`, bun config, ESLint+Prettier | 4 |
| 2 | TS CLI rewrite (8 commands) | 40 |
| 3 | TS scripts rewrite (auto_improve ~25h alone; remaining 12 ~25h) | 50 |
| 4 | TS utils + shared libraries | 10 |
| 5 | Test infra: bun test config + 1,628 test ports | 60 |
| 6 | scipy decision + impl (assume β simple-statistics port) | 12 |
| 7 | Plugin packaging (manifest, hooks `bun run` rewrite, marketplace.json) | 12 |
| 8 | Documentation rewrite (README, CLAUDE.md, ARCHITECTURE, gotcha files) | 15 |
| 9 | Cutover: parallel-then-flip Phase 3, smoke testing | 10 |
| 10 | Archive Python-era gotchas + dependency removal | 4 |
| 11 | v4: TS port of context_loader path-lookup for `modes/` + `mcp/` (already covered in scripts rewrite; explicit verification) | 2 |
| | **Total (planned)** | **~217 hours** |
| | **Total (realistic +30%)** | **~280 hours (~35 dev days)** |

This is **~6-7 weeks full-time**, ~3-4 months part-time. Substantially larger than A or B.

### 4.9 Plan C Open Questions

- **C-Q1**: scipy A/B testing — (α) separate Python tool / (β) TS port / (γ) drop infrastructure?
- **C-Q2**: bun-only or bun-with-Node-fallback? Latter doubles maintenance, former locks out Node-only users.
- **C-Q3**: pytest plugin entry point — drop entirely OR re-implement as bun test plugin (research feasibility)?
- **C-Q4**: Cutover style — Phase 3 hard flip (atomic) OR gradual (one script at a time, both runtimes coexist briefly)?

---

## 5. Comparison Matrix (3-plan, v2)

| Dimension | Plan A (flatten) | Plan B (preserve+plugin) | Plan C (TS+bun rewrite) |
|---|---|---|---|
| **Effort (planned)** | 106h | 33h | 217h |
| **Effort (realistic)** | 120-140h (~16 dev days) | ~45h (~5-6 dev days) | ~280h (~35 dev days) |
| **Effort multiple vs B** | 3-4× | 1× | **~6×** |
| **Reversibility** | Low (src/ merges) | High (additive) | **Lowest** (Python tree deletion + TS-only future) |
| **Architectural impact** | Reverses ARCHITECTURE.md skills decision | Preserves all | Preserves content; replaces runtime layer |
| **Trigger reliability** | New risk (~60-95% by phrasing) | Unchanged | Unchanged |
| **Capability loss** | modes, `--flag`, `<sub_agent_decision>` | None | None for content; pytest11 entry point retired |
| **Issue #17688 exposure** | High (mitigation 2 dev-days; audit I2 reclassified) | Not exposed | Not exposed |
| **pip dependency (CLI tool install)** | Kept (CLI/pytest only) | Kept (full pip path) | **Eliminated** |
| **Runtime dependency (hook execution)** | `python3 ≥3.10` system | `python3 ≥3.10` system (context_loader.py runs as hook) | **`bun ≥1.0` only** |
| **Cross-platform consistency** | Same as today (UV/MSYS2 pain persists) | Same as today (Python via system path; MSYS2 issues persist) | **Improved** (bun native cross-platform) |
| **Description budget pressure** | Tight (~7840/8000) | None | None |
| **Marketplace pattern fit** | Skills-only (uncommon) | Multi-type (well-supported) | Multi-type + bun runtime (modern) |
| **Distribution UX** | `/plugin install` | `/plugin install` + pip | `/plugin install` + `bun add -g` |
| **Core (FLAGS/PRINCIPLES/RULES)** | Inline in plugin | Inline via plugin CLAUDE.md + core/ (α resolved v3) | Inline via plugin CLAUDE.md + core/ (α, identical to B) |
| **modes/, mcp/ delivery (v4)** | Inline in plugin (modes absorbed into skills) | Plugin tree subdirs; context_loader.py path-lookup | Plugin tree subdirs; context_loader.ts path-lookup |
| **context_loader role** | Reduced (modes/core handled inline; MCP injection only) | Full (modes + MCP on-demand injection) | Full (TS port; same behavior) |
| **Test baseline impact** | -50/+200 (reshape) | Minimal | **Full rewrite (1,628 tests)** |
| **Rollback if it fails** | Hard | Easy | **Hardest** — runtime change is one-way |
| **Future extensibility** | Skills-only locked in | All extensions open | TS ecosystem (typed, modern toolchain) |
| **Fits clarified Q3 (pip removal OK)** | Partial (pip CLI still Python) | No (full pip retained) | **Yes** (Python eliminated) |
| **Open questions** | 4 (A-Q1..A-Q4) | 4 (B-Q1..B-Q4) | 4 (C-Q1..C-Q4) |

---

## 6. Recommendation (revised v2)

**Recommendation pivots based on user's clarified Q3 intent.** Two valid recommendations depending on goal weighting:

### If goal = "ecosystem alignment with minimal disruption" → **Plan B**
- Lowest cost (~5-6 dev days)
- No runtime change, no content reshape
- Easiest rollback (delete `release/plugin/` + manifests)
- Acknowledged trade-off: pip dependency persists; UV/MSYS2 Windows pain remains

### If goal = "Python-free codebase + modern runtime" → **Plan C** ★
- User's clarified Q3 intent ("PIP 의존성 제거 필요시 bun TS 전환") makes Plan C the **principled** option
- ~6× cost vs Plan B but produces a categorically simpler codebase (one runtime, modern tooling, native cross-platform)
- Reversibility lowest — runtime decisions are sticky
- Eliminates the persistent UV/MSYS2 Windows pain

### Plan A no longer recommended
v1 reasoning stands (multi-type pattern is well-supported, Plan A causes capability loss + issue #17688 exposure + irreversibility). Plan A's structural reshape doesn't gain coding clarity; if the goal is "simpler codebase", Plan C delivers it more directly.

### Acknowledgment of contradicting Q1=a confirmed (audit C2)

This v2 recommendation pivots away from the user's Q1 "1: a" confirmed selection. Rationale: new evidence emerged after Q1 (well-supported multi-type pattern in marketplace; user clarified Q3 opens TS+bun option). The recommendation is evidence-driven re-surfacing for review, not override.

### Synthesis

For a 2-3 person team that wants Python out of the codebase and bun in, **Plan C is recommended**. For a team wanting fastest ecosystem alignment without runtime change, **Plan B is recommended**. The user's stated openness to TS+bun (turn 5) tilts toward C; the cost asymmetry tilts toward B. The choice is a single question: "is Python removal worth ~235 extra hours?"

---

## 7. Resolved Decisions (v2 post-audit)

| # | Question | User reply | Mode | Resolution |
|---|---|---|---|---|
| Q1 | Distribution shape | "1: a" | **confirmed** (literal letter) | A chosen; v1 authored both A and B on user request; v2 adds Plan C after Q3 clarification |
| Q2 | Motivation | "2: c" | **confirmed** (literal letter) | (c) CC ecosystem alignment |
| Q3 | Migration policy | v1: "관계없어. 마이그레이션은 필요 없어"; v2 clarification: "사용자 마이그레이션으로 오해. PIP 의존성 제거 필요하다면 bun만 사용한 ts 코드로 전환" | **resolved** (clarified post-audit) | (1) No **user** migration burden. (2) **pip removal acceptable** if replaced by TS+bun → triggered Plan C analysis |
| Q4 | npx skills inclusion | "npx는 고려 대상이 아닌 것으로 판단(너의 정보를 신뢰)" | **delegated** (judgment statement, no numbered options offered) | Excluded — sharpened reasoning: SC's CC-specific frontmatter fields neutralize npx's cross-tool value |
| Q' | Reframe — keep A or accept B | "두 방안 모두 작성하고 비교" | **delegated** (didn't pick a/b/c, requested parallel work) | All 3 plans authored (v2 adds C); final choice deferred to user post-/sc:review |

**Delegated decisions remaining: 1** (Q'). Q3 resolved via direct user clarification in audit cycle. Q4 reasoning sharpened but decision stands.

---

## 8. Consolidated Open Decisions (post-audit v2)

User must resolve before `/sc:plan`:

1. **Final plan choice**: A vs B vs C (§6 offers two valid recommendations: B for minimal disruption, C for Python-free goal). Audit-flagged single delegated Q'.
2. **If Plan A is chosen**: A-Q1 through A-Q4 (§2.7).
3. **If Plan B is chosen**: B-Q1 through B-Q4 (§3.9).
4. **If Plan C is chosen**: C-Q1 through C-Q4 (§4.9).
5. **Cross-cutting**: MCP server registration policy (inline `mcpServers` in plugin.json vs separate CLI step).

---

## 9. Self-Review Iteration Log

- **v1 (2026-05-05)** — Initial draft authored by `/sc:brainstorm --seq --tavily --c7 --delegate auto`. Two sub-agents (system-architect × 2) authored Plans A and B in parallel; main thread synthesized comparison + recommendation (Plan B). Pending `/sc:review`.
- **v4 (2026-05-05)** — context_loader treatment + modes/mcp distribution corrections:
  - §3.1 plugin tree: `modes/` + `mcp/` undeferred — shipped as plugin subdirs (CC ignores native; context_loader path-lookups them via `${CLAUDE_PLUGIN_ROOT}/modes/*.md`).
  - §3.6: removed misleading "modes/mcp pip-only" framing; surfaced **hidden Python dependency** of Plan B (context_loader.py requires system `python3 ≥3.10` to fire as hook — plugin-only users not exempt).
  - §4.4 Plan C content tree: explicit `modes/` + `mcp/` listing.
  - §5 matrix: added "Runtime dependency (hook execution)" row exposing python3 vs bun split; added "modes/mcp delivery" row + "context_loader role" row showing reduced/full/full split across A/B/C.
  - §3.8 Plan B work item 13: +2h for modes/mcp ship.
  - §4.8 Plan C work item 11: +2h verification.
  - Plan B revised total: ~33-45h → ~35-47h (negligible).
  - Plan C revised total: ~217-280h → ~219-283h (negligible).
- **v3 (2026-05-05)** — Core delivery decision: user picked **(α) plugin-bundled CLAUDE.md + core/**.
  - §3.1 plugin tree: `core/` undeferred — shipped inside plugin.
  - §3.6 mitigation table: (α) selected; (γ) `/sc:enable-core` rejected.
  - §3.7 R2: resolved (no longer red-flagged).
  - §3.8 work item 6: scope reduced from 4h to 2h (CLAUDE.md @import wiring only).
  - §3.9 B-Q2: resolved.
  - §5 matrix: Core delivery row updated for B and C.
  - Plan C inherits the same α treatment.
- **v2 (2026-05-05)** — Audit findings applied:
  - **C1 resolved**: User clarified Q3 misread; pip removal acceptable via TS+bun. Added §4 Plan C (~217-280h).
  - **C2 addressed**: §6 recommendation now explicitly acknowledges contradicting Q1 confirmed selection with new evidence.
  - **I1 applied**: §1.4 "Multi-type IS canonical" → "well-supported pattern with notable production examples".
  - **I2 applied**: Issue #17688 severity reclassified Blocker → High (2 dev-days mitigation) in §5 matrix.
  - **I3 applied**: §1.3 + §7 Q4 reasoning sharpened to CC-specific extension argument.
  - Comparison matrix expanded to 3-plan grid (§5).
  - Open decisions consolidated for A/B/C trichotomy (§8).
  - status remains `draft` pending user pick of B vs C (or A); single delegated Q' remains.

---

## 10. Handoff

**Single remaining delegated decision: Q' (plan-choice).** Q3 was clarified directly; Q4 reasoning was sharpened but decision stands.

After user picks B vs C (or revisits A):
- If Plan B chosen → `/sc:plan` for ~33-45h Plan B breakdown + answer B-Q1..B-Q4.
- If Plan C chosen → `/sc:plan` for ~217-280h Plan C breakdown + answer C-Q1..C-Q4.
- If Plan A revisited → `/sc:plan` for ~106-140h Plan A breakdown + answer A-Q1..A-Q4.

Spec status will move to `approved-for-plan` when user picks a plan and answers its open questions.

---

## Appendix A — Sources

### Anthropic spec (verified by sub-agents)

- [Plugins reference — `code.claude.com/docs/en/plugins-reference`](https://code.claude.com/docs/en/plugins-reference) (plugin.json schema, hook locations, `${CLAUDE_PLUGIN_ROOT}`, scope behavior)
- [Plugin marketplaces — `code.claude.com/docs/en/plugin-marketplaces`](https://code.claude.com/docs/en/plugin-marketplaces) (marketplace.json schema, source field formats, install workflow)
- [Skills — `code.claude.com/docs/en/skills`](https://code.claude.com/docs/en/skills)
- [Anthropic claude-plugins-official marketplace.json](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) — multi-type plugin examples (aws-dev-toolkit, cockroachdb)

### SuperClaude codebase references

- `src/superclaude/ARCHITECTURE.md` — taxonomy SSOT
- `src/superclaude/cli/install_settings.py` — current marker-based hooks merge
- `src/superclaude/hooks/hooks.json`, `serena-hooks.json` — current hook config
- `src/superclaude/skills/confidence-check/canary.yaml` — canary pattern reference
- `.claude/rules/skill-authoring.md` — skill body conventions
- `pyproject.toml:67-71` — CLI + pytest11 entry points
- `Makefile` — current deploy/sync pipeline

### Project memory references

- `reference_claude-code-truncation-thresholds` — verified description char limits (1024/250)
- `feedback_scripts-path-resolution` — `{{SCRIPTS_PATH}}` template behavior
- `gotcha 1315` — Windows MSYS2/UV path canonicalization
- `S390` — measured boundary blur in Labeled-list shape (XML prose format precedent)
