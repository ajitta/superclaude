# SuperClaude MCP Server Documentation

Tool ref — docs + config for integrated MCP servers.

## Content Delivery

MCP docs load on-demand via `context_loader.py` thru flag/keyword triggers. Servers in the Core + Plugin tables install via `superclaude mcp`; Core auto-suggested in interactive pick, Plugin must opt-in explicit w/ `--servers`. Context7 + Tavily are externally provided — see their sections below.

## Available MCP Servers

### Core (auto-suggested by `superclaude mcp`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Serena | `--serena` | `serena-agent` (PyPI, v1.5.1) | Semantic code understanding w/ project memory |

### Plugin (opt-in: `superclaude mcp --servers <name>`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Playwright | `--play` | `@playwright/mcp` v0.0.75 (Microsoft official) | Browser automation, E2E testing, network mocking |
| Chrome DevTools | `--perf` | `chrome-devtools-mcp` v1.0.1 | Perf, Lighthouse, a11y, memory profiling |
| Tavily | `--tavily` | `tavily-mcp` v0.2.19 (npm) | Web search + extract — optional in-conv MCP; prefer Tavily Agent Skills (below) |

Server **launch flags** (token-saving `--slim`, `--persistent` profiles, `--test-id-attribute`, `--secrets`, timeouts) are upstream package options set in the MCP client config, not SuperClaude behavior — read the package's own README for the current set. The `MCP_*.md` docs deliberately carry none of them (`.claude/rules/mcp-authoring.md` trim rule: no version/install/setup blocks).

## Context7 — claude.ai connector

Context7 ships as a **claude.ai connector**, not a `superclaude mcp` server. Enable it once from the connector directory in claude.ai settings; it then appears in Claude Code as a connected MCP server with no local `npx` process and no API key to manage.

1. Open claude.ai → Settings → Connectors, find Context7, enable it.
2. Restart Claude Code (or run `/mcp`) to pick up the connection.
3. Verify with `/mcp` — the server lists as `Context7`.

No `MCP_Context7.md` ships: the connector injects its own server instructions and the tool descriptions carry the resolve-then-query order, version-pinning format, and 3-call cap. The `--c7` flag stays, as an inline directive in `context_loader.py` that forces a lookup where the connector's question-shaped trigger would not fire.

`/mcp disable` is per-project: turning Context7 off in one project leaves it on elsewhere. Do **not** register `@upstash/context7-mcp` via `superclaude mcp` alongside the connector — the same tools would surface under two server names and the model would pick between duplicates.

## Tavily Web Access — Agent Skills (recommended)

Tavily's web capabilities install as **Agent Skills** via the Tavily CLI — no MCP server, no `superclaude mcp` step:

1. Install the Tavily CLI: `curl -fsSL https://cli.tavily.com/install.sh | bash`
2. Install the skills: `npx skills add tavily-ai/skills --all` (single skill: `--skill tavily-search`)
3. Restart Claude Code to load them. Set `TAVILY_API_KEY` (get from https://app.tavily.com).

Skills: `tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research`, `tavily-best-practices`. Auto-invoked by task, or explicit via `/tavily-search`, `/tavily-crawl`, `/tavily-research`, etc. Docs: https://docs.tavily.com/documentation/agent-skills

The `--tavily` MCP server (plugin table above) stays available as an in-conversation alternative but exposes only search + extract; the skills add crawl, map, and multi-source research.

> **Last verified**: 2026-07-04. Run `/sc:research` w/ `--tavily` to check newer versions.

## Composite Flags

| Flag | Servers Activated |
|------|-------------------|
| `--frontend-verify` | Playwright + DevTools + Serena |
| `--all-mcp` | All available servers |
| `--no-mcp` | None (native tools + WebSearch only) |

## MCP Coordination Matrix

| From → To | Purpose |
|-----------|---------|
| Tavily → Context7 | Updates searched → stable docs given |
| Tavily → Playwright | URLs found → complex content extracted |
| Playwright → DevTools | Flow automated → perf analyzed |

## Related

- `core/FLAGS.md` — MCP flag defs + auto-detection
- `cli/install_mcp.py` — Install registry (`MCP_SERVERS`) for core servers (Context7 deliberately absent — connector, not install target)
- `scripts/context_loader.py` — On-demand delivery mechanism
- `okf/superclaude/mcp/index.md` — OKF v0.1 catalog: MCP servers as concept docs, resource-linked to source (repo-root bundle; dev tree only — not shipped to `~/.claude/` at install)