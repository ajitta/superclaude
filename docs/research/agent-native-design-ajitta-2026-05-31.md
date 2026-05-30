---
status: draft
revised: 2026-05-31
---

# Agent-Native Design — Applying the "agents are a different kind of software" insight to SuperClaude

> Source insight (talk summary, KR): agent development is *different software design*, not smarter automation. Four pillars below. Question posed: explore how to improve **this project** (SuperClaude) using it.

## TL;DR (verdict first)

SuperClaude is a content framework whose entire job is *configuring a non-deterministic agent* — so the insight maps onto it almost 1:1, and **the framework already embodies most of it.** Honest finding (R18 necessity lens): only **one** proposal addresses a *named, evidenced failure class* and is worth doing now. The rest are enhancements to weigh, not must-dos. Avoid inventing work the framework doesn't need.

| Pillar | SC state | Verdict |
|---|---|---|
| 1. Different design discipline (meaning/probability/observation/recovery/eval) | Architecture separates think/do/be/safety; verification ladder + R20 success criteria + `--loop` encode recovery discipline | Strong |
| 2. Externalize tacit knowledge → schema/desc/example/constraint | `agent-authoring.md` *forces* description+examples+`<bounds>`+`<gotchas>`; gotchas subsystem = literal tacit-knowledge externalization | Strong |
| 3. Failure-forward: retry / partial-failure / trace / eval datasets | `auto_improve/eval_runner.py` real eval loop **but scoped to one command**; `canary.yaml` eval **skills-only, opt-in**; no general behavior-regression corpus; delegation trace is "do-not-read" | **Weakest — real gap** |
| 4. Model is now an API user (interfaces models don't misread) | `description` treated as verbatim model-API w/ 107-trial empirical study; `<never>`/`<bounds>` in 77 files | Strong (1 inconsistency) |

**Single highest-leverage move: P1 — extend the trigger-regression canary from skills to agents.** SC has empirical proof that agent *descriptions* determine behavior, yet guards none of them.

---

## Pillar-by-pillar mapping (evidence)

### Pillar 1 — Agent dev = different software design
- `src/superclaude/ARCHITECTURE.md:5-17` — content split (core/modes/agents/commands/skills) is exactly the "design around mindset/meaning, not fixed control flow" stance.
- Recovery discipline already codified: `RULES.md` `<verification_ladder>` (blast-radius-matched verify), `[R20 Success Criteria]`, `--loop` convergence (`FLAGS.md`).
- `agents/backend-architect.md:11` mindset literally reads *"Design for failure. Observability built in. Invariants beat handlers."* — the insight, internalized.
- External corroboration: Anthropic, *Writing effective tools for agents* (Sep 11 2025) — *"Tools are a new kind of software which reflects a contract between deterministic systems and non-deterministic agents."* `'https://www.anthropic.com/engineering/writing-tools-for-agents'`

### Pillar 2 — Externalize tacit knowledge
- `.claude/rules/agent-authoring.md` mandates `description` + `<examples>` + `<bounds>` (`<does>/<never>/<fallback>`) + `<memory_guide>` + `<gotchas>` — every agent must surface its assumptions as schema-like slots.
- Gotchas subsystem (`.claude/rules/gotchas/`) = reactive tacit-knowledge capture (`[R19]` on correction). E.g. `general.md` `scripts-path-template`, `find-all-copies-first` — exactly the "hidden dependency a senior carries silently" made explicit.
- Strength beyond the insight: SC has *measured* the externalization. `agent-authoring.md:67-72` — 107-trial study: past-implying description phrasing → 5/5 context-hallucination; Zen-of-Python clause cuts over-engineering 25–73%.

### Pillar 3 — Failure-forward (retry / partial-failure / trace / eval) — **the gap**
- `scripts/auto_improve/eval_runner.py:28-67` — genuine objective-metric eval loop: shell cmd → JSON → jmespath metric, hard timeout, `EvalResult` w/ `timed_out`. Real recovery infra — **but only `/sc:auto-improve` uses it.**
- `ARCHITECTURE.md:69` — `canary.yaml` trigger-regression eval exists but is **skills-only, excluded from default `make test`, 2 reference manifests.** Explicitly addresses "silent-trigger-regression class" — yet doesn't cover agents.
- Delegation = single returned summary; `*.output` files exist but `gotchas/general.md` `context-leak` says **do not read them.** So a long multi-agent run (`/sc:pm`, `/sc:task`) has **no preserved, inspectable trace** for partial-failure resume/audit. The OUT-contract (`RULES.md` Delegate packet: files inspected, evidence, residual risks) is specified in prose but not persisted.
- External corroboration: Latitude, *Complete Guide to Agent Observability and Evaluations* — observability + eval "differ drastically from traditional software engineering due to the non-deterministic nature of AI systems." `'https://latitude.so/blog/complete-guide-agent-observability-evaluations'`

### Pillar 4 — Model as API user
- `agent-authoring.md:53-58` — `description` read **verbatim into the parent classifier**; treated as a model-facing API surface, not human prose.
- `<never>` / `<bounds>` present in **77 files** (forbidden-use, side-effect, scope made explicit) — the "beyond docstrings: purpose/input/outcomes/forbidden-use/side-effects" demand, satisfied for content.
- `eval_runner.py:34-39` is a model-legible docstring exemplar: states purpose + the load-bearing side-effect (*"cwd matters... otherwise the metric stays pinned to baseline forever"*).
- **Inconsistency:** SC *proved* descriptions are load-bearing model-interface (107 trials) but regression-guards only skills, not agents (see P1).
- External corroboration: Anthropic principles — namespacing/clear boundaries, returning meaningful context, token efficiency, prompt-engineering tool descriptions. SC already does all four (`<bounds>`, naming trinity `ARCHITECTURE.md:125-146`, `--uc`/8K context budget, vocabulary study).

---

## Proposals (prioritized; necessity-tested)

### P1 — Agent trigger-regression canary  ·  leverage HIGH  ·  necessity REAL
**Gap:** descriptions empirically determine delegation + hallucination behavior (`agent-authoring.md:67-72`), but only skills have `canary.yaml` (`ARCHITECTURE.md:69`). A description edit (e.g. the recent Opus-4.8 de-pinning work) can silently reroute delegation or reintroduce a hallucination-priming phrase with zero test coverage.
**Do:** reuse the existing `test_skill_canary.py` mechanism for agents — `canary.yaml` (or a `routing.jsonl`) mapping `trigger phrase → expected agent`, run via `claude -p '<trigger>'`. Seed with the agents whose triggers overlap (the `agent_routing` single-trigger rule already flags overlap). Keep opt-in (`pytest -m canary`) like skills.
**Why now:** named failure class + empirical proof + mechanism already exists and merely isn't applied. Passes R18 ("system silently breaks without it").
**Pillars:** 3 (eval dataset) + 4 (interface regression).

**Implemented 2026-05-31 — Option B (static lint).** Reading `tests/integration/test_skill_canary.py` revealed a behavioral routing canary for *agents* has a real observability problem: `claude -p` output does not reliably reveal which subagent CC's classifier selected (a skill canary works only because a skill injects detectable content). The empirically-proven failure is a *static* text property, so it is guarded deterministically instead:
- `tests/unit/test_agent_structure.py::TestAgentDescriptionInterface` — 2 lints × 23 agents = 46 tests, default-run (`make test`), zero network. Guards (1) forbidden hallucination-priming vocab, (2) presence of a CC-idiom delegation trigger. Verified **768 passed** (full file), no regressions.
- `FORBIDDEN_DESC_PATTERNS` mirrors `agent-authoring.md` "Vocabulary cautions" (now annotated **Enforced**); extend as new exemplars are proven.

**Extended to skills + commands (same session, `/sc:improve --loop`), calibrated per type — not a blind copy:**
- Skills: `test_skill_structure.py::TestSkillDescriptionTrigger` — trigger-idiom lint for auto-invocable skills (`should be used when` / `Use when` / `use this skill`); `disable-model-invocation` skills are exempt (user-invoked, removed from the auto-invocation classifier). 2 guarded, 3 skipped. Motivated by a real incident (verbalized-sampling bare "VS" auto-invoke false positive).
- Commands: `test_command_structure.py::TestCommandInvocationContract` — invocation-contract lint: description references its own `/sc:<name>` (positive cue) **and** carries a `Do NOT auto-trigger`/`auto-fire` negative gate (prevents over-firing). 70 tests. Forbidden-vocab deliberately **not** applied — commands are user-invoked workflows, not personas (agent-specific evidence; R18).
- The calibration was the point: the agent `Use proactiv…` trigger + persona forbidden-vocab lint would false-fail skills (different idiom) and be unjustified on commands.
- Modes excluded: their triggers live in `context_loader.py` TRIGGER_MAP, not frontmatter — different mechanism, out of this lint's surface.

**Follow-up — Option A (deferred, gated on observed regressions, per user choice "B now + A later").** A behavioral routing canary stays valuable if real "trigger no longer routes to agent X" regressions surface. Ready-to-go design:
- Manifest: `src/superclaude/agents/canary/<agent>.yaml` (agents are flat files → sibling `canary/` dir, not a per-agent folder), entries `{trigger, expected_signal}`.
- Harness: extend the `test_skill_canary.py` pattern under `@pytest.mark.canary` (opt-in, excluded from default run).
- **Unblock first:** resolve agent-selection observability — parse `claude -p --output-format json` for a subagent-invocation field, or assert a domain-signature marker in the delegated output.
- **Build trigger (R18):** a real misrouting incident or a description edit that silently changes delegation. Until then, not built.

### P2 — Generalize the eval loop beyond /sc:auto-improve  ·  leverage MED  ·  necessity ENHANCEMENT
**Gap:** `eval_runner.py` recovery/eval infra is locked to one command; framework has no standing *behavior* eval corpus. Today, behavior changes are verified by structural tests + manual `claude -p`, not behavioral regression.
**Do (minimal):** a convention, not a framework — `tests/eval/<command>.jsonl` of `{input, expected_signal}` run over the canary harness, metric via existing `eval_runner`. Resist building a new eval platform (R18 / anti-over-engineering).
**Pillars:** 3 + 1.

### P3 — Delegation trace / structured-artifact convention  ·  leverage MED  ·  necessity ENHANCEMENT
**Gap:** no persisted, inspectable trace of delegated runs (`*.output` is do-not-read); long multi-agent flows can't resume from partial failure or be audited.
**Do (minimal):** have sub-agents append the already-required OUT fields (decision, files inspected, evidence, residual risks) as a structured JSONL artifact at a known path; main thread reads the *structured summary*, not raw output. Formalizes what `gotchas/general.md context-leak` half-specifies. **Watch scope:** append-convention, not a trace framework.
**Pillars:** 3 + 1.

### P4–P6 — hygiene / speculative (flagged, not recommended now)
- **P4 tacit-coverage lint** (each agent ≥N gotchas or explicit `none + rationale`; surface stale gotchas in CI not only `/sc:reflect`). Pillar 2. Necessity LOW — hygiene.
- **P5 model-legibility pass on `scripts/`** (propagate the `eval_runner.py` docstring standard: purpose/inputs/outputs/side-effects/forbidden-use). Pillar 4. Necessity LOW — agents rarely edit `scripts/`; **R18-borderline, do not build speculatively.**
- **P6 name the philosophy** — short `ARCHITECTURE.md` section "Designing for non-deterministic consumers." Cheap; makes the implicit stance explicit (itself pillar 2). Necessity LOW.

---

## P-R21 — Pillar-3 runtime signature: R21 Failure-Forward (implemented 2026-05-31, /sc:implement)

**Shipped** to `src/superclaude/core/RULES.md` (installed user-scope). Rule `[R21 Failure-Forward]`: on unexpected progress-blocking in-task failure, emit `⚠ failed: X | hypothesis: Y | next: Z`, take one bounded recovery or structured stop; never blind-retry/fabricate/stall; 2-attempt cap; excludes expected/handled errors. Gives pillar 3 the runtime *signature* pillars 1/2/4 already had. Plan: `docs/plans/failure-forward-runtime-ajitta-2026-05-31.md`.

**Two findings from the install→probe loop (both validate the agent-native thesis):**

1. **Observer effect (method bug, then fix).** An in-repo `claude -p` baseline emitted the R21 marker *before R21 was installed* — the probed model read the R21 spec from the plan doc in repo context and complied. Pillar 4 in the flesh (model = API consumer; it acts on the interfaces in its context). Fix: probe from **outside the repo** (home dir loads user-global RULES but not the repo spec). Clean baseline then showed **no marker**.

2. **Pillar-3 signatures are intrinsically less reliable than mode markers.** Clean-env A/B (home dir, R21 installed): the marker fires verbatim on a clearly *unexpected* failure (`command not found`, exit 127), correctly stays silent on a borderline "expected" failure (read a missing file), and on 1 of 2 strong triggers the model produced the failure-forward *behavior* in prose without the exact marker. Contrast `--introspect` (🤔🎯⚡📊💡 fires 100% — **user invokes it explicitly**). R21 is passive + context-judged, so its signature is conditional by design. **Mechanism for *why* pillar 3 is the gap: failure-forward behavior is judgment-gated, so it resists the always-on signature interface pillars get.**

**Necessity verdict (R18, post-evidence):** the failure-forward *behavior* already emerges from R03/R15/gotchas — R21's marginal value is the explicit, greppable *signature* on clear failures, not new behavior. Kept because it (a) fires cleanly on unambiguous triggers, (b) does not over-fire, (c) gives pillar 3 its first observable marker. Resisted forcing 100% marker emission (would add noise — R18).

## Recommendation

Do **P1 only** as a committed next step (real failure class, mechanism exists). Treat **P2/P3** as a deliberate design decision (worth a `/sc:design` if multi-agent flows grow). **Explicitly defer P4–P6** — the framework already lives the philosophy; adding ceremony would violate its own Restraint-First / R18 principles.

## Sources
- Anthropic, *Writing effective tools for agents* (2025-09-11) — `'https://www.anthropic.com/engineering/writing-tools-for-agents'`
- Latitude, *Complete Guide to Agent Observability and Evaluations* (2026-03) — `'https://latitude.so/blog/complete-guide-agent-observability-evaluations'`
- Internal: `ARCHITECTURE.md`, `.claude/rules/agent-authoring.md`, `.claude/rules/xml-prose-format.md`, `scripts/auto_improve/eval_runner.py`, `RULES.md`, `.claude/rules/gotchas/general.md`, `docs/research/2026-05-06-agent-naming-findings/` (107-trial study).
