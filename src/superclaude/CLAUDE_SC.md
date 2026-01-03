---
name: superclaude
type: manifest
version: 4.3.0
loading: static
cache_strategy: prefix-stable
total_static_tokens: ~6.5K
---

# Static Context (~6.5K tokens)
# All @ referenced files load at session start (Claude Code limitation)
# Ordered for prefix-stable caching - do not reorder

# Core Policy (~5.5K tokens)
@core/FLAGS.md
@core/PRINCIPLES.md
@core/RULES.md
@core/RESEARCH_CONFIG.md
@core/ABBREVIATIONS.md

# Unified References (~1K tokens) - replaces 17 individual files
@modes/MODE_UNIFIED.md
@mcp/MCP_UNIFIED.md

# Dynamic Context (loaded via Skill tool on demand)
# commands/*.md: ~15K tokens - loaded on /sc:* invocations
# agents/*.md: ~11K tokens - loaded on Task tool invocations

# Individual files preserved for detailed reference (Read on demand):
# - mcp/MCP_*.md (10 files) - detailed MCP guides
# - modes/MODE_*.md (7 files) - detailed mode behaviors
# - core/BUSINESS_*.md (2 files) - business panel details
