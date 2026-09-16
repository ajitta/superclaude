# SuperClaude MCP Server Documentation

Tool ref — docs + config for integrated MCP servers.

## Content Delivery

MCP docs load on-demand via `context_loader.py` through flag/keyword triggers. Servers in the Core + Plugin tables install via `superclaude mcp`; Core auto-suggested in interactive pick, Plugin must opt-in explicit with `--servers`. Context7 + Tavily are externally provided — see their sections below.

## Available MCP Servers

### Core (auto-suggested by `superclaude mcp`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Serena | `--serena` | `serena-agent` (PyPI, v1.7.0) | Semantic code understanding with project memory |

### Plugin (opt-in: `superclaude mcp --servers <name>`)

| Server | Flag | Package / Version | Mission |
|--------|------|-------------------|---------|
| Playwright | `--play` | `@playwright/mcp` v0.0.81 (Microsoft official) | Browser automation, E2E testing, network mocking — CLI alternative: `playwright-cli` + its skill (below) |
| Chrome DevTools | `--perf` | `chrome-devtools-mcp` v1.9.0 | Perf traces, Lighthouse (a11y/SEO/best-practices), heap-snapshot memory analysis |
| Tavily | `--tavily` | `tavily-mcp` v0.2.22 (npm) | Web search, extract, crawl, map, research — optional in-conv MCP; prefer Tavily Agent Skills (below) |

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

1. Install the Tavily CLI: `curl -fsSL https://cli.tavily.com/install.sh | bash` (or `uv tool install tavily-cli`).
2. Run `tvly init` — it authenticates, detects Claude Code, and installs the skills pinned to the CLI release. The installer starts it automatically on an interactive desktop install. Skills only, for other agents: `npx skills add https://github.com/tavily-ai/skills`.
3. Restart Claude Code to load them. `search` and `extract` work keyless with limits; `map`, `crawl`, and `research` need the authenticated key.

Skills: `tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research`, `tavily-dynamic-search` (filter and dedupe large results before they enter context), `tavily-cli` (setup and command choice), `tavily-best-practices`. Auto-invoked by task, or explicit via `/tavily-search`, `/tavily-crawl`, `/tavily-research`, etc. Docs: https://docs.tavily.com/documentation/agent-skills

The `--tavily` MCP server (plugin table above) stays available as an in-conversation alternative. As of `tavily-mcp` 0.2.22 (`src/index.ts`) it exposes the same five operations as tools (`tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research`); the skills still win on context isolation (`tavily-dynamic-search`), saving crawl output as local markdown, and zero per-tool schema cost. Tavily also hosts a remote server (`claude mcp add --transport http tavily https://mcp.tavily.com/mcp`, API key in URL or OAuth) that needs no Node — `superclaude mcp` registers the local `npx` form only. The same remote server is available as a **claude.ai connector** (Settings → Connectors → Tavily), which shows up in `claude mcp list` as `claude.ai Tavily` with tools named `mcp__claude_ai_Tavily__*`. Skills and a connected Tavily MCP fire on the same intents, so keep one active per project: skills as the primary (this README's stance), or `/mcp` to disable the connector where the skills are installed. Permission rules written for the `npx` form (`mcp__tavily__*`) do not match the connector's tool names.

## Playwright — CLI or MCP

Microsoft ships both `@playwright/mcp` (the `--play` plugin above) and `playwright-cli` (`npm install -g @playwright/cli@latest`, then `playwright-cli install --skills` to install or refresh its `playwright-cli` skill). Upstream's own guidance: CLI + skill for coding agents, since it keeps tool schemas and accessibility trees out of the context; MCP for loops that need one browser kept alive across many turns. The `--play` hint the loader injects carries the short form of the rule (skill if installed, else MCP); `MCP_Playwright.md` `<cli_vs_mcp>` carries the long form and loads only under `--verbose-context`. The skill file is a copy pinned to the CLI release, so re-run `playwright-cli install --skills` after upgrading the CLI. Repo: https://github.com/microsoft/playwright-cli

> **Last verified**: 2026-09-16 against the npm registry (`@playwright/mcp`, `chrome-devtools-mcp`, `tavily-mcp`), PyPI (`serena-agent`) and each project's README. Re-check with `curl -s https://registry.npmjs.org/<pkg> | jq -r '."dist-tags".latest'` and `curl -s https://pypi.org/pypi/serena-agent/json | jq -r .info.version`.

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