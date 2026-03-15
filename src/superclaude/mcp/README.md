# SuperClaude MCP Server Documentation

Tool reference — documentation and configuration for integrated MCP servers.

## Content Delivery

MCP server docs are loaded on-demand by `context_loader.py` via flag/keyword triggers. Server configs in `configs/` are installed by `install_mcp.py` into Claude Code's `settings.json`.

## Available MCP Servers

| Server | Flag | Mission |
|--------|------|---------|
| Context7 | `--c7` | Official library documentation and framework patterns |
| Sequential | `--seq` | Multi-step reasoning for complex analysis |
| Serena | `--serena` | Semantic code understanding with project memory |
| Tavily | `--tavily` | Web search and real-time information retrieval |
| Playwright | `--play` | Browser automation and E2E testing |
| Chrome DevTools | `--perf` | Performance analysis and Core Web Vitals |
| Magic | `--magic` | UI component generation from 21st.dev patterns |
| Morphllm | `--morph` | Pattern-based bulk code transformations |

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
| Context7 → Magic | Patterns supplied → components generated |
| Sequential → Playwright | Test strategy planned → tests executed |
| Sequential → DevTools | Perf strategy planned → metrics verified |
| Serena → Sequential | Symbol context + memory → architectural analysis |
| Serena → Morphllm | Symbol analysis → pattern edits executed |
| Tavily → Context7 | Updates searched → stable docs provided |
| Tavily → Playwright | URLs discovered → complex content extracted |
| Magic → Playwright | UI created → accessibility validated |
| Playwright → DevTools | Flow automated → performance analyzed |

## Related

- `core/FLAGS.md` — MCP flag definitions and auto-detection
- `configs/` — Server configuration files for `settings.json`
- `scripts/context_loader.py` — On-demand delivery mechanism
