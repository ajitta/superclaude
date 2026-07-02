---
status: draft
revised: 2026-07-03
---

# Utility Improvement Roadmap — Post Model-Advance Reassessment

> **Origin:** 2026-07-02~03 Cowork session (Fable 5). Three converging evidence sources: (1) live hook execution tests run in-session, (2) the repo's own audit `../analysis/superclaude-audit-vs-superpowers-ajitta-2026-06-05.md`, (3) an external model assessment (user-supplied, figures independently re-verified within ±10%). Phase 0-1 **shipped in the same session** (see below).

**Goal:** Shift the framework's weight from "behavior engineering via always-loaded prose" (value eroding as model defaults converge with the rules) toward the three layers where value is model-independent: hard guardrails, project-specific knowledge (gotchas/conventions), and tooling — with every slimming decision gated by measurement, per R18.

**Core diagnosis (evidence-anchored):**

- Enforcement layer is real but narrow: `destructive_guard` covered exactly 3 patterns; live test showed `git push -f origin main`, `git reset --hard`, `git clean -fdx` all sailed through (2026-07-02 session). `loop_guard` verified spec-exact (5-error block, per-signature scope, success reset).
- Standing token tax is core-only: FLAGS+PRINCIPLES+RULES ≈ 28KB / ~7.4k tokens per session (chars/3.8 estimate) + ~817 tokens/prompt context_loader injection. The on-demand corpus (commands/agents/skills/modes ≈ 80k tokens) is pay-per-use, NOT standing cost — don't conflate the two when prioritizing cuts.
- Prose-model convergence observed live: R15/R21-equivalent behavior manifested in a session where RULES.md was *not* loaded; the gotchas file, by contrast, demonstrably changed behavior (subagent-summary revalidation). Gotchas layer = the one prose layer with observed ROI.

---

## Phase 0 — Immediate fixes

### 0-1. destructive_guard coverage patch — **DONE 2026-07-03 (this session)**

- Regex widened: force-push to main/master now caught via `--force` OR standalone `-f`, flag and branch in any argument order (original ordering also missed `git push origin main --force`). `--force-with-lease` still allowed by construction; `\b(main|master)\b` word-bounded (strictly fewer false positives than before — old pattern matched `mainline`).
- `tests/unit/test_safety_hooks.py`: +5 block cases (live-test bypasses), +3 allow cases (false-positive guards).
- Verified: 22-case matrix (11 block / 11 allow) → 22/22 pass in isolated run. **Full `uv run pytest tests/unit/test_safety_hooks.py` on the Windows baseline still pending** (sandbox mount lag prevented in-session suite run).

### 0-2. Enforcement-vs-prose boundary paragraph (open)

One README/ARCHITECTURE paragraph: "mechanically enforced = 3 hooks (file_size / destructive / loop); everything else is model-followed prose." Closes audit P3's residual documentation gap. Cost ≈ 0.

### 0-3. Warn-tier for reversible-but-risky commands (open question, do NOT rush)

`git reset --hard` / `clean -fdx` / `branch -D` are legitimate often enough that hard-block is wrong. Candidate mechanism: PreToolUse `hookSpecificOutput.permissionDecision: "ask"` — **unverified** in this codebase (0 uses of the schema; CC version support unconfirmed). Verify schema support first; otherwise skip — CC's native Bash permission prompt already covers this tier.

## Phase 1 — Measurement infrastructure (gates everything below)

### 1-1. 4-arm eval harness

Arms: vanilla / SC-full / SC-core-lite / SC-command-only. Built on the existing `make sync-user` + headless `claude -p` path (reuse, not new infra). Tasks (7): small bugfix (scope-creep check), doc creation (naming convention), install scope change, destructive-command elicitation, large-file analysis, plan routing (docs/features vs docs/plans), review (file:line accuracy). Metrics: success rate, unnecessary file changes, actual-verification-ran, output location accuracy, tokens, user interventions, wrong auto-command activations, **gotcha compliance rate**.

### 1-2. Model-release canary (new proposal, not in prior audits)

Pin ~10 eval tasks as a canary suite auto-run on each new model release. Converts the recurring per-release "compat polish" cost (evidence: Opus 4.8 alignment commits) from reactive guessing to detected diffs: "which prose rules died on this model" becomes a report, not a feeling.

## Phase 2 — Slimming, conditional on Phase 1 results

### 2-1. core-lite split

RULES.md ~5.5k tokens → always-loaded kernel ≤ 2k (scope discipline, no-completion-claim-without-verification, destructive-op confirmation, project-rules-priority) + on-demand modules routed by context_loader (mechanism already exists — this is routing-table extension, not new development). verification ladder → implement/review commands only; doc convention → doc-producing commands only.

### 2-2. Agent rewrite pilot (3 agents, not 23)

Top-3 most-used agents: strip generic persona (SOLID/OWASP/coverage boilerplate — model already knows), inject repo-specific ops knowledge (uv-only, stdlib-only hooks, tests/unit/scripts isolation, Windows traps). A/B against Phase 1 baseline before touching the remaining 20.

## Phase 3 — Structural (quarter horizon)

- **3-1. Subagent context gap mitigation (audit P2, harness-boundary):** add "active mode directives copy" field to the RULES.md delegate packet. Prose-level mitigation only; the context_loader/UserPromptSubmit limitation is not markdown-fixable.
- **3-2. Gotchas layer promotion:** the one prose layer with observed behavioral ROI. Keep R19 auto-capture; add gotcha-compliance metric to eval (see 1-1) to quantify.

## Explicitly rejected

- **Bulk XML-wrapper rewrite** (external assessment's suggestion): on-demand content carries no standing tax; regression risk across 79 files exceeds compression gain. Revisit per-file only if Phase 1 flags a specific agent's verbosity as a measured problem.
- **Slimming before measuring:** cutting core prose before the 4-arm eval exists would violate this repo's own R18 — if a rule was silently carrying behavior, we'd never know which one.

## Necessity (R18 — honest)

Phase 0-1 had a concrete failure scenario (live bypass demonstrated). Phase 1 is the prerequisite that makes every later cut evidence-based instead of vibes-based. Phases 2–3 are ENHANCEMENT class, explicitly conditional. Known risk: the eval harness adds maintenance surface to a one-maintainer fork — if it rots unmaintained, it becomes dead weight (superpowers ran 5 versions unmeasured; measurement infra is not self-justifying). Canary task selection bias could false-green prose cuts.
