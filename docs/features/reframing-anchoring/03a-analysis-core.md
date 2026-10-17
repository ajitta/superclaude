---
status: draft
revised: 2026-10-17
---

# 03a — Phase 2 content value classification: core/ (always-loaded chain + rules modules)

Scope judged ONLY from the text under `src/superclaude/`. Delivery facts taken from the file headers and `core/README.md` (in scope). Not opened: `~/.claude/`, repo `.claude/`, `docs/`, CHANGELOG, root README, `ARCHITECTURE.md`, `context_loader.py`.

## 1. Scope and files read

| File | Bytes | Delivery (per file text / core/README) |
|---|---|---|
| src/superclaude/CLAUDE_SC.md | 50 | import chain entry, always loaded |
| core/FLAGS.md | 5,172 | always loaded |
| core/PRINCIPLES.md | 2,169 | always loaded |
| core/RULES.md | 4,838 | always loaded (kernel) |
| core/BUSINESS_SYMBOLS.md | 2,488 | on-demand (business-panel patterns) |
| core/README.md | 2,338 | never in model context (dev README) |
| core/rules/RULES_DELEGATION.md | 8,757 | on-demand (delegation contexts) |
| core/rules/RULES_DOCS.md | 10,220 | on-demand (doc-producing contexts) |
| core/rules/RULES_INTERACTION.md | 1,138 | on-demand (/sc: commands) |
| core/rules/RULES_QUALITY.md | 13,594 | on-demand (implement/test/review/build/debug) |
| **Total** | **50,764** | always-loaded chain = 12,229 bytes |

Section byte sizes were measured by script over top-level XML elements; sub-section figures are estimates (±15%).

## 2. Classification table

Class key: A = model already does it · B = structural remedy · C = project information · D = other (exhortation, unmeasurable, duplicate, persona, repo-only leak, unconfident A).

| File | Section | Class | Reason | Failure (B) | Mechanism / exhortation (B) | Quoted phrase |
|---|---|---|---|---|---|---|
| CLAUDE_SC.md | whole file | C | import chain; model cannot know it | | | "@core/FLAGS.md" |
| FLAGS.md | `<role>` | D | boilerplate mission line | | | "Behavioral flags for Claude Code exec modes" |
| FLAGS.md | `<modes>` preamble (l.7) | C | hook injection semantics, where MODE files live after compaction, "suggest in one line" | | | "Read it from `modes/` in the superclaude directory" |
| FLAGS.md | `<modes>` flag list (l.8–15) | C | flag vocabulary → mode routing; unknowable | | | "--vs [standard\|cot\|multi]" |
| FLAGS.md | `<mcp>` | C | flag → MCP/tool routing | | | "--c7\|--context7: force Context7 lookup" |
| FLAGS.md | `<execution>` --delegate / --concurrency | C | pointer to SSOT; harness limit fact | | | "does not change the harness's own limits" |
| FLAGS.md | `<execution>` --loop | B (flag-gated) | ORDERING: criteria stated before exec, self-eval vs criteria each iteration, bounded stop | A3 (weak) | mechanism, but inert unless user types `--loop`; criterion is action-derived, not purpose-derived | "state verifiable success criteria up-front" |
| FLAGS.md | `<execution>` --iterations / --plan / --validate / --safe-mode / --verbose-context | C | flag semantics; `--plan` is a user-approval gate but only when typed | | | "wait for user approval before executing" |
| FLAGS.md | `<execution>` Note (l.38) | D | advice on which flags to use; model infers this | | | "match flags to session type" |
| FLAGS.md | `<output>` | C | --uc semantics incl. harness-reported 60% rule; --scope/--focus | | | "never estimate the figure" |
| FLAGS.md | `<priority_rules>` Safety/Override | D/A | obvious precedence; "user flags > auto-detection" is default behavior | | | "Explicit Override: user flags > auto-detection" |
| FLAGS.md | `<priority_rules>` MCP line | C | --no-mcp precedence + fallback instruction | | | "say so once and fall back to native tools" |
| PRINCIPLES.md | `<role>` directive | D | exhortation; "Code reality > documentation" names A2 but gives no mechanism | | | "Code reality > documentation" |
| PRINCIPLES.md | `<philosophy>` Task-First, Evidence-Based, Parallel-Thinking, Context-Aware | A | generic workflow slogans; models batch calls and verify unprompted; Task-First duplicates R01 | | | "batch independent operations into one step" |
| PRINCIPLES.md | `<philosophy>` Assumption-Surfacing | D | duplicate of R12/R13 (lives in RULES_QUALITY); surfaces *interpretation* not purpose | | | "state the interpretation being acted on" |
| PRINCIPLES.md | `<philosophy>` Restraint-First | D | duplicate of kernel `<scope_discipline>` | | | "do not fix nearby code unasked" |
| PRINCIPLES.md | `<philosophy>` Right-Altitude | D | authoring guidance for framework devs leaking into model context | | | "specific enough guide, flexible enough heuristic" |
| PRINCIPLES.md | `<philosophy>` `<examples>` table | D | illustrations of A/D items | | | "I also cleaned up the utils" |
| PRINCIPLES.md | `<thinking_strategy>` | A | models answer simple tasks directly and do not restate CoT | | | "Simple task: direct answer" |
| PRINCIPLES.md | `<decisions>` | D | slogan lists, unmeasurable ("bias check", "preserve option"); Diagnosis line duplicates R03 | | | "measure first \| hypothesis test \| source validate" |
| RULES.md | `<role>` | D | mission boilerplate | | | "four rule classes whose loss is most expensive" |
| RULES.md | `<priority_system>` marks + Conflict order | D | 🔴/🟡/🟢 legend and an unmeasurable precedence chain | | | "Safety > Scope > Restraint > Quality > Speed" |
| RULES.md | `<priority_system>` tag note (l.9) | C | explains `[Rnn]` notation and where detail lives | | | "name the detailed rule in core/rules/RULES_QUALITY.md" |
| RULES.md | `<priority_system>` Intent Propagation (l.10) | B | ISOLATION: verbatim request to delegates; reviewer gets artifact without author rationale / verdicts; prior findings as acceptance criteria | A4 (primary), A1/A2 for the reviewer | real mechanism (changes what reaches whom); always loaded; compressed duplicate of `<delegate_packet>` | "not the author's rationale, self-assessment or verdicts" |
| RULES.md | `<scope_discipline>` l.16 | A | Claude Code system prompt already forbids drive-by refactors | | | "No speculative features, no drive-by refactors" |
| RULES.md | `<scope_discipline>` l.17 | D | locks deliverable to the literal request shape (report and stop) — reinforces I0/R2 action lock rather than relieving it | | | "the deliverable is the assessment: report findings and stop" |
| RULES.md | `<scope_discipline>` l.18 necessity test | D | exhortation; same text repeated in R18 | | | "Is system broken without this?" |
| RULES.md | `<verification_before_completion>` main | A | models run tests and cite output; "should work" is already avoided | | | "Never claim work complete without running the verification" |
| RULES.md | `<verification_before_completion>` "state the concrete check" | B (partial) | ORDERING: criterion stated before non-trivial work. BUT criterion is derived from the *action* ("done"), not an inferred purpose; arrives after the anchor | A3 (gives a re-eval target); does NOT address I0 | mechanism, but mis-targeted for I0 | "Before non-trivial work, state the concrete check that will prove \"done\"" |
| RULES.md | `<verification_before_completion>` docs-only / skipped-check phrasing | D | output phrase convention; models already disclose skipped checks | | | "not executed; inspection only" |
| RULES.md | `<destructive_op_confirmation>` first sentence | A | Claude Code already asks before destructive git ops | | | "require explicit user confirmation first" |
| RULES.md | `<destructive_op_confirmation>` category-vs-named-paths rule | D | specific policy; not confident a bare model distinguishes "all changes" from named paths | | | "a category (\"all changes\"...) names none" |
| RULES.md | `<project_rules_priority>` first sentence | A | harness loads CLAUDE.md; models honor it | | | "Read and honor them before acting" |
| RULES.md | `<project_rules_priority>` gotcha path | C | location convention | | | "`.claude/rules/gotchas/<domain>.md`" |
| RULES.md | `<on_demand_modules>` | C | file locations + load-when routing; unknowable | | | "`~/.claude/superclaude/core/rules/<file>` for a user install" |
| BUSINESS_SYMBOLS.md | `<role>` | D | boilerplate | | | "Business analysis symbol system" |
| BUSINESS_SYMBOLS.md | `<symbols>`, `<abbreviations>`, `<expert_selection>`, `<templates>`, `<config_defaults>` | C | panel vocabulary, expert routing table, output templates, defaults — unknowable conventions | | | "experts: 2-3 by default (the domain's primary pair" |
| core/README.md | whole file | D | never delivered to the model; repo-only; leaks roadmap/evals references | | | "roadmap Phase 2-1) is measurement-gated" |
| RULES_DELEGATION.md | `<role>` | C | loading note (when to Read explicitly) | | | "Read explicitly before spawning agents outside those triggers" |
| RULES_DELEGATION.md | `<sub_agent_decision>` Axis (l.8) | C | Workflow-tool vs Agent-tool fact | | | "the Workflow tool executes it" |
| RULES_DELEGATION.md | `<sub_agent_decision>` Direct / Sub-agent / Never (l.9–11) | D | thresholds ("3+ independent streams") are reasonable but a bare model routes similarly; not confident A | | | "Never sub-agent: the task needs recent conversation context" |
| RULES_DELEGATION.md | `<sub_agent_decision>` Spawn discipline (l.12) | D | exhortation against assurance-spawns | | | "Never spawn a sub-agent unasked to verify or double-check" |
| RULES_DELEGATION.md | `<sub_agent_decision>` Model (l.13) | C | model-parameter fallback order and billing fact | | | "CLAUDE_CODE_SUBAGENT_MODEL, or the session model" |
| RULES_DELEGATION.md | `<sub_agent_decision>` Run-alongside / Worktree-parallel (l.14–15) | C | SendMessage continuation, EnterWorktree — harness facts; "Decline when…" clause is D | | | "continue the existing delegate with SendMessage" |
| RULES_DELEGATION.md | `<sub_agent_decision>` `<examples>` | D | illustrations | | | "\"Find where UserAuth is defined\" \| Direct grep" |
| RULES_DELEGATION.md | `<delegate_packet>` fields (l.30–32) | C | packet fields; sub-agents never receive hook injections — unknowable | | | "sub-agents never receive context_loader/UserPromptSubmit injections" |
| RULES_DELEGATION.md | `<delegate_packet>` Withheld / Marker / Sent / Earlier findings / Decided defects (l.33–38) | B | ISOLATION: reviewer receives artifact + acceptance criteria only; rationale, self-assessment, prior verdicts, review history cut; marker makes the cut visible; prior findings never "fixed" | A4 (primary); A1 (prior verdict in prompt); A2 (review-history notes in artifact) | real mechanism — defines exactly which information reaches the reviewer | "a persuasive rationale flips a reviewer's verdict even when it is wrong" |
| RULES_DELEGATION.md | `<delegate_packet>` Alternatives (l.39) | B | ORDERING: alternatives presented together, not sequentially (sequential = first option anchors) | A1 / R3 (delegate side) | mechanism (one prompt, side by side) | "go side by side in one prompt, not as a follow-up" |
| RULES_DELEGATION.md | `<delegate_packet>` Limit (l.40) | C | honest boundary of the mechanism | | | "can still reach withheld material in the artifact's file" |
| RULES_DELEGATION.md | `<delegate_return>` Before dispatch (l.45) | B | ORDERING + ISOLATION: main loop writes evidence shape + check BEFORE dispatch, never a predicted verdict; ground truth stays out of prompt | A3 (main loop's own predicted verdict), A4/A1 (verdict leaking into prompt) | real mechanism | "never a predicted verdict — a predicted verdict anchors the main loop" |
| RULES_DELEGATION.md | `<delegate_return>` On return (l.46) | B | GATE: judge by the pre-written check, not confidence; revalidate every file:line before acting | A2 variant (delegate output as trusted document), A4 | real mechanism (gate before edit/report) | "not by how confident it reads, and revalidates every cited file:line" |
| RULES_DELEGATION.md | `<delegate_return>` Exploration and audit (l.47) | B | OUTPUT-SHAPE: delegate must return counterevidence + unknowns beside its conclusion | A3 / A2 (incomplete set read as complete) | mechanism (required return fields) | "return counterevidence and unknowns next to its conclusion" |
| RULES_DELEGATION.md | `<workflow_delegation>` | C | Workflow-tool semantics (schema, cache replay, parallel/filter, discarded writes); cache line is a small A2 gate but harness-specific | | | "cached/replayed results ... must be re-validated" |
| RULES_DELEGATION.md | `<agent_routing>` | C | tie-break rule + repo-before-web routing; "state the options ... and pick one" clause is D | | | "repo before web — try Grep and connected symbol-aware tools" |
| RULES_DOCS.md | `<role>` | C | loading note | | | "Read explicitly before creating docs outside those triggers" |
| RULES_DOCS.md | `<doc_output_convention>` Long documents (l.9) | D | efficiency advice; model-tendency exhortation | | | "write the document once" |
| RULES_DOCS.md | `<doc_output_convention>` Size (l.11–14) | C | 25KB target, 30,000-byte guard, split rules per doc type — unknowable; could be shorter | | | "the guard blocks a Read at 30,000 bytes" |
| RULES_DOCS.md | `<doc_output_convention>` Default layout / Multi-of-same-phase / Standalone (l.16–27) | C | naming + location conventions | | | "docs/<type>/<slug>-<suffix?>-<username>-YYYY-MM-DD.md" |
| RULES_DOCS.md | `<doc_output_convention>` Slug resolution (l.29) | C (R3 hazard) | routing; but "pre-selecting the command default" hands the user a starred default | | | "pre-selecting the command default: `[f]` for brainstorm" |
| RULES_DOCS.md | `<doc_output_convention>` README update / Phase mapping (l.30–35) | C | state machine for README `phase:` | | | "it never moves back" |
| RULES_DOCS.md | `<doc_output_convention>` Living docs / ADRs / Archive / Inline only (l.37–40) | C | locations | | | "docs/adr/NNNN-<slug>.md" |
| RULES_DOCS.md | `<doc_output_convention>` Durability routing (l.42–50) | C | admissibility test + routing table for always-loaded docs; project policy, unknowable | | | "name the routine event that falsifies the sentence" |
| RULES_DOCS.md | `<doc_output_convention>` Username / Frontmatter / Status enum / Cross-links / Formatter (l.52–66) | C | conventions | | | "Status enum (per-doc): draft \| review \| approved-for-plan" |
| RULES_DOCS.md | `<doc_output_convention>` Examples (l.68–73) | D | redundant with the rules above | | | "docs/features/auth-refactor/04-design.md" |
| RULES_DOCS.md | `<workflow_gates>` "Committed" precondition | A/D | models do not commit unasked | | | "do not commit unasked" |
| RULES_DOCS.md | `<workflow_gates>` /sc:intent gate | B (voluntary) | GATE: intent approved in the user's words BEFORE analysis — the only intent-first step in scope, but fires only if the user chooses /sc:intent; no rule routes a plain action request into it | I0 / R1 | mechanism, but opt-in | "User approves the intent text in their own words; file committed before analysis" |
| RULES_DOCS.md | `<workflow_gates>` brainstorm → review self-review gate | B | GATE: spec re-examined before plan because approved specs carry reversed decisions | A3 | mechanism (ordering) | "approved specs can still carry reversed decisions" |
| RULES_DOCS.md | `<workflow_gates>` remaining gates | C | command-chain routing / preconditions | | | "Plan document committed to repo" |
| RULES_INTERACTION.md | `<role>` | C | loading note | | | "Injected by context_loader on /sc: command invocations" |
| RULES_INTERACTION.md | `<selection_protocol>` When / Labels / Format / Close / Depth | C | menu output-shape convention | | | "\"select: N\" ... plus \"or type your own\"" |
| RULES_INTERACTION.md | `<selection_protocol>` ★ recommended + [y/n] | D (anti-B) | instructs the exact R3 failure: starred default + yes/no compression | | | "mark the recommended option with ★" |
| RULES_QUALITY.md | `<role>` | C | loading note | | | "Read explicitly when applying R-rule detail" |
| RULES_QUALITY.md | R01 Workflow | A | generic workflow | | | "Status Check → Understand → Plan → Execute → Validate" |
| RULES_QUALITY.md | R02 Status Check | D | ordering rule (check prior art first); plausible A, not confident | | | "check git log and grep the key identifiers" |
| RULES_QUALITY.md | R03 Diagnosis | D | runtime-first checklist + "falsify before confirm" — the latter is an A1 exhortation with no mechanism | | | "falsify before confirm" |
| RULES_QUALITY.md | R06 / R15 / R18 pointers | D | duplicates of kernel text | | | "kernel `<scope_discipline>`; measurable: 0 unsolicited files" |
| RULES_QUALITY.md | R12 Clarification | D | reversibility branching for ambiguity; duplicates PRINCIPLES Assumption-Surfacing; A-candidate | | | "branch by reversibility" |
| RULES_QUALITY.md | R13 Intent Verification | D | output-shape ("state the interpretation") but trigger is ambiguity only, and the skip-list exempts "explicit file paths" — precisely the I0 case | | | "Skip for: single-file edits, explicit file paths" |
| RULES_QUALITY.md | R14 Correction Capture | C | memory layout, `violated_rule` field, fallback path | | | "its body carries `violated_rule: \"[RNN Name]\"`" |
| RULES_QUALITY.md | R16 Safe Read | C | hook blocks ≥30KB reads without limit | | | "hook blocks reads ≥30KB without limit/pages" |
| RULES_QUALITY.md | R17 Symbolic-First | D | models use LSP/Grep sensibly; A-candidate | | | "start with its overview, definition and reference queries" |
| RULES_QUALITY.md | R19 Project Gotcha Capture | C | entry format, `paths:` frontmatter, approval rule | | | "create the file with `paths:` frontmatter if absent" |
| RULES_QUALITY.md | R20 Success Criteria | D | duplicate of kernel; examples prove the criterion is action-derived ("add validation" → "invalid-input tests pass"), never purpose-derived | | | "\"fix bug\" → \"the repro ... now passes\"" |
| RULES_QUALITY.md | R21 Failure-Forward | B (narrow) | OUTPUT-SHAPE + re-plan trigger: hypothesis record then a *different* approach, bounded; but fires only on hard failures, not on evidence that invalidates a plan | A3 (failure-triggered only) | mechanism | "each with a different approach (never the identical retry)" |
| RULES_QUALITY.md | `<core_rules>` `<examples>` table | D | ~2.9KB of illustrations | | | "\"42/42 pass (baseline: 40, +2 new)\"" |
| RULES_QUALITY.md | `<anti_over_engineering>` headline + Earned > Premature | A | models avoid speculative abstraction; Claude Code system prompt covers it | | | "abstract at 2nd occurrence not 1st" |
| RULES_QUALITY.md | `<anti_over_engineering>` Dependency gate / Do NOT simplify / examples / `<model_tendencies>` | D | exhortations and illustrations; "Do NOT simplify" list is a reasonable but unmeasurable guard | | | "avoid classes for one-time ops" |
| RULES_QUALITY.md | `<thresholds>` | D | pointers to rules stated elsewhere | | | "Scope tiers: see <checklist_scaling> (single source)" |
| RULES_QUALITY.md | `<checklist_scaling>` | D | "full checklist" is unmeasurable; process scaling a model already does | | | "a typo fix does not need a risk matrix" |
| RULES_QUALITY.md | `<verification_ladder>` | D | reasonable mapping but models choose test scope similarly; A-candidate | | | "Escalate a behavior change to Level 4" |
| RULES_QUALITY.md | `<anti_misunderstanding>` Same mistake twice | C | where to put a repeated finding; superclaude-repo detection | | | "root `pyproject.toml` has `name = \"superclaude\"`" |
| RULES_QUALITY.md | `<anti_misunderstanding>` Scope words / Unverified numbers | D | vocabulary exhortation; "~" prefix is about the model's own output, not prompt-embedded numbers (A1) | | | "prefix estimates with ~" |

## 3. Anchor-point map

Core files have no command flow of their own; the moments below are the points at which the always-loaded chain or a rules module governs what the model receives.

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| CLAUDE_SC → FLAGS/PRINCIPLES/RULES | user's first prompt | ACTION instruction (and any prompt-embedded number, cause, prior estimate) | **none** — nothing in the chain asks for the purpose or a purpose-derived criterion. Closest: RULES `<verification_before_completion>` "Before non-trivial work, state the concrete check that will prove \"done\"" — fires *after* the request is read and derives the check from the action, not the purpose. I0: **no step states the purpose before acting.** |
| RULES `<scope_discipline>` l.17 | user describes a problem instead of requesting a change | the user's PROBLEM DEFINITION (R1/R2 anchor) | none; the rule tells the model to answer inside that frame: "the deliverable is the assessment: report findings and stop" |
| RULES_QUALITY R13 | request with 2+ plausible targets | ambiguous action instruction | partial: "state in one sentence the interpretation being acted on, then proceed" — but explicitly "Skip for: single-file edits, explicit file paths", i.e. skipped in the I0 fixture shape |
| RULES_QUALITY R03 / PRINCIPLES directive | prompt names a suspected cause or number | A1 anchor | exhortation only: "falsify before confirm"; "Evidence > assumptions" |
| PRINCIPLES directive | model reads README/docstring/comments | A2 document | exhortation only: "Code reality > documentation" |
| RULES_QUALITY R21 | tool error / test red | invalidating signal (hard failure) | B: "⚠ failed ... hypothesis ... next" + "each with a different approach" — A3 only when a failure occurs; no trigger for silent plan invalidation |
| FLAGS `<modes>` l.7 | after compaction | model's own prior state (A3 re-entry) | partial: re-reads the MODE file ("When the flag was typed but its MODE text is not in context (e.g. after compaction), Read it") — restores mode text, not plan validity; no re-plan rule |
| RULES Intent Propagation / RULES_DELEGATION `<delegate_packet>` | main loop composes a delegate prompt | user request + (for reviewers) author rationale, prior verdicts | **B**: "not the author's rationale, self-assessment or verdicts"; "[prior verdict withheld]"; findings travel "with no claim that it is fixed" |
| RULES_DELEGATION `<delegate_return>` l.45 | before dispatch | main loop's own expectation (A3 self-anchor) | **B**: "writes down the evidence shape it expects and the check that will judge it ... never a predicted verdict" |
| RULES_DELEGATION `<delegate_return>` l.46 | delegate's summary returns | DELEGATE RESULT (document anchor) | **B**: "judges the summary against that check ... not by how confident it reads, and revalidates every cited file:line" |
| RULES_DELEGATION `<delegate_packet>` l.39 | alternatives exist for a delegate | option list | **B**: "side by side in one prompt, not as a follow-up" |
| RULES_DELEGATION `<workflow_delegation>` l.54 | Workflow resume-from-cache | cached prior result | gate: "must be re-validated against the current repo before acting" |
| RULES_INTERACTION `<selection_protocol>` | command step waits on user | OPTION LIST presented to the user | **anti-B**: "mark the recommended option with ★"; "[y/n] for yes/no" — produces the R3 shape measured today |
| RULES_DOCS slug resolution l.29 | file-producing command picks a folder | option list `[f]`/`[s]` | anti-B: "pre-selecting the command default" |
| RULES_DOCS `<workflow_gates>` /sc:intent | start of a feature flow | user's intent text | **B (opt-in)**: "User approves the intent text in their own words" — only if the user runs /sc:intent; no routing from an action request |
| RULES_DOCS `<workflow_gates>` brainstorm → review | spec approved, about to plan | PRIOR PLAN/SPEC (A3) | **B**: "Spec self-review mandatory ... approved specs can still carry reversed decisions" |
| FLAGS --loop | user typed --loop | iteration result | B (flag-gated): "state verifiable success criteria up-front ... self-eval vs criteria" |

**I0 verdict for scope:** no file in core/ makes the model state the purpose behind the request and derive a success criterion from it before acting. R20/`<verification_before_completion>` derive the check from the stated action ("add validation" → "tests for invalid inputs pass"), which is the action lock restated as a test. The only purpose-first gate (/sc:intent) is a separate opt-in command.

## 4. Totals per class

| Class | Sections (rows) | Approx. bytes | Share | Of which always-loaded (FLAGS+PRINCIPLES+RULES, 12,229 B) |
|---|---|---|---|---|
| A | 9 | ~2,000 | 4% | ~1,400 |
| B | 11 (3 caveated: flag-gated, partial, opt-in) | ~5,000 | 10% | ~1,200 (Intent Propagation + "state the concrete check" + --loop) |
| C | 44 | ~24,500 | 48% | ~5,900 |
| D | 38 | ~18,600 | 37% | ~3,800 (+ README 2,338 never delivered) |
| **Total** | 102 | ~50,100 (measured 50,764) | | |

Always-loaded chain breakdown: C ~5.9KB (mostly FLAGS routing + on_demand_modules map), D ~3.8KB, A ~1.4KB, B ~1.2KB. Roughly 42% of every session's core payload is A or D.

RULES_QUALITY.md alone carries ~10.3KB of D (examples table ~2.9KB, checklist_scaling, thresholds, verification_ladder, anti_over_engineering detail, duplicated pointers) against ~1.7KB of C and ~0.9KB of B.

## 5. Top 10 findings (ranked)

1. **I0 gap — no purpose-inference step anywhere in the always-loaded chain.** The only "criterion before acting" rule (`<verification_before_completion>`: "state the concrete check that will prove \"done\"", detailed in R20) derives the check from the action verb, so it formalizes the action lock instead of breaking it. A B-class step would have to make the model write *why the user wants this* and *what outcome proves the purpose met* — and look beyond the named file — before executing. Nothing in scope does this.
2. **R13 Intent Verification exempts the I0 case by design.** "Skip for: single-file edits, explicit file paths, continuation of confirmed plan" — the fixture ("draft a reply in thread.md") hits two of three skip conditions. If any rule is to become the purpose gate, this skip-list must be inverted for action instructions that name a file.
3. **RULES_INTERACTION `<selection_protocol>` prescribes the R3 failure.** "mark the recommended option with ★" and "[y/n] for yes/no" produce starred defaults and bare yes/no answers — exactly what today's measurement showed. Replace with: no default marker; yes/no questions answered as a conditional recommendation first, verdict last. RULES_DOCS slug resolution ("pre-selecting the command default") has the same shape.
4. **RULES_QUALITY.md ~10.3KB of D on every implement/test/review/debug turn.** Deletion candidates: `<core_rules>` `<examples>` table (~2.9KB), `<checklist_scaling>` (~0.8KB), `<thresholds>` (~0.8KB, pure pointers), `<verification_ladder>` (~1.2KB, A-candidate), `<anti_over_engineering>` examples + `<model_tendencies>` (~1.4KB), duplicated R06/R15/R18/R20 pointers.
5. **`<scope_discipline>` l.17 reinforces frame lock (R1/R2).** "the deliverable is the assessment: report findings and stop" tells the model to answer within the user's problem definition. Needs a premise-check clause (state the problem as understood *and* the one-layer-out alternative) or it works against the restructure principle.
6. **The real B content is all in RULES_DELEGATION `<delegate_packet>` + `<delegate_return>` (~2.6KB) and it is on-demand.** These are genuine isolation/ordering mechanisms for A4/A3/A2 — but they cover only the delegation path. Kernel `Intent Propagation` (always loaded) carries the A4 part; the A3 "write the check before dispatch, never a predicted verdict" rule has no kernel echo and no non-delegation analogue (the main loop never writes its own check before reading a document or a prior plan).
7. **A2 and A1 have exhortations only.** "Code reality > documentation" (PRINCIPLES directive), "falsify before confirm" (R03), "Evidence > assumptions" — none changes order or information flow. Candidate mechanism: before accepting a README/docstring/prompt-embedded number as a premise, record it as *claim* with a verifying command, in the same shape R21 uses for failures.
8. **A3 re-plan trigger exists only for hard failures.** R21 fires on "tool error, test red, missing target"; FLAGS l.7 re-reads MODE text after compaction. Neither covers "evidence contradicts the current plan" or "re-enter a plan after compaction: re-validate before continuing". Gap.
9. **PRINCIPLES.md is ~80% A/D (≈1.7KB of 2.2KB) and always loaded.** `<philosophy>` slogans, the examples table, `<thinking_strategy>`, `<decisions>` — all duplicates of RULES/RULES_QUALITY or generic practice. Only the Diagnosis pointer and the Assumption-Surfacing thresholds carry anything, and both exist elsewhere.
10. **Caveated B rows:** `--loop` is inert without the flag; the /sc:intent gate is opt-in; `<verification_before_completion>` "state the concrete check" is action-derived. Count as B only once a trigger fires on an ordinary action instruction.

Smaller deletions: FLAGS l.38 note, `<priority_rules>` Safety/Override, RULES `<priority_system>` legend + conflict chain, RULES_DOCS `Examples`, RULES_DELEGATION `<examples>`, core/README.md roadmap/evals sentence (repo-only, never delivered).

## 6. Not read

`~/.claude/`, repo `.claude/`, `docs/` (except writing this file), `CHANGELOG.md`, root `README.md`, `ARCHITECTURE.md`, `scripts/context_loader.py` (delivery facts came from file headers + core/README.md), `modes/`, `commands/`, `agents/`, `skills/`. No web search, tests, or `claude` runs.
