# SuperClaude MCP Server Documentation

Tool ref — docs + config for integrated MCP servers.

## Content Delivery

MCP docs load on-demand via `context_loader.py` thru flag/keyword triggers. All servers below install via `superclaude mcp`. Core servers auto-suggested in interactive pick; plugin servers must opt-in explicit w/ `--servers`.

## Available MCP Servers

### Core (auto-suggested by `superclaude mcp`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Context7 | `--c7` | `@upstash/context7-mcp` v2.1.6 | Official library docs + framework patterns |
| Sequential | `--seq` | `@modelcontextprotocol/server-sequential-thinking` v0.2.0 | Multi-step reasoning for complex analysis |
| Serena | `--serena` | `serena-agent` (PyPI, pre-1.0) | Semantic code understanding w/ project memory (17 tools) |
| Tavily | `--tavily` | `tavily-mcp` (npm) | Web search, extract, crawl, research |

### Plugin (opt-in: `superclaude mcp --servers <name>`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Playwright | `--play` | `@playwright/mcp` (Microsoft official) | Browser automation, E2E testing, network mocking (30+ tools) |
| Chrome DevTools | `--perf` | `chrome-devtools-mcp` v0.21.0 | Perf, Lighthouse, a11y, memory profiling (26 tools) |

> **Last verified**: 2026-04-04. Run `/sc:research` w/ `--tavily` to check newer versions.

## Composite Flags

| Flag | Servers Activated |
|------|-------------------|
| `--frontend-verify` | Playwright + DevTools + Serena |
| `--all-mcp` | All available servers |
| `--no-mcp` | None (native tools + WebSearch only) |

## MCP Coordination Matrix

| From → To | Purpose |
|-----------|---------|
| Context7 → Sequential | Docs given → strategy analyzed |
| Sequential → Playwright | Test strategy planned → tests run |
| Sequential → DevTools | Perf strategy planned → metrics verified |
| Serena → Sequential | Symbol context + memory → arch analysis |
| Tavily → Context7 | Updates searched → stable docs given |
| Tavily → Playwright | URLs found → complex content extracted |
| Playwright → DevTools | Flow automated → perf analyzed |

## Related

- `core/FLAGS.md` — MCP flag defs + auto-detection
- `configs/` — Server config files for core servers
- `scripts/context_loader.py` — On-demand delivery mechanism