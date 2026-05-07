---
status: draft
revised: 2026-04-14
---

# Discovery: `.claude/rules/` Schema Extraction (not XML Conversion)

## Original request

> ".claude/rules/** 를 XML hybrid 형식 + YAML frontmatter로 만들기"
>
> Motivation: (1) testability, (2) consistency with agent/command/skill format.

## Why the scope changed

Research (`docs/research/rules-xml-conversion-ajitta-2026-04-14.md`, confidence 0.78) converged on a **smaller, sharper intervention** than the original request. Key findings:

1. **Tests never read the rule docs.** Grep of `tests/` for `authoring.md` returns zero matches. `VALID_COLORS`, `VALID_EFFORT_VALUES`, `FORBIDDEN_FIELDS` are hardcoded in Python test files, parallel to rule doc prose. They have already drifted once: `VALID_COLORS` (test_agent_structure.py:17) includes `red`, but agent-authoring.md "color by role group" table has no `red` role.
2. **Only 3 enum sets are genuinely duplicated.** Colors, effort values, forbidden command fields. Everything else in the 828-line rule corpus is pedagogical prose (templates, checklists, anti-patterns) — not mechanically testable.
3. **Anthropic does not forbid XML in authoring doc bodies.** Earlier research overstated this (see research doc correction appended 2026-04-14). The ban is narrow — `name`/`description` frontmatter fields only. So XML is *permitted*, but also not *necessary*.
4. **Consistency claim is cosmetic.** Rule docs are read by humans authoring new content and by Claude when loaded via `@.claude/rules/`. Markdown tables and prose render well for both audiences. XML structure would not improve either reader.

## Revised goal

**Extract only what is duplicated, not what is prose.** Create a single `.claude/rules/schemas.yaml` holding the three enum sets. Wire existing tests to load from it. Leave all 828 lines of prose rule guides untouched in their current markdown form.

## Scope (in / out)

### In scope
- New file: `.claude/rules/schemas.yaml` holding:
  - `agent_colors` — role group → allowed color mapping (kills the current `red` drift)
  - `effort_values` — allowed effort enum with per-value semantics
  - `forbidden_command_fields` — fields disallowed in command frontmatter
- Edit `tests/unit/test_agent_structure.py` to load `VALID_COLORS` + `VALID_EFFORT_VALUES` from schemas.yaml
- Edit `tests/unit/test_command_structure.py` to load `FORBIDDEN_FIELDS` from schemas.yaml
- Minimal prose sync: update the 3 tables in agent-authoring.md / command-authoring.md to reference `schemas.yaml` as source of truth (single-line pointer, no body rewrite)

### Out of scope — explicitly deferred
- XML `<component>` wrapping of agent-authoring.md / command-authoring.md / skill-authoring.md / mode-authoring.md
- YAML frontmatter on the authoring rule docs (`status:`, `revised:`, `name:`)
- Gotchas files (`gotchas/*.md`) — the line-format `- name: description` is intentional and already structured enough for CC native loading
- Extraction of XML structure templates, checklists, anti-pattern tables (pedagogical; no test consumer)
- skill/mode authoring rule extraction (tests already pass; no observed drift; not duplicated)

## Requirements

| ID | Requirement | Verification |
|---|---|---|
| R1 | Single source of truth for agent colors, effort values, forbidden command fields | `grep -r "VALID_COLORS\s*=" tests/` returns 0 hardcoded literals |
| R2 | Color drift (`red` in tests but not in role-group table) is resolved | Either `red` added with role group, or removed from test set — decision documented in YAML comment |
| R3 | `pytest tests/unit/` baseline preserved — no new failures introduced | 1,628+ passing maintained (CLAUDE.md baseline) |
| R4 | schemas.yaml is human-readable and self-documenting | Comments explain each key; no magic strings |
| R5 | Prose rule docs (agent/command/skill/mode-authoring.md) remain authoritative for *how to author*; schemas.yaml is authoritative only for *what values are valid* | Single-line reference in prose tables pointing to schemas.yaml |

## Artifacts to produce (during implementation, not now)

1. `.claude/rules/schemas.yaml` — new file, ~20–30 lines
2. `tests/unit/test_agent_structure.py` — load colors + effort from YAML
3. `tests/unit/test_command_structure.py` — load forbidden fields from YAML
4. `.claude/rules/agent-authoring.md` — add pointer comment to schemas.yaml in the color + effort tables
5. `.claude/rules/command-authoring.md` — add pointer comment in forbidden-fields list

Estimated diff: **<60 lines total** (research estimate: <50; add 10 for prose pointers).

## Necessity test ([R18 Necessity Test])

Is the system broken without this?

- **Drift bug**: `VALID_COLORS` permits `red` but role-group taxonomy has no `red` role. A new agent authored with `color: red` passes tests but violates the documented role-group rule. Latent correctness bug. ✅ justifies change.
- **Duplication**: 3 enums maintained in two places. Not broken today, but the drift above is evidence the coupling is unreliable over time. ✅ justifies change.
- **Pure prose extraction**: would not fix a broken system — pedagogical docs serve their purpose as markdown. ❌ fails necessity test → deferred.

Verdict: **pass for partial extraction, fail for full XML conversion.**

## Open questions (resolve during /sc:plan)

1. For the `red` drift: add `red` to agent-authoring.md as a recognized role (which role?) OR remove `red` from test's `VALID_COLORS`? Evidence from `git log` + `grep -r "color: red" src/superclaude/agents/` needed.
2. YAML schema format: flat lists vs nested mapping? Prefer nested (`colors: {architecture: blue, engineering: green, ...}`) so the mapping itself is asserted, not just the flat set.
3. Test loader pattern: module-level `SCHEMAS = yaml.safe_load(...)` at top of each test file, or shared fixture in `conftest.py`? Shared fixture preferred if both files load the same YAML.

## Trade-offs accepted

- **Format heterogeneity**: rule docs remain markdown + one YAML sidecar. Not visually uniform with agents/commands content. Accepted — research confirmed uniformity is cosmetic.
- **Incomplete testability**: only 3 enums become test-consumed. Remaining ~820 lines stay human-verified. Accepted — those sections are pedagogical, not mechanical.
- **Soft deferral of XML on SKILL.md**: 5 existing SKILL.md files use `<component>` XML bodies. Anthropic API rules permit this (ban is frontmatter-only). Left as-is; not revisited here.

## Handoff

- **Next command**: `/sc:plan` — produce phased implementation plan with file-level TDD tasks
- **Acceptance gate before /sc:plan**: user confirms this discovery spec (R1–R5 scope, deferred items, open questions)
- **Not recommended**: jumping to `/sc:implement` — open questions (especially #1: the `red` drift resolution) need a plan pass to lock down evidence-based decisions

## References

- Research: `docs/research/rules-xml-conversion-ajitta-2026-04-14.md` (with correction appended)
- Existing authoring guides: `.claude/rules/{agent,command,skill,mode}-authoring.md`
- Existing tests: `tests/unit/test_{agent,command,skill,mode}_structure.py`
- Rules: R18 (necessity test), R06 (scope), R15 (verification)
