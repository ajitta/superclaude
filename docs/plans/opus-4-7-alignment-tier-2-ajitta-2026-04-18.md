---
status: implemented
revised: 2026-04-18
---

# Opus 4.7 Alignment — Tier 2 Implementation Plan

## Execution Log (2026-04-18)

| Task | Status | Evidence |
|------|--------|----------|
| 1. agent-authoring.md enum fix + xhigh guidance | ✅ done | Line 22 now reads `effort: low\|medium\|high\|xhigh\|max`; new guidance block lands at line 49 (`When \`xhigh\` is worth setting`) |
| 2. RULES.md `<sub_agent_decision>` 4.7 note | ✅ done | `grep "Opus 4.7" src/superclaude/core/RULES.md` → line 17 match inside the block |
| 3. Checklist V4 flip + Tier 2 run results | ✅ done | V4 `⚠️ deferred` → `✅ pass (doc-level)`; Tier 2 run-results table appended |
| 4. Spec `revised:` bump | ✅ noop | Frontmatter already `revised: 2026-04-18` (Tier 1 day) — no change needed |
| 5. Full regression suite | ✅ pass | `uv run -- python -m pytest tests/unit/ -q` → **1684 passed, 0 failed** (identical to Tier 1 baseline) |
| 6. Part A verification re-walk | ⚠️ 1 pre-existing finding | V2–V10 all pass; V1 surfaced 1 pre-existing match at `commands/insight.md:107` (commit `b5c974f3`, 2026-04-11 — pre-Tier-1). Scope-gate prevents inline fix; flagged as follow-up |
| 7. Commit | ⏸ awaiting user approval | CLAUDE.md requires explicit "commit" before staging |

**Regression delta:** 0 new failures · 0 new errors · 1684 pass (net +0, matches Tier 1 baseline exactly).

**New finding surfaced during Tier 2 verification:**
- V1 `NEVER ` grep now matches `src/superclaude/commands/insight.md:107` (pre-existing; missed in Tier 1's V1 walk). Context is a tool-safety gotcha about `Write` overwriting JSONL files, not aggressive enforcement prompting. User decision needed:
  - (a) reword `NEVER use Write tool` → `Do not use Write tool` at insight.md:107 (1-word edit, in-spirit-of-V1)
  - (b) refine the V1 grep in the checklist to exclude gotcha-style `NEVER use X tool` warnings
  - (c) accept as a documented V1 exception

**Behavioral verification status (Korean directive — 시물레이션/측정):**
- T2-a (xhigh guidance): verifiable by grep — ✅ done
- T2-b (sub_agent 4.7 under-spawn note): doc-level change is verifiable by grep (✅ done); the underlying *behavioral claim* ("4.7 under-spawns vs 4.6") is Part B work (spec §5) — requires identical multi-stream prompts run under 4.6 vs 4.7 and delegation-count comparison. **Not run in this session** — Part B is explicitly deferred per spec §6 Q3 to manual user sessions + `/sc:insight` capture
- Recommendation: trigger a Part B smoke test by issuing a known 3-stream research prompt (e.g., "Research React 19 + Vue 4 + Svelte 5") in a follow-up session under Opus 4.7 and observing whether the model auto-delegates vs runs serially. Capture with `/sc:insight`.

---


**Goal:** Close the two Tier 2 gaps identified in the Opus 4.7 alignment spec — (T2-a) document when to consider `effort: xhigh` for coding-heavy sessions (Option 3 from spec: guidance in `agent-authoring.md`, not per-agent frontmatter changes), and (T2-b) add a lightweight doc-only note to `<sub_agent_decision>` about Opus 4.7's reduced spawn rate. Flip Part A checklist V4 from ⚠️ deferred to ✅ (doc-level).

**Architecture:** Pure content framework edits — 2 source files modified, 1 checklist artifact updated. No Python, no schema, no new tests, no per-agent frontmatter changes. Regression coverage provided by existing `tests/unit/test_agent_structure.py` and `test_content_structure.py`.

**Tech Stack:** Markdown + XML (SuperClaude agent format) · pytest regression · ripgrep for Part A verification

**Spec:** `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` (status: approved)
**Prior work:** `docs/plans/opus-4-7-alignment-tier-1-ajitta-2026-04-18.md` (status: implemented)

**Scope decisions (§6 of spec):**
- **Q1 — Tier 2 scope:** commit to both T2-a and T2-b now, both at documentation level (smallest reversible intervention)
- **Q2 — T2-a which agents:** N/A — Option 3 chosen (no per-agent `effort:` additions); guidance lives in authoring rules
- **T2-a approach:** Option 3 from spec — document when `xhigh` is worth setting; preserve inherit-by-default policy from commit `8edd05d`
- **T2-b approach:** documentation-only note inside `<sub_agent_decision>`. R18 Necessity Test: user-facing failure scenario is documented (D6 — 4.7 under-spawns, serialised research costs time and context). Heavier rule rewrites remain deferred until we have eval data on `--delegate auto` trigger rate under 4.7

---

## File Map

| File | Action | Lines affected | Purpose |
|------|--------|----------------|---------|
| `.claude/rules/agent-authoring.md` | Modify | `22`, insert after `45` | Fix effort enum example (missing `xhigh`) + add xhigh-guidance block |
| `src/superclaude/core/RULES.md` | Modify | insert after `16` (inside `<sub_agent_decision>`, before `<examples>` on line 17) | One-line 4.7 under-spawn note |
| `docs/reports/OPUS_4_7_ALIGNMENT.md` | Modify | V4 section + Run results table | Flip V4 from ⚠️ deferred to ✅ doc-only |
| `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` | Modify | frontmatter `revised:` | Bump `revised:` only (status already `approved`) |

---

## Tasks

### Task 1: Fix effort enum example + add xhigh guidance (T2-a)

**Files:** Modify: `.claude/rules/agent-authoring.md` (line 22; insert block after line 45)
**Test:** `uv run pytest tests/unit/ -q` (no structure test gates this file; regression-only)

**Sub-step 1a — Fix enum example on line 22.** The YAML example currently omits `xhigh`, contradicting the valid-values list on line 43.

- Before: `effort: low|medium|high|max                # optional | omit by default; inherit from parent (v2.1.69+)`
- After:  `effort: low|medium|high|xhigh|max          # optional | omit by default; inherit from parent (v2.1.69+); xhigh requires CC 2.1.111+`

**Sub-step 1b — Insert xhigh-when-to-use guidance.** Insert after the existing "Precedence:" line (currently line 47 pre-edit: `Precedence: CLAUDE_CODE_EFFORT_LEVEL env > frontmatter > session > model default.`), before the `**\`maxTurns\`** — turn-limit safety net:` heading.

Block to insert (keep one blank line above and one below):

```markdown
**When `xhigh` is worth setting (Opus 4.7+):** Anthropic's prompting guidance recommends `xhigh` as the baseline for coding and agentic work — at `low`/`medium`, Opus 4.7 tends to under-think edge cases. Two safe paths:

1. **Session-level (preferred):** set `CLAUDE_CODE_EFFORT_LEVEL=xhigh` or choose `xhigh` at session start — applies uniformly to all agents and honors the user's cost-vs-quality choice.
2. **Agent-level override:** add `effort: xhigh` to a specific agent's frontmatter **only** when you have measured a quality regression for that agent at the session default.

Do not add `effort: xhigh` to an agent just because the domain "feels" coding-heavy — the session default covers that case. The framework's inherit-by-default policy (commit `8edd05d`) is intentional: it keeps cost control with the user, not the agent author.
```

**Checklist:**
- [ ] Step 1: Verify baseline — `uv run pytest tests/unit/ -q` passes (baseline count)
- [ ] Step 2: Edit line 22 to add `xhigh` to the enum and CC version note
- [ ] Step 3: Locate insertion point — `grep -n "^Precedence: " .claude/rules/agent-authoring.md` (should match line 47 pre-edit)
- [ ] Step 4: Insert the guidance block after the Precedence line with one blank line above and below
- [ ] Step 5: Grep verification — `grep -n "When \`xhigh\` is worth setting" .claude/rules/agent-authoring.md` returns 1 match
- [ ] Step 6: Grep verification — `grep -n "low|medium|high|xhigh|max" .claude/rules/agent-authoring.md` returns 1 match
- [ ] Step 7: Re-run full suite — no new failures

---

### Task 2: Add 4.7 under-spawn note to `<sub_agent_decision>` (T2-b)

**Files:** Modify: `src/superclaude/core/RULES.md` (insert after line 16 `Never sub-agent:`, before line 17 `<examples>`)
**Test:** `uv run pytest tests/unit/test_content_structure.py -v`

Current block (lines 13-27; confirmed with `grep -nE "(<sub_agent_decision>|Never sub-agent|<examples>)"`: 13/16/17):

```xml
  <sub_agent_decision>
  Direct work: single file edit, <3 steps, sequential dependency, simple search, context already loaded
  Sub-agent: 3+ independent parallel streams, different expertise domains, >20K tokens exploration, isolated failure OK
  Never sub-agent: tasks needing recent conversation context, sequential A→B, completable in <30s directly
  <examples>
  ...
  </examples>
  </sub_agent_decision>
```

Insert this one-line guidance between the `Never sub-agent:` line and the `<examples>` tag:

```
  Opus 4.7 note: This model spawns subagents less eagerly than 4.6 — when the Sub-agent criteria above are met, prefer explicit invocation (direct Agent tool call or `--delegate auto`) rather than assuming the model will auto-spawn.
```

**R18 Necessity Test (explicit):**
- Broken without it? Yes — the spec's own example ("Research React 19 + Vue 4 + Svelte 5") degrades from 3 parallel streams to serial under 4.7's under-spawn default
- Quantitative evidence? Anthropic D6 source guidance: "4.7 spawns fewer subagents by default — add explicit guidance when you want more"
- Specific failure scenario? Yes — independent-stream tasks run serially, tripling wall-clock time and context pressure
- User-facing impact? Yes — slower and more expensive research sessions

Verdict: ✅ doc-only note passes R18. A rule rewrite (changing thresholds) still fails R18 pending eval data and remains out of scope.

**Checklist:**
- [ ] Step 1: Verify baseline — `uv run pytest tests/unit/test_content_structure.py -v` passes
- [ ] Step 2: Confirm insertion point — `grep -nE "(Never sub-agent|<examples>)" src/superclaude/core/RULES.md | head -3` shows `Never sub-agent:` on line 16 and `<examples>` on line 17 pre-edit
- [ ] Step 3: Insert the one-line note immediately after line 16 (`Never sub-agent:…`) and before line 17 (`<examples>`), preserving 2-space indent
- [ ] Step 4: Grep verification — `grep -n "Opus 4.7" src/superclaude/core/RULES.md` returns ≥1 match inside `<sub_agent_decision>`
- [ ] Step 5: Re-run content structure test — expect pass (no tag/structure change, only content addition)
- [ ] Step 6: Re-run agent structure test (RULES.md is not an agent, but smoke-run the suite) — expect pass

---

### Task 3: Update Part A checklist V4 + add Tier 2 run results

**Files:** Modify: `docs/reports/OPUS_4_7_ALIGNMENT.md` (V4 section; Run results table)
**Test:** None (checklist is a reference artifact; not installed to `~/.claude/`)

**Sub-step 3a — Replace V4 section.** Current V4 reads:

```markdown
## V4 (D6) Subagent guidance reflects 4.7's lower-spawn default
Search: `src/superclaude/core/RULES.md` <sub_agent_decision>
Expected: note about explicit invocation for 3+ independent streams under Opus 4.7
Known state: **deferred to Tier 2 (T2-b)** — current rules are written for 4.6 over-spawning. Track as open gap until eval data supports the fix.
```

Replace with:

```markdown
## V4 (D6) Subagent guidance reflects 4.7's lower-spawn default
Command: `grep -n "Opus 4.7" src/superclaude/core/RULES.md`
Expected: ≥1 match inside `<sub_agent_decision>` referencing explicit invocation for 3+ independent streams
Known state: Doc-level note added in Tier 2 (commit `<HASH>`). Behavioral-threshold rewrite (changing Sub-agent criteria numbers) remains deferred pending eval data on `--delegate auto` trigger rate under Opus 4.7.
```

**Sub-step 3b — Update the Run results table.** After the existing `## Run results 2026-04-18 (initial run after Tier 1 implementation)` section, append a new section:

```markdown
## Run results 2026-04-18 (after Tier 2 implementation)

| V# | Status | Evidence |
|----|--------|----------|
| V1 | ✅ pass | unchanged from Tier 1 |
| V2 | ✅ pass | unchanged from Tier 1 |
| V3 | ⏭ manual review pending | unchanged — scheduled for next framework audit |
| V4 | ✅ pass (doc-level) | `grep "Opus 4.7" src/superclaude/core/RULES.md` matches inside `<sub_agent_decision>`; threshold rewrite still deferred pending eval |
| V5 | ✅ pass | unchanged from Tier 1 |
| V6 | ✅ pass | unchanged from Tier 1 |
| V7 | ✅ pass | unchanged from Tier 1 |
| V8 | ✅ (pre-existing) | unchanged |
| V9 | ✅ (pre-existing) | unchanged |
| V10 | ✅ (pre-existing) | unchanged |

**Summary:** 9 ✅ pass · 1 ⏭ pending manual (V3). Tier 2 complete; only V3 remains for a future framework-rule audit.
**Regression:** `uv run -- python -m pytest tests/unit/` → <record count after Task 5>
```

**Sub-step 3c — Bump `# Last reviewed:` header** at the top of the file from `2026-04-18` to `2026-04-18` (same date — only update if the date has changed; keep as-is if still 2026-04-18 local).

**Checklist:**
- [ ] Step 1: Replace V4 section per 3a
- [ ] Step 2: Append Tier 2 run-results table per 3b
- [ ] Step 3: Verify — `grep -n "Tier 2 implementation" docs/reports/OPUS_4_7_ALIGNMENT.md` returns 1 match
- [ ] Step 4: The `<HASH>` placeholder in the V4 known-state note will be filled after Task 7 (commit); tolerate `<HASH>` in checklist until then

---

### Task 4: Bump spec `revised:` date

**Files:** Modify: `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` (frontmatter `revised:`)
**Test:** None

- [ ] Step 1: Change `revised:` to today (`2026-04-18` — unchanged if run same day as Tier 1)
- [ ] Step 2: Leave `status: approved` as-is (already approved after Tier 1 plan landed)
- [ ] Step 3: Optional — add a one-line note under §7 "Recommended Next Steps" marking Tier 2 as implemented, mirroring how §5/§7 treated Tier 1

---

### Task 5: Run full regression suite

**Files:** none (test execution)
**Test:** `uv run pytest tests/unit/ -v`

- [ ] Step 1: Run — `uv run pytest tests/unit/ -v`
- [ ] Step 2: Compare pass count to Tier 1 baseline recorded in that plan (`1684 passed, 0 failed`)
- [ ] Step 3: Expected: same 1684 pass, 0 new failures (changes are content-only, not tag-structure-altering)
- [ ] Step 4: If failure: stop, diagnose per R03/R15 — do not proceed to verification until resolved

---

### Task 6: Run Part A verification checklist (post-change)

**Files:** none (verification)
**Test:** walk through `docs/reports/OPUS_4_7_ALIGNMENT.md`

- [ ] Step 1: V1 — `grep -rnE "CRITICAL:|MUST use|You MUST|NEVER " src/superclaude/{agents,commands,modes,core}/` → expect 0 (unchanged from Tier 1)
- [ ] Step 2: V2 — `grep -rnE "(If in doubt|by default) use" src/superclaude/agents/` → expect soft-language-only (unchanged)
- [ ] Step 3: V3 — manual review still pending; carry forward as ⏭
- [ ] Step 4: V4 — **new expected pass** — `grep -n "Opus 4.7" src/superclaude/core/RULES.md` returns ≥1 match inside `<sub_agent_decision>`
- [ ] Step 5: V5, V6, V7 — unchanged from Tier 1; confirm stable
- [ ] Step 6: V8, V9, V10 — pre-existing rules; confirm presence
- [ ] Step 7: Record final results into the Tier 2 run-results table in the checklist (replace `<record count after Task 5>` with actual pytest count)

---

### Task 7: Commit with conventional message

**Files:** git

- [ ] Step 1: `rtk git status` — expected change set: 3 modifications + 1 plan creation
  - modified: `.claude/rules/agent-authoring.md`
  - modified: `src/superclaude/core/RULES.md`
  - modified: `docs/reports/OPUS_4_7_ALIGNMENT.md`
  - modified: `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` (frontmatter)
  - new:      `docs/plans/opus-4-7-alignment-tier-2-ajitta-2026-04-18.md`
- [ ] Step 2: Stage by specific file name (no `git add -A`)
- [ ] Step 3: Commit with message (HEREDOC; include Co-Authored-By per CLAUDE.md):
  ```
  docs(core,authoring): align with Opus 4.7 prompting defaults (Tier 2)

  - agent-authoring.md: document when xhigh effort is worth setting (Option 3 — guidance only, no per-agent frontmatter changes; preserves inherit-by-default from commit 8edd05d)
  - RULES.md <sub_agent_decision>: one-line note on 4.7's reduced spawn rate (doc-only; threshold rewrite still deferred pending eval)
  - checklist V4 flips from ⚠️ deferred to ✅ doc-level
  - spec revised: date bumped

  Spec: docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md
  Plan: docs/plans/opus-4-7-alignment-tier-2-ajitta-2026-04-18.md

  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
  ```
- [ ] Step 4: After commit lands, edit the checklist to replace `<HASH>` placeholder in V4 known-state with the short SHA (amend-safe alternative: next commit)
- [ ] Step 5: Verify — `rtk git log --oneline -3`

---

## Verification Summary (post-implementation)

Expected end-state evidence:

| Check | Command | Expected |
|-------|---------|----------|
| xhigh guidance block present | `grep -c "When \`xhigh\` is worth setting" .claude/rules/agent-authoring.md` | 1 |
| Effort enum includes xhigh | `grep -n "low|medium|high|xhigh|max" .claude/rules/agent-authoring.md` | line 22 match |
| 4.7 under-spawn note in RULES | `grep -n "Opus 4.7" src/superclaude/core/RULES.md` | ≥1 inside `<sub_agent_decision>` |
| Checklist V4 flipped | `grep -n "Doc-level note added in Tier 2" docs/reports/OPUS_4_7_ALIGNMENT.md` | 1 |
| Unit tests pass | `uv run pytest tests/unit/ -q` | 1684 pass, 0 fail (Tier 1 baseline) |
| Part A V1-V10 | walk checklist | 9 ✅ · 1 ⏭ (V3 manual) · 0 ⚠️ |

---

## Scope Guard

- **In scope:** 3 file modifications + 1 plan creation + 1 checklist update + spec `revised:` bump
- **Out of scope:** T2-a Option 2 (per-agent `effort: xhigh` frontmatter additions), behavioral rule rewrites in `<sub_agent_decision>` (threshold/count changes), Part B empirical evals, Tier 3 items, model identity prompt, new unit tests for either change
- **If unexpected work surfaces:** stop and consult user — do not expand scope within this plan execution (R06)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| xhigh guidance inflates user session cost if over-applied | Low | Medium | Guidance explicitly names session-level as preferred path and warns against per-agent additions without measurement |
| 4.7 under-spawn note gets stale on next model release | Medium | Low | Note references "Opus 4.7" explicitly so future regex audit (V4 in checklist) will flag it for review |
| V4 false-confidence: doc note doesn't actually fix behavior | Medium | Medium | Checklist V4 now explicitly splits doc-level vs behavioral-threshold; eval-gated rewrite remains open |
| Line numbers drift between plan draft and implementation | Medium | Low | Each task uses `grep -n` to locate insertion point at execution time rather than relying on absolute line numbers |

## Handoff

Ready for `/sc:implement --plan docs/plans/opus-4-7-alignment-tier-2-ajitta-2026-04-18.md`.

Next candidate work (out of this plan):
- Part B behavioral evals against Opus 4.7 (spec §6 Q3) — needed before further rule-threshold rewrites
- V3 manual RULES.md scope audit (unchanged from Tier 1 deferral)
- Tier 3 items (T3-a literal-scope rule audit, T3-b `≤25 words` scaffolding review)
