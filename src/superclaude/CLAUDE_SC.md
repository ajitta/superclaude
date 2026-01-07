# Static Context (~4.2K tokens)
# All @ referenced files load at session start (Claude Code limitation)
# Ordered for prefix-stable caching - do not reorder

# Core Policy (~3.7K tokens)
@core/FLAGS.md
@core/PRINCIPLES.md
@core/RULES.md
@core/RESEARCH_CONFIG.md
# @core/ABBREVIATIONS.md removed - 68% duplicate content, ~1.3K tokens saved

# Routing Indexes (~0.5K tokens) - lightweight trigger-to-file mappings
@modes/MODE_INDEX.md
@mcp/MCP_INDEX.md

# Dynamic Context (loaded via context_loader.py hook on trigger detection)
# modes/MODE_*.md (7 files): Detailed mode behaviors - loaded when triggered
# mcp/MCP_*.md (10 files): Detailed MCP guides - loaded when triggered
# commands/*.md (~15K tokens): Loaded on /sc:* skill invocations
# agents/*.md (~11K tokens): Loaded on Task tool invocations

# Token savings: ~2K static → ~0.5K static (75% reduction in index layer)
# Total potential: ~27K (all static) → ~4.2K + ~3K dynamic = ~7.2K (73% reduction)
