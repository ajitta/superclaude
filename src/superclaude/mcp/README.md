# SuperClaude MCP Server Documentation

Tool reference — documentation and configuration for integrated MCP servers.

## Content Delivery

MCP server docs are loaded on-demand by `context_loader.py` via flag/keyword triggers. All servers below are installable via `superclaude mcp`. Core servers are auto-suggested in interactive selection; plugin servers must be opted into explicitly with `--servers`.

## Available MCP Servers

### Core (auto-suggested by `superclaude mcp`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Context7 | `--c7` | `@upstash/context7-mcp` v2.1.6 | Official library documentation and framework patterns |
| Sequential | `--seq` | `@modelcontextprotocol/server-sequential-thinking` v0.2.0 | Multi-step reasoning for complex analysis |
| Serena | `--serena` | `serena-agent` (PyPI, pre-1.0) | Semantic code understanding with project memory (17 tools) |
| Tavily | `--tavily` | `tavily-ai/skills` (Claude plugin) | Web search, extract, crawl, research |

### Plugin (opt-in: `superclaude mcp --servers <name>`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Playwright | `--play` | `@playwright/mcp` (Microsoft official) | Browser automation, E2E testing, network mocking (30+ tools) |
| Chrome DevTools | `--perf` | `chrome-devtools-mcp` v0.21.0 | Performance, Lighthouse, a11y, memory profiling (26 tools) |

> **Last verified**: 2026-04-04. Run `/sc:research` with `--tavily` to check for newer versions.

## Composite Flags

| Flag | Servers Activated |
|------|-------------------|
| `--frontend-verify` | Playwright + DevTools + Serena |
| `--all-mcp` | All available servers |
| `--no-mcp` | None (native tools + WebSearch only) |

## MCP Coordination Matrix

| From → To | Purpose |
|-----------|---------|
| Context7 → Sequential | Docs provided → strategy analyzed |
| Sequential → Playwright | Test strategy planned → tests executed |
| Sequential → DevTools | Performance strategy planned → metrics verified |
| Serena → Sequential | Symbol context + memory → architectural analysis |
| Tavily → Context7 | Updates searched → stable docs provided |
| Tavily → Playwright | URLs discovered → complex content extracted |
| Playwright → DevTools | Flow automated → performance analyzed |

## Related

- `core/FLAGS.md` — MCP flag definitions and auto-detection
- `configs/` — Server configuration files for core servers
- `scripts/context_loader.py` — On-demand delivery mechanism
