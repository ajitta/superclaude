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
| Sequential → Magic | UI logic analyzed → components implemented |
| Sequential → Playwright | Test strategy planned → tests executed |
| Sequential → DevTools | Perf strategy planned → metrics verified |
| Serena → Morphllm | Semantic analysis → pattern edits executed |
| Serena → Sequential | Context provided → architectural analysis |
| Tavily → Sequential | Info gathered → synthesized/analyzed |
| Tavily → Playwright | URLs discovered → complex content extracted |
| Tavily → Context7 | Updates searched → stable docs provided |
| Tavily → Serena | Research done → sessions stored |
| Magic → Playwright | UI created → accessibility validated |
| Playwright → DevTools | Flow automated → performance analyzed |

**Key distinctions:** Serena (semantic/symbol ops) vs Morphllm (pattern/bulk ops) | Tavily (web search) vs WebFetch (single URL) | DevTools (metrics) vs Playwright (automation) vs Claude-in-Chrome (live debug)

## Related

- `core/FLAGS.md` — MCP flag definitions and auto-detection
- `configs/` — Server configuration files
