---
status: draft
revised: 2026-04-25
spec: ./01-discovery.md
depends-on: ./05a-plan-pr1-p0.md
---

# PR2: P1 Drift Fixes — Update skill-authoring.md to Current Anthropic Truth

**Goal:** Replace stale figures, fix wrong field formats, add missing supported fields (narrowed per D8), add XML house-style callout (D6 two-location), mark optional vs required body tags, and add the reserved-words constraint promoted from P3.

**Architecture:** Single-file edits to `.claude/rules/skill-authoring.md`. No shipped-skill changes. Plus one investigation task (D12) for plugin-distribution.

**References:** Spec P1-1 through P1-7, D6, D8, D10, D12, P2-7.

**Prerequisite:** PR1 must be merged. After PR1, `when-to-use` is gone and the file is in a known clean state.

---

### Task 1: Top-of-file XML house-style callout (D6 part 1)

**Files:** Modify: `.claude/rules/skill-authoring.md` (top of file)

- [ ] Insert a blockquote callout immediately after the title line, before the "Decision gate" section:
  ```
  > **House style note.** SuperClaude uses XML body for all authoring; this diverges from Anthropic's "no XML anywhere" guidance for skills. Decision rationale: `docs/research/rules-xml-conversion-ajitta-2026-04-14.md`. CC runtime accepts both forms; if redistributing a skill outside SuperClaude, prefer Markdown headings.
  ```

---

### Task 2: Fix `SLASH_COMMAND_TOOL_CHAR_BUDGET` figure (P1-1)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Rules #2)

- [ ] Replace "전체 skill/command description 합산 ~15,000 chars (`SLASH_COMMAND_TOOL_CHAR_BUDGET`)" with: "전체 skill/command description budget: **1% of the context window, fallback ~8,000 chars** (override via `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var)."

**Verify:** `grep "15,000\|16,000" .claude/rules/skill-authoring.md` returns nothing.

---

### Task 3: Simplify the 1,536 cap framing (P1-2)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Reference inline comment + Field Rules #2)

- [ ] Update the inline YAML comment on `description:` to: `# ≤1024 chars (validator-friendly), ≤1,536 chars (CC listing cap, soft truncation)`.
- [ ] Drop the "combined description + when_to_use" framing from Field Rules #2 — post-PR1, it's `description` only.

---

### Task 4: Fix `allowed-tools` format (P1-3)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Reference + Field Rules #5 templates)

- [ ] Change all `allowed-tools` examples from comma-separated to space-separated: `Read, Grep, Glob` → `Read Grep Glob`.
- [ ] Add a 1-line clarification under Field Rules #5: "`allowed-tools` is permission-grant (no-prompt list), not access-restriction. Tools not listed remain callable but require user approval."

---

### Task 5: Add `${CLAUDE_SKILL_DIR}` and `paths:` to field reference (P1-4 / D8)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Reference block)

- [ ] Add `paths:` to the Field Reference YAML with brief comment: `paths: ["**/api/**"]   # rarely needed; auto-load only on matching files`.
- [ ] Add a "Template Variables" subsection (or extend existing "Template variables" section at L128) with `${CLAUDE_SKILL_DIR}`:
  > `${CLAUDE_SKILL_DIR}` (Anthropic-portable): expands at runtime to the skill's install directory. Use this instead of `{{SKILLS_PATH}}` if the skill may be redistributed via plugin marketplace, where install-time substitution may not fire.
- [ ] Do NOT add `arguments`, `shell`, inline `` !`<cmd>` `` per D8.

---

### Task 6: Inline reminder of XML house-style note (D6 part 2)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Body Structure section header)

- [ ] Add 1 line directly under the "Body Structure (XML `<component>`)" header: `> See top-of-file house-style note: this XML body convention diverges from Anthropic's guidance and is intentional.`

---

### Task 7: Mark optional vs required XML body tags (P1-6)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Body Structure XML template)

- [ ] In the XML template, annotate tags:
  - **Required:** `<role>`, `<gotchas>`, `<bounds>`, `<handoff>` — mark with `(required)` comment.
  - **Optional:** `<references>`, `<syntax>`, `<flow>`, `<tools>`, `<examples>` — mark with `(optional)` comment.
- [ ] Add a 1-line note under the template: "Required tags appear in 5/5 shipped skills. Optional tags are skill-shape-dependent."

---

### Task 8: Reserved-words constraint on `name:` (P1-7 / D10)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Field Rules section)

- [ ] Add a new Field Rule item: "`name:` cannot contain reserved words `anthropic` or `claude` — installs silently fail. Per Anthropic's authoring guide."

---

### Task 9: Install-path scope correction (P2-7)

**Files:** Modify: `.claude/rules/skill-authoring.md` (Directory Structure / Install path section)

- [ ] Replace "Install path: `src/superclaude/skills/ → ~/.claude/skills/`" with:
  > Install paths (per `src/superclaude/cli/install_components.py:46-55`):
  > - `--scope user` (default): `src/superclaude/skills/ → ~/.claude/skills/` (absolute).
  > - `--scope project` or `--scope local`: `src/superclaude/skills/ → ./.claude/skills/` (relative).

---

### Task 10: Plugin-distribution investigation (D12)

**Files:** Investigation only; output goes to PR description, not files.

- [ ] Read `src/superclaude/cli/install_components.py:_resolve_skill_templates` (around L58-71) — does it fire on `/plugin install` paths, or only on `superclaude install`?
- [ ] Search for any plugin-marketplace install hook in the codebase: `grep -rn "marketplace\|plugin.*install" src/superclaude/cli/`.
- [ ] Document findings in PR description:
  - Confirmed firing → no follow-up needed.
  - Not firing → log a follow-up issue with title "skill template substitution skipped on plugin-marketplace install" and link from PR description.

**Verify:** PR description includes a 2-3 line "Plugin distribution check" subsection.

---

### Task 11: Final verification + commit

- [ ] `uv run pytest` — baseline 1,628+ passing.
- [ ] `make verify` passes.
- [ ] Visual diff of `.claude/rules/skill-authoring.md` — all 9 edit points landed; no accidental reformatting.
- [ ] Commit:
  ```
  docs(skills): fix drift in skill-authoring.md vs Anthropic v2.1.119

  - Update SLASH_COMMAND_TOOL_CHAR_BUDGET formula (1% / 8K fallback)
  - Simplify description cap framing (post-PR1: description-only)
  - Switch allowed-tools examples to space-separated; clarify grant semantics
  - Add ${CLAUDE_SKILL_DIR} and paths: to field reference
  - Add XML house-style callout (top-of-file + Body Structure inline)
  - Mark required vs optional XML body tags
  - Add reserved-words constraint on name: (runtime-fail)
  - Correct install-path scope (2 targets, not 3)

  Plus plugin-distribution investigation (see PR description).
  Spec: ./01-discovery.md
  ```
