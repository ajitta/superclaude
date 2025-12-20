# SuperClaude v5.0

<config model="opus-4.5" version="5.0" style="goal-oriented"/>

## Core (Always Loaded)
@core/RULES_CORE.md
@core/OPUS_PROFILE.md

## Loading Rules

### Mode Triggers (load at most one)
| Keywords | File |
|---|---|
| research, investigate, deep-analysis | @modes/deep-research.md |
| brainstorm, explore, ideas, maybe | @modes/brainstorming.md |
| multi-tool, parallel, optimize | @modes/orchestration.md |
| business, panel, stakeholder | @modes/business-panel.md |

### MCP Triggers
| Keywords | File |
|---|---|
| library, docs, framework | @mcp/context7.md |
| ui, component, design | @mcp/magic.md |
| bulk-edit, pattern-edit | @mcp/morphllm.md |
| browser, e2e, visual-test | @mcp/playwright.md |
| complex, reasoning, sequential | @mcp/sequential.md |
| symbol, navigate, codebase | @mcp/serena.md |
| web, search, current | @mcp/tavily.md |

### Agents / Commands
- agents/ -> use `@agent-[name]` or `/sc:agent [name]`
- commands/ -> use `/sc:[command]`
