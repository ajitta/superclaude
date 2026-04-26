---
status: draft
revised: 2026-04-26
---

# Serena Follow-ups — PR-C: Hooks Integration

**Source:** [follow-ups queue](serena-mcp-realignment-followups-ajitta-2026-04-26.md) Item #2.
**Branch (proposed):** `feat/serena-hooks-integration`
**Sequencing:** Independent of PR-A and PR-B. Touches `install_settings.py` + settings template only — can run in parallel.

## Goal

Add upstream-recommended Serena hooks (per `setup claude-code` post-install message → `oraios.github.io/serena/02-usage/030_clients.html#claude-code`) to SuperClaude's default `.claude/settings.json` template, leveraging the existing marker-based merger in `install_settings.py` to preserve user customizations.

## Done When

- Fresh install lands hooks matching the upstream recommendation as of the implementation-time re-verification (Phase 0).
- An existing install with user-authored hooks survives an upgrade unchanged (preserve-user-hooks invariant holds).
- If Serena MCP is not registered, hooks are NOT installed and an informational message is shown.

## Resolved Decisions (carry from queue)

| # | Decision | Confirmed |
|---|----------|-----------|
| D1 | Hooks are authored by SuperClaude based on upstream guidance — Serena does not ship payloads | queue Item #2 What |
| D2 | Mechanism: extend `install_settings.py` marker-based merger (do NOT modify the merger algorithm itself) | queue Item #2 What |
| D3 | Gate hook installation on `claude mcp list | grep serena` — silently skip if absent | queue Item #2 Assumption |
| D4 | Snapshot the upstream hook recommendation at implementation time (not at queue-creation time) | queue Item #2 Snapshot |

## Phases

### Phase 0 — Upstream Re-verification (BLOCKING)

- [ ] Fetch the live `oraios.github.io/serena/02-usage/030_clients.html#claude-code` page.
- [ ] Compare to 2026-04-26 queue snapshot.
- [ ] **STOP gate:** if upstream now ships hooks as part of `setup claude-code` itself, fold this PR into Item #1 (PR-B) and abandon PR-C — do NOT proceed.
- [ ] Capture the hook definitions verbatim into `tests/fixtures/serena-hooks-upstream-snapshot-<date>.json`. Record the fetch date in the fixture's `_meta` field.

### Phase 1 — Settings Template

- [ ] Add the Serena hook block to the SuperClaude default settings template (locate via `grep -r "settings.json" src/superclaude/`).
- [ ] Wrap the block with a unique marker, e.g. `"_meta": { "source": "serena-recommended", "snapshot": "<date>" }`.
- [ ] Validate the resulting JSON parses cleanly.

### Phase 2 — Merger Integration

- [ ] Register the Serena marker in `install_settings.py` known-sources list (whatever the existing pattern is — see `CLAUDE.md` "Hooks merge (not replace)").
- [ ] Verify the merger preserves: (a) user-authored hooks NOT under the Serena marker, (b) Serena hooks marked by us (overwritable on upgrade).
- [ ] Unit test: pre-existing user hooks + Serena hooks coexist after merge.

### Phase 3 — MCP Presence Gate

- [ ] Before applying Serena hooks, run `claude mcp list` and check for the `serena` entry.
- [ ] If absent: skip hook installation; print informational message: `Serena MCP not registered. Re-run after registering Serena to enable recommended hooks.`
- [ ] If present: proceed with merge.

### Phase 4 — Regression Tests

- [ ] Test: fresh install + Serena MCP present → Serena hooks present in `settings.json`.
- [ ] Test: existing install with user hooks + upgrade → both user hooks AND Serena hooks present.
- [ ] Test: existing install with user-authored hooks that collide with Serena recommendation → user's version wins (Serena marker absent on user-authored entries).
- [ ] Test: Serena MCP not registered → hooks NOT installed, message shown.
- [ ] Test: re-install (idempotent) → no duplicate Serena hook entries.

## Validation Gates

- All existing `install_settings.py` tests pass (baseline before changes).
- New tests all pass.
- Test baseline of 1,628 passing maintained.
- Manual smoke: clean `~/.claude/`, run `make sync-user`, verify `settings.json` contents.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Upstream hook recommendation changes mid-development | Phase 0 captures snapshot; PR description records the date |
| 2 | Marker collision with another integration's hooks | Marker key includes `serena-recommended` — namespaced |
| 3 | Merger algorithm breaks existing tests | Run baseline tests in Phase 0; compare deltas after changes |
| 4 | Serena MCP absent but hooks added → silent runtime failures | Phase 3 gate prevents this (do not install hooks if Serena absent) |
| 5 | User has hand-authored Serena hooks (no marker) — upgrade overwrites | Marker presence is the discriminator; hand-authored entries lack the marker and are preserved |

## Non-Goals

- Do **not** modify the marker-based merger algorithm itself.
- Do **not** auto-register Serena MCP if absent (Item #3 / PR-A territory).
- Do **not** alter the upstream-authoritative install command.
- Do **not** ship hook payloads SuperClaude itself authored (only upstream-recommended ones from the snapshot).
