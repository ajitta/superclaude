---
status: implementing
revised: 2026-05-30
---

# Opus 4.8 Alignment — Plan

**Source:** `./02-research.md` (Opus 4.8 behavior + 4.7 diff, evidence-backed).
**Precedent:** mirrors `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` tier structure and `docs/reports/OPUS_4_7_ALIGNMENT.md` verification format.
**Scope (R06):** content/authoring-rule edits + a re-runnable audit artifact. **No** new agents/modes/commands, **no** code changes, **no** runtime/SDK config. Behavioral tests are documented as a checklist, not executed here (cross-session harness required — see 4.7 run results B1/B8).
**Gate:** This is a `draft`. Per `<workflow_gates>` `/sc:plan → /sc:implement --plan`, do not implement before user approval.

**Guiding principle:** 4.8 *reinforces* almost every existing SuperClaude decision (model-agnostic content, inherit-only effort, coverage-first review). The only justified edits are **version-pinned claims** that now misrepresent a stable multi-version trait as 4.6/4.7-specific. Fix by **version-neutralizing** (not 4.7→4.8 stamping, which re-stales in ~41 days), consistent with the model-agnostic design spec.

---

## 1. Current-state audit (4.8-relevant)

Anchors verified by grep on `master`, 2026-05-30.

| # | Item | Location | State under 4.8 |
|---|---|---|---|
| C1 | Subagent note pinned to "Opus 4.7 / less eager than 4.6" | `src/superclaude/core/RULES.md:16` | ⚠️ behaviorally stale — 4.8 improves tool triggering |
| C2 | Declarative-voice rationale pinned to "Opus 4.7" | `.claude/rules/xml-prose-format.md:16,91,287` | ⚠️ trait is multi-version (4.5+), reinforced by 4.8 |
| C3 | Effort guidance "xhigh = coding/agentic baseline" | `.claude/rules/agent-authoring.md:92,96` | ❌ outdated — 4.8 default is `high` (best balance); xhigh/"extra" is for *difficult/long-async*, not blanket baseline |
| C4 | Effort enum stale: `max` "Opus 4.6 only", `medium` "(default)", **`xhigh` missing** | `agent-authoring.md:92`, `schemas.yaml:18-22` | ❌ 4.8 supports max, default is `high`; `xhigh` absent from SSOT yet documented valid → would fail tests |
| C5 | No `effort:` field on any agent (inherit-only) | `src/superclaude/agents/*` (commit `8edd05d`) | ✅ validated by 4.8 (high default) |
| C6 | Adaptive-thinking line model-neutral | `src/superclaude/core/PRINCIPLES.md:25` | ✅ correct, no change |
| C7 | No CAPS enforcement / aggressive prompting | agents/commands/modes/core | ✅ from 4.6 work, still correct (4.7 V1) |
| C8 | Frontend AI-slop guard, review `<finding_policy>` | `frontend-architect.md`, 3 review agents | ✅ from 4.7 work, *more* effective under 4.8 |
| C9 | Model-string examples `'claude-opus-4-7'` | 6 authoring rules + `agent-authoring.md:34` | 🟢 cosmetic illustration of quote convention — not broken |
| C10 | Token Efficiency `--uc` thresholds (%-based) | `MODE_Token_Efficiency.md`, `FLAGS.md` | ✅ proportional, valid at 1M |
| C11 | `compaction-drift` gotcha "~50 turns" | `.claude/rules/gotchas/general.md` | ⚠️ safety practice — measure before relaxing |

## 2. Tier 1 — ship (durable, low-risk)

### T1-a — De-pin the subagent-spawn note (`RULES.md:16`)
- **Why:** The note's version label ("Opus 4.7 … less eager than 4.6") is two versions stale; 4.8 explicitly improves tool triggering (docs "Behavior changes"; Devin tester quote). The residual advice (prefer explicit invocation when delegation criteria are met) is model-independent and stays.
- **What:** Replace the version-pinned clause with model-neutral phrasing, e.g. *"Recent Opus models may not auto-spawn subagents even when criteria are met — prefer explicit invocation (direct Agent call or `--delegate auto`) rather than assuming auto-spawn. Spawn-eagerness under 4.8 not yet measured (see plan T2-a); threshold numbers unchanged pending eval."*
- **R18:** Borderline-broken — the label misleads a reader into thinking the guidance is 4.6/4.7-specific. Minimal one-clause edit. ✅
- **Blast radius:** 1 line, core content (shipped). Verification Level 1.

### T1-b — De-pin the declarative-voice rationale (`xml-prose-format.md:16,91,287`) — optional (low user-impact)
- **Why:** Literal-instruction-following is a trait shared by Opus 4.5→4.8 and *improved* in 4.8 ("more reliable behavior", "follows instructions with consistency"). Pinning the rationale to "Opus 4.7" makes a stable design principle look version-specific.
- **What:** "Opus 4.7 read instructions literally / drops hedging" → "recent Opus models (4.5+) read instructions literally". Keep the URL reference and the rule itself unchanged.
- **R18:** Author-facing meta-doc (not shipped — `install-tree-boundary`). Low user impact but the rationale is load-bearing for authors; de-pinning prevents future churn. ✅ (low priority within T1)
- **Blast radius:** 3 lines, `.claude/rules/` (not shipped). Verification Level 0 (text-only).

### T1-c — Correct effort guidance + reconcile effort-enum SSOT (`agent-authoring.md:92,96` + `schemas.yaml:18-22`) — highest-value edit
- **Why:** `:96` states "Anthropic recommend `xhigh` as baseline for coding/agentic work." 4.8 supersedes this: `high` is the all-surface default and "best overall balance"; "extra"/`xhigh` and "max" are for *difficult tasks and long-running async workflows*. The old text would push authors to over-spend tokens against a well-tuned default. Separately, `schemas.yaml` — the effort-enum SSOT enforced by `test_agent_structure.py` — is stale (`medium` marked default, `max` marked "Opus 4.6 only") and self-inconsistent with the authoring doc (`xhigh` documented valid but absent from the enum, so `effort: xhigh` would fail validation).
- **What:**
  - `agent-authoring.md:96` → "Opus 4.8 defaults to `high` on all surfaces (best quality/UX balance). Reserve `xhigh` ('extra') / `max` for difficult tasks or long-running async work — not as a blanket coding baseline. Still omit `effort:` by default (inherit); set explicitly only with measured evidence."
  - `agent-authoring.md:92` → update availability: `xhigh`/`max` available on Opus 4.8 (and 4.6/4.7 per prior gates). Keep CC-version gates accurate.
  - `schemas.yaml:18-22` → (a) move the `(default)` marker from `medium` to `high`; (b) drop `max`'s "(Opus 4.6 only)" — 4.8 supports max; (c) **add `xhigh`** to `effort_values` (between `high` and `max`) to reconcile the SSOT with `agent-authoring.md` and CC support (v2.1.111+).
- **R18:** Outdated recommendation that actively misguides authors **+** an SSOT/doc contradiction that would reject a valid `effort: xhigh` → fix. ✅
- **Blast radius:** 2 files, both `.claude/rules/` (not shipped). Adding `xhigh` to the enum is **test-enforced** → **Verification Level 1**: run `tests/unit/test_agent_structure.py`. Cross-check C5 (no agent should gain an `effort:` field as a result).

### T1-d — Create `docs/reports/OPUS_4_8_ALIGNMENT.md` audit checklist
- **Why:** The 4.7 work left a re-runnable living checklist; the brief explicitly asks to *track* improvements. This is the tracking artifact.
- **What:** Clone V1–V10 from `OPUS_4_7_ALIGNMENT.md` (they remain valid), add 4.8-specific checks VA2/VA3/VA4 below, and a "Run results" section to fill after implementation.
- **R18:** Directly fulfills the "track" requirement; re-runnable on the next model upgrade. ✅

## 3. Tier 2 — measure / decide (defer change until evidence)

- **T2-a — Subagent spawn eagerness under 4.8.** Open question from research §4: "works independently longer" could mean *more self-work* or *more delegation*. Inherits the 4.7 deferred item (T2-b). **Test before** changing any `<sub_agent_decision>` threshold numbers. Harness-limited (see 4.7 B4 — not observable from a sub-agent).
- **T2-b — Compaction-drift threshold.** 4.8 claims "better compaction recovery / fewer derailments." Measure whether the "~50 turns" re-read-rules practice can be relaxed. Do **not** weaken a safety practice on a vendor claim alone (R18; "do NOT simplify safety").
- **T2-c — Confirm inherit-only effort.** Mostly verification + documentation: assert no agent ships `effort:` (grep VA4), and record in `agent-authoring.md` that 4.8's `high` default validates inherit-only. No behavioral change.

## 4. Tier 3 — monitor / out-of-scope

- **Dynamic workflows** (CC research preview; Enterprise/Team/Max): plans + runs hundreds of parallel subagents, verifies, reports. Overlaps `--delegate`/`--orchestrate`/`--task-manage`. **Monitor**; revisit at GA — do not redesign delegation around a preview feature.
- **Mid-conversation system messages + 1,024-tok cache minimum:** SDK/harness, not content. Possible future `context_loader.py`/hook optimization (inject mode/MCP context as system entries; smaller injections now cacheable). **Monitor.**
- **1M context vs Token Efficiency thresholds:** %-based → no change; note absolute budget is larger.
- **Absolute-token assumptions audit:** grep for hardcoded context/output token counts that assume a <1M window (truncation thresholds, `context_loader.py` sizing, the `cc-truncation-thresholds` memory). Audit + note only; %-based thresholds already covered (C10).
- **Cosmetic version-string sweep** (`'claude-opus-4-7'` → `'claude-opus-4-8'` across 6 authoring files + `agent-authoring.md:34` ID example): **skip** — pure quote-convention illustrations, version-irrelevant, re-stales in ~41 days (R18 — not broken). *(The `schemas.yaml` effort-enum staleness, originally lumped here, was promoted to T1-c — it is enforced config, not illustration.)*

## 5. Explicitly deferred / out-of-scope

- Benchmark figures as fact (69.2% / 57.9% / 4×) — secondary-source; confirm against system card before any quote (research §7).
- Effort control in claude.ai/Cowork, fast-mode pricing, Messages API code — runtime/SDK, not CLAUDE.md content (matches 4.7 D2/D10 deferrals).
- Model identity prompt — framework stays model-agnostic by design (2026-03-23 spec; 4.7 T3-c).
- `frontend-architect.md:39` "Opus 4.7 house style" label — ✅ de-pinned 2026-05-30 to "a common model default house style" (palette provenance kept in 4.7 B5); completes the shipped-content version-pin sweep.

## 6. Verification checklist

### Part A — content audit (run after implementation)

```
[ ] VA1 No stale behavioral version-pins remain
        grep -rn "Opus 4\.7\|less eager\|4.7 note" src/superclaude/core/RULES.md .claude/rules/xml-prose-format.md
        Expected: behavioral-rationale lines de-pinned (historical/migration/URL mentions OK)
[ ] VA2 Subagent note model-neutral
        grep -n "auto-spawn\|explicit invocation" src/superclaude/core/RULES.md
        Expected: guidance present, no "less eager than 4.6" version claim
[ ] VA3 Effort guidance reflects 4.8 (high default; xhigh for hard/async)
        grep -n "high\|xhigh\|baseline\|inherit" .claude/rules/agent-authoring.md
        Expected: "high = default", "xhigh for difficult/long-async", no "xhigh as baseline"
[ ] VA3b Effort-enum SSOT current (xhigh present; comments fixed)
        grep -n "xhigh\|default\|max" .claude/rules/schemas.yaml
        Expected: xhigh in effort_values; no "(Opus 4.6 only)"; (default) marks high not medium
[ ] VA4 No agent hardcodes effort (inherit-only preserved)
        grep -rn "effort:" src/superclaude/agents/
        Expected: 0 matches
[ ] VA5 Carry-forward 4.7 checks still pass
        V1 no CAPS enforcement; V5 frontend aesthetics; V6 finding_policy ×3; V7 no budget_tokens in core/
        Expected: unchanged from OPUS_4_7_ALIGNMENT.md
[ ] VA6 Audit artifact exists and is linked
        test -f docs/reports/OPUS_4_8_ALIGNMENT.md ; linked from this feature README
```

### Part B — behavioral (cross-session harness; not in-session per 4.7 limits)

*Gate: Tier 1 (T1-a/b/c/d) ships independent of Part B. Part B results are recorded in `OPUS_4_8_ALIGNMENT.md` and gate only the Tier-2 threshold decisions (T2-a/T2-b), not the Tier-1 edits.*

```
[ ] B1 Subagent spawn eagerness 4.8 (T2-a) — does 4.8 auto-spawn for 3+ independent streams?
[ ] B2 Tool triggering — does 4.8 skip fewer required tool calls than 4.7? (docs claim)
[ ] B3 Literal instruction following still holds (4.7 B3 passed) — "first section" vs "every section"
[ ] B4 Compaction-drift threshold under 4.8 (T2-b) — does rule-adherence survive past ~50 turns?
[ ] B5 Code-review coverage delta with <finding_policy> (4.7 B6 = 3.8×) — re-confirm under 4.8
```

### Part C — regression (after implementation, future /sc:implement step)

```
[ ] R1 uv run pytest tests/unit/test_agent_structure.py   Expected: pass — schemas.yaml enum change (+xhigh) is test-enforced
[ ] R2 uv run pytest tests/unit/        Expected: ~1,904 pass, baseline otherwise unchanged
[ ] R3 make deploy && superclaude install --list-all   Expected: success
[ ] R4 grep -r "{{.*PATH" src/superclaude/   Expected: all resolve at install
```

## 7. Open decisions (R12 — non-blocking; proceeding on stated defaults, redirect welcome)

1. **T1-b priority:** ✅ resolved 2026-05-30 — **included** in this iteration (de-pin xml-prose-format rationale).
2. **Effort-enum / version sweep:** ✅ resolved 2026-05-30 — illustration-string sweep **skipped** (Tier 3); `schemas.yaml` effort-enum staleness **promoted to T1-c**, including **adding `xhigh`** to `effort_values`.
3. **Folder vs content naming:** folder is `opus-4-8-alignment` (tracks the triggering release, matches the 4.6→4.7→4.8 chain for discoverability) while the content pushes version-neutral phrasing. Acceptable, or prefer a model-agnostic feature slug (4.7 Q5)? *Default: keep — folder names an event, content states the principle.*

## 8. Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| De-pinning RULES.md note loosens delegation guidance | Low | Medium | Keep the explicit-invocation directive verbatim; only the version label changes |
| Effort-guidance rewrite makes authors set `effort:` again | Low | Medium | VA4 asserts 0 `effort:` fields; T1-c keeps "omit by default" |
| Weakening compaction-drift practice on vendor claim | Low | High | T2-b gates change behind measurement; safety practice stays until evidence |
| Audit checklist re-stales next release | High | Low | Version-neutral checks where possible; re-run on each upgrade (same as 4.7) |
| Treating dynamic-workflows preview as stable → premature delegation redesign | Medium | Medium | Tier 3 monitor only; no edits until GA |

## 9. Recommended next steps (pending approval)

1. Self-review + verify these docs (this session).
2. On approval: `/sc:implement --plan` Tier 1 (T1-a/b/c/d) as a `docs/`-or-`refactor:`-branch (content + meta-docs only).
3. Run Part A verification; record results in `docs/reports/OPUS_4_8_ALIGNMENT.md`.
4. Schedule Part B behavioral tests when a cross-session harness is available (T2-a/b).
