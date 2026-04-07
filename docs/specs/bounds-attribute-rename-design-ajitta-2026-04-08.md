---
status: implemented
revised: 2026-04-08
---

# Bounds Attribute Rename: `will/wont` → `should/avoid`

## Problem

The `<bounds>` XML tag uses `will` and `wont` as attribute names across all 77 content files (23 agents, 33 commands, 7 modes, 5 skills, 8 MCP docs, 1 architecture doc). Two issues:

1. **`wont` is a real English word** meaning "habitual tendency" (archaic) — the semantic opposite of the intended "will not". XML attributes can't contain apostrophes cleanly, so `won't` was never viable.
2. **`will` is declarative/predictive** ("the agent will do X") rather than normative/directive ("the agent should do X"). Normative framing aligns better with how LLMs process behavioral instructions.

## Decision

Rename attributes: `will` → `should`, `wont` → `avoid`. Keep `fallback` unchanged.

### Before/After

```xml
<!-- Before -->
<bounds will="accessible UI|frontend perf" wont="backend APIs|database ops" fallback="Escalate to backend-architect"/>

<!-- After -->
<bounds should="accessible UI|frontend perf" avoid="backend APIs|database ops" fallback="Escalate to backend-architect"/>
```

## Design Rationale

| Factor | `will/wont` | `should/avoid` |
|--------|------------|----------------|
| Semantic clarity | `wont` = archaic "habit" | Both unambiguous |
| Grammar | `wont` ≠ `won't` | Standard modern English |
| LLM compliance frame | Declarative (predictive) | Normative (directive) |
| Brevity | 4+4 chars | 6+5 chars |
| Readability | "wont backend APIs" = ? | "avoid backend APIs" = clear |

`fallback` stays — it's already a clear, unambiguous noun.

## Scope

### Change Surface

| Category | File Count | Complexity | Notes |
|----------|-----------|------------|-------|
| Agent content | 23 | Low | Attribute replacement in `<bounds>` |
| Command content | 33 | Low | Same |
| Mode content | 7 | Low | Same |
| Skill content | 5 | Low | Same |
| MCP docs | 8 | Low | Same |
| Architecture doc | 1 | Low | Pattern reference |
| Authoring rules | 4 | Medium | Templates + requirement text + examples |
| Test files | 1 critical | Medium | `test_mode_structure.py` checks `will`/`wont` by name |
| **Total** | **82 files** | Low-Medium | 77 content + 4 rules + 1 test |

**Note:** Multi-line `<bounds>` tags exist (e.g., `verbalized-sampling/SKILL.md:70-71` where `wont=` is on a continuation line). Replacement must handle this.

### NOT In Scope

- Changing `fallback` attribute (stays as-is)
- Restructuring `<bounds>` tag semantics or merging with `<tool_guidance>`
- Adding new attributes
- Changing tag name from `<bounds>` to something else
- Historical docs in `docs/specs/` and `docs/plans/` — these are point-in-time records; leave `will/wont` as-is
- `CLAUDE.md` — contains no bounds attributes (confirmed)

## Validation Surface (Critical Path)

Only **one test** validates attribute names:

**`tests/unit/test_mode_structure.py:93-99`**
```python
will_attr = extract_xml_attr(content, "bounds", "will")
wont_attr = extract_xml_attr(content, "bounds", "wont")
assert will_attr, f"{stem}: <bounds> missing 'will' attribute"
assert wont_attr, f"{stem}: <bounds> missing 'wont' attribute"
```

Change to:
```python
should_attr = extract_xml_attr(content, "bounds", "should")
avoid_attr = extract_xml_attr(content, "bounds", "avoid")
assert should_attr, f"{stem}: <bounds> missing 'should' attribute"
assert avoid_attr, f"{stem}: <bounds> missing 'avoid' attribute"
```

Other tests (`test_agent_structure.py`, `test_command_structure.py`, `test_content_structure.py`) only check `<bounds ` tag presence — no attribute name validation. **Add `should`/`avoid` attribute checks to agent and command tests too** for consistency (T7 below).

## Implementation Strategy

**Approach: Batch find-and-replace with verification.**

All changes are mechanical attribute renames with no logic changes. Safe for parallel execution.

### Task Breakdown

| Task | Description | Parallel? |
|------|------------|-----------|
| T1 | Replace `will=` → `should=` and `wont=` → `avoid=` in all 77 content files (agents, commands, modes, skills, MCP, architecture) | Yes (by directory) |
| T2 | Update 4 authoring rules (templates, requirements, examples, anti-patterns) | Yes (parallel with T1) |
| T3 | Update test file (`test_mode_structure.py`) — rename attribute checks | Yes |
| T4 | Add `should`/`avoid` attribute checks to `test_agent_structure.py` and `test_command_structure.py` | Yes (parallel with T3) |
| T5 | Run full test suite — verify 0 regressions | After T1-T4 |

### Verification

```bash
# After all replacements:
# 1. No remaining will=/wont= in bounds tags
grep -rn 'bounds.*will=' src/superclaude/ --include="*.md" | wc -l  # expect: 0
grep -rn 'bounds.*wont=' src/superclaude/ --include="*.md" | wc -l  # expect: 0

# 2. All bounds tags have should=/avoid=
grep -rn 'bounds.*should=' src/superclaude/ --include="*.md" | wc -l  # expect: 77
grep -rn 'bounds.*avoid=' src/superclaude/ --include="*.md" | wc -l  # expect: 76

# 3. Full test suite passes
uv run pytest  # baseline: ~1,628 passing
```

**Edge case:** `verbalized-sampling/SKILL.md` has a multi-line `<bounds>` where `wont=` starts on line 71. Verify this file individually after replacement.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Missed file | Low | Low | Post-replace grep verification |
| Test regex breaks | Low | Medium | Single test file, simple change |
| Claude behavior regression | Very Low | Low | Attributes are documentary, not parsed by runtime |
| Installed user files stale | Medium | Low | `make deploy` refreshes all installed files |

## R18 Necessity Test

> "Is the system broken without this?"

No — the system functions. However:

1. `wont` semantically means the opposite of intended (archaic English)
2. Every new contributor/author encounters the ambiguity
3. The framework is pre-1.0 — rename cost only increases over time
4. Zero runtime risk (documentary-only attributes)

**Justification:** Semantic correctness fix for a framework-wide convention, not speculative improvement.
