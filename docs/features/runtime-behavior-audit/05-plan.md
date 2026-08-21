---
status: approved-for-plan
revised: 2026-08-21
---

# Runtime Behavior Audit — Implementation Plan

**Goal:** Make `/sc:` commands fire without being typed, fix the defects that corrupt user state or
silently disable the framework, and ship the result as a Claude Code plugin so it is present in
every repository.

**Architecture:** Four layers in dependency order — the model-facing contract in
`commands/*.md` (decides whether a command is ever selected; the audit says it is not, so the
diagnostic comes first), the hook scripts in `scripts/` (injection, state, guards), the CLI in
`cli/` (install-time merge and scope), and packaging on top. Code tasks are test-first against an
existing suite file; content tasks are gated by the structural tests already covering them.

**Tech Stack:** Python ≥3.10, UV, pytest (baseline 2102 passed / 28 skipped / 4 deselected), ruff.

**Source:** findings A1–A12 in [03-analysis.md](./03-analysis.md). Per-command trigger detail in
[05a-plan-trigger-tiers.md](./05a-plan-trigger-tiers.md).

---

## Decisions

D1–D6, taken 2026-08-21, are recorded with their reasoning in
[README.md](./README.md#decisions). Tasks cite them by number.

**One tension, stated plainly.** D2 and Task 8 pull opposite ways: the tier work removes model
access from eleven commands while the root cause is that model access produces no fires. They target
different halves — the eleven are where a wrong fire mutates code, writes repository state, or skips
an approval gate, and the D2 fix is making the *safe* commands get selected. So Task 8 ships its
downgrades now and holds its upgrades until Task 1 reports.

---

## Phase 1 — Root cause: why nothing fires

No code. Everything about the framework's future hinges on the answer, and Phases 2–3 do not depend
on it, so they can proceed in parallel.

### Task 1: Why 22 auto-triggerable commands never fire (A12, D2)

**Files:** Create: `docs/features/runtime-behavior-audit/06-diagnostics.md`

- [ ] Take three commands with clean Tier A wording that stay Tier A after Task 8 (`analyze`, `review`, `explain`) and the plugin skills that win the same conversational cues today (caveman, karpathy-guidelines, claude-mem)
- [ ] For each, determine whether the SuperClaude description is considered and loses, or is never considered at all — the two have different fixes
- [ ] Check the mechanical preconditions the audit did not: description length against the 1024-char skill cap, whether project-scope commands reach the model's skill list at all, and whether the negative gate ("Do NOT auto-trigger on …") suppresses more than intended
- [ ] Record the finding and the implied fix in the diagnostics doc
- [ ] Update Task 8's upgrade half and Task 13's packaging notes from the result

**Why first:** D2 makes this the root cause of A1; everything else is maintenance until it is answered.

### Task 2: Why delegation never reaches the agents (A6)

**Files:** Append: `docs/features/runtime-behavior-audit/06-diagnostics.md`

- [ ] Trace three sessions where `RULES_DELEGATION.md` `<sub_agent_decision>` should have fired; record what was chosen instead
- [ ] Classify: routing never suggests the agents, or routing suggests them and they are declined
- [ ] Feed the result into Task 12's scope

**Why:** 22 of 23 agents have zero invocations, but cutting on usage alone would delete agents that
never got a fair chance to be routed to. If Task 1 finds a shared mechanism, this is it one layer down.

---

## Phase 2 — Stop state corruption

### Task 3: Session-keyed context cache (A3)

**Files:** Modify: `src/superclaude/scripts/context_loader.py:64` | Test: `tests/unit/test_context_loader.py`

- [ ] Write failing test: run the loader twice with one prompt and `session_id` "A" then "B"; assert both emit non-empty output
- [ ] Verify it fails — today B emits 0 bytes (reproduced: A=779, B=0)
- [ ] Replace module-level `SESSION_ID = project_key()` / `CACHE_FILE` with a resolver called after `_extract_session_id()`, naming the file `claude_context_{project_key}_{session_id}.txt`; fall back to the project-only name when stdin carries no session id
- [ ] Thread the resolved path through `get_loaded_contexts()` and `mark_as_loaded()`; rename the misleading `SESSION_ID` constant
- [ ] Verify it passes: `uv run pytest tests/unit/test_context_loader.py -v`
- [ ] Commit

**Risk:** low — the worst outcome is more injection, never less.

### Task 4: Test isolation from the real `~/.claude` (A4)

**Files:** Modify: `tests/conftest.py` | Test: `tests/unit/test_loop_guard.py:274`

- [ ] Write failing test: snapshot `hook_state_dir()` under a patched `HOME`, run the guard against a bare `tmp_path`, assert no new file appears in the real home state dir
- [ ] Verify it fails — `uv run pytest` currently adds one `loop_guard_<md5>.json` per run
- [ ] Add an autouse fixture in `tests/conftest.py` pointing `HOME` at `tmp_path` for the unit suite, so any `claude_base()` fallback lands in the sandbox
- [ ] Audit `test_safety_hooks.py`, `test_scope_paths.py`, `test_eval_harness.py` for the same fallback
- [ ] Verify: `ls ~/.claude/.superclaude_hooks/ > /tmp/before && uv run pytest && ls ~/.claude/.superclaude_hooks/ | diff /tmp/before -`
- [ ] Commit

**Cleanup (D4, done):** 32 orphan files deleted 2026-08-21; the directory is now empty. Until this
task lands, every `pytest` run recreates one.

### Task 5: Per-hook install merge (A11-a)

**Files:** Modify: `src/superclaude/cli/install_settings.py` (`merge_hooks_to_settings`) | Test: `tests/unit/test_install_settings.py`

- [ ] Write failing test: settings with one SC hook under `PostToolUse`, merge a two-hook `PostToolUse` config without `--force`, assert both present
- [ ] Verify it fails — the current per-event-type skip returns "Hooks already exist … (use --force to update)" and drops the new hook
- [ ] Replace the `has_sc_hooks and not force` early-`continue` with a per-hook check: add any shipped hook whose (matcher, script) signature is absent; leave existing entries untouched unless `--force`. `_hook_entry_signature` and `_dedup_hook_array` already provide the identity
- [ ] Add a registered-vs-shipped hook count to `superclaude install --list-all` so a frozen install is visible without diffing settings files
- [ ] Verify: `uv run pytest tests/unit/ -k "settings or hooks" -v`, then re-run the install on `oasis-nakama-dev` and confirm `prettier_hook.py` appears in its `settings.local.json`
- [ ] Commit

---

## Phase 3 — Close the silent-failure paths

### Task 6: Resolve command-name typos and retired names (A7c)

**Files:** Modify: `src/superclaude/scripts/context_loader.py` | Test: `tests/unit/test_context_loader.py`

- [ ] Write failing test: `/sc:analayze` names `/sc:analyze`; `/sc:workflow` names `/sc:roadmap`; an unknown name injects no command context
- [ ] Verify it fails — both currently emit no notice and still pull 1,469 bytes of command context
- [ ] Extend the `resolve_flags` Levenshtein ≤ 2 fallback to the `/sc:<name>` token against the 36 command names; add a retired-name map (`workflow → roadmap`)
- [ ] Emit one comment naming the substitution — never silently rewrite — and suppress command-context injection when the name resolves to nothing
- [ ] Verify: `uv run pytest tests/unit/test_context_loader.py -v`
- [ ] Commit

### Task 7: Deprecation notices for retired flags (A7a, A7b, D5)

**Files:** Modify: `src/superclaude/scripts/context_loader.py` | Test: `tests/unit/test_context_loader.py`

- [ ] Write failing test: `--think-hard` and `--parellel` each produce one notice; `--effort` and `--ultrathink` produce none
- [ ] Verify it fails — all four are silent today (`--think` 175, `--think-hard` 145, `--effort` 307, `--parellel` 159 uses)
- [ ] Add a retired-flag map naming the replacement (`--think` family retired in `0cdf20f`; `--effort` removed in `06d972b`, now a native control); map `parallel` to `--delegate` / `--concurrency`
- [ ] Recognize native Claude Code controls (`--effort`, `--ultrathink`) and stay silent on them
- [ ] Verify: `uv run pytest tests/unit/test_context_loader.py -v`
- [ ] Commit

Per D5 the flag is not restored — the one-canonical-name rule at `context_loader.py:250-255`
stands, and the notice carries the redirect.

---

## Phase 4 — Trigger surface and hygiene

### Task 8: Realign the trigger tier (A12)

**Files:** Modify: `src/superclaude/commands/{git,brainstorm,design,plan,roadmap,improve,insight,pm,task,troubleshoot,document}.md` | Test: `tests/unit/test_command_structure.py`

- [ ] Rewrite each `description` positive cue to "Use ONLY when user explicitly types `/sc:X`", keeping the existing negative gate and staying ≤1024 chars
- [x] `git` also carries `disable-model-invocation: true` (applied 2026-08-21) — wording rewrite still due, as `auto-improve` has both
- [ ] Verify: `uv run pytest tests/unit/test_command_structure.py -v` — the own-slash-command and negative-gate assertions must still pass
- [ ] Commit
- [ ] **Hold until Task 1 reports:** the two Tier B → A upgrades (`select-tool`, `index-repo`) and any rewriting of the 15 auto-triggerable descriptions

**Rationale:** four of the eleven sit behind `RULES_DOCS.md` `workflow_gates` and would create phase
documents unasked; `git` rewrites history; `improve` mutates code; `troubleshoot` writes a test and
applies a fix; `document --type inline` edits source files; `insight` appends to `insights.jsonl`;
`pm` and `task` orchestrate sub-agents. Tier A shrinks 22 → 13; full classification
in [05a-plan-trigger-tiers.md](./05a-plan-trigger-tiers.md).

### Task 9: Garbage-collect runtime state (A8)

**Files:** Modify: `src/superclaude/scripts/context_reset.py` (or a helper in `src/superclaude/utils/`) | Test: `tests/unit/test_scope_paths.py`

- [ ] Write failing test: an aged state file in `hook_state_dir()` is removed on `SessionStart` while live state survives
- [ ] Verify it fails — nothing prunes state files today; `loop_guard.py` prunes entries inside a file, not the files
- [ ] Delete state files older than 7 days; prune `mcp_fallbacks.json` entries not keyed to the current session; drop keys for servers absent from `MCP_SERVERS` (`magic`, `morphllm`)
- [ ] Verify: `uv run pytest tests/unit/ -k "scope_paths or mcp_fallback" -v`
- [ ] Commit

### Task 10: Session-start output reflects real state (A10)

**Files:** Modify: `src/superclaude/scripts/session_init.py:202-207` | Test: `tests/unit/test_session_init.py`

- [ ] Write failing test: startup output contains no capability claim the hook did not actually check
- [ ] Replace the five hardcoded checkmarks with either nothing or a line derived from real state
- [ ] Verify: `uv run pytest tests/unit/test_session_init.py -v`
- [ ] Commit

---

## Phase 5 — Repair and right-size

### Task 11: Give `INSIGHT:` a real producer (A5, D3)

**Files:** Modify: `src/superclaude/scripts/insight_writer.py`, `src/superclaude/hooks/hooks.json`, `src/superclaude/commands/insight.md` | Test: `tests/unit/test_insight_writer.py`

The harvester works; nothing produces the markers it scans for. Per D3 the subsystem is repaired.

- [ ] Write failing test: a session that completes a named workflow leaves at least one pending insight
- [ ] Verify it fails — 0 entries since 2026-05-08 with the hooks installed and exiting 0
- [ ] Pick the producer and implement one of: a `Stop`-hook prompt that asks for an `INSIGHT:` line when the session changed code, or a rule that makes emission part of a named workflow step (`/sc:reflect`, `/sc:save`)
- [ ] Keep the marker contract unchanged so `cmd_harvest`'s regex at `insight_writer.py:57-62` still matches
- [ ] Verify: `uv run pytest tests/unit/test_insight_writer.py -v`, then run a real session and confirm a pending entry appears
- [ ] Commit

**Success criterion:** insights accumulate without the user typing `/sc:insight`. If that does not
hold after a week of real use, reopen the retire option.

### Task 12: Right-size the agent roster and its memory path (A6, A11-b)

**Files:** Move: `src/superclaude/agents/*.md` → `docs/archive/` | Modify: `src/superclaude/cli/` (memory dir creation) | Test: `tests/unit/test_agent_structure.py`

- [ ] Keep the agents that survive Task 2 plus `self-review`; move the rest to `docs/archive/` so restoring is a file move
- [ ] Create the scope-appropriate agent memory directory at install time — `memory: local` resolves to `.claude/agent-memory-local/<agent>/` per `.claude/rules/agent-authoring.md:128` and nothing creates it today
- [ ] Verify: `uv run superclaude install --list` matches the kept roster; a fresh local install produces `.claude/agent-memory-local/`; `uv run pytest`
- [ ] Commit

---

## Phase 6 — Distribution (D1-a)

### Task 13: Package as a Claude Code plugin (A2)

**Files:** Create: `.claude-plugin/plugin.json`, marketplace manifest | Modify: `src/superclaude/hooks/hooks.json`

- [ ] Resolve the blocker first: `{{SCRIPTS_PATH}}` / `{{SKILLS_PATH}}` assume a copy-into-`.claude/` model and must resolve against the plugin root instead
- [ ] Map `commands/` → plugin commands, `agents/` → plugin agents, `skills/` → plugin skills, hooks → plugin hooks
- [ ] Apply whatever Task 1 found about how a plugin-scoped command reaches the model's skill list — packaging that reproduces the current activation failure buys nothing
- [ ] Keep the `superclaude install` CLI — it remains the only path for project-scoped, team-shared installs
- [ ] Verify: install into a scratch repo with no `.claude/superclaude/`, run `/sc:analyze`, confirm hooks fire and context injects
- [ ] Commit

### Task 14: Make user-scope install actually happen (A2)

**Files:** Modify: `src/superclaude/cli/main.py` / `install_paths.py` (if a defect is found)

- [ ] Test the leading hypothesis first: `main.py:148-157` prints a "Detected git repo at CWD … rerun with --scope local" hint whenever scope falls back to its `user` default inside a git repo. Every install this user ran was from inside a repo, so the CLI nudged toward local scope each time
- [ ] Decide whether the hint stays, is reworded, or fires only on a team-shared repo
- [ ] If the hint is not the cause, trace the install path for an outright failure
- [ ] Verify: a default `superclaude install` from inside a git repo leaves content in `~/.claude/`
- [ ] Commit

---

## Out of scope

- Caveman mode (D6). Verified separately in [`docs/analysis/caveman-mode-verification-chosh1179-2026-08-21.md`](../../analysis/caveman-mode-verification-chosh1179-2026-08-21.md); staying as-is.
- Rewriting `RULES`/`PRINCIPLES` to compete with karpathy-guidelines. The overlap is real (A1) but no log evidence shows the SuperClaude versions being rejected on quality.
- Changes to `/sc:` command bodies. Nothing in the audit implicates them; only descriptions change.
- Backfilling `.claude/insights.jsonl` or agent memory. Task 11 fixes the flow, not the history.
- A9 (inventory drift). The stale counts live in the session-memory index, not in shipped content, so there is no repository change to make; the index was corrected directly instead.

## Global verification

Every phase ends green against the baseline. It is echoed in `CLAUDE.md`, `AGENTS.md` and
`README.md` — update all three together if it moves.

```
uv run pytest      # expect 2102 passed, 28 skipped, 4 deselected
make lint
```

## Handoff

Phase 1 is investigation — run it first and read the result. Phases 2–4 are ready for
`/sc:implement --plan` and do not wait on it. Phases 5–6 consume Phase 1.
