---
status: ready-to-execute
revised: 2026-04-25
plan: docs/plans/skill-authoring-consistency-pr1-p0-ajitta-2026-04-25.md
purpose: PR1 Task 10 (D3) acceptance gate — verify auto-invocation works after `when-to-use` removal
---

# PR1 Canary Probe — Test Scenarios

**What we're verifying:** After folding `when-to-use` content into `description`, does Claude actually auto-invoke skills on the trigger phrases? The leaked-source analysis says yes, but until we observe it in a real session, the fix is unverified.

**Branch:** `fix/skill-authoring-consistency` (already deployed to global tool via `make deploy`).

**Time budget:** ~10–15 minutes for all 5 scenarios.

---

## Pre-flight (run once)

- [ ] **P0.** Confirm branch is checked out and deployed:
  ```bash
  cd C:/Users/ajitta/Repos/ajitta/superclaude
  rtk git status                       # → on fix/skill-authoring-consistency, clean
  make deploy                          # uv tool install --editable .
  cat ~/.claude/skills/confidence-check/SKILL.md | head -8
  ```
  **Pass:** `description:` line contains `"This skill should be used when the user says 'confidence check', ..."` and there is **no** `when-to-use:` key.

- [ ] **P1.** Open a fresh CC session in a scratch directory (NOT this repo, to avoid `.claude/rules/skill-authoring.md` `paths:` priming the conversation):
  ```bash
  mkdir -p /tmp/canary-probe && cd /tmp/canary-probe
  claude
  ```

- [ ] **P2.** Confirm 5 skills are visible in the new session: type `/help` or `/menu` and look for confidence-check, finishing-a-development-branch, ship, simplicity-coach, verbalized-sampling. (`disable-model-invocation: true` skills will appear in the menu but not auto-invoke; `confidence-check` and `verbalized-sampling` are the auto-invoke candidates.)

---

## Scenario A — `confidence-check` auto-invoke (PASS = green light)

**Skill type:** Archetype ① (no `disable-model-invocation`) — auto-invoke is the contract.

**Trigger expectation:** Description contains "This skill should be used when the user says 'confidence check', 'validate first', 'before starting', 'before implementing'..."

- [ ] **A1.** In the fresh session, type:
  ```
  confidence check before I start this refactor
  ```
- [ ] **A2.** Observe Claude's response. **PASS** if Claude either:
  - Invokes the `Skill` tool with `confidence-check`, OR
  - States it's running the confidence check (the 3-question gate from the skill body), OR
  - Asks the 3 check questions (Already exists? / Fits stack? / Root cause clear?).

  **FAIL** if Claude responds generically without referencing the 3-check pattern.

- [ ] **A3.** Try a paraphrase that should also trigger:
  ```
  validate first before implementing the new auth flow
  ```
  Same pass/fail criteria as A2.

- [ ] **A4.** **Negative control** — should NOT trigger:
  ```
  what's the weather today?
  ```
  **PASS** if Claude does NOT invoke `confidence-check`. (False-positives would indicate description is too broad.)

---

## Scenario B — `verbalized-sampling` auto-invoke

**Skill type:** Archetype ① — auto-invoke.

**Trigger expectation:** Description names "multiple perspectives", "diverse responses", "VS", "VS-CoT", "verbalized sampling", "--vs".

- [ ] **B1.** Trigger phrase test:
  ```
  give me multiple perspectives on whether to use Postgres or DynamoDB
  ```
  **PASS** if Claude invokes `verbalized-sampling` or generates k probability-weighted candidates with the VS pattern.

- [ ] **B2.** Compact alias test:
  ```
  --vs API design tradeoffs
  ```
  **PASS** if `verbalized-sampling` activates.

- [ ] **B3.** **Negative control:**
  ```
  what is 2+2?
  ```
  **PASS** if NOT triggered (the skill description has an explicit "Do NOT trigger for routine coding questions, simple factual queries, or single-answer requests" exclusion that the model should respect).

---

## Scenario C — `disable-model-invocation` skills stay quiet on auto-trigger phrases

**Skill type:** Archetype ② — explicitly NOT auto-invoke. We're verifying the safety mechanism still works.

- [ ] **C1.** Type a phrase that matches `ship`'s description but should NOT trigger it:
  ```
  ship this commit and push to remote
  ```
  **PASS** if Claude does NOT auto-invoke `/ship`. (Claude may *describe* what shipping would do, but should not run the skill.)

- [ ] **C2.** Type a phrase matching `finishing-a-development-branch`:
  ```
  I'm done with this feature branch, want to merge
  ```
  **PASS** if Claude does NOT auto-invoke `/finishing-a-development-branch`.

- [ ] **C3.** Now confirm explicit invocation still works:
  ```
  /ship
  ```
  **PASS** if `/ship` runs (skill loads on explicit slash-command per `disable-model-invocation: true` rules).

---

## Scenario D — `simplicity-coach` (delegation-discipline ②)

**Skill type:** Archetype ② with delegation-discipline framing.

- [ ] **D1.** Auto-trigger phrase that would naively match — should NOT auto-invoke:
  ```
  this code feels overcomplicated
  ```
  **PASS** if Claude responds with simplicity guidance INLINE (likely via `simplicity-guide` agent which auto-loads), but does NOT invoke `/simplicity-coach` skill.

- [ ] **D2.** Explicit invocation:
  ```
  /simplicity-coach daybook
  ```
  **PASS** if the skill activates.

---

## Scenario E — Fresh-session reproducibility

This catches "it worked once but won't again":

- [ ] **E1.** Exit the CC session (`/exit`).
- [ ] **E2.** Open a brand-new CC session in the same scratch dir.
- [ ] **E3.** Re-run **A1** only. **PASS** if `confidence-check` still auto-invokes.

---

## Decision matrix

| Result | Action |
|--------|--------|
| **All scenarios PASS** | PR1 verified. Push branch + open PR. Note canary results in PR description. |
| **Scenario A fails (auto-invoke broken)** | STOP. Possibilities: (a) description-folding is unreadable to model, (b) `make deploy` didn't update `~/.claude/skills/`, (c) trigger phrasing is too oblique. Diagnose with `cat ~/.claude/skills/confidence-check/SKILL.md` to confirm install state. If install is correct but model doesn't trigger, revise descriptions and re-deploy. |
| **Scenario B fails but A passes** | Skill-specific issue with verbalized-sampling description; revise that one description and re-test. |
| **Scenario C fails (auto-invokes when blocked)** | `disable-model-invocation` is being ignored. Check that the field is at top-level (not nested under `metadata:`). This would be an authoring bug, not a parser bug. |
| **Negative control fails (false positive)** | Description is too broad — too many trigger words or too generic. Tighten the trigger phrasing. |
| **E1 (reproducibility) fails** | Session-state contamination. Possible cause: ~/.claude/sessions cache. Investigate before merging. |

---

## What to record in the PR description

For each scenario, capture:
- **Input prompt** (verbatim)
- **Observed behavior** (1-line summary: "auto-invoked confidence-check" / "responded generically without skill" / etc.)
- **Pass/Fail**

Minimum to document for merge approval:
- A1 PASS
- A4 PASS (no false positive on weather)
- C1 or C2 PASS (one disable-model-invocation skill confirmed quiet)
- C3 PASS (explicit invocation still works)

Optional but valuable for future reference:
- Full B + D scenarios.
- E1 reproducibility.

---

## Rollback (if probe fails irrecoverably)

```bash
rtk git checkout master                                      # leave fix branch intact for forensics
rtk git branch -D fix/skill-authoring-consistency            # only after confirming you don't need the diff
make deploy                                                  # restore master state to ~/.claude/
```

Or, less destructively, leave the branch and just `git checkout master && make deploy`. Branch retains the work for later iteration.

---

## Why this scenario set

- **A** — primary positive case: the field we changed must work for at least one skill.
- **B** — second positive case: confirms the pattern generalizes, not just a coincidence on `confidence-check`.
- **A4 / B3 / D1** — negative controls: prevent over-broad triggers (description bloat is a real risk after folding).
- **C** — confirms `disable-model-invocation` still gates correctly (PR1 didn't touch this field, but we should re-verify the pairing now that descriptions are richer).
- **C3** — confirms explicit invocation still works for the gated skills.
- **E** — fresh-session reproducibility, defending against session-state false-positives.
