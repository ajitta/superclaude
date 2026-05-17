---
feature: serena-mcp-realignment
phase: complete
owner: ajitta
created: 2026-04-26
updated: 2026-05-18
---

# Serena MCP Realignment

## Purpose

Realign SuperClaude content (CLI install code, runtime instructions, docs, command flows) with the upstream-authoritative Serena MCP shape — a re-installed Serena MCP server with new launch command and reduced tool catalog. Eliminates stale references that would cause agents to call removed tools, while preserving R17 Serena-First for symbol operations. Main work shipped as [PR #2](https://github.com/ajitta/superclaude/pull/2) merged 2026-04-26; deferred follow-ups (PR-A migration automation, PR-B setup shortcut, PR-C hooks integration) tracked separately.

## Documents

1. [Discovery](./01-discovery.md) — 2026-04-26, status: approved-for-plan — current MCP state probe + tool catalog delta + 6 design questions resolved
2. [Plan](./05-plan.md) — 2026-04-26, status: draft — 6 sequential single-commit phases for content realignment
3. [Follow-ups](./05a-plan-followups.md) — 2026-04-27, status: review — deferred items from PR #2 (setup shortcut delegation, migration automation, hooks integration)

## Status

Phase: **complete**. Main realignment shipped via PR #2 (2026-04-26). Deferred follow-ups in `05a-plan-followups.md` tracked as separate-branch work; PR-A + PR-C plans drafted, PR-B blocked on PR-A merge.

## Migration Note

Promoted from standalone via `/sc:promote-feature serena-mcp-realignment` on 2026-05-18 per doc-convention-v2 R4. Pre-promotion paths: `docs/specs/serena-mcp-realignment-discovery-*.md`, `docs/plans/serena-mcp-realignment-*.md`. Statuses preserved as-of original revision date; only `feature:`/`phase:` README frontmatter freshly assigned.
