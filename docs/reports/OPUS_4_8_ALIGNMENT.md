# Opus 4.8 Alignment — Content Audit Checklist
# Last reviewed: 2026-05-30
# Source: docs/features/opus-4-8-alignment/ (02-research.md + 05-plan.md)
# Re-run on every model upgrade. Builds on docs/reports/OPUS_4_7_ALIGNMENT.md (V1/V5/V6/V7 carry forward unchanged).

## How to run

Walk each V# below. Any row with an unexpected result = gap to address. Commands assume repo root.

## V1 (carry 4.7) No CAPS enforcement language in shipped content
Command: `grep -rnE "CRITICAL:|MUST use|You MUST|NEVER " src/superclaude/{agents,commands,modes,core}/`
Expected: 0 matches (documented gotcha-style exceptions noted in OPUS_4_7_ALIGNMENT.md)

## V2 (4.8) Subagent note is model-neutral — no version-pinned spawn claim
Command: `grep -nE "less eager than 4\.6|Opus 4\.7 note" src/superclaude/core/RULES.md`
Expected: 0 matches; `<sub_agent_decision>` still carries the explicit-invocation directive

## V3 (4.8) Effort guidance reflects 4.8 defaults
Command: `grep -nE "baseline|high|xhigh|inherit" .claude/rules/agent-authoring.md`
Expected: "high = default on all surfaces"; xhigh/max framed as "difficult/long-async", NOT "baseline for coding"

## V4 (4.8) Effort-enum SSOT current
Command: `grep -nE "xhigh|default|Opus 4\.6 only" .claude/rules/schemas.yaml`
Expected: `xhigh` present in `effort_values`; `(default)` marks `high`; no "(Opus 4.6 only)" on `max`

## V5 (carry 4.7 + 4.8) No agent hardcodes effort (inherit-only preserved)
Command: `grep -rnE "^\s*effort:" src/superclaude/agents/`
Expected: 0 matches (commit `8edd05d` stance; reinforced by 4.8 `high` default)

## V6 (carry 4.7 V5) Frontend AI-slop guard present
Command: `grep -nE "aesthetics|house style|Forbidden defaults" src/superclaude/agents/frontend-architect.md`
Expected: `<aesthetics>` block present; house-style label is version-neutral (no "Opus 4.7 house style")

## V7 (carry 4.7 V6) Review agents use coverage-first finding language
Command: `grep -l "finding_policy" src/superclaude/agents/{quality-engineer,self-review,security-engineer}.md`
Expected: all 3 match

## V8 (carry 4.7 V7) Thinking references are adaptive-thinking-aware
Command: `grep -rnE "extended thinking|budget_tokens" src/superclaude/core/`
Expected: 0 matches as prescribed default (historical/migration mentions OK)

## V9 (4.8) No residual behavioral version-pins in authoring rules
Command: `grep -rnE "Opus 4\.7 (read|follows|drops)" .claude/rules/xml-prose-format.md`
Expected: 0 — rationale de-pinned to "recent Opus models (4.5+)"

## V10 (4.8) Effort-enum change passes structure tests
Command: `uv run pytest tests/unit/test_agent_structure.py -q`
Expected: pass (the `effort_values` enum is the test-enforced SSOT)

## V11 (gap — deferred) Absolute-token assumptions audit
Method: grep for hardcoded context/output token counts assuming a <1M window (truncation thresholds, `context_loader.py` sizing).
Status: Tier 3, not run this pass. %-based Token Efficiency thresholds already proportional.

---

## Run results 2026-05-30 (after Tier 1 implementation)

| V# | Status | Evidence |
|----|--------|----------|
| V1 | ⏭ carry-forward | unchanged from OPUS_4_7_ALIGNMENT.md; Tier-1 edits added no CAPS language |
| V2 | ✅ pass | `grep "less eager\|Opus 4.7 note" src/superclaude/core/RULES.md` → 0 matches; directive retained |
| V3 | ✅ pass | `agent-authoring.md:92,96` rewritten — "high = default on all surfaces", xhigh/max = "difficult/long-async", no "baseline" |
| V4 | ✅ pass | `schemas.yaml:18-23` — `xhigh` added; `(default)` moved to `high`; `max` now "Opus 4.6+" |
| V5 | ✅ pass | `grep "effort:" src/superclaude/agents/` → 0 occurrences across 0 files |
| V6 | ✅ pass | `<aesthetics>` present at `frontend-architect.md:38-40`; "Opus 4.7 house style" label de-pinned → "a common model default house style" (palette provenance stays in 4.7 B5) |
| V7 | ⏭ carry-forward | unchanged; finding_policy present in 3 review agents per 4.7 V6 |
| V8 | ⏭ carry-forward | unchanged; no budget_tokens in core/ per 4.7 V7 |
| V9 | ✅ pass | `xml-prose-format.md:16,91,287` de-pinned to "recent Opus models (4.5+)" |
| V10 | ✅ pass | `uv run pytest tests/unit/test_agent_structure.py -q` → **722 passed in 1.17s** |
| V11 | ⏭ deferred | Tier 3 — not run |

**Summary:** 7 ✅ pass · 3 ⏭ carry-forward · 1 ⏭ deferred (V11). Tier 1 (T1-a/b/c/d) complete; frontend label de-pinned same pass.

**Regression:** `uv run pytest tests/unit/{test_agent,test_command,test_mode,test_skill}_structure.py -q` → **1368 passed in 2.42s** (covers the `schemas.yaml` SSOT fixture across all content types). Full `tests/unit/` suite hit **Exit 137** (process killed — Windows env OOM/timeout, not a test failure); targeted structure suite stands as Level-1 evidence for the only test-enforced change (effort enum). Re-run full suite in CI / healthy `.venv` to confirm the ~1,904 baseline.

**Tier-1 files changed (this pass):**
- `src/superclaude/core/RULES.md` — T1-a, subagent note de-pinned (shipped)
- `.claude/rules/xml-prose-format.md` — T1-b, declarative-voice rationale de-pinned ×3 (not shipped)
- `.claude/rules/agent-authoring.md` — T1-c, effort guidance corrected ×2 (not shipped)
- `.claude/rules/schemas.yaml` — T1-c, effort enum reconciled (+`xhigh`; not shipped)
- `docs/reports/OPUS_4_8_ALIGNMENT.md` — T1-d, this artifact

**Deferred (Tier 2/3, unchanged from plan):** subagent spawn-eagerness eval (T2-a), compaction-drift threshold (T2-b), absolute-token audit (V11), behavioral Part B suite.
