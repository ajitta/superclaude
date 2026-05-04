---
status: complete
revised: 2026-05-05
---

## Execution Notes (2026-05-05)

- All 5 phases complete; status: `complete`.
- Phases 1-3 landed cleanly (commit `c83377d`).
- Phase 4 D2a: migrated 34 shipped command files via PowerShell regex; `tests/unit/test_command_structure.py:112` updated to accept both `<role>` and `<role command="…">` forms (regex `<role[\s>]`); empty-role guard at line 189 tightened to `<role[^>]*>\s*</role>`. Commit `62905e2`.
- Phase 4 D1a: initially deferred as editorial work, then completed in same session — all 6 shipped MCP docs (`MCP_Serena.md`, `MCP_Tavily.md`, `MCP_Playwright.md`, `MCP_Sequential.md`, `MCP_Chrome-DevTools.md`, `MCP_Context7.md`) migrated from `Use:`/`Avoid:` bullets to `<use>`/`<never>` prose. `MCP_Serena.md` retained the decision-rule framing sentence above the sub-tags. Commit `7222ba4`.
- Bonus cleanup: removed stale `.serena/memories/serena_followups_state_2026-04-26.md` snapshot. Commit `9bc7312`.
- Final test count: 1869 / 1869 passing (0 failures).
- No `<should>`/`<avoid>` slot-tag regressions; no residual `Use:`/`Avoid:` literal markers in `src/superclaude/mcp/`.
- All commits pushed to `origin/master`.

**Commit chain:** `e3d29bf` (baseline) → `c83377d` → `62905e2` → `7222ba4` → `9bc7312`.

# Authoring Spec Conformance Implementation Plan

**Goal:** Reconcile `xml-prose-format.md` with the 5 `*-authoring.md` meta-docs so the spec text, the templates, and the deployed components agree on section ordering — closing the spec-vs-practice gap surfaced by the 2026-05-05 audit.

**Architecture:** All changes are markdown-only edits to `.claude/rules/`. No source code, no shipped components, no installer logic touched. The spec text is updated to match the universally-deployed ordering (`examples → gotchas → bounds → handoff`), then two template-internal flips are corrected, then a shared cross-reference block is added to each authoring doc to surface 6 spec rules that were previously only in `xml-prose-format.md`.

**Tech Stack:** Markdown, XML-in-prose convention, `pytest` structural tests (regression guard only).

## Scope

In scope: `.claude/rules/xml-prose-format.md`, `.claude/rules/agent-authoring.md`, `.claude/rules/command-authoring.md`, `.claude/rules/skill-authoring.md`, `.claude/rules/mode-authoring.md`, `.claude/rules/mcp-authoring.md`.

Out of scope: shipped components under `src/superclaude/` (no migration needed — practice already matches the new spec text), `tests/`, installer code, `core/RULES.md`.

## Decision Gate (resolved 2026-05-05)

- **D1 → D1a:** Convert `mcp-authoring.md <choose>` to sub-tags (`<use>` / `<never>`). Matches `<bounds>` slot-tag discipline; drops "Avoid" hedging.
- **D2 → D2a:** Move `command-authoring.md <role>` identifier to attribute (`<role command="/sc:command-name">`). Cleanest per spec's attributes-vs-body rule.

## Phase 1 — Spec Ordering Reconciliation

**Files:** Modify: `.claude/rules/xml-prose-format.md` (Section Ordering at lines 14-26, Authoring Checklist item 3 at line 275, Skeleton at lines 206-255 if needed).

**Why first:** All later phases assume the new canonical order. Spec text is the source of truth — fix it before touching templates.

- [x] Step 1: Read `xml-prose-format.md:14-26` (Section Ordering numbered list) and `:275` (Checklist item 3).
- [x] Step 2: Update Section Ordering #5/#6/#7 to: `5. Examples` (was Bounds) → `6. Gotchas` (was Examples) → `7. Bounds / handoffs`. Rewrite the rationale sentence under #5 from "Bounds — edge cases and escalation" to keep examples-as-reference rationale, and add a new rationale under #7: "Bounds and handoff define exit semantics — paired together at component boundary so authors and readers see the scope-and-next-step pair adjacent."
- [x] Step 3: Update Authoring Checklist item 3 (line 275) from `identity → critical safety → core rules → tool/flag guidance → bounds → examples → gotchas` to `identity → critical safety → core rules → tool/flag guidance → examples → gotchas → bounds → handoff`.
- [x] Step 4: Verify Skeleton at lines 206-255 still illustrates the new order; reorder `<examples>` / `<bounds>` / `<example>` blocks if needed.
- [x] Step 5: Run `uv run python -m pytest tests/unit/ -v` to confirm no regression (spec ordering is not enforced by tests today; this is a baseline guard).
- [x] Step 6: Commit as `docs(rules): align xml-prose-format section ordering with deployed practice`.

## Phase 2 — Template Gotchas/Examples Flip (Commands & Skills)

**Files:** Modify: `.claude/rules/command-authoring.md:62-80` (XML template, XML Rules section). Modify: `.claude/rules/skill-authoring.md:191-208` (XML template, body rules).

**Why second:** Command and skill templates today show `<gotchas>` *before* `<examples>`, but the shipped `commands/analyze.md` places `<gotchas>` *after* `<examples>`. Templates and deployed reality disagree.

- [x] Step 1: In `command-authoring.md`, swap the order of `<gotchas>` (lines 62-64) and `<examples>` (lines 66-71) inside the XML template so `<examples>` precedes `<gotchas>`.
- [x] Step 2: In `skill-authoring.md`, swap the order of `<gotchas>` (lines 191-193) and `<examples>` (lines 195-200) inside the XML template so `<examples>` precedes `<gotchas>`.
- [x] Step 3: Verify `agent-authoring.md` template (lines 160-178) and `mode-authoring.md` template (lines 64-78) and `mcp-authoring.md` template (lines 61-78) already match the canonical order — no edit needed.
- [x] Step 4: Run `uv run python -m pytest tests/unit/test_command_structure.py tests/unit/test_skill_structure.py -v` to confirm no regression.
- [x] Step 5: Commit as `docs(rules): fix gotchas/examples order in command and skill templates`.

## Phase 3 — Shared Cross-Reference Block

**Files:** Modify: `.claude/rules/agent-authoring.md`, `command-authoring.md`, `skill-authoring.md`, `mode-authoring.md`, `mcp-authoring.md` (append a single new section near the end of each, before any "Anti-Patterns" or "Checklist" section if present).

**Why third:** Six rules in `xml-prose-format.md` are not echoed in any authoring doc; component authors reading only their domain doc miss them. Independent additive change — does not depend on Phases 1 or 2.

The block to append (identical text in all 5 docs, with the size-target row customized per component type):

```markdown
## Inherited from xml-prose-format.md

The following rules apply to all components and are not restated above. See `.claude/rules/xml-prose-format.md` for full text.

- **Single root XML wrapper** — exactly one root tag per component body; sibling sections only at root level.
- **Long-form embedded enumerations** — lists embedded in running prose use natural-language enumeration ("things include x, y, z"), not bullets.
- **Quoting conventions** — URLs and model identifier strings in single quotes (`'https://…'`, `'claude-opus-4-7'`); UI / product / feature names in double quotes (`"settings"`); runtime variables in double curly braces (`{{currentDateTime}}`).
- **Cross-references** — point to other sections by plain English topic, not by tag path.
- **Markdown headers inside `<example>`** — permitted when the illustration mirrors a real markdown artifact (report template, commit message, user document); the body-prose "no markdown headers" rule does not extend into `<example>` bodies.
- **Size target** — body ≤[N] lines for this component type ([component]); extract overflow into a referenced sibling file rather than inline-bloating the body.
```

- [x] Step 1: Append the block to `agent-authoring.md` (size target: ≤300 lines).
- [x] Step 2: Append to `command-authoring.md` (size target: ≤200 lines).
- [x] Step 3: Append to `skill-authoring.md` (size target: ≤500 lines — replaces existing scattered mention at line 220 if duplication is awkward; Korean-mixed prose retained elsewhere).
- [x] Step 4: Append to `mode-authoring.md` (size target: ≤300 lines).
- [x] Step 5: Append to `mcp-authoring.md` (no size target listed in spec for MCP; omit that bullet for this doc only).
- [x] Step 6: Commit as `docs(rules): add inherited-from-spec cross-reference block to authoring docs`.

## Phase 4 — Decision-Gated Polish

**Files:** Modify: `.claude/rules/mcp-authoring.md:43-50` (per D1). Modify: `.claude/rules/command-authoring.md:41-44` (per D2).

**Resolved:** D1a + D2a.

- [x] Step 1 (D1a): Replace `<choose>` template body in `mcp-authoring.md:43-50` with sub-tag form — `<choose>` containing `<use>...</use>` and `<never>...</never>` sub-tags, each holding prose. Update the body-rules paragraph (line 85 area) to describe the sub-tag form alongside `<bounds>`.
- [x] Step 2 (D2a): Update `command-authoring.md:41-44` template to `<role command="/sc:command-name"> <mission>...</mission> </role>`. Update XML Rules paragraph at line 89 to document the attribute form.
- [x] Step 3: Survey shipped MCP docs (`src/superclaude/mcp/MCP_*.md`) for any using the bare `Use:`/`Avoid:` form inside `<choose>`; if found, migrate to sub-tag form so deployed components match the new template (or note the gap as deferred work in the commit message if migration is broader than this plan's scope).
- [x] Step 4: Survey shipped command docs (`src/superclaude/commands/*.md`) for any using bare `/sc:command-name` lines inside `<role>`; migrate to attribute form for consistency.
- [x] Step 5: Run `uv run python -m pytest tests/unit/test_command_structure.py tests/unit/test_content_structure.py -v` to confirm no regression. The attribute form is structurally novel — if a test asserts on tag-body content of `<role>`, it may surface here.
- [x] Step 6: Commit as `docs(rules): apply mcp <choose> sub-tags and command <role command=> attribute`.

## Phase 5 — Verification & Closeout

**Files:** Read-only.

- [x] Step 1: Run `uv run python -m pytest tests/unit/ -v` and confirm 1373/1373 pass (baseline from migration commit `e3d29bf`).
- [x] Step 2: Grep for any residual `<should>`/`<avoid>` slot-tag references in `.claude/rules/` to confirm migration cleanup is intact: `grep -rn "<should>\|<avoid>" .claude/rules/` should return zero hits in slot-tag context.
- [x] Step 3: Read each authoring doc top-to-bottom once and verify:
  - Section-ordering language matches the new spec text.
  - Each XML template lists `<examples>` before `<gotchas>` before `<bounds>` before `<handoff>`.
  - Each doc carries the "Inherited from xml-prose-format.md" cross-reference block.
- [x] Step 4: Update `MEMORY.md` index entry under Project with a one-line note: `- [authoring-spec-conformance](project_authoring-spec-conformance.md) — section ordering reconciled with deployed practice (2026-05-05)`.
- [x] Step 5: Commit as `docs(rules): close authoring spec conformance audit`.

## Risks

- **R1:** Spec ordering change is text-only, no test enforces the old order. Risk: low. Verification: visual review.
- **R2:** Phase 3 cross-reference block could duplicate content already present in some authoring docs (e.g., `skill-authoring.md` mentions the size target). Risk: cosmetic. Mitigation: Step 3 of Phase 3 explicitly checks for overlap before appending.
- **R3:** D1a (sub-tags inside `<choose>`) introduces a structural pattern not currently used in any shipped MCP doc — no migration needed for `mcp/MCP_*.md` files unless a future MCP doc opts in. Risk: minor template-ahead-of-practice gap.

## Verification Commands

```powershell
uv run python -m pytest tests/unit/ -v          # full structural test suite (baseline 1373)
uv run python -m pytest tests/unit/test_command_structure.py tests/unit/test_skill_structure.py tests/unit/test_agent_structure.py tests/unit/test_mode_structure.py -v   # per-component subset
```

Per project gotcha: `uv run pytest` fails on Windows with "Failed to canonicalize script path"; use `uv run python -m pytest` instead.

## Out-of-Scope (deferred)

- Migrating shipped components to a different ordering (Phase 1 path B, rejected). Cost: ~80 files; benefit: zero, since deployed practice already matches the new spec text.
- Adding automated tests that enforce section ordering. The audit found ordering drift via inspection, not test failure; structural tests today validate tag presence, not order. Adding an order test is a separate hardening initiative.
