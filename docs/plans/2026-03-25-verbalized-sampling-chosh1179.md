# Verbalized Sampling Integration — Implementation Plan

**Goal:** Create a Reference Skill for verbalized sampling that auto-triggers on diversity keywords and integrates with /sc:brainstorm via --vs flag.
**Spec:** `docs/specs/2026-03-25-verbalized-sampling-integration-design-chosh1179.md`
**Architecture:** CC-native Reference Skill (auto-invocation via description) + FLAGS.md entry + brainstorm.md --vs flag. No hooks, no context_loader TRIGGER_MAP.
**Tech Stack:** Markdown content only (no Python code changes except test registration + alias)

## Pre-work (modified, unstaged)

These changes were made during the brainstorm session but are NOT yet committed:
- [x] `tests/unit/test_skill_structure.py` — added `REFERENCE_SKILL_NAMES` set (empty), dynamic count test, `test_all_reference_skills_present`
- [x] `.claude/rules/skill-authoring.md` — expanded decision gate for Reference Skills
- [x] `src/superclaude/skills/README.md` — added Reference Skills section to taxonomy

**Action before starting:** Commit pre-work changes first, or stage them so they're not lost.

## Source files

Original skill extracted at `/tmp/vs-skill-extract/verbalized-sampling-enhanced/`. If this path doesn't exist (new session), re-extract:
```bash
mkdir -p /tmp/vs-skill-extract && cd /tmp/vs-skill-extract && unzip /Users/chosh/Downloads/verbalized-sampling-enhanced/verbalized-sampling-enhanced.skill
```

---

## Task 1: Register skill + create SKILL.md

**Files:**
- Modify: `tests/unit/test_skill_structure.py` (registration FIRST — before creating the directory)
- Create: `src/superclaude/skills/verbalized-sampling/SKILL.md`

**Source:** Spec §"Files to Create > 1" + original at `/tmp/vs-skill-extract/verbalized-sampling-enhanced/SKILL.md`

- [ ] Add `"verbalized-sampling"` to `REFERENCE_SKILL_NAMES` set in `test_skill_structure.py:31`
- [ ] Create directory `src/superclaude/skills/verbalized-sampling/`
- [ ] Write SKILL.md with frontmatter (name, description — narrowed triggers per C2 fix)
- [ ] Write XML body: `<component name="verbalized-sampling" type="skill">` with sections: role, syntax, flow, variants, parameters, diversity_dial, prompt_templates, output_format, critical_rules, references, attribution, bounds, handoff
- [ ] Verify body < 500 lines
- [ ] Verify `name` matches directory name

**Verify:** `uv run pytest tests/unit/test_skill_structure.py -v` — expect 59 passed, 0 skipped (was 58+1 skip)

---

## Task 2: Create references/theory.md

**Files:** Create: `src/superclaude/skills/verbalized-sampling/references/theory.md`
**Source:** `/tmp/vs-skill-extract/verbalized-sampling-enhanced/references/theory.md`

- [ ] Create `references/` directory
- [ ] Adapt original theory.md: remove bilingual labels, keep English only
- [ ] Preserve: typicality bias section, distribution-level prompts mechanism, prompt format ablation results, combining VS with other techniques
- [ ] Keep ~100 lines

**Verify:** File exists and is well-formed markdown

---

## Task 3: Create references/examples.md

**Files:** Create: `src/superclaude/skills/verbalized-sampling/references/examples.md`
**Source:** `/tmp/vs-skill-extract/verbalized-sampling-enhanced/references/examples.md`

Can run in parallel with Task 2 (both only need directory from Task 1).

- [ ] Adapt Examples 1-5 from original: creative (VS-Standard), analytical (VS-CoT), decision (VS-CoT), brainstorming (VS-Multi), custom config. Translate Korean text to English equivalents
- [ ] Add Example 6: Architecture decision — VS-CoT, microservices vs monolith, k=5
- [ ] Add Example 7: Code review perspectives — VS-Standard, performance vs readability vs security, k=5
- [ ] Add Example 8: Debugging hypotheses — VS-CoT, 5 hypotheses for endpoint 500 error, aligns with RULES.md [R03]
- [ ] Preserve Common Mistakes section from original (5 mistakes)
- [ ] Keep ~300 lines

**Verify:** File exists, has 8 examples + common mistakes section

---

## Task 4: Update README + CLAUDE.md

**Files:** Modify: `src/superclaude/skills/README.md`, `CLAUDE.md`

- [ ] Add entry to README.md Reference Skills table: `| verbalized-sampling | Reference skill (auto-invocation) | Research-backed diverse response generation via distribution-level prompting |`
- [ ] Update README.md count: `## Current Skills (4)` → `## Current Skills (5)`
- [ ] Update CLAUDE.md line 52: `| skills/ | Runtime hooks + safety — CC-native only |` → `| skills/ | Runtime hooks, safety, and reference knowledge — CC-native |`
- [ ] Update CLAUDE.md line 61: `(4 hook/safety skills)` → `(5 skills: 2 hook, 2 safety, 1 reference)`

**Verify:** Grep for updated counts in both files

---

## Task 5: Add --vs to FLAGS.md

**Files:** Modify: `src/superclaude/core/FLAGS.md`

Can run in parallel with Tasks 1-4.

- [ ] Add to `<execution>` section (after `--fast` line): `--vs [standard|cot|multi]: "multiple perspectives", diverse responses → verbalized sampling (distribution-level diversity, probability-weighted candidates). Bracket sub-params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]`
- [ ] Add to `<aliases>` section: `--sampling → --vs | --verbalized → --vs`

**Verify:** `grep '\-\-vs' src/superclaude/core/FLAGS.md` — confirms entry exists in `<execution>` and `<aliases>`

---

## Task 6: Add --vs to brainstorm.md

**Files:** Modify: `src/superclaude/commands/brainstorm.md`

Can run in parallel with Tasks 1-4.

- [ ] Update `<syntax>` to include `[--vs [standard|cot|multi]]`
- [ ] Add conditional flow in step 2: `(default): Multi-persona | (--vs): VS distribution generation`
- [ ] Add to `<patterns>`: `Verbalized-Sampling: --vs → distribution-level diversity`
- [ ] Add 3 examples to `<examples>` table
- [ ] Do NOT change other sections (role, mission, bounds, handoff — they stay as-is)

**Verify:** `uv run pytest tests/unit/test_command_structure.py -k brainstorm -v`

---

## Task 7: Add flag + aliases to context_loader.py

**Files:** Modify: `src/superclaude/scripts/context_loader.py`

Can run in parallel with Tasks 1-4.

- [ ] Add `"vs"` to `VALID_FLAGS` set at line 237 (REQUIRED — `test_context_loader.py:158-160` enforces alias targets must be in VALID_FLAGS)
- [ ] Add to `FLAG_ALIASES` dict at line 219: `"sampling": ["vs"], "verbalized": ["vs"]`

**Verify:** `uv run pytest tests/unit/test_context_loader.py -v` — alias validation passes

---

## Task 8: Full regression + deploy

- [ ] `uv run pytest tests/unit/ -v` — baseline ~1,694, expect +1 (reference skill test unskipped)
- [ ] `make deploy` — install to global ~/.claude/skills/
- [ ] Verify `~/.claude/skills/verbalized-sampling/SKILL.md` exists after deploy
- [ ] Manual: `/sc:brainstorm "topic" --vs` produces VS-formatted output
- [ ] Manual: "show me multiple perspectives on X" auto-triggers skill
- [ ] Manual: "should I use a class here?" does NOT trigger skill (false positive check)

---

## Execution Order

```
                    ┌─── Task 5 (FLAGS.md) ──────────────┐
                    ├─── Task 6 (brainstorm.md) ─────────┤
                    ├─── Task 7 (context_loader.py) ─────┤
                    │                                     │
Task 1 (register + SKILL.md) ──┬── Task 2 (theory.md) ──┤
                               └── Task 3 (examples.md) ─┤
                                                          │
                               Task 4 (README + CLAUDE) ──┤
                                                          │
                                              Task 8 (regression + deploy)
```

**Parallel groups:**
- Group A (independent): Tasks 5, 6, 7
- Group B (sequential): Task 1 → [Task 2 | Task 3] → Task 4
- Final: Task 8 (after all)

Groups A and B can run concurrently.
