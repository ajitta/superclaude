# Skills Improvement (Tier 1 + 2) Implementation Plan

**Goal:** Guide-based skill improvements + framework extension — gotchas standardization, description optimization, safety hooks, core trimming, progressive disclosure
**Spec:** `docs/specs/2026-03-29-skills-improvement-design-ajitta.md` (Rev 3)
**Architecture:** `<gotchas>` tag in XML `<component>`, skill frontmatter hooks, references/ file split
**Status:** COMPLETE — all 8 tasks done, 1,673 tests pass, 0 regressions

---

## Phase 1: Skills (Tier 1 — Guide Direct Recommendation) ★ COMPLETE

### Task 1: Skill `<gotchas>` Standardization + New ✅

**Files:** 5 skills modified
- [x] ship: `<safety>` → `<gotchas>` rename (4 entries: force-push, secrets, staged-scan, main-direct)
- [x] finishing-a-dev-branch: `<constraints>` kept + `<gotchas>` added (2 entries: stash-check, base-branch)
- [x] verbalized-sampling: `<critical_rules>` → `<gotchas>` (6 entries: pre-assign, role-label, k-limit, word-diversity, synthesis-verdict, prob-word)
- [x] confidence-check: new `<gotchas>` (3 entries: websearch-dup, score-rounding, evidence-gap)
- [x] simplicity-coach: new `<gotchas>` (2 entries: timeout, osl-skip)

### Task 2: Skill Description Trigger Optimization ✅

- [x] ship: added 'ship', 'deploy', 'push', 'commit and push', 'create PR' triggers
- [x] confidence-check: added 'confidence', 'before implementing', 'validate first' triggers
- [x] finishing-a-dev-branch: added 'branch done', 'merge back', 'finish branch', 'work complete' triggers
- [x] ship: $ARGUMENTS pattern added to body

### Task 3: Safety Hooks for Destructive Skills ✅

- [x] ship: PreToolUse Bash hook — blocks `git push --force|git push -f` (exit 2)
- [x] finishing-a-dev-branch: PreToolUse Bash hook — blocks `git branch -D|git push --force` (exit 2)

---

## Phase 2: Framework Extension (Tier 2) ★ COMPLETE

### Task 4: RULES.md Trimming ✅

**File:** `src/superclaude/core/RULES.md` (169→124 lines, -27%)
- [x] Removed [R07] Trust, [R08] Language, [R11] Honesty (duplicate Claude defaults)
- [x] Merged `<conflict_resolution>` + `<agent_orchestration>` into compact `<priority_system>`
- [x] Removed `<decision_trees>` and `<priority_actions>` (redundant with core_rules)
- [x] Preserved [R13], [R14], [R16] intact
- [x] All examples tables preserved
- [x] Archive comment with all removed items on line 123

### Task 5: Skill Progressive Disclosure ✅

**Files:** 3 skills trimmed + 3 reference files created
- [x] ship: moved branch_validation, commit_format, pr_template, exclusions → `references/conventions.md`
- [x] confidence-check: moved checks table, mcp_integration, roi, hooks note → `references/checks-detail.md`
- [x] verbalized-sampling: moved parameters, diversity_dial, prompt_templates, output_format → `references/paper-methodology.md`
- [x] Each SKILL.md now has `<references note="Load on demand">` tag pointing to files

### Task 6: Agent `<gotchas>` + Description Triggers ✅

**Files:** 4 agents modified
- [x] security-engineer: gotchas (owasp-default, false-positive) + 6 trigger keywords (encrypt, jwt, hash, token, csrf, xss)
- [x] frontend-architect: gotchas (generic-wcag, framework-default)
- [x] backend-architect: gotchas (pattern-over-context, premature-scale)
- [x] performance-engineer: 4 trigger keywords (N+1, cache, lazy-load, query-optimization)

### Task 7: research.md Content Externalization ✅

**File:** `src/superclaude/commands/research.md` (140→70 lines, -50%)
- [x] Removed depth_flow, depth_levels, mcp_routing, parallel_strategy, patterns, token_efficiency
- [x] Replaced with compact references to modes/RESEARCH_CONFIG.md
- [x] Added gotchas (single-source, source-quality)
- [x] Examples trimmed from 4 verbose to 2 compact

---

## Phase 3: Authoring Rules Update ★ COMPLETE

### Task 8: Authoring Rules `<gotchas>` Guidance ✅

- [x] agent-authoring.md: `<gotchas>` added to template (placement: after handoff, before bounds). "Recommended"
- [x] command-authoring.md: `<gotchas>` added to template (placement: after flow, before examples). "Recommended"
- [x] skill-authoring.md: `<references>` + `<gotchas>` added. Quality criteria included (project-specific only)

---

## Verification ✅

| Metric | Baseline | Result | Status |
|---|---|---|---|
| Tests | 1,673 pass | **1,673 pass** | NO REGRESSION |
| `<gotchas>` in skills | 0/5 | **5/5** | COMPLETE |
| `<gotchas>` in agents | 0/3 | **3/3** | COMPLETE |
| Safety hooks | 0/2 | **2/2** | COMPLETE |
| RULES.md lines | 169 | **124** | COMPLETE |
| research.md lines | 140 | **70** | COMPLETE |
| Korean in modified files | N/A | **0** | CLEAN |

---

## Commit Strategy

- Phase 1 commit: `feat: add <gotchas> standardization and safety hooks to skills`
- Phase 2 commit: `refactor: trim core rules, progressive disclosure, agent improvements`
- Phase 3 commit: `docs: update authoring rules with <gotchas> and <references> guidance`
