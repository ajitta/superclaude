---
status: complete
revised: 2026-04-25
spec: docs/specs/retrospective-followups-discovery-ajitta-2026-04-25.md
phases: 8
branch: fix/retrospective-followups-2026-04-25
implementation_log:
  - phase: 1 (B1 make test python -m)
    commit: 18e0921
  - phase: 2 (E1 make deploy chains install)
    commit: 0dbd62c
  - phase: 3 (E2 status enum)
    commit: a9a28b0
  - phase: 8 (Q5 plan phase-default)
    commit: b8dc312
  - phase: 4 (C1 brainstorm hard-block)
    commit: c438fa3
  - phase: 5 (A1 canary manifests)
    commit: 1959698
  - phase: 6 (A2 memory verified hook)
    commit: 01a520b
  - phase: 7 (C2 delegated audit)
    commit: d7e1fb8
test_baseline: "1,777 passed / 24 skipped / 4 canary deselected (was 1,628)"
---

# Retrospective Followups Implementation Plan

**Goal:** Land 8 improvements (B1, E1, E2, C1, A1, A2, C2, plus Q5 /sc:plan default) from the 2026-04-25 retrospective.
**Architecture:** Single feature branch, one commit per phase. Phases 1–3, 8 are sub-5-line edits; 4–6 are skill/hook work; Phase 7 has an inline mini-design gate.
**Tech Stack:** Makefile, Markdown frontmatter (RULES.md, brainstorm.md, plan.md), Python (pytest fixture, SessionStart hook), YAML manifests.

**TDD applicability:** Per CLAUDE.md ("Markdown-only changes carry no test risk"), Phases 1–4, 7, 8 (markdown/Makefile-only) skip the failing-test-first ceremony — verification is by manual canary or grep on installed artifact. Phase 5 (new pytest file) and Phase 6 (new Python hook) follow standard TDD.

## Phase Order (small-fix-first, structural-last)

| # | Phase | Files | Dep |
|---|---|---|---|
| 1 | **B1** make test fix | `Makefile:20` | — |
| 2 | **E1** make deploy chains install | `Makefile:12-15`, `CLAUDE.md` | — |
| 3 | **E2** status enum | `src/superclaude/core/RULES.md` (doc_output_convention) | — |
| 4 | **C1** brainstorm → review hard-block | `src/superclaude/commands/brainstorm.md` | — |
| 5 | **A1** canary manifests + iterator | `tests/integration/test_skill_canary.py` (new), `src/superclaude/skills/**/canary.yaml` (new) | — |
| 6 | **A2** memory `verified:` + warn | `src/superclaude/hooks/memory_staleness.py` (new), `hooks.json` | — |
| 7 | **C2** auto-review on delegated | `brainstorm.md` (extend Phase 4), `commands/review.md` | **Phase 4** |
| 8 | **Q5** /sc:plan phase-default + opt-in PR | `src/superclaude/commands/plan.md` | — |

## Verification Baselines
- `make test`: 1,628+ passing, 24 skipped (must hold)
- `make doctor`: clean
- No regressions in `tests/integration/test_cross_directory_refs.py`

---

### Phase 1 — B1: Fix `make test` to use `python -m pytest`

**Files:** Modify: `Makefile:20`
**Why/Verify:** `uv run pytest` fails with "canonicalize script path" on Windows; `python -m pytest` works. Verify: `make test` exits 0, no canonicalize stderr.

- [ ] Step 1: Edit `Makefile:20` — `uv run pytest` → `uv run python -m pytest`
- [ ] Step 2: Run `make test` — assert exit 0, no "canonicalize script path" in output
- [ ] Step 3: Commit: `fix(make): use python -m pytest to dodge uv Windows canonicalize bug`

---

### Phase 2 — E1: `make deploy` chains `superclaude install --force`

**Files:** Modify: `Makefile:11-15`, `CLAUDE.md` (Make Commands + Developer Environment sections)
**Why/Verify:** Two-step deploy is undocumented; source §4.1. Verify: append marker to `src/superclaude/skills/confidence-check/SKILL.md`, `make deploy`, grep marker in `~/.claude/skills/confidence-check/SKILL.md`, revert.

- [ ] Step 1: Edit Makefile `deploy:` target — append `uv run superclaude install --force` after the `uv tool install` line; update echo to "Changes in src/ AND ~/.claude/ content updated."
- [ ] Step 2: Update `CLAUDE.md` Developer Environment section: remove "Editable install via `make deploy`..." misstatement, replace with "`make deploy` deploys CLI + content (chained install --force)."
- [ ] Step 3: Update Make Commands section line for `make deploy` accordingly.
- [ ] Step 4: Manual verification: append a temp marker string (e.g. `<!-- canary-2026-04-25 -->`) to `src/superclaude/skills/confidence-check/SKILL.md`, run `make deploy`, grep marker in `~/.claude/skills/confidence-check/SKILL.md`. Revert marker.
- [ ] Step 5: Commit: `fix(make): make deploy chains superclaude install --force`

---

### Phase 3 — E2: `status:` frontmatter enum in RULES.md

**Files:** Modify: `src/superclaude/core/RULES.md` (doc_output_convention block, lines ~144-154)
**Why/Verify:** No documented enum; ad-hoc values today (§6.1). Verify: `grep -rh "^status:" docs/ | sort -u` — every value appears in the enum (or migration recorded).

- [ ] Step 1: Edit RULES.md `<doc_output_convention>` — add line: `Status enum: draft | review | approved-for-plan | implementing | complete | deprecated`
- [ ] Step 2: Run `grep -rh "^status:" docs/specs/ docs/plans/ docs/analysis/ docs/research/ 2>/dev/null | sort -u` — record current values
- [ ] Step 3: For each out-of-enum value, decide: rename file frontmatter, OR expand enum if domain-justified. Record decisions inline.
- [ ] Step 4: Run grep again — assert all values are in enum
- [ ] Step 5: Commit: `docs(rules): add status frontmatter enum + reconcile existing docs`

---

### Phase 4 — C1: `/sc:brainstorm` hard-blocks `/sc:plan` until `/sc:review`

**Files:** Modify: `src/superclaude/commands/brainstorm.md` (77 lines)
**Why/Verify:** 3 critical reversals on a user-approved spec last session (§3.5); soft recommendation insufficient. Verify: grep on installed brainstorm.md (see Step 7).

- [ ] Step 1: Read full brainstorm.md (77 lines)
- [ ] Step 2: Update `<flow>` — split current step 5 ("Approve") into steps 5 (Approve) + 6 (Self-review **required** — emit explicit handoff "Run /sc:review on this spec before /sc:plan. Plan handoff is gated on review.")
- [ ] Step 3: Update `<handoff next="..."/>` from `/sc:plan /sc:design /sc:research` to `/sc:review /sc:plan /sc:design /sc:research` (review listed first)
- [ ] Step 4: Add to `<gotchas>`: `skip-review: do NOT route to /sc:plan when status: draft AND no /sc:review iteration logged. Hard gate, not advisory.`
- [ ] Step 5: Update `<bounds should="...">` to include "self-review precedes implementation handoff"
- [ ] Step 6: Sync via `make deploy` (now chains install per Phase 2)
- [ ] Step 7: Verification (replaces unreliable `claude -p` slash invocation per source §2.4): `grep -E "review|hard.gate|skip-review" ~/.claude/commands/brainstorm.md` — assert all three terms present at expected anchors (handoff line, gotcha line, flow step 6)
- [ ] Step 8: Commit: `feat(brainstorm): hard-block /sc:plan until /sc:review runs`

---

### Phase 5 — A1: Per-skill canary manifests + iterator fixture

**Files:**
  - Create: `tests/integration/test_skill_canary.py`
  - Create: `src/superclaude/skills/<skill>/canary.yaml` for ≥2 reference skills — **`confidence-check` and `verbalized-sampling`** (both have unambiguous trigger keywords; `find-skills`/`tavily-cli` are not in this repo's source so unavailable as targets)
  - Modify: `src/superclaude/ARCHITECTURE.md` (document the convention)

**Schema (canary.yaml):**
```yaml
- trigger: "user phrase that should activate this skill"
  expected_pattern: "regex on response indicating the skill ran"
- trigger: "another phrase"
  expected_pattern: "another regex"
```

**Why/Verify:** Keystone bug (`when-to-use:` ignored 14 days, §1.1) shipped because no trigger test existed. Verify: `pytest tests/integration/test_skill_canary.py -m canary -v` green; `make test` baseline holds when marker excluded.

- [ ] Step 1: Write `tests/integration/test_skill_canary.py` — define `@pytest.mark.canary`, glob `src/superclaude/skills/**/canary.yaml`, parse YAML, parametrize test cases per (skill, trigger, pattern)
- [ ] Step 2: Test body — invoke `claude -p '<trigger>' --output-format json`, parse JSON, assert `re.search(expected_pattern, response, re.IGNORECASE)`
- [ ] Step 3: Add `canary` marker to `pyproject.toml` `[tool.pytest.ini_options].markers` (so it's not unknown)
- [ ] Step 4: Author 2 reference canary.yaml files (`src/superclaude/skills/confidence-check/canary.yaml` + `src/superclaude/skills/verbalized-sampling/canary.yaml`) with 1-2 trigger phrases each
- [ ] Step 5: Document the convention in `ARCHITECTURE.md` — "Skills MAY ship `canary.yaml`; CI runs `pytest -m canary` to catch trigger regressions."
- [ ] Step 6: Run canary tests — assert pass
- [ ] Step 7: Run `make test` (excludes canary by default) — assert 1,628+ baseline holds
- [ ] Step 8: Commit: `feat(test): per-skill canary manifests for trigger regression coverage`

**Open for /sc:implement:** CI vs manual `pytest -m canary` (network + slow). Recommend manual for v1; revisit in 1 month.

---

### Phase 6 — A2: Memory `verified:` field + SessionStart staleness warn

**Files:**
  - Create: `src/superclaude/hooks/memory_staleness.py` (SessionStart hook)
  - Modify: `src/superclaude/hooks/hooks.json` (register hook — existing pattern: `{{PYTHON_BIN}} {{SCRIPTS_PATH}}/<script>.py`)
  - Modify: `src/superclaude/cli/install_components.py` (only if hook installation needs explicit wiring — existing hooks register declaratively via hooks.json, so this is unlikely; verify during step 1)
  - Modify: `src/superclaude/hooks/README.md` (document `verified:` field — installable docs home so users learn the convention)

**Why/Verify:** Stale memory was the keystone bug's source (§1.1, §4.3); SessionStart scan converts invisible→visible. Verify: see Step 7 manual canary.

**Decisions (locked):** SessionStart trigger; 90-day threshold (env `SUPERCLAUDE_MEMORY_STALE_DAYS`); current-project scope; path encoding: separators→`-`, drive colon→`--` (e.g., `C:\Users\ajitta\Repos\ajitta\superclaude` → `C--Users-ajitta-Repos-ajitta-superclaude`); stderr non-blocking output `⚠️ N memory entries verified > 90 days ago: [files]`.

- [ ] Step 1: Inspect existing `src/superclaude/hooks/hook_tracker.py` and `hooks.json` to confirm SessionStart registration pattern (`{{PYTHON_BIN}} {{SCRIPTS_PATH}}/<script>.py`)
- [ ] Step 2: TDD — write failing test in `tests/unit/test_memory_staleness.py`: given a memory dir with one `verified: 2026-01-01` entry and one `verified: <today>`, scanner returns exactly the stale entry's filename
- [ ] Step 3: Implement `memory_staleness.py` — derive project memory dir from `os.getcwd()` using documented encoding (separators → `-`, drive colon → `--`), glob `*.md`, parse YAML frontmatter, compute age vs threshold, print stderr summary
- [ ] Step 4: Verify unit test passes
- [ ] Step 5: Register in `hooks.json` under SessionStart matcher
- [ ] Step 6: Document `verified: <YYYY-MM-DD>` convention in `src/superclaude/hooks/README.md` (installable home so users see it)
- [ ] Step 7: Manual canary: add `verified: 2026-01-01` to a memory file, run `make deploy`, start fresh session, assert stderr warning. Revert test entry.
- [ ] Step 8: Run `make test` — baseline holds (1,628+ passing, +1 for new unit test)
- [ ] Step 9: Commit: `feat(hooks): SessionStart memory-staleness warning + verified: convention`

---

### Phase 7 — C2: Auto-trigger `/sc:review` on delegated decisions

**Inline mini-design (locked):**
- Heuristic: **confirmed** = response contains `[a-c]`/`a`/`b`/`c` literal OR ≥2 contiguous words from option label. Else **delegated**.
- Rationale: zero schema change; backwards-compatible with all existing /sc:brainstorm outputs.
- Risk: false-positive auto-review on confirmed-but-bare answers. If observed >1× in canary, revisit.

**Files:**
  - Modify: `src/superclaude/commands/brainstorm.md` (extends Phase 4's changes — implement *after* Phase 4 commits)
  - Modify: `src/superclaude/commands/review.md` (slash-command target; `agents/self-review.md` is a separate delegated-review agent and is *not* the target here)

**Verification:**
- Canary A: brainstorm with 2 Qs, accept both ★ with bare "proceed" → assert review handoff fires with "N delegated decisions" message.
- Canary B: brainstorm with 2 Qs, answer "[a]" and "[b]" explicitly → assert no auto-review trigger.

- [ ] Step 1: Define heuristic concretely in brainstorm.md: "confirmed = response contains `[a-c]`/`a`/`b`/`c` literal OR contains ≥2 contiguous words from the option's label text. Else delegated."
- [ ] Step 2: Update brainstorm.md decision-output template — for each Q, capture inline in spec output: `{q: Q1, choice: [c], mode: confirmed|delegated}`
- [ ] Step 3: Add to brainstorm.md `<flow>` step 6 — "If any decision.mode == delegated, the /sc:review handoff message must explicitly say 'mandatory: N delegated decisions need independent audit'"
- [ ] Step 4: Update `commands/review.md` — accept invocation flag `--audit-delegated` that surfaces only Qs marked delegated
- [ ] Step 5: Sync via `make deploy`
- [ ] Step 6: Verification A (delegated): grep installed `~/.claude/commands/brainstorm.md` for "delegated decisions need independent audit" string presence
- [ ] Step 7: Verification B (confirmed): grep `~/.claude/commands/review.md` for `--audit-delegated` flag definition
- [ ] Step 8: Commit: `feat(brainstorm): auto-trigger /sc:review on delegated decisions`

---

### Phase 8 — Q5: `/sc:plan` phase-default + opt-in PR-bundle flag

**Files:** Modify: `src/superclaude/commands/plan.md`
**Why/Verify:** Spec §7 Q5=[b]; source §5.1 (4-PR plan executed as 4 phase commits — naming should match reality). Verify: grep installed plan.md for "phase" + `--pr-bundle` (see Step 5).

- [ ] Step 1: Edit `commands/plan.md` `<role>`/`<flow>` text to use "phase N" terminology in default examples (replacing "PR1/PR2/..." patterns where they appear as defaults)
- [ ] Step 2: Add `[--pr-bundle]` to `<syntax>` line and document it under `<examples>`: opt-in flag that switches output framing to "PR" semantics for true multi-PR review cycles
- [ ] Step 3: Update `<bounds>` or `<gotchas>` to note "default phase framing matches single-branch execution per source §5.1; --pr-bundle for multi-review cycles"
- [ ] Step 4: Sync via `make deploy`
- [ ] Step 5: Verification: `grep -E "phase|--pr-bundle" ~/.claude/commands/plan.md` — both terms present
- [ ] Step 6: Commit: `feat(plan): default phase framing; opt-in --pr-bundle for multi-PR cycles`

---

## Acceptance Checklist

- [ ] All 8 phases committed on `fix/retrospective-followups-2026-04-25`
- [ ] `make test` → 1,628+ passing, 24 skipped (baseline held)
- [ ] `make doctor` clean
- [ ] Spec status updated `approved-for-plan` → `complete` post-merge
- [ ] No file appears in both `<theme-improvement-list>` and `<§5 Out of Scope>` (spec-internal contradiction check)

## Fallback (per spec §7)

If Phase 7 mini-design's heuristic produces >1 false-positive in canary, mark Phase 7 deferred and ship Phases 1–6 alone. Phases 1–6 have no dependency on C2 → partial-bundle merge is safe (matches source §5.1 phase-collapse pattern).

If Phase 4 (C1) blocks on review-skill location ambiguity, that affects Phase 7 (depends on Phase 4); other phases proceed.

## Cross-Phase Notes

- Phase 4 + Phase 7 both edit `brainstorm.md` (Phase 7 sequenced after 4; out-of-order requires rebase). Phase 7 also edits `commands/review.md` (no conflict).
- Phase 2 (make deploy) before Phases 4-8 so verifications use single-step deploy. Phase 1 (make test fix) first for clean test output. Phase 8 is independent (sequenced last for thematic grouping).

## Handoff

→ `/sc:implement --plan @docs/plans/retrospective-followups-ajitta-2026-04-25.md`
