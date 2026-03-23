# Model-Agnostic Compatibility for SuperClaude

**Date:** 2026-03-23
**Author:** chosh1179
**Source:** Brainstorm session — Sonnet compatibility audit expanded to full model-agnostic design
**Status:** Delivered — all 4 sprints complete

---

## Executive Summary

SuperClaude framework has 17 hardcoded "Opus 4.6" assumptions across 6 files (core/RULES.md, core/PRINCIPLES.md, core/FLAGS.md, MODE_Token_Efficiency.md, simplicity-guide.md, 21 agent frontmatters). These assumptions cause incorrect guidance when the framework runs on Sonnet or other models — most critically, anti-over-engineering guardrails that are counterproductive for Sonnet (which under-delivers rather than over-engineers).

**Design philosophy: Remove model assumptions, don't add model-conditional logic.**

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent model routing | Full inherit (remove `model:` from all 21 agents) | Respect user's model choice; no cost surprises |
| Anti-over-engineering | Keep 7 rules + add `model_tendencies` self-calibration | Proven rules preserved; +30 tokens for universal applicability |
| Core files | Remove all "Opus 4.6" hardcoding | Model reads its own name; framework shouldn't assume |
| Detection mechanism | None needed | Models self-identify; hybrid notes sufficient |

### Change Summary

| Category | Files | Changes | Token Impact |
|----------|-------|---------|--------------|
| Agent frontmatter | 21 agents | Remove `model:` field | -21 lines (~-63 tokens) |
| Agent authoring rule | agent-authoring.md | `model: required` → `optional` | ±0 |
| Agent README | agents/README.md | Remove Model column, update routing doc | -20 lines |
| Core RULES.md | 1 file | Generalize note + add model_tendencies | +30 tokens |
| Core PRINCIPLES.md | 1 file | Generalize 2 notes | ±0 |
| Core FLAGS.md | 1 file | Generalize 3 hardcoded references | ±0 |
| Mode | MODE_Token_Efficiency.md | Generalize 1 note | ±0 |
| Agent | simplicity-guide.md | Generalize 1 note | ±0 |
| **Net** | **27 files** | | **~-33 tokens** |

---

## Audit Findings

### Model-Specific Content Map

| Location | Line(s) | Content | Severity |
|----------|---------|---------|----------|
| RULES.md | 82 | `note="Opus 4.6 tends to over-engineer"` | 🔴 HIGH — counterproductive on Sonnet |
| RULES.md | 59 | `note="examples teach better than rules for Opus 4.6"` | 🟡 MEDIUM — misleading |
| PRINCIPLES.md | 24 | `note="Opus 4.6 adaptive thinking"` | 🔴 HIGH — wrong guidance on other models |
| PRINCIPLES.md | 52 | `note="Opus 4.6"` (multimodal) | 🟡 MEDIUM — Sonnet 4.6 also has vision |
| FLAGS.md | 39 | `Default: sub-agents inherit parent model unless explicit model field` | 🟢 OK — already correct |
| FLAGS.md | 40 | `Heuristic: opus for all specialist agents \| sonnet for repo-index` | 🔴 HIGH — obsoleted by full inherit |
| FLAGS.md | 48 | `--fast: same Opus 4.6 model, faster output` | 🟡 MEDIUM — misleading on Sonnet |
| FLAGS.md | 51 | `Note: Opus 4.6 overengineers by default` | 🔴 HIGH — wrong on Sonnet |
| FLAGS.md | 52 | `Note: Opus 4.6 uses 25-50% more tokens than 4.5` | 🟡 MEDIUM — model-specific |
| MODE_Token_Efficiency.md | 27 | `Opus 4.6 uses 25-50% more tokens` | 🟡 MEDIUM |
| simplicity-guide.md | 36 | `note="Opus tendencies to resist"` | 🟡 MEDIUM |
| 21 agent .md files | line 4 | `model: opus` (or `sonnet`) | 🔴 HIGH — prevents inheritance |

### Clean Areas (no model dependencies)

- MCP documentation (9 files)
- Commands (32 files)
- Skills (11 files)
- context_loader.py (Python code)
- Hooks and scripts
- Test suite (no model validation in test_agent_structure.py)

---

## Sprint 1: Agent Model Routing — Full Inherit

### 1.1 Remove `model:` from all 21 agent frontmatters

**Before** (each agent):
```yaml
---
name: backend-architect
description: ...
model: opus          # ← remove this line
permissionMode: default
memory: project
color: blue
---
```

**After:**
```yaml
---
name: backend-architect
description: ...
permissionMode: default
memory: project
color: blue
---
```

**Files (21):**
- backend-architect.md, business-panel-experts.md, deep-researcher.md
- devops-architect.md, frontend-architect.md, git-workflow.md
- learning-guide.md, performance-engineer.md, project-initializer.md
- project-manager.md, python-expert.md, quality-engineer.md
- refactoring-expert.md, repo-index.md, requirements-analyst.md
- root-cause-analyst.md, security-engineer.md, self-review.md
- simplicity-guide.md, socratic-mentor.md, system-architect.md
- technical-writer.md

**Behavior:** All agents inherit the parent session's model. User chose Opus → agents run Opus. User chose Sonnet → agents run Sonnet.

### 1.2 Update agent-authoring.md

**Before:**
```yaml
model: opus|sonnet|haiku                   # required | see model routing below
```

**After:**
```yaml
model: opus|sonnet|haiku                   # optional | omit to inherit parent model (recommended)
```

**model routing heuristic section — Before:**
```markdown
- `opus` — architecture, security, judgment, deep analysis, strategy
- `sonnet` — coding, documentation, analysis, testing, teaching
- `haiku` — mechanical scanning, indexing, low-complexity reads
```

**After:**
```markdown
- Default: omit `model:` field — agent inherits parent session's model (recommended)
- Override: set `model:` explicitly only when a specific model is required regardless of user's session choice
- Use sparingly — explicit `model:` overrides the user's cost/speed preference
```

### 1.3 Update agents/README.md

**Before:**
```markdown
| Agent | Model | Permission | Description |
|-------|-------|------------|-------------|
| `backend-architect` | sonnet | default | ... |
```

**After:**
```markdown
| Agent | Permission | Description |
|-------|------------|-------------|
| `backend-architect` | default | ... |
```

Remove Model column entirely. Add routing note at bottom:

```markdown
## Model Routing

All agents inherit the parent session's model by default. No `model:` field in frontmatter.
To pin a specific model, add `model: opus|sonnet|haiku` to frontmatter (not recommended — overrides user's choice).
```

### 1.4 Verification

```bash
uv run pytest tests/unit/test_agent_structure.py -v
# Expected: all pass (tests don't validate model field)
```

---

## Sprint 2: Core Files — Remove Opus Hardcoding

### 2.1 RULES.md — anti_over_engineering

**Before (line 82):**
```xml
<anti_over_engineering note="Opus 4.6 tends to over-engineer — these rules are critical guardrails">
```

**After:**
```xml
<anti_over_engineering note="Scope discipline — prevent gold-plating">
```

**Before (line 59):**
```xml
<examples note="Representative scenarios — examples teach better than rules for Opus 4.6">
```

**After:**
```xml
<examples note="Representative scenarios — examples teach better than rules">
```

**Add after line 99 (before `</anti_over_engineering>`):**
```xml
  <model_tendencies note="Self-calibrate based on your known behavioral patterns">
    Over-engineering signals: creating classes for one-time operations, adding config for fixed values, building frameworks for single features
    Under-engineering signals: skipping error handling at system boundaries, omitting types in public interfaces, happy-path-only testing
  </model_tendencies>
```

7 existing rules and 3 existing examples **unchanged**.

### 2.2 PRINCIPLES.md — thinking_strategy

**Before (line 24):**
```xml
<thinking_strategy note="Opus 4.6 adaptive thinking">
Complex reasoning (debug, arch): Adaptive Thinking (auto)
Task planning: manual thinking block
Simple tasks: neither (adaptive may skip)
Anti-pattern: Extended + Manual = redundant; choose one by complexity
</thinking_strategy>
```

**After:**
```xml
<thinking_strategy note="Adaptive by complexity">
Complex reasoning (debug, arch): extended thinking when available
Task planning: structured thinking block
Simple tasks: direct response
Anti-pattern: Extended + Manual = redundant; choose one by complexity
</thinking_strategy>
```

### 2.3 PRINCIPLES.md — multimodal

**Before (line 52):**
```xml
<multimodal note="Opus 4.6">
```

**After:**
```xml
<multimodal note="Vision-capable models">
```

### 2.4 FLAGS.md — execution section

**Before (lines 39-41):**
```
  Default: sub-agents inherit parent model unless explicit model field in agent frontmatter
  Heuristic: opus for all specialist agents | sonnet for repo-index (scanning) | haiku for future lightweight tasks
  Override: user can set explicit model in Task() calls
```

**After:**
```
  Default: sub-agents inherit parent model (no agent declares model: by default)
  Override: add model: to agent frontmatter to pin a specific model (overrides user's session choice)
```

**Before (line 48):**
```
--fast: same Opus 4.6 model, faster output (v2.1.36+)
```

**After:**
```
--fast: same model, faster output (v2.1.36+)
```

**Before (lines 51-52):**
```
Note: Opus 4.6 overengineers by default — see RULES.md anti_over_engineering for guardrails
Note: Opus 4.6 uses 25-50% more tokens than 4.5 — monitor context usage
```

**After:**
```
Note: see RULES.md anti_over_engineering for scope discipline guardrails
Note: token consumption varies by model — monitor context usage, use --uc at 60%+
```

### 2.5 Verification

```bash
uv run pytest tests/unit/ -v
# Expected: all pass (content-only changes to markdown)
```

---

## Sprint 3: Mode & Agent Content Updates

### 3.1 MODE_Token_Efficiency.md

**Before (line 27):**
```
  - Opus 4.6 uses 25-50% more tokens — trigger efficiency earlier
```

**After:**
```
  - Token consumption varies by model — monitor context usage proactively
```

### 3.2 simplicity-guide.md

**Before (line 36):**
```xml
<anti_patterns note="Opus tendencies to resist">
```

**After:**
```xml
<anti_patterns note="Common over-engineering tendencies">
```

7 anti-pattern items **unchanged** (universally good advice).

### 3.3 Verification

```bash
uv run pytest tests/unit/test_mode_structure.py tests/unit/test_agent_structure.py -v
```

---

## Sprint 4: Documentation & Deployment

### 4.1 Update MEMORY.md

Add entry documenting the model-agnostic transition.

### 4.2 Update FLAGS.md persona_index

No changes needed — persona_index is already model-agnostic.

### 4.3 Full test suite

```bash
uv run pytest
# Expected: 1,694+ pass (baseline), 0 new failures
```

### 4.4 Deploy

```bash
make deploy
```

---

## What Does NOT Change

| Item | Why unchanged |
|------|--------------|
| 7 anti-over-engineering rules | Content is universally good advice, not Opus-specific |
| 3 over-engineering examples | Same — right-sizing examples apply to all models |
| 16 core rules [R01]-[R16] | Already model-agnostic |
| context_loader.py | No model detection logic; no Python changes needed |
| Test suite | No tests validate `model:` field; content changes don't break structure tests |
| Commands (32 files) | Already model-agnostic |
| Skills (11 files) | Already model-agnostic |
| MCP docs (9 files) | Already model-agnostic |
| Hooks/scripts | Already model-agnostic |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Quality degradation when Haiku inherits for complex agents | Low | Medium | User chose Haiku knowingly; can override per-agent |
| README → frontmatter mismatch recurrence | Low | Low | Authoring rule now says "omit model:" as default |
| Existing memory references to "model: opus" agents | Low | None | Memory is context, not config — stale memory auto-corrects |

---

## Appendix: Agent Frontmatter Before/After Summary

| Agent | Before `model:` | After `model:` |
|-------|-----------------|----------------|
| system-architect | opus | *(removed — inherit)* |
| security-engineer | opus | *(removed — inherit)* |
| root-cause-analyst | opus | *(removed — inherit)* |
| self-review | opus | *(removed — inherit)* |
| requirements-analyst | opus | *(removed — inherit)* |
| business-panel-experts | opus | *(removed — inherit)* |
| deep-researcher | opus | *(removed — inherit)* |
| project-initializer | opus | *(removed — inherit)* |
| project-manager | opus | *(removed — inherit)* |
| simplicity-guide | opus | *(removed — inherit)* |
| backend-architect | opus | *(removed — inherit)* |
| frontend-architect | opus | *(removed — inherit)* |
| devops-architect | opus | *(removed — inherit)* |
| performance-engineer | opus | *(removed — inherit)* |
| quality-engineer | opus | *(removed — inherit)* |
| refactoring-expert | opus | *(removed — inherit)* |
| python-expert | opus | *(removed — inherit)* |
| technical-writer | opus | *(removed — inherit)* |
| learning-guide | opus | *(removed — inherit)* |
| socratic-mentor | opus | *(removed — inherit)* |
| git-workflow | opus | *(removed — inherit)* |
| repo-index | sonnet | *(removed — inherit)* |
