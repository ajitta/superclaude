---
status: draft
revised: 2026-04-25
spec: ./01-discovery.md
depends-on: ./05b-plan-pr2-p1.md
---

# PR3: P2 Internal Coherence + 4-File `<bounds>` Unification

**Goal:** Resolve internal coherence drift in skill-authoring.md AND unify the `<bounds>` rule across all 4 authoring files (skill / agent / command / mode), per user-chosen option (b) in D2.

**Architecture:** Multi-file edits across `.claude/rules/{skill,agent,command,mode}-authoring.md` plus a sweep of shipped components. No invalidating edits to shipped skills (the unified rule was chosen so existing 2-attr skills remain compliant).

**References:** Spec P2-1 through P2-7, D2 (revised), D5.

**Prerequisite:** PR2 merged.

---

### Task 1: Adopt unified `<bounds>` rule across 4 authoring files (D2)

**Unified rule:** `should + avoid` required; `fallback` optional with author guidance.

**Files:** Modify: `.claude/rules/{skill,agent,command,mode}-authoring.md`

- [ ] **skill-authoring.md** (~L176, L187): change `<bounds>` rule to "`should` + `avoid` required; `fallback` optional." Add 1-line note: "Skills are short-lived — the implicit fallback is 'skill ends, control returns to caller'. Use explicit `fallback=` only if the recovery posture is non-obvious."
- [ ] **agent-authoring.md** (~L134): change from "should + avoid + fallback required" to "`should` + `avoid` required; `fallback` recommended (agents are long-lived; explicit recovery posture is high-leverage)."
- [ ] **command-authoring.md** (~L70, L84): fix the internal contradiction. Update both the rule line AND the example to match the unified rule. Note in commit message that command's example previously had `fallback` while the rule said "2-attr required."
- [ ] **mode-authoring.md** (~L101): same as agent — `should` + `avoid` required; `fallback` recommended.

**Verify:** `grep -n "fallback" .claude/rules/*-authoring.md` shows consistent framing across all 4 files.

---

### Task 2: Sweep shipped components for `<bounds>` compliance

**Files:** Read-only audit + targeted fixes if any miss required attrs.

- [ ] `grep -rn "<bounds" src/superclaude/{skills,agents,commands,modes}/ --include="*.md"`.
- [ ] For each match, confirm `should=` and `avoid=` are present. List any missing-required-attrs in PR description.
- [ ] Fix only those that violate REQUIRED attrs (skip optional `fallback` additions). Existing `fallback=` attributes stay as-is — they're now optional, not redundant.

**Verify:** No `<bounds>` tag in shipped components is missing `should=` or `avoid=`.

---

### Task 3: `effort:` policy clarification (P2-2)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Reference + Field Rules)

- [ ] Add a 1-line policy note next to the `effort:` example, matching agent-authoring.md's stance: `# omit by default — inherit from parent. Set only when the skill genuinely needs deeper reasoning than the calling context provides.`
- [ ] Optionally drop the `effort: high` example value entirely if the policy makes the example confusing — replace with `# effort: high   # rarely set; see agent-authoring.md L47-58 for guidance`.

---

### Task 4: Archetype ② broadening (P2-3)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Pick an Archetype section)

- [ ] Update archetype ② row: change "Side-effect operations (deploy, release). Protect from auto-trigger" to "Workflow / explicit-invocation skill. Side-effect protection (deploy, release) OR delegation discipline (delegating to peer agent reliably)."
- [ ] Add a footnote example: `simplicity-coach` is the delegation-discipline case.

---

### Task 5: Opener uplift to peer-symmetry (P2-4)

**Files:** Modify: `.claude/rules/skill-authoring.md` (top L7-11)

- [ ] Add the unified 4-dimension table at the top, matching agent/command/mode-authoring openers:
  ```
  | Component | Role |
  |-----------|------|
  | Agent     | WHO TO BE |
  | Command   | WHAT TO DO |
  | Skill     | WHICH CAPABILITY |
  | Mode      | HOW TO THINK |
  ```
- [ ] Keep the existing "Decision gate" section after the table — it adds the skill-specific trigger conditions which the table alone doesn't convey.

---

### Task 6: `{{SKILLS_PATH}}` scope clarification (P2-5)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Template Variables / Directory Structure)

- [ ] Clarify the scope of the rule: "`{{SKILLS_PATH}}` is required in **`command:` strings** (where the runtime executes the script). `<references>` paths are project-relative and resolved by the reader, not the runtime — no template substitution required."
- [ ] If consistent with this rule, remove the `simplicity-coach:29` violation flag (it's no longer a violation under the clarified scope).

---

### Task 7: Field-reference annotation per D5

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Reference YAML)

- [ ] For each field in the YAML reference block, append a usage-count annotation comment:
  - `name:` → no annotation (5/5 use it; obvious).
  - `description:` → no annotation (5/5).
  - `disable-model-invocation:` → `# 3/5 shipped use this`.
  - `allowed-tools:` → `# 1/5 shipped use this`.
  - `hooks:` → `# 2/5 shipped use this`.
  - `model:`, `effort:`, `argument-hint:`, `context:`, `agent:`, `metadata:`, `user-invocable:` → all `# 0/5 shipped use this — rarely needed`.
  - `paths:` → `# 0/5 shipped use this — rarely needed (added for completeness)`.
- [ ] Pair with a 1-line preamble: "*Annotations reflect actual usage as of 2026-04-25. Aspirational fields are marked but kept for reference.*"

---

### Task 8: Final verification + commit

- [ ] `uv run pytest` — baseline 1,628+ passing.
- [ ] Visual diff of all 4 authoring files.
- [ ] Re-run conformance audit (use the same agent prompt from the original brainstorm session) and confirm all P2 items resolved.
- [ ] Commit:
  ```
  docs(authoring): unify <bounds> rule + resolve skill-authoring P2 drift

  - 4-file <bounds>: should+avoid required, fallback optional
  - Fix command-authoring.md internal contradiction (rule vs example)
  - effort: omit-by-default policy in skill-authoring
  - Broaden archetype ② (side-effects OR delegation discipline)
  - Add unified 4-dim opener table to skill-authoring
  - Clarify {{SKILLS_PATH}} scope (command: only, not <references>)
  - Annotate field reference with shipped-skill usage counts

  Spec: ./01-discovery.md
  ```
