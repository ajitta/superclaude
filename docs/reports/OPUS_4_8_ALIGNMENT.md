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

## V11 (4.8 Tier 3) Absolute-token assumptions audit
Method: grep for hardcoded context/output token counts assuming a <1M window (truncation thresholds, `context_loader.py` sizing).
Expected: every numeric threshold is window-independent in rationale (ratio / per-operation conservation / attention-budget cap) or env-overridable — no value scales off a <1M total-window assumption.

## V12 (4.8 Tier 2-c) Inherit-only effort validated by 4.8 `high` default
Command: `grep -rnE "^\s*effort:" src/superclaude/agents/` + read `agent-authoring.md` effort section
Expected: 0 `effort:` fields (inherit-only intact); authoring doc states 4.8 `high` default + omit-by-default + cost-control-with-user. No edit if already current.

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
| V11 | ✅ audited (no action) | See V11 findings below — no <1M-window hardcoded assumption to fix |
| V12 | ✅ pass | `grep "^\s*effort:" src/superclaude/agents/` → 0 across 0 files; `agent-authoring.md:92,96,100` already states 4.8 `high` default + omit-by-default + cost-control. No edit (R18 — not broken) |

**Summary:** 9 ✅ pass/audited · 3 ⏭ carry-forward. Tier 1 (T1-a/b/c/d) complete; frontend label de-pinned same pass; V11 absolute-token audit + V12 inherit-only confirmation run 2026-05-30 (Tier 2-c / Tier 3 in-session slice).

## V11 findings 2026-05-30 — absolute-token audit

Audited every numeric token/size constant in framework source for a <1M-window assumption. None found that needs changing — each threshold is window-independent in rationale or env-overridable:

| Location | Constant | Classification | Verdict |
|----------|----------|----------------|---------|
| `scripts/token_estimator.py:15` | `CHARS_PER_TOKEN = 4` | char→token ratio | window-independent ✅ |
| `scripts/file_size_guard.py:20,23` | `SIZE_THRESHOLD = 30_000`, `SMALL_FILE_THRESHOLD = 5_000` (bytes) | per-file Read guard (per-operation conservation, not budget allocation) | window-independent ✅ — one 30KB Read flooding context is undesirable regardless of total window; `SUPERCLAUDE_SIZE_GUARD=0` opt-out |
| `scripts/context_loader.py:46` | `MAX_TOKENS_ESTIMATE = 8000` | attention-budget cap on on-demand TRIGGER_MAP injection ("minimize attention dilution", `:271`) | window-independent ✅ — rationale is signal-to-noise, not window capacity; env-overridable via `CLAUDE_CONTEXT_MAX_TOKENS` |
| `MODE_Token_Efficiency.md`, `FLAGS.md` | `--uc` thresholds (≥60%, ≥85%) | %-based | already proportional (C10) ✅ |
| `cc-truncation-thresholds` memory | skill 1024/250자, available_skills ~15K, MEMORY 200줄, Bash 30K | **CC-native harness limits, not framework code** | out of scope — not editable by SuperClaude; verified facts, no <1M dependency |

**Conclusion:** The 1M default window enlarges absolute budgets but does not invalidate any framework threshold. Attention-budget caps (8K injection) and per-op Read guards (30KB) are deliberately *not* scaled to window size — bigger window ≠ dump more in. No code change. Re-audit only if a future constant is introduced that divides a fixed fraction of total window.

**Regression:** `uv run pytest tests/unit/{test_agent,test_command,test_mode,test_skill}_structure.py -q` → **1368 passed in 2.42s** (covers the `schemas.yaml` SSOT fixture across all content types). Full `tests/unit/` suite hit **Exit 137** (process killed — Windows env OOM/timeout, not a test failure); targeted structure suite stands as Level-1 evidence for the only test-enforced change (effort enum). Re-run full suite in CI / healthy `.venv` to confirm the ~1,904 baseline.

**Tier-1 files changed (this pass):**
- `src/superclaude/core/RULES.md` — T1-a, subagent note de-pinned (shipped)
- `.claude/rules/xml-prose-format.md` — T1-b, declarative-voice rationale de-pinned ×3 (not shipped)
- `.claude/rules/agent-authoring.md` — T1-c, effort guidance corrected ×2 (not shipped)
- `.claude/rules/schemas.yaml` — T1-c, effort enum reconciled (+`xhigh`; not shipped)
- `docs/reports/OPUS_4_8_ALIGNMENT.md` — T1-d, this artifact

**Deferred (harness-blocked — need cross-session / 50+-turn observation, not single-pass measurable):** subagent spawn-eagerness eval (T2-a / Part B B1-B2), compaction-drift threshold past ~50 turns (T2-b / Part B B4), literal-instruction + review-coverage re-confirm (B3/B5). These gate only the Tier-2 *threshold* decisions, not any shipped edit. Record results here when a cross-session harness runs them.

**Closed this pass (Tier 2-c + Tier 3 in-session slice):** absolute-token audit (V11 — no action), inherit-only effort confirmation (V12 — verify-only, doc already current).
