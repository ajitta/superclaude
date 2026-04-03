---
status: implemented (simplicity-trimmed)
revised: 2026-04-03
---

# Retrospective-Driven Improvements — Implementation Plan

**Goal**: Apply 5 improvements (P1-P5) from spec-panel-reviewed retrospective analysis to RULES.md, FLAGS.md, and 3 command files.
**Architecture**: Pure documentation changes — markdown edits to core rules, flags, and command gotchas.
**Tech Stack**: Markdown, XML (SuperClaude component format)

**Spec**: `docs/specs/retrospective-driven-improvements-discovery-chosh1179-2026-04-03.md`

---

### Task 1: Expand [R13] + Rewrite [R18] + Add [R19] in RULES.md

**Files:** Modify: `src/superclaude/core/RULES.md:39,44`

- [ ] Step 1: Edit R13 (line 39) — append ambiguous verb list after existing text
  ```
  [R13] Intent Verification 🔴: before non-trivial work (>3 steps, ambiguous scope, or new task direction), restate user's intent in 1-2 sentences and confirm. Skip for: single-file edits, explicit file paths, continuation of confirmed plan. Ambiguous verbs requiring confirmation: adjust/재조정, improve, optimize, strengthen, refactor, clean up, modernize — may mean "review" not "change."
  ```

- [ ] Step 2: Rewrite R18 (line 44) — broaden scope to "unsolicited code change", promote to 🔴, add infra-first + execution order
  ```
  [R18] Necessity Test 🔴: before proposing any unsolicited code change, answer "Is the system broken without this?" — "safer/better" alone is insufficient. Require: specific failure scenario, quantitative evidence, or user-facing impact. Check infra/config/settings before code. "Deferred to post-MVP review" is a valid design decision. Unsolicited = model-initiated, not user-requested. Skip for: explicit change requests, confirmed plan items. Execution order: R13 → R18 → R19.
  ```

- [ ] Step 3: Add R19 after R18 (new line after 44) — evidence source citation
  ```
  [R19] Evidence-First 🔴: numbers and metrics must cite source type [code|config|measurement|doc|estimate]. Estimates prefixed with "~" or "약/approx". Skip for: well-known framework defaults, official documentation quotes.
  ```

- [ ] Step 4: Add 3 example rows to the examples table (lines 45-60) for R13 verb, R18 unsolicited, R19 citation
  ```
  | User: "API 성능 최적화해줘" | Starts profiling and rewriting | Asks: "Review current performance, or make specific changes?" | Intent Verification 🔴 |
  | Model proposes adding retry logic | "This would be more resilient" | "System works without this. No failure scenario. SKIP." | Necessity Test 🔴 |
  | "drain rate is 150 items/2s" | States as fact | "drain rate ~150 items/2s [estimate, not measured]" | Evidence-First 🔴 |
  ```

- [ ] Step 5: Verify R13, R18, R19 text is correct and examples table renders properly

---

### Task 2: Add Session-Type Flag Profiles to FLAGS.md

**Files:** Modify: `src/superclaude/core/FLAGS.md:53` (after `</execution>`)

- [ ] Step 1: Insert `<session_profiles>` section between `</execution>` (line 53) and `<output>` (line 55)
  ```xml
  <session_profiles note="Recommended flag sets — avoid loading execution flags in analysis sessions">
  | Session Type | Recommended | Avoid | Rationale |
  |-------------|-------------|-------|-----------|
  | Analysis/Discussion | --seq --tavily --c7 | --delegate --loop | Sequential dialogue, no parallel work |
  | Implementation | --delegate --serena --loop | — | Parallel execution, code-centric |
  | Debug/Troubleshoot | --seq --serena --c7 | --delegate --loop | Sequential diagnosis, symbolic exploration |
  | Research | --tavily --c7 --seq | --delegate --serena | Web-centric, no code changes |
  | Review/Audit | --serena --seq | --delegate --loop | Read-only, systematic |
  </session_profiles>
  ```

- [ ] Step 2: Verify table renders correctly and section is between `</execution>` and `<output>`

---

### Task 3: Add Gotchas to brainstorm.md, analyze.md, troubleshoot.md

**Files:** Modify: `src/superclaude/commands/brainstorm.md:65`, `analyze.md:74`, `troubleshoot.md:55`

Gotcha content (same for all 3 commands):
```xml
<gotchas note="From 2026-04-03 retrospective">
- evidence-fabrication: Do not construct hypothetical failure scenarios to justify a pre-existing recommendation. Evidence (code, config, measurements) must precede proposals.
- seq-loop: If sequential thinking reaches the same conclusion twice on the same question, terminate that analysis branch and move to next topic.
</gotchas>
```

- [ ] Step 1: Insert `<gotchas>` in brainstorm.md between `<token_note>` (line 65) and `<bounds>` (line 67)
- [ ] Step 2: Insert `<gotchas>` in analyze.md between `<token_note>` (line 74) and `<bounds>` (line 76)
- [ ] Step 3: Insert `<gotchas>` in troubleshoot.md between `<token_note>` (line 55) and `<bounds>` (line 57)

---

### Task 4: Verification

- [ ] Step 1: Run `uv run pytest tests/unit/test_command_structure.py -v` (verify command gotchas don't break tests)
- [ ] Step 2: Run `uv run pytest tests/unit/ -v -k "rule or flag or core"` (verify core file integrity)
- [ ] Step 3: Spot-check installed files match source after `make deploy`
- [ ] Step 4: Update spec status to `approved` if all tests pass

---

## Summary

| Task | Files | Lines Changed | Risk |
|------|-------|--------------|------|
| 1. RULES.md (P1+P2+P3) | 1 | ~12 modified + 4 added | Low |
| 2. FLAGS.md (P4) | 1 | ~9 added | Low |
| 3. Command gotchas (P3+P5) | 3 | ~12 added (4 each) | Low |
| 4. Verification | 0 | 0 | — |
| **Total** | **5 files** | **~37 lines** | **Low** |
