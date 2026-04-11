---
status: implemented
revised: 2026-04-11
source: docs/specs/superclaude-weakness-improvement-discovery-ajitta-2026-04-11.md
methodology: sequential-thinking (4 steps with self-evaluation loop)
---

# Design Spec: SuperClaude Weakness Fixes

## Scope

5 weaknesses from the discovery spec. 3 implemented now (W3, W4, W5), 1 partially (W2 gotchas only), 1 designed but deferred to plan phase (W1 agent gotchas).

| Weakness | Action | Phase |
|----------|--------|-------|
| W3: False Reporting Enumeration | Extend R15 + add example | **Now** |
| W4: Skills Budget Mechanics | Add budget section to skill-authoring.md | **Now** |
| W5: Numeric Criteria | Add numbers to R06, R12 | **Now** |
| W2: Context Isolation (partial) | Populate gotchas/general.md | **Now** |
| W1: Agent Rule Reinforcement | Phase 1 implemented (5 agents), Phase 2 deferred | **Partial** |

## Design: W3 — R15 False Reporting Enumeration

### Target File
`src/superclaude/core/RULES.md` line 41

### Current
```
[R15] Verification 🔴: before claiming done, run full test suite fresh (not cached); compare pass count to baseline; cite evidence ("42/42 pass, baseline 40")
```

### Proposed
```
[R15] Verification 🔴: before claiming done, run full test suite fresh (not cached); compare pass count to baseline; cite evidence ("42/42 pass, baseline 40"); prohibited: claiming passage without running tests, summarizing failures as 'minor issues', reporting completion without command output, predicting results instead of observing. If unable to verify, state "verification not possible: [reason]"
```

### Rationale
Anthropic's CC source enumerates all evasion forms (prose, summary, structured output). Current R15 says "cite evidence" but doesn't enumerate HOW agents evade verification. Adding prohibited patterns closes loopholes.

### Convention Compliance
Matches R16 (Safe Read) convention: single long line with multiple semicolon-separated clauses.

### Examples Table Addition
Add new row to the examples table in `<examples>` section:

| Agent says "all tests pass" without output | Runs tests first OR states "verification not possible: no test suite configured" | Verification 🔴 |

---

## Design: W4 — Skills Budget Mechanics

### Target File
`.claude/rules/skill-authoring.md` — insert after the `description + when-to-use 분리` section (after the Good/Bad example block ending around line 108)

### Proposed Content

```markdown
**Description Budget Constraints (CC Runtime)**:
- **Total budget**: ~15,000 characters for all skill/command descriptions combined (`SLASH_COMMAND_TOOL_CHAR_BUDGET`)
- **Per-skill truncation**: descriptions are truncated to ~250 chars in the listing shown to Claude
- **Priority**: Anthropic bundled skills retain full descriptions; custom skills are trimmed first when budget exceeded
- **Implication**: Keep `description` under 250 chars. Put trigger keywords in first 100 chars. Use `when-to-use` for additional trigger context (not budget-constrained in the same way)
- **Current budget usage**: 5 skills, ~376 chars total — well within 15K. Monitor if adding more skills
```

### Rationale
skill-authoring.md documents `max 1024자` for description but doesn't explain that CC truncates to 250 in the listing or that there's a total budget. Authors creating verbose descriptions won't understand why their skills don't trigger.

### Numbers Source
- 15K: `SLASH_COMMAND_TOOL_CHAR_BUDGET` (web research, multiple sources)
- 250: CC changelog 2.1.86+ and official docs (code.claude.com/docs/en/skills)
- 376: Measured — sum of current 5 skill descriptions

---

## Design: W5 — Numeric Criteria for Vague Rules

### Target File
`src/superclaude/core/RULES.md` lines 35 and 38

### R06 — Current
```
[R06] Scope 🟡: build only what's asked, YAGNI
```

### R06 — Proposed
```
[R06] Scope 🟡: build only what's asked — 0 unsolicited files, 0 adjacent refactors, YAGNI
```

### R12 — Current
```
[R12] Clarification 🟡: ambiguous requests (multiple valid interpretations) → ask before implementing
```

### R12 — Proposed
```
[R12] Clarification 🟡: ambiguous requests (2+ valid interpretations) → ask before implementing
```

### Rationale
Anthropic's internal prompts use measurable numeric thresholds. "0 unsolicited files" gives a binary check. "2+ valid interpretations" specifies when ambiguity triggers a question. Both add precision at zero cost.

---

## Design: W2 (partial) — Populate gotchas/general.md

### Target File
`.claude/rules/gotchas/general.md` (currently empty — 4 comment lines only)

### Proposed Content (append after existing comments)

```markdown
- context-leak: Do not Read sub-agent output files (*.output) — wait for returned summary. Reading transcripts pollutes main context with tool noise
- compaction-drift: Rules from session start may degrade after ~50 turns of auto-compaction. For long sessions, re-read critical rules if behavior drifts
- rule-tag-vs-concept: When counting rule occurrences, grep for exact tag (e.g., \bR18\b), not concept name. "Verification" appears broadly but R15 appears once
```

### Rationale
gotchas/general.md exists (created by /sc:init) but is empty. CC loads these natively. These 3 patterns were discovered during this analysis session and are project-specific (not general advice). Limit: 50 lines per file per CLAUDE.md.

---

## Design: W1 — Agent Rule Reinforcement (Phase 1 IMPLEMENTED, Phase 2 DEFERRED)

### Problem
18/23 agents lack `<gotchas>` sections. Critical rules (R02, R13, R15, R18) have zero cross-file reinforcement.

### Template Design

Agents are categorized by role, each getting the most relevant critical rule:

| Agent Category | Members | Gotcha Rule | Template Line |
|---------------|---------|-------------|---------------|
| **Implementers** | refactoring-expert, python-expert, devops-architect, performance-engineer | R02 Status Check | `- status-check: Before starting work, run 2-3 targeted searches to verify work isn't already complete [R02]` |
| **Reviewers** | self-review, quality-engineer | R15 Verification | `- verification-evidence: Cite actual test output, not claims. "42/42 pass" requires running the tests [R15]` |
| **Proposers** | system-architect, simplicity-guide (already has gotchas), requirements-analyst | R18 Necessity Test | `- necessity-gate: Before proposing changes, answer "Is the system broken without this?" [R18]` |
| **Planners** | project-manager, root-cause-analyst, deep-researcher | R13 Intent Verification | `- intent-confirm: Restate user intent before non-trivial work, especially when task direction changes mid-conversation [R13]` |
| **Executors** | git-workflow, repo-index, project-initializer | R02 Status Check | `- status-check: Verify current state before executing — check branch, working tree, existing output [R02]` |
| **Educators** | learning-guide, socratic-mentor, technical-writer | (none — low risk of rule drift) | — |
| **Analysts** | business-panel-experts, insight-analyst (already has gotchas) | R13 Intent | `- intent-confirm: Confirm which analysis dimension the user wants before deep-diving [R13]` |

### Placement Rule
Insert gotcha lines BEFORE `<bounds>` tag, after `<handoff>` (matching existing convention in the 5 agents that already have gotchas).

### Token Cost
~3 lines x 18 agents = 54 lines, ~1.5-2K tokens total. Per-session cost: ~3 lines for whichever agent is delegated to.

### Phase 1 — IMPLEMENTED (2026-04-11)
5 highest-judgment agents: self-review (R15+R06), system-architect (R18+R06), refactoring-expert (R02+R06), project-manager (R13+R04), root-cause-analyst (R13+R03). 2 gotchas per agent, placed after `<handoff>` before `<bounds>`. Total agent gotchas count: 10 (up from 5). Measure before expanding to all 18.

### Why Deferred
1. The reviewer noted "content framework improvements, not measured problems" — no evidence of actual rule drift in production
2. 18 agent edits require individual review (each agent's gotchas should be contextually appropriate)
3. Hooks may be a better enforcement mechanism than content repetition

---

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| 1 | R15 extension includes prohibited patterns + fallback text | Read RULES.md line 41 |
| 2 | skill-authoring.md has budget section with 15K/250 numbers | Grep "Budget Constraints" in skill-authoring.md |
| 3 | R06 has "0 unsolicited" numeric anchor | Grep R06 in RULES.md |
| 4 | R12 has "2+" numeric anchor | Grep R12 in RULES.md |
| 5 | gotchas/general.md has 3+ entries | wc -l on file |
| 6 | All tests pass | `uv run pytest tests/unit/ -v` |
| 7 | No new files created | git status shows only modified files |

## Constraints

- **No new rules**: Don't add R20 (context isolation rule). The gotchas/general.md entry covers this lighter-weight.
- **No skill frontmatter changes**: Don't add `context: fork` yet — reviewer showed current skills don't benefit.
- **No agent edits in this phase**: W1 deferred to plan. Template designed but not applied.
- **Numbers must be sourced**: 15K and 250 from web research, not from the video's unverified 1% claim.
