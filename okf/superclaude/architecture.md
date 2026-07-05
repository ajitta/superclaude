---
type: "Overview"
title: "SuperClaude Architecture"
description: "SuperClaude is a content framework — markdown (commands, agents, modes, skills, MCP docs, core config) installed into ~/.claude/ to configure Claude Code behavior. Ships a CLI (superclaude) and a pytest plugin."
resource: "src/superclaude/ARCHITECTURE.md"
tags: [overview, architecture]
timestamp: 2026-07-05
---

# SuperClaude Architecture

SuperClaude is a content framework — markdown (commands, agents, modes, skills, MCP docs, core config) installed into ~/.claude/ to configure Claude Code behavior. Ships a CLI (superclaude) and a pytest plugin.

Source of truth: `src/superclaude/ARCHITECTURE.md`.

Delivery: source markdown resolves template vars ({{SCRIPTS_PATH}}, {{SKILLS_PATH}}) at install time, then installs into user/project/local scope.

# Links

- [Bundle index](/index.md)
- [Agents](/agents/index.md)
- [Commands](/commands/index.md)
- [Modes](/modes/index.md)
- [Skills](/skills/index.md)
- [MCP Servers](/mcp/index.md)
- [Core Config](/core/index.md)
