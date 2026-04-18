---
status: implemented
revised: 2026-04-18
---

# Opus 4.7 Alignment — Tier 1 Implementation Plan

**Goal:** Close three content-level gaps identified in the Opus 4.7 brainstorm spec: frontend-aesthetics guard, review-agent finding policy, and PRINCIPLES.md thinking framing. Persist the Part A verification checklist as a re-runnable artifact.

**Architecture:** Pure content framework edits — 5 markdown files modified, 1 new checklist artifact created. No Python, no schema changes, no new tests. Regression coverage comes from existing `tests/unit/test_agent_structure.py` and `test_content_structure.py`.

**Tech Stack:** Markdown + XML tags (SuperClaude agent format) · pytest for regression · ripgrep for Part A verification

**Spec:** `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md`

## Execution Log (2026-04-18)

| Task | Status | Evidence |
|------|--------|----------|
| 1. PRINCIPLES.md line 25/28 | ✅ done | `grep "adaptive thinking" src/superclaude/core/PRINCIPLES.md` matches line 25; V7 grep for "extended thinking" in core/ returns 0 |
| 2. frontend-architect `<aesthetics>` | ✅ done | 3 matches for aesthetics in file; V5 pass |
| 3. quality-engineer `<finding_policy>` | ✅ done | V6 pass (file in match list) |
| 4. self-review `<finding_policy>` | ✅ done | V6 pass (file in match list) |
| 5. security-engineer `<finding_policy>` | ✅ done | V6 pass (file in match list) |
| 6. Checklist artifact | ✅ done | `docs/reports/OPUS_4_7_ALIGNMENT.md` created; run results filled in |
| 7. Regression suite | ✅ pass | `uv run -- python -m pytest tests/unit/` → **1684 passed, 0 failed** (CLAUDE.md baseline "~1628" is stale — out of scope to fix here) |
| 8. Part A verification | ✅ done | V1/V2/V5/V6/V7 pass · V3 pending manual review · V4 deferred to T2-b |
| 9. Spec + plan status flip | ✅ done | spec `draft→approved`, plan `draft→implemented` |
| 10. Commit | ⏸ awaiting user approval | Commit message drafted; CLAUDE.md requires explicit "commit" before staging |

**Regression delta:** 0 new failures · 0 new errors · 1684 pass (net +0).
**Deferred work:** V3 manual RULES.md scope review · Tier 2 (T2-a effort:xhigh, T2-b subagent guidance rewrite) pending eval data.

**Open-question defaults taken (§6 of spec):**
- Q1 Tier 2 scope → deferred (this plan covers Tier 1 only)
- Q2 xhigh on coding agents → N/A (Q1 deferred)
- Q3 Part B ownership → manual user sessions + `/sc:insight` capture, not automated
- Q4 Part A cadence → manual checklist at `docs/reports/OPUS_4_7_ALIGNMENT.md` (CI lift can come later)
- Q5 Naming → "opus-4-7-alignment" (follows 2026-03-15 precedent; can rename in a future model-agnostic refactor)

---

## File Map

| File | Action | Lines affected | Purpose |
|------|--------|----------------|---------|
| `src/superclaude/core/PRINCIPLES.md` | Modify | `25` | Replace "extended thinking" with adaptive-thinking framing |
| `src/superclaude/agents/frontend-architect.md` | Modify | insert after `35` | Add `<aesthetics>` block (AI-slop guard) |
| `src/superclaude/agents/quality-engineer.md` | Modify | insert after `69` | Add `<finding_policy>` block |
| `src/superclaude/agents/self-review.md` | Modify | insert after `33` | Add `<finding_policy>` block |
| `src/superclaude/agents/security-engineer.md` | Modify | insert after `34` | Add `<finding_policy>` block |
| `docs/reports/OPUS_4_7_ALIGNMENT.md` | Create | — | Part A verification checklist (re-runnable) |
| `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` | Modify | frontmatter `status:` | Flip `draft` → `approved` after implementation |

---

## Tasks

### Task 1: Update PRINCIPLES.md thinking framing (T1-c)

**Files:** Modify: `src/superclaude/core/PRINCIPLES.md:25`
**Test:** `uv run pytest tests/unit/test_content_structure.py -v`

- [ ] Step 1: Verify baseline test passes pre-edit (`uv run pytest tests/unit/test_content_structure.py::test_principles_structure -v` or full suite)
- [ ] Step 2: Edit line 25 — replace `Complex reasoning (debug, arch): extended thinking when available` with `Complex reasoning (debug, arch): adaptive thinking (model-managed; effort parameter tunes depth)`
- [ ] Step 3: Edit line 28 (consequential — line 28 becomes stale once line 25 is reframed) — replace `Anti-pattern: Extended + Manual = redundant; choose one by complexity` with `Anti-pattern: Adaptive + Manual CoT = redundant; choose one by complexity`
- [ ] Step 4: Re-run content structure test — expect pass
- [ ] Step 5: Grep regression — `grep -rn "extended thinking" src/superclaude/core/` should now return 0 matches

---

### Task 2: Add `<aesthetics>` block to frontend-architect (T1-a)

**Files:** Modify: `src/superclaude/agents/frontend-architect.md` (insert after line 35, before line 38)
**Test:** `uv run pytest tests/unit/test_agent_structure.py -v`

Insert this block exactly (keep the preceding blank line on 36-37, prepend one more blank line to maintain visual separation). Note: `<aesthetics>` is a custom XML tag not in the agent template — `tests/unit/test_agent_structure.py` validates required tags only and does not reject extras (verified 2026-04-18), so this is safe.

```xml
  <aesthetics>
- Propose first: For ambiguous briefs, present 4 distinct visual directions (bg hex / accent hex / typeface / one-line rationale) before building. User picks one, then implement only that direction.
- Avoid AI-slop defaults: cream/off-white + serif + terracotta is the Opus 4.7 house style — correct for editorial/hospitality/portfolio briefs, wrong for dashboards, dev tools, fintech, healthcare, enterprise. Don't auto-apply it.
- Forbidden by default: Inter, Roboto, Arial, system fonts | purple gradients on white or dark backgrounds | cookie-cutter layouts lacking context-specific character. Choose distinctive fonts, cohesive palettes, purposeful motion.
- Respect explicit specs: When the user gives a concrete palette/typography/layout, follow it precisely — do not inject aesthetic opinions.
  </aesthetics>
```

- [ ] Step 1: Verify baseline test passes — `uv run pytest tests/unit/test_agent_structure.py -v`
- [ ] Step 2: Insert block above between `</outputs>` (line 35) and `<tool_guidance>` (line 38)
- [ ] Step 3: Verify file renders valid XML — `python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/superclaude/agents/frontend-architect.md')"` will fail (markdown wrapper) — instead run the structure test
- [ ] Step 4: Re-run agent structure test — expect pass
- [ ] Step 5: Grep check — `grep -n "aesthetics" src/superclaude/agents/frontend-architect.md` returns ≥2 lines

---

### Task 3: Add `<finding_policy>` to quality-engineer (T1-b-1)

**Files:** Modify: `src/superclaude/agents/quality-engineer.md` (insert after line 69, before line 72)
**Test:** `uv run pytest tests/unit/test_agent_structure.py::test_all_agents_have_required_tags -v` (or full suite)

Insert this block exactly:

```xml
  <finding_policy>
- Coverage over filter: Report every finding including low-severity and low-confidence ones. Do not pre-filter under guidance like "focus on real issues" or "don't nitpick" — downstream review will rank.
- Tag every finding: Include `severity: {critical|high|medium|low|nit}` and `confidence: {high|medium|low}` so a downstream pass can filter deterministically.
- Separate finding from ranking: Your job at this stage is recall; precision is a later stage's job.
  </finding_policy>
```

- [ ] Step 1: Confirm insertion point — `</outputs>` on line 69, `<tool_guidance>` on line 72 (blank lines 70-71)
- [ ] Step 2: Insert block between them (keep one blank line on each side)
- [ ] Step 3: Re-run agent structure test — expect pass
- [ ] Step 4: Grep check — `grep -n "finding_policy" src/superclaude/agents/quality-engineer.md` returns ≥2 lines

---

### Task 4: Add `<finding_policy>` to self-review (T1-b-2)

**Files:** Modify: `src/superclaude/agents/self-review.md` (insert after line 33, before line 36)
**Test:** same as Task 3

- [ ] Step 1: Confirm insertion point — `</outputs>` on line 33, `<tool_guidance>` on line 36
- [ ] Step 2: Insert the same `<finding_policy>` block from Task 3 between them
- [ ] Step 3: Re-run agent structure test — expect pass
- [ ] Step 4: Grep check — `grep -n "finding_policy" src/superclaude/agents/self-review.md` returns ≥2 lines

---

### Task 5: Add `<finding_policy>` to security-engineer (T1-b-3)

**Files:** Modify: `src/superclaude/agents/security-engineer.md` (insert after line 34, before line 37)
**Test:** same as Task 3

- [ ] Step 1: Confirm insertion point — `</outputs>` on line 34, `<tool_guidance>` on line 37
- [ ] Step 2: Insert the same `<finding_policy>` block from Task 3 between them
- [ ] Step 3: Re-run agent structure test — expect pass
- [ ] Step 4: Grep check — `grep -n "finding_policy" src/superclaude/agents/security-engineer.md` returns ≥2 lines

---

### Task 6: Create Part A verification checklist artifact

**Files:** Create: `docs/reports/OPUS_4_7_ALIGNMENT.md`
**Test:** None (pure documentation artifact; not installed to `~/.claude/`)

- [ ] Step 1: Create parent dir — `mkdir -p docs/reports/`
- [ ] Step 2: Write the checklist with exactly the Part A commands from the spec §5, plus a header identifying it as a living audit doc

Content template:

```markdown
# Opus 4.7 Alignment — Content Audit Checklist
# Last reviewed: 2026-04-18
# Source spec: docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md
# Re-run on every model upgrade. Each V# maps to a doc guidance ID (D1-D16).

## How to run

Walk through each V# below. Any row with an unexpected result = gap to address.

## V1 (D3,D6,D13) No CAPS enforcement language in content files
Command: `grep -rnE "CRITICAL:|MUST use|You MUST|NEVER " src/superclaude/{agents,commands,modes,core}/`
Expected: 0 matches

## V2 (D13) No pre-Opus-4.5 aggressive prompting patterns
Command: `grep -rnE "(If in doubt|by default) use" src/superclaude/agents/`
Expected: soft language only ("consider", "prefer")

## V3 (D5) Rules with broad scope have explicit application boundaries
Method: manual review of `src/superclaude/core/RULES.md` <core_rules>
Expected: each rule containing "all"/"every"/"always" has a scope qualifier

## V4 (D6) Subagent guidance reflects 4.7's lower-spawn default
Search: `src/superclaude/core/RULES.md` <sub_agent_decision>
Expected: note about explicit invocation for 3+ independent streams under Opus 4.7
Known state: **deferred to Tier 2 (T2-b)** — current rules are written for 4.6 over-spawning. Track as open gap until eval data supports the fix.

## V5 (D7) Frontend agent has AI-slop guard
Command: `grep -n "aesthetics\|frontend_aesthetics\|generic\|AI-slop" src/superclaude/agents/frontend-architect.md`
Expected: ≥1 match

## V6 (D9) Review agents use coverage-first finding language
Command: `grep -l "finding_policy\|report every\|coverage.*filter" src/superclaude/agents/quality-engineer.md src/superclaude/agents/self-review.md src/superclaude/agents/security-engineer.md`
Expected: all 3 files match

## V7 (D11) Thinking references are adaptive-thinking-aware
Command: `grep -rn "extended thinking\|budget_tokens" src/superclaude/core/`
Expected: 0 matches in prescribed guidance (historical/migration mentions outside `core/` are OK)

## V8 (D15) Anti-overengineering language present
Check: RULES.md `<anti_over_engineering>` + R06 + R18
Expected: all present

## V9 (D16) Investigation-before-answering rules present
Check: RULES.md R02 (Status Check), R17 (Serena-First)
Expected: both present

## V10 (D14) Parallel-tool-call guidance present
Check: FLAGS.md `--concurrency` + CC system prompt parallel instructions
Expected: both present
```

- [ ] Step 3: Write the file with the above content
- [ ] Step 4: Verify existence — `ls -la docs/reports/OPUS_4_7_ALIGNMENT.md`

---

### Task 7: Run full regression suite

**Files:** none (test execution)
**Test:** `uv run pytest tests/unit/ -v`

- [ ] Step 1: Run unit suite — record pre-change baseline if unknown
- [ ] Step 2: Verify test counts unchanged vs pre-edit baseline (no new failures, no skipped-that-was-passing)
- [ ] Step 3: If any failure: do NOT proceed. Diagnose root cause per R03/R15 (hypothesis → evidence), not "minor"
- [ ] Step 4: Per CLAUDE.md baseline: ~1,628 passing / 12 pre-existing failures / 6 collection errors is the expected state

---

### Task 8: Run Part A verification checklist

**Files:** none (verification)
**Test:** walk through `docs/reports/OPUS_4_7_ALIGNMENT.md`

- [ ] Step 1: Run V1 grep — expect 0 matches
- [ ] Step 2: Run V2 grep — expect soft language only
- [ ] Step 3: V3 manual review — confirm scope qualifiers in broad rules
- [ ] Step 4: V4 search — **expected gap here; T2-b deferred** — document as known deferred
- [ ] Step 5: Run V5 grep — expect ≥1 match (new aesthetics block)
- [ ] Step 6: Run V6 grep — expect 3 files match
- [ ] Step 7: Run V7 grep — expect 0 matches in core/ (PRINCIPLES.md line 25 updated)
- [ ] Step 8: V8/V9/V10 already confirmed in spec audit — reconfirm presence only
- [ ] Step 9: Record results in the checklist file (update `# Last reviewed:` date + add a "Run results 2026-04-18" section listing pass/gap status per V#)

---

### Task 9: Flip spec status to approved

**Files:** Modify: `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` (frontmatter)

- [ ] Step 1: Change `status: draft` to `status: approved`
- [ ] Step 2: Update `revised:` to today if materially changed (no material change expected)

---

### Task 10: Commit with conventional message

**Files:** git

- [ ] Step 1: `rtk git status` — confirm expected set: 5 modifications + 2 creations (checklist + plan)
- [ ] Step 2: Stage specific files by name — do NOT use `git add -A`
- [ ] Step 3: Commit with message: `docs(agents,core): align with Opus 4.7 prompting defaults (Tier 1)` + body citing spec path + Co-Authored-By footer
- [ ] Step 4: Verify commit clean — `rtk git log --oneline -3`

---

## Verification Summary (post-implementation)

Expected end-state evidence:

| Check | Command | Expected |
|-------|---------|----------|
| PRINCIPLES.md thinking updated | `grep -n "adaptive thinking" src/superclaude/core/PRINCIPLES.md` | line 25 match |
| Aesthetics block present | `grep -c "aesthetics" src/superclaude/agents/frontend-architect.md` | ≥2 |
| Finding policy in 3 review agents | `grep -l "finding_policy" src/superclaude/agents/{quality-engineer,self-review,security-engineer}.md` | 3 files |
| Checklist artifact exists | `ls docs/reports/OPUS_4_7_ALIGNMENT.md` | file exists |
| Unit tests pass | `uv run pytest tests/unit/ -q` | baseline count unchanged |
| Part A V1-V10 run | walk checklist | V4 = known deferred (T2-b); others pass |

---

## Scope Guard

- **In scope:** 5 file edits + 1 new checklist + 1 spec status flip
- **Out of scope:** T2-a (effort: xhigh on coding agents), T2-b (subagent guidance rewrite), T3 items, new unit tests for the new XML tags, model identity prompt, Part B behavioral evals
- **If unexpected work surfaces:** stop and consult user — do not expand scope within this plan execution (R06)

## Handoff

Ready for `/sc:implement --plan docs/plans/opus-4-7-alignment-tier-1-ajitta-2026-04-18.md`.
