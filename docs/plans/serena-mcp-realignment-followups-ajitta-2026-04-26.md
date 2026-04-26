---
status: draft
revised: 2026-04-26
---

# Serena MCP Realignment — Deferred Follow-ups

Tracked queue of items deferred from [PR #2](https://github.com/ajitta/superclaude/pull/2) (Serena MCP realignment, merged 2026-04-26). To be handled in a **separate branch**, not in the original realignment scope.

**Source:** `docs/plans/serena-mcp-realignment-ajitta-2026-04-26.md` Non-Goals section; `docs/specs/serena-mcp-realignment-discovery-ajitta-2026-04-26.md` Q6 + §Hooks recommendation.

## Why deferred

PR #2 scope was tightly bounded to docs realignment (17 tools, upstream-authoritative install command). Tooling/automation work has a different review surface and risk profile — keeping it separate let PR #2 ship as a pure docs fix without scope creep.

## Deferred items

### 1. `serena setup claude-code` shortcut delegation
- **What:** Have `install_mcp.py` subprocess-call `serena setup claude-code` instead of constructing the `claude mcp add ...` string directly (current behavior).
- **Status:** Q6 deferred during spec review (default = stay manual).
- **Risk profile:** Low-Medium — adds a runtime assumption that the `serena` CLI is on PATH; needs a pre-flight check or graceful fallback to the manual command path.
- **Done when:** New install flow passes without hard-coding the verbose `claude mcp add ...` line, and missing-CLI case fails loud with a clear next step.

### 2. Serena hooks integration
- **What:** Add Serena-recommended hooks (per upstream `setup claude-code` post-install message → `oraios.github.io/serena/02-usage/030_clients.html#claude-code`) to SuperClaude's default `.claude/settings.json` template; rely on `install_settings.py` marker-based merger to preserve user customizations. Serena does **not** ship hook payloads — we author them based on upstream guidance.
- **Status:** Out of scope per discovery spec §"Hooks recommendation (out of scope, noted for future)".
- **Risk profile:** Medium — modifies settings template + exercises the marker-based merger; needs regression test on preserve-user-hooks invariant.
- **Done when:** Fresh install lands the recommended hooks; an existing install with custom hooks survives an upgrade unchanged.

### 3. Existing-user migration automation
- **What:** Replace the 1-line manual hint (`claude mcp remove serena && <re-run>`) with detection + prompted execution. Concretely: `install_mcp.py` detects a pre-realignment Serena MCP entry (no `--project-from-cwd`, or stale `--enable-*` flags) and prompts the user before running `claude mcp remove serena` and re-installing.
- **Status:** Deferred (not in PR #2 scope; Q3 shipped only the docs hint).
- **Risk profile:** Low-Medium — destructive command on user's MCP config; needs explicit confirmation prompt and a `--no-interactive` opt-out path.
- **Done when:** A user with the old install command can run `superclaude install` (or equivalent) once and end up on the new flag set, without hand-running `claude mcp remove`.

## Suggested priority order

When the queue is picked up, tackle in this order:

1. **Item 3 (migration UX)** — unblocks existing users immediately; highest user-facing impact per unit of work. The destructive-command risk is bounded by the explicit confirmation prompt, so the Low-Medium risk profile is acceptable to take first.
2. **Item 1 (setup shortcut)** — UX improvement for new users; low marginal risk on top of Item 3 since both touch `install_mcp.py`. **Coupling note:** Items 1 and 3 share the install path — consider sequencing them in the same PR (or back-to-back PRs) so the install flow is only refactored once.
3. **Item 2 (hooks integration)** — enhancement; isolated to settings template + merger, decoupled from Items 1/3.

## When to revisit

Pick this queue up when **any** of:
- 1+ existing-user reports an upgrade issue tied to the old `claude mcp add ...` command (Item 3 priority bump).
- New-user onboarding feedback flags the manual install line as friction (Item 1).
- 90-day staleness check: **2026-07-26** — if untouched, revalidate that all three items still match upstream Serena's current behavior before scheduling.

## Non-Goals for the follow-up branch

- Do **not** revisit the 17-tool documentation surface (already shipped in PR #2).
- Do **not** alter the upstream-authoritative install command policy.
