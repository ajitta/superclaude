---
type: "Overview"
title: "SuperClaude Architecture"
description: "SuperClaude is a content framework — markdown (commands, agents, modes, MCP docs, core config) installed into ~/.claude/ to configure Claude Code behavior. Ships a CLI (superclaude) and a pytest plugin."
resource: "src/superclaude/ARCHITECTURE.md"
tags: [overview, architecture]
generated:
  by: process:okf-migrate
  at: 2026-07-05
---

# SuperClaude Architecture

SuperClaude is a content framework — markdown (commands, agents, modes, MCP docs, core config) installed into ~/.claude/ to configure Claude Code behavior. Ships a CLI (superclaude) and a pytest plugin.

Source of truth: `src/superclaude/ARCHITECTURE.md`.

Delivery: source markdown installs verbatim into user/project/local scope; hooks register as `superclaude hook <name>` console-entry commands, so no install-time template variable remains.

# Links

- [Bundle index](/index.md)
- [Agents](/agents/index.md)
- [Output Styles](/output-styles/index.md)
- [Commands](/commands/index.md)
- [Modes](/modes/index.md)
- [MCP Servers](/mcp/index.md)
- [Core Config](/core/index.md)
