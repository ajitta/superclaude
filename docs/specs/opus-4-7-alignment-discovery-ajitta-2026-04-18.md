---
status: approved
revised: 2026-04-18
---

# SuperClaude × Opus 4.7 Prompting Alignment — Discovery Spec

**Source document:** `C:\Users\ajitta\ObsidianVault\Prompting Claude Opus 4.7.md` (915 lines, Anthropic prompting best-practices guide for Opus 4.7)
**Prior work:** `docs/specs/2026-03-15-opus46-alignment-design.md` (Opus 4.6 alignment, approved)
**Scope:** Identify behavioral gaps between SuperClaude framework content and Opus 4.7's documented defaults; produce a verification checklist the team can rerun on future model upgrades.
**Owner:** ajitta
**Status:** Draft for user review — do NOT proceed to `/sc:plan` before approval.

---

## 1. Problem Statement

Opus 4.7 changes several defaults that SuperClaude's framework content was tuned for under Opus 4.6:

- **Effort parameter** gains a new `xhigh` tier; 4.7 respects effort strictly (under-thinks at `low`/`medium`)
- **Tool use** decreases by default — models now prefer reasoning over tool calls
- **Subagent spawning** decreases by default — 4.7 waits for explicit guidance
- **Instruction following** is more literal — 4.7 will not silently generalize across items
- **Response length** calibrates adaptively — less verbose on simple queries
- **Frontend design** has a persistent cream/serif/terracotta house style
- **Code-review harnesses** that say "don't nitpick" now faithfully drop findings (recall ↓, precision ↑)

SuperClaude's Opus 4.6 alignment (March 2026) removed HOW-prescriptions and aggressive language. That work is still correct. But the 4.7-specific shifts above introduce new questions the existing alignment didn't answer.

## 2. Source Document — Key Points

| # | Guidance | Source § |
|---|----------|----------|
| D1 | `xhigh` is the recommended default for coding/agentic use cases; `high` minimum for intelligence-sensitive work | Calibrating Effort |
| D2 | Set max output token budget to 64k when running at `xhigh`/`max` | Calibrating Effort (Note) |
| D3 | 4.7 uses tools *less* than 4.6 — raise effort to increase tool use, not prompts | Tool Use Triggering |
| D4 | 4.7 provides natural progress updates — remove scaffolding like "summarize every 3 tool calls" | User-facing Progress Updates |
| D5 | 4.7 follows instructions literally — state scope explicitly ("apply to every section, not just the first") | More Literal Instruction Following |
| D6 | 4.7 spawns fewer subagents by default — add explicit guidance when you want more | Controlling Subagent Spawning |
| D7 | Frontend default is cream/serif/terracotta; specify concrete alternatives or ask for options | Design and Frontend Defaults |
| D8 | For coding products: use `xhigh`/`high`, add auto-mode, reduce user interactions | Interactive Coding Products |
| D9 | Code-review harnesses: "report every issue" at finding stage; filter downstream | Code Review Harnesses |
| D10 | Prefilled assistant responses deprecated — use structured outputs / direct instruction instead | Migrating away from Prefilled Responses |
| D11 | Adaptive thinking (`thinking: {type: "adaptive"}`) is the new default — `budget_tokens` deprecated | Leverage Thinking Capabilities |
| D12 | Model identity: `claude-opus-4-7` | Model Self-knowledge |
| D13 | Dial back aggressive language ("CRITICAL: You MUST…") — 4.5/4.6/4.7 overtrigger on it | Tool Usage |
| D14 | Parallel tool calling easily pushed to ~100% with explicit `<use_parallel_tool_calls>` block | Optimize Parallel Tool Calling |
| D15 | Overeagerness: add minimize-overengineering block when you see extra files/abstractions | Overeagerness |
| D16 | Agentic coding: `<investigate_before_answering>` block reduces hallucinations | Minimizing Hallucinations |

## 3. Current State Audit (what SuperClaude already does)

Audited on `master` @ commit `8edd05d` (2026-04-18).

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| A1 | `effort:` removed from all agents | ✅ aligned | commit 8edd05d removed 11 occurrences; grep for `effort:` in `agents/` returns zero |
| A2 | No aggressive language in agents | ✅ aligned | grep `CRITICAL:\|MUST use\|NEVER \|ALWAYS ` in `agents/` → 0 matches |
| A3 | Parallel tool calling guidance | ✅ aligned | CC system prompt + FLAGS.md `--concurrency` |
| A4 | Overeagerness / anti-over-engineering rules | ✅ aligned | RULES.md `<anti_over_engineering>` block |
| A5 | Investigate-before-answering (R17 Serena-First, R02 Status Check) | ✅ aligned | RULES.md core_rules |
| A6 | Subagent decision matrix | ⚠️ tuned for 4.6 | `<sub_agent_decision>` written when 4.6 over-spawned; 4.7 under-spawns |
| A7 | Frontend AI-slop guard | ❌ missing | `frontend-architect.md` has 0 lines addressing aesthetics/typography/default house style |
| A8 | Code-review coverage-vs-filter language | ❌ missing | `quality-engineer`, `self-review`, `security-engineer` have no "report every finding" block |
| A9 | `xhigh` documented | ⚠️ partial | Mentioned in `agent-authoring.md` effort enum but no agent uses it; no guidance on when to set it |
| A10 | Adaptive thinking framing in PRINCIPLES.md | ⚠️ outdated | Line 25 says "extended thinking when available" — should reference adaptive thinking as the 4.6+ default |
| A11 | Model identity block | ❌ missing | No `claude-opus-4-7` identity prompt; framework is model-agnostic by design but users may want it |
| A12 | "Reduce human interactions" / auto-mode guidance | ✅ already exists | CC auto-mode is native; SuperClaude defers |
| A13 | Literal-instruction-following callouts in rules | ⚠️ implicit | RULES.md uses broad language ("when code may be read") that 4.7 may apply narrowly |
| A14 | Progress-update scaffolding | ⚠️ possibly over-prompted | CC system prompt's "≤25 words between tool calls" + "one sentence updates" — natural to 4.7, may be redundant |

**Legend:** ✅ aligned · ⚠️ partial / needs review · ❌ missing

## 4. Improvement Opportunities (ranked by impact × reversibility)

### Tier 1 — High impact, low risk (recommend shipping)

**T1-a. Add frontend-aesthetics guard to `frontend-architect.md`**
- **Why:** Opus 4.7 has a persistent cream/serif/terracotta house style that is wrong for dashboards/dev-tools/fintech/healthcare. SuperClaude users hitting `frontend-architect` will inherit this default unless steered.
- **What:** Add an `<aesthetics>` section to `frontend-architect.md` (~15 lines) pairing Anthropic's recommended `<frontend_aesthetics>` snippet with a "propose 4 directions first" pattern for ambiguous briefs.
- **R18 check:** Specific failure scenario = AI-slop output on enterprise briefs. ✅ passes.
- **Sketch:**
  ```xml
  <aesthetics>
    For ambiguous briefs: propose 4 distinct directions (bg hex / accent / typeface / rationale) before building. Never default to cream + serif + terracotta — that house style fits editorial/hospitality, not dashboards/fintech/healthcare/dev-tools. Avoid Inter, Roboto, Arial, purple-on-white gradients, and cookie-cutter layouts.
  </aesthetics>
  ```

**T1-b. Add coverage-vs-filter language to review agents**
- **Why:** `quality-engineer`, `self-review`, `security-engineer` risk dropping low-severity findings under 4.7's literal interpretation of "be concise" / "focus on real issues."
- **What:** Add one `<finding_policy>` block to each (~5 lines): "Report every finding with confidence + severity; filtering happens downstream."
- **R18 check:** Measurable via eval recall. ✅ passes.
- **Sketch:**
  ```xml
  <finding_policy>
    Report every finding including low-severity and low-confidence ones. Tag each with `severity` and `confidence`. Do not filter at this stage — ranking happens downstream. Coverage > precision here.
  </finding_policy>
  ```

**T1-c. Update PRINCIPLES.md thinking line**
- **Why:** Current wording ("extended thinking when available") predates adaptive thinking as Opus 4.6+ default.
- **What:** Single line diff — replace "extended thinking" with "adaptive thinking (model decides)".
- **Sketch:** `PRINCIPLES.md:25` change:
  - Before: `Complex reasoning (debug, arch): extended thinking when available`
  - After: `Complex reasoning (debug, arch): adaptive thinking (model-managed; effort parameter tunes depth)`

### Tier 2 — Medium impact, requires measurement

**T2-a. Document when (if ever) to set `effort: xhigh` on specific agents**
- **Why:** Doc says `xhigh` default for coding/agentic. SuperClaude deleted all effort fields last night (commit 8edd05d) on the principle "inherit from parent unless measured evidence says otherwise." The doc provides that evidence for coding agents.
- **Options:**
  1. Keep current behavior (inherit only). Trust users to set session effort.
  2. Add `effort: xhigh` to ~5 coding-heavy agents: `backend-architect`, `frontend-architect`, `refactoring-expert`, `root-cause-analyst`, `performance-engineer`.
  3. Document the decision in `agent-authoring.md` with "if your session runs at `medium` or `low`, set `effort: xhigh` on coding agents explicitly."
- **Recommendation:** Option 3 — preserve inherit-by-default but give users a clear signal. Matches commit 8edd05d's stated intent ("measured evidence") — we don't yet have agent-level evals proving xhigh improves SuperClaude output.
- **Decision needed from user.**

**T2-b. Soften `<sub_agent_decision>` rules for 4.7's lower spawn rate**
- **Why:** Current rules (`Never sub-agent: tasks needing recent conversation context, sequential A→B, completable in <30s directly`) were written when Opus 4.6 over-spawned. 4.7 under-spawns — users may see *too little* delegation now.
- **What:** Add a prompt pattern to `--delegate auto` docs: "If task has 3+ independent streams, explicitly invoke parallel subagents — do not rely on 4.7 to auto-spawn them."
- **R18 check:** Needs measurement (how often does auto-delegate fire under 4.7?). ⚠️ defer pending eval.

### Tier 3 — Opportunities worth considering but not urgent

- **T3-a.** Audit RULES.md for rules that broadly say "all" / "every" without scope — 4.7's literalism may make these brittle. Add explicit scope where intent is broad (e.g., R02 "2-3 targeted searches" is fine; R06 "0 unsolicited files" is fine; borderline ones need review).
- **T3-b.** Consider removing "≤25 words between tool calls" scaffolding from CC-level system prompt (this is CC harness, not SuperClaude — out of scope for this project but worth noting).
- **T3-c.** Model identity prompt: leave unset. SuperClaude ships model-agnostic content by design (see `docs/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md`).
- **T3-d.** Migration-away-from-prefilled-responses: N/A — SuperClaude doesn't use prefills.

### Explicitly deferred / out-of-scope

- 64k max-token budget recommendation (D2) — runtime config, not framework content
- Computer-use resolution guidance (D16 in doc) — specific to CU workloads, no SuperClaude agent covers CU
- API migration code examples — SDK-user concern, not CLAUDE.md concern

## 5. Verification Checklist — "Does SuperClaude match Opus 4.7's documented defaults?"

Self-audit checklist. Re-run on every model upgrade. Each item maps to a document guidance ID (D1–D16) and includes a verification command where possible.

### Part A — Content audit (can run today)

```
[ ] V1  (D3,D6,D13) No CAPS enforcement language
        grep -rE "CRITICAL:|MUST use|You MUST|NEVER " src/superclaude/{agents,commands,modes,core}/
        Expected: 0 matches
[ ] V2  (D13) No pre-Opus-4.5 aggressive prompting patterns
        grep -rE "(If in doubt|by default) use" src/superclaude/agents/
        Expected: soft language only ("consider", "prefer")
[ ] V3  (D5) Rules with broad scope have explicit application boundaries
        Manual review of RULES.md <core_rules> for rules containing "all", "every", "always"
        Expected: each has scope qualifier
[ ] V4  (D6) Subagent guidance reflects 4.7's lower-spawn default
        Search: RULES.md <sub_agent_decision> references 4.7 behavior
        Expected: includes "explicit invocation" note for 3+ stream cases
[ ] V5  (D7) Frontend agent has AI-slop guard
        Search: frontend-architect.md for "aesthetic" / "frontend_aesthetics" / "generic"
        Expected: ≥1 match inside <aesthetics> or <design_defaults> tag
[ ] V6  (D9) Review agents use coverage-first language
        Search: quality-engineer/self-review/security-engineer for "report every" / "coverage" / "downstream filter"
        Expected: ≥1 finding-policy block per agent
[ ] V7  (D11) Thinking references are adaptive-thinking-aware
        grep -r "extended thinking\|budget_tokens" src/superclaude/core/
        Expected: only in historical context (migration notes), not as prescribed default
[ ] V8  (D15) Anti-overengineering language present
        Check: RULES.md <anti_over_engineering> and R06/R18
        Expected: ✅ (already exists)
[ ] V9  (D16) Investigation-before-answering rule present
        Check: RULES.md R02 (Status Check), R17 (Serena-First)
        Expected: ✅ (already exists)
[ ] V10 (D14) Parallel-tool-call guidance present
        Check: FLAGS.md --concurrency, system-prompt parallel instructions
        Expected: ✅ (already exists)
```

### Part B — Behavioral verification (empirical tests)

Run these against the actual model to confirm the doc's claims (not just alignment). Use `/sc:insight` to capture results.

```
[ ] B1  (D1) Effort strictness at low/medium
        Test: identical complex task at effort=low vs effort=high; measure solution completeness.
        Expected: low under-thinks (misses edge cases); high covers them.
[ ] B2  (D3) Tool-use decrease
        Test: ambiguous research task with --tavily available, effort=high vs effort=medium.
        Expected: higher effort → more tool calls.
[ ] B3  (D5) Literal instruction following
        Test: "Apply this formatting to the first section" vs "to every section" — observe scope.
        Expected: 4.7 narrowly scopes to "first section" when phrased that way.
[ ] B4  (D6) Subagent under-triggering
        Test: "Research React 19 + Vue 4 + Svelte 5" without --delegate.
        Expected: 4.7 does NOT auto-spawn 3 subagents; direct tool calls instead.
[ ] B5  (D7) Frontend default house style
        Test: "Build a dashboard for a fintech startup" without aesthetic guidance.
        Expected: cream/serif output (confirms need for guard).
[ ] B6  (D9) Code-review filtering under "don't nitpick"
        Test: known-buggy PR with prompt "review this, only report important issues" vs "report every issue".
        Expected: latter returns strictly more findings.
[ ] B7  (D4) Progress updates natural vs scaffolded
        Test: long multi-tool task without progress-update instructions.
        Expected: 4.7 gives natural updates (confirms scaffolding can be removed).
[ ] B8  (D11) Adaptive thinking behavior
        Test: simple query and complex query in same session.
        Expected: thinking token count scales with complexity (adaptive confirmed).
```

### Part C — Regression checks (after any alignment change)

```
[ ] R1  All unit tests pass
        uv run pytest tests/unit/ -v
[ ] R2  Agent structure tests pass (enforces authoring rules)
        uv run pytest tests/unit/test_agent_structure.py -v
[ ] R3  Content structure tests pass
        uv run pytest tests/unit/test_content_structure.py -v
[ ] R4  Install-tree self-containment preserved (gotcha: install-tree-boundary)
        make deploy && superclaude install --list-all succeeds
[ ] R5  No broken @-imports or {{PATH}} variables
        grep -r "{{.*PATH" src/superclaude/ → all resolve at install
```

## 6. Open Questions (need user input before `/sc:plan`)

1. **Scope of Tier 2:** Should we commit to T2-a (effort field decision) and T2-b (subagent guidance) in this iteration, or defer them pending eval data?
2. **Agent-specific xhigh:** If we go with T2-a Option 2 (add `effort: xhigh` to 5 coding agents), which 5? Proposed: `backend-architect`, `frontend-architect`, `refactoring-expert`, `root-cause-analyst`, `performance-engineer`. Do you want `system-architect` and `python-expert` added?
3. **Verification Part B ownership:** Who runs the empirical tests — manual user sessions, or a new `tests/behavioral/` suite (out of scope for most frameworks, but SuperClaude has `/sc:insight` for capture)?
4. **Cadence:** Should Part A become part of CI (`tests/unit/test_opus_alignment.py`) or a manual checklist run per model upgrade?
5. **Naming:** I drafted this as "Opus 4.7 alignment" following the 4.6 precedent. Prefer a model-agnostic title like "Prompting-best-practices alignment" so the checklist survives future upgrades?

## 7. Recommended Next Steps (pending user approval)

Assuming Tier 1 is approved:

1. `/sc:plan` to break Tier 1 (T1-a, T1-b, T1-c) into concrete file edits with line-level changes
2. Implement as `docs/`-branch (no code changes — pure content)
3. Run Part A verification checklist after implementation
4. Capture Part A results to `.claude/rules/checklists/opus-4-7-alignment.md` (new file) as a living audit artifact
5. Update `src/superclaude/agents/README.md` and `docs/reference/` with a pointer to the new checklist

**Tier 2/3 decisions deferred until user provides answers to §6.**

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Frontend-aesthetics guard over-steers on editorial/hospitality briefs (where cream/serif IS appropriate) | Medium | Low | Keep guard as "propose directions first" pattern rather than outright ban — user picks direction |
| Coverage-first finding policy floods output with noise on clean code | Medium | Medium | Require severity+confidence tags so downstream can filter; this matches doc D9 verbatim |
| Adding `effort: xhigh` to coding agents inflates token spend unexpectedly | Medium | Medium | Defer to Tier 2 decision with explicit user opt-in; document the cost trade-off |
| Alignment changes regress Opus 4.6 behavior for users not on 4.7 | Low | High | Framework is model-agnostic by design (see 2026-03-23 spec); all changes use model-neutral language |
| Verification checklist becomes stale after next model release | High | Low | §6 Q5 — consider model-agnostic naming so checklist evolves via re-grep not rewrite |

## 9. References

- Source: `C:\Users\ajitta\ObsidianVault\Prompting Claude Opus 4.7.md`
- Prior: `docs/specs/2026-03-15-opus46-alignment-design.md`
- Prior: `docs/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md`
- Audit evidence: commit `8edd05d` (2026-04-18) removed `effort:` from 11 agents
- Related: `docs/reference/opus-4.5-evaluation-report.md` (earlier model evaluation)
