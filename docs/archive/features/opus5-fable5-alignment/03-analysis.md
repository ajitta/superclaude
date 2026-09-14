---
status: draft
revised: 2026-08-02
---

# `src/superclaude` Alignment Audit — Findings and Proposals

Audit of the installed content framework against the guideline in [02-research.md](./02-research.md).

## Method

Six auditors covered the framework by area — the rule kernel, flags and principles, modes, commands, agents, and the delegation/skills/MCP surface. Each was given the guideline as ground truth, required to quote offending text verbatim, and required to read the governing `.claude/rules/*-authoring.md` spec before proposing an edit. Each area's findings then went to an independent adversarial verifier instructed to **refute** them and to default to REJECTED under uncertainty.

The verification stage was built around one specific trap. Anthropic says to delete instructions that make the model *perform* extra verification (A1), but explicitly endorses instructions that require *grounding claims* in real tool output (B5). These look alike and point opposite ways, so both auditors and verifiers were told to keep them separate. It worked in both directions: the modes auditor deliberately filed no finding against `MODE_DeepResearch.md`'s "every claim need verify" because it is B5 anti-fabrication about external sources, and a verifier stripped A1 from the `brainstorm` rationale on the grounds that emitting a routing sentence is not performing a verification pass.

**49 findings raised, 43 survived, 6 rejected.** 16 confirmed outright; 26 plausible with a stated adjustment; 1 never received a verdict.

| Verdict | High | Medium | Low | Total |
|---|---|---|---|---|
| CONFIRMED | 7 | 6 | 3 | 16 |
| PLAUSIBLE (adjustment required) | 8 | 14 | 4 | 26 |
| REJECTED | 0 | 5 | 1 | 6 |
| UNVERIFIED | 0 | 0 | 1 | 1 |

The unverified one is `te-unmeasurable-compression-target` (`MODE_Token_Efficiency.md`, low severity): the modes auditor overflowed its `area` field with prose, and that finding fell out of the verifier's join. It rides along with CS2 and should be treated as unreviewed rather than as evidence.

Nothing has been edited. This document is a proposal set.

## Headline

The framework is not broadly misaligned. Its architecture is *validated* by the research: the always-loaded kernel plus on-demand `RULES_*.md` modules is precisely the hybrid Anthropic recommends, and `content-quality.md`'s deletion test already encodes the pruning discipline the Claude 5 family calls for.

What has drifted is a specific stratum: **instructions written to compensate for Opus 4.x weaknesses that the Claude 5 family no longer has.** Those instructions did not go neutral — the model still follows them. Three clusters carry nearly all the risk, and one of them can fail closed.

## Change sets

Grouped so each ships as one coherent commit. Ordered by risk.

---

### CS1 — Reasoning-exposure wording (Fable 5 refusal risk)

**Why first:** Anthropic documents this as the one failure mode that fails *closed* rather than degrading. A `reasoning_extraction` refusal returns HTTP 200 with `stop_reason: "refusal"`; with no fallback configured the request simply stops. Anthropic names system prompts and skills as the audit target by name.

> **Measured correction (2026-08-02) — the refusal was not reproduced.** Running `probe-introspect-marker` on `claude-fable-5` against the *pre-alignment* content (`d49b498`, carrying the original `expose thinking (🤔🎯⚡📊💡)` wording, with only the harness `--` fix applied so the probe could execute) passed **1/1 with zero denials** — the same result as the post-change wording. There is no measurement in this repository showing the old wording ever triggered a refusal.
>
> What the probe can and cannot say: one short run on a benign technical question, against a classifier that is probabilistic and context-sensitive. Absence of a refusal here is not proof the old wording was safe under all prompts. But it does mean the refusal framing rests entirely on Anthropic's published guidance and not on anything observed here.
>
> **The change still stands, on the other argument.** `FLAGS.md`'s `expose thinking` was a lossy description of what the mode actually does — surface decision logic, assumptions, and alternatives, which is analysis output rather than a reasoning transcript. That accuracy defect is model-independent, and post-change probes confirm no capability was lost (1/1 on sonnet, Opus 5, and Fable 5). Read this cluster as an accuracy fix that also reduces a documented risk — not as a fix for an observed failure.

| File | Text | Verdict |
|---|---|---|
| `core/FLAGS.md:10` | `--introspect: … → expose thinking (🤔🎯⚡📊💡)` | CONFIRMED |
| `modes/MODE_Introspection.md:13` | `Surface decision logic … \| Use emoji markers (🤔 thinking\|…) for transparency` | CONFIRMED |
| `modes/MODE_Introspection.md:31-32` | `reasoning transparency`, `hide decision logic` | PLAUSIBLE |

`FLAGS.md` is the more dangerous surface because it is always loaded via the `CLAUDE_SC.md` import chain — this is resident text, not conditional. It is also lossy: the mode's actual behavior is *"surface decision logic + assumptions + alternatives + verification state,"* which is analysis output, not a reasoning transcript. The flag line compresses that into the exact phrase Anthropic flags.

**Proposal.** Reframe from *exposing reasoning* to *reporting decisions and evidence*, and drop the 🤔 thinking marker while keeping the other four.

- `FLAGS.md:10` → `--introspect: self-analysis, error recovery → surface decision logic + assumptions + alternatives (🤔🎯⚡📊💡)` — the verifier notes the emoji set should also lose 🤔 for consistency with the mode edit.
- `MODE_Introspection.md:13` → `Report the decision made, the evidence behind it, the alternatives rejected, and what remains unverified | … | Mark sections with 🎯 target, ⚡ action, 📊 metrics, 💡 insight`

The mode keeps all four axes and its single-line pipe form; no test pins the emoji set.

**Uncovered residual:** `core/BUSINESS_SYMBOLS.md:49,51` also uses 🤔 and fell outside every auditor's file scope. Decide it with this set rather than leaving it inconsistent.

---

### CS2 — Compression-as-brevity, and context-budget self-monitoring

Two distinct Anthropic findings converge on one file. `MODE_Token_Efficiency.md` currently states `Information density > readability` and ships an arrow/abbreviation output contract — the inverse of Anthropic's *"readability matters more"* and *"if you have to choose between short and clear, choose clear,"* which names arrow chains and abbreviations specifically as the wrong lever.

The mode is already self-contradictory: line 63's `<never>compress beyond readability</never>` contradicts line 15's priority ordering. This change makes the file consistent with itself, not just with Anthropic.

| Item | Text | Verdict |
|---|---|---|
| `MODE_Token_Efficiency.md:15` | `Information density > readability \| … \| Compression > expansion` | CONFIRMED |
| `:34-46` | `## Symbols` / `## Abbreviations` tables (`-> leads to`, `cfg config`, `impl implementation`) | PLAUSIBLE |
| `:9` | `Budget Awareness: Monitor context usage proactively, not reactively` | CONFIRMED |
| `:24-28` | `## Context Limits` — `context_window.used_percentage`, `monitor context usage proactively` | PLAUSIBLE |
| `core/FLAGS.md:41` | `--uc: symbol system, 30-50% reduction` | PLAUSIBLE |
| `core/BUSINESS_SYMBOLS.md` | arrow-chain template | PLAUSIBLE |

**Proposal.** Keep the mode's purpose — fewer output tokens — but route it through Anthropic's endorsed mechanism (drop details that don't change the reader's next action) instead of compressing prose.

- `:15` → `Clarity > compression | Selectivity > completeness | Signal > noise | Fewer items > shorter sentences`
- Delete `## Symbols` and `## Abbreviations`; rewrite `<communication>` to `Drop details that do not change the reader's next action | Tables for dense lookups, sentences for reasoning | Full words and complete sentences`
- Delete `:9` and the `## Context Limits` block; replace the Compaction activation line with a non-numeric cue: `When: answer quality degrading, or explicit --uc flag`

**Two adjustments the verifiers require before this ships:**

1. `.claude/rules/mode-authoring.md` lists *"Symbol tables (Token Efficiency mode)"* and *"Abbreviation maps"* under **Allowed** content. Deleting the tables without updating that spec creates exactly the sediment `content-quality.md` forbids. Same commit.
2. `FLAGS.md:42` reads `Manual/proactive trigger >=60% ctx (per MODE_Token_Efficiency.md)` — it points *at* the deleted block. Drop the parenthetical in the same change set.

**A note on evidence quality.** I could not measure whether the abbreviation table saves tokens — no API credentials this session, and Claude's tokenizer is not available offline. The recommendation does not rest on that: Anthropic names the constructs directly. Two independent corroborations point the same way — this repo's own harness research already lists *"Token efficiency symbols → context windows growing, models compress better"* among practices to retire, and the bundled caveman plugin bans invented abbreviations on the identical tokenizer argument. If a number is wanted, `count_tokens` against `claude-opus-5` is the way to get it.

---

### CS3 — Verification and delegation scaffolding

Opus 5 reversed direction on both axes at once: it self-verifies natively (so verification instructions now over-fire) and it over-delegates (so delegation encouragement compounds the cost). Anthropic's guidance closes the loop between them — *"do not use subagents to verify or double-check your own work"* — which makes a verifier subagent doubly wrong.

| File | Text | Verdict |
|---|---|---|
| `agents/self-review.md:3` | `Use proactively after draft to catch gaps pre-handoff.` | CONFIRMED |
| `commands/agent.md:32` | `- @self-review (post-impl validation)` in the Phase 2 list | PLAUSIBLE |
| `core/rules/RULES_DELEGATION.md:12` | `Threshold numbers generation-neutral … (unmeasured on current flagship)` | PLAUSIBLE |
| `commands/pm.md:43` | `<never>skip specialist delegation, bypass documentation.</never>` | PLAUSIBLE |
| `skills/simplicity-coach/SKILL.md:76-81` | trailing `<checklist>` duplicating `<flow>` | CONFIRMED |

**`self-review.md` is the sharpest case.** Claude Code reads `description` verbatim into the parent delegation classifier, so *"Use proactively after draft to catch gaps pre-handoff"* functions as an instruction, not inert metadata — and A1 names *"use a subagent to verify"* as exactly the scaffolding to remove. The verifier traced every reference in the tree and found that all load-bearing uses are command-invoked (`/sc:review`, the brainstorm gate); nothing depends on the proactive clause. So the prune removes automatic self-verification while leaving the measured gate intact.

Proposal: replace the two proactive sentences with an explicit-request trigger — `Use when the user explicitly asks for an independent second pass on a finished work product (/sc:review, "review this plan before I share it").` Keep `<finding_policy>`, `<gotchas>`, and `<bounds>` untouched — those are B5 anti-fabrication and A9 report-everything-then-filter, both endorsed.

**`RULES_DELEGATION.md` has a real gap.** The verifier grepped the install tree and found no *"never spawn a sub-agent to verify"* rule and no *"one rather than several"* anywhere, while A6 names both as the Opus 5 reversal. Add spawn discipline in place of the stale `(unmeasured on current flagship)` hedge.

**Three proposals were corrected by verification and must not ship as originally written:**

- The `pm.md` replacement clause encoded a one-subagent cap that contradicts the installed SSOT (`<sub_agent_decision>` explicitly endorses *"3+ independent parallel streams"* and returns 3 subagents in its own examples table) and contradicts `pm.md`'s own shipped wave fan-outs. Corrected to prune-only: `<never>bypass documentation.</never>`.
- A numeric spawn cap of 3 in `<sub_agent_decision>` was rejected — that section is explicitly scoped to the *single-delegate* primitive, and `FLAGS.md` states the Workflow fan-out cap is harness-fixed and wins on process count. A count cap belongs on the fan-out line or nowhere.
- The `commands/agent.md` rewrite restated `RULES_DELEGATION.md` verbatim (a second answer location) and deleted a parallel-tool-call instruction C5 endorses. Corrected to point at the SSOT instead.

---

### CS4 — Rule-kernel calibration

Prescriptive scaffolds in `RULES_QUALITY.md` that the Claude 5 family now performs natively, plus one genuine internal contradiction.

**R13 is a real bug, independent of any model guidance.** `R12` ends *"Default bounded-proceed; ask reserved for four trigger classes."* `R13` then fires a blocking confirm on a `>3 steps` trigger that is not one of those four classes — and the examples table proves "confirm" means a blocking question (`"Correct?"`). The two rules contradict each other in always-reachable content. The verifier also found the fix *removes* a divergence rather than creating one: three downstream agents already say "restate user intent" **without** "and confirm."

| Item | Change | Verdict |
|---|---|---|
| `R13` | Drop the `>3 steps` trigger and unconditional "and confirm"; bind the ask-gate to R12's four classes | CONFIRMED |
| `R03` | Drop the `3+ hypotheses` count; keep `falsify before confirm` and the evidence requirement | PLAUSIBLE |
| `R02` | Drop the `2-3 targeted searches` count; keep the default-on duplicate-work check | PLAUSIBLE |
| `R17` | Replace `reserve Read for … when all above insufficient` with a scoped trigger | CONFIRMED |
| `RULES.md:7` | 🔴 tier inflation — five rules marked 🔴 including scope rules | PLAUSIBLE |

`R17` is notable: `PRINCIPLES.md:19` already names *"ALWAYS use Serena for ALL symbol operations"* as the anti-pattern and *"Use Serena for symbol operations when exploring unfamiliar code"* as the fix. `R17` currently ships the anti-pattern shape. The framework already knows the answer and contradicts itself.

**Mechanical requirement the auditors nearly missed:** the `<examples>` table encodes priority tiers in its Rule column (`Status Check 🔴`, `Diagnosis 🔴`, `Intent Verification 🔴`). Any tier change must update rows 26, 27, and 32 in the same edit or the file contradicts itself.

**Adjustments required.** The `R02` replacement — *"when a request plausibly duplicates work already done"* — was flagged as swinging past right altitude: it is self-judged by the same model whose blind spot the rule covers. Corrected to keep the default-on posture and exempt only what the session already established. And `R03`'s claim that downstream references stay valid is false — `skills/verbalized-sampling/references/examples.md:183` and `agents/root-cause-analyst.md:51` both quote the *count*; leaving them turns the citation into sediment.

---

### CS5 — Always-loaded budget

Pure pruning of the resident tier, where every line costs on every turn.

| Item | Change | Verdict |
|---|---|---|
| `PRINCIPLES.md:40-47` | Delete `<karpathy_lens>` — restates R06/R18/R15/R20 from the always-loaded kernel | CONFIRMED |
| `PRINCIPLES.md:26-27` | Delete two `<thinking_strategy>` lines | CONFIRMED |
| `PRINCIPLES.md:11` | Delete `Layered-Composition` — SSOT is `RULES_DELEGATION.md:8` | CONFIRMED |

`thinking_strategy` self-nullifies: `commands/help.md:65` states *"Effort levels are Claude Code native, not managed by SuperClaude,"* so `effort param tune depth` points at a lever the content framework does not hold, and `model-managed` concedes the line changes nothing. An archived 2026-03-15 alignment spec already recommended deleting it.

**One decision this raises rather than settles:** should `FLAGS.md` gain effort guidance (G13)? The auditor argued no, and the verifier agreed — the model cannot set its own effort parameter, so A7/B11 are harness-config guidance for the *user*, not content-framework material. I think that is right, and it makes the correct action pruning the stale mention rather than adding an effort table. Worth an explicit decision rather than a silent omission.

**Sequencing risk, flagged by two verifiers independently.** Deleting `karpathy_lens` and `Layered-Composition` together removes *every* always-loaded statement of governance/harness composition, and `karpathy_lens` is the only always-loaded carrier of R12/R13 (which otherwise live in on-demand `RULES_QUALITY.md`). If both land, add one `<philosophy>` line: `Assumption-Surfacing: state interpretation and ask when 2+ readings are valid (R12/R13)`. Treat that as required, not optional.

Separately: `MCP_Sequential.md`'s `<fallback>` points at `<thinking_strategy>` as the adaptive-vs-manual-CoT SSOT. The proposal keeps the rewritten anti-pattern line, so the pointer survives — but verify it after editing.

---

### CS6 — The only additions

Everything above prunes. Three findings argue for adding, and only one is clearly justified.

**`RULES.md` `<scope_discipline>`, +1 sentence** (CONFIRMED). Anthropic's B6 boundary — *"when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment"* — has no equivalent anywhere in the framework. The verifier grepped for four phrasings and got zero hits. Scope discipline currently governs *how much* to change but never says *whether a change was requested at all*. Proposed: `When the user describes a problem, asks a question, or thinks out loud rather than requesting a change, the deliverable is the assessment: report findings and stop.`

The other two — written-deliverable length calibration (A4) and a note that verbosity is not an effort lever (A3) — are real gaps but lower value. Given E5's prune-first posture and D3's add-only-on-observed-failure rule, hold them until the failure is actually seen.

---

### CS7 — Trigger hygiene

Agent and skill descriptions sit permanently in the system prompt and drive auto-invocation. Four cases where the trigger contradicts the component's own body.

- **`agents/technical-writer.md:3`** (CONFIRMED) — `Use right after feature ship that need reference or onboarding material.` arms the agent on completion of unrelated work, while line 68's own gotcha forbids unsolicited docs. The preceding sentence already carries a valid artifact-type trigger, so this is a pure deletion. The distinction that saves it: an *artifact-type* trigger tells the classifier which agent owns doc work; a *post-work-state* trigger arms on completion.
- **`skills/confidence-check/SKILL.md:3`** (CONFIRMED) — `Auto-fire on destructive verbs (refactor X, rename Y, delete Z, restructure)` is the blanket-trigger genus C1 names. Scope it to multi-file targets and state the positive alternative: single-file renames go direct.
- **`agents/python-expert.md:18,33`** (CONFIRMED) — prescribes `property-based` testing in two places. The framework's own research records that `hypothesis`-style patterns are a *sticky prior* that over-fires unprompted and resists soft suppression; positively prescribing it is strictly the wrong direction. Two-word prune.
- **`agents/repo-index.md`** (PLAUSIBLE) — triggers not distinguishable from `project-initializer`, which D5 treats as a correctness defect.

The verifier rejected an add-on suggestion to insert a Zen-of-Python clause into `python-expert`'s description: no observed failure behind it, so it violates E5 and D3. Correctly declined.

---

### CS8 — Duplication and sediment

`mcp/MCP_Tavily.md:27-31` `<strategies>` (CONFIRMED) — credibility scoring exists in three places at three different granularities (`RESEARCH_CONFIG.md` 4-tier, `deep-researcher.md` 1-5 scale, this file 3-tier), and `<strategies>` is not in `mcp-authoring.md`'s closed tag list. Delete; keep `<search_patterns>`, which names real Tavily parameters.

The verifier corrected the rationale: this file loads at Tier 1 as a compact instruction string, not full body, so the token saving is much smaller than the finding claimed. The duplication grounds carry the edit on their own.

Remaining lower-value items — `MCP_Playwright.md` a11y overlap, `commands/explain.md` contentless validate steps, `RESEARCH_CONFIG.md` per-hop reflection, `MODE_Task_Management.md` chatspeak — are all PLAUSIBLE and can ride along.

---

## What was rejected

Six findings did not survive. Reporting them matters, because two were refuted by *this repository's own measurements* — which is a stronger result than the confirmations.

| Finding | Why it failed |
|---|---|
| `r21-failure-narration-template` | A clean-environment A/B in `docs/research/agent-native-design-ajitta-2026-05-31.md:102` shows the marker fires on genuine failures and stays silent on borderline ones — *"does not over-fire."* The rule already carries the scoping clause the finding asked for. |
| `load-context-percentage-trigger` | Surfaces no count. Conditions a restatement of the session goal on depth — goal persistence, the *opposite* of context anxiety, and what C6 endorses. |
| `context-budget-threshold-sprawl` | The "inconsistent thresholds" claim was false: 60/75/85 is a documented three-tier ladder, and the finding double-counted to reach "four numbers." B4 targets countdowns shown to the model, not static activation thresholds. |
| `orchestration-never-sequential` | A6 is about subagent width; the clause concerns tool-call batching, which C5 explicitly endorses. |
| `sequential-vs-native-thinking-boundary` | Inferring "Sequential MCP is redundant with native thinking" from effort-parameter guidance is an unsupported leap; the proposed edit was judged harmful. |
| `brainstorm-never-prescribe` | The mode loads only on an explicit `--brainstorm` flag, so a prohibition on prescribing solutions *is* the requested deliverable. B6/B10 describe default posture and do not override an explicit user request. |

The `B4` rejections are the useful signal: three separate findings tried to read context-percentage triggers as context-anxiety risk, and only the one instructing the model to *monitor its own usage* survived. The line is between the harness acting on a threshold (fine) and the model watching its own budget (the documented trigger).

## Confidence and limits

**What is solid.** Every surviving finding quotes verbatim text confirmed present by a second agent that was instructed to refute it. Spec conformance was checked against the governing `.claude/rules/*-authoring.md` in each case, and several proposals were corrected or narrowed as a result.

**What is not measured.** No claim here has been A/B tested against this repository. Everything rests on Anthropic's published behavioral guidance plus the framework's own recorded research. The abbreviation token-saving claim in CS2 is explicitly unmeasured and labeled as such.

**Recommended gate before adopting CS1–CS3.** The framework has a working probe method — `claude -p` from *outside* the repo, per the `probe-observer-effect` gotcha, so the probed model loads user-global rules but not the repo's spec documents. High-severity behavioral claims should clear that gate before being treated as settled. CS5 (pruning duplicates) and CS8 (sediment) need no probe; they are correctness edits under the framework's own rules.

**Coverage gaps.** `core/BUSINESS_SYMBOLS.md` fell outside every auditor's file scope and carries both the 🤔 marker (CS1) and an arrow-chain template (CS2). `scripts/context_loader.py` was not audited as code; it emits a `~N tokens full load` string into every prompt, which is adjacent to B4 but is a static cost figure rather than a remaining-budget countdown — weaker than the `used_percentage` case and not filed as a finding.

**Tooling caveat — grep false negatives on long lines.** While revalidating a cited quote, `Grep` in `content` mode returned *"No matches found"* for `Auto-fire on destructive` in `skills/confidence-check/SKILL.md`, while `files_with_matches` mode found the file and a direct `Read` showed the text plainly on line 3. The file is plain ASCII with no BOM and no NUL bytes; the distinguishing property is line length — that `description:` line is roughly 460 characters, and content mode suppresses very long lines while reporting the result as no match rather than as a skipped line.

This has direct bearing on audit completeness. Skill and agent `description:` fields are precisely this repository's long lines — `skill-authoring.md` permits up to 1024–1536 characters — and they are also the highest-value audit target, since Claude Code reads them verbatim into the system prompt and the delegation classifier. Any content-mode grep over frontmatter descriptions can therefore return false negatives, and the auditors used grep. Descriptions that *were* filed as findings are safe (all were confirmed by direct read), but **absence of a description finding is not evidence of absence**. A follow-up sweep of agent and skill descriptions should use `files_with_matches` or direct reads rather than content-mode grep.

Worth capturing in `.claude/rules/gotchas/general.md` under R19. Not added here — R19 requires user approval, and that file sits outside the `src/superclaude/` scope of this work.

**Model scope.** These proposals target Opus 5 and Fable 5. Some guidance inverts on older models — Opus 4.8 *under*-delegated and *under*-reached for tools, exactly opposite to Opus 5. Where the framework must serve older targets, CS3's wording should damp without forbidding.
