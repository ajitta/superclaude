---
status: approved-for-plan
revised: 2026-04-26
---

# Serena MCP Realignment — Discovery Spec

## Context

The Serena MCP server has been re-installed with a new launch command and a reduced tool catalog. The existing SuperClaude content (docs, command flows, runtime instruction strings) was authored against the previous shape and now contains stale references that will cause agents to call tools that no longer exist.

**Current MCP state (verified 2026-04-26 04:23 GMT+9 via `claude mcp list`):**
```
serena: serena start-mcp-server --context=claude-code --project-from-cwd  - ✓ Connected
```

**Tool catalog delta (deferred-tools snapshot 2026-04-26 04:23 GMT+9; `claude mcp list` may differ across sessions):**

| Category | SC docs claim | Exposed in claude-code context | Not exposed |
|---|---|---|---|
| Symbol Operations | 8 | 8 ✅ | — |
| Memory | 6 | 6 ✅ | — |
| Project Management | 5 | 3 | `activate_project`, `get_current_config` |
| Search & Navigation | 3 | 0 | `search_for_pattern`, `list_dir`, `find_file` (whole category) |
| **Total** | **22** | **17** | **5 tools** |

**Framing note:** "Not exposed" rather than "removed" — these tools may still exist in the upstream Serena server but are filtered out by the `claude-code` context (parallel to how the doc already describes `think_about_*` tools). Verifying upstream-vs-context cause is out of scope; the spec treats them as unavailable for SC content purposes.

**Key behavioral change:** `--project-from-cwd` flag now auto-activates the project from the current working directory at MCP startup, replacing the explicit `activate_project` call. Upstream source description: *"Auto-detect project from current working directory (searches for `.serena/project.yml` or `.git`, falls back to CWD). Intended for CLI-based agents like Claude Code, Gemini and Codex."* (`src/serena/cli.py`, oraios/serena@main).

**Upstream-authoritative install command** (verified 2026-04-26 via `oraios/serena/src/serena/config/client_setup.py::ClientSetupHandlerClaudeCode.apply`):
```
claude mcp add --scope user serena -- serena start-mcp-server --context=claude-code --project-from-cwd
```
This is exactly what `serena setup claude-code` runs internally. Note: upstream does NOT pass `--enable-web-dashboard false` or `--enable-gui-log-window false`, confirming Risk-2 resolution (see Risks).

**Upstream-confirmed "not exposed" framing** (oraios/serena `README.md` §"How Serena Works"):
> *"When Serena is used inside an agentic harness such as Claude Code or Codex, these tools are typically disabled by default, since the surrounding harness already provides overlapping file, search, and shell capabilities."* — listing `search_for_pattern`, `replace_content`, `list_dir`, `find_file`, `read_file`, `execute_shell_command`.

This validates the spec's "not exposed in claude-code context" wording and explains why the Search & Navigation category is empty by design — not an upstream regression.

**Hooks recommendation (out of scope, noted for future):** Upstream's `setup claude-code` post-install message recommends adding hooks to `.claude/settings.json` (link: `oraios.github.io/serena/02-usage/030_clients.html#claude-code`). Treated as a follow-up enhancement, not in this spec.

## Goal

Realign SuperClaude content with the actual Serena MCP shape so that agents and commands no longer reference removed tools, document the new install command, and provide an explicit native-tool fallback table for migrated users — without weakening the project's R17 (Serena-First) principle for symbol operations.

## Resolved Decisions

| # | Question | Decision | Mode |
|---|---|---|---|
| Q1 | Improvement scope | **1b**: MCP_Serena.md + context_loader.py instruction string + load.md / save.md / reflect.md | confirmed |
| Q2 | Document fallbacks for removed tools | **2a**: Explicit mapping table in MCP_Serena.md | confirmed |
| Q3 | Install guide policy | **3a + 1-line migration hint**: Use upstream-authoritative `claude mcp add --scope user serena -- serena start-mcp-server --context=claude-code --project-from-cwd` (mirrors `serena setup claude-code`); one-line note for users with prior install (`claude mcp remove serena && <new install>`) | confirmed |
| Q6 | install_mcp.py implementation strategy (NEW after upstream research) | **Default: stay manual** — keep `install_mcp.py` constructing the MCP config string directly with the upstream-authoritative command, matching the existing pattern for other MCP servers in that file. Delegating to `serena setup claude-code` (subprocess call) deferred as future enhancement (decouples SC from Serena CLI presence assumption) | inferred default — flag for user review during plan |
| Q4 | `/sc:load` workflow | **4b (narrow reading)**: Lighten `/sc:load` only — auto-activation acknowledged, fewer Serena calls at session start. **R17 (Serena-First) for symbol ops remains unchanged.** | confirmed |
| Q5 | Self-review gate | **5a**: Spec → mandatory `/sc:review` before `/sc:plan` | confirmed |

All decisions are `confirmed` (literal option-letter responses or explicit free-text confirmations). No delegated decisions.

## Affected Surface (Evidence-Based)

**Recommended implementation order** (CLI install code first → all users get correct MCP on next install; then runtime instruction string → next session loads accurate Serena guidance; then docs/commands → users reading docs see truth):

1. `src/superclaude/cli/install_mcp.py:39` — **Code, not docs**. The `superclaude install` CLI writes the OLD install command into MCP config. Docs-only fix is insufficient — every fresh `superclaude install` would re-introduce the old MCP. Replace the command string with the upstream-authoritative `serena start-mcp-server --context=claude-code --project-from-cwd` (Risk-2 resolved: drop both `--enable-*` flags to match upstream `client_setup.py`). Per Q6 default, keep the existing manual-config pattern; do NOT switch to `subprocess.run(["serena", "setup", "claude-code"])` in this PR.
2. `src/superclaude/scripts/context_loader.py` (lines 156–164, Serena instruction string) — Update "22 tools" → "17 tools"; remove `search_for_pattern` reference; replace `activate_project → list_memories` with `list_memories → read/write/...` (CWD auto-activation noted).
3. `src/superclaude/mcp/MCP_Serena.md` — Five concrete edits:
   - **Initialization section (lines 6–10)**: drop step 3 (`activate_project`) and the trailing "If onboarding not performed: call `onboarding` before `activate_project`" line. Replace with: "Project auto-activates from CWD via `--project-from-cwd` flag. If onboarding not performed: call `onboarding`."
   - **Tool catalog (lines 12–42)**: change `note="22 tools active in claude-code context"` → `note="17 tools active in claude-code context"`. Remove Search & Navigation category entirely. Remove `activate_project` and `get_current_config` from Project Management category (5→3).
   - **Install line (line 105)**: replace with upstream-authoritative `claude mcp add --scope user serena -- serena start-mcp-server --context=claude-code --project-from-cwd` + 1-line migration hint per Q3 (`Already installed via old command? claude mcp remove serena && <re-run above>`). Optionally note the `serena setup claude-code` shorthand as an equivalent.
   - **Memory Patterns (line 81)**: change `activate_project → list_memories → ...` → `list_memories → read_memory(...) → ...` (CWD auto-activation makes the call redundant).
   - **Examples table (line 113)**: change "load project context | `activate_project` → `list_memories`" → "load project context | `list_memories` → `read_memory`" (note: project auto-active).
   - **New: Fallback mapping table** (per Q2) inserted after Tool catalog.
4. `src/superclaude/mcp/README.md:17` — Update "Serena | ... | (22 tools)" → "(17 tools)".
5. `src/superclaude/commands/load.md` (lines 14, 17, 21, 33, 35, 41, 67, 70) — Step 1 → "MCP auto-activates from CWD; verify with `check_onboarding_performed`"; replace `list_dir` with native `Glob`; remove `activate_project` from tool list and flow.
6. `src/superclaude/commands/save.md` (lines 15, 22, 32, 39, 49, 50, 56, 85) — Audit; expected: no change beyond confirming memory tool references still valid.
7. `src/superclaude/commands/reflect.md` (lines 2, 45) — Audit; expected: no change (mission references memory/symbol ops which remain valid).

**Out of scope (intentional):**
- `docs/specs/2026-03-2*-*.md` (3 historical design docs mentioning removed tools): point-in-time records, not living docs. Per Q1 = 1b (not 1c), no header notes added.
- Worktree copies under `.claude/worktrees/lucid-kalam/`: out of scope for source tree.
- R17 in `src/superclaude/core/RULES.md`: unchanged. Serena-First remains primary for symbol ops.
- `src/superclaude/agents/*.md`, `src/superclaude/modes/*.md`, `src/superclaude/skills/*`: grep returned no removed-tool references (verified 2026-04-26).
- `MEMORY.md` (auto-memory) and `.serena/memories/` (Serena memory): user/project memory stores, not framework content. Will pick up correct values on next session refresh.
- Upstream investigation (whether tools were removed from Serena server vs filtered by claude-code context): treated as unknown; SC content uses neutral "not exposed" language.

## Fallback Mapping Table (to be embedded in MCP_Serena.md)

| Removed Serena tool | Native fallback | When to use |
|---|---|---|
| `activate_project` | (automatic via `--project-from-cwd`) | No action needed; verify with `check_onboarding_performed` if uncertain |
| `get_current_config` | (none — MCP itself reports tools at startup) | Use `claude mcp list` from shell when you need to verify |
| `search_for_pattern` | native `Grep` | Regex/text search; same capability, no LSP overhead |
| `list_dir` | native `Glob` (e.g., `**/*.py`) | Directory listing and file discovery |
| `find_file` | native `Glob` | Filename pattern matching |

## Non-Goals

- Removing or downgrading R17 (Serena-First) for symbol operations.
- Restructuring `/sc:save` or `/sc:reflect` beyond removing stale tool references.
- Adding a "migration guide" document — the 1-line hint in MCP_Serena.md is the entire migration surface per Q3.
- Updating historical design specs in `docs/specs/2026-03-*`.

## Validation Criteria

After implementation, all six gates must pass:

1. **No stale tool references outside MCP_Serena.md**:
   ```bash
   grep -rn -E "activate_project|search_for_pattern|list_dir|find_file|get_current_config" src/superclaude/ \
     | grep -v "src/superclaude/mcp/MCP_Serena.md"
   ```
   Expected: empty output. (MCP_Serena.md is allowed to mention the names inside the fallback mapping table and in the "not exposed" notice.)
2. **Install code carries new command**: `grep -n "project-from-cwd" src/superclaude/cli/install_mcp.py` returns line 39, and the line does NOT contain `enable-web-dashboard` or `enable-gui-log-window`.
3. **Install_mcp.py command tail equals upstream `get_mcp_server_options()` output**: the args portion in `install_mcp.py:39` matches `["--context=claude-code", "--project-from-cwd"]` exactly (no extra flags, no missing flags). The doc's user-facing install command in `MCP_Serena.md` matches the upstream `claude mcp add --scope user serena -- ...` format.
4. **Tool count claims** in `MCP_Serena.md` and `mcp/README.md` both read **17** (not 22).
5. **`/sc:load` step 1** no longer calls `activate_project()`.
6. **`context_loader.py` Serena instruction string** contains no removed tool name and no "22 tools" claim.
7. **R17 unchanged**: `git diff src/superclaude/core/RULES.md` shows no R17 modification (Serena-First for symbol ops preserved).
8. **Dashboard/GUI flag decision documented** in plan or implementation commit message (per Risk-2 outcome).

## Risks

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | Other agent/command files reference removed tools (not surfaced in initial grep) | Stale runtime calls persist | `/sc:review` re-runs the canonical grep (Validation #1) across full `src/superclaude/` tree |
| 2 | ~~New install command drops `--enable-web-dashboard false --enable-gui-log-window false` flags~~ **RESOLVED 2026-04-26 via upstream source check** | (was: dashboard/GUI may auto-open in headless CI) | **Resolved**: upstream `client_setup.py::ClientSetupHandlerClaudeCode.get_mcp_server_options()` returns only `["--context=claude-code", "--project-from-cwd"]` — no `--enable-*` flags. Match upstream behavior; drop both flags from `install_mcp.py`. If a user later reports dashboard popping up in headless mode, file an upstream issue rather than diverging from `serena setup claude-code` |
| 3 | User has older Serena install lacking `--project-from-cwd` flag support | Install command in doc fails | 1-line migration hint addresses this (Q3) |
| 4 | Reading 4b too broadly during plan/implement → R17 weakening | Lose semantic-search advantage | Explicit non-goal stated; `/sc:review` Validation #7 enforces R17 byte-equality |
| 5 | `save.md` / `reflect.md` audit reveals deeper coupling than expected | Scope expansion mid-implementation | Plan phase reads both files in full and surfaces findings before edits |
| 6 | Tool catalog snapshot (2026-04-26 04:23) drifts before implementation lands | Implementation based on stale capability map | Re-run `claude mcp list` and confirm `mcp__serena__*` count = 17 at the start of `/sc:plan` |

## Self-Review Iteration Log

- **v1 (2026-04-26)**: Initial draft after Socratic Q1–Q5 with user. All 5 decisions confirmed.
- **v2 (2026-04-26, /sc:review --loop iter 1)** — Critical fixes:
  - Added `cli/install_mcp.py:39` to Affected Surface as item #1 (doc-only fix would be defeated by next `superclaude install`).
  - Added `mcp/README.md:17` ("22 tools" claim) to Affected Surface as item #4.
  - Reframed "removed" → "not exposed in claude-code context" for accuracy.
  - Added Risk-2 (dropped `--enable-*` flags), Risk-6 (catalog snapshot drift).
  - Added implementation order, Validation #2/#3/#7/#8.
  - Added out-of-scope notes for agents (verified clean) and upstream investigation.
- **v3 (2026-04-26, /sc:review --loop iter 2)** — Hardening:
  - Made Risk-2 mitigation safe (no second MCP launch).
  - Tightened Validation #1 grep filter to "outside MCP_Serena.md".
  - Extended out-of-scope: `modes/`, `skills/`, `MEMORY.md`, `.serena/memories/` (verified clean).
- **v4 (2026-04-26, /sc:review --loop iter 3)** — Implementation precision:
  - Expanded Affected Surface item #3 (MCP_Serena.md) from a line list into 5 concrete edits, including the previously-implicit Initialization section transformation. A `/sc:plan` author can now produce edits without re-deriving them.
- **v5 (2026-04-26, post-research from `oraios.github.io/serena/02-usage/030_clients.html` + upstream source `oraios/serena@main/src/serena/`)** — Authoritative grounding:
  - Replaced inferred install command with upstream-authoritative one (verified via `client_setup.py::ClientSetupHandlerClaudeCode`).
  - Added upstream README citation confirming "not exposed" framing for Search/Nav category (intentional disable in agentic harness, not a regression).
  - **Risk-2 RESOLVED**: upstream omits `--enable-*` flags by design; spec now mandates dropping them. No plan-phase verification needed.
  - Added Q6 surfacing the new architectural choice (`install_mcp.py` manual config vs delegating to `serena setup claude-code`); inferred-default decision to stay manual, flagged for user confirmation in plan phase.
  - Added hooks recommendation as explicit follow-up (out-of-scope for this spec).
  - Added upstream description of `--project-from-cwd` semantics (searches `.serena/project.yml` or `.git`, falls back to CWD).

## Handoff

**Run `/sc:review` on this spec before `/sc:plan`. Plan handoff is gated on review.**

All 5 decisions are `confirmed` (no delegated audit needed). Standard `/sc:review` is sufficient; `--audit-delegated` is not required.
