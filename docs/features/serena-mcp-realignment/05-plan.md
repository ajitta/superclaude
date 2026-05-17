---
status: draft
revised: 2026-04-26
---

# Serena MCP Realignment — Implementation Plan

**Goal:** Realign SuperClaude content (CLI install code, runtime instructions, docs, command flows) with the upstream-authoritative Serena MCP shape so that no stale references to removed-from-context tools remain, while preserving R17 (Serena-First) for symbol operations.

**Architecture:** Six sequential single-commit phases on one feature branch. Each phase narrows blast radius — install code first (so future `superclaude install` correctness is locked in immediately), then runtime instruction string (next session reads truth), then canonical docs, then active command flow, then audit pass, then validation gate. Order matches spec's recommended implementation order (Affected Surface §1–§7).

**Tech Stack:** Markdown content framework (`src/superclaude/`), Python install module (`cli/install_mcp.py`), context-loader Python (`scripts/context_loader.py`). No application code; "tests" = 8 validation gates from spec.

**Source Spec:** [`./01-discovery.md`](./01-discovery.md) (v5, status: approved-for-plan) — promoted from `docs/specs/serena-mcp-realignment-discovery-ajitta-2026-04-26.md` on 2026-05-18

**Branch:** `fix/serena-mcp-realignment` (per CLAUDE.md git conventions; this is a correctness fix for stale references)

**Non-Goals (lifted from spec):** No R17 modification. No `serena setup claude-code` delegation in `install_mcp.py` (Q6 default = stay manual). No header-notes on historical `docs/specs/2026-03-*`. No hooks integration (deferred enhancement).

---

## Phase 1: CLI install code (install_mcp.py)

**Files:** Modify: `src/superclaude/cli/install_mcp.py:39`

**Why first:** Doc-only fixes get defeated by the next `superclaude install`. Locking in correct install command first means every fresh install from this point produces the right MCP config, regardless of doc state.

- [ ] Step 1: Read `src/superclaude/cli/install_mcp.py` lines 25–60 to confirm Serena entry structure
- [ ] Step 2: Replace the `"command": "uvx --from git+...serena start-mcp-server --context claude-code --enable-web-dashboard false --enable-gui-log-window false"` value with `"command": "serena start-mcp-server --context=claude-code --project-from-cwd"` (matches upstream `client_setup.py::ClientSetupHandlerClaudeCode.get_mcp_server_options()` exactly — no `--enable-*` flags per Risk-2 resolution)
- [ ] Step 3: Verify with `grep -n "project-from-cwd" src/superclaude/cli/install_mcp.py` → expect line 39
- [ ] Step 4: Verify NO regression of `--enable-` references in same file: `grep -nc "enable-web-dashboard\|enable-gui-log-window" src/superclaude/cli/install_mcp.py` → expect `0`
- [ ] Step 5: `git add src/superclaude/cli/install_mcp.py && git commit -m "fix(install): adopt upstream Serena MCP launch command (--project-from-cwd, drop --enable-* flags)"`

**Validation gates passed by this phase:** #2 (install code carries new command), partial #3 (args portion of install_mcp.py)

---

## Phase 2: Runtime instruction string (context_loader.py)

**Files:** Modify: `src/superclaude/scripts/context_loader.py:156–164`

**Why second:** This string is injected into agent context on every session start. Out-of-date instructions cause agents to attempt removed tools at runtime, even if docs are correct.

- [ ] Step 1: Read lines 150–170 of `context_loader.py` to confirm the Serena `INSTRUCTION_MAP` entry shape
- [ ] Step 2: Edit the Serena instruction string:
  - Change `"Serena (22 tools): ..."` → `"Serena (17 tools): ..."`
  - Remove the sentence `"Use search_for_pattern when symbol name is unknown. "` entirely (tool not exposed in claude-code context)
  - Change `"Memory (6): activate_project → list_memories → read/write/edit/rename/delete_memory."` → `"Memory (6): list_memories → read/write/edit/rename/delete_memory. Project auto-active via --project-from-cwd; verify with check_onboarding_performed if uncertain."`
  - Keep all other content (symbol-ops list, decision rule, thinking-tools note, prioritize-symbolic note) unchanged
- [ ] Step 3: Verify: `grep -n "22 tools\|search_for_pattern\|activate_project" src/superclaude/scripts/context_loader.py` → expect empty (or only matches outside this instruction string)
- [ ] Step 4: `git add src/superclaude/scripts/context_loader.py && git commit -m "fix(context-loader): update Serena runtime instruction (17 tools, drop removed-tool refs)"`

**Validation gates passed:** #6 (context_loader.py contains no removed tool name and no "22 tools" claim)

---

## Phase 3: Canonical doc + MCP README (MCP_Serena.md, mcp/README.md)

**Files:** Modify: `src/superclaude/mcp/MCP_Serena.md` (multiple sections); Modify: `src/superclaude/mcp/README.md:17`

**Why third:** Docs are user/agent-facing reference. After install code and runtime are correct, ensure the documentation people read matches reality.

### 3a. MCP_Serena.md — five concrete edits (per spec Affected Surface item #3)

- [ ] Step 1: **Initialization section (lines 6–10)**: drop step 3 (`activate_project`) and the trailing "If onboarding not performed: call `onboarding` before `activate_project`" line. Replace with: `Project auto-activates from CWD via --project-from-cwd flag. If onboarding not performed: call onboarding.`
- [ ] Step 2: **Tool catalog (lines 12–42)**:
  - Change `<tools note="22 tools active in claude-code context">` → `<tools note="17 tools active in claude-code context">`
  - Remove the entire **Search and Navigation (3)** category block (lines 31–34)
  - In **Project Management**, change header `(5)` → `(3)` and remove the `activate_project` and `get_current_config` bullet lines
- [ ] Step 3: **Add new "Fallback for context-disabled tools" section** immediately after Tool catalog, before "Thinking Tools" section. Use the spec's Fallback Mapping Table verbatim (5 rows: `activate_project`, `get_current_config`, `search_for_pattern`, `list_dir`, `find_file` → respective fallbacks). Add one-sentence preface: "These tools exist in upstream Serena but are not exposed in the claude-code context (per upstream README §How Serena Works). Use the native fallback when you would have reached for one."
- [ ] Step 4: **Memory Patterns (line 81)**: change `activate_project → list_memories → read_memory("pm_context") → report context` → `list_memories → read_memory("pm_context") → report context (project auto-active via --project-from-cwd)`
- [ ] Step 5: **Install line (line 105)**: replace with:
  ```
  **Install:** `claude mcp add --scope user serena -- serena start-mcp-server --context=claude-code --project-from-cwd`
  (Equivalent shorthand: `serena setup claude-code`. Already installed via old command? `claude mcp remove serena` first, then re-run.)
  ```
- [ ] Step 6: **Examples table (line 113)**: change row `| load project context | activate_project → list_memories | Session initialization |` → `| load project context | list_memories → read_memory | Project auto-active; just read memory |`

### 3b. mcp/README.md tool count

- [ ] Step 7: Edit `src/superclaude/mcp/README.md:17`: change `(22 tools)` → `(17 tools)`

### 3c. Verify and commit

- [ ] Step 8: Validation grep:
  ```bash
  grep -rn -E "22 tools|activate_project|get_current_config|search_for_pattern|list_dir|find_file" src/superclaude/mcp/
  ```
  Expect: only the new Fallback Mapping Table rows and the "not exposed" preface in `MCP_Serena.md`. No survivors in `mcp/README.md`.
- [ ] Step 9: `git add src/superclaude/mcp/MCP_Serena.md src/superclaude/mcp/README.md && git commit -m "docs(mcp): realign Serena docs to 17 tools + upstream-authoritative install"`

**Validation gates passed:** #4 (tool count = 17 in both files), partial #1 (no stale tool refs outside MCP_Serena.md fallback table after this + Phase 4)

---

## Phase 4: Active command flow (load.md)

**Files:** Modify: `src/superclaude/commands/load.md` (lines 14, 17, 21, 33, 35, 41, 67, 70 per spec)

**Why fourth:** `/sc:load` is the most heavily-affected command — Step 1 currently calls `activate_project()` which doesn't exist. After this phase, the active session-start flow stops attempting non-existent tools.

- [ ] Step 1: Read `src/superclaude/commands/load.md` end-to-end to confirm line layout (~80 lines expected)
- [ ] Step 2: Edit Step 1 of the workflow (line 14): `1. Initialize: activate_project() → check_onboarding_performed()` → `1. Initialize: MCP auto-activates from CWD; verify with check_onboarding_performed()`
- [ ] Step 3: Edit Step 4 (line 17): replace `list_dir` with `Glob` in the discovery tool list
- [ ] Step 4: Edit Tools section (lines 33–35):
  - Remove the `activate_project: Serena project activation (primary)` bullet entirely
  - Change `get_symbols_overview/list_dir: Serena structure analysis` → `get_symbols_overview: Serena structure analysis (use native Glob for directory listing)`
- [ ] Step 5: Edit Activation pattern (line 41): change `Serena activate → Serena memories → auto memory → context establish` → `Serena memories (auto-active) → auto memory → context establish`
- [ ] Step 6: Audit other Serena references in this file (lines 21, 67, 70 — fallback wording, dual-persistence note, bounds) — confirm they reference memory/symbol tools that remain valid; no edits expected
- [ ] Step 7: Validation grep:
  ```bash
  grep -n -E "activate_project|list_dir|find_file|search_for_pattern|get_current_config" src/superclaude/commands/load.md
  ```
  Expect: empty.
- [ ] Step 8: `git add src/superclaude/commands/load.md && git commit -m "fix(load): drop activate_project (auto from CWD), replace list_dir with native Glob"`

**Validation gates passed:** #5 (`/sc:load` step 1 no longer calls non-existent tool), completes #1 (no stale tool refs anywhere outside MCP_Serena.md fallback table)

---

## Phase 5: Audit pass (save.md, reflect.md)

**Files:** Read-only audit + conditional edit: `src/superclaude/commands/save.md`, `src/superclaude/commands/reflect.md`

**Why fifth:** Spec marks these as "audit only, expected: no change" — but per Risk-5 and the auto-handle policy, if audit reveals removed-tool references, fix them in this phase rather than expanding scope mid-implementation.

- [ ] Step 1: Read `save.md` end-to-end. Confirmed-valid references (memory tools): `write_memory`, `read_memory`, `list_memories`. These remain.
- [ ] Step 2: Run grep in `save.md` for removed-tool names:
  ```bash
  grep -n -E "activate_project|list_dir|find_file|search_for_pattern|get_current_config" src/superclaude/commands/save.md
  ```
- [ ] Step 3: If grep returns matches → fix them inline (replace with appropriate fallback or remove). If empty → no change needed.
- [ ] Step 4: Repeat Step 1–3 for `reflect.md`
- [ ] Step 5: Decision branch:
  - **If both files unchanged**: skip commit (no work to record)
  - **If either file changed**: `git add <changed> && git commit -m "fix(save|reflect): remove stale Serena tool references"`

**Validation gates passed:** completes #1 across `commands/`, contributes to #7 enforcement (R17 unchanged — these files do not modify R17)

---

## Phase 6: Final validation gate

**Files:** No edits — verification only.

**Why last:** Run all 8 validation gates from spec §Validation Criteria. If any fail, return to corresponding phase.

- [ ] Gate 1 — No stale tool references outside MCP_Serena.md:
  ```bash
  grep -rn -E "activate_project|search_for_pattern|list_dir|find_file|get_current_config" src/superclaude/ \
    | grep -v "src/superclaude/mcp/MCP_Serena.md"
  ```
  Expected: empty.
- [ ] Gate 2 — Install code carries new command:
  ```bash
  grep -n "project-from-cwd" src/superclaude/cli/install_mcp.py
  grep -nc "enable-web-dashboard\|enable-gui-log-window" src/superclaude/cli/install_mcp.py
  ```
  Expected: line 39 hit; second grep returns `0`.
- [ ] Gate 3 — Args portion equals upstream `["--context=claude-code", "--project-from-cwd"]`:
  Inspect `install_mcp.py:39` line manually; confirm no extra flags, no missing flags. Doc command in `MCP_Serena.md` matches `claude mcp add --scope user serena -- ...` upstream format.
- [ ] Gate 4 — Tool count = 17 in both files:
  ```bash
  grep -nE "17 tools|22 tools" src/superclaude/mcp/MCP_Serena.md src/superclaude/mcp/README.md
  ```
  Expected: only `17 tools` matches; no `22 tools`.
- [ ] Gate 5 — `/sc:load` step 1 no longer calls `activate_project()`:
  ```bash
  grep -n "activate_project" src/superclaude/commands/load.md
  ```
  Expected: empty.
- [ ] Gate 6 — `context_loader.py` Serena instruction string clean:
  ```bash
  grep -n -E "22 tools|search_for_pattern|activate_project →" src/superclaude/scripts/context_loader.py
  ```
  Expected: empty.
- [ ] Gate 7 — R17 byte-equality:
  ```bash
  git diff src/superclaude/core/RULES.md
  ```
  Expected: empty (file untouched across all phases).
- [ ] Gate 8 — Dashboard flag decision documented: confirm Phase 1 commit message references "drop `--enable-*` flags" with upstream rationale.
- [ ] Step 9: If all 8 gates pass → push branch and open PR. If any gate fails → return to the phase that owns it, fix, re-run gate.

**No commit in this phase** unless gate failures triggered fixes that weren't committed individually.

---

## Risks & Mitigations (lifted from spec, plan-time stance)

| Risk | Plan-time mitigation |
|---|---|
| R1 — hidden references in unreviewed files | Gate 1 grep covers full `src/superclaude/`; Phase 5 audit handles `save.md`/`reflect.md` explicitly |
| ~~R2 — dropped --enable-* flags~~ | **Resolved at spec time**; Phase 1 just enacts |
| R3 — old install on user machines | Migration hint shipped in Phase 3a Step 5 |
| R4 — R17 weakening from 4b creep | Gate 7 enforces byte-equality |
| R5 — save/reflect audit reveals deeper coupling | Phase 5 absorbs (per auto-handle policy) |
| R6 — catalog snapshot drift | At start of execution, re-run `claude mcp list` and confirm `mcp__serena__*` count = 17 before Phase 1 |

## Pre-flight checklist (run once before Phase 1)

- [ ] `git status` clean (or any pending changes are intentional baseline)
- [ ] `claude mcp list` shows `serena: serena start-mcp-server --context=claude-code --project-from-cwd  - ✓ Connected`
- [ ] Branch created: `git checkout -b fix/serena-mcp-realignment`
- [ ] Spec re-read: [`./01-discovery.md`](./01-discovery.md) v5

## Handoff

Ready for `/sc:implement --plan docs/features/serena-mcp-realignment/05-plan.md`. Each phase is a single commit; total 6 phases, ≤6 commits. Phase 5 may produce zero commits if audit clean.
