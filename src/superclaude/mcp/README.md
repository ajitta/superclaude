# SuperClaude MCP Server Documentation

Tool ref — docs + config for integrated MCP servers.

## Content Delivery

MCP docs load on-demand via `context_loader.py` thru flag/keyword triggers. All servers below install via `superclaude mcp`. Core servers auto-suggested in interactive pick; plugin servers must opt-in explicit w/ `--servers`.

## Available MCP Servers

### Core (auto-suggested by `superclaude mcp`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Context7 | `--c7` | `@upstash/context7-mcp` v2.2.5 | Official library docs + framework patterns |
| Sequential | `--seq` | `@modelcontextprotocol/server-sequential-thinking` 2025.12.18 | Multi-step reasoning for complex analysis |
| Serena | `--serena` | `serena-agent` (PyPI, v1.5.1) | Semantic code understanding w/ project memory |
| Tavily | `--tavily` | `tavily-mcp` v0.2.19 (npm) | Web search + extract (map/crawl/research live in `/tavily-cli` skill) |

### Plugin (opt-in: `superclaude mcp --servers <name>`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Playwright | `--play` | `@playwright/mcp` v0.0.75 (Microsoft official) | Browser automation, E2E testing, network mocking |
| Chrome DevTools | `--perf` | `chrome-devtools-mcp` v1.0.1 | Perf, Lighthouse, a11y, memory profiling |

> **Last verified**: 2026-05-20. Run `/sc:research` w/ `--tavily` to check newer versions.

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
- `cli/install_mcp.py` — Install registry (`MCP_SERVERS`) for core servers
- `scripts/context_loader.py` — On-demand delivery mechanism