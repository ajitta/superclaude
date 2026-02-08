# SuperClaude MCP Server Documentation

Configuration and usage docs for MCP (Model Context Protocol) servers integrated with SuperClaude.

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

## Deprecated

| Server | Replacement |
|--------|-------------|
| Mindbase | `airis-mcp-gateway` |
| Airis-Agent | `airis-mcp-gateway` |

## Composite Flags

| Flag | Servers Activated |
|------|-------------------|
| `--frontend-verify` | Playwright + DevTools + Serena |
| `--all-mcp` | All available servers |
| `--no-mcp` | None (native tools + WebSearch only) |

## Related

- `core/FLAGS.md` — MCP flag definitions and auto-detection
- `configs/` — Server configuration files
