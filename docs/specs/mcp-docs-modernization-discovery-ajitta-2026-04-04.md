---
status: closed
revised: 2026-04-04
---

# MCP Documentation Modernization — Discovery Spec

## Problem Statement

SuperClaude ships 9 MCP server documentation files in `src/superclaude/mcp/` that guide Claude Code's tool selection and usage patterns. These docs were written when the MCP ecosystem was younger and have not kept pace with upstream changes. Meanwhile, `install_mcp.py` has been partially updated (e.g., Morphllm package name, Tavily remote MCP URL), creating a **docs-vs-installer divergence**.

Research conducted 2026-04-04 against GitHub repos, changelogs, and npm/PyPI registries.

---

## Per-MCP Findings

### Tier 1 — Complete Rewrite Needed (3 servers)

#### 1. Chrome DevTools MCP (`MCP_Chrome-DevTools.md`)

| Dimension | Our Docs | Current Reality |
|-----------|----------|-----------------|
| Version | unspecified | **v0.21.0** (2026-04-01) |
| Tool count | ~5 implied (CWV workflow) | **26 tools** |
| Capabilities | CWV measurement only | Performance + Accessibility + Memory + Network + Lighthouse + Skills + Screencast + Device emulation |
| Install | `mcp-find/mcp-add` (Docker catalog) | `npx -y chrome-devtools-mcp@latest` (already in install_mcp.py) |

**Key new capabilities not documented:**
- **Lighthouse audits** (v0.19.0) — integrated web performance/a11y/SEO auditing
- **Skills system** (v0.14.0+) — onboarding, accessibility debugging, LCP optimization, memory leak detection
- **`--slim` mode** (v0.18.0) — maximum token savings for MCP responses
- **pageId routing** (v0.19.0) — parallel multi-agent workflows on different pages
- **Screencast recording** (v0.18.0) — experimental video capture
- **Device emulation** (v0.14.0) — viewport + user-agent simulation
- **Dark/light mode testing** (v0.15.0)
- **Storage-isolated contexts** (v0.18.0)
- **Script injection** on page load (v0.15.0)
- **press_key tool**, page reload, DOM node inspection from Elements panel

**Doc impact:** Complete rewrite. Current doc covers ~10% of actual capabilities.

---

#### 2. Playwright MCP (`MCP_Playwright.md`)

| Dimension | Our Docs | Current Reality |
|-----------|----------|-----------------|
| Package | via MCP Docker (`mcp-find/mcp-add`) | `@playwright/mcp@latest` (official Microsoft package, already in install_mcp.py) |
| Tool count | unspecified (generic) | **30+ tools** across capability groups |
| Architecture | flat tool list | **Capability system**: core, pdf, vision, devtools, network, storage |

**Key new capabilities not documented:**
- **Capability opt-in system** (`--caps=network,storage,pdf,vision,devtools`)
- **Network mocking** — `browser_route_set/list/unroute` with glob patterns, custom status/body/headers
- **`run-code`** — advanced Playwright routing via inline code
- **Storage tools** — cookie CRUD, localStorage CRUD (opt-in via `--caps=storage`)
- **Incognito by default** — `--persistent` to opt into persistent profile
- **Workspace-scoped daemon** — prevents cross-project interference
- **Simplified sessions** — `-s=` flag replaces `--session`
- **Incremental snapshots** — `--snapshot-mode=incremental|full|none`
- **Test ID attribute** — `--test-id-attribute` for custom selectors
- **Secrets management** — `--secrets` for dotenv-format credential files

**Doc impact:** Complete rewrite. Activation method, tool architecture, and capabilities all changed.

---

#### 3. Morphllm MCP (`MCP_Morphllm.md`)

| Dimension | Our Docs | Current Reality |
|-----------|----------|-----------------|
| Package | via MCP Docker (`mcp-find/mcp-add`) | `@morphllm/morphmcp` (already in install_mcp.py) |
| Tools described | generic "Fast Apply" | **`edit_file`** (10,500 tok/s) + **`warpgrep_codebase_search`** (8 parallel calls/turn) |
| Concept | "pattern-based bulk transformations" | Semantic code editing + intelligent codebase search subagent |

**Key changes:**
- **`edit_file`** — not pattern-based; works with partial code snippets, no full file content needed. 11s vs 60s for traditional read/write
- **`warpgrep_codebase_search`** — semantic search subagent for broader queries ("Find the XYZ flow", "How does XYZ work?"). Not for pinpoint keywords
- **`MORPH_API_KEY`** required (already in install_mcp.py)
- **`WORKSPACE_MODE`** — auto workspace detection (default: true)
- **FlashCompact** — 33,000 tok/s context compaction (separate product, replaces default /compact)
- **Morph SDK** — OpenAI-compatible API, Anthropic & Vercel AI SDK support

**Doc impact:** Complete rewrite. Tool names, use cases, and mental model all wrong.

---

### Tier 2 — Significant Updates (2 servers)

#### 4. Serena (`MCP_Serena.md`)

| Dimension | Our Docs | Current Reality |
|-----------|----------|-----------------|
| Version | v0.1.4 mentioned | Pre-1.0 (pypi published, JetBrains Plugin released) |
| Tool count (claude-code) | 20 listed | **22 confirmed** in current session |
| New tools | — | `safe_delete_symbol`, `rename_memory` |

**Verified against current session tools** (22 tools):
- Symbol Operations (8, was 7): +`safe_delete_symbol`
- Memory (6, was 5): +`rename_memory`
- Search and Navigation (3): unchanged
- Project Management (5): unchanged

**Additional capabilities (not in claude-code context but exist):**
- JetBrains Plugin: move (symbol/file/directory), inline refactoring, propagate deletions, type hierarchy, find implementations, search in project dependencies
- New contexts: `ide-assistant`, `codex` (beyond `claude-code`)
- New basic tools (in full mode): `create_text_file`, `delete_lines`, `insert_at_line`, `replace_lines`, `read_file`, `execute_shell_command`, `restart_language_server`, `switch_modes`, `replace_content`
- Install: now available via `pip install serena` / `uvx serena` (PyPI)

**Thinking tools status:** Still restricted in claude-code context (confirmed). Our doc note is still accurate.

**Doc impact:** Update tool counts, add safe_delete_symbol + rename_memory, update version references, note JetBrains capabilities. Structure valid.

---

#### 5. Context7 (`MCP_Context7.md`)

| Dimension | Our Docs | Current Reality |
|-----------|----------|-----------------|
| MCP version | unspecified | `@upstash/context7-mcp@2.1.6` |
| Install method | `npx -y @upstash/context7-mcp` | Same (also remote MCP server URL option now available) |
| Tools | `resolve-library-id`, `query-docs` (2-step workflow) | Same core workflow, now also available as `find-docs` skill |
| Ecosystem | MCP only | MCP + SDK (`@upstash/context7-sdk`) + AI SDK tools (`@upstash/context7-tools-ai-sdk`) |

**Key changes:**
- **Remote MCP server** option (no local install needed)
- **Skill-based setup** — `find-docs` skill with 98% invocation rate (up from 66%)
- **Agent-specific rules** — CLI generates rule files per agent (Cursor: alwaysApply, Codex: AGENTS.md)
- **`--version/-v` flag** added to CLI

**Doc impact:** Add remote server option, update version reference, note skill-based alternative. Core 2-step workflow documentation still correct.

---

### Tier 3 — Minor Updates (4 servers)

#### 6. ast-grep MCP (`MCP_AstGrep.md`)

**Changes:**
- `find_code` and `find_code_by_rule` now have `max_results` and `output_format` ("text" | "json") parameters
- AST rule documentation file (`ast-grep.mdc`) included in repo for LLM reference
- Rule development workflow documented (dump → test → search iterative process)

**Doc impact:** Add parameter notes to tool descriptions. Minor.

---

#### 7. Tavily MCP (`MCP_Tavily.md`)

**Changes:**
- Install now via remote MCP: `npx -y mcp-remote https://mcp.tavily.com/mcp` (already in install_mcp.py)
- `DEFAULT_PARAMETERS` env var for configuring default search behavior
- All 5 tools confirmed active: search, extract, research, crawl, map
- `tavily_search` has new parameters: `start_date`, `end_date`, `time_range`, `country`, `include_favicon`, `search_depth` now includes "fast" and "ultra-fast" options

**Doc impact:** Add new search parameters, DEFAULT_PARAMETERS config. Minor.

---

#### 8. Sequential Thinking (`MCP_Sequential.md`)

**Changes:**
- Package version `v0.2.0` / `2025.7.1`
- Single `sequentialthinking` tool unchanged
- Still no tool annotations (issue #3403 open)
- Known compatibility issues with some clients (Cowork mode, Node.js v24)

**Doc impact:** None needed. Our doc is accurate and comprehensive.

---

#### 9. Magic / 21st.dev (`MCP_Magic.md`)

**Changes:**
- CLI installation: `npx @21st-dev/cli@latest install <client> --api-key <key>`
- API key required (via `TWENTYFIRST_API_KEY`, already in install_mcp.py)
- Component library continuously growing
- Still same core concept: AI-powered UI component generation

**Doc impact:** Minimal. Could add CLI install note.

---

## Docs-vs-Installer Divergence

| Server | install_mcp.py | MCP doc | Gap |
|--------|---------------|---------|-----|
| Chrome DevTools | `npx -y chrome-devtools-mcp@latest` | `mcp-find("chrome-devtools")` | **Activation method wrong in doc** |
| Playwright | `npx -y @playwright/mcp@latest` | `mcp-find("playwright")` | **Activation method wrong in doc** |
| Morphllm | `@morphllm/morphmcp` with `edit_file,warpgrep_codebase_search` | `mcp-find("morphllm")` + generic "Fast Apply" | **Activation + tools wrong in doc** |
| Magic | `npx -y @21st-dev/magic` | `mcp-find("magic")` | Activation method wrong in doc |
| Tavily | `npx -y mcp-remote https://mcp.tavily.com/mcp` | No install mentioned | Minor |
| Serena | `uvx --from git+https://...` | Same uvx command | Aligned |
| Context7 | `npx -y @upstash/context7-mcp` | No install mentioned | Aligned |
| Sequential | `npx -y @modelcontextprotocol/server-sequential-thinking` | No install mentioned | Aligned |
| ast-grep | `uvx --from git+https://...ast-grep-mcp` | No install mentioned | Aligned |

4 docs reference `mcp-find/mcp-add` Docker catalog activation — this pattern is outdated. All servers are now installed directly via install_mcp.py.

---

## Prioritized Update Plan

### Phase 1 — Tier 1 Rewrites (HIGH impact, 3 files)

| File | Action | Estimated Effort |
|------|--------|-----------------|
| `MCP_Chrome-DevTools.md` | Complete rewrite with 26 tools, capabilities, skills, --slim | Large |
| `MCP_Playwright.md` | Complete rewrite with capability groups, 30+ tools, network mocking | Large |
| `MCP_Morphllm.md` | Complete rewrite: edit_file + warpgrep, drop "bulk pattern" framing | Medium |

### Phase 2 — Tier 2 Updates (MEDIUM impact, 2 files)

| File | Action | Estimated Effort |
|------|--------|-----------------|
| `MCP_Serena.md` | Add safe_delete_symbol, rename_memory, update version refs, note JetBrains | Small |
| `MCP_Context7.md` | Add remote server, version ref, skill-based setup note | Small |

### Phase 3 — Tier 3 Patches (LOW impact, 4 files)

| File | Action | Estimated Effort |
|------|--------|-----------------|
| `MCP_AstGrep.md` | Add max_results/output_format params | Trivial |
| `MCP_Tavily.md` | Add new search params, DEFAULT_PARAMETERS | Trivial |
| `MCP_Magic.md` | Fix activation to CLI install, drop mcp-find | Trivial |
| `MCP_Sequential.md` | No changes needed | None |

### Phase 4 — Ancillary

| File | Action |
|------|--------|
| `README.md` | Update server table with versions |

---

## Design Constraints

1. **Token budget**: MCP docs are loaded on-demand by context_loader. Keep each doc under ~120 lines to avoid context bloat
2. **Reference not tutorial**: These are tool selection guides, not setup guides. Install is handled by install_mcp.py
3. **Existing XML structure**: All docs use `<component type="mcp">` format — maintain consistency
4. **Remove Docker catalog activation**: Replace all `mcp-find/mcp-add` patterns with direct tool availability notes
5. **Verify before documenting**: For Tier 1 rewrites, verify actual tool names against live MCP connections before publishing

## Open Questions

1. **Tavily tool count**: Research confirms 5 tools in our Docker MCP session, but the GitHub README only mentions 4 (search, extract, crawl, map — omitting research). Is `tavily_research` a Docker-only addition or an unlisted tool? → Verify against npm package
2. **Serena 1.0**: Pre-1.0 release imminent with JetBrains Plugin. Should we wait for 1.0 or update now? → Recommend: update now with current tools, note pre-1.0 status
3. **Chrome DevTools tool list**: 26 tools claimed, but full list not extracted. Need to verify against live MCP connection or GitHub README → Use `chrome-devtools-mcp` npm README
4. **Playwright tool completeness**: GitHub README has full tool list but parsing was partial → Extract full list for rewrite

## Ripple Effects Beyond MCP Docs

### `mcp-find/mcp-add` Pattern Removal
4 MCP docs reference the Docker catalog activation pattern. This pattern is no longer the primary install method — `install_mcp.py` installs servers directly. Remove all `mcp-find/mcp-add` activation sections.

Affected files (MCP docs only — no agent/command/mode files reference this pattern):
- `MCP_Chrome-DevTools.md:9-10`
- `MCP_Playwright.md:8-9`
- `MCP_Morphllm.md:8-9`
- `MCP_Magic.md:8-9`

### `--frontend-verify` Composite Flag
The concept is still valid (Playwright + DevTools + Serena). References in `FLAGS.md`, `README.md`, `context_loader.py` don't need changes. The individual MCP docs that describe this integration pattern should update the specific tool names used.

### MCP Coordination Matrix (`mcp/README.md`)
Current matrix has 12 coordination paths. With Playwright's new network mocking and DevTools' Lighthouse/a11y capabilities, potential new coordination paths:
- **Playwright:network-mock → DevTools:lighthouse** — mock API responses then audit performance
- **DevTools:accessibility → Playwright:assertion** — find a11y issues then verify fixes in browser

Consider updating matrix after Tier 1 rewrites are complete.

### Agents Referencing MCP Servers
No agent `.md` files directly reference `mcp-find/mcp-add`. The `<mcp servers="..."/>` attribute in agents is documentation-only (confirmed in agent-authoring.md). No agent changes needed.

---

## Sources

| Server | Primary Source |
|--------|---------------|
| Chrome DevTools | `github.com/ChromeDevTools/chrome-devtools-mcp` CHANGELOG.md |
| Playwright | `github.com/microsoft/playwright-mcp` README.md |
| Morphllm | `docs.morphllm.com/mcpquickstart` + `morphllm.com/setup` |
| Serena | `github.com/oraios/serena` releases + current session tools |
| Context7 | `github.com/upstash/context7` releases |
| ast-grep | `github.com/ast-grep/ast-grep-mcp` README |
| Tavily | `github.com/tavily-ai/tavily-mcp` README |
| Sequential | `github.com/modelcontextprotocol/servers` |
| Magic | `21st.dev/magic`, npm `@21st-dev/cli` |
