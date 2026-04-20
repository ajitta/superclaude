---
status: draft
revised: 2026-04-21
---

# Circuit-Breaker Hook + `/sc:init` Docs Scaffold — Implementation Plan

**Goal:** Close two harness-engineering gaps identified in 2026-04-21 analysis: (1) no loop-detection safety net for `--loop`/`--iterations` and (2) no `docs/` project-brain scaffolding in `/sc:init`.

**Architecture:** Two independent, small-surface changes. Gap 1 adds one new Python hook script + JSON state file + PreToolUse+PostToolUse registration in `hooks.json`. Gap 4 adds one new task `[i]` to `commands/init.md` with four minimal markdown templates. No cross-coupling — ship order is interchangeable.

**Tech Stack:** Python 3.10+, pytest, CC PreToolUse/PostToolUse JSON hook protocol, ruff.

**Baseline to preserve:** 1,628 passing / 1,807 collected (per CLAUDE.md).

---

## Scope Decisions (Evidence-Based)

Before implementing, three design calls are fixed here:

1. **State file location for Gap 1:** project-local `$CLAUDE_PROJECT_DIR/.claude/loop_guard_state.json`, not home-global. Rationale: matches precedent of project-scope hook hardening (memory ID 1972, `$CLAUDE_PROJECT_DIR` + `sys.executable`). Prevents one project's loop from blocking another.
2. **Reset signal:** sliding window (15 min) + manual reset on every `UserPromptSubmit`. Hook script adds a reset-on-user-prompt behavior via `context_loader.py` side call, OR simpler: state file includes last-write timestamp and entries older than 15 min are discarded on read. Choose the simpler path.
3. **Block threshold:** warn at 3, block at 5. Matches video ("동일 에러 5회 반복 시 루프 탈출"). Env opt-out: `SUPERCLAUDE_LOOP_GUARD=0`.

---

## File Map

### Gap 1 — Circuit Breaker
| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `src/superclaude/scripts/loop_guard.py` | PreToolUse+PostToolUse hook; tracks consecutive error signatures; blocks after 5 |
| Create | `tests/unit/test_loop_guard.py` | Unit tests mirroring `test_file_size_guard.py` pattern |
| Modify | `src/superclaude/hooks/hooks.json` | Register loop_guard on PreToolUse(Edit\|Write\|Bash) and PostToolUse(Edit\|Write\|Bash) |
| Modify | `src/superclaude/scripts/README.md` | Document loop_guard.py purpose + env var |

### Gap 4 — `/sc:init` Docs Scaffold
| Action | Path | Responsibility |
|--------|------|---------------|
| Modify | `src/superclaude/commands/init.md` | Add task `[i] docs/ project-brain scaffolding` + dependency graph + task_outputs row + safety_rule |
| Create | `src/superclaude/commands/templates/docs-scaffold/PRD.md` | Minimal PRD template (goal, users, features, MVP exclusions) |
| Create | `src/superclaude/commands/templates/docs-scaffold/ARCHITECTURE.md` | Directory structure, patterns, data flow placeholders |
| Create | `src/superclaude/commands/templates/docs-scaffold/ADR-0001-template.md` | Single ADR template (context, decision, consequences) |
| Create | `src/superclaude/commands/templates/docs-scaffold/UI-GUIDE.md` | Design tokens, component conventions placeholders |
| Modify | `src/superclaude/cli/install_components.py` | Ship `commands/templates/` directory on install (if not already generic) |
| Create | `tests/unit/test_init_docs_scaffold.py` | Verify templates exist in install tree + idempotency contract doc |

---

## Task Decomposition

### Task 1: Gap 1 — loop_guard.py skeleton + failing tests

**Files:**
- Create: `tests/unit/test_loop_guard.py`
- Create: `src/superclaude/scripts/loop_guard.py` (stub returning approve)

- [ ] Step 1: Write `test_loop_guard.py` with classes `TestApprove`, `TestBlockAfterRepeats`, `TestStateIsolation`, `TestEnvOptOut`. Copy `run_guard()` helper pattern from `test_file_size_guard.py:13`. Use `tmp_path` for state file via `CLAUDE_PROJECT_DIR` env override.
- [ ] Step 2: Add test: `test_approves_first_error` — single failed Bash tool_response → approve.
- [ ] Step 3: Add test: `test_blocks_after_5_consecutive_errors` — feed 5 identical normalized error signatures → 5th call returns `{"decision": "block", ...}` with reason mentioning "circuit breaker".
- [ ] Step 4: Add test: `test_different_signatures_do_not_accumulate` — 4 errors of sig-A, 1 error of sig-B → both approved, no block.
- [ ] Step 5: Add test: `test_env_opt_out` — `SUPERCLAUDE_LOOP_GUARD=0` → always approve regardless of state.
- [ ] Step 6: Add test: `test_successful_tool_resets_counter` — 4 errors, 1 success, 4 more errors → all approved.
- [ ] Step 7: Add test: `test_sliding_window_expiry` — simulate state file with 20-min-old entries → fresh count starts.
- [ ] Step 8: Write `loop_guard.py` returning `{"decision": "approve"}` on all input (stub). Verify `uv run pytest tests/unit/test_loop_guard.py -v` shows expected failures (approve-tests pass, block-tests fail).
- [ ] Step 9: Commit: `test: add loop_guard contract tests (gap 1 — circuit breaker)`

**Verify:**
```bash
uv run pytest tests/unit/test_loop_guard.py -v  # Expect: 2 pass, 5 fail
```

---

### Task 2: Gap 1 — loop_guard.py implementation

**Files:** Modify: `src/superclaude/scripts/loop_guard.py`

- [ ] Step 1: Implement state file read at `$CLAUDE_PROJECT_DIR/.claude/loop_guard_state.json` with `{"signatures": [{"sig": str, "ts": float, "count": int}], ...}`. Fall back to `Path.cwd()/.claude/` if env missing. Use `sys.executable` pattern (memory ID 1972).
- [ ] Step 2: Implement PostToolUse branch: read `tool_response`, extract error (stderr/non-zero exit/Edit error message), normalize via regex (strip line numbers, paths, timestamps, hashes), hash → signature. Append to state. Drop entries older than 15 min.
- [ ] Step 3: Implement PreToolUse branch: read `tool_input`, compute prospective signature heuristic (same tool_name + same first 80 chars of command/file_path), check recent signatures. If matching signature appears ≥5 times in window → `{"decision": "block", "reason": "Circuit breaker: same error repeated 5 times in 15 min. Change approach (different tool, different file, or ask user)."}`.
- [ ] Step 4: Hook dispatch: read `hook_event_name` from stdin JSON. Branch Pre vs Post. Unknown event → approve (fail open).
- [ ] Step 5: Env opt-out check at top: `SUPERCLAUDE_LOOP_GUARD=0` → approve immediately.
- [ ] Step 6: Wrap all logic in try/except: on any error → approve (fail open), same pattern as `file_size_guard.py:118`.
- [ ] Step 7: Verify `uv run pytest tests/unit/test_loop_guard.py -v` all 7 pass.
- [ ] Step 8: Run `make lint` — fix ruff warnings.
- [ ] Step 9: Commit: `feat(hooks): add loop_guard circuit breaker (blocks after 5 identical errors in 15min)`

**Verify:**
```bash
uv run pytest tests/unit/test_loop_guard.py -v  # All 7 pass
uv run pytest                                    # Baseline: ≥1,628 pass
make lint
```

---

### Task 3: Gap 1 — Register hook in hooks.json + docs

**Files:**
- Modify: `src/superclaude/hooks/hooks.json`
- Modify: `src/superclaude/scripts/README.md`

- [ ] Step 1: Write test `test_hooks.py::test_loop_guard_registered` — assert `hooks.json` contains `loop_guard.py` under both PreToolUse and PostToolUse with matcher `Edit|Write|Bash`. (Check existing `test_hooks.py` for parsing helpers.)
- [ ] Step 2: Verify test fails (hook not registered yet).
- [ ] Step 3: Edit `hooks.json`: under `PreToolUse`, add a new block with matcher `Edit|Write|Bash`, command `{{PYTHON_BIN}} {{SCRIPTS_PATH}}/loop_guard.py`, timeout 5, `_comment: "[superclaude] safety — circuit breaker (SUPERCLAUDE_LOOP_GUARD=0 to disable)"`. Add symmetric entry under `PostToolUse`.
- [ ] Step 4: Edit `scripts/README.md` — add loop_guard.py row to hook table with purpose + env var.
- [ ] Step 5: Verify `uv run pytest tests/unit/test_hooks.py -v` all pass.
- [ ] Step 6: Run `make deploy` + manual smoke: trigger a deliberate error 5 times in a test subshell, confirm 6th call blocked.
- [ ] Step 7: Commit: `feat(hooks): register loop_guard on Pre/PostToolUse (Edit|Write|Bash)`

**Verify:**
```bash
uv run pytest tests/unit/test_hooks.py tests/unit/test_loop_guard.py -v
make deploy
# Manual: trigger same Bash error 5x, confirm block message appears
```

---

### Task 4: Gap 4 — docs scaffold templates

**Files (all new, minimal):**
- Create: `src/superclaude/commands/templates/docs-scaffold/PRD.md`
- Create: `src/superclaude/commands/templates/docs-scaffold/ARCHITECTURE.md`
- Create: `src/superclaude/commands/templates/docs-scaffold/ADR-0001-template.md`
- Create: `src/superclaude/commands/templates/docs-scaffold/UI-GUIDE.md`

- [ ] Step 1: Write `PRD.md` template — sections: Goal, Target Users, Core Features, MVP Exclusions, Success Metrics. Placeholder `<fill in>` markers. ~30 lines.
- [ ] Step 2: Write `ARCHITECTURE.md` template — sections: Directory Layout, Design Patterns, Data Flow, External Dependencies. ~25 lines.
- [ ] Step 3: Write `ADR-0001-template.md` — sections: Context, Decision, Consequences, Alternatives Considered, Date. ~15 lines.
- [ ] Step 4: Write `UI-GUIDE.md` — sections: Design Tokens, Component Conventions, Accessibility Baseline, Forbidden Patterns. ~20 lines. Mark "optional, remove if headless backend".
- [ ] Step 5: Verify templates render as GitHub-flavored markdown (local preview).
- [ ] Step 6: Commit: `feat(init): add docs-scaffold templates (PRD, ARCHITECTURE, ADR, UI-GUIDE)`

**Verify:**
```bash
ls src/superclaude/commands/templates/docs-scaffold/  # 4 .md files
```

---

### Task 5: Gap 4 — Install templates on deploy

**Files:** Modify: `src/superclaude/cli/install_components.py`

- [ ] Step 1: Check existing installer — does it already copy arbitrary directories under `commands/`, or is it file-by-file? (Read `install_components.py::_install_commands` or similar.)
- [ ] Step 2: Write `tests/unit/test_init_docs_scaffold.py::test_templates_shipped_on_install` — simulate install, assert `~/.claude/commands/templates/docs-scaffold/PRD.md` exists post-install.
- [ ] Step 3: Modify installer to include `templates/` subdirectory in the commands install tree. Minimum change: add pattern or explicit directory copy.
- [ ] Step 4: Verify test passes and no baseline test regresses.
- [ ] Step 5: Commit: `feat(install): ship command templates directory to ~/.claude/commands/templates/`

**Verify:**
```bash
uv run pytest tests/unit/test_cli_install.py tests/unit/test_init_docs_scaffold.py -v
make deploy
ls ~/.claude/commands/templates/docs-scaffold/  # 4 files
```

---

### Task 6: Gap 4 — Wire task [i] into /sc:init

**Files:** Modify: `src/superclaude/commands/init.md`

- [ ] Step 1: Add test `tests/unit/test_init_docs_scaffold.py::test_init_md_declares_task_i` — parse `init.md`, assert task `[i]` present in menu, appears in `dependency_graph`, `task_outputs`, and `safety_rules`. Assert `--full` preset updated to include `i`.
- [ ] Step 2: Verify test fails.
- [ ] Step 3: Edit `init.md` menu block (line ~36): add line `    [i] docs/ project brain scaffold   — PRD + ARCHITECTURE + ADR + UI-GUIDE   (no deps)`.
- [ ] Step 4: Update `dependency_graph` batch 1 to include `i`.
- [ ] Step 5: Add `task_outputs` row: `| i | docs/{PRD,ARCHITECTURE,UI-GUIDE}.md + docs/ADR/0001-*.md | project root |`.
- [ ] Step 6: Add `safety_rules` bullet: `- Docs scaffold (i): create docs/ dir + 4 files from templates/docs-scaffold/ only if missing. Idempotent — skip per-file if exists. Never overwrite.`
- [ ] Step 7: Update `--full` preset line to `a,b,c,d,e,f,g,h,i`.
- [ ] Step 8: Update `examples` table — add one row demonstrating `/sc:init i`.
- [ ] Step 9: Run `uv run pytest tests/unit/test_command_structure.py tests/unit/test_init_docs_scaffold.py -v`.
- [ ] Step 10: Commit: `feat(init): add task [i] docs/ project-brain scaffold`

**Verify:**
```bash
uv run pytest tests/unit/test_command_structure.py tests/unit/test_init_docs_scaffold.py -v
make deploy
# Manual in a scratch dir: /sc:init i → verify 4 files created, re-run is no-op
```

---

### Task 7: Integration + regression gate

**Files:** (no code change) — final verification sweep.

- [ ] Step 1: Run full suite fresh: `uv run pytest -x`.
- [ ] Step 2: Confirm pass count ≥1,628 (baseline). Record actual: `<fill>`.
- [ ] Step 3: Run `make verify` + `make doctor` — clean.
- [ ] Step 4: Manual smoke: fresh scratch repo, run `/sc:init --full`, confirm docs/ scaffold + no loop_guard false positives during subsequent edits.
- [ ] Step 5: Update `src/superclaude/hooks/README.md` if it lists hooks (add loop_guard row).
- [ ] Step 6: Commit: `chore: verify circuit-breaker + docs-scaffold integration (gap 1+4 complete)`

**Verify:**
```bash
uv run pytest  # Baseline ≥1,628
make verify
make doctor
```

---

## Out of Scope (Gaps Deferred)

Per analysis, these are explicitly NOT in this plan:
- **Gap 2 (TDD Guard hook)** — opinionated; defer until user demand
- **Gap 3 (headless phase executor)** — large design surface; needs separate spec
- **Gap 5 (worktree pattern docs)** — pure docs change; handle in separate PR after these two ship

## Risks

- **loop_guard false positives on legitimate retries** (e.g., flaky network retries): mitigated by env opt-out + 15-min window + distinct-signature reset. If reports come in, raise threshold to 7 before blocking.
- **Template install path mismatch**: `install_components.py` may not generically handle nested subdirectories under `commands/`. Task 5 Step 1 verifies first; if not generic, add explicit handling.
- **Hook stdin protocol variance**: `tool_response` shape for Edit/Write differs from Bash. Normalize defensively in loop_guard.py (try/except per branch).

## Handoff

After Task 7 passes: run `/sc:implement --plan docs/plans/circuit-breaker-docs-scaffold-ajitta-2026-04-21.md` to execute, or cherry-pick Gap 1 vs Gap 4 independently (they are decoupled).
