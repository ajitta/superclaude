# SuperClaude Content Framework Architecture

Single source of truth for the SuperClaude content framework taxonomy, delivery pipelines, and directory roles.

## Framework Taxonomy

```
Content Type    Role                Analogy         Delivery
─────────────   ──────────────────  ─────────────   ──────────────────────────
core/           Framework DNA       Constitution    Always loaded (CLAUDE_SC.md)
modes/          Mindset overlay     Mood/Posture    On-demand (context_loader)
agents/         Domain expert       Specialist      CC-native delegation
commands/       Workflow entry      Menu item       CC-native /sc:*
skills/         Runtime hooks       Safety gate     CC-native (hooks + safety only)
mcp/            Tool docs+config    Tool manual     context_loader + install_mcp
scripts/        Hook infra          Plumbing        hooks.json → settings.json
```

## Directory Roles

### core/ — WHO WE ARE

Always-applied principles and rules that define SuperClaude's identity. Loaded via `CLAUDE_SC.md` `@import` at session start.

**Sub-roles:**
- **Always-loaded** — FLAGS.md, PRINCIPLES.md, RULES.md (imported by CLAUDE_SC.md, present in every session)
- **On-demand reference** — BUSINESS_SYMBOLS.md (loaded by context_loader when business-panel mode/agent activates)

**Contract:** Files in core/ define framework-wide behavior. Always-loaded files must be concise — they consume context in every session.

### modes/ — HOW TO THINK

Situational cognitive overlays that modify Claude's thinking, communication, priorities, and behaviors. Activated on-demand via context_loader.py flag/keyword detection.

**Structure:** Each mode follows the 4-axis pattern:
- `<thinking>` — cognitive posture and reasoning approach
- `<communication>` — expression style and framing
- `<priorities>` — what to optimize for (trade-off guidance)
- `<behaviors>` — concrete action patterns

**Supporting files:** RESEARCH_CONFIG.md (type="config") provides operational parameters for the research mode — depth profiles, confidence thresholds, tool routing. It is not a mode itself but ships with modes/ because it's loaded alongside the research mode.

**Contract:** Modes shape mindset, not process. They do not contain step-by-step procedures (→ commands), API references (→ mcp), or tool routing matrices (→ core/FLAGS).

### agents/ — WHO TO BE

Domain expert agents with specialized knowledge, behaviors, and tool preferences. Managed by Claude Code's native agent delegation system — auto-selected based on task keywords in the `description` frontmatter field.

**Contract:** Each agent is a self-contained definition with frontmatter (identity + permissions) and XML body (expertise + behavior). Agents receive tasks from commands and produce structured outputs.

### commands/ — WHAT TO INVOKE

User-facing workflow entry points accessible as `/sc:*` slash commands. Managed by Claude Code's native command system — installed to `~/.claude/commands/sc/`.

**Contract:** Commands define what to do, not how to think. They route to agents, activate modes, and orchestrate tool usage. Each command has syntax, flow steps, and handoff chains.

### skills/ — RUNTIME HOOKS & SAFETY

CC-native execution containers limited to capabilities that commands and agents cannot provide: lifecycle hooks, tool restrictions, auto-invocation blocking, and script execution.

**Contract:** Skills exist only when CC-native features are required. Workflow procedures belong in commands/. Domain expertise belongs in agents/. Skills provide:
- `hooks` (PreToolUse, PostToolUse, Stop) — runtime behavior modification
- `disable-model-invocation` — prevent auto-execution of destructive workflows
- `allowed-tools` — restrict tool access for safety
- Script execution via `{{SKILLS_PATH}}` template variables

**Current skills (4):** confidence-check (PreToolUse hook), simplicity-coach (Stop hook + scripts), ship (disable-model-invocation), finishing-a-development-branch (disable-model-invocation + allowed-tools)

### mcp/ — TOOL REFERENCE

Documentation and configuration for MCP (Model Context Protocol) servers. Server docs are loaded on-demand by context_loader.py; server configs are installed by `install_mcp.py`.

**Contract:** MCP docs describe external tool capabilities and coordination patterns. They do not define behavior (→ modes) or workflows (→ commands).

### scripts/ — INFRASTRUCTURE

Python and shell scripts that power SuperClaude's hook system, context loading, and session management. Referenced by `hooks.json` and executed by Claude Code's hook runtime.

**Contract:** Scripts are infrastructure plumbing — they should be invisible to the user. They handle context injection, session initialization, skill activation, and formatting hooks.

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
3. context_loader.py → modes/ + mcp/                         ← on-demand by flag/keyword
  │                    (TRIGGER_MAP matching, session dedup,
  │                     8K token budget, hybrid injection)
  ▼
4. CC auto-detection → skills/                                ← description keyword matching
  │                    (name + description loaded at startup,
  │                     full SKILL.md on invocation)
  ▼
5. User invokes → commands/                                   ← /sc:* slash commands
  │
  ▼
6. CC delegation → agents/                                    ← task-based agent selection
                   (description triggers, model routing,
                    permissionMode enforcement)
```

### Three Delivery Mechanisms

| Mechanism | Content Types | Trigger | Budget |
|-----------|--------------|---------|--------|
| **Always loaded** | core/ (FLAGS, PRINCIPLES, RULES) | Session start | ~500 lines via @import |
| **On-demand** | modes/, mcp/, core/BUSINESS_SYMBOLS | Flag/keyword in prompt | 8K token budget (context_loader) |
| **CC-native** | agents/, commands/, skills/ | Auto-delegation, /sc:*, hooks/safety | Managed by Claude Code runtime |

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

These are not redundant — each serves a distinct purpose in the framework:
- **Mode** activates the right cognitive posture
- **Agent** provides domain expertise and tool guidance
- **Command** orchestrates the workflow and defines the entry point

**Note:** Skills are deliberately absent from the naming trinity. They serve a cross-cutting infrastructure role (hooks, safety), not a domain-specific one. Workflow procedures that were formerly in skills now live in commands.

## Authoring Rules

Each content type has a dedicated authoring guide:

| Content Type | Authoring Rules | Structural Test |
|-------------|----------------|-----------------|
| agents/ | `.claude/rules/agent-authoring.md` | `tests/unit/test_agent_structure.py` |
| commands/ | `.claude/rules/command-authoring.md` | `tests/unit/test_command_structure.py` |
| skills/ | `.claude/rules/skill-authoring.md` | `tests/unit/test_skill_structure.py` |
| modes/ | `.claude/rules/mode-authoring.md` | `tests/unit/test_mode_structure.py` |
| core/ | N/A (framework maintainers only) | N/A |
| mcp/ | N/A (no dedicated rules) | `tests/unit/test_content_structure.py` |
| scripts/ | Standard Python/shell conventions | `tests/unit/` (per-script) |

## XML Component Pattern

All content types use the unified `<component>` XML pattern:

```xml
<component name="{name}" type="{agent|command|skill|mode|mcp|core}">
  <role>
    <mission>Single-sentence purpose</mission>
  </role>
  <!-- Type-specific sections -->
  <bounds will="..." wont="..." fallback="..."/>
  <handoff next="/sc:..."/>
</component>
```

Type-specific required sections:

| Type | Required Sections |
|------|-------------------|
| agent | role, mission, mindset, focus, actions, outputs, tool_guidance, bounds |
| command | role, mission, syntax, flow, bounds, handoff |
| skill | role, mission, flow, bounds |
| mode | role, mission, thinking, communication, priorities, behaviors, bounds, handoff |
| mcp | role, mission, bounds, handoff |
