---
status: implemented
revised: 2026-04-08
---

# Bounds Attribute Rename Implementation Plan

**Goal:** Rename `will` → `should` and `wont` → `avoid` in all `<bounds>` XML tags across the framework.
**Architecture:** Mechanical find-and-replace across 82 files (77 content + 4 authoring rules + 1 test update). No logic changes.
**Spec:** `docs/specs/bounds-attribute-rename-design-ajitta-2026-04-08.md`

## Task 1: Replace attributes in content files (77 files)

All replacements target XML attributes only: ` will=` and ` wont=` (with leading space to avoid matching English words in content).

**Files:** Modify: `src/superclaude/agents/*.md` (23), `src/superclaude/commands/*.md` (33), `src/superclaude/modes/MODE_*.md` (7), `src/superclaude/skills/*/SKILL.md` (5), `src/superclaude/mcp/MCP_*.md` (8), `src/superclaude/ARCHITECTURE.md` (1)

- [ ] 1a. Run sed replacement across all content directories:
  ```bash
  find src/superclaude/ -name "*.md" ! -name "README.md" -exec sed -i 's/ will="/ should="/g; s/ wont="/ avoid="/g' {} +
  ```
- [ ] 1b. Verify zero remaining old attributes:
  ```bash
  grep -rn 'bounds.*will=' src/superclaude/ --include="*.md" | wc -l   # expect: 0
  grep -rn 'bounds.*wont=' src/superclaude/ --include="*.md" | wc -l   # expect: 0
  ```
- [ ] 1c. Verify correct new counts:
  ```bash
  grep -rn 'bounds.*should=' src/superclaude/ --include="*.md" | wc -l  # expect: 77
  grep -rn 'bounds.*avoid=' src/superclaude/ --include="*.md" | wc -l   # expect: 76
  ```
- [ ] 1d. Spot-check multi-line edge case: `src/superclaude/skills/verbalized-sampling/SKILL.md:70-71`

## Task 2: Update authoring rules (4 files)

**Files:** Modify: `.claude/rules/agent-authoring.md`, `.claude/rules/command-authoring.md`, `.claude/rules/mode-authoring.md`, `.claude/rules/skill-authoring.md`

- [ ] 2a. `agent-authoring.md`: Replace template (`will="core capabilities" wont="out-of-scope actions"` → `should="core capabilities" avoid="out-of-scope actions"`), update requirement text ("must include `will`, `wont`" → "must include `should`, `avoid`")
- [ ] 2b. `command-authoring.md`: Same template + requirement text + anti-pattern table row ("Add will/wont" → "Add should/avoid")
- [ ] 2c. `mode-authoring.md`: Same template + validation list + checklist item ("will/wont/fallback" → "should/avoid/fallback")
- [ ] 2d. `skill-authoring.md`: Same template + requirement text + validation checklist

## Task 3: Update mode test (1 file)

**Files:** Modify: `tests/unit/test_mode_structure.py:96-99`

- [ ] 3a. Rename `will_attr` → `should_attr`, `wont_attr` → `avoid_attr`
- [ ] 3b. Update assert messages: `'will'` → `'should'`, `'wont'` → `'avoid'`
  ```python
  # Lines 96-99: change to
  should_attr = extract_xml_attr(content, "bounds", "should")
  avoid_attr = extract_xml_attr(content, "bounds", "avoid")
  assert should_attr, f"{stem}: <bounds> missing 'should' attribute"
  assert avoid_attr, f"{stem}: <bounds> missing 'avoid' attribute"
  ```

## Task 4: Add attribute checks to agent + command tests (2 files)

**Files:** Modify: `tests/unit/test_agent_structure.py:173-175`, `tests/unit/test_command_structure.py:142-144`

Both files already have `extract_xml_attr` helper. Extend `test_has_bounds` to check attributes.

- [ ] 4a. `test_agent_structure.py:173-175`: Add `should`/`avoid` attribute assertions after existing bounds tag check:
  ```python
  def test_has_bounds(self, agent):
      stem, content, _ = agent
      assert "<bounds " in content, f"{stem}: missing <bounds> tag"
      should_attr = extract_xml_attr(content, "bounds", "should")
      avoid_attr = extract_xml_attr(content, "bounds", "avoid")
      assert should_attr, f"{stem}: <bounds> missing 'should' attribute"
      assert avoid_attr, f"{stem}: <bounds> missing 'avoid' attribute"
  ```
- [ ] 4b. `test_command_structure.py:142-144`: Same pattern with `stem, content, _ = command`

## Task 5: Run full test suite + final verification

- [ ] 5a. `uv run pytest` — full suite, compare to baseline (~1,628 passing)
- [ ] 5b. If failures, fix and re-run
- [ ] 5c. Update spec status to `implemented`, plan status to `implemented`
