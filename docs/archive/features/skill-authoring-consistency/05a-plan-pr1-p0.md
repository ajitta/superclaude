---
status: draft
revised: 2026-04-25
spec: ./01-discovery.md
---

# PR1: Remove `when-to-use`, Fold Triggers into `description`

**Goal:** Eliminate the silently-dropped `when-to-use` field from 5 shipped skills + skill-authoring.md, fold trigger keywords into `description` with third-person voice, and probe-verify that auto-invocation actually works after the change.

**Architecture:** Markdown-only edits across 6 files (5 SKILL.md + 1 authoring rule) + 1 memory-file edit + 1 canary verification. No code or test-fixture changes (verified absent). Single coordinated commit per D3 to avoid half-broken intermediate state.

**Tech Stack:** Markdown, YAML frontmatter, Claude Code v2.1.119+ runtime.

**References:** Spec P0-1, D1, D3, D11, I9. Self-review C1, C2.

---

### Task 1: Defensive sweep for `when-to-use` references

**Files:** Read-only sweep across `tests/`, `src/`, `.claude/`, `docs/`

- [ ] Run `grep -rn "when-to-use\|when_to_use" tests/ src/ .claude/ docs/` from repo root.
- [ ] Confirm only the 6 expected files contain matches: 5 shipped SKILL.md + `.claude/rules/skill-authoring.md`. Plus the spec/plan docs themselves (acceptable — they describe the change).
- [ ] If any unexpected match appears, halt and report; do not proceed.

**Verify:** `grep -rln "when-to-use" src/ tests/ | wc -l` returns 5 (the 5 SKILL.md only).

---

### Task 2: Compose new `description` strings (no edits yet)

**Files:** Read-only — review current frontmatter before composing.

For each shipped skill, compose a new `description` that folds the current `when-to-use` content using third-person voice ("This skill should be used when..."). Total length ≤1024 chars per skill (validator-friendly cap).

Pre-composed candidates (review before applying):

- **confidence-check** → `Pre-start validation checklist for any work (plan, design, spec, implementation). This skill should be used when the user says 'confidence check', 'validate first', 'before starting', 'before implementing', or wants validation before any plan/design/spec/implementation work.`
- **finishing-a-development-branch** → `Complete development work with structured options for merge, PR, or cleanup. This skill should be used when the user is done with a feature branch and wants to merge it, create a PR, or clean up branches.`
- **ship** → `Ship changes with git add, conventional commit, push, and optional PR creation. This skill should be used when the user says 'ship', 'commit and push', 'create PR', or wants to deploy changes to remote.`
- **simplicity-coach** → `Explicit OSL coaching, daybook journaling, and dependency audits (invoke with /simplicity-coach). This skill should be used for daybook journaling, dependency-gate audits, 3-level feedback reviews, or structured OSL coaching sessions. For passive simplicity mindset during coding, the simplicity-guide agent activates automatically — do not invoke this skill for that.`
- **verbalized-sampling** → `Research-backed verbalized sampling for diverse response generation with three variants. This skill should be used when the user explicitly requests 'multiple perspectives', 'diverse responses', 'explore options', 'brainstorm alternatives', or says 'VS', 'VS-CoT', 'verbalized sampling', or '--vs'. Do NOT trigger for routine coding questions, simple factual queries, or single-answer requests.`

- [ ] Sanity-check each composed `description`: length ≤1024 chars, trigger phrases in first ~200 chars, third-person voice (no "I"), no XML.

---

### Task 3: Edit `confidence-check/SKILL.md`

**Files:** Modify: `src/superclaude/skills/confidence-check/SKILL.md` (frontmatter only)

- [ ] Replace `description:` line with the new pre-composed string from Task 2.
- [ ] Delete the `when-to-use:` block (3 lines: key + multi-line value).
- [ ] Verify YAML still parses: `python -c "import yaml; yaml.safe_load(open('src/superclaude/skills/confidence-check/SKILL.md').read().split('---')[1])"`.

---

### Task 4: Edit `finishing-a-development-branch/SKILL.md`

**Files:** Modify: `src/superclaude/skills/finishing-a-development-branch/SKILL.md` (frontmatter only)

- [ ] Replace `description:` line with the new pre-composed string.
- [ ] Delete the `when-to-use:` block.
- [ ] Preserve `disable-model-invocation`, `allowed-tools`, `hooks` fields exactly as-is.
- [ ] YAML parse check.

---

### Task 5: Edit `ship/SKILL.md`

**Files:** Modify: `src/superclaude/skills/ship/SKILL.md` (frontmatter only)

- [ ] Replace `description:` line with the new pre-composed string.
- [ ] Delete the `when-to-use:` block.
- [ ] Preserve `disable-model-invocation`, `hooks`.
- [ ] YAML parse check.

---

### Task 6: Edit `simplicity-coach/SKILL.md`

**Files:** Modify: `src/superclaude/skills/simplicity-coach/SKILL.md` (frontmatter only)

- [ ] Replace `description:` line with the new pre-composed string.
- [ ] Delete the `when-to-use:` block.
- [ ] Preserve `disable-model-invocation`.
- [ ] Note: this skill's `when-to-use` had a "do not invoke for X" exclusion clause — confirm it survived the fold (it should be in the new description).
- [ ] YAML parse check.

---

### Task 7: Edit `verbalized-sampling/SKILL.md`

**Files:** Modify: `src/superclaude/skills/verbalized-sampling/SKILL.md` (frontmatter only)

- [ ] Replace `description:` line with the new pre-composed string.
- [ ] Delete the `when-to-use:` block.
- [ ] YAML parse check.

---

### Task 8: Update `.claude/rules/skill-authoring.md`

**Files:** Modify: `.claude/rules/skill-authoring.md` (multiple sections)

- [ ] Remove `when-to-use:` from Field Reference YAML example (current L67 in field reference; current L74 in archetype example).
- [ ] Remove `when-to-use` from "Field Rules" #1 (currently described as "description vs when-to-use 분리" at L102) — replace with new "Description authoring pattern" guidance (single `description` field, third-person voice, trigger phrases first ~200 chars).
- [ ] Remove `when-to-use` from "Validation Checklist" item #2 (currently "description + when-to-use 분리, 합쳐서 ≤1,536 chars" at L182) — replace with single-`description` cap guidance.
- [ ] Add a "Naming taxonomy" subsection per spec P0-1 final paragraph: list kebab-case fields, single-word fields, and the deprecated `when_to_use` form (do-not-use).
- [ ] All inline YAML comments in the field reference: leave Korean for now (D4 covered in PR4).

**Verify:** `grep -n "when-to-use\|when_to_use" .claude/rules/skill-authoring.md` returns only the deprecation-warning line in the new "Naming taxonomy" subsection (1 hit).

---

### Task 9: Retire stale memory entry

**Files:** Modify: `C:/Users/ajitta/.claude/projects/C--Users-ajitta-Repos-ajitta-superclaude/memory/reference_cc-native-fields.md`

- [ ] Delete the row `| \`when-to-use\` | Trigger keywords, separate from description |` from the "Skill Frontmatter Fields" table (currently L37).
- [ ] Add a note immediately above that table: `> Updated 2026-04-25: \`when-to-use\` removed (silently dropped by parser); \`when_to_use\` exists but is deprecated by Anthropic. Use \`description\` only with third-person trigger phrases.`
- [ ] Update the file's frontmatter `description` if it claims comprehensiveness for skill fields (the file may need a date bump).

**Verify:** `grep "when-to-use" reference_cc-native-fields.md` returns only the deprecation note (1 hit).

---

### Task 10: Probe-verify with canary skill (D3 acceptance gate)

**Files:** Modify temporarily: `src/superclaude/skills/confidence-check/SKILL.md` (insert canary trigger)

- [ ] In `confidence-check`'s NEW `description`, append a unique nonsense trigger word: `... or says 'xyzzy-canary-probe'.` (placed at end so it doesn't affect normal usage).
- [ ] Run `make deploy` (project's `uv tool install --editable .`).
- [ ] Open a fresh Claude Code session in a scratch directory (NOT the superclaude repo, to avoid `.claude/rules/skill-authoring.md` triggering).
- [ ] Type the prompt: `xyzzy-canary-probe what should I do?`
- [ ] **Observe:** Does Claude auto-invoke `/confidence-check`? (Look for skill activation in response.)
- [ ] If YES → fix verified; remove the canary trigger word from `description`; re-run `make deploy`.
- [ ] If NO → STOP. Investigate. Possibilities: (a) description-folding pattern still wrong, (b) install pipeline didn't pick up the change, (c) parser behavior differs from leaked-source analysis. Document the failure mode and revise plan before proceeding.

**Verify:** Document the canary result (PASS / FAIL with details) in the eventual PR description.

---

### Task 11: Final verification + commit

**Files:** All edited above.

- [ ] `grep -rln "when-to-use" src/superclaude/skills/` returns nothing.
- [ ] `grep -n "when-to-use\|when_to_use" .claude/rules/skill-authoring.md` returns ≤1 hit (deprecation note only).
- [ ] `uv run pytest tests/unit/test_skill_structure.py -v` — must pass with no regressions.
- [ ] `uv run pytest` (full suite) — baseline 1,628 passing; must remain 1,628+ passing.
- [ ] `make verify` passes.
- [ ] Stage all 7 files (5 SKILL.md + skill-authoring.md + memory file).
- [ ] Commit with message:
  ```
  fix(skills): remove dead when-to-use field; fold triggers into description

  Anthropic's canonical skill-reviewer marks when_to_use deprecated and the
  leaked CC parser silently drops the hyphenated when-to-use form. All 5
  shipped skills' trigger keywords were invisible to auto-invocation.

  - Remove when-to-use from 5 SKILL.md files
  - Fold triggers into description with third-person voice
  - Update skill-authoring.md field reference + validation checklist
  - Retire stale memory entry in reference_cc-native-fields.md
  - Canary probe verified: confidence-check auto-invokes on trigger phrase

  Spec: ./01-discovery.md
  ```
- [ ] No fixture changes (verified absent in Task 1) — note this in commit body or PR description per D11.

**Verify:** `git diff --stat HEAD~1` shows exactly 7 files changed.

---

## Out of scope (covered in later PRs)

- P1 drift fixes (budget figure, allowed-tools format, missing fields, XML callout, optional/required tags, reserved-words) → PR2 plan.
- P2 internal coherence + 4-file `<bounds>` unification → PR3 plan.
- P3 cosmetic + conditional runtime-bug gotchas → PR4 plan.

## Rollback

If the canary probe fails (Task 10) AND root cause cannot be identified within 30 minutes: `git checkout -- src/superclaude/skills/ .claude/rules/skill-authoring.md` and revert memory file. The system returns to "broken but-stable" state (description-only triggers, which is what the leaked parser actually used anyway). File a follow-up issue with the canary failure details.
