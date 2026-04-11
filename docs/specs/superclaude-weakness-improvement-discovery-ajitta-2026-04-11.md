---
status: reviewed
revised: 2026-04-11
methodology: sequential-thinking (6 steps) + verbalized-sampling (4 perspectives) + codebase-audit (64 tool calls) + web-research (10 queries) + self-review (37 tool calls, 4 critical corrections applied)
source_document: docs/research/claude-code-7-techniques-analysis-ajitta-2026-04-11.md
---

# SuperClaude Weakness & Improvement Analysis

Based on mapping Anthropic's 7 internal prompting techniques against SuperClaude's current implementation.

## Executive Summary

SuperClaude scores **STRONG** on 4/7 techniques (T1, T2, T4, T6), **PARTIAL** on 2 (T5, T7), and **WEAK** on 1 (T3). The framework's architecture is sound — the gaps are content-level, not structural. Three weaknesses have high practical impact and are addressable without architectural changes.

| Technique | Current Score | Impact of Gap | Fix Complexity |
|-----------|:------------:|:-------------:|:--------------:|
| T1: DO/DON'T + Numeric | 8/10 | Low | S |
| T2: Verification Enforcement | 8/10 | Medium | S |
| **T3: Triple Repetition** | **3/10** | **High** | **M** |
| T4: Turn Strategy | 8/10 | Low | — |
| T5: CoT Stripping | N/A | — | — |
| T6: Skills Budget | 7/10 | Medium | S |
| **T7: Context Pollution** | **4/10** | **High** | **M** |

## Weakness 1: No Rule Reinforcement Strategy (T3) — CRITICAL

### Current State (3/10)

Critical rules are stated ONCE in `core/RULES.md`, imported via `CLAUDE_SC.md` @import chain at conversation start. Individual agents/commands do NOT repeat critical rules.

**Audit findings (grep-verified `\bRxx\b` tag counts + phrase counts):**
- R02 Status Check: `\bR02\b` tag = 1x. "Status Check" phrase = 4x, all within RULES.md. Zero appearances in agents or commands
- R13 Intent Verification: `\bR13\b` tag = 2x, both within RULES.md (definition + example). Zero cross-file reinforcement — **most underreinforced critical rule**
- R15 Verification: `\bR15\b` tag = 1x in RULES.md. Verification concept echoes in self-review agent but without R15 reference. Weaker than initially assessed
- R18 Necessity Test: `\bR18\b` tag = 4x across 3 files (RULES.md 2x, design.md 1x, insight.md 1x). **Best-reinforced** of the critical rules at content level, but zero agent-level gotchas

### What Breaks

When conversations exceed ~50 turns, Claude Code's auto-compaction summarizes earlier context. Rules loaded at session start get compressed into summaries. Without reinforcement at later positions:
- R13 Intent Verification is the first casualty (2x, single file) — agents skip confirmation on ambiguous requests
- R02 Status Check weakens (tag 1x, phrase 4x, single file) — agents start implementing before checking existing state
- R18 Necessity Test is better reinforced (4x, 3 files) but still lacks agent-level gotchas — agents may propose unsolicited improvements in long sessions

### Impact Evidence

The Anthropic "Effective context engineering for AI agents" post describes n-squared pairwise relationships creating a "performance gradient" as context grows — consistent with our observation that rules loaded at session start degrade over long conversations. The video document demonstrates CC uses positional repetition (beginning, middle, end) to counteract this — SuperClaude has no equivalent mechanism.

### Proposed Improvement

**Strategy: Layered positional reinforcement using SuperClaude's existing architecture**

Position 1 — **Core** (session start): Already exists in `core/RULES.md`. No change needed.

Position 2 — **Agent/Command level** (mid-conversation): Add the 3 most relevant critical rules to each agent's `<gotchas>` section. This is natural — gotchas already exist as a pattern. Example:

```xml
<!-- In agents that frequently violate R18 (architects, engineers): -->
<gotchas>
- necessity-test: Before proposing unsolicited changes, answer "Is the system broken without this?" — "safer/better" alone is insufficient [R18]
- existing-gotchas: ...
</gotchas>
```

Position 3 — **Hook-based reminder** (late conversation): The `context_loader.py` UserPromptSubmit hook already injects context. Could extend to inject a 2-line critical rule reminder when conversation length exceeds a threshold. This is a code change (not just content).

**Recommended scope**: Position 2 only (content-only change, no code). Position 3 is valuable but requires `context_loader.py` modification — defer to a future iteration. Note: the existing `context_loader.py` UserPromptSubmit hook already injects context per-turn and could serve as a Position 3 vehicle if needed later.

**Token cost estimate**: ~3 lines x 23 agents = 69 lines, ~2-3K tokens total. Since agents load individually (not all at once), actual per-session impact is ~3 lines per delegated agent. Consider starting with 3-5 highest-violation agents rather than all 23.

**Complexity**: M (audit all 23 agents + select top 3 rules per agent)

---

## Weakness 2: Context Isolation Gap (T7) — HIGH

### Current State (4/10)

`context: fork` is documented in skill-authoring.md but **NOT USED in any of the 5 live skills**. No explicit rules exist about work boundary enforcement or sub-agent transcript isolation.

**Audit findings:**
- Checked: confidence-check, finishing-a-development-branch, ship, simplicity-coach, verbalized-sampling
- None use `context: fork` in SKILL.md frontmatter
- `.claude/rules/gotchas/general.md` exists but is empty (only header comment)
- No "work boundary" enforcement patterns in commands/

### What Breaks

Without context isolation enforcement:
1. Long `/sc:implement` sessions accumulate sub-agent tool noise in main context
2. `/sc:analyze` with `--delegate` brings back full analysis text rather than summaries
3. Context budget depletes faster than necessary in multi-agent workflows

### Impact Evidence

The fork-not-just-efficiency memory (existing auto-memory) already captures this insight: "Fork purpose includes intentional info asymmetry, not just efficiency." But the insight hasn't been operationalized in the framework.

### Proposed Improvement

**A. Add context isolation guidance to RULES.md** (new rule or amendment):

```markdown
[R20] Context Isolation 🟡: when delegating to sub-agents (--delegate, Agent tool), 
do NOT read sub-agent output files or transcripts during execution. 
Wait for the summary return. Reading mid-execution defeats isolation purpose.
```

**B. Add `context: fork` to skills that benefit from isolation:**
- Evaluate per-skill: confidence-check is a fast 3-step inline check where fork overhead may hurt latency. Verbalized-sampling's full output IS the deliverable, so fork summary would lose value.
- Better candidates: skills that do heavy exploration with disposable intermediate work (e.g., a future research or audit skill)
- Start with 1 skill where fork clearly helps before rolling out broadly

**C. Populate `gotchas/general.md`** with first 3-5 patterns:

```markdown
- context-leak: Do not Read sub-agent output files (*.output) — use returned summary only
- transcript-noise: Long agent transcripts pollute main context — prefer fork over inline for >5-turn tasks
- compaction-drift: Rules from session start degrade after ~50 turns — critical rules need mid-session reinforcement
```

**Complexity**: M (skill frontmatter changes + new rule + gotchas content)

---

## Weakness 3: Missing False Reporting Enumeration (T2 refinement) — MEDIUM

### Current State (8/10 — strong but incomplete)

R15 requires evidence ("42/42 pass, baseline 40") but doesn't enumerate specific forms of false reporting. The CC source explicitly lists: prose fabrication, summary fabrication, structured output fabrication, hidden failures, premature completion claims.

### What Breaks

Without enumeration, sophisticated evasion paths remain open:
- Agent says "all tests pass" without running them (prose fabrication)
- Agent summarizes "minor issues resolved" without specifying which (summary hiding)
- Agent claims "implemented as designed" without verification command output

### Proposed Improvement

Add enumeration to R15 in RULES.md:

```markdown
[R15] Verification 🔴: before claiming done, run full test suite fresh (not cached); 
compare pass count to baseline; cite evidence ("42/42 pass, baseline 40"). 
Prohibited verification patterns:
- Claim test passage without running tests (prose fabrication)
- Summarize failures as "minor issues" without specifics (summary hiding)  
- Report completion without verification command output (premature completion)
- Predict results instead of observing them (speculation)
If verification is impossible, state "verification not possible: [reason]" explicitly.
```

**Complexity**: S (single file edit, ~5 lines added to RULES.md)

---

## Weakness 4: Skills Budget Mechanics Missing (T6 refinement) — MEDIUM

### Current State (7/10)

`skill-authoring.md` documents `description` max 1024 chars and the description/when-to-use separation pattern (excellent). But it lacks the actual CC budget mechanics that explain WHY brevity matters.

### What Breaks

Authors create verbose descriptions (1024 chars allowed) without understanding that:
- CC truncates to ~250 chars in the skill listing shown to Claude
- Total budget for all skill/command descriptions is `SLASH_COMMAND_TOOL_CHAR_BUDGET = 15,000 chars`
- When budget is exceeded, custom skill descriptions are trimmed BEFORE Anthropic's bundled ones
- Trimmed descriptions lose trigger keywords, making skills unreachable

### Proposed Improvement

Add a "Budget Awareness" section to `skill-authoring.md`:

```markdown
### Description Budget Constraints

Claude Code allocates a fixed character budget for all skill/command descriptions:
- **Total budget**: ~15,000 characters (`SLASH_COMMAND_TOOL_CHAR_BUDGET`)
- **Per-skill truncation**: descriptions are truncated to ~250 chars in the listing
- **Priority**: Anthropic bundled skills retain full descriptions; custom skills are trimmed first
- **Implication**: Write `description` under 250 chars. Put trigger keywords in first 100 chars.
  Use `when-to-use` for additional context (loaded separately, not budget-constrained).

**Budget math**: With 33 commands + 5 skills = 38 entries, average budget is ~395 chars each.
But bundled skills consume their share first, leaving less for custom entries.
```

**Complexity**: S (single file edit, ~15 lines added)

---

## Weakness 5: Vague Rules Without Numeric Criteria (T1 refinement) — LOW

### Current State (8/10)

SuperClaude uses 10+ numeric thresholds throughout. But some high-impact rules remain vague:

| Rule | Current (vague) | Suggested (numeric) |
|------|-----------------|---------------------|
| R06 Scope | "build only what's asked" | "build only what's asked — 0 unsolicited files, 0 adjacent refactors" |
| R12 Clarification | "ambiguous requests → ask" | "2+ valid interpretations → ask before implementing" |
| R13 Intent Verification | ">3 steps, ambiguous scope" | Already has numeric — good |
| anti_over_engineering | "Three similar lines is better..." | Already has numeric — good |
| Memory curation | "consolidate at 150 lines" | Already has numeric — good |

### Proposed Improvement

Add numeric anchors to the 2-3 vaguest rules. Small changes, high clarity gain.

**Complexity**: S (2-3 line edits in RULES.md)

---

## Priority Matrix

```
                    HIGH IMPACT
                        │
        ┌───────────────┼───────────────┐
        │   W1: Triple  │  W3: False    │
        │   Repetition  │  Reporting    │
HIGH    │   (T3)        │  Enum (T2)    │
EFFORT  │               │               │
        │   W2: Context │  W4: Budget   │
        │   Isolation   │  Mechanics    │
        │   (T7)        │  (T6)         │
        ├───────────────┼───────────────┤
        │               │               │
        │               │  W5: Numeric  │
LOW     │               │  Criteria     │
EFFORT  │               │  (T1)         │
        │               │               │
        │               │               │
        │               │               │
        └───────────────┼───────────────┘
                        │
                    LOW IMPACT

    ← Do first: W3, W4, W5 (right side, quick wins)
    ← Do next: W1, W2 (left side, structural)
```

## Recommended Implementation Order

1. **W3: False Reporting Enumeration** — 30 min, single file, immediate clarity gain
2. **W4: Skills Budget Mechanics** — 30 min, single file, prevents future skill authoring mistakes
3. **W5: Numeric Criteria** — 15 min, 2-3 line edits
4. **W1: Triple Repetition (Position 2 only)** — 2-4 hrs, audit all 23 agents, add top-3 rules to gotchas
5. **W2: Context Isolation** — 1-2 hrs, new rule + skill frontmatter + gotchas population

## Scope Boundaries — What NOT to Change

- **Don't redesign the @import chain** — the architecture is sound; the content needs sharpening
- **Don't add a hook-based rule reinforcer** (Position 3 of T3) — code change with unclear ROI; defer
- **Don't consolidate skills** to reduce budget pressure — 5 skills is well within 15K budget
- **Don't add CoT stripping rules** — T5 is runtime-managed by CC, not a framework concern
- **Don't triple-repeat ALL rules** — only R13, R18, and R02 warrant agent-level reinforcement
- **Don't create new files** for these improvements — all changes fit in existing files

## Verbalized Sampling — Perspective Distribution

This analysis was validated through 4 perspectives (VS distribution):

| Perspective | Weight | Key Claim | Status |
|-------------|--------|-----------|--------|
| Prompt Engineering Purist | p=0.35 | Core instruction quality > surface area | Confirmed by audit |
| System Architect | p=0.25 | T3 and T7 are structural gaps | Confirmed — T3 weakest, T7 unused |
| Token Economist | p=0.25 | Skills budget is most actionable | Partially confirmed — budget is fine at 5 skills, but documentation gap is real |
| Practitioner / UX | p=0.15 | Mental model teaching gap | Valid but out of scope for this analysis |

The Token Economist perspective was **corrected** by web research: with only 5 custom skills, SuperClaude is well within the 15K character budget. The gap is documentation (skill authors don't KNOW the budget exists), not actual budget pressure.
