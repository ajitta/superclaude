# Usage Insights Improvement Design Spec

**Date:** 2026-03-21
**Author:** chosh1179
**Status:** Draft — pending user review
**Data basis:** [Deep analysis](../analysis/2026-03-21-claude-code-insights-deep-analysis-chosh1179.md) of 640 sessions, 3.6M tokens

---

## Problem Statement

Deep analysis of Claude Code usage data (2026-02-19 to 2026-03-20) reveals five systemic inefficiencies that the standard HTML report failed to surface:

1. **47.3% token waste** on observer sessions with near-zero ROI
2. **14.5% flag error rate** due to missing aliases/fuzzy matching
3. **Workflow pipeline disconnection** — /sc:plan has 0 uses despite being a defined workflow gate
4. **Project-agnostic friction** — recommendations are diluted by aggregating all projects
5. **Serena underutilization** in superclaude project (20.3% vs 40.2% in oasis_editor)

---

## Improvement 1: Observer Session Phase-Out

### Current State
- 317 observer sessions consuming 1,717,941 tokens (47.3% of total)
- 0 commits, 40 total tool calls (0.13/session), 37.7% success rate
- 249 sessions use "hello memory agent" prompt
- Observer pattern predates claude-mem's built-in memory system

### Design

**Phase 1: Deprecation (immediate)**
- Remove observer session startup from any automated workflow
- Add deprecation notice to observer prompt templates if any exist
- Document `/sc:save` as the replacement for session-end context capture

**Phase 2: Replacement**
- `/sc:save` already exists — ensure it captures what observers were meant to capture:
  - Architectural decisions made during the session
  - Friction events and corrections
  - Key file paths and patterns discovered
- Add auto-save hook suggestion: PostToolUse on final message → prompt /sc:save reminder

**Phase 3: Validation**
- Track token consumption in next report period
- Target: observer tokens → 0, total tokens reduced by ~40%

### Expected Impact
- **Token savings:** ~1.7M tokens/period (47.3% reduction)
- **Session count reduction:** ~300 fewer sessions to manage
- **Friction reduction:** 9 wrong_approach events eliminated (41% of category)

---

## Improvement 2: Flag Alias & Fuzzy Matching System

### Current State
- 39 invalid flag uses across 14 distinct typo/missing flags (14.5% error rate)
- context_loader.py silently ignores unrecognized flags
- Most common: `--ultrathink` (14), `--fix` (8), `--parellel` (4)

### Design

**Alias Table** — Add to `context_loader.py`:

```python
FLAG_ALIASES = {
    # Conceptual aliases
    "ultrathink": ["seq", "effort max"],
    "think": ["seq"],
    "think-hard": ["seq", "effort max"],
    "fix": ["troubleshoot"],  # or no-op with message
    "parallel": ["delegate"],
    "agent": ["delegate"],

    # Typo corrections
    "parellel": ["delegate"],
    "conccurrency": ["concurrency"],
    "confidenc-check": ["validate"],
    "iteration": ["iterations"],
    "loo": ["loop"],
    "sea": ["serena"],
}
```

**Fuzzy Matching** — For flags not in alias table:
1. Compute Levenshtein distance to all valid flags
2. If distance ≤ 2 and unique match → auto-correct with notification
3. If ambiguous → suggest top 3 matches in output

**User Notification:**
```
⚠ --parellel → auto-corrected to --delegate (typo)
⚠ --ultrathink → expanded to --seq --effort max (alias)
⚠ --fix is not a recognized flag. Did you mean: --seq, --introspect, or /sc:troubleshoot?
```

### Implementation Scope
- `context_loader.py`: Add `FLAG_ALIASES` dict + `resolve_flag()` function
- `context_loader.py`: Add fuzzy match fallback using `difflib.get_close_matches()`
- Notification via `<sc-directive>` output

### Expected Impact
- **14.5% → <2% flag error rate**
- Better user experience — flags "just work" even with typos
- Usage data quality improves for future analysis

---

## Improvement 3: Workflow Pipeline Reconnection

### Current State

Defined pipeline in RULES.md:
```
/sc:brainstorm → /sc:plan → /sc:implement → /sc:test → done
```

Actual usage:
```
/sc:analyze (80) → ad-hoc implementation
/sc:brainstorm (13) → direct implementation (no /sc:plan)
/sc:plan: 0 uses
/sc:test: 0 uses
/sc:review: 0 uses
```

### Root Cause Analysis

1. **Discovery problem** — Users don't know /sc:plan exists or when to use it
2. **Friction** — /sc:plan may require too much upfront structure for the user's iterative style
3. **Workflow gate enforcement is advisory** — nothing prevents skipping /sc:plan

### Design Options

**Option A: Auto-suggest (low friction)**
- After /sc:brainstorm completes, output includes: `"Next: /sc:plan to create implementation plan, or proceed directly"`
- After /sc:analyze with findings, suggest: `"Consider /sc:plan before implementing"`
- No enforcement — just awareness

**Option B: Analyze→Plan bridge**
- When /sc:analyze produces actionable findings (not just information), auto-prompt:
  `"Would you like to create an implementation plan? [y/n]"`
- If yes, transition to /sc:plan with analyze findings as input
- Reduces friction of starting /sc:plan from scratch

**Option C: Lightweight plan mode**
- Create /sc:plan-lite or `--plan` flag for /sc:implement
- Generates a 5-line plan (not a full document) before implementing
- Captures the planning value without the overhead

### Recommendation: Option B + C combined
- B connects the most-used command (/sc:analyze) to the missing workflow step
- C reduces the barrier to planning for users who find /sc:plan too heavy

### Expected Impact
- /sc:plan usage from 0 → estimated 5-10/period
- Reduced "wrong_approach" friction from better pre-implementation planning
- More deliberate implementation sessions

---

## Improvement 4: Project-Specific Test Conventions (oasis_editor)

### Current State
- 9/17 buggy_code friction events are in oasis_editor
- Root cause: Vitest vi.mock hoisting, mock isolation, test setup patterns
- No project-specific testing guidance in oasis_editor's CLAUDE.md

### Design

**Add to oasis_editor project's CLAUDE.md:**

```markdown
## Testing Conventions (Vitest)

- vi.mock() calls MUST be at the top of the file (hoisting requirement)
- Use vi.clearAllMocks() in beforeEach(), NOT afterEach()
- Each test file must be self-contained — no shared mock state across files
- Before writing new tests: read 2-3 existing test files for patterns
- When using vi.mock for ES modules, use factory function form:
  `vi.mock('./module', () => ({ default: vi.fn() }))`
```

**Add to /sc:test command flow:**
```
Step 0 (new): Read 2-3 existing test files in the target directory
              to learn project-specific mock patterns and conventions
```

**Optionally:** Context7 query for Vitest mock hoisting docs when writing tests in oasis_editor

### Scope
- This is a PROJECT-LEVEL fix (oasis_editor CLAUDE.md), not a SuperClaude framework change
- /sc:test flow enhancement benefits all projects

### Expected Impact
- buggy_code friction in oasis_editor: 9 → target 2-3 (66-77% reduction)
- Test rewrite iterations: 2-3 passes → 1 pass

---

## Improvement 5: Serena-First Directive for superclaude Project

### Current State
- superclaude: Serena adoption 20.3% of code-read operations
- oasis_editor: Serena adoption 40.2% (2x higher — proves Serena is effective)
- superclaude has 681 Read + 263 Grep = 944 file-read ops vs 240 Serena ops

### Design

**Add behavioral directive to context_loader.py** when `--serena` flag is active:

```python
SERENA_DIRECTIVE = """
<sc-directive name="serena-first">
When exploring code in a Serena-activated project:
1. Use get_symbols_overview before Read for code files
2. Use find_symbol with include_body=True for specific functions
3. Use search_for_pattern instead of Grep for code search
4. Reserve Read for non-code files, config, or when full file context needed
5. Use find_referencing_symbols instead of Grep for usage tracing
</sc-directive>
"""
```

**Trigger:** Emit when `--serena` flag is present AND Serena project is activated

### Expected Impact
- superclaude Serena adoption: 20.3% → target 35-40%
- Read/Grep reduction: estimated 30-40% fewer calls
- Token savings: ~200K tokens/period (5-6% of total)

---

## Improvement 6: Unused Command Audit

### Current State
- 13/32 commands have 0 usage in the data period
- These commands consume context (loaded into system prompt when invoked) but provide no proven value

### Unused Commands

| Command | Possible Reason for Non-Use |
|---------|---------------------------|
| /sc:plan | Workflow gap (see Improvement 3) |
| /sc:test | Users run tests directly via `make test` |
| /sc:review | Self-review happens organically |
| /sc:design | Folded into /sc:brainstorm |
| /sc:workflow | Too specialized |
| /sc:build | Users use `make` directly |
| /sc:cleanup | Not needed for current projects |
| /sc:estimate | Not part of individual dev workflow |
| /sc:spec-panel | Too specialized |
| /sc:business-panel | Not relevant to current projects |
| /sc:recommend | Meta-command, rarely needed |
| /sc:select-tool | Internal use only |
| /sc:pm | Orchestration handled ad-hoc |

### Recommendation

**Do not remove commands.** Instead:
1. Audit each 0-use command — is it discoverable? Is the name intuitive?
2. Consider consolidating: /sc:design → alias for /sc:brainstorm --depth deep
3. Add command suggestions in /sc:help output based on user's current activity
4. Track command usage in next period to see if awareness helps

### Priority: LOW
- This is informational, not urgent
- Commands that aren't used don't cost tokens unless invoked

---

## Implementation Priority

| # | Improvement | Impact | Effort | Priority |
|---|-----------|--------|--------|----------|
| 1 | Observer session phase-out | **CRITICAL** (47% token savings) | Low | **P0** |
| 2 | Flag alias/fuzzy matching | HIGH (UX quality) | Medium | **P1** |
| 3 | Workflow pipeline reconnection | HIGH (process quality) | Medium | **P1** |
| 4 | oasis_editor test conventions | MEDIUM (project-specific) | Low | **P2** |
| 5 | Serena-first directive | MEDIUM (token savings) | Low | **P2** |
| 6 | Unused command audit | LOW (informational) | Low | **P3** |

---

## Open Questions

1. **Observer sessions** — Are there any observer sessions that provide value not captured by claude-mem? If so, what specific observations are they recording?
2. **--ultrathink** — Should this become an official flag (alias for `--seq --effort max`), or should users be guided to the existing flags?
3. **/sc:plan** — Is the 0-usage a discovery problem, or does the user deliberately prefer ad-hoc over structured planning?
4. **Flag notification mechanism** — Should typo corrections be visible to the user (stderr/directive), or silently applied?
5. **Token budget tracking** — Should SuperClaude add per-session token tracking to enable cost-aware decisions?

---

## Success Metrics (next report period)

| Metric | Current | Target |
|--------|---------|--------|
| Observer session tokens | 1,717,941 (47.3%) | 0 (0%) |
| Invalid flag usage | 39 (14.5%) | < 5 (< 2%) |
| /sc:plan usage | 0 | 5-10 |
| oasis_editor buggy_code friction | 9 | 2-3 |
| superclaude Serena adoption | 20.3% | 35-40% |
| Overall friction events | 72 | < 40 |
