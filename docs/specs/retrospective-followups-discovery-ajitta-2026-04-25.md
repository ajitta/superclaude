---
status: complete
revised: 2026-04-25
source: docs/analysis/superclaude-session-retrospective-ajitta-2026-04-25.md
purpose: Cluster the 2026-04-25 retrospective's catalog of frictions/bugs into prioritized improvement themes for /sc:plan handoff
implementation: docs/plans/retrospective-followups-ajitta-2026-04-25.md (8 phases, all committed)
---

# Discovery: Project Improvements from 2026-04-25 Retrospective

## 1. Source & Method

**Source.** `docs/analysis/superclaude-session-retrospective-ajitta-2026-04-25.md` — 32 catalogued items across 6 categories (internal bugs, harness friction, command friction, integration gaps, workflow gaps, doc gaps). Author already produced a Top-5 actionable list (§8).

**Method.** No external research needed (retrospective is the SoT for project-internal friction). Verbalized-sampling brainstorm with k=5 themes anchored by countable signals from retrospective §9 (12 friction events → recurrence; 3 critical self-review reversals → governance impact; 14-day silent-failure window → stealth class), plus landscape synthesis to surface what the author's own Top 5 underweighted. Theme weights below are qualitative anchors, not normalized probabilities — they encode "this class merits a slot" not "this class has X% of total leverage".

**Constraint.** Discovery only — defer architecture to `/sc:design`, exact tasks to `/sc:plan`. Resolve Q1–Q5 (§4) before handoff.

---

## 2. VS-Distributed Improvement Themes (k=5)

### Theme A — Reliability: silent-bug class (anchor: 14-day stealth window) ★

**Pattern.** Three classes of failures shipped invisibly:
- Field-name parser mismatch (`when-to-use:` ignored 14 days; §1.1)
- Memory entry contradicting upstream truth (`reference_cc-native-fields.md`; §4.3)
- Hook regex substring false-positives (`-f` blocked `-force-with-lease`; §1.3)

**Common shape.** A documented-as-true claim was actually false, with no automated detector.

**Improvements:**
- **A1.** Skill-canary fixture (`tests/integration/test_skill_canary.py`) — programmatic `claude -p` invocation; fails CI when triggers stop firing. *(Top-5 #4)*
- **A2.** Per-entry `verified: <date>` frontmatter field on memory files — auto-warn after N days when the entry is referenced. *Distinct from* the broader "quarterly memory-curation skill" suggested in §4.3 (the curation skill is the systemic version; A2 is the per-entry minimal stub). *(retrospective §4.3 — partially in source, scope-narrowed here)*
- **A3.** Hook-pattern lint — CI check that flag-like substrings in regex hooks use word-boundary fences (`[^a-z]`).

**Why this matters.** This class produced a 14-day invisible-degradation window. Without detectors, the next equivalent silent bug ships invisibly again. **The retrospective's Top 5 missed A2 and A3** — both are direct reactions to the keystone bug's root cause.

---

### Theme B — Ergonomics: per-session friction (anchor: 12 friction events / session)

**Pattern.** Tool-harness papercuts; ~12 redundant tool calls observed in a single session (§2, §9 metrics row).

**Improvements:**
- **B1.** Replace the `uv run pytest` invocation inside `make test` with `uv run python -m pytest` (the bug is in `uv run`'s script-path canonicalization on Windows, not the Makefile target itself — kills "canonicalize script path" false failures). *(Top-5 #1; §2.2)*
- **B2.** Read dedup hook bypass-on-mtime-change (or `--force-fresh` flag). *(§2.1)*
- **B3.** Hook matcher scope: `make test` only on `src/` `tests/` paths. *(§2.3)*
- **B4.** TaskCreate reminder suppression after "proceed all" / clean task list. *(§2.5)*

**Why this matters.** High volume, low individual severity. Each fix is small but the aggregate cost is real and recurring.

---

### Theme C — Governance: self-review as load-bearing gate (anchor: 3 critical reversals / spec)

**Pattern.** Self-review caught **3 critical errors after user approval** (D1 reversal: `when_to_use` is deprecated; install-path "3 targets" wrong; D2 sunk-cost rationale). Without it, v1 spec ships → PR1 work is wasted (§3.5, §5.3).

**Improvements:**
- **C1.** `/sc:brainstorm` final output emits `<handoff next="/sc:review"/>` before `/sc:plan`. *(Top-5 #3)*
- **C2.** Auto-trigger `/sc:review` on any decision tagged "delegated to model" (Q4/Q5/D-D5 pattern). **Tagging mechanism deferred to /sc:design** — possible markers include explicit `delegated: true` in decision frontmatter, or absence-of-user-recommendation as the implicit signal. Source proposes the pattern but offers no marker (§5.3).
- **C3.** `/sc:review` auto-emits v1→v2 decision-trail delta when modifying drafts. *(§5.2)*
- **C4.** Document auto-mode decision-gate matrix in `/sc:brainstorm` body — which pauses are real, which are ceremonial. *(§3.3)*

**Why this matters.** Structurally load-bearing but lower frequency than ergonomics. One missed review = a multi-PR rework cycle.

---

### Theme D — Leverage: introspection + automation (anchor: hand-rolled 11-call canary, manual 4-file plan split)

**Pattern.** Manual work that should be tooled. *(D1 dedup'd against A1 — Theme A owns the skill-canary fixture; Theme D no longer claims it. D2 `/sc:trace` deferred to §5 Out of Scope and removed from this list.)*

**Improvements:**
- **D1.** `/sc:plan --phases N` — auto-split when over 15KB cap (currently hand-authored across 4 phase files). *(§3.1)*
- **D2.** Plan template `<verification mode="auto|interactive|deferred">` per task with explicit fallback paths for automation-blocked steps (e.g., canary probes that need fresh interactive sessions). *(§3.4)*
- **D3.** `/sc:insight` body switches from `python -c "..."` to temp-file pattern (fragile shell quoting with backticks). *(§3.2)*

**Why this matters.** Lower individual leverage than A/B/C, but each fix removes a class of manual repetition. D3 is a small concrete fix landable today; D1 is a larger plan-command change.

---

### Theme E — Convention drift control (anchor: per-fix one-liner; aggregate value over time)

**Pattern.** Documented-state vs reality gaps that confuse readers.

**Improvements:**
- **E1.** CLAUDE.md two-step deploy clarification, **OR** `make deploy` chains `superclaude install --force`. *(Top-5 #2)*
- **E2.** RULES.md `<doc_output_convention>` `status:` enum (e.g., `draft|review|approved|implementing|complete|deprecated`). *(Top-5 #5)*
- **E3.** `<deferred until="..." reason="...">` greppable marker convention. *(§6.2)*
- **E4.** Default greps exclude `.claude/worktrees/` (mirror inflates counts). *(§4.4)*

**Why this matters.** Each is a one-line fix. Lower individual leverage; the value is consistency over time.

---

## 3. Landscape Synthesis

Two strategic axes emerge from the distribution:

**Axis 1 — Detect vs Prevent.** Theme A *detects* bugs that already shipped invisibly; Theme C *prevents* them at design time. Both are needed:
- C alone wouldn't have caught the parser-field bug — it was invisible to design review.
- A alone would catch it after-the-fact — still a 14-day window of invisible degradation.

**Axis 2 — Per-session vs Structural.** B + E hit per-session friction. A + C + D are structural, affecting all future sessions. **The retrospective's Top 5 weights per-session friction higher** (B + E = 3 of 5 slots), but structural changes have higher amortized leverage.

**Delta from author's Top 5:**
| Top 5 # | Theme | Status |
|---|---|---|
| 1 | B (B1) | covered |
| 2 | E (E1) | covered |
| 3 | C (C1) | covered |
| 4 | A1 (skill-canary; D theme contributes nothing distinct here) | covered |
| 5 | E (E2) | covered |
| — | **A2 (memory `verified:` field)** | **missing — root cause of keystone bug; minimal stub of §4.3's curation suggestion** |
| — | C2/C3 (decision-trail audit) | missing — load-bearing for auto-mode |
| — | D `/sc:trace` (§4.5) | deferred to §5 — speculative until trigger overlap actually breaks something |

---

## 4. Open Decisions (resolve before /sc:plan)

#### [Q1] Theme priority — accept Top 5 or rebalance?
- [a] Accept retrospective's Top 5 verbatim — favors author's original prioritization (no swap risk)
- [b] Swap: drop E2 (status-enum, the lowest-ranked Top 5 item, pure consistency value) for A2 (memory `verified:` field, detection of stale claims) — *judgment call, not obvious*: trades frontmatter consistency-of-state for one detector of the keystone-bug class
- [c] Expand to Top 7: keep all five + add A2 + C2 (more scope, but no swap forced)

select: a / b / c — or type your own. (Author leans [c] — A2 is the highest-leverage gap but [a] has zero scope risk.)

#### [Q2] Self-review gate enforcement (Theme C1)
- [a] Soft — `/sc:brainstorm` emits a recommendation banner at end
- [b] Hard — `/sc:brainstorm` blocks `/sc:plan` handoff until `/sc:review` runs
- [c] Conditional — hard-block only when decisions are tagged "delegated to model" (requires C2's tagging mechanism, which is design-deferred)

select: a / b / c. (Author leans [b] given §3.5 evidence: 3 critical reversals on a single approved spec; [c] is correct in principle but blocked on C2 design work.)

#### [Q3] Skill-canary fixture scope (A1)
- [a] Single fixture, in-tree (`tests/integration/test_skill_canary.py`) — author writes triggers there; lower per-skill ceremony
- [b] Per-skill manifest — each skill ships `(trigger, expected_pattern)` tuples; fixture iterates; higher per-skill ceremony but better isolation
- [c] Both: framework fixture + per-skill manifests

select: a / b / c. (Author leans [b] — per-skill manifests survive skill rename/move; [a] centralizes everything in one churned file.)

#### [Q4] `make deploy` resolution (E1)
- [a] Doc-only — CLAUDE.md notes the two-step requirement
- [b] `make deploy` chains `superclaude install --force`
- [c] Rename: `make deploy-cli` + `make deploy-content` + `make deploy-all` (the latter chains both)

select: a / b / c. (Author leans [b] — single command matches mental model; [c] is more honest but adds three targets where one was confusing.)

#### [Q5] Phase-vs-PR semantics (§5.1, ties to C/D)
- [a] No change — keep "PR" framing; add note that phases collapse to commits in auto mode
- [b] `/sc:plan` switches to "phase" by default; "PR" is opt-in via flag
- [c] Decided per-plan by user at invocation time

select: a / b / c. (Author leans [b] — matches actual single-branch execution; [c] over-options a default.)

**Note on auto-mode.** "Author leans [X]" is informational, not a default-pick. Auto-mode should still surface Q1–Q5 to the user before `/sc:plan` invocation — the prior session's lesson (§3.5) is that delegated decisions need explicit confirmation, not silent rubber-stamping.

---

## 5. Out of Scope

Deferred — not in this improvement bundle:
- **`/sc:trace` introspection (originally Theme D, §4.5)** — speculative; defer until trigger overlap actually breaks something. *Removed from Theme D's improvement list to avoid double-counting.*
- **Worktree-grep default exclude (E4)** — defer until the next time it actually friction-hits.
- **Systemic memory-curation skill (§4.3 broader version)** — quarterly re-verification of all time-sensitive memory claims. Design-spec-level, not improvement-level; spawn its own brainstorm later. **A2 is the in-scope minimal stub** (per-entry `verified:` field with on-reference warning), explicitly distinguished from this systemic version.

---

## 6. Handoff

**Recommended next step:**
1. `/sc:review` on this discovery spec (Theme C is itself the argument for this gate — eat our own dog food).
2. After Q1–Q5 resolved, `/sc:plan` over the selected items.

**Acceptance for /sc:plan:**
- Q1–Q5 answered explicitly (no silent ★-pick — see §3.5 of source)
- Final improvement list has ≤7 items (per checklist_scaling: small-medium scope per item)
- Each item has owner-theme (A/B/C/D/E) + verification path (test, doc-grep, manual canary)
- No internal contradictions (each improvement appears in exactly one of: in-scope theme list OR §5 Out of Scope)

---

## 7. Resolved Decisions (user-confirmed 2026-04-25)

| Q | Choice | Resulting scope |
|---|---|---|
| Q1 | **[c]** Top 7 — Top 5 + **A2** (memory `verified:` field) + **C2** (auto-trigger /sc:review on delegated decisions) | 7 in-scope improvements; ceiling per §6 acceptance |
| Q2 | **[b]** Hard block — `/sc:brainstorm` blocks `/sc:plan` handoff until `/sc:review` runs | Affects `/sc:brainstorm` skill body; new <handoff> requirement |
| Q3 | **[b]** Per-skill manifest — each skill ships `(trigger, expected_pattern)` tuples; fixture iterates | A1 implementation: schema + iterator fixture; *not* a centralized in-tree trigger registry |
| Q4 | **[b]** `make deploy` chains `superclaude install --force` | Makefile target change; CLAUDE.md updated to match |
| Q5 | **[b]** `/sc:plan` switches to "phase" default; "PR" opt-in via flag | `/sc:plan` skill body change; existing plan docs retain PR framing |

**Final 7-item improvement bundle for /sc:plan:**

| # | Item | Theme | Source ref | Verification path |
|---|---|---|---|---|
| 1 | `make test` invokes `python -m pytest` (fix `uv run pytest` Windows bug) | B1 | §2.2, §8 #1 | run `make test` → no "canonicalize script path" output |
| 2 | `make deploy` chains `superclaude install --force` | E1 | §4.1, §8 #2 | `make deploy` → ~/.claude/ content reflects src/ changes |
| 3 | `/sc:brainstorm` hard-blocks `/sc:plan` until `/sc:review` runs | C1 | §3.5, §8 #3 | inspect skill body; manual canary on a fresh brainstorm |
| 4 | Per-skill skill-canary manifests + iterator fixture | A1 | §4.2, §8 #4 | `pytest tests/integration/test_skill_canary.py` passes |
| 5 | RULES.md `<doc_output_convention>` `status:` enum | E2 | §6.1, §8 #5 | grep status: across docs/, all values in enum |
| 6 | Memory `verified: <date>` field with on-reference staleness warn | A2 | §1.1, §4.3 (minimal stub of curation skill) | reference a memory entry with `verified:` >N days old → warning emitted |
| 7 | C2 auto-trigger `/sc:review` on delegated decisions (with C2 design-deferred tagging) | C2 | §5.3 | `/sc:design` produces tagging mechanism; then verify on a brainstorm with delegated Q |

**C2 tagging-mechanism resolution (user-confirmed 2026-04-25):**
- **Approach (a) — inline mini-design within /sc:plan, no separate design cycle.** Tagging-mechanism decision (candidates: explicit `delegated: true` frontmatter vs absence-of-user-★ as implicit signal) is a 1-2-option comparison; a separate /sc:design spec + plan cycle is over-ceremony per R06/R18.
- **Sequencing:** Phase 7 (C2 implementation) gated by a ≤5-line inline design decision recorded in the plan body before Phase 7 starts. Phases 1–6 have no dependency on C2 → unblocked regardless.
- **Fallback:** If Phase 7 design stalls, mark Phase 7 `<verification mode="deferred"/>` and ship Phases 1–6 alone (matches §5.1 phase-collapse pattern from source retrospective).

## 8. Self-Review Iteration Log

| Version | Date | Trigger | Critical changes |
|---|---|---|---|
| v1 (draft) | 2026-04-25 | Initial brainstorm | Themes A–E with normalized `p≈` weights, ★ recommendations on Q1–Q5 |
| v2 (this) | 2026-04-25 | Self-review (revise-required verdict) | C1: removed `/sc:trace` from Theme D (was double-listed). C2: removed null D1 entry, renumbered D items. C3: distinguished A2 (`verified:` field, in-scope) from systemic curation skill (out of scope). I1: reframed Q1[b] as judgment trade-off. I2: dropped probability weights for countable-signal anchors. I3: corrected B1 phrasing (bug is in `uv run`, not `make test`). I4: marked C2 tagging mechanism as design-deferred. ★ pattern downgraded to "Author leans" with explicit no-rubber-stamp note. |
