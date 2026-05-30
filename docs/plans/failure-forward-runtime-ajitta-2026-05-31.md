---
status: complete
revised: 2026-05-31
---

# Failure-Forward Runtime Contract (R21) — Implementation Plan

> **Done 2026-05-31.** R21 shipped to `src/superclaude/core/RULES.md`, installed user-scope, structural tests green (1402/3-skip), clean-env A/B confirms the marker fires on unexpected failures + does not over-fire. Method bug found and fixed mid-run (in-repo probe = observer effect; corrected to home-dir probe). Findings recorded in `../research/agent-native-design-ajitta-2026-05-31.md` § P-R21. Marker format reliability is partial-by-design (passive context-judged rule, unlike user-invoked mode markers).

**Goal:** Give pillar 3 (failure-forward) a thin, explicit, runtime-observable behavioral contract + signature in installed core RULES, so that on an in-task failure Claude emits a compact recovery record and moves forward — never blind-retry, never fabricate-past-failure, never silent-stall.

**Architecture:** SuperClaude is a content framework — behavior is configured by markdown installed into `~/.claude/`. The always-loaded SSOT `src/superclaude/core/RULES.md` is copied verbatim to `~/.claude/superclaude/core/RULES.md` at install. Adding rule `[R21 Failure-Forward]` there changes runtime behavior of every session after reinstall. Observable via headless `claude -p` because the rule emits a greppable single-line marker (parity with `--introspect`'s `🤔🎯⚡📊💡`).

**Tech Stack:** Markdown (content), `superclaude` CLI (install), `claude -p` (behavioral probe), `uv run pytest` (structural regression).

**Origin:** `docs/research/agent-native-design-ajitta-2026-05-31.md` — pillar 3 is the doc-identified gap; this is the minimal runtime-observable strengthening (the lightweight, no-infra cousin of that doc's P3 "persisted trace").

---

## Necessity (R18 — honest)

Not "broken" without it. Justification is bounded and explicit:
- Pillar 3 is the only pillar **lacking a runtime signature** (1/2/4 emit R-citations, `select:N`, introspect markers; 3's recovery discipline is diffuse — verification ladder, `--loop` — with no emitted marker).
- Consolidates **3 scattered partial behaviors** into one forward-handling contract: R03 (pre-fix diagnosis), `gotchas/general.md` `hypothesis-before-fix`, `askuserquestion-rejection-fallback` (narrow). R21 = the *general* in-task-failure handler + emitted trace.
- User-requested exploration (chose "[2] strengthen pillar 3 + observe").
- Necessity class: **ENHANCEMENT**, kept minimal (a format convention, no infra/JSONL/eval platform) and reversible (single rule, single file).

**Scope guard:** must NOT over-fire. R21 triggers only on *unexpected, progress-blocking* in-task failure — not on expected/handled errors, anticipated empty results, or normal validation. 2-attempt recovery cap → structured stop.

**Blast radius:** core RULES = every session, every project. HIGH. → plan-then-implement gate (this doc) is mandatory; do not edit `core/RULES.md` without approval.

---

## Proposed rule text (drop-in, so implement is mechanical)

Insert in `<core_rules>` immediately after the `[R20 Success Criteria]` block, before the `<examples>` table:

```
[R21 Failure-Forward] 🟡: on in-task failure (tool error, test red, missing target, denied permission, empty result where output expected) — emit compact record before next step: `⚠ failed: <what + exact error/signal> | hypothesis: <top cause + evidence> | next: <bounded recovery OR structured stop>`. Then take ONE bounded recovery probe (different approach, not identical retry) OR surface a structured stop if recovery needs user input. Never: silently retry identical action, fabricate output past the failure, stall with no record. Cap: 2 recovery attempts on same failure → escalate to structured stop. Fires only on unexpected progress-blocking failure, not expected/handled errors. Distinct from R03 (pre-fix diagnosis), R15 (success verification), `askuserquestion-rejection-fallback` (AskUserQuestion-only).
```

Add one row to the `<core_rules>` `<examples>` table:

```
  | `pytest` errors: file not found | Retries identical command, or invents a result | `⚠ failed: pytest — file tests/x.py not found \| hypothesis: wrong path (typo or moved) \| next: glob tests/ for real name` then re-run with corrected path | Failure-Forward 🟡 |
```

(No FLAGS/mode/PRINCIPLES change — restraint. R21 is a rule, not a flag.)

---

## Tasks (single branch, ordered; behavioral-TDD)

### Task 1: Baseline (red) — confirm pillar-3 signature absent today
**Files:** none (probe only)
- [ ] Step 1: run failure-inducing probe on **current** install:
      `claude -p "run the command 'uv run pytest tests/unit/test_nonexistent.py' and report what happened"`
- [ ] Step 2: confirm output does **NOT** contain the `⚠ failed: … | hypothesis: … | next:` format (baseline = no signature). Capture output for the A/B record.

### Task 2: Add R21 to RULES.md (implement)
**Files:** Modify: `src/superclaude/core/RULES.md` (insert rule after `[R20 …]`; add 1 example row)
- [ ] Step 1: find which tests parse RULES.md rule tags — `grep -rl "RULES.md\|\[R[0-9]" tests/` — note any rule-numbering/structure assertions that must stay green (e.g. sequential R-numbers, tag format).
- [ ] Step 2: insert the R21 rule block + example row (text above), verbatim.
- [ ] Step 3: `make format` (no-op for md, but run for hygiene) — skip if not applicable to markdown.

### Task 3: Structural regression (green-1)
**Files:** Test: `tests/unit/`
- [ ] Step 1: `uv run pytest tests/unit/test_agent_structure.py tests/unit/test_skill_structure.py tests/unit/test_command_structure.py` (the 3 lint files) + any RULES-touching test found in Task 2 Step 1.
- [ ] Step 2: confirm green (baseline 1402 passed / 3 skipped on the 3 lint files). If a RULES structural test exists and fails on the new R21, fix the rule format (not the test) unless the test encodes a bug.
- [ ] Note: full `tests/unit` run risks exit-137 SIGKILL (resource cap) — scope to affected files (documented gotcha).

### Task 4: Reinstall + behavioral re-probe (green-2 — the payoff)
**Files:** none (install + probe)
- [ ] Step 1: `superclaude install --force --scope user` (direct, dodges Windows `make sync` lib64 gotcha). Confirm "Core framework … 4 installed".
- [ ] Step 2: re-run the **same** probe from Task 1:
      `claude -p "run the command 'uv run pytest tests/unit/test_nonexistent.py' and report what happened"`
- [ ] Step 3: assert output now contains `⚠ failed:` + `hypothesis:` + `next:` — pillar-3 signature present. Same machine, same probe, rule-off → rule-on = clean A/B differential.
- [ ] Step 4: 1 over-fire check — `claude -p "what is 2+2"` → confirm R21 does **NOT** fire on a non-failure (guards against over-triggering).

### Task 5: Record + commit
**Files:** Modify: `docs/research/agent-native-design-ajitta-2026-05-31.md` (note R21 ships pillar-3's runtime signature, links this plan); this plan `status: draft → complete`
- [ ] Step 1: append A/B result (Task 1 vs Task 4 output) to the research doc pillar-3 section.
- [ ] Step 2: commit on a branch (`feat/r21-failure-forward` or current `test/agent-description-canary` if bundling) — message: `feat(core): add R21 Failure-Forward runtime contract`.
- [ ] Step 3: decide promote-to-feature (research + plan + impl = 3 related docs → `/sc:promote-feature` candidate). Flagged, not auto-done (R06).

---

## Success criteria (R20)

1. **Structural:** 3 lint files green (1402/3-skip baseline held); any RULES-structure test green.
2. **Runtime (green):** post-reinstall probe emits `⚠ failed: … | hypothesis: … | next: …`.
3. **No over-fire:** non-failure probe does NOT emit the marker.
4. **Clean A/B:** Task-1 output (no marker) vs Task-4 output (marker) on identical probe = the differential [1] couldn't produce.

## Risks

- **Over-firing** — rule fires on every minor/expected error → noise. Mitigation: trigger scoped to "unexpected progress-blocking"; Task 4 Step 4 over-fire check.
- **High blast radius** — core RULES affects all sessions. Mitigation: minimal single-rule change, reversible, approval gate.
- **Probe nondeterminism** — `claude -p` behavior varies. Mitigation: signature is a format string the rule explicitly mandates; re-run if a single probe is ambiguous.
- **R18 creep** — resist expanding R21 into a trace-infra/eval platform (that's doc P2/P3, separately gated). This task = behavioral contract only.

## Handoff

Ready for `/sc:implement --plan` against this file. Implement gate: approval required before Task 2 (edits installed core RULES).
