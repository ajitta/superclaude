---
status: deprecated
revised: 2026-04-27
---

> **2026-04-27 — Reverted.** PR #3 was merged then reverted in a follow-up
> simplification PR. Rationale: stale-entry migration is not in upstream
> Serena's documented flow (`010_installation.html` / `030_clients.html`),
> and `docs/troubleshooting/serena-installation.md` already covers the
> manual `claude mcp remove serena` step. The 157-line surgical-edit
> surface + 19 tests was disproportionate to the one-line manual hint it
> automated. Item #3 of the follow-ups queue is now closed as
> "documented manually, no automation."

# Serena Follow-ups — PR-A: Existing-User Migration Automation

**Source:** [follow-ups queue](serena-mcp-realignment-followups-ajitta-2026-04-26.md) Item #3.
**Branch (proposed):** `fix/serena-mcp-migration-automation`
**Sequencing:** First in 3-PR queue (PR-A → PR-B → PR-C). Lands before PR-B to avoid `install_mcp.py` merge conflicts.

## Goal

Replace the 1-line manual hint (`claude mcp remove serena && <re-run>`) shipped in PR #2 with detection + prompted execution inside `install_mcp.py`. After this PR, a user upgrading from a pre-realignment install runs `superclaude install` once and ends up on the new flag set.

## Done When

- A user with the old install command runs `superclaude install` (or equivalent) once and ends up on the new flag set without hand-running `claude mcp remove`.
- Fresh-install path (no existing Serena MCP entry) is unchanged.
- `--no-interactive` mode fails fast with a copy-pasteable manual command instead of prompting.

## Resolved Decisions (carry from queue)

| # | Decision | Confirmed |
|---|----------|-----------|
| D1 | Detection signal: missing `--project-from-cwd` OR presence of stale `--enable-*` flag | from queue Item #3 |
| D2 | Migration is opt-in via prompt (default = no auto-execute) | queue Risk profile |
| D3 | `--no-interactive` opt-out path required | queue Risk profile |
| D4 | Scope of `claude mcp remove` matches scope of install (`--scope user`) | matches PR #2 install command |

## Phases

### Phase 0 — Preparation (read-only)

- [ ] Read `src/superclaude/scripts/install_mcp.py` end-to-end; identify the Serena install branch.
- [ ] Capture sample `claude mcp list` JSON output for: (a) no Serena, (b) old-flag Serena, (c) new-flag Serena. Save as fixtures.
- [ ] Confirm `claude mcp list` JSON schema is stable enough to parse (else fall back to text parsing — document the choice).

### Phase 1 — Detection

- [ ] Add `_detect_stale_serena(mcp_list_output) -> bool` to `install_mcp.py`.
  - Returns `True` if Serena entry exists AND any of: missing `--project-from-cwd`, contains `--enable-web-dashboard`, contains `--enable-gui-log-window`.
  - Returns `False` otherwise (no entry, or already on new flags).
- [ ] Unit tests against the 3 fixtures from Phase 0.

### Phase 2 — Prompted Migration

- [ ] On detection in interactive mode, prompt: `Stale Serena MCP install detected. Migrate now (runs 'claude mcp remove serena' then re-installs)? [y/N]`
- [ ] On `y`: subprocess `claude mcp remove serena --scope user`, then proceed with the normal new-flag install.
- [ ] On `n` (or any non-`y`): skip migration; do NOT attempt re-install (avoids confusing partial state); print one-line manual command for later.

### Phase 3 — `--no-interactive` Opt-out

- [ ] Detect non-interactive context (`--no-interactive` flag OR `not sys.stdin.isatty()`).
- [ ] In non-interactive mode + stale detected: exit non-zero with stderr:
  ```
  Stale Serena MCP install detected. Run manually:
    claude mcp remove serena --scope user && <new install command>
  ```
- [ ] Fresh install in non-interactive mode is unaffected.

### Phase 4 — Tests

- [ ] Integration test: fresh env (no Serena) → install succeeds, no prompt.
- [ ] Integration test: stale env + interactive + `y` → migrates and re-installs cleanly.
- [ ] Integration test: stale env + interactive + `n` → no-op exit, manual hint shown.
- [ ] Integration test: stale env + `--no-interactive` → non-zero exit, hint on stderr.
- [ ] Idempotency: run install twice in a row on already-migrated env → second run is no-op.
- [ ] Smoke: real machine — verified by hand once before merge.

## Validation Gates

- All existing `install_mcp.py` tests pass (baseline captured in Phase 0).
- New tests all pass.
- Test baseline of 1,628 passing (per `CLAUDE.md`) is maintained or grows — no regression.
- One manual smoke test recorded in PR description.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| 1 | `claude mcp list` JSON format changes between CLI versions | Phase 0 captures snapshot; parser falls back to regex on JSON-parse failure |
| 2 | User's MCP config has fields we don't expect | Defensive parsing — only inspect the `serena` entry's command/args; ignore unknown fields |
| 3 | Subprocess hangs (CLI prompt) | Add timeout + clear error |
| 4 | User declines migration but later install fails | Print copy-pasteable manual command on decline so user can self-recover |
| 5 | Race: another tool modifies MCP config between detect and remove | Re-read MCP list right before `remove`; if entry no longer matches stale signal, skip the remove |

## Non-Goals

- Do **not** auto-migrate other MCP servers (Serena-only — other servers are out of scope).
- Do **not** alter the upstream-authoritative install command (PR #2 policy).
- Do **not** touch `install_settings.py` or hooks (that is PR-C / Item #2).
- Do **not** change the existing migration documentation hint shipped in PR #2 (it remains the fallback for `--no-interactive` users).
