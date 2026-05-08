---
title: Karpathy Guidelines × /sc:* Command Impact Analysis
type: analysis
author: ajitta
date: 2026-05-08
session: karpathy-skill-introspection
---

# Karpathy Guidelines × /sc:* Command Impact Analysis

> Empirical (source-grounded) analysis of how the `andrej-karpathy-skills:karpathy-guidelines` skill — when active — modifies the behavior of each `/sc:*` command in this fork.

## TL;DR

- **34 commands analyzed.** Karpathy guidelines are **mostly synergistic** with SuperClaude RULES; the 4 axes already overlap heavily with R03/R06/R12/R13/R15/R18/R20.
- **Highest-impact commands** (first-turn response visibly changes): `/sc:brainstorm`, `/sc:implement`, `/sc:improve`, `/sc:design`, `/sc:plan`, `/sc:troubleshoot`, `/sc:task`. All are scope-bearing or interpretation-bearing operations.
- **Lowest-impact commands** (zero behavioral delta): `/sc:help`, `/sc:sc`, `/sc:recommend`, `/sc:select-tool`, `/sc:explain` (read-only, no scope authority).
- **Native pattern match**: `/sc:auto-improve` is *literally named* the "Karpathy AutoResearch pattern" in its mission line. Skill activation is a no-op there because the command already implements the loop pattern.
- **One latent conflict**: Auto mode + karpathy "if uncertain, ask" pull opposite ways. Resolution rides on R12 reversibility branching (already in RULES).

> **Empirical update (2026-05-08, n=1 per condition)**: 4 commands tested via `claude -p` baseline vs karpathy-prefix runs. Major refinements below — full test in companion doc `karpathy-empirical-test-ajitta-2026-05-08.md`. Headline: 3 of 4 commands enter a **"refusal mode"** under karpathy strict — they detect a precondition violation (no evidence, deliverable already exists, etc.) and stop with a selection-protocol instead of executing. This pattern was not predicted by the static analysis.

---

## Methodology

### Source

Each `/sc:*.md` was read in full from `src/superclaude/commands/`. Analysis cites command sections by tag (`<flow>`, `<bounds>`, `<gotchas>`, etc.) so claims are verifiable.

### Karpathy 4 axes

| Axis | Question | Maps to RULES |
|---|---|---|
| **TBC** — Think-Before-Coding | Does the command surface assumptions / present alternatives / ask when unclear? | R03 (3+ hypotheses), R12 (Clarification), R13 (Intent Verification) |
| **SF** — Simplicity-First | Does the command resist speculative scope, prefer minimum-viable, refuse "safer/better"-only justification? | R06 (Scope), R18 (Necessity Test) |
| **SC** — Surgical-Changes | Does the command bound edits to what was asked, no adjacent cleanup? | R06 (Scope), `<anti_over_engineering>` |
| **GDE** — Goal-Driven-Execution | Does the command translate task into a verifiable success criterion / loop until met? | R15 (Verification Ladder), R20 (Success Criteria), `<workflow_gates>` |

### Verdict scale

- ✅ **Reinforce** — command already has logic on this axis; karpathy strengthens it (existing rule fires harder)
- ✅✅ **Strong reinforce** — multiple existing hooks fire harder; first-turn response shape changes
- ✅✅✅ **Refusal mode** *(empirical addition)* — karpathy promotes an advisory `<gotcha>` to a hard gate; command stops before executing, presents selection-protocol options. Observed in design/troubleshoot/task under karpathy strict prefix.
- ⚪ **No-op** — axis doesn't engage this command's domain (e.g., read-only commands are inherently SC-trivial)
- ⚠️ **Conflict** — karpathy would push against existing command behavior (none observed in this analysis; flagged if found)

---

## Domain Buckets

To keep the analysis tractable, commands are grouped by what they produce. Karpathy's effect varies by bucket.

| Bucket | Commands | Karpathy salience |
|---|---|---|
| **Discovery / spec** | brainstorm, design, plan, workflow, spec-panel, business-panel, estimate | High — scope-defining work |
| **Code mutation** | implement, build, improve, cleanup, troubleshoot, auto-improve, test | High — scope discipline matters |
| **Read-only analysis** | analyze, review, explain, document, index, index-repo | Medium — TBC for inputs, SC inherent |
| **Session / memory** | load, save, reflect, insight, init | Medium — SC bounded by store, GDE for completeness |
| **Meta / dispatch** | help, sc, recommend, select-tool, agent, pm, task | Low — no code authority |
| **Workflow utilities** | git, research | Mixed — context-dependent |

---

## Master Matrix

| Command | Domain | TBC | SF | SC | GDE | Existing alignment cited |
|---|---|---|---|---|---|---|
| /sc:agent | Meta | ✅ | ✅ | ✅ | ✅ | `<task_protocol>` Phase 1-clarify; `<bounds>` impl below 0.90 blocked; `<gotchas>` scope-leak |
| /sc:analyze | Read-only | ✅ | ✅ | ⚪ | ✅ | `<gotchas>` evidence-fabrication; severity classification; `<bounds>` "never modify code" |
| /sc:auto-improve | Code-mut | ✅ | ✅ | ✅ | ✅ | Mission line: "Karpathy AutoResearch pattern"; isolated worktree; metric-driven |
| /sc:brainstorm | Discovery | ✅ | ✅ | ⚪ | ✅ | Socratic flow step 1; `<bounds>` discovery only; spec acceptance gate (5-7) — **empirical: baseline already 70% karpathy-shape, skill effect is citation-tightening not shape-change** |
| /sc:build | Code-mut | ✅ | ⚪ | ✅ | ✅ | Validate env step 2; `<bounds>` never modify config; build success/fail evidence |
| /sc:business-panel | Read-only | ✅ | ✅ | ⚪ | ✅ | `<gotchas>` opinion-as-fact; synthesis required; `<bounds>` "never decide for user" |
| /sc:cleanup | Code-mut | ✅ | ✅ | ✅ | ✅ | `--safe`/`--dry-run`; `<gotchas>` scope-check + verify-unused; tests-pass post |
| /sc:design | Discovery | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅ | Flow step 5: explicit R18 per component; `<bounds>` never modify existing arch; ≥90% req coverage — **empirical: refusal mode — `existing-check` gotcha promoted to hard gate** |
| /sc:document | Read-only | ✅ | ✅ | ✅ | ✅ | Audience identification; `<gotchas>` no-unsolicited; coverage metrics per --type |
| /sc:estimate | Discovery | ✅ | ✅ | ⚪ | ✅ | `<gotchas>` scope-assumptions explicit; no-time-estimates; confidence intervals |
| /sc:explain | Read-only | ✅ | ✅ | ⚪ | ⚪ | Audience-level assess step 2; `<gotchas>` serena-first; pure read-only |
| /sc:git | Workflow | ✅ | ⚪ | ✅ | ✅ | Validate operation appropriateness step 2; `<safety_rules>` approval_required; PR state evidence |
| /sc:help | Meta | ⚪ | ⚪ | ⚪ | ⚪ | Display-only; bounds: never execute/modify |
| /sc:implement | Code-mut | ✅✅ | ✅✅ | ✅✅ | ✅ | Step 2 "simplest viable"; step 3 checkpoint >3 files; step 5 phase-gate skip-if-solved; `<gotchas>` scope-discipline + scope-creep example |
| /sc:improve | Code-mut | ✅ | ✅✅ | ✅✅ | ✅ | `<gotchas>` necessity-test (R18) + unchanged-code; functionality-preserved validate |
| /sc:index | Read-only | ✅ | ✅ | ✅ | ✅ | Token-budget gotcha; preserve `<!-- MANUAL -->`; coverage ≥80% |
| /sc:index-repo | Read-only | ✅ | ✅ | ✅ | ✅ | 94% reduction target; never modify source; <5KB metric |
| /sc:init | Session | ✅ | ✅ | ✅ | ✅ | Interactive task menu (always asks); idempotent; `<safety_rules>` confirmation gates |
| /sc:insight | Session | ✅ | ✅ | ✅ | ✅ | Dedup before propose; script-only-writes; append-only schema validation |
| /sc:load | Session | ✅ | ⚪ | ✅ | ✅ | Verify path; `<gotchas>` stale-memory; context-integrity validate |
| /sc:pm | Meta | ✅ | ✅ | ✅ | ✅ | Classify complexity; `<gotchas>` direct-work-first + intent-propagation; PDCA |
| /sc:plan | Discovery | ✅ | ✅✅ | ✅✅ | ✅✅ | `<gotchas>` existing-plan + scope-match; `<size_note>` <15KB; TDD task verification commands |
| /sc:recommend | Meta | ✅ | ✅ | ⚪ | ⚪ | `<gotchas>` simplicity-bias + flag-match; never execute |
| /sc:reflect | Session | ✅ | ✅ | ⚪ | ✅ | Step 2.5 misunderstanding-audit; step 3.5 gotchas-gardening; `<gotchas>` evidence-required |
| /sc:research | Workflow | ✅ | ⚪ | ⚪ | ✅ | Success-criteria step 1; cross-source verification; depth-profile constraint |
| /sc:review | Read-only | ✅✅ | ✅ | ✅ | ✅ | Step 4 "Challenge" (what could fail); `<gotchas>` no-unsolicited-fixes; evidence per artifact |
| /sc:save | Session | ✅ | ✅ | ✅ | ✅ | Step 3.5 corrections-review; `<compaction_strategy>` discard low-signal; data-integrity validate |
| /sc:sc | Meta | ⚪ | ⚪ | ⚪ | ⚪ | Pure dispatcher; routes only |
| /sc:select-tool | Meta | ✅ | ✅ | ⚪ | ✅ | Multi-dim scoring; `<gotchas>` native-first + mcp-justify; <100ms decision |
| /sc:spec-panel | Discovery | ✅ | ✅ | ✅ | ✅ | Multi-mode review; `<gotchas>` necessity-test (R18); never modify without consent |
| /sc:task | Meta | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅ | Step 4 checkpoint >3 files; `<gotchas>` task-count 3-7 max + already-done; completion verification — **empirical: refusal mode + caught a baseline rule violation (Run A skipped >3-file checkpoint and created 4 files unprompted)** |
| /sc:test | Code-mut | ✅ | ✅ | ✅ | ✅✅ | TDD RED-GREEN-REFACTOR pattern (--tdd); baseline-first gotcha; never modify framework config |
| /sc:troubleshoot | Code-mut | ✅✅✅ | ✅✅✅ | ✅✅ | ✅✅ | Reproduce step 1 (R03 alignment); 3+ hypotheses cap; "no while-I'm-here fixes"; failing-test-passes gate — **empirical: refusal mode — `evidence-fabrication` gotcha → 0 hypotheses without file:line evidence** |
| /sc:workflow | Discovery | ✅ | ✅ | ✅ | ✅ | Parse PRD step 1; `<gotchas>` scope-match + step-granularity (independently verifiable) |

**Legend**: ✅ Reinforce, ✅✅ Strong reinforce (multiple existing hooks fire), ✅✅✅ Refusal mode *(empirical, n=1)*, ⚪ No-op, ⚠️ Conflict (none observed).

**Aggregate**: 0 conflicts, ~32 reinforce-or-strong, ~38 no-ops (mostly SC for read-only, GDE/SF for dispatchers). **Empirical addition**: 3 commands (design, troubleshoot, task) confirmed refusal-mode under karpathy strict; pattern likely generalizes to other ✅✅ commands but not yet tested.

---

## Per-Command Behavioral Delta

For each command, the **first-turn response shape** difference when karpathy is active. Only commands with non-trivial delta are expanded; trivial cases collapsed to a single line.

### Discovery / spec bucket

#### /sc:brainstorm
**Delta — moderate** *(empirical revision: was "strong" pre-test)*:
- Without karpathy: "I see two interpretations — A) ..., B) ... — which is closer?" (Already alternative-surfacing.)
- With karpathy: same alternatives + ★ recommended marker + selection-protocol `select: A/B/C` format + explicit `R13/R18/R20/Karpathy 1` citations + silent-pick refusal phrasing.
- **Why**: TBC #1 + GDE #4 layer onto an already-Socratic command. **Empirical finding**: baseline already covers ~70% of the predicted shape — the actual delta is *citation-explicitness* and *protocol formalization*, not behavioral redirection. Source: companion empirical doc Test 1.

#### /sc:design
**Delta — strong + refusal mode** *(empirical revision: was "moderate" pre-test)*:
- Without karpathy: applies R18 necessity test per component; `<gotchas>` `existing-check` cited softly. **Run A actually skipped existing-check** and wrote a fresh spec.
- With karpathy: `existing-check` becomes a hard gate. **Run B refused to re-execute** when prior same-day spec was found, presented 4-option selection-protocol (overturn / refine / overwrite / cancel), framed each option with explicit "delta criterion" requirement.
- **Why**: SF #2 + SF #3 ("surgical, traces to request") force the gotcha to fire; "overwriting equivalent same-day artifact = churn" was Run B's exact phrasing. Source: companion empirical doc Test 2.

#### /sc:plan
**Delta — strong**:
- Without karpathy: phase decomposition; `<gotchas>` scope-match flagged
- With karpathy: rejects scope expansion *more* eagerly; each phase task gets a verify-step (already in `<templates>`); "while we're at it" sub-tasks get filtered out. SF #3 + SC layered on existing scope-match gotcha.

#### /sc:workflow
**Delta — small**: workflow already requires scope-match; karpathy reinforces step-granularity (each step independently verifiable = GDE #4). No first-turn shape change.

#### /sc:spec-panel, /sc:business-panel
**Delta — small**: panels remain multi-expert. Karpathy adds a soft preference for **Hickey** (essential complexity) and **Beck** (incremental design) over more speculative experts when no `--experts` specified.

#### /sc:estimate
**Delta — small**: already says "make scope assumptions explicit"; karpathy strengthens that to "*and present alternatives if scope has 2+ valid readings* before estimating".

### Code-mutation bucket

#### /sc:implement
**Delta — strong** (largest in this bucket):
- Without karpathy: Phase Gate at step 5 ("does this already solve next phase?") is advisory
- With karpathy: Phase Gate becomes load-bearing — answer it explicitly per phase, not silently. Step 2 "simplest viable" becomes mandatory pre-build verbalization, not implicit. SF #2 ("no features beyond what was asked") + SC ("every changed line traces directly to user request") fire on every adjacent file touched.
- **Source**: `<flow>` steps 2, 5; `<gotchas>` scope-discipline; scope-creep example (`<example name="scope-creep">`).

#### /sc:improve
**Delta — strong**:
- Without karpathy: necessity-test gotcha + unchanged-code gotcha already present
- With karpathy: the gotchas become first-class refusal triggers. "safer/better" framing for unrequested improvements gets explicit pushback ("System works without this. No failure scenario → SKIP").
- **Source**: `<gotchas>` necessity-test, unchanged-code.

#### /sc:troubleshoot
**Delta — strong + refusal mode** *(empirical confirmation: highest alignment in bucket)*:
- Already karpathy-shaped: reproduce → 3 hypotheses → confirm → failing test → single fix → verify.
- With karpathy active: `<gotchas>` `evidence-fabrication` becomes absolute. **Run B produced 0 hypotheses** when no auth code was found in the target repo — explicitly stated "file:line 증거 0건 → 가설 0건". Refused even general checklists. Pre-stated R20 success criterion (t=4min/t=6min reproduction test) before any fix.
- **Compare**: Run A (baseline) softly cited evidence-fabrication but produced 6 hypotheses anyway, framing them as "통계적 추측". Karpathy promotes the soft cite to a hard refusal.
- **Source**: `<flow>` steps 3, 6; `<gotchas>` evidence-fabrication; companion empirical doc Test 3.

#### /sc:cleanup
**Delta — moderate**:
- Without karpathy: --safe is recommended for unfamiliar code (gotcha aggressive-without-review)
- With karpathy: --safe + --dry-run becomes the default suggestion when codebase familiarity isn't established. SC #3 ("don't remove pre-existing dead code unless asked") aligns directly with `<auto_fix_threshold>`.

#### /sc:build
**Delta — small**: build is mechanical. Karpathy adds: when a build fails, **don't retry without diagnosing** (already in error-path example), and don't try "small adjacent fix" — pause for diagnosis. Already-aligned.

#### /sc:test
**Delta — moderate**:
- The `--tdd` mode literally is karpathy GDE #4: RED → GREEN → REFACTOR is the canonical "translate to verifiable goal" pattern.
- Without flag: karpathy adds "what *failing test* proves done?" framing even when --tdd not set, raising the GDE bar.
- **Source**: `<patterns>` TDD line.

#### /sc:auto-improve
**Delta — none** (already maxed out): mission line cites "Karpathy AutoResearch pattern" by name. Phase 0 confirm + isolated worktree + objective metric + single git lineage all match karpathy 4 axes natively. Activating the skill changes nothing.

### Read-only analysis bucket

#### /sc:analyze
**Delta — small**: evidence-fabrication gotcha already enforces TBC. With karpathy: severity classifications get challenged harder ("is this 🔴 because of an actual failure, or because the pattern looked risky?").

#### /sc:review
**Delta — moderate**:
- Step 4 "Challenge" is karpathy TBC #1 in disguise — already asks "what could fail / what's hardest to change in 6 months"
- With karpathy: more aggressive pushback in `<example name="pushback-protocol">` — defaults to YAGNI when reviewer suggests adding abstractions for "future flexibility".

#### /sc:explain, /sc:document, /sc:index, /sc:index-repo
**Delta — small to none**: read-only by `<bounds>`. Karpathy adds: prefer **shorter** explanations over comprehensive ones when audience is uncertain (SF #2). For document, the "no-unsolicited" gotcha aligns directly.

### Session / memory bucket

#### /sc:init
**Delta — moderate**:
- Already interactive (presents menu, awaits selection) — TBC #1 in form already
- With karpathy: when user selects task `(b)` without `(a)`, the prompt to "add prerequisite?" becomes more like "you'll need (a) — adding both, redirect if you want to skip". Bounded-proceed pattern.

#### /sc:insight
**Delta — small**: schema-validating script already enforces SC (append-only, never modify). Dedup-before-propose maps to TBC #1. No first-turn shape change.

#### /sc:reflect
**Delta — small**:
- Step 2.5 misunderstanding-audit is literally TBC retrospective (find moments where intent was misread)
- Step 3.5 gotchas-gardening is SF in maintenance form (prune stale)
- Karpathy active: misunderstanding-audit findings get higher priority for memory persistence.

#### /sc:save
**Delta — small**: corrections-review step 3.5 already aligned with karpathy. No shape change.

#### /sc:load
**Delta — small**: stale-memory gotcha is karpathy GDE-adjacent (verify before acting). Already aligned.

### Meta / dispatch bucket

#### /sc:agent
**Delta — moderate**:
- Phase 1 Clarify step already enforces TBC #1
- With karpathy: confidence ≥0.90 floor in `<task_protocol>` Phase 3 stays the same, but "speculate without research" prohibition fires more often — tendency to ask `@deep-researcher` over guessing.

#### /sc:pm
**Delta — moderate**:
- direct-work-first gotcha is karpathy SF (don't orchestrate <3-step tasks)
- intent-propagation gotcha is karpathy TBC (no re-interpretation)
- With karpathy: rejection of orchestration for borderline cases (4-step but cohesive) becomes more aggressive — "do directly, save the orchestration overhead".

#### /sc:task
**Delta — strong + refusal mode + baseline rule violation detected** *(empirical revision: was "moderate" pre-test)*:
- Step 4 checkpoint `>3 files → present numbered plan → wait for user approval` is in the source. **Run A skipped this checkpoint entirely** and created 4 files at the framework root unprompted. Empirical proof that gotchas can fail to fire in baseline.
- **Run B caught the duplicate** (Run A's `todo-app/`), refused new execution, presented 4-option selection-protocol (skip / review / overwrite / extend), specified default-on-silence behavior ("proceed" without picking → option 1 skip).
- **Why**: TBC #1 ("ask, don't pick silently") + SF #2 ("R18 fails — system isn't broken without intervention") combined to convert the >3-files checkpoint and already-done gotcha into a blocking gate.
- **Source**: companion empirical doc Test 4.

#### /sc:recommend, /sc:select-tool, /sc:help, /sc:sc
**Delta — none**: pure mappers/dispatchers. simplicity-bias gotcha in /sc:recommend already implements karpathy SF.

### Workflow utilities

#### /sc:git
**Delta — small**: `<safety_rules>` already gates destructive ops (force push, hard reset) on approval. Karpathy adds: don't suggest `--amend` as "clean up history" — every changed line should trace to user request, including commits.

#### /sc:research
**Delta — small**:
- `<flow>` step 1 already requires success-criteria up-front = GDE #4
- With karpathy: rejection of single-source claims becomes stricter, and "exhaustive" depth gets challenged ("do we actually need 5+ hops, or is 2 sufficient?") — SF on depth selection.

---

## Cross-Cutting Patterns

### 1. Karpathy ≈ RULES distilled
Karpathy's 4 axes correspond cleanly to existing RULES:

| Karpathy axis | Already enforced by |
|---|---|
| Think-Before-Coding | R03 (3+ hypotheses), R12 (Clarification), R13 (Intent Verification), R14 (Correction Capture) |
| Simplicity-First | R06 (Scope), R18 (Necessity Test), `<anti_over_engineering>` |
| Surgical-Changes | R06 (Scope), `<sub_agent_decision>` "Direct work" preference |
| Goal-Driven-Execution | R15 (Verification), R20 (Success Criteria), `<workflow_gates>` |

**Implication**: this fork's `core/PRINCIPLES.md` already cites the karpathy_lens cross-reference (lines 39-44). The skill activation is *additive emphasis*, not new rule content.

### 2. Where karpathy actually changes behavior
Three patterns in command bodies act as the "fire harder" levers:

- **Step-2 "simplest viable" verbalization** — present in /sc:implement; karpathy makes it mandatory pre-build, not implicit
- **Necessity-test gotchas** — present in /sc:improve, /sc:design, /sc:spec-panel; karpathy lowers the threshold for "defer/skip"
- **Scope-match gotchas** — present in /sc:plan, /sc:workflow, /sc:cleanup, /sc:implement; karpathy raises the bar for adjacent edits

Commands without these existing hooks (e.g., /sc:research, /sc:select-tool) don't change behaviorally — there's no surface for karpathy to amplify.

### 3. Already-karpathy-shaped commands
Three commands are de-facto karpathy implementations even before skill activation:

- `/sc:auto-improve` — explicitly named "Karpathy AutoResearch pattern"
- `/sc:troubleshoot` — flow steps 3-7 are textbook GDE (test → fix root cause → verify)
- `/sc:test --tdd` — RED-GREEN-REFACTOR is canonical GDE

### 4. Auto-mode interaction (only observed friction)
Auto mode says "Make reasonable assumptions, proceed on low-risk work". Karpathy #1 says "if uncertain, ask". The conflict is resolved by R12's reversibility branching:

- Reversible + low-risk → state assumption + proceed (karpathy #1 satisfied via "say so" + "push back when warranted" in subsequent turn)
- Irreversible / >3 files / security-bearing → ask (karpathy #1 strict mode)

No command body needs modification — the resolution is in RULES.md `<core_rules>` already.

### 5. Refusal mode — gotchas advisory→hard-gate *(empirical, 2026-05-08)*

The `/sc:*` commands carry `<gotchas>` (e.g., `existing-check` in design, `evidence-fabrication` in troubleshoot, `>3 files checkpoint` in task). Without karpathy:

- **Baseline runs treat gotchas as advisory** — they get cited softly or skipped entirely. Empirical: design Run A wrote a spec without checking for an existing one; task Run A created 4 files without the checkpoint; troubleshoot Run A produced 6 hypotheses without code evidence.

With karpathy strict prefix:

- **Gotchas become blocking gates.** Each Run B detected the precondition violation (artifact already exists / no evidence / deliverable already meets constraints) and *refused execution*, defaulting to a `<selection_protocol>`-formatted exit with 3-4 numbered options.
- **Default-on-silence is specified.** Run B (task) explicitly stated "proceed without picking → option 1 (skip)". This formalizes how the user redirects without re-stating the request.

This is qualitatively different from "tighter version of the same output" — it's a *new mode* the static analysis didn't surface. Reading the matrix: ✅✅✅ rows mark commands where this mode is observed in n=1 testing; pattern likely generalizes to other ✅✅ commands but is unconfirmed for /sc:implement, /sc:improve, /sc:plan, /sc:review.

---

## Key Findings

1. **Karpathy is a velocity-control on existing rules, not a new ruleset.** The fork's PRINCIPLES.md already cross-references it (`<karpathy_lens>` lines 39-44). Skill activation makes the velocity-control engage harder.
2. **Highest first-turn response delta**: `/sc:brainstorm` (alternatives + success criteria up-front) and `/sc:implement` (mandatory simplest-viable verbalization).
3. **Zero command body needs modification** to be karpathy-compliant. All 4 axes are already represented somewhere in the command corpus.
4. **No conflicts observed.** The only friction is auto-mode × ask-first, resolved by R12.
5. **Read-only commands are inherently SC-trivial** — bounds: never modify forces karpathy SC compliance. The 6 read-only commands (analyze, review, explain, document, index, index-repo) all score ⚪ on SC.
6. **Dispatchers are inherently no-op**: /sc:help, /sc:sc, /sc:recommend, /sc:select-tool route or display only — karpathy has no behavioral surface to engage.
7. **Latent recommendation**: if a future command author wants karpathy maximally applied, three ingredients yield it cheaply: (a) a step-2 "simplest viable" verbalization before action, (b) a necessity-test gotcha, (c) a scope-match gotcha. These three patterns capture ~80% of the skill's effect.
8. **Empirical: gotchas are advisory in practice, not actually-blocking.** Run A baselines repeatedly skipped the gotchas their own command files declared (`existing-check`, `>3 files checkpoint`, soft-cite of `evidence-fabrication`). This is a self-finding about *baseline rule compliance*, not just karpathy effects — worth tracking separately. Karpathy is one way to harden those gotchas into gates; another would be making them load-bearing in `<flow>` rather than `<gotchas>`.
9. **Empirical: when karpathy refuses, it exits via selection-protocol.** All 3 refusal-mode runs converged on the same exit shape — numbered options + default-on-silence. RULES.md's `<selection_protocol>` already specifies this format; karpathy just activates it more aggressively. No new format needed.

---

## Spot-Check Verification

To verify the matrix wasn't fabricated, re-validating 3 randomly selected commands by re-reading the source.

### Random pick 1 — /sc:brainstorm
- Claim: "Socratic flow step 1; `<bounds>` discovery only; spec acceptance gate (5-7)"
- Re-verify: `<flow>` step 1 = "Explore: Socratic dialogue + systematic questioning" ✅
- Re-verify: `<bounds>` `<does>` = "ambiguous→concrete...self-review precedes implementation handoff" ✅
- Re-verify: `<flow>` 5/6/7 = approve / self-review hard gate / decision-mode tagging ✅
- **Match: yes**

### Random pick 2 — /sc:troubleshoot
- Claim: "Reproduce step 1 (R03 alignment); 3+ hypotheses cap; 'no while-I'm-here fixes'; failing-test-passes gate"
- Re-verify: `<flow>` step 1 = "Reproduce: Confirm failure" ✅
- Re-verify: `<flow>` step 3 = "Form specific hypothesis...max 3 cycles before escalating" ✅
- Re-verify: `<flow>` step 6 = "single change addressing root cause — no 'while I'm here' fixes" ✅
- Re-verify: `<flow>` step 7 = "Failing test passes, all existing tests pass, no regressions" ✅
- **Match: yes**

### Random pick 3 — /sc:task
- Claim: "Step 4 checkpoint >3 files; `<gotchas>` task-count 3-7 max + already-done; completion verification"
- Re-verify: `<flow>` step 4 = "If changes affect >3 files → present numbered plan → wait for user approval" ✅
- Re-verify: `<gotchas>` = "Do not create excessive sub-tasks. Break into 3-7 tasks maximum per feature" ✅
- Re-verify: `<gotchas>` already-done = "Check git log and existing code before creating implementation tasks" ✅
- Re-verify: `<flow>` step 6 = "Validate: Quality gates + completion verification" ✅
- **Match: yes**

3/3 spot-checks pass. Matrix claims are source-grounded.

---

## Limitations

- **Not run-and-measure**: this is static source analysis. Actually executing 34 commands twice (with/without karpathy) is impractical without real targets and would mostly produce noise.
- **First-turn-shape inference**: behavioral delta is predicted from rule combination, not from observed runs. Some "moderate" deltas may turn out smaller in practice.
- **No frontend/runtime testing**: this analysis covers content (rule firing) only, not Claude Code harness integration (e.g., whether skill activation reorders other system reminders).

## References

- Karpathy guidelines (skill body): `~/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/skills/karpathy-guidelines/SKILL.md`
- SuperClaude RULES: `~/.claude/superclaude/core/RULES.md` `<core_rules>` (R03, R06, R12, R13, R15, R18, R20)
- SuperClaude PRINCIPLES: `~/.claude/superclaude/core/PRINCIPLES.md` `<karpathy_lens>` lines 39-44
- Source: Andrej Karpathy thread, https://x.com/karpathy/status/2015883857489522876
- **Empirical companion** (n=1 validation, 4 commands tested): `docs/analysis/karpathy-empirical-test-ajitta-2026-05-08.md`
