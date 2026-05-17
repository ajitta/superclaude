---
status: review
revised: 2026-04-27
---

# Serena MCP Realignment — Deferred Follow-ups

Tracked queue of items deferred from [PR #2](https://github.com/ajitta/superclaude/pull/2) (Serena MCP realignment, merged 2026-04-26). To be handled in a **separate branch**, not in the original realignment scope.

**Source:** [implementation plan](./05-plan.md) Non-Goals section; [discovery spec](./01-discovery.md) Q6 + §Hooks recommendation.

## Why deferred

PR #2 scope was tightly bounded to docs realignment (17 tools, upstream-authoritative install command). Tooling/automation work has a different review surface and risk profile — keeping it separate let PR #2 ship as a pure docs fix without scope creep.

## Deferred items

### 1. `serena setup claude-code` shortcut delegation
- **What:** Have `install_mcp.py` subprocess-call `serena setup claude-code` instead of constructing the `claude mcp add ...` string directly (current behavior).
- **Status:** Q6 deferred during spec review (default = stay manual).
- **Risk profile:** Low-Medium — adds a runtime assumption that the `serena` CLI is on PATH; needs a pre-flight check or graceful fallback to the manual command path.
- **Done when:** New install flow passes without hard-coding the verbose `claude mcp add ...` line, and missing-CLI case fails loud with a clear next step.

### 2. Serena hooks integration — MERGED 2026-04-27 (PR #4)
- **What:** Add Serena-recommended hooks (per upstream `setup claude-code` post-install message → `oraios.github.io/serena/02-usage/030_clients.html#claude-code`) to SuperClaude's default `.claude/settings.json` template; rely on `install_settings.py` marker-based merger to preserve user customizations.
- **Resolution:** Shipped as `src/superclaude/hooks/serena-hooks.json` + gate in `install_components.py` (Serena MCP presence required). Marked via `[superclaude] _comment` convention so existing merger logic preserves user-authored hooks. No merger algorithm change.

### 3. Existing-user migration automation — CLOSED 2026-04-27 (won't fix)
- **What:** Replace the 1-line manual hint (`claude mcp remove serena && <re-run>`) with detection + prompted execution.
- **Resolution:** Implemented as PR #3, then reverted in simplification PR. Upstream Serena's documented flow (`010_installation.html` / `030_clients.html`) does not include stale-entry migration; SC scope is mcp registration + hooks + install/uninstall scope. Manual `claude mcp remove serena` remains documented in `docs/troubleshooting/serena-installation.md`.
- **Reopen if:** Multiple existing-user reports cite the manual step as friction. Until then, do not re-implement.

## Suggested priority order

When the queue is picked up, tackle in this order:

1. **Item 3 (migration UX)** — unblocks existing users immediately; highest user-facing impact per unit of work. The destructive-command risk is bounded by the explicit confirmation prompt, so the Low-Medium risk profile is acceptable to take first.
2. **Item 1 (setup shortcut)** — UX improvement for new users; low marginal risk on top of Item 3 since both touch `install_mcp.py`. **Coupling note:** Items 1 and 3 share the install path — consider sequencing them in the same PR (or back-to-back PRs) so the install flow is only refactored once.
3. **Item 2 (hooks integration)** — enhancement; isolated to settings template + merger, decoupled from Items 1/3.

### Suggested PR boundaries

- **PR-A:** Item #3 only — `install_mcp.py` detection + prompted migration. Lands first, unblocks existing users.
- **PR-B:** Item #1 — `setup claude-code` delegation. Depends on PR-A merging first to avoid `install_mcp.py` merge conflicts.
- **PR-C:** Item #2 — settings template hooks. Independent surface, can run in parallel with PR-A/PR-B.

If upstream Serena expands `setup claude-code` to also configure hooks before this queue is picked up (currently MCP-registration-only as of 2026-04-26), fold Item #2 into Item #1 and drop PR-C.

## When to revisit

Pick this queue up when **any** of:
- 1+ existing-user reports an upgrade issue tied to the old `claude mcp add ...` command (Item 3 priority bump).
- New-user onboarding feedback flags the manual install line as friction (Item 1).
- 90-day staleness check: **2026-07-26** — if untouched, revalidate that all three items still match upstream Serena's current behavior before scheduling.

## Non-Goals for the follow-up branch

- Do **not** revisit the 17-tool documentation surface (already shipped in PR #2).
- Do **not** alter the upstream-authoritative install command policy.
