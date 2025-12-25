<document type="manifest" name="superclaude" version="4.1.9">

# SuperClaude Framework Configuration

> **Version**: 4.1.9
> **Purpose**: Bootstrap manifest for SuperClaude components
> **Usage**: Include in your CLAUDE.md via `@src/superclaude/CLAUDE_SC.md`

---

## Core Configuration (Enabled by Default)

@core/FLAGS.md
@core/PRINCIPLES.md
@core/RULES.md
@core/RESEARCH_CONFIG.md

---

## Execution Modes

Modes are mutually exclusive. Activation based on keywords or flags.

| Mode | Trigger Keywords | Flag |
|------|------------------|------|
| Brainstorming | maybe, explore, thinking about | `--brainstorm` |
| Deep Research | research, investigate, analyze deeply | `--research` |
| Orchestration | parallel, multi-tool, optimize | `--orchestrate` |
| Task Management | plan, organize, multi-step | `--task-manage` |
| Token Efficiency | compress, efficient, --uc | `--token-efficient` |
| Introspection | reflect, analyze my reasoning | `--introspect` |
| Business Panel | ROI, stakeholder, business case | `--business` |

@modes/MODE_Brainstorming.md
@modes/MODE_DeepResearch.md
@modes/MODE_Orchestration.md
@modes/MODE_Task_Management.md
@modes/MODE_Token_Efficiency.md
@modes/MODE_Introspection.md
@modes/MODE_Business_Panel.md

---

## MCP Server Integration

| Server | Trigger Keywords | Flag | Purpose |
|--------|------------------|------|---------|
| Context7 | docs, library, framework | `--c7` | Official documentation |
| Tavily | search, current, news | `--tavily` | Web search |
| Sequential | debug, analyze, design | `--seq` | Multi-step reasoning |
| Serena | symbol, rename, codebase | `--serena` | Semantic navigation |
| Morphllm | bulk edit, pattern, refactor | `--morph` | Pattern transformations |
| Magic | UI, component, design | `--magic` | UI generation |
| Playwright | test, browser, e2e | `--play` | Browser automation |
| Chrome DevTools | performance, debug, network | `--chrome` | Browser inspection |
| Airis Agent | orchestration, gateway | `--airis` | MCP gateway |
| Mindbase | memory, cross-session | `--mindbase` | Persistent memory |

@mcp/MCP_Context7.md
@mcp/MCP_Tavily.md
@mcp/MCP_Sequential.md
@mcp/MCP_Serena.md
@mcp/MCP_Morphllm.md
@mcp/MCP_Magic.md
@mcp/MCP_Playwright.md
@mcp/MCP_Chrome-DevTools.md
@mcp/MCP_Airis-Agent.md
@mcp/MCP_Mindbase.md

---

## Specialist Agents

Agents are delegable specialists activated via Task tool or `/sc:agent`.

## Architecture & Design

@agents/system-architect.md
@agents/backend-architect.md
@agents/frontend-architect.md
@agents/devops-architect.md

## Quality & Security

@agents/quality-engineer.md
@agents/security-engineer.md
@agents/performance-engineer.md

## Development

@agents/python-expert.md
@agents/refactoring-expert.md
@agents/technical-writer.md

## Analysis & Research

@agents/deep-research-agent.md
@agents/deep-research.md
@agents/requirements-analyst.md
@agents/root-cause-analyst.md

## Project Management

@agents/pm-agent.md
@agents/repo-index.md
@agents/self-review.md

## Education & Collaboration

@agents/learning-guide.md
@agents/socratic-mentor.md
@agents/business-panel-experts.md

---

## Business Context (On-Demand)

@core/BUSINESS_SYMBOLS.md
@core/BUSINESS_PANEL_EXAMPLES.md

---

## Session Lifecycle

```
/sc:load                    # Start session, activate project
    |
[Work with /sc:* commands]  # Use slash commands
    |
Checkpoint (30min)          # Auto-save via Serena memory
    |
/sc:save                    # End session, persist state
```

---

## Activation Priority

```
1. Explicit flags (--research, --c7) override auto-detection
2. Mode keywords (mutual exclusive) take priority
3. MCP keywords (can stack) activate servers
4. Agent delegation via Task tool or /sc:agent
5. Default: standard Claude behavior
```

---

## Quick Reference

## Flags

**Modes**: `--brainstorm` `--research` `--orchestrate` `--task-manage` `--token-efficient` `--introspect` `--business`

**MCPs**: `--c7` `--tavily` `--seq` `--serena` `--morph` `--magic` `--play` `--chrome` `--airis` `--mindbase`

**Analysis**: `--think` `--think-hard` `--ultrathink`

**Control**: `--uc` `--delegate` `--validate` `--safe-mode`

## Token Efficiency Symbols

| Symbol | Meaning | Symbol | Meaning |
|--------|---------|--------|---------|
| `→` | leads to | `↔` | bidirectional |
| `✅` | completed | `❌` | failed |
| `⚠️` | warning | `🔄` | in progress |
| `⚡` | performance | `🛡️` | security |
| `🔍` | analysis | `@` | reference |

---

## Installation

```bash
# Add to project CLAUDE.md
echo "@src/superclaude/CLAUDE_SC.md" >> ./CLAUDE.md

# Or add to user config
echo "@/path/to/superclaude/src/superclaude/CLAUDE_SC.md" >> ~/.claude/CLAUDE.md
```

</document>
