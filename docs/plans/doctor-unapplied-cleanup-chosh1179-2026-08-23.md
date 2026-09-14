---
status: draft
revised: 2026-08-23
---

# Doctor Cleanup — Unapplied Items

A `/doctor` run on 2026-08-23 proposed four phases of cleanup. Phases 1 and 2 were applied
and committed; phases 3 and 4 were not. This records what is left so it can be applied
later without repeating the scan.

**Scope note.** Everything here edits the operator's own machine — `~/.claude/settings.json`
and `~/.claude.json`. Nothing in this file touches the SuperClaude repository, and applying
it changes nothing for anyone else installing the framework.

## Evidence behind the findings

| Source | Volume | Window |
|---|---|---|
| `~/.claude/projects/**/*.jsonl` transcripts | 50 most recent, 2 project dirs | 2026-08-21 → 2026-08-23 |
| Corroborating wide sweep | all 1,208 transcripts, 1.1 GB | last 31 days |
| `~/.claude.json` `skillUsage` / `pluginUsage` | lifetime counters | since install |

Lifetime `numStartups` at scan time: 1,485. Skill counters are written only on real
dispatch, so a zero there is genuine disuse evidence; the transcript sweep was used to
confirm nothing fired inside the window.

## Applied already (for context, no action needed)

- **Phase 1** — removed 8 dangling `tavily-*` symlinks in `.claude/skills/` (targets did not
  exist) and 2 dead keys in `.claude/settings.local.json` (`enabledMcpjsonServers`,
  `enableAllProjectMcpServers`, both pointing at a `.mcp.json` this project does not have).
- **Phase 2** — trimmed 27 derivable lines from `CLAUDE.md` and moved
  `.claude/rules/gotchas/README.md` behind `paths:` frontmatter. Committed as `d7a5b46`.

## Phase 3 — disable unused skills and plugins (not applied)

Saving: about **2,406 estimated resident tokens per session**, the largest remaining item
from the scan. Every change below is reversible by deleting the key.

### 3a — 21 user-scope skills

Add to `skillOverrides` in `~/.claude/settings.json` as `"<name>": "off"`.

Never dispatched since install (18):

| Skill | Est. resident tokens |
|---|---|
| `agent-browser` | 234 |
| `orchestration` | 206 |
| `orca-cli` | 205 |
| `imagegen-frontend-web` | 170 |
| `design` | 155 |
| `computer-use` | 135 |
| `adhd` | 134 |
| `banner-design` | 127 |
| `ui-styling` | 124 |
| `gpt-taste` | 80 |
| `find-skills` | 78 |
| `design-system` | 72 |
| `mcp-builder` | 72 |
| `redesign-existing-projects` | 62 |
| `aside-browser` | 61 |
| `brand` | 47 |
| `slides` | 36 |
| `gsd` | 26 |

Used once or twice, long ago (3):

| Skill | Lifetime uses | Last used | Est. tokens | Reason |
|---|---|---|---|---|
| `tavily-best-practices` | 0 | never | 77 | not referenced by the `--tavily` flag |
| `ui-ux-pro-max` | 1 | 34 days ago | 120 | one use across 1,485 startups |
| `playwright-cli` | 5 | 83 days ago | 22 | the Playwright MCP server covers it (256 calls in 31 days) |

**Keep, do not disable:** `tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`,
`tavily-research` are named by `--tavily` in `core/FLAGS.md`, so disabling them would break
a documented framework flag. `tavily-cli` has the highest lifetime count of that group (21).
`design-taste-frontend` was used inside the window.

### 3b — 2 plugins

Add to `enabledPlugins` in `~/.claude/settings.json` as `"<key>": false`. Both are enabled
at user scope, so the user file is the correct place — a `false` in project settings would
be overridden.

| Plugin | Lifetime uses | Last real use | Est. tokens |
|---|---|---|---|
| `claude-md-management@claude-plugins-official` | 0 | never | 103 |
| `frontend-design@claude-plugins-official` | 2 | 42 days ago | 54 |

**Keep:** `claude-mem` (101,229 uses), `unknowns` (5,004), `caveman` (172),
`andrej-karpathy-skills` (124) all fired inside the window. `typescript-lsp` shows a
lifetime zero, but LSP usage tracking shipped recently and the operator's other active
repository holds 215 `.ts` files — the zero is more likely missing telemetry than disuse.

### Applying it safely

Skill and plugin names are read from local config, so write them as JSON rather than
splicing them into a shell command: build the new settings in a `mktemp` file and merge
with `jq --slurpfile`, or edit `~/.claude/settings.json` directly. Restart Claude Code
afterwards and confirm with `/context`.

## Phase 4 — Context7 connector — SUPERSEDED, do not apply

The scan proposed disabling the `claude.ai Context7` connector for this project: zero tool
calls in 31 days, and its tools are deferred so it costs no resident context.

**That proposal is now wrong.** Commit `9c0412b` made the claude.ai connector the framework's
only documented source for Context7 — the npx `@upstash/context7-mcp` server was removed
from `cli/install_mcp.py::MCP_SERVERS`. Disabling the connector would leave the `--c7` flag
pointing at nothing. (`mcp/MCP_Context7.md` was itself deleted afterwards: the connector's
server instructions and the two tool descriptions already carried everything it said, so the
flag now fires an inline directive in `context_loader.py` instead of a doc.)

Zero calls in the window is now a signal that Context7 is under-used, not that it is
redundant. Leave it enabled.

## Not actionable from this repository

`claude-mem`'s `worker-service.cjs` is the largest single hook cost measured anywhere in the
scan — 1,834.6ms mean, 4,751ms max on SessionStart, larger than SuperClaude's entire
per-session hook budget. It is a third-party plugin; see
[../features/hook-performance/03-analysis.md](../archive/features/hook-performance/03-analysis.md)
for the measurement.

## Findings that needed no action

- Installation is healthy: one native install at `~/.local/bin/claude`, resolved by PATH,
  matching `installMethod`, with no npm-global or `~/.claude/local` leftovers.
- All settings files parse; all 23 agent and 34 skill definitions load with valid
  frontmatter and no name collisions.
- Claude Code was on the latest version for its channel.
- `permissions.defaultMode` is already `auto` at user scope with nothing shadowing it.
- No permission allow-rules were worth adding. Of 94 denials in 31 days, 80 were `Read`
  calls blocked by the operator's own Safe Read `[R16]` hook — deliberate, and an allow rule
  cannot override a hook. The remaining 14 were one-off `Bash` denials on commands that are
  write-capable, interpreters, or `gh api`, all excluded from allowlisting.
- No hook exceeded its threshold at the time of the scan. The hook costs that were worth
  attention turned out to be a separate investigation — see
  [../features/hook-performance/](../archive/features/hook-performance/).
