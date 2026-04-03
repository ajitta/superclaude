---
status: implemented
revised: 2026-04-03
---

# Insight Schema + Agent — Implementation Plan

**Goal:** Add `author` field to insight schema and create `insight-analyst` agent for contextual retrieval + annotation.
**Architecture:** Schema-only changes in command markdown + new agent markdown file. No Python code. Model-enforced conventions.
**Spec:** `docs/specs/insight-schema-agent-discovery-chosh1179-2026-04-03.md`

---

### Task 1: Update insight command schema

**Files:** Modify: `src/superclaude/commands/insight.md`

- [ ] Add `author` to Optional fields in `<schema>` section (always emitted, not enforced)
- [ ] Add `ref_ts` to Optional fields
- [ ] Add `annotation` to type taxonomy enum
- [ ] Add annotation rules: ref_ts must target non-annotation, agent verifies target exists, dedup check
- [ ] Add timestamp format note: second precision, colon offset (`+09:00`)
- [ ] Update `--stats` query in `<query_reference>` to exclude annotations by default
- [ ] Add `--query author=<name>` example
- [ ] Add annotation example to `<examples>` table
- [ ] Update dedup flow step to include annotation dedup guidance
- [ ] Verify: `uv run pytest tests/unit/test_command_structure.py -k insight -v`

### Task 2: Create insight-analyst agent

**Files:** Create: `src/superclaude/agents/insight-analyst.md`

Frontmatter:
```yaml
---
name: insight-analyst
description: Find and present relevant project insights with contextual analysis (triggers - find insights, past insights, what did we learn, insight history, search insights)
model: sonnet
permissionMode: default
memory: project
disallowedTools: NotebookEdit
color: purple
---
```

XML body sections (in order per agent-authoring.md template):
- [ ] `<role>` — mission + mindset
- [ ] `<focus>` — 4 capabilities: semantic search, context matching, annotation, formatting
- [ ] `<actions>` — 5 steps: understand → pre-filter → match → present → annotate
- [ ] `<outputs>` — formatted results, annotations, relevance summary
- [ ] `<tool_guidance>` — Proceed (jq, matching) / Ask First (annotations) / Never (modify, delete, cross-project)
- [ ] `<checklist>` — 4 items from spec
- [ ] `<memory_guide>` — Query-Patterns, Insight-Gaps, Cross-References + refs
- [ ] `<examples>` — 3-4 trigger/output pairs
- [ ] `<handoff>` — `/sc:insight /sc:analyze /sc:save`
- [ ] `<gotchas>` — orphaned-ref-ts, stats-inflation, tz-mismatch
- [ ] `<bounds>` — will/wont/fallback from spec
- [ ] Verify: `uv run pytest tests/unit/test_agent_structure.py -k insight -v`

### Task 3: Update agents README

**Files:** Modify: `src/superclaude/agents/README.md`

- [ ] Add `insight-analyst` to Research & Analysis table
- [ ] Update Model Routing table: sonnet count 10→11, add `insight-analyst` to sonnet agent list
- [ ] Update Model Routing description line 83: "10 agents" → "11 agents"

### Task 4: Update FLAGS.md model routing

**Files:** Modify: `src/superclaude/core/FLAGS.md`

- [ ] Add `insight-analyst` to Sonnet agent list in `<model_routing>` section
- [ ] Update "10 agents pinned to sonnet" → "11 agents pinned to sonnet" in `--delegate` description

### Task 5: Update discovery spec status

**Files:** Modify: `docs/specs/insight-schema-agent-discovery-chosh1179-2026-04-03.md`

- [ ] Change `status: draft` → `status: implemented`

### Task 6: Deploy and validate

- [ ] `make deploy`
- [ ] `uv run pytest tests/unit/test_agent_structure.py -v` (full agent suite)
- [ ] `uv run pytest tests/unit/test_command_structure.py -v` (full command suite)
- [ ] Verify insight-analyst appears in agent list after deploy

---

## Execution Order

```
Task 1 (schema) ──┐
                   ├── Task 3 (README) ──┐
Task 2 (agent) ───┘                      ├── Task 5 (spec status) → Task 6 (deploy+validate)
                   Task 4 (FLAGS) ───────┘
```

Tasks 1+2 are independent (parallel). Tasks 3+4 depend on Task 2 frontmatter being finalized. Task 5+6 are sequential at the end.
