---
name: superclaude
type: manifest
version: 4.2.0
loading: tiered
cache_strategy: prefix-stable
---

# Tier 1: Pinned (always loaded) - ~31K tokens
# Core policy + behavioral config - stable prefix for cache hits

@core/FLAGS.md
@core/PRINCIPLES.md
@core/RULES.md
@core/RESEARCH_CONFIG.md

@modes/MODE_Brainstorming.md
@modes/MODE_DeepResearch.md
@modes/MODE_Orchestration.md
@modes/MODE_Task_Management.md
@modes/MODE_Token_Efficiency.md
@modes/MODE_Introspection.md

# Tier 2: Gated (load on MCP flag detection) - ~14K tokens
# Load when --c7, --tavily, --seq, --serena, etc. detected
# Triggers: imports, frameworks, search, research, think, symbol ops

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

# Tier 3: Deferred (load on business/panel triggers) - ~7K tokens
# Business analysis components - load on explicit activation

@modes/MODE_Business_Panel.md
@core/BUSINESS_SYMBOLS.md
@core/BUSINESS_PANEL_EXAMPLES.md

# Note: commands/ and agents/ loaded dynamically via /sc:* invocations
# See: src/superclaude/commands/*.md (30 commands, ~15K tokens)
# See: src/superclaude/agents/*.md (19 agents, ~20K tokens)
