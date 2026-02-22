# Requirements Specification: Opus Practical Guide Alignment

> Source: `/Users/chosh/ObsidianVault/opus-practical-guide.md`
> Scope: All P0–P2 items from brainstorm analysis
> Date: 2026-02-22

---

## Executive Summary

This spec aligns the SuperClaude content framework with the Opus Practical Guide's core principle: **"Find the smallest high-signal token set that maximizes the probability of the desired outcome."**

The audit found SuperClaude is already well-aligned on language tone (zero aggressive patterns), always-loaded token budget (~1,500 tokens), and JIT architecture. The gaps are in **example richness**, **delegation guardrails**, **skill manifest optimization**, **compaction strategy**, and **cross-command workflows**.

---

## P0-1: Enrich Examples in High-Rule Commands

### Rationale
Guide §6: "A few diverse, representative examples beat verbose rule lists."
Current: 4 commands have rules/examples ratio >3.0 with only happy-path examples.

### Target Files
- `src/superclaude/commands/pm.md` (ratio 3.33 → target 1.5)
- `src/superclaude/commands/research.md` (ratio 3.33 → target 1.5)
- `src/superclaude/commands/recommend.md` (ratio 3.0 → target 1.5)
- `src/superclaude/commands/spawn.md` (ratio 3.0 → target 1.5)

### Format Change
Replace table-based examples with richer input→output blocks:

**Current format (all 4 files):**
```markdown
<examples>
| Input | Output |
|-------|--------|
| `'Build auth system'` | Brainstorm → specialists |
```

**New format:**
```markdown
<examples>

<example name="strategy-selection" type="happy-path">
  <input>/sc:pm 'Build auth system'</input>
  <reasoning>Vague scope, multi-domain (DB + API + UI + security) → brainstorm strategy</reasoning>
  <output>
    Strategy: brainstorm
    Flow: requirements-analyst → system-architect → [backend-architect ‖ security-engineer] → frontend-architect
    MCP: seq (decomposition) → c7 (auth patterns) → magic (login UI)
    Tasks: 4 stories, 12 subtasks across 3 waves
  </output>
</example>

<example name="error-recovery" type="error-path">
  <input>/sc:pm 'Deploy to production'</input>
  <reasoning>No test results in context, no CI config detected → self-correction triggers</reasoning>
  <output>
    Strategy: direct (but blocked)
    Self-correction: STOP → Investigate (no test evidence) → Hypothesis (untested code)
    New approach: /sc:test --coverage first → then /sc:pm 'Deploy to production'
    User prompt: "No test results found. Run /sc:test first?"
  </output>
</example>

<example name="cross-command" type="handoff">
  <input>/sc:pm 'Optimize API response times'</input>
  <reasoning>Performance domain → needs profiling before action</reasoning>
  <output>
    Strategy: direct
    Handoff: /sc:analyze --focus perf → findings → /sc:improve --performance → /sc:test --e2e
    MCP: devtools (profiling) → seq (bottleneck analysis) → c7 (optimization patterns)
  </output>
</example>
```

### Specific Examples to Add Per File

#### pm.md (add 4 examples, replace existing 3)
1. **Happy path — brainstorm strategy**: Vague multi-domain request → full breakdown showing strategy selection logic, MCP phases, task creation
2. **Happy path — direct strategy**: Precise single-file fix → c7 lookup → refactoring-expert → done
3. **Error path — self-correction**: Request missing prerequisites → STOP → investigate → redirect
4. **Handoff path**: Request that spans commands → pm delegates to /sc:analyze → /sc:implement chain

#### research.md (add 4 examples, replace existing 3)
1. **Happy path — standard depth**: Factual query → 2-hop search → structured report with citations
2. **Happy path — exhaustive depth**: Complex comparative analysis → 5-hop investigation → full report
3. **Error path — no sources found**: Niche topic → standard fails → auto-escalate to deep → still sparse → report confidence gap
4. **Depth comparison**: Same query at quick vs deep showing different output granularity

#### recommend.md (add 4 examples, replace existing 3)
1. **Keyword detection flow**: `'my login page is broken'` → keyword_map matches debug+web → recommends /sc:troubleshoot + /sc:analyze --focus security
2. **Project context flow**: Detected React project + performance complaint → project_detect(react) + keyword_map(perf) → /sc:analyze --performance --play --magic
3. **Multi-domain request**: `'build e-commerce with payments'` → [api, web, sec] domains → multi-command workflow with ordering
4. **Beginner vs expert**: Same request with different expertise levels → different flag recommendations

#### spawn.md (add 4 examples, replace existing 3)
1. **Sequential strategy**: DB migration with ordering constraints → Epic → 3 Stories → 8 Tasks with dependency chain
2. **Parallel strategy**: Independent microservices → Epic → 4 Stories executed concurrently → integration Story
3. **Adaptive strategy**: Unknown scope → starts sequential → discovers parallelizable work → switches mid-execution
4. **Error path**: Spawn detects circular dependency in task graph → surfaces to user before execution

---

## P0-2: Tighten Sub-Agent Delegation Criteria

### Rationale
Guide §1.3: "Opus has a strong sub-agent bias. It creates agents for tasks a single grep could handle."
Current: FLAGS.md `--delegate` section only says WHEN to delegate, not when NOT to.

### Target File
`src/superclaude/core/FLAGS.md` — `<execution>` section

### Change
Add explicit non-delegation criteria after the `--delegate` line:

```xml
<execution>
--delegate [auto|files|folders]: >7 dirs, >50 files, complexity >0.8 → sub-agent parallel
  Prefer direct work for: single-file edits, sequential ops, <3 steps, simple searches
  Prefer sub-agents for: parallel-capable, isolated context, independent work streams, >5 files
--concurrency [n]: 1-15 → max concurrent operations
...
```

### Acceptance Criteria
- Two lines added: "Prefer direct work for:" and "Prefer sub-agents for:"
- Indented under `--delegate` to show they're sub-guidance
- Concise — no verbose explanation

---

## P0-3: Skill Manifest Token Optimization

### Rationale
Guide core principle: "Attention budget dilutes with more tokens."
Current: The full skill listing in the system prompt is injected into every conversation (~600 tokens for descriptions alone). As skills grow, this scales linearly.

Additionally, the system prompt skill listing (`<!-- Skills Available -->`) is generated by `context_loader.py` on every `UserPromptSubmit` — it shows frontmatter token estimates but the actual descriptions come from Claude Code's built-in skill discovery (the `<system-reminder>` block listing all skills). This built-in listing is ~1,200 tokens and grows with each new skill.

### Current Architecture
```
UserPromptSubmit hook:
  context_loader.py → outputs <!-- Skills Available --> with token estimates

Claude Code built-in:
  <system-reminder> with full skill listing (name + description + triggers for each)
```

### Proposed: Tiered Skill Listing

**Tier 1 — Always visible** (5-6 most-used skills, ~200 tokens):
```
Skills (common): /ship, /confidence-check, /sc:implement, /sc:research, /sc:test, /sc:analyze
Full list: /sc:help | All 31+ commands: /sc:<name>
```

**Tier 2 — On-demand via /sc:help** (full listing, loaded JIT):
The existing `help.md` command already lists all commands. No change needed here.

### Implementation Options

**Option A — Reduce context_loader.py skill output** (low effort):
- Change `format_skills_summary()` to output a single-line reference instead of per-skill breakdown
- From: `<!-- Skills Available --> \n <!--   confidence-check: ~103 tokens ... -->` (5 lines)
- To: `<!-- 3 skills installed. Use /sc:help for full list. -->` (1 line)
- Savings: ~150 tokens per conversation

**Option B — Categorized listing in system prompt** (medium effort):
- Group the 31+ skills into 5-6 categories in their registration
- System prompt shows category headers with 1-2 top skills each
- Requires changes to how skills register with Claude Code (may need upstream support)

**Option C — Frontmatter `priority` field** (medium effort):
- Add `priority: primary|secondary` to skill SKILL.md frontmatter
- `context_loader.py` only emits primary skills in the summary
- Secondary skills still work via `/sc:<name>` — just not listed in every prompt

### Recommendation
**Option A for immediate wins, Option C for long-term.**
Option B requires upstream Claude Code changes we don't control.

### Target Files
- `src/superclaude/scripts/context_loader.py` — `format_skills_summary()` function
- Optionally: skill SKILL.md files (add `priority` field)

---

## P1-4: Add Negative/Error Examples Universally

### Rationale
Guide §6.1: "Edge case rules are fragile. Show the behavior instead."
Guide §1.1: "Opus follows instructions literally — if you don't show failure modes, it won't handle them."
Current: Zero commands have negative examples or error recovery paths.

### Target Files
All 31 command .md files in `src/superclaude/commands/`

### Change
Add 1 negative example to each command's `<examples>` section. Format:

```markdown
<example name="invalid-usage" type="negative">
  <input>/sc:analyze --focus everything</input>
  <why_wrong>--focus accepts: perf|security|quality|arch|a11y|testing. 'everything' is not valid.</why_wrong>
  <correct>/sc:analyze --focus quality --scope module</correct>
</example>
```

### Priority Order (highest value first)
1. **pm.md** — Show what happens when no strategy fits
2. **spawn.md** — Show circular dependency detection
3. **research.md** — Show "no sources found" graceful degradation
4. **recommend.md** — Show "ambiguous request" asking for clarification
5. **implement.md** — Show scope creep prevention (request + adjacent changes rejected)
6. **build.md** — Show build failure recovery
7. **test.md** — Show test failure analysis vs retry
8. Remaining 24 commands — 1 negative example each

### Acceptance Criteria
- Each command has at least 1 `type="negative"` or `type="error-path"` example
- Negative examples show the CORRECT recovery, not just the failure
- No net increase in rule count — examples replace rules where possible

---

## P1-5: Model Tiering for Delegated Agents

### Rationale
Guide §8.1: "Not all tasks need Opus. Route exploration to cheaper models."
Current: FLAGS.md `--delegate` section has no model routing guidance.

### Target File
`src/superclaude/core/FLAGS.md` — `<execution>` section

### Change
Add model routing guidance:

```xml
--delegate [auto|files|folders]: >7 dirs, >50 files, complexity >0.8 → sub-agent parallel
  Prefer direct work for: single-file edits, sequential ops, <3 steps, simple searches
  Prefer sub-agents for: parallel-capable, isolated context, independent work streams, >5 files
  Model routing: haiku for search/explore, sonnet for general coding, opus for architecture/complex reasoning
```

### Acceptance Criteria
- One additional indented line under `--delegate`
- Covers the three model tiers with clear task-type mappings

---

## P2-7: Compaction Strategy Enhancement

### Rationale
Guide §5.1: "Compaction prompt tuning: recall first → precision improvement → test on complex traces."
Guide §5.1: "Safest lightweight compaction: clear old tool call results."
Current: MODE_Token_Efficiency.md covers symbol communication but not compaction strategy.

### Target File
`src/superclaude/modes/MODE_Token_Efficiency.md`

### Change
Add a `<compaction>` section:

```xml
<compaction note="Guide §5.1: Long-session context management">
  <when>Context >60% used, answer quality degrading, or explicit --uc flag</when>
  <preserve>Architecture decisions, unresolved issues, implementation details, active file paths</preserve>
  <discard>Completed tool outputs, resolved intermediate results, stale error messages, duplicate information</discard>
  <tuning_order>
    1. Recall: Capture all relevant information first
    2. Precision: Remove unnecessary content iteratively
    3. Validate: Test on complex agent traces, not simple conversations
  </tuning_order>
  <safest_action>Clear old tool call results — agent rarely needs raw results from much earlier</safest_action>
</compaction>
```

### Acceptance Criteria
- New `<compaction>` section in MODE_Token_Efficiency.md
- Covers when/what to preserve/discard
- Includes the guide's tuning order
- Concise — under 100 words

---

## P2-8: Cross-Command Workflow Examples

### Rationale
Guide §4.3: "Progressive disclosure — agents build context incrementally."
Current: No examples show how one command's output feeds into the next.

### Target Files
- `src/superclaude/commands/help.md` — Add workflow section
- P0-1 command examples already include handoff paths (see pm.md example 4, recommend.md example 3)

### Change to help.md
Add a `<workflows>` section showing common pipelines:

```xml
<workflows note="Common multi-command pipelines">

<workflow name="feature-development">
  /sc:brainstorm 'user auth' → requirements
  /sc:design --api --ddd → architecture spec
  /sc:implement --tdd → code
  /sc:test --coverage --e2e → validation
  /ship --pr → delivery
</workflow>

<workflow name="performance-fix">
  /sc:analyze --focus perf → bottleneck report
  /sc:troubleshoot --investigate → root cause
  /sc:improve --performance → optimized code
  /sc:test --e2e → regression check
</workflow>

<workflow name="research-to-implementation">
  /sc:research 'topic' --depth deep → findings
  /sc:brainstorm 'approach' → refined requirements
  /sc:design → architecture
  /sc:implement → code
</workflow>

</workflows>
```

### Acceptance Criteria
- 3-4 workflow pipelines showing realistic multi-command sequences
- Each step shows what artifact flows to the next
- Added to help.md (the reference command) not a new file

---

## Implementation Plan

### Phase 1 — Core guardrails (P0-2, P1-5): ~15 min
Edit FLAGS.md: add delegation criteria + model tiering (3 lines)

### Phase 2 — Token optimization (P0-3): ~30 min
Edit context_loader.py: simplify format_skills_summary()

### Phase 3 — Rich examples for top-4 commands (P0-1): ~2 hours
Rewrite examples sections in pm.md, research.md, recommend.md, spawn.md

### Phase 4 — Compaction strategy (P2-7): ~15 min
Add compaction section to MODE_Token_Efficiency.md

### Phase 5 — Cross-command workflows (P2-8): ~20 min
Add workflows section to help.md

### Phase 6 — Universal negative examples (P1-4): ~2 hours
Add 1 negative example to each of 31 command files

### Estimated total token impact
- FLAGS.md: +3 lines (~40 tokens)
- context_loader.py: -4 lines (~-150 tokens per conversation)
- pm/research/recommend/spawn.md: +~200 tokens each (but richer signal)
- MODE_Token_Efficiency.md: +~80 tokens
- help.md: +~120 tokens
- All commands: +~30 tokens each (1 negative example)
- **Net per-conversation: -150 tokens** (from skill summary optimization)
- **Net on-demand: +~1,900 tokens** (richer examples across files loaded JIT)

---

## Validation Criteria

1. All existing tests pass (`uv run pytest`)
2. `superclaude install` deploys updated content correctly
3. Language audit: zero new CRITICAL/MUST/ALWAYS/NEVER in added content
4. Token budget: always-loaded context stays under 2,000 tokens
5. Each modified command has rules/examples ratio ≤ 2.0
6. Negative examples show recovery, not just failure
