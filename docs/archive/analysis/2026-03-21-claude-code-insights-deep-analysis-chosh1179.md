# Claude Code Insights — Deep Usage Data Analysis

**Date:** 2026-03-21
**Author:** chosh1179
**Data source:** `~/.claude/usage-data/` (facets: 200, session-meta: 640)
**Report period:** 2026-02-19 to 2026-03-20 (18 active days)
**Scope:** SuperClaude-aware analysis of raw usage data, beyond the standard HTML report

---

## 1. Data Overview

| Metric | Value |
|--------|-------|
| Total sessions | 640 (report counted 312 — excludes observer sessions) |
| Facets (rated sessions) | 200 |
| Total tokens | 3,629,344 (864K input / 2,765K output) |
| Messages | 5,561 |
| Projects | 4 active (superclaude, oasis_editor, observer-sessions, oasis-nakama-dev) |

**Critical note:** The HTML report analyzed only 312 sessions. The raw data contains 640 — the missing 328 are predominantly observer-sessions (317) which were excluded from the report's analysis, masking a major inefficiency.

---

## 2. Per-Project Breakdown

The report aggregated all projects. Project-level segmentation reveals dramatically different profiles:

| Project | Sessions | Commit Rate | Success Rate | Avg Duration | Tokens | Top Friction |
|---------|----------|-------------|-------------|-------------|--------|-------------|
| **observer-sessions** | 317 (49.5%) | **0%** | 37.7% | 4.6m | 1,717,941 (47.3%) | wrong_approach (9) |
| **superclaude** | 159 (24.8%) | **45.9%** | 67% | 41m | 804,094 (22.2%) | buggy_code (5) |
| **oasis_editor** | 140 (21.9%) | 28.6% | 59% | 133m | 1,008,873 (27.8%) | **buggy_code (9)** |
| **oasis-nakama-dev** | 12 (1.9%) | 16.7% | 50% | 171m | 58,006 (1.6%) | wrong_approach (1) |
| Others | 12 (1.9%) | — | — | — | 40,430 (1.1%) | — |

### Key Insights

1. **observer-sessions consumes 47.3% of all tokens for 0 commits** — this is the single biggest efficiency finding
2. **superclaude is the healthiest project** — highest commit rate (45.9%), highest success rate (67%), moderate friction
3. **oasis_editor carries the test friction** — 9/17 buggy_code events (53% of all buggy_code friction)
4. **Friction is project-specific, not user-wide** — report's aggregated recommendations miss this

---

## 3. Observer Sessions — Cost-Benefit Analysis

| Metric | Observer | Non-Observer |
|--------|----------|-------------|
| Sessions | 317 (49.5%) | 323 (50.5%) |
| Tokens consumed | 1,717,941 (47.3%) | 1,911,403 (52.7%) |
| Tool calls (total) | **40** (0.13/session) | **8,078** (25/session) |
| Commits | **0** | 115 |
| Fully achieved | 37.7% | 66.9% |
| Avg duration | 4.6 minutes | 97.3 minutes |

### What observer sessions do

- 249 sessions start with `"hello memory agent, you are continuing to observe..."` prompt
- 63 sessions start with `"you are a claude-mem, a specialized observer tool..."`
- Total tool calls across all 317 sessions: 40 (ToolSearch: 21, TaskCreate: 11, TaskUpdate: 4, Skill: 3, TaskList: 1)
- No Read, Grep, Edit, Write, Bash, or Serena calls — zero code interaction

### Verdict

**Observer sessions are a 47.3% token tax with near-zero ROI.** They were designed to maintain cross-session context, but:
- They produce no code changes (0 commits)
- They make almost no tool calls (0.13/session)
- They have the lowest success rate (37.7%)
- They contribute the most wrong_approach friction (9/22)
- claude-mem's built-in memory system now provides the same cross-session persistence natively

**Recommendation:** Phase out observer sessions entirely. Replace with claude-mem's structured memory writes at session end via `/sc:save`.

---

## 4. Tool Efficiency — Serena Adoption by Project

| Project | Read | Grep | Serena | Serena Adoption Rate |
|---------|------|------|--------|---------------------|
| oasis_editor | 854 | 539 | 936 | **40.2%** |
| superclaude | 681 | 263 | 240 | 20.3% |
| oasis-nakama-dev | 26 | 40 | 10 | 13.2% |

### Serena Tool Breakdown (all projects)

| Tool | Uses | Purpose |
|------|------|---------|
| find_symbol | 442 | Code navigation (main use) |
| search_for_pattern | 167 | Regex search (Grep alternative) |
| get_symbols_overview | 111 | File structure exploration |
| think_about_* (combined) | 100 | Internal reasoning (token cost!) |
| read_memory | 70 | Cross-session recall |
| activate_project | 65 | Project switching |
| write_memory | 47 | Context persistence |
| delete_memory | 29 | Memory cleanup |
| replace_symbol_body | 22 | Symbolic editing |
| find_referencing_symbols | 17 | Usage tracing |

### Key Insights

1. **oasis_editor has 2x Serena adoption vs superclaude** — likely because oasis has larger files where symbolic reads are more valuable
2. **Serena's think_about_* tools consume 100 calls** — these are internal reasoning steps that consume tokens without providing direct value to the user
3. **replace_symbol_body (22) vs Edit (393+470)** — symbolic editing barely adopted even where Serena is active
4. **superclaude has room for Serena improvement** — 20.3% → target 40%+ would save significant Read/Grep tokens

---

## 5. SuperClaude Command Usage

### /sc:* Command Distribution

```
/sc:analyze:      ████████████████████████████████████████  80 (52.0%)
/sc:troubleshoot: ████████  15 (9.7%)
/sc:brainstorm:   ███████  13 (8.4%)
/sc:git:          ██████  11 (7.1%)
/sc:implement:    ███  6 (3.9%)
/sc:improve:      ███  6 (3.9%)
/sc:help:         ███  5 (3.2%)
/sc:index:        ███  5 (3.2%)
/sc:load:         ███  5 (3.2%)
/sc:research:     █  2 (1.3%)
/sc:reflect:      █  2 (1.3%)
/sc:save:         ▏  1 (0.6%)
/sc:agent:        ▏  1 (0.6%)
/sc:document:     ▏  1 (0.6%)
/sc:explain:      ▏  1 (0.6%)
```

### Unused Commands (0 uses in data period)

```
/sc:plan, /sc:test, /sc:review, /sc:design, /sc:workflow,
/sc:build, /sc:cleanup, /sc:estimate, /sc:spec-panel,
/sc:business-panel, /sc:recommend, /sc:select-tool, /sc:pm
```

### Key Insights

1. **/sc:analyze dominates at 52%** — likely because "analyze" is a broad verb covering many investigation tasks
2. **/sc:plan is never used** despite being a key workflow gate in RULES.md (`brainstorm → plan → implement`)
3. **The workflow pipeline is theoretical** — real usage is `analyze → ad-hoc` or `brainstorm → direct implementation`
4. **13 out of 32 commands have 0 usage** — either undiscoverable, unnecessary, or too specialized
5. **/sc:save (1 use) vs /sc:load (5 uses)** — save is barely adopted despite being the session-end checkpoint

---

## 6. Flag Usage Quality

### Valid Flags (in FLAGS.md)

| Flag | Uses | Purpose |
|------|------|---------|
| --seq | 66 | Sequential thinking MCP |
| --effort | 32 | Effort level control |
| --tavily | 15 | Web search MCP |
| --c7 | 14 | Context7 docs MCP |
| --delegate | 11 | Sub-agent delegation |
| --orchestrate | 9 | Tool matrix optimization |
| --introspect | 9 | Self-analysis mode |
| --concurrency | 8 | Parallel tool calls |
| --uc | 7 | Ultra-compressed output |
| --loop | 6 | Iterative improvement |
| --brainstorm | 3 | Discovery mode |
| --iterations | 2 | Fixed iteration count |

### Invalid/Typo Flags (NOT in FLAGS.md)

| Flag | Uses | Probable Intent |
|------|------|----------------|
| --ultrathink | 14 | `--seq --effort max` ? |
| --fix | 8 | No mapping — commonly expected |
| --parellel | 4 | `--delegate` (typo) |
| --think | 3 | `--seq` ? |
| --think-hard | 3 | `--effort max` ? |
| --force | 2 | No mapping |
| --agent | 2 | `--delegate` ? |
| --conccurrency | 1 | `--concurrency` (typo) |
| --confidenc-check | 1 | `--validate` (typo) |
| --loo | 1 | `--loop` (truncation) |
| --iteration | 1 | `--iterations` (singular typo) |
| --sea | 1 | `--serena` (truncation) |
| --bc | 1 | Unknown |

**Total invalid flag uses: 39** (14.5% of all flag usage)

### Key Insights

1. **--ultrathink (14 uses)** is the most common non-existent flag — users expect this to work
2. **Spelling errors account for ~10 uses** — fuzzy matching would eliminate these
3. **Conceptual flags (--fix, --think, --force)** suggest user mental model includes flags SuperClaude doesn't offer
4. **context_loader silently ignores unknown flags** — no error or suggestion provided

---

## 7. Friction Analysis (project-specific)

### Overall Friction Distribution

| Friction Type | Count | Primary Project | % of Total |
|---------------|-------|----------------|-----------|
| wrong_approach | 22 | observer (9), oasis (7), superclaude (3) | 30.6% |
| buggy_code | 17 | oasis (9), superclaude (5) | 23.6% |
| user_rejected_action | 10 | oasis (5), superclaude (3) | 13.9% |
| misunderstood_request | 6 | oasis (3), superclaude (2) | 8.3% |
| excessive_changes | 4 | superclaude (2), observer (1) | 5.6% |
| tool_limitation(s) | 6 | observer (4), oasis (1) | 8.3% |
| Other types | 7 | Various | 9.7% |

### Friction Details (representative samples)

1. **wrong_approach (observer):** "Serena's get_symbols_overview repeatedly failed due to project root misconfiguration, forcing fallback to manual file reading"
2. **buggy_code (oasis):** "Test file required two rewrites due to vi.mock hoisting and vi.clearAllMocks issues"
3. **user_rejected_action (oasis):** "User interrupted Claude's plan/write action for the bulk delete fix, suggesting approach misaligned"
4. **misunderstood_request:** "Claude assumed number type analysis when user wanted JSON payload size reduction"
5. **excessive_changes (superclaude):** Multi-step interactive approval process too verbose

---

## 8. Token Efficiency by Outcome

| Outcome | Count | Avg Tokens | Median Tokens | Range |
|---------|-------|-----------|--------------|-------|
| fully_achieved | 100 | 7,859 | 4,044 | 65 – 94,354 |
| mostly_achieved | 35 | **11,831** | 8,149 | 115 – 56,325 |
| partially_achieved | 36 | 5,812 | 2,636 | 176 – 27,317 |
| not_achieved | 3 | 589 | 558 | 501 – 709 |

### Key Insights

1. **mostly_achieved costs 50% more tokens than fully_achieved** — friction adds token cost without completing the goal
2. **partially_achieved has LOW median tokens (2,636)** — confirms these are intentional investigative probes, not failures
3. **not_achieved sessions exit quickly (589 avg)** — user recognizes dead ends fast
4. **Fully achieved sessions have high variance** (65 – 94,354) — some tasks are inherently more complex

---

## 9. Weekly Trends

| Week | Sessions | Tokens | Success Rate | Friction |
|------|----------|--------|-------------|---------|
| W04 | 55 | 222,879 | 50% | 0 |
| W05 | 68 | 322,188 | 100% | 1 |
| W06 | 36 | 175,868 | 65% | **9** |
| W07 | 28 | 147,877 | 62% | **18** |
| W08 | 26 | 358,110 | 50% | **16** |
| W09 | 180 | 604,198 | 30% | 4 |
| W10 | 81 | 419,347 | **100%** | **0** |
| W11 | 106 | 923,358 | 53% | **14** |

### Key Insights

1. **W07-W08 friction spike** (18 + 16 = 34 events in 2 weeks) — coincides with heavy oasis_editor debugging work
2. **W09 anomaly** — 180 sessions but 30% success rate and only 4 friction events → massive observer session burst (few facets rated)
3. **W10 was the best week** — 100% success, 0 friction, 81 sessions. What was different? Possibly superclaude-focused work after RULES.md improvements
4. **W11 regression** — back to 53% success, 14 friction. RULES.md improvements don't prevent friction consistently

---

## 10. Multi-Clauding Patterns

| Metric | Value |
|--------|-------|
| Total overlap events | 190 |
| Cross-project overlaps | 129 (67.9%) |
| Same-project overlaps | 61 (32.1%) |

### Top Overlap Combinations

| Combination | Count |
|-------------|-------|
| oasis_editor + observer-sessions | 26 |
| observer-sessions + observer-sessions | 25 |
| oasis_editor + oasis_editor | 24 |
| workspaces + observer-sessions | 18 |
| oasis-nakama-dev + observer-sessions | 16 |
| superclaude + observer-sessions | 14 |
| superclaude + superclaude | 12 |
| superclaude + oasis_editor | 12 |

### Key Insight

**Observer sessions are involved in 99 of 190 overlaps (52.1%)** — the primary pattern is "primary work session + observer running alongside." This confirms observer sessions are satellite processes, not independent work.

---

## 11. Error Analysis

| Error Type | Count | % | Top Project |
|-----------|-------|---|-------------|
| Other | 122 | 44.2% | superclaude (64), oasis (51) |
| User Rejected | 77 | 27.9% | oasis (52), superclaude (23) |
| Command Failed | 55 | 19.9% | superclaude (31), oasis (21) |
| File Not Found | 13 | 4.7% | oasis (6), superclaude (5) |
| Edit Failed | 4 | 1.4% | oasis (3) |
| File Too Large | 4 | 1.4% | superclaude (3) |
| File Changed | 1 | 0.4% | oasis (1) |

### Key Insights

1. **"Other" errors (122) remain the largest opaque category** — 44.2% of all errors have no clear classification
2. **User Rejected is highest in oasis_editor (52)** — Claude proposes actions the user disagrees with more often in the complex JS codebase
3. **Command Failed in superclaude (31)** — likely `make deploy`, `uv run pytest`, or hook-related commands
4. **Sessions with errors: 104/640 (16.2%)** — roughly 1 in 6 sessions hits at least one error

---

## 12. Commit Efficiency

| Project | Commits | Sessions | Rate |
|---------|---------|----------|------|
| superclaude | 73 | 159 | **45.9%** |
| oasis_editor | 40 | 140 | 28.6% |
| oasis-nakama-dev | 2 | 12 | 16.7% |
| observer-sessions | 0 | 317 | 0% |

**Overall: 115 commits / 640 sessions = 18.0% commit rate**
**Excluding observer: 115 / 323 = 35.6% commit rate**

---

## Summary: Report vs. Reality

| Report Claim | Data Reality |
|-------------|-------------|
| "312 sessions" | 640 sessions (328 observer sessions hidden) |
| "96% satisfaction" | Model-estimated; observer 37.7% success pulls real effectiveness down |
| "Friction: wrong_approach #1" | True, but 41% lives in observer sessions — eliminate observers, eliminate friction |
| "Vitest mock issues" | 53% concentrated in oasis_editor — project-specific, not user-wide |
| "Use hooks for auto-testing" | Already implemented in SuperClaude |
| "Use custom slash commands" | 13/32 commands have 0 usage — discovery problem, not supply problem |
| "Observer sessions low value" | Confirmed: 47.3% tokens, 0 commits, 0.13 tool calls/session |
