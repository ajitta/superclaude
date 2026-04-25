---
status: draft
revised: 2026-04-25
spec: docs/specs/skill-authoring-consistency-discovery-ajitta-2026-04-25.md
depends-on: docs/plans/skill-authoring-consistency-pr3-p2-ajitta-2026-04-25.md
---

# PR4: P3 Cosmetic — Bilingual Standardization + Conditional Gotchas

**Goal:** Standardize inline YAML comments to English (D4); optionally adopt Anthropic style recommendations; conditionally include runtime-bug gotchas only after staleness verification (D9).

**Architecture:** Single-file edit on `.claude/rules/skill-authoring.md` for D4 + optional style uplift. Conditional addition of a runtime-bug gotcha subsection if D9 verification passes.

**References:** Spec P3-1, P3-2, P3-3, D4, D9.

**Prerequisite:** PR3 merged.

---

### Task 1: Standardize YAML inline comments to English (D4 / P3-1)

**Files:** Modify: `.claude/rules/skill-authoring.md` (YAML field reference block)

- [ ] Replace Korean inline YAML comments with English equivalents. Examples:
  - `# 권장 | lowercase+hyphens, ≤64자` → `# recommended | lowercase+hyphens, ≤64 chars`.
  - `# 권장 | ≤1,536 chars (CC 2.1.105+ listing cap, 초과 시 기동 경고)` → `# recommended | ≤1,536 chars (CC 2.1.105+ listing cap; truncation warning on startup)`.
  - All other Korean YAML comments in the field reference → translate to English.
- [ ] Korean prose in non-YAML sections may stay as-is (audience-driven decision; not in scope).

**Verify:** `grep -P '[\x{AC00}-\x{D7AF}]' .claude/rules/skill-authoring.md` shows hits only in prose sections, not YAML blocks.

---

### Task 2: Optional Anthropic style recommendations (P3-2)

**Files:** Modify: `.claude/rules/skill-authoring.md` (new "Style recommendations" subsection)

- [ ] Add a "Style recommendations" subsection (1 short paragraph each):
  - **Gerund naming:** prefer `processing-pdfs` over `pdf-processor` for skill names.
  - **Reference-file ToC:** if a `references/*.md` file exceeds 100 lines, add a table-of-contents at the top.
  - **Time-sensitive content:** wrap "old patterns" in `<details>` collapsible blocks so they don't dominate context.
- [ ] Mark this subsection as **optional / advisory**, not required, in the section header.

(Third-person voice rule is already absorbed by PR1's description authoring pattern — no separate task.)

---

### Task 3: Verify GH issue staleness (D9 gate)

**Files:** Investigation only — output gates Task 4.

For each cited issue, check status:
- [ ] `gh issue view 17688 --repo anthropics/claude-code` — open or closed?
- [ ] `gh issue view 40630 --repo anthropics/claude-code` — open or closed?
- [ ] `gh issue view 30874 --repo anthropics/claude-code` — open or closed?

Decision matrix:
- **All 3 closed/fixed** → skip Task 4 entirely; runtime-bug section not added.
- **At least 1 still open** → proceed to Task 4 with only the still-open ones.

Document each issue's status in PR description.

---

### Task 4 (CONDITIONAL): Runtime-bug gotcha subsection (P3-3 / D9)

**Files:** Modify: `.claude/rules/skill-authoring.md` (new "Runtime quirks" or `<gotchas>` subsection)

**Only execute if Task 3 found at least one open issue.**

- [ ] Add a "Runtime quirks (CC version-pinned)" subsection at the bottom of the file.
- [ ] List only the issues confirmed still-open in Task 3, with: 1-line description + GH URL + last-verified date.
- [ ] Mark the subsection with a `<!-- last reviewed: 2026-04-25 -->` HTML comment.
- [ ] Add a sentence: "Re-verify these issues quarterly; remove fixed ones."

---

### Task 5: Final verification + commit

- [ ] `uv run pytest` — baseline 1,628+ passing.
- [ ] Visual diff of `.claude/rules/skill-authoring.md`.
- [ ] Korean-character check: `grep -P '[\x{AC00}-\x{D7AF}]' .claude/rules/skill-authoring.md | grep "^[^#]*\(name:\|description:\|when_to_use:\|effort:\|model:\|hooks:\|paths:\)"` returns nothing (no Korean in YAML reference).
- [ ] Commit:
  ```
  docs(skills): standardize skill-authoring YAML comments to English

  - YAML inline comments: Korean → English (matches peer authoring files)
  - Optional style recommendations subsection (gerund naming, ToC, <details>)
  - Runtime-quirks subsection: [conditional — N issues confirmed still-open]
    OR: omitted (all cited issues closed/fixed as of 2026-04-25)

  Spec: docs/specs/skill-authoring-consistency-discovery-ajitta-2026-04-25.md
  ```

---

## Out of scope

- Translating Korean prose elsewhere in skill-authoring.md (audience-driven, not in spec scope).
- Translating other authoring files' Korean content (none exists currently).
