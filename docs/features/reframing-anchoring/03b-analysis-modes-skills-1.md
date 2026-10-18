# Phase 2 analysis 03b — modes/ and skills sc-author, sc-prompt

> Split by size into 3 files (part 1 of 3): [part 2](./03b-analysis-modes-skills-2.md) · [part 3](./03b-analysis-modes-skills-3.md). Section boundaries and content unchanged.

Content value classification per the Phase 2 brief. Scope: `src/superclaude/modes/` (eight MODE_*.md, RESEARCH_CONFIG.md, README.md), `src/superclaude/skills/sc-author/` and `src/superclaude/skills/sc-prompt/` (SKILL.md and references/). Read-only; judged from the file text alone. Delivery facts (modes injected whole on flag/keyword with an 8K-token budget; README skipped; RESEARCH_CONFIG never injected, read by `/sc:research` from its installed copy; skills loaded natively by Claude Code) come from `ARCHITECTURE.md` and `scripts/context_loader.py` only.

Classes: **A** already does it · **B** structural remedy (failure named; mechanism vs exhortation stated) · **C** project information · **D** other (exhortation, persona, duplicate, unmeasurable, repo leak, unsure A).

## 1. Scope and files read

| File | Bytes |
|---|---:|
| modes/MODE_Brainstorming.md | 2,197 |
| modes/MODE_Business_Panel.md | 3,992 |
| modes/MODE_DeepResearch.md | 4,162 |
| modes/MODE_Introspection.md | 2,368 |
| modes/MODE_Orchestration.md | 4,196 |
| modes/MODE_Task_Management.md | 2,388 |
| modes/MODE_Token_Efficiency.md | 2,936 |
| modes/MODE_Verbalized_Sampling.md | 8,860 |
| modes/README.md | 2,951 |
| modes/RESEARCH_CONFIG.md | 3,749 |
| skills/sc-author/SKILL.md | 7,893 |
| skills/sc-author/references/agent.md | 3,260 |
| skills/sc-author/references/command.md | 1,526 |
| skills/sc-author/references/fields.yaml | 4,205 |
| skills/sc-author/references/format-xml.md | 3,047 |
| skills/sc-author/references/memory.md | 2,293 |
| skills/sc-author/references/output-style.md | 1,884 |
| skills/sc-author/references/quality.md | 10,837 |
| skills/sc-author/references/skill.md | 3,357 |
| skills/sc-prompt/SKILL.md | 16,344 |
| skills/sc-prompt/references/evidence.md | 1,516 |
| skills/sc-prompt/references/fable-5-1.md | 3,350 |
| skills/sc-prompt/references/opus.md | 4,884 |
| skills/sc-prompt/references/sonnet-5-5.md | 4,518 |
| **Total** | **106,713** |

Section bytes below are measured per XML element or heading block and rounded where an element was split across classes; totals are approximate (±3 %).

## 2. Classification table

| File | Section | Class | Reason | Failure (B) | Mechanism or exhortation (B) | Quote | ~Bytes |
|---|---|:-:|---|---|---|---|---:|
| modes/MODE_Brainstorming.md | `<role><mission>` | D | persona/mission line, no behavior |  |  | “Collaborative discovery mindset” | 141 |
| modes/MODE_Brainstorming.md | `<thinking>` | D | heuristic slogans (diverge/converge); exhortation |  |  | “Diverge then Converge” | 293 |
| modes/MODE_Brainstorming.md | `<communication>` | B | output-shape rule: a requested recommendation comes as 2-3 options with trade-offs, no single answer | R3 | mechanism (output shape), weak: no 'no default' clause | “give two or three options with their trade-offs” | 290 |
| modes/MODE_Brainstorming.md | `<priorities>` | D | exhortation ('Discover constraints > assume them') |  |  | “Discover constraints > assume them” | 143 |
| modes/MODE_Brainstorming.md | `<behaviors>` | D | persona traits (Socratic, Collaborative); 'surface hidden requirements' is exhortation |  |  | “Ask probing questions to surface hidden requirements” | 368 |
| modes/MODE_Brainstorming.md | `<examples>` | D | asks the user 'Problem solved?' before a brief — purpose asked, not inferred; example only, no gate |  |  | “Discovery: Problem solved? Target users?” | 335 |
| modes/MODE_Brainstorming.md | `<bounds> does/never` | D | duplicate of communication (options with trade-offs) |  |  | “a requested recommendation comes as options with trade-offs” | 330 |
| modes/MODE_Brainstorming.md | `<bounds><fallback>` | C | loader misfire on quoted flag — a fact about the delivery mechanism |  |  | “appears only in quoted or pasted text” | 150 |
| modes/MODE_Brainstorming.md | `<handoff>` | C | command routing |  |  | “/sc:brainstorm /sc:design /sc:implement” | 57 |
| modes/MODE_Business_Panel.md | `<role><mission>` | D | mission line |  |  | “Multi-expert business analysis” | 107 |
| modes/MODE_Business_Panel.md | `<thinking>` | D | 'make implicit assumptions explicit before concluding' is an exhortation with no gate; repeated in behaviors |  |  | “Assumption Surfacing: Make implicit assumptions explicit” | 391 |
| modes/MODE_Business_Panel.md | `<communication>` | B | ordering/output shape: trade-offs before conclusions, consensus vs outlier labelled | R3 | mechanism (output shape), weak | “Surface trade-offs before conclusions” | 219 |
| modes/MODE_Business_Panel.md | `<priorities>` | D | exhortation |  |  | “Trade-off clarity > consensus” | 167 |
| modes/MODE_Business_Panel.md | `<behaviors> Multi-Lens` | B | forces >=2 frameworks per question so the user's frame is never the only one | R2 | mechanism (mandatory plural frames) | “Apply 2-3 frameworks per question and surface where they agree” | 150 |
| modes/MODE_Business_Panel.md | `<behaviors> Adaptive/Synthesis/Assumption` | D | routing dup of domain_routing; assumption line dup of thinking |  |  | “Make implicit business assumptions explicit before concluding” | 312 |
| modes/MODE_Business_Panel.md | `<experts>` | C | project-chosen roster of nine lenses |  |  | “Christensen \| Disruptive innovation \| Jobs-to-be-done” | 585 |
| modes/MODE_Business_Panel.md | `<interaction_modes>` | C | routing: which sequence per mode |  |  | “Position -> Challenge -> Rebuttal -> Resolution” | 313 |
| modes/MODE_Business_Panel.md | `<domain_routing>` | C | routing table plus precedence rule |  |  | “A matching domain_routing row decides the mode” | 450 |
| modes/MODE_Business_Panel.md | `<examples>` | D | illustrative; the yes/no example answers with a landscape (R3-correct) but only as an example |  |  | “Should we enter this market? \| Debate” | 592 |
| modes/MODE_Business_Panel.md | `<bounds> does/never` | D | restates behaviors; 'impersonating an expert persona' is project style |  |  | “impersonating an expert persona in place of applying the framework lens” | 395 |
| modes/MODE_Business_Panel.md | `<bounds><fallback>` | C | keyword-match loader misfire fact |  |  | “loaded by a keyword match (not --business-panel” | 150 |
| modes/MODE_Business_Panel.md | `<handoff>` | C | routing |  |  | “/sc:business-panel /sc:design /sc:document” | 60 |
| modes/MODE_DeepResearch.md | `<role><mission>` | C | install location of RESEARCH_CONFIG; shorten to the path |  |  | “installed .claude/superclaude/modes/RESEARCH_CONFIG.md” | 350 |
| modes/MODE_DeepResearch.md | `<thinking>` | D | exhortations ('assume nothing', 'question each source') |  |  | “every claim needs verification; assume nothing” | 270 |
| modes/MODE_DeepResearch.md | `<communication>` | D | lead-with-answer is default; quotation marking is project policy, not anchoring |  |  | “Mark reproduced source wording as a quotation” | 210 |
| modes/MODE_DeepResearch.md | `<priorities>` | D | exhortation; the Token-Efficiency composition clause (~120 B) is C |  |  | “that mode governs the wording of the report” | 265 |
| modes/MODE_DeepResearch.md | `<behaviors> Parallel-Search, Evidence-Chaining` | A | models parallelize searches and keep provenance unprompted |  |  | “search in parallel when appropriate” | 120 |
| modes/MODE_DeepResearch.md | `<behaviors> Source-Verification` | B | count gate before a claim is accepted; one source cannot settle a claim | A2 | mechanism (numeric gate) | “cross-check each load-bearing claim against ≥2 independent sources” | 330 |
| modes/MODE_DeepResearch.md | `<behaviors> Replan` | B | named triggers that force a plan change | A3 | mechanism (re-plan trigger); the only explicit re-plan trigger in scope besides RESEARCH_CONFIG | “change the search plan when sources disagree on a load-bearing claim” | 370 |
| modes/MODE_DeepResearch.md | `<behaviors> Name-Verification` | B | gate: an unrecognised name forces a search with the user's wording before answering | A1 (adjacent: own recall as anchor) | mechanism (search-before-answer gate) | “partial familiarity is a reason to search, not to skip it” | 330 |
| modes/MODE_DeepResearch.md | `<outcomes>` | D | restates behaviors and communication |  |  | “Confidence stated for each load-bearing claim” | 191 |
| modes/MODE_DeepResearch.md | `<example quoting-retrieved-sources>` | D | 1.1 KB teaching paraphrase of sources — unrelated to research quality or anchoring; A-leaning |  |  | “One short marked phrase from one source” | 1126 |
| modes/MODE_DeepResearch.md | `<bounds> does/never` | D | restates behaviors |  |  | “skip validation, and accept unverified claims” | 300 |
| modes/MODE_DeepResearch.md | `<bounds><fallback>` | C | loader misfire fact |  |  | “loaded by a keyword match (not --research” | 154 |
| modes/MODE_DeepResearch.md | `<handoff>` | C | routing |  |  | “/sc:research /sc:document /sc:analyze” | 55 |
| modes/MODE_Introspection.md | `<role><mission>` | D | mission line |  |  | “Metacognitive analysis mindset” | 117 |
| modes/MODE_Introspection.md | `<thinking>` | D | exhortations; 'Framework-Compliance: check against superclaude standards' is a repo leak |  |  | “Check against superclaude standards” | 288 |
| modes/MODE_Introspection.md | `<communication>` | D | post-hoc report shape plus emoji markers (tone); 📊-only-from-tool-output is anti-fabrication, not anchoring |  |  | “Mark sections with 🎯 target, ⚡ action” | 420 |
| modes/MODE_Introspection.md | `<priorities>` | D | exhortation |  |  | “Self-awareness > confidence” | 152 |
| modes/MODE_Introspection.md | `<behaviors>` | D | 'State assumptions, then verify' is an exhortation; no re-plan trigger; file:line-only-if-read is anti-fabrication |  |  | “State assumptions, then verify them against evidence” | 313 |
| modes/MODE_Introspection.md | `<examples>` | D | illustrative |  |  | “Why structural over functional?” | 479 |
| modes/MODE_Introspection.md | `<bounds> does/never` | D | restates |  |  | “skip self-examination, hide decision logic” | 300 |
| modes/MODE_Introspection.md | `<bounds><fallback>` | C | loader misfire fact |  |  | “loaded by a keyword match (not --introspect)” | 158 |
| modes/MODE_Introspection.md | `<handoff>` | C | routing |  |  | “/sc:reflect /sc:improve /sc:analyze” | 53 |
| modes/MODE_Orchestration.md | `<role><mission>` | D | mission line |  |  | “Intelligent tool selection mindset” | 123 |
| modes/MODE_Orchestration.md | `<thinking>` | A | batching independent calls is default behavior |  |  | “Independent operations are batched, not serialized” | 263 |
| modes/MODE_Orchestration.md | `<communication>` | D | tone |  |  | “Explain tool selection rationale when non-obvious” | 168 |
| modes/MODE_Orchestration.md | `<priorities>` | C | symbol-aware vs native tool routing is a project decision |  |  | “symbol-aware tool (LSP or code index) for symbol/semantic ops” | 240 |
| modes/MODE_Orchestration.md | `<behaviors> Tool-Task Matching` | C | routing (docs→Context7, browser→Playwright, web→Tavily) |  |  | “full routing in core/FLAGS.md mcp section” | 260 |
| modes/MODE_Orchestration.md | `<behaviors> Batching, Constraint-Adaptive` | A | default behavior |  |  | “Degrade gracefully when preferred tools are unavailable” | 180 |
| modes/MODE_Orchestration.md | `<behaviors> Verification-First` | D | 'never assume correctness' is an exhortation; 'consult official docs before infra/config changes' has no observable trigger |  |  | “Consult official docs before infra/config changes” | 130 |
| modes/MODE_Orchestration.md | `<fan_out_execution> harness facts` | C | Workflow tool semantics the model cannot know (no parent intent forwarded, writes discarded, cap limits, no auto-injection) |  |  | “the Workflow executor forwards no parent intent or system prompt” | 1400 |
| modes/MODE_Orchestration.md | `<fan_out_execution> Schema-vs-Evidence` | B | delegate output is not trusted until file:line is revalidated in the main loop | A4/A2 (delegate result as document) | mechanism (gate on accepting a delegate's claims); SSOT lives in RULES_DELEGATION, so this copy is a pointer | “cited-file:line revalidation per core/rules/RULES_DELEGATION.md stays mandatory” | 160 |
| modes/MODE_Orchestration.md | `<fan_out_execution> pointers` | D | three pointers to RULES_DELEGATION.md repeat the same SSOT |  |  | “full rule: core/rules/RULES_DELEGATION.md” | 150 |
| modes/MODE_Orchestration.md | `<examples>` | D | restates fan_out_execution rows |  |  | “one Agent-tool delegate, not a Workflow” | 482 |
| modes/MODE_Orchestration.md | `<bounds> does/never` | A | 'never run sequentially when parallel is possible' is default |  |  | “run operations sequentially when parallel execution is possible” | 330 |
| modes/MODE_Orchestration.md | `<bounds><fallback>` | C | loader misfire fact |  |  | “loaded by a keyword match (not --orchestrate” | 161 |
| modes/MODE_Orchestration.md | `<handoff>` | C | routing |  |  | “/sc:task /sc:select-tool /sc:implement” | 56 |
| modes/MODE_Task_Management.md | `<role><mission>` | D | mission line |  |  | “Hierarchical task organization with persistent memory” | 127 |
| modes/MODE_Task_Management.md | `<thinking>` | D | decompose-before-starting is default (A-leaning); Plan→Phase→Task→Todo naming is convention no tool consumes |  |  | “Break work into a hierarchy (Plan -> Phase -> Task -> Todo)” | 343 |
| modes/MODE_Task_Management.md | `<communication>` | D | progress reporting is default behavior |  |  | “Report the current position in the plan” | 181 |
| modes/MODE_Task_Management.md | `<priorities>` | C | which tools persist state and that /sc:save runs only on request |  |  | “across sessions: /sc:save, which runs only on the user's request” | 259 |
| modes/MODE_Task_Management.md | `<behaviors> State-Aware` | D | orient-then-resume with no validity check on the prior plan — reinforces A3 rather than remedying it |  |  | “Orient to the current position (load context, identify the phase, resume) before acting” | 160 |
| modes/MODE_Task_Management.md | `<behaviors> Checkpoint-Disciplined` | C | when to suggest /sc:save |  |  | “suggest /sc:save when the state must survive the session” | 200 |
| modes/MODE_Task_Management.md | `<behaviors> other` | D | default behavior / convention |  |  | “Track status across tasks and phases” | 130 |
| modes/MODE_Task_Management.md | `<examples>` | D | 'Implement auth system' goes straight to phases — no purpose step; 'resume from the last checkpoint' reinforces A3 |  |  | “resume from the last checkpoint” | 404 |
| modes/MODE_Task_Management.md | `<bounds> does/never` | D | 'never work outside the task list once one exists' is a frame lock (anti-A3/anti-R2) |  |  | “work outside the task list once one exists” | 300 |
| modes/MODE_Task_Management.md | `<bounds><fallback>` | C | loader misfire fact |  |  | “--task-manage appears only in quoted or pasted text” | 147 |
| modes/MODE_Task_Management.md | `<handoff>` | C | routing |  |  | “/sc:task /sc:save /sc:reflect” | 47 |
| modes/MODE_Token_Efficiency.md | `<role><mission>` | D | mission line |  |  | “Selective-omission mindset” | 114 |
| modes/MODE_Token_Efficiency.md | `<thinking>` | D | style principle |  |  | “Selectivity not Compression” | 270 |
| modes/MODE_Token_Efficiency.md | `<communication>` | D | style |  |  | “Drop details that do not change the reader's next action” | 175 |
| modes/MODE_Token_Efficiency.md | `<priorities>` | D | style |  |  | “Clarity > compression” | 126 |
| modes/MODE_Token_Efficiency.md | `<behaviors>` | D | lead-with-outcome is default; omission disclosure is style |  |  | “State when detail was dropped so the reader can ask for it” | 358 |
| modes/MODE_Token_Efficiency.md | `<subagent_output> Per-Step-Shrink` | C | harness fact: shorter returns do not raise subagent limits |  |  | “does not raise the harness's limits on how many subagents run” | 190 |
| modes/MODE_Token_Efficiency.md | `<subagent_output> Revalidate-Floor` | D | duplicate pointer to RULES_DELEGATION revalidation |  |  | “does not waive the cited-file:line revalidation” | 195 |
| modes/MODE_Token_Efficiency.md | `<examples>` | D | third row compresses an option set to one recommendation — works against R3 |  |  | “The recommendation, and the one option that was close” | 396 |
| modes/MODE_Token_Efficiency.md | `<compaction>` | C | 60 % trigger, /compact suggestion, SSOT pointer; natural home for a post-compaction re-entry rule, which is absent |  |  | “suggests the user run /compact with focus instructions” | 494 |
| modes/MODE_Token_Efficiency.md | `<bounds> does/never` | A | a current model does not emit arrow chains or invented abbreviations |  |  | “arrow chains, invented abbreviations, dropped articles” | 300 |
| modes/MODE_Token_Efficiency.md | `<bounds><fallback>` | C | loader misfire fact |  |  | “loaded by a keyword match (not --uc, --token-efficient” | 180 |
| modes/MODE_Token_Efficiency.md | `<handoff>` | C | routing |  |  | “/sc:save /sc:reflect” | 38 |
| modes/MODE_Verbalized_Sampling.md | `<role><mission>` | D | mission line |  |  | “Distribution-level answering” | 173 |
| modes/MODE_Verbalized_Sampling.md | `<thinking>` | D | research rationale (mode collapse); 'Describe then Label' is B but restated four more times below |  |  | “Describe then Label: what emerged decides the label” | 512 |
| modes/MODE_Verbalized_Sampling.md | `<communication>` | B | output shape: a set not a ranking, user picks, reproducibility header | R3 | mechanism (output shape: no default, no verdict) | “Present k candidates as a set, not a ranking \| ... the user picks” | 248 |
| modes/MODE_Verbalized_Sampling.md | `<priorities>` | D | restates communication |  |  | “User's choice > model's verdict” | 203 |
| modes/MODE_Verbalized_Sampling.md | `<behaviors> Detect/Route/Generate/Synthesize` | C | flag grammar, variant routing, template handling |  |  | “parse `--vs [standard\|cot\|multi]`, the brackets” | 820 |
| modes/MODE_Verbalized_Sampling.md | `<behaviors> Label` | B | ordering: probability/label attached only after the text exists | A3 (micro self-anchor) / R3 | mechanism (ordering) | “attach probabilities and descriptive names only AFTER the text exists” | 150 |
| modes/MODE_Verbalized_Sampling.md | `<params>` | C | ranges, defaults, clamps, precedence |  |  | “explicit flags > brackets > NL hints” | 648 |
| modes/MODE_Verbalized_Sampling.md | `<diversity_dial>` | C | tau values and literal tail instruction per signal |  |  | “the tails of the distribution, such that the probability” | 611 |
| modes/MODE_Verbalized_Sampling.md | `<templates> recipes` | C | the three elicitation templates |  |  | “Generate {k} responses to the following query” | 1300 |
| modes/MODE_Verbalized_Sampling.md | `<templates> provenance/paper notes` | D | paper citation, cost ratios, wording-ablation commentary not needed at run time |  |  | “the paper's 7-way wording ablation found no significant” | 680 |
| modes/MODE_Verbalized_Sampling.md | `<output_format>` | C | layout; the 'label written after the text, since a label written first steers the text' clause duplicates Label (B) |  |  | “a probability or label written first steers the text toward it” | 741 |
| modes/MODE_Verbalized_Sampling.md | `<gotchas> pre-assign, synthesis-verdict` | D | duplicates of Label and communication (B rules restated) |  |  | “never pre-assign probabilities or roles” | 330 |
| modes/MODE_Verbalized_Sampling.md | `<gotchas> task-fit, token-cutoff, long-form` | C | when not to use the overlay; reply-cap protocol with [CONTINUE] |  |  | “emit one `### Turn N` section per reply” | 900 |
| modes/MODE_Verbalized_Sampling.md | `<gotchas> k-tradeoff, population-sim, word-diversity` | D | research commentary |  |  | “SD-ratio 0.4–0.56 → 1.26–1.37 across 3 model families” | 700 |
| modes/MODE_Verbalized_Sampling.md | `<bounds> does/never` | D | restates (collapse, pre-assign, calibration) |  |  | “collapse to a single answer while the overlay is active” | 330 |
| modes/MODE_Verbalized_Sampling.md | `<bounds><fallback>` | C | when to revert (factual query, expanding a pick); user flag wins |  |  | “state the quality trade-off in one line and proceed” | 336 |
| modes/MODE_Verbalized_Sampling.md | `<handoff>` | C | routing |  |  | “/sc:brainstorm /sc:analyze /sc:design” | 55 |
| modes/README.md | whole file (not injected: context_loader skips README) | D | human-facing index; zero model tokens; 'Authoring Rules' leaks a repo path and a pytest command |  |  | “See `.claude/rules/mode-authoring.md`” | 2951 |
| modes/RESEARCH_CONFIG.md | `<role><mission>` | D | mission line |  |  | “Deep research configuration and strategy settings” | 89 |
| modes/RESEARCH_CONFIG.md | `<defaults>` | C | max_hops, approval policy per clarity |  |  | “a clear query runs without waiting for approval” | 262 |
| modes/RESEARCH_CONFIG.md | `<parallel_rules>` | C | batch sizes are a project number; the parallel exhortation is A |  |  | “searches=5, extractions=3, analyses=2” | 273 |
| modes/RESEARCH_CONFIG.md | `<strategies>` | C | routing by query clarity; 'Clarify first (max 3 questions)' is an R1-lite gate that asks the user rather than tests the premise |  |  | “Intent-Planning \| ambiguous, broad \| Clarify first” | 268 |
| modes/RESEARCH_CONFIG.md | `<hop_config>` | D | generic traversal patterns the model would choose |  |  | “Entity: Paper→Authors→Works→Collaborators” | 317 |
| modes/RESEARCH_CONFIG.md | `<reflection>` | B | scheduled checkpoint after each hop with named triggers | A3 | mechanism (periodic re-plan check); duplicates <replanning> and the mode's Replan | “freq="after_each_hop" triggers="thin sources\|contradictions\|core question unanswered"” | 171 |
| modes/RESEARCH_CONFIG.md | `<memory>` | D | attribute-only element, no behavior |  |  | “case_based="true" pattern_learning="true"” | 72 |
| modes/RESEARCH_CONFIG.md | `<tool_routing>` | C | tool → use → fallback |  |  | “playwright \| JS required, dynamic, auth” | 327 |
| modes/RESEARCH_CONFIG.md | `<gates> planning` | B | criteria must exist before execution — the only pre-action criterion gate in scope | I0 (criterion before acting; purpose still absent) | mechanism (phase gate), but 3 words and never injected by the mode | “planning: objectives+strategy+criteria” | 60 |
| modes/RESEARCH_CONFIG.md | `<gates> execution/synthesis` | D | execution gate duplicates the mode's Source-Verification verbatim; synthesis gate is vague |  |  | “no open contradiction on a load-bearing claim” | 325 |
| modes/RESEARCH_CONFIG.md | `<credibility>` | D | a model ranks academic above forums unprompted (A-leaning) |  |  | “Forums, Unverified, Personal blogs” | 248 |
| modes/RESEARCH_CONFIG.md | `<depth_profiles>` | C | numbers per --depth |  |  | “quick \| 10/1/1 \| tavily” | 247 |
