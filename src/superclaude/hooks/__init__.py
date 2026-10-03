"""SuperClaude hooks package: mcp_fallback (once-per-session MCP hints).

Import the submodule directly. This file runs before any submodule, so it
deliberately imports and re-exports nothing: context_loader reaches
mcp_fallback on every prompt, and an eager import here would load every sibling
module, with its imports, on each one.
"""
