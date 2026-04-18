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
Command: `grep -n "Opus 4.7" src/superclaude/core/RULES.md`
Expected: ≥1 match inside `<sub_agent_decision>` referencing explicit invocation for 3+ independent streams
Known state: Doc-level note added in Tier 2 (2026-04-18). Behavioral-threshold rewrite (changing Sub-agent criteria numbers) remains deferred pending eval data on `--delegate auto` trigger rate under Opus 4.7.

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

---

## Run results 2026-04-18 (initial run after Tier 1 implementation)

| V# | Status | Evidence |
|----|--------|----------|
| V1 | ✅ pass | grep returns 0 matches across agents/commands/modes/core |
| V2 | ✅ pass | no "(If in doubt|by default) use" patterns in agents/ |
| V3 | ⏭ manual review pending | scheduled for next framework audit |
| V4 | ⚠️ deferred | T2-b — not in Tier 1 scope |
| V5 | ✅ pass | 3 matches in frontend-architect.md (<aesthetics> block) |
| V6 | ✅ pass | finding_policy present in quality-engineer, self-review, security-engineer |
| V7 | ✅ pass | 0 matches for "extended thinking"/"budget_tokens" in core/ |
| V8 | ✅ (pre-existing) | RULES.md <anti_over_engineering> confirmed in audit |
| V9 | ✅ (pre-existing) | RULES.md R02, R17 confirmed in audit |
| V10 | ✅ (pre-existing) | FLAGS.md --concurrency confirmed in audit |

**Summary:** 8 ✅ pass · 1 ⏭ pending manual (V3) · 1 ⚠️ deferred (V4, T2-b). Tier 1 complete.
**Regression:** `uv run -- python -m pytest tests/unit/` → 1684 passed, 0 failed.

---

## Run results 2026-04-18 (after Tier 2 implementation)

| V# | Status | Evidence |
|----|--------|----------|
| V1 | ⚠️ 1 match (pre-existing, missed in Tier 1) | `src/superclaude/commands/insight.md:107` has `NEVER use Write tool for insights.jsonl` — line introduced 2026-04-11 (commit `b5c974f3`), predates Tier 1 run. Context is a technical tool-safety gotcha, not aggressive enforcement prompting. Scope-gate (R06) prevents inline fix within Tier 2; flagged as follow-up — user decision: (a) reword `NEVER` → `Do not` at insight.md:107, (b) refine V1 grep to exclude gotcha-style warnings, or (c) accept as documented exception |
| V2 | ✅ pass | `grep -rnE "(If in doubt\|by default) use" src/superclaude/agents/` → 0 matches |
| V3 | ⏭ manual review pending | unchanged — scheduled for next framework audit |
| V4 | ✅ pass (doc-level) | `grep "Opus 4.7" src/superclaude/core/RULES.md` matches at line 17 inside `<sub_agent_decision>`; threshold rewrite still deferred pending eval |
| V5 | ✅ pass | `grep -cE "aesthetics\|..." src/superclaude/agents/frontend-architect.md` → 3 |
| V6 | ✅ pass | `grep -l "finding_policy" <3 review agents>` → 3 files match |
| V7 | ✅ pass | `grep -rnE "extended thinking\|budget_tokens" src/superclaude/core/` → 0 matches |
| V8 | ✅ (pre-existing) | RULES.md `<anti_over_engineering>` + R06 + R18 all present |
| V9 | ✅ (pre-existing) | RULES.md R02, R17 present |
| V10 | ✅ (pre-existing) | FLAGS.md `--concurrency` present at line 34 |

**Summary:** 8 ✅ pass · 1 ⚠️ pre-existing V1 match surfaced (not caused by Tier 2 — missed in Tier 1 run) · 1 ⏭ pending manual (V3). Tier 2 content changes themselves complete; V1 follow-up awaiting user decision.
**Regression:** `uv run -- python -m pytest tests/unit/ -q` → **1684 passed, 0 failed** (identical to Tier 1 baseline).
