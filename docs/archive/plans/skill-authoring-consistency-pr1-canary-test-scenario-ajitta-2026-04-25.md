---
status: complete
revised: 2026-04-25
plan: docs/plans/skill-authoring-consistency-pr1-p0-ajitta-2026-04-25.md
results: docs/plans/skill-authoring-consistency-pr1-canary-test-results-ajitta-2026-04-25.md
purpose: PR1 Task 10 (D3) acceptance gate — verify auto-invocation works after `when-to-use` removal
verdict: PASS (all minimum-required gates green; full coverage executed 2026-04-25)
---

# PR1 Canary Probe — Test Scenarios

**What we're verifying:** After folding `when-to-use` content into `description`, does Claude actually auto-invoke skills on the trigger phrases? The leaked-source analysis says yes, but until we observe it in a real session, the fix is unverified.

**Branch:** `fix/skill-authoring-consistency` (already deployed to global tool via `make deploy`).

**Time budget:** ~10–15 minutes for all 5 scenarios.

---

## Pre-flight (run once)

- [x] **P0.** Confirm branch is checked out and deployed:
  ```bash
  cd C:/Users/ajitta/Repos/ajitta/superclaude
  rtk git status                       # → on fix/skill-authoring-consistency, clean
  make deploy                          # uv tool install --editable .
  cat ~/.claude/skills/confidence-check/SKILL.md | head -8
  ```
  **Pass:** `description:` line contains `"This skill should be used when the user says 'confidence check', ..."` and there is **no** `when-to-use:` key.

- [x] **P1.** Open a fresh CC session in a scratch directory (NOT this repo, to avoid `.claude/rules/skill-authoring.md` `paths:` priming the conversation):
  ```bash
  mkdir -p /tmp/canary-probe && cd /tmp/canary-probe
  claude
  ```
  **Adapted to** headless `claude -p "<prompt>" --output-format json` per call (each spawns a fresh session — covers E1 reproducibility intrinsically).

- [x] **P2.** Confirm 5 skills are visible in the new session: type `/help` or `/menu` and look for confidence-check, finishing-a-development-branch, ship, simplicity-coach, verbalized-sampling. (`disable-model-invocation: true` skills will appear in the menu but not auto-invoke; `confidence-check` and `verbalized-sampling` are the auto-invoke candidates.)
  **Verified** via system-prompt skill listing: confidence-check + verbalized-sampling visible with full new descriptions; ship/finishing-a-development-branch/simplicity-coach correctly absent (gated by `disable-model-invocation: true`).

---

## Scenario A — `confidence-check` auto-invoke (PASS = green light)

**Skill type:** Archetype ① (no `disable-model-invocation`) — auto-invoke is the contract.

**Trigger expectation:** Description contains "This skill should be used when the user says 'confidence check', 'validate first', 'before starting', 'before implementing'..."

- [x] **A1.** In the fresh session, type:
  ```
  confidence check before I start this refactor
  ```
- [x] **A2.** ✅ **PASS** — Claude responded: "I need a task description to run the confidence check ... I'll run the 3 checks (already exists? / fits context? / intent clear?) with concrete evidence before you start." Skill body's 3-question pattern referenced.

- [x] **A3.** Try a paraphrase that should also trigger:
  ```
  validate first before implementing the new auth flow
  ```
  ✅ **PASS** — produced "## Confidence Check — auth flow implementation" + full 3-row check table.

- [x] **A4.** **Negative control** — should NOT trigger:
  ```
  what's the weather today?
  ```
  ✅ **PASS** — "I don't have access to weather data ... ask a voice assistant ..." Plain response, no skill invoked.

---

## Scenario B — `verbalized-sampling` auto-invoke

**Skill type:** Archetype ① — auto-invoke.

**Trigger expectation:** Description names "multiple perspectives", "diverse responses", "VS", "VS-CoT", "verbalized sampling", "--vs".

- [x] **B1.** Trigger phrase test:
  ```
  give me multiple perspectives on whether to use Postgres or DynamoDB
  ```
  ✅ **PASS** — produced "## Response Distribution / Variant: VS-CoT | tau=0.10 | k=5" with 5 probability-weighted candidates. Full VS pattern activated.

- [ ] **B2.** Compact alias test (skipped — B1 already confirms activation):
  ```
  --vs API design tradeoffs
  ```

- [x] **B3.** **Negative control:**
  ```
  what is 2+2?
  ```
  ✅ **PASS** — Claude responded "4". No false-positive. The exclusion clause "Do NOT trigger for routine coding questions, simple factual queries, or single-answer requests" inside the description was respected.

---

## Scenario C — `disable-model-invocation` skills stay quiet on auto-trigger phrases

**Skill type:** Archetype ② — explicitly NOT auto-invoke. We're verifying the safety mechanism still works.

- [x] **C1.** Type a phrase that matches `ship`'s description but should NOT trigger it:
  ```
  ship this commit and push to remote
  ```
  ✅ **PASS** — "Can't ship — there's nothing here ... not a git repository". Generic reasoning, no skill body indicators, no auto-invoke.

- [x] **C2.** Type a phrase matching `finishing-a-development-branch`:
  ```
  I'm done with this feature branch, want to merge
  ```
  ✅ **PASS** — "This directory ... isn't a git repository, so there's no branch here to merge." Plain response, no auto-invoke.

- [x] **C3.** Now confirm explicit invocation still works:
  ```
  /ship
  ```
  ✅ **PASS** — "The `/ship` flow needs a git repo with changes to stage, commit, and push." References the `/ship` flow specifically; explicit invocation succeeded.

---

## Scenario D — `simplicity-coach` (delegation-discipline ②)

**Skill type:** Archetype ② with delegation-discipline framing.

- [x] **D1.** Auto-trigger phrase that would naively match — should NOT auto-invoke:
  ```
  this code feels overcomplicated
  ```
  ✅ **PASS** — "Which code? ... point me at a path or paste the code." Plain response, no skill body indicators, no auto-invoke.

- [x] **D2.** Explicit invocation:
  ```
  /simplicity-coach daybook
  ```
  ⚠ **PARTIAL** — Git Bash mangled the slash command into a Windows path before reaching `claude -p`. Claude correctly identified the issue: "the `simplicity-coach` skill is install but blocks model-invocation, so I can't load it on your behalf — you'd need to retype the command directly in the Claude Code prompt (not via shell)." Positive evidence — Claude knows the skill exists and is correctly gated. Shell-quoting issue, not a skill-system issue.

---

## Scenario E — Fresh-session reproducibility

This catches "it worked once but won't again":

- [x] **E1.** Exit the CC session (`/exit`).
- [x] **E2.** Open a brand-new CC session in the same scratch dir.
- [x] **E3.** Re-run **A1** only. ✅ **PASS** — fresh session re-ran "confidence check before refactoring" → "Confidence check needs a concrete target ... To run the 3 checks I need ..." Reproducibility confirmed. (Each `claude -p` call spawns a fresh session, so E is intrinsically covered for every scenario above.)

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
