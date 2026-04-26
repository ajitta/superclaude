# Serena MCP Realignment — Follow-ups State (2026-04-26)

PR #2 (Serena MCP realignment) shipped to master 2026-04-26. Three items deferred and now have committed plan docs (status: draft):

## Plan docs in repo
- **Queue tracker:** `docs/plans/serena-mcp-realignment-followups-ajitta-2026-04-26.md` — 3-item queue, PR boundaries, revisit triggers
- **PR-A plan:** `docs/plans/serena-followups-pr-a-migration-automation-ajitta-2026-04-26.md` — Item #3, install_mcp.py detection + prompted migration
- **PR-C plan:** `docs/plans/serena-followups-pr-c-hooks-integration-ajitta-2026-04-26.md` — Item #2, settings template hooks behind MCP-presence gate
- **PR-B plan:** NOT YET drafted — depends on PR-A merging to avoid install_mcp.py merge conflicts

## Sequencing
PR-A → PR-B → PR-C. PR-C is independent and can run parallel.

## Phase 0 STOP gate (PR-C)
Before implementing PR-C, re-verify upstream `oraios.github.io/serena/02-usage/030_clients.html#claude-code`. If upstream now configures hooks via `setup claude-code` itself (currently MCP-registration-only as of 2026-04-26), fold PR-C into PR-B and abandon PR-C.

## Verified fact
`serena setup claude-code` is a shorthand for `claude mcp add --scope user serena -- serena start-mcp-server --context=claude-code --project-from-cwd`. It does NOT configure hooks. Hooks are a separate manual step per upstream guidance.

## Revisit triggers
- 1+ existing-user upgrade issue → bump PR-A
- New-user onboarding friction on manual install line → start PR-B
- 90-day staleness check 2026-07-26: revalidate items still match upstream
