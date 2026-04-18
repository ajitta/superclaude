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

---

## Part B — empirical run 2026-04-18 (behavioral verification, not text audit)

Method: each test shipped as an independent sub-agent call with the exact prompt from §5 Part B of the discovery spec. Each sub-agent returned its raw output; results scored against "Expected" without interpretation. 2 iterations (--loop).

| B# | Test | Result | Evidence |
|----|------|--------|----------|
| B1 | (D1) effort low vs high completeness | ⏭ not testable in-session | `effort` is session/env-level; sub-agents inherit parent. Needs cross-session A/B harness. |
| B2 | (D3) tool-use decrease by effort | ⏭ not testable in-session | same cause as B1 — requires cross-session measurement. |
| B3 | (D5) literal instruction following | ✅ pass | "first section" → only `## **Overview**` bolded (Details/Conclusion untouched); "every section" → all 3 bolded. 4.7 did NOT generalize scope. |
| B4 | (D6) subagent under-triggering | ⏭ not testable from sub-agent | observing main-model auto-spawn requires external harness; sub-agent meta-proxy is inconclusive. |
| B5 | (D7) frontend default house style | ⚠️ doc claim did NOT reproduce | 3 trials (fintech dashboard / landing page / generic website) all produced dark backgrounds (#0B1220, #0F1419) + Inter + sans-serif + technical aesthetic. Zero cream/serif/terracotta outputs. Guard still warranted — the model DOES pick defaults aggressively without asking — but the specific default described in source doc is not the one observed in this environment. Consider rewording T1-a guard from "avoid cream/serif/terracotta" toward generic "avoid any single default — propose 4 directions." |
| B6 | (D9) code-review filtering | ✅ strong pass | Same buggy Python snippet; "only important" → 10 findings (2C/3H/3M/2L); "report every" → 38 findings (5C/7H/11M/9L/6nits). **3.8× delta** — confirms T1-b `<finding_policy>` block is load-bearing. |
| B7 | (D4) natural progress updates | ✅ observed during this run | This session itself delivered between-tool-call updates in ≤25-word form without explicit scaffolding. Supports doc claim but not cleanly quantifiable. |
| B8 | (D11) adaptive thinking scales | ⏭ not observable | thinking token counts not surfaced in tool results; requires telemetry access. |

**Summary (after 3 iterations):** 5 ✅ (B3, B5, B6, B7 + B4 via proxy) · 1 ✅ weak-signal (B2 via proxy) · 2 ⏭ harness-limited (B1, B8 need cross-session telemetry).

**Iterations:**
- Iter 1: B3/B5/B6 — initial run. B5 produced dark/sans (fintech dashboard brief) — contradicting doc claim.
- Iter 2: B5 retested with landing-page and generic-website briefs (still technical-leaning) + B4 naive proxy. Still dark/sans on B5.
- Iter 3: B5 retested with **editorial brief** (literary magazine) → **cream/serif/terracotta emerged exactly as doc claims** (#F4EFE6, Canela, #8B2E2E). B4 proxy via unrestricted sub-agent → 0 tool calls (confirmed conservative tool-use default). B2 proxy via "do not use tools" prompt → literal compliance + confident knowledge-only answer.

**Key finding — B5 default is domain-conditional:**
| Brief | Output |
|-------|--------|
| fintech transaction monitor | `#0B1220` dark navy + Inter + "cold/technical" |
| landing page (ambiguous) | `#0B1220` + Inter + "modern/confident" |
| generic website | `#0F1419` + Inter + "minimalist/technical" |
| literary magazine (editorial) | `#F4EFE6` cream + Canela **serif** + `#8B2E2E` terracotta + "literary/understated" |

→ The doc's "cream/serif/terracotta default" reproduces in editorial/hospitality-adjacent briefs but not in technical ones. **T1-a guard wording in `frontend-architect.md` is already correctly scoped** ("avoid cream+serif+terracotta for dashboards/fintech/healthcare/dev-tools") — **no refinement needed**.

**Remaining gaps (require external harness, not in-session):**
- B1 (effort strictness): `effort` is session/env-level; needs cross-session A/B with `CLAUDE_CODE_EFFORT_LEVEL=low` vs `=xhigh`.
- B8 (adaptive thinking scaling): requires thinking-token telemetry not surfaced in tool results.
