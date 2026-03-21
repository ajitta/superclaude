# Usage Insights Improvement Design Spec

**Date:** 2026-03-21
**Author:** chosh1179
**Status:** Partially shipped — Improvements 2, 3, 5 deployed; 1, 4, 6 pending user action
**Data basis:** [Deep analysis](../analysis/2026-03-21-claude-code-insights-deep-analysis-chosh1179.md) of 640 sessions, 3.6M tokens
**Implementation:** [Plan](../plans/2026-03-21-usage-insights-improvements-chosh1179.md) | Commits: `74d24ba`, `f37ddaf`

---

## Delivery Summary

| # | Improvement | Status | Commit |
|---|-----------|--------|--------|
| 1 | Observer session phase-out | **USER ACTION** — stop launching observers, use /sc:save | — |
| 2 | Flag alias/fuzzy matching | **SHIPPED** | `74d24ba` |
| 3 | Workflow pipeline reconnection | **SHIPPED** (Options A+B+C) | `74d24ba` + pending |
| 4 | oasis_editor test conventions | **PENDING** — project-level CLAUDE.md change | — |
| 5 | Serena-first directive | **SHIPPED** | `74d24ba` |
| 6 | Unused command audit | **INFORMATIONAL** — no action needed | — |

**Deployed:** `superclaude v4.3.0+ajitta` via `uv tool install --force --editable .`
**E2E verified:** `--ultrathink`→`--seq`, `--loo`→`--loop` (alias); `--seqq`→"Did you mean: --seq?" (fuzzy)

---

## Problem Statement

Deep analysis of Claude Code usage data (2026-02-19 to 2026-03-20) reveals five systemic inefficiencies that the standard HTML report failed to surface:

1. **47.3% token waste** on observer sessions with near-zero ROI
2. ~~**14.5% flag error rate** due to missing aliases/fuzzy matching~~ → **FIXED** (12 aliases + fuzzy matching)
3. ~~**Workflow pipeline disconnection** — /sc:plan has 0 uses~~ → **FIXED** (analyze.md handoff added)
4. **Project-agnostic friction** — recommendations are diluted by aggregating all projects
5. ~~**Serena underutilization** in superclaude project (20.3%)~~ → **FIXED** (Serena-first directive)

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

## Improvement 2: Flag Alias & Fuzzy Matching System ✅ SHIPPED

### Before
- 39 invalid flag uses across 14 distinct typo/missing flags (14.5% error rate)
- context_loader.py silently ignored unrecognized flags
- Most common: `--ultrathink` (14), `--fix` (8), `--parellel` (4)

### What Was Delivered

**Alias Table** — `context_loader.py` lines 160-175:

```python
FLAG_ALIASES: dict[str, list[str]] = {
    # Conceptual aliases
    "ultrathink": ["seq"],
    "think": ["seq"],
    "think-hard": ["seq"],
    "parallel": ["delegate"],
    "agent": ["delegate"],
    # Typo corrections
    "parellel": ["delegate"],
    "conccurrency": ["concurrency"],
    "confidenc-check": ["validate"],
    "confidence-check": ["validate"],
    "iteration": ["iterations"],
    "loo": ["loop"],
    "sea": ["serena"],
}
```

> **Design delta:** `--ultrathink` maps to `["seq"]` only (not `["seq", "effort max"]` as originally proposed). `--fix` kept in `VALID_FLAGS` as a no-op rather than aliased to `--troubleshoot`. `--confidence-check` added (hyphenated variant missing from original spec).

**Fuzzy Matching** — `resolve_flags()` at line 189:
- `difflib.get_close_matches(flag, VALID_FLAGS, n=3, cutoff=0.6)` for unrecognized flags
- Suggests up to 3 closest matches (does not auto-correct — suggestion only)
- Notifications surfaced as HTML comments (invisible in rendering, auditable in source)

**Documentation** — FLAGS.md `<aliases>` section (commit `f37ddaf`):
- All 12 aliases documented with arrow notation
- Fuzzy match behavior documented

**Tests** — 16 unit tests in `TestResolveFlags` class:
- Alias resolution, fuzzy matching, edge cases (empty, unknown, already-valid)

### Expected Impact
- **14.5% → <2% flag error rate**
- Flags "just work" even with typos
- Usage data quality improves for future analysis

---

## Improvement 3: Workflow Pipeline Reconnection ✅ SHIPPED (all options)

### Before

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

### What Was Delivered

**Option A: Handoff** (commit `74d24ba`) — `/sc:plan` added to analyze.md `<handoff>` chain

**Option B: Analyze→Plan bridge** — analyze.md `<flow>` step 6 added:
```
6. Bridge: If findings are actionable (fixable issues, not just informational),
   suggest: "Would you like to create an implementation plan? → /sc:plan"
```

**Option C: `--plan` flag** — lightweight planning mode:
- `context_loader.py`: `--plan` directive in `_EXECUTION_DIRECTIVES` — generates 5-line plan (goal, approach, files, risks, verification) before implementation
- `FLAGS.md`: `--plan` documented in `<execution>` section
- `VALID_FLAGS`: `"plan"` added for fuzzy match support
- Usage: `/sc:implement --plan feature-name`

### Expected Impact
- /sc:plan usage from 0 → estimated 5-10/period
- `--plan` provides lightweight alternative for users who find /sc:plan too heavy
- Reduced "wrong_approach" friction from better pre-implementation planning

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

## Improvement 5: Serena-First Directive for superclaude Project ✅ SHIPPED

### Before
- superclaude: Serena adoption 20.3% of code-read operations
- oasis_editor: Serena adoption 40.2% (2x higher — proves Serena is effective)
- superclaude has 681 Read + 263 Grep = 944 file-read ops vs 240 Serena ops

### What Was Delivered

**Execution directive in `_EXECUTION_DIRECTIVES`** — context_loader.py lines 456-463:

```python
re.compile(r"--serena\b", re.IGNORECASE): (
    lambda _: "<sc-directive flag=\"--serena\">"
    "Serena-first code exploration: prefer symbolic tools over Read/Grep for code files. "
    "1) get_symbols_overview before Read, 2) find_symbol(include_body=True) for specific functions, "
    "3) search_for_pattern instead of Grep, 4) find_referencing_symbols instead of Grep for usage tracing. "
    "Reserve Read for non-code files or when full file context is needed."
    "</sc-directive>"
),
```

> **Design delta:** Implemented as an `_EXECUTION_DIRECTIVES` entry (emitted on every `--serena` prompt) rather than a standalone `SERENA_DIRECTIVE` constant. Same content, integrated into the existing directive pipeline. FLAGS.md `--serena` description also updated to mention "Serena-first exploration directive" (commit `f37ddaf`).

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

| # | Improvement | Impact | Effort | Priority | Status |
|---|-----------|--------|--------|----------|--------|
| 1 | Observer session phase-out | **CRITICAL** (47% token savings) | Low | **P0** | User action needed |
| 2 | Flag alias/fuzzy matching | HIGH (UX quality) | Medium | **P1** | **SHIPPED** `74d24ba` |
| 3 | Workflow pipeline reconnection | HIGH (process quality) | Medium | **P1** | **SHIPPED** (A+B+C) |
| 4 | oasis_editor test conventions | MEDIUM (project-specific) | Low | **P2** | Pending — different project |
| 5 | Serena-first directive | MEDIUM (token savings) | Low | **P2** | **SHIPPED** `74d24ba` |
| 6 | Unused command audit | LOW (informational) | Low | **P3** | Informational only |

---

## Open Questions — Resolution Status

1. **Observer sessions** — Are there any observer sessions that provide value not captured by claude-mem?
   → **UNRESOLVED.** User should stop launching observers and use `/sc:save` instead. Requires user process change, not code.

2. ~~**--ultrathink** — Should this become an official flag or alias?~~
   → **RESOLVED.** Implemented as alias: `--ultrathink` → `--seq`. Kept simple (no `--effort max` bundling). Documented in FLAGS.md `<aliases>` section.

3. **/sc:plan** — Is the 0-usage a discovery problem or deliberate preference?
   → **PARTIALLY RESOLVED.** Added `/sc:plan` to analyze.md handoff for discoverability. If usage remains 0 in next period, consider Options B/C from Improvement 3.

4. ~~**Flag notification mechanism** — Visible or silent?~~
   → **RESOLVED.** Notifications surfaced as HTML comments (invisible in rendered output, auditable in source). Alias corrections auto-applied; fuzzy matches suggestion-only.

5. **Token budget tracking** — Should SuperClaude add per-session tracking?
   → **UNRESOLVED.** Not in scope for this spec. Could be a future improvement.

---

## Success Metrics (next report period: 2026-03-21 → 2026-04-20)

| Metric | Baseline (Feb 19–Mar 20) | Target | Tracking |
|--------|---------|--------|----------|
| Observer session tokens | 1,717,941 (47.3%) | 0 (0%) | Requires user action |
| Invalid flag usage | 39 (14.5%) | < 5 (< 2%) | Alias system deployed |
| /sc:plan usage | 0 | 5-10 | Handoff added |
| oasis_editor buggy_code friction | 9 | 2-3 | Requires CLAUDE.md update |
| superclaude Serena adoption | 20.3% | 35-40% | Directive deployed |
| Overall friction events | 72 | < 40 | Partial — 3 of 6 improvements shipped |
