---
name: superclaude
type: manifest
version: 4.3.1
loading: hybrid
cache_strategy: prefix-stable
total_static_tokens: ~5.5K
---

# Static Context (~5.5K tokens)
# All @ referenced files load at session start (Claude Code limitation)
# Ordered for prefix-stable caching - do not reorder

# Core Policy (~5K tokens)
@core/FLAGS.md
@core/PRINCIPLES.md
@core/RULES.md
@core/RESEARCH_CONFIG.md
@core/ABBREVIATIONS.md

# Routing Indexes (~0.5K tokens) - lightweight trigger-to-file mappings
@modes/MODE_UNIFIED.md
@mcp/MCP_UNIFIED.md

# Dynamic Context (loaded via context_loader.py hook on trigger detection)
# modes/MODE_*.md (7 files): Detailed mode behaviors - loaded when triggered
# mcp/MCP_*.md (10 files): Detailed MCP guides - loaded when triggered
# commands/*.md (~15K tokens): Loaded on /sc:* skill invocations
# agents/*.md (~11K tokens): Loaded on Task tool invocations

# Token savings: ~2K static → ~0.5K static (75% reduction in index layer)
# Total potential: ~27K (all static) → ~5.5K + ~3K dynamic = ~8.5K (69% reduction)
