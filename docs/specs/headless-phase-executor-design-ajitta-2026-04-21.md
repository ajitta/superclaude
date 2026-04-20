---
status: draft
revised: 2026-04-21
---

# Headless Phase Executor — Design Spec

**Gap:** SuperClaude's `/sc:implement --plan` runs all phases in a single session. Long plans suffer context rot. The Meta-eng harness video's core lesson is phase-isolated execution via `claude -p`: each phase runs in a fresh subprocess so earlier context doesn't poison later phases. SuperClaude has no equivalent.

**Scope of this spec:** a Minimum Viable Slice (MVS) and the design decisions it depends on. Implementation plan comes **after** user sign-off on the decisions here.

---

## 1. Core Design Questions (require user sign-off)

### Q1 — Entry point: new command or flag on /sc:implement?

**Option A (flag):** `/sc:implement --headless --plan <path>`
- Pro: one surface to learn; natural "opt in to headless" posture
- Con: /sc:implement is already complex; adding subprocess orchestration on a flag obscures behavior

**Option B (new command):** `/sc:execute-phases --plan <path>`
- Pro: clean separation — a dedicated runner for phase-based plans
- Con: two commands to remember; /sc:implement still can't self-headless

**Recommendation:** Option B. Phase execution is a distinct operational mode, not an implementation variant. Keeps /sc:implement simple for single-session work.

### Q2 — Phase format: how does the planner express phase boundaries?

**Current:** /sc:plan emits markdown with `### Task N:` headings and checkboxes. No machine-parsable phase boundaries.

**Proposed:** planner emits a sibling file `<plan>.phases.json` with a strict schema:
```json
{
  "plan_path": "docs/plans/foo.md",
  "phases": [
    {"id": "01-setup", "heading": "Task 1: ...", "file": "phases/01-setup.md",
     "dependencies": [], "status": "pending", "max_turns": 15},
    {"id": "02-impl",  "heading": "Task 2: ...", "file": "phases/02-impl.md",
     "dependencies": ["01-setup"], "status": "pending", "max_turns": 20}
  ]
}
```
- Each phase file is a self-contained prompt (goal + files to touch + acceptance)
- Dependencies express sequential ordering; executor honors them
- Status: pending | running | passed | failed | skipped

### Q3 — Subprocess management: `claude -p` vs internal Agent tool?

**Option A (`claude -p` shell-out):** matches video exactly; requires CC binary on PATH and user's credentials
- Pro: real context isolation — separate process, zero shared state with main session
- Con: cross-platform shell quoting (Windows), credential handoff, debugging harder

**Option B (CC's Agent tool with `context: fork`):** already available in SuperClaude skills
- Pro: same-process, tool budget respected, stdin/stdout already structured
- Con: not *truly* isolated — shares parent's token budget and recent messages

**Recommendation:** Option B for MVS. Matches existing SuperClaude `context: fork` pattern; no new dependency on external binary. Option A can be added later as `--headless=subprocess` if users need hard isolation.

### Q4 — State management and resumability

- State file: `docs/plans/<plan>.phases.json` (same as Q2)
- Updated after each phase: status, start_ts, end_ts, last_commit_sha, error_summary
- **Crash recovery:** re-running the executor picks up from first non-`passed` phase
- **Circuit breaker integration:** loop_guard already tracks repeated errors; if a phase fails 3× consecutively with the same error signature, executor marks it `failed` and stops

### Q5 — Git discipline: who commits, and when?

**Options:**
- A: Each phase commits its own changes on success (matches video)
- B: No auto-commit; user reviews and commits manually at the end
- C: Batch commit at the end, with a summary message

**Recommendation:** B for MVS. Auto-commits are destructive in the wrong hands; we punt until there's demand. Document the user's responsibility in the command's `<gotchas>`.

### Q6 — Failure modes

- **Subprocess error (claude not on PATH):** fail fast, clear message
- **Phase declares success but tests regress:** up to phase's acceptance_criteria to verify; executor does not auto-run tests (that's the phase's job)
- **Infinite loop within a phase:** `max_turns` per phase (default 20) enforced via Agent tool

---

## 2. Minimum Viable Slice (MVS)

Deliverables to ship the thinnest usable version:

| Layer | Artifact | Responsibility |
|-------|----------|----------------|
| Planner | Extension to `/sc:plan` | Emit `<plan>.phases.json` alongside `.md` |
| Runner | New `/sc:execute-phases` command | Load plan + phases.json, orchestrate |
| Script | `src/superclaude/scripts/execute_phases.py` | Read phases.json, spawn Agent per phase via `context: fork`, update state |
| Docs | Update `/sc:implement` README | Point users toward `/sc:execute-phases` for multi-phase plans |
| Tests | `tests/unit/test_execute_phases.py` | Contract tests for state machine, resumability, circuit-breaker integration |

**Explicit non-goals for MVS:**
- No `claude -p` subprocess mode (deferred)
- No auto-commit between phases
- No parallel phase execution (sequential only)
- No UI/progress bar beyond console output

---

## 3. Integration with Shipped Infrastructure

- **loop_guard (just shipped):** each phase's Agent call is an Edit/Write/Bash surface; the hook will catch runaway error loops within a phase
- **/sc:init task [i] (just shipped):** `docs/` scaffold provides PRD/ARCH context the planner reads to emit phases.json with real content
- **existing `context: fork` skill pattern:** executor reuses the same fork mechanism; nothing new to learn

---

## 4. Risks and Open Questions

1. **Scope creep:** "Let's also add parallel phases, auto-commit, Gantt charts..." — resist; MVS or nothing.
2. **Agent tool budget:** spawning N agents for a 10-phase plan may blow token budget. Need per-phase budget estimate in planner.
3. **Cross-platform `claude -p`** (if Q3 flips to A later): Windows shell quoting is error-prone.
4. **State file corruption:** same fail-open policy as loop_guard; bad JSON → treat as fresh state, log warning.
5. **Is there user demand?** This is the biggest open question. Before implementing, gather 2-3 real cases where `/sc:implement --plan` context rot caused a concrete failure. Without that, MVS is premature abstraction.

---

## 5. Decision Required Before Implementation Plan

Before I write the TDD implementation plan, I need user decisions on:

- [ ] **Q1:** Option B (new `/sc:execute-phases` command) — confirm?
- [ ] **Q2:** `<plan>.phases.json` schema acceptable, or different shape?
- [ ] **Q3:** Option B (Agent tool + `context: fork`) for MVS — confirm?
- [ ] **Q4:** Sliding-window state + resume from first non-passed phase — confirm?
- [ ] **Q5:** No auto-commit (user commits manually) — confirm?
- [ ] **Risk #5:** Is there evidence of context-rot failures today? If not, suggest parking this until there is.

## Handoff

Once decisions are fixed, next command: `/sc:plan --from docs/specs/headless-phase-executor-design-ajitta-2026-04-21.md` → produces the TDD implementation plan for MVS.
