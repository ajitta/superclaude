# SuperClaude Content Framework Architecture

Single source of truth for the SuperClaude content framework taxonomy, delivery pipelines, and directory roles.

## Framework Taxonomy

```
Content Type    Role                Analogy         Delivery
─────────────   ──────────────────  ─────────────   ──────────────────────────
core/           Framework DNA       Constitution    Always loaded (CLAUDE_SC.md)
modes/          Mindset overlay     Mood/Posture    On-demand (context_loader)
agents/         Domain expert       Specialist      CC-native delegation
output-styles/  Response voice      House style     CC-native, user-selected (/config)
commands/       Workflow entry      Menu item       CC-native /sc:*
mcp/            Tool docs+config    Tool manual     context_loader + install_mcp
scripts/        Hook infra          Plumbing        hooks.json → settings.json
```

## Enforcement Boundary

Only three hooks are mechanically enforced — `file_size_guard.py` (blocks Read on files >30KB), `destructive_guard.py` (two tiers: hard-blocks irreversible commands like `rm -rf /` and force-push to main; warn-tier `permissionDecision: "ask"` on reversible-but-risky `git reset --hard` / `clean -f` / `branch -D`, which prompts interactively and denies headless), and `loop_guard.py` (circuit breaker on repeated identical failures). These act at the Claude Code hook layer regardless of what the model decides. Everything else in this framework — core rules, modes, agents, commands — is model-followed prose: it shapes behavior through context, and compliance depends on the model honoring it. When a guarantee matters, it must live in a hook, not a rule.

## Directory Roles

### core/ — WHO WE ARE

Always-applied principles and rules that define SuperClaude's identity. Loaded via `CLAUDE_SC.md` `@import` at session start.

**Sub-roles:**
- **Always-loaded** — FLAGS.md, PRINCIPLES.md, RULES.md (imported by CLAUDE_SC.md, present in every session). RULES.md is a ~0.9k-token kernel (Phase 2-1 core-lite split, measurement-gated by the evals/ 4×7 matrix): four rule classes whose loss is most expensive, plus a map of the on-demand modules.
- **On-demand rule modules** — core/rules/RULES_{QUALITY,DELEGATION,DOCS,INTERACTION}.md — full R01–R21 detail, verification ladder, delegation matrix, doc conventions, selection protocol. Injected as full .md by context_loader on matching context (implement/review, delegation, doc-producing, /sc: commands); readable explicitly when no trigger fired.
- **On-demand reference** — BUSINESS_SYMBOLS.md (loaded by context_loader on business-symbol/example keywords or `--structured` — not by `--business-panel`, which loads only MODE_Business_Panel.md)

**Contract:** Files in core/ define framework-wide behavior. Always-loaded files must be concise — they consume context in every session.

### modes/ — HOW TO THINK

Situational cognitive overlays that modify Claude's thinking, communication, priorities, and behaviors. Activated on-demand via context_loader.py flag/keyword detection.

**Structure:** Each mode follows the 4-axis pattern:
- `<thinking>` — cognitive posture and reasoning approach
- `<communication>` — expression style and framing
- `<priorities>` — what to optimize for (trade-off guidance)
- `<behaviors>` — concrete action patterns

**Supporting files:** RESEARCH_CONFIG.md (type="config") provides operational parameters for the research mode — depth profiles, confidence thresholds, tool routing. It is not a mode itself and is **not** auto-injected by `context_loader.py`; it ships with modes/ as reference material accessed via cross-refs from `commands/research.md` and the research mode body.

**Contract:** Modes shape mindset, not process. They do not contain step-by-step procedures (→ commands), API references (→ mcp), or tool routing matrices (→ core/FLAGS).

### agents/ — WHO TO BE

Domain expert agents with specialized knowledge, behaviors, and tool preferences. Managed by Claude Code's native agent delegation system — auto-selected based on task keywords in the `description` frontmatter field.

**Contract:** Each agent is a self-contained definition with frontmatter (identity + permissions) and XML body (expertise + behavior). Agents receive tasks from commands and produce structured outputs.

### output-styles/ — HOW EVERY RESPONSE READS

Claude Code output styles: Markdown with YAML frontmatter that replaces the tone and format instructions in Claude Code's system prompt for every response. Installed to `<scope>/output-styles/`, the directory Claude Code scans natively; the user selects one via `/config` → **Output style**, which writes `outputStyle` to `.claude/settings.local.json`. Nothing in SuperClaude loads or injects them.

**Contract:** Plain Markdown prose, not the `<component>` pattern. `keep-coding-instructions: true` always, so Claude Code's own software-engineering instructions survive. Language-neutral: the style ships to every user, so it names patterns, never one language's phrases. A style shapes voice for every turn; a mode shapes mindset for a task.

### commands/ — WHAT TO INVOKE

User-facing workflow entry points accessible as `/sc:*` slash commands. Managed by Claude Code's native command system — installed to `~/.claude/commands/sc/`.

**Contract:** Commands define what to do, not how to think. They route to agents, activate modes, and orchestrate tool usage. Each command has syntax, flow steps, and handoff chains.

### mcp/ — TOOL REFERENCE

Documentation and configuration for MCP (Model Context Protocol) servers. Server docs are loaded on-demand by context_loader.py; server configs are installed by `install_mcp.py`.

**Contract:** MCP docs describe external tool capabilities and coordination patterns. They do not define behavior (→ modes) or workflows (→ commands).

### scripts/ — INFRASTRUCTURE

Python and shell scripts that power SuperClaude's hook system, context loading, and session management. Every `hooks.json` command is `superclaude hook <name>` (registry: `cli/hook_dispatch.py`, dispatched in `cli/entry.py` ahead of the click app), so Claude Code's hook runtime runs the copy inside the installed package — nothing is copied into the install tree and no command carries an interpreter or a path.

**Contract:** Scripts are infrastructure plumbing — they should be invisible to the user. They handle context injection, session initialization, and formatting hooks.

**Sub-package:** `scripts/auto_improve/` — overnight autonomous code improvement loop powering `/sc:auto-improve` (coordinator, eval_runner, mutator, worktree isolation, results reporter). Distinct from per-event hook scripts; runs as a standalone `superclaude auto-improve` console entrypoint (`uv run python -m superclaude.scripts.auto_improve` in a dev checkout).

**Runtime state:** every path a script writes at runtime resolves through `superclaude.utils` — never `os.getcwd()`, `Path.cwd()`, or a CWD-relative literal, since hook CWD is not guaranteed to be the project root. Two classes:

| Class | Resolver | Examples | On uninstall |
|---|---|---|---|
| Ephemeral machine state | `hook_state_dir()` → `<claude_base>/.superclaude_hooks/` | context dedup cache, hook tracker, MCP fallback log, loop_guard counters | removed wholesale |
| Durable project data | `project_root() / ".claude"` | `insights.jsonl`, `insights.pending.jsonl` | preserved |

State that is not session-keyed adds `project_key()` to its filename, because a user-scope install shares one `hook_state_dir()` across every project.

### Python Infrastructure (not content types)

The following directories support the content framework but are not content types themselves: `cli/` (Click-based CLI and installation logic), `hooks/` (hook system integration), and `utils/` (shared utilities). These are documented in the project `CLAUDE.md`.

## Content Delivery Pipeline

```
Session Start
  │
  ▼
1. CLAUDE_SC.md → core/ (FLAGS, PRINCIPLES, RULES)          ← always loaded
  │
  ▼
2. User prompt submitted
  │
  ▼
3. context_loader.py → modes/ + mcp/ + core/rules/           ← on-demand by flag/keyword
  │                    (TRIGGER_MAP matching, session dedup,
  │                     8K token budget, hybrid injection)
  ▼
4. User invokes → commands/                                   ← /sc:* slash commands
  │
  ▼
5. CC delegation → agents/                                    ← task-based agent selection
                   (description triggers, model routing,
                    permissionMode enforcement)
```

### Three Delivery Mechanisms

| Mechanism | Content Types | Trigger | Budget |
|-----------|--------------|---------|--------|
| **Always loaded** | core/ (FLAGS, PRINCIPLES, RULES kernel) | Session start | ~140 lines via @import |
| **On-demand** | modes/, mcp/, core/rules/, core/BUSINESS_SYMBOLS | Flag/keyword in prompt | 8K token budget (context_loader) |
| **CC-native** | agents/, commands/, output-styles/ | Auto-delegation, /sc:*, selected style | Managed by Claude Code runtime |

## Naming Trinity

The same domain often has content in three directories serving different roles:

```
Domain: "Research"
  ├── modes/MODE_DeepResearch.md      → HOW TO THINK about research (mindset)
  ├── agents/deep-researcher.md        → WHO TO BE when researching (agent)
  └── commands/research.md            → WHAT TO DO for a research task (workflow)

Domain: "Business"
  ├── modes/MODE_Business_Panel.md    → HOW TO THINK about business analysis (mindset)
  ├── agents/business-panel-experts.md → WHO TO BE in a business panel (agent)
  └── commands/business-panel.md      → WHAT TO DO for business analysis (workflow)
```

These are not redundant — each serves a distinct purpose in the framework.

## Authoring Rules

Each content type has a dedicated authoring guide:

| Content Type | Authoring Rules | Structural Test |
|-------------|----------------|-----------------|
| agents/ | `.claude/rules/agent-authoring.md` | `tests/unit/test_agent_structure.py` |
| commands/ | `.claude/rules/command-authoring.md` | `tests/unit/test_command_structure.py` |
| output-styles/ | `.claude/rules/output-style-authoring.md` | `tests/unit/test_output_style_structure.py` |
| modes/ | `.claude/rules/mode-authoring.md` | `tests/unit/test_mode_structure.py` |
| core/ | N/A (framework maintainers only) | N/A |
| mcp/ | `.claude/rules/mcp-authoring.md` | `tests/unit/test_content_structure.py` |
| scripts/ | Standard Python/shell conventions | `tests/unit/` (per-script) |

Cross-cutting body-format rule: `.claude/rules/xml-prose-format.md` governs XML body prose style for all component bodies under `src/superclaude/` (agents/commands/modes/mcp/core). Authoring meta-docs themselves are exempt — they may use plain Markdown.

## XML Component Pattern

All content types use the unified `<component>` XML pattern:

```xml
<component name="{name}" type="{agent|command|mode|mcp|core}">
  <role>
    <mission>Single-sentence purpose</mission>
  </role>
  <!-- Type-specific sections -->
  <bounds>
    <does>...</does>
    <never>...</never>
    <fallback>...</fallback>
  </bounds>
  <handoff next="/sc:..."/>
</component>
```

Type-specific required sections:

| Type | Required Sections |
|------|-------------------|
| agent | role, mission, mindset, focus, actions, outputs, tool_guidance, bounds |
| command | role, mission, syntax, flow, bounds, handoff |
| mode | role, mission, thinking, communication, priorities, behaviors, bounds, handoff |
| mcp | role, mission, bounds, handoff |

## Machine-Navigable Catalog (OKF)

`okf/superclaude/` mirrors this taxonomy as an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) (OKF) v0.2 knowledge bundle — one concept doc per component (agent, command, mode, MCP server, core file), each carrying a `resource` pointer back to its source in this tree. Navigation is progressive-disclosure: bundle `index.md` → section `index.md` → concept.

This document stays the human-authored source of truth for the taxonomy; the bundle is a generated, agent-navigable catalog view of the same content. Regenerate the bundle after adding a component so the catalog stays in sync.
