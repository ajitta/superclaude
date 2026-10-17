# Phase 2 analysis 03b — modes/ and skills sc-author, sc-prompt

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
| modes/RESEARCH_CONFIG.md | `<output_formats>` | C | sections per --format |  |  | “exec, methodology, findings, synthesis, conclusions” | 290 |
| modes/RESEARCH_CONFIG.md | `<replanning>` | D | verbatim duplicate of MODE_DeepResearch Replan |  |  | “no second source can outrank that” | 388 |
| modes/RESEARCH_CONFIG.md | `<errors>` | C | fallback per tool failure |  |  | “tavily: api_key\|rate_limit\|no_results → native WebSearch” | 249 |
| modes/RESEARCH_CONFIG.md | `<handoff>` | C | routing |  |  | “/sc:research /sc:document” | 43 |
| skills/sc-author/SKILL.md | frontmatter | C | allowed-tools pre-approval, disable-model-invocation |  |  | “Bash(superclaude author-check *)” | 626 |
| skills/sc-author/SKILL.md | preamble: isolation of in-context rules and project docs | B | in-context authoring rules and the project's existing sections do not shape the draft; a conflict is surfaced for the person to choose | A2 (prior documents as anchor) | mechanism (isolation + conflict escalated to a human choice) | “authoring rules already in context ... do not shape this document” | 900 |
| skills/sc-author/SKILL.md | preamble: no write before approval | C | workflow gate |  |  | “Nothing is written into the project before the person approves” | 150 |
| skills/sc-author/SKILL.md | Step 1 Resolve | C | type/path/format resolution facts; no purpose or success-criterion step |  |  | “Path: for a new file, the type's `location` in `fields.yaml`” | 1200 |
| skills/sc-author/SKILL.md | Step 2 Load-set | C | defines the checker's scope; harness load behavior |  |  | “a document left out of it is a conflict nobody checks” | 300 |
| skills/sc-author/SKILL.md | Step 3 Load | C | which references to read; repeats the isolation rule ('format and language only') |  |  | “for two things only: format (md or XML body) and language” | 600 |
| skills/sc-author/SKILL.md | Step 4 Draft/audit: evidence-first candidates | B | every removal must carry evidence and wait for approval; harm reported before no-ops | A4 (reviewer anchor, inverted: the author must prove, the person judges) | mechanism (evidence requirement + approval gate), weak as an anchoring remedy | “each with its evidence ("Removal evidence")” | 500 |
| skills/sc-author/SKILL.md | Step 4 Draft/audit: rest | C | reformat-moves-not-deletes, three-line header (Resolve/Load set/Match), embedded-text handling |  |  | “The message that shows it opens with three lines” | 1300 |
| skills/sc-author/SKILL.md | Step 5 Neighbors | C | compare descriptions with listed skills; do not open their files |  |  | “Do not open their files for this” | 250 |
| skills/sc-author/SKILL.md | Step 6 Check | C | validator command, finding codes, scratch-copy rule, three-run cap |  |  | “superclaude author-check <path> --type <type> --format” | 1500 |
| skills/sc-author/SKILL.md | Step 7 Hand-off | C | trigger prompts, /doctor prompt-audit, plugin validate — the success criterion, produced after writing |  |  | “one or two that should trigger the document and one similar that should not” | 700 |
| skills/sc-author/SKILL.md | ## Reference files | C | file map |  |  | “${CLAUDE_SKILL_DIR}/references/fields.yaml” | 656 |
| skills/sc-author/references/agent.md | When to use / Template / Return | C | subagent facts and template |  |  | “returns a summary to the main conversation” | 650 |
| skills/sc-author/references/agent.md | Project format and language | D | third restatement of the isolation rule (B in SKILL.md preamble) |  |  | “for their format and language only” | 428 |
| skills/sc-author/references/agent.md | What the subagent sees | C | harness facts (no history, CLAUDE.md unless omitClaudeMd) |  |  | “Not the conversation history, the skills already invoked” | 971 |
| skills/sc-author/references/agent.md | Pitfalls | C | field casing, tools list semantics, MCP tools dropped |  |  | “a `tools` list drops MCP tools it does not name” | 1046 |
| skills/sc-author/references/agent.md | sources frontmatter | D | provenance, not needed at run time |  |  | “retrieved: 2026-10-14” | 97 |
| skills/sc-author/references/command.md | When to use / Template / Pitfalls | C | command facts (skills preferred, name/paths ignored) |  |  | “`name` and `paths` are not supported in command files” | 990 |
| skills/sc-author/references/command.md | Project format and language | D | isolation rule restated |  |  | “for their format and language only” | 521 |
| skills/sc-author/references/skill.md | When to use / Template / Description | C | skill facts (1,536-char listing cut, third person) |  |  | “cuts `description` plus `when_to_use` at 1,536 characters” | 1240 |
| skills/sc-author/references/skill.md | Project format and language | D | isolation rule restated |  |  | “for their format and language only” | 381 |
| skills/sc-author/references/skill.md | Pitfalls | C | allowed-tools semantics, 500-line body, context: fork |  |  | “`allowed-tools` does not limit which tools the skill can use” | 1434 |
| skills/sc-author/references/skill.md | sources frontmatter | D | provenance |  |  | “retrieved: 2026-10-13” | 210 |
| skills/sc-author/references/memory.md | When to use / How these files load / Template | C | load order, AGENTS.md rule, @import hops, MEMORY.md cap |  |  | “AGENTS.md is read only when there is no CLAUDE.md” | 1400 |
| skills/sc-author/references/memory.md | Project format and language | D | isolation rule restated (softer: put new instruction near similar ones) |  |  | “put a new instruction where similar ones already are” | 234 |
| skills/sc-author/references/memory.md | Pitfalls | C | 200-line target, paths-only frontmatter; 'specific instructions are followed more consistently' is A |  |  | “`paths` is the only frontmatter field Claude Code reads” | 531 |
| skills/sc-author/references/memory.md | sources frontmatter | D | provenance |  |  | “retrieved: 2026-10-13” | 93 |
| skills/sc-author/references/output-style.md | whole file | C | keep-coding-instructions default, restart requirement, fork scope |  |  | “`keep-coding-instructions` defaults to `false`” | 1784 |
| skills/sc-author/references/output-style.md | sources frontmatter | D | provenance |  |  | “retrieved: 2026-10-13” | 100 |
| skills/sc-author/references/format-xml.md | When tags help (first paragraph) | A | XML-tag prompting practice the model applies unprompted |  |  | “Tags separate kinds of content that would otherwise run together” | 400 |
| skills/sc-author/references/format-xml.md | When tags help (X1 / memory-file caveat) | C | checker behavior on appended lines |  |  | “the checker reports it as X1” | 387 |
| skills/sc-author/references/format-xml.md | What the checker enforces | C | checker rules |  |  | “One root element. Nothing but blank lines sits outside it” | 515 |
| skills/sc-author/references/format-xml.md | Tags and sections | D | isolation rule restated + reformat-moves-not-deletes restated |  |  | “tag names and sections come from the type's reference, not from those documents” | 413 |
| skills/sc-author/references/format-xml.md | Skeletons | C | project skeletons |  |  | “<instructions><context>” | 915 |
| skills/sc-author/references/format-xml.md | sources frontmatter | D | provenance |  |  | “retrieved: 2026-10-14” | 234 |
| skills/sc-author/references/fields.yaml | whole file | C | fields, locations, limits, tool names per type |  |  | “optional: [tools, disallowedTools, model, permissionMode” | 4205 |
| skills/sc-author/references/quality.md | sources frontmatter + Contents | D | provenance and TOC |  |  | “retrieved: 2026-10-14” | 1382 |
| skills/sc-author/references/quality.md | Writing guidance | D | Anthropic prompting-guide summaries; A-leaning except the emphasis-over-triggers fact |  |  | “Strong emphasis over-triggers on current models” | 1789 |
| skills/sc-author/references/quality.md | Load set | C | what is read together with what, by which tool |  |  | “Subagent body \| the CLAUDE.md hierarchy and rules” | 1042 |
| skills/sc-author/references/quality.md | Judgment questions | C | the project's per-sentence audit criterion with evidence types; examples are D (~700 B) |  |  | “Restated default: would Claude or the harness do this anyway?” | 2091 |
| skills/sc-author/references/quality.md | Keep | C | project policy: recorded 'no', harness quirk, stale location |  |  | “A recorded "no" that stops a suggestion Claude would otherwise make” | 403 |
| skills/sc-author/references/quality.md | Harm | C | ordering: harm before no-ops; contradiction and phantom-check cases |  |  | “Report these before any no-op candidate” | 493 |
| skills/sc-author/references/quality.md | Removal evidence | C | output shape of a candidate |  |  | “quotes the failed check as printed” | 357 |
| skills/sc-author/references/quality.md | Model differences | C | per-model defaults the reading model cannot know about the others; expires fast |  |  | “judge for the model that needs the sentence most” | 2563 |
| skills/sc-author/references/quality.md | Audit checklist | D | restates the sections above as a table |  |  | “For each sentence: does a judgment question say it changes nothing?” | 689 |
| skills/sc-prompt/SKILL.md | frontmatter + flags | C | triggers, flags |  |  | “--model opus55\|sonnet55\|opus5\|fable51” | 694 |
| skills/sc-prompt/SKILL.md | Step 1-2 Capture/Resolve | C | flag→model-ID map, session inference, never-default-to-Opus |  |  | “Never default to Opus: its verification edit is the inverse” | 900 |
| skills/sc-prompt/SKILL.md | Step 3-4 Diagnose/Apply | C | run detectors both directions; cc vs api axes |  |  | “touching only the axes the prompt exercises” | 500 |
| skills/sc-prompt/SKILL.md | Step 5-6 Rewrite/Report: source gate | B | no addition without a named source; unknown context becomes [FILL] — isolates the model's assumptions from the user's facts | A2 (self-generated 'facts' as document) | mechanism (provenance gate on every added sentence) | “An addition with no source is deleted, not reported” | 450 |
| skills/sc-prompt/SKILL.md | Step 7 Emit | C | api config output |  |  | “effort tier, `thinking.display` and the `max_tokens` floor” | 164 |
| skills/sc-prompt/SKILL.md | Model facts: locating/reading the reference | C | hook note, glob order, section anchors, mirror precedence |  |  | “anchor on `## Migrating to Claude <target>`” | 2400 |
| skills/sc-prompt/SKILL.md | Model facts: 'never use a recalled value in place of a read' | B | read-not-recall gate; reference outranks mirror on conflict | A2 (document precedence made explicit) | mechanism (precedence + read gate) | “never use a recalled value in place of a read” | 250 |
| skills/sc-prompt/SKILL.md | Model facts: environment-fact rationale | D | exhortative rationale |  |  | “the costliest defect this skill can ship” | 350 |
| skills/sc-prompt/SKILL.md | Removal targets: Embedded anchor ‡ | B | rewrite rule: own estimate + criterion first, several candidates, prior presented afterwards as one input; 'ignore the above' forbidden | A1 | mechanism (ordering + isolation) — applied to the prompt being rewritten, not to this session's own behavior | “Ask for the model's own estimate or diagnosis first, with its criterion stated” | 700 |
| skills/sc-prompt/SKILL.md | Removal targets: Verifiability switch ‡ | B | splits opinion framing into a fact request and a judgment request whose criterion is stated first | R3 / I0 (criterion before judgment) | mechanism (ordering/output shape), applied to the rewritten prompt | “a separate judgment request with its criterion stated first” | 700 |
| skills/sc-prompt/SKILL.md | Removal targets: Severity filters | B | report everything with severity and confidence; filtering during the pass depresses recall | A4 (adjacent: reviewer recall suppression) | mechanism (output shape) | “filtering during the pass depresses recall” | 250 |
| skills/sc-prompt/SKILL.md | Removal targets: Step choreography | C | the project's anti-procedure rewrite rule |  |  | “keep ordering only where order is real” | 200 |
| skills/sc-prompt/SKILL.md | Removal targets: other 14 rows | C | per-model folklore detectors with directions and refusal/400 facts |  |  | “a prefill returns 400 on both Opus targets” | 5160 |
| skills/sc-prompt/SKILL.md | Context targets: Reason + Quality bar | B | the rewritten prompt must carry why the work is asked and what done looks like, or a [FILL] slot | I0 | mechanism (required output slots) — the only I0 content in scope; it repairs the user's prompt, it does not make this session infer purpose | “Reason: why the work is asked for” | 400 |
| skills/sc-prompt/SKILL.md | Context targets: Audience/Environment/Boundaries/Compaction | C | required context slots; api compaction contract |  |  | “Compaction contract (`--target api`, client-side compaction only)” | 486 |
| skills/sc-prompt/SKILL.md | Output: shape + tools | C | sections, tools |  |  | “The change delta as its own labeled section” | 800 |
| skills/sc-prompt/SKILL.md | Output: invocation table | D | seven examples restating the steps |  |  | “Report the prompt as clean and emit no diff” | 900 |
| skills/sc-prompt/SKILL.md | Gotchas | C | model-specific inversions, reasoning_extraction pre-decline, mirror-vs-reference |  |  | “never delete Sonnet 5.5's verification requirement” | 1037 |
| skills/sc-prompt/references/evidence.md | Expert persona / Embedded anchor / Verifiability switch | C | evidence strength cited in the change delta; the anchor paragraph is the basis of the restructure principle |  |  | “stating the model's own criterion first reduces it, if modestly” | 1400 |
| skills/sc-prompt/references/evidence.md | sources frontmatter | D | provenance |  |  | “retrieved: 2026-09-14” | 113 |
| skills/sc-prompt/references/fable-5-1.md | Behavioral delta + Request configuration | C | per-model facts (400s, effort ladders, failure modes); Fable's 'Intent framing: give the reason behind the request' is the I0 fact |  |  | “Thinking cannot be disabled” | 2830 |
| skills/sc-prompt/references/fable-5-1.md | sources frontmatter + header | D | provenance and reading rules for the mirror |  |  | “retrieved: 2026-09-30” | 520 |
| skills/sc-prompt/references/opus.md | Behavioral delta + Request configuration | C | per-model facts (400s, effort ladders, failure modes); Fable's 'Intent framing: give the reason behind the request' is the I0 fact |  |  | “`tool_choice` `any` or `tool` returns 400” | 4364 |
| skills/sc-prompt/references/opus.md | sources frontmatter + header | D | provenance and reading rules for the mirror |  |  | “retrieved: 2026-09-30” | 520 |
| skills/sc-prompt/references/sonnet-5-5.md | Behavioral delta + Request configuration | C | per-model facts (400s, effort ladders, failure modes); Fable's 'Intent framing: give the reason behind the request' is the I0 fact |  |  | “Thinking cannot be disabled” | 3998 |
| skills/sc-prompt/references/sonnet-5-5.md | sources frontmatter + header | D | provenance and reading rules for the mirror |  |  | “retrieved: 2026-09-30” | 520 |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| MODE_Brainstorming | user states an idea/need | action instruction ('I want to build a web app') | asks, does not infer: 'Discovery: Problem solved? Target users?' (example only, no gate) |
| MODE_Brainstorming | user asks for a recommendation | option request (R3) | 'give two or three options with their trade-offs' — output shape, no 'no default' clause |
| MODE_Business_Panel | user poses a (often yes/no) question | question + implied domain frame | 'Surface trade-offs before conclusions'; 'Apply 2-3 frameworks per question' (R2/R3). No premise test (R1); domain_routing accepts the user's framing |
| MODE_Business_Panel | synthesis | own lens outputs | 'Synthesis closes: where the lenses agree and the trade-off that splits them' — landscape not verdict (example only) |
| MODE_DeepResearch | research request | action instruction, possibly with a prior belief embedded (A1) | none — no purpose/criterion step; Name-Verification covers only unknown names |
| MODE_DeepResearch | each retrieved source | document (A2) | 'cross-check each load-bearing claim against ≥2 independent sources' |
| MODE_DeepResearch | sources disagree / claim thin / question open | invalidating evidence (A3) | 'change the search plan when sources disagree on a load-bearing claim' |
| MODE_Introspection | review of own earlier reasoning | prior plan / prior output (A3) | none — 'State assumptions, then verify them against evidence' is an exhortation; no re-plan or re-entry rule |
| MODE_Orchestration | task to route | action instruction | none (routing only) |
| MODE_Orchestration | delegate / Workflow returns | delegate's result (A4/A2) | 'cited-file:line revalidation ... stays mandatory' (pointer to RULES_DELEGATION) |
| MODE_Task_Management | 'Implement auth system' | action instruction (I0) | none — example decomposes immediately into Phase 1-4 |
| MODE_Task_Management | 'Continue from last session' / after compaction | prior plan + checkpoint (A3) | none; 'resume from the last checkpoint' and 'never work outside the task list once one exists' lock the prior plan |
| MODE_Token_Efficiency | subagent returns | delegate's result | 'does not waive the cited-file:line revalidation' (duplicate pointer) |
| MODE_Token_Efficiency | context ≥60 % / compaction | compaction event (A3 re-entry) | none — <compaction> has preserve/discard only, no re-derive-purpose or re-validate-plan rule |
| MODE_Token_Efficiency | reporting a decision | option list → report | negative: example compresses 'six options' to 'the recommendation' (R3 harm) |
| MODE_Verbalized_Sampling | query arrives | action instruction + diversity hints | route only; 'factual single-answer → no overlay' |
| MODE_Verbalized_Sampling | after generating candidates | own text (A3 micro) | 'attach probabilities and descriptive names only AFTER the text exists' |
| MODE_Verbalized_Sampling | synthesis / handing to user | option list (R3) | 'Present k candidates as a set, not a ranking ... the user picks' |
| RESEARCH_CONFIG | before execution | query | 'planning: objectives+strategy+criteria' (gate; not injected by the mode); 'ambiguous, broad \| Clarify first (max 3 questions)' |
| RESEARCH_CONFIG | after each hop | new sources | 'triggers="thin sources\|contradictions\|core question unanswered" ... maybe_replan' |
| sc-author | request to write/revise a document | action instruction (I0) | none before drafting — Step 1 resolves type/path/format only; the success criterion (trigger prompts) appears in Step 7, after writing |
| sc-author | in-context authoring rules / project docs | documents (A2) | preamble: 'authoring rules already in context ... do not shape this document'; Step 3: 'for two things only: format ... and language' |
| sc-author | author-check output | tool document | 'An N finding ... goes back to step 4 as a candidate and waits for approval' |
| sc-author | person rejects candidates | human decision | accepted as final ('drop the candidates they reject') — correct, the person is the owner |
| sc-prompt | prompt text to rewrite | document that may itself contain anchors (A1) | Step 3 'Diagnose both directions' runs detectors first; 'Embedded anchor' row rewrites the prompt so the target model estimates before seeing the prior |
| sc-prompt | model-migration reference + mirror files | documents (A2) | 'On conflict the reference wins'; 'never use a recalled value in place of a read' |
| sc-prompt | producing the rewrite | output with context slots (I0 for the target model) | 'Reason: why the work is asked for' and 'Quality bar: what good means here, what done looks like' are required slots or [FILL] |
| sc-prompt | own impulse to add 'helpful' context | self-generated claims (A2 self) | 'An addition with no source is deleted, not reported' |

**I0 check per file** — a step that makes the model state the purpose behind the request and derive a success criterion before acting:

- MODE_Brainstorming: no (asks the user 'Problem solved?' in an example; no rule).
- MODE_Business_Panel, DeepResearch, Introspection, Orchestration, Task_Management, Token_Efficiency, Verbalized_Sampling: no.
- RESEARCH_CONFIG: partial — `planning: objectives+strategy+criteria` gate requires criteria before execution, says nothing about purpose, and the mode never injects it.
- sc-author: no before drafting; Step 7 ('prompts that should trigger the document and one similar that should not') is a criterion produced after writing.
- sc-prompt: yes, but for the target prompt, not for itself — Context targets: “Reason: why the work is asked for” and “Quality bar: what good means here, what done looks like and how success gets checked”; the rewrite must carry them or a `[FILL]` slot.

## 4. Totals per class

| Class | Rows | ~Bytes | Share |
|:-:|---:|---:|---:|
| A | 6 | 1,593 | 1 % |
| B | 19 | 6,628 | 6 % |
| C | 84 | 68,809 | 64 % |
| D | 77 | 29,149 | 27 % |
| total | 186 | 106,179 | |

Reading of the totals: 64 % of the bytes are project facts (C) — dominated by sc-prompt's model facts and detector table, sc-author's harness facts and fields.yaml, and the VS mode's params/templates. 6 % is genuine structural remedy (B), concentrated in three places (DeepResearch verification/replan, VS output shape, sc-prompt anchor/verifiability/context rows). 29 % is deletable or rewritable (A+D), of which the eight modes' role/thinking/priorities/examples/bounds-never blocks are the recurring pattern. B for I0 against the model's own behavior is 0 bytes.

## 5. Top 10 findings (ranked)

1. **I0 gap is total for the model's own behavior.** No mode or skill in scope contains a step that makes the model state the purpose behind the request and derive a success criterion before acting. The three nearest things are sc-prompt's Context targets ('Reason: why the work is asked for' — but it repairs the user's prompt for another session), RESEARCH_CONFIG's three-word gate 'planning: objectives+strategy+criteria' (never injected by the mode), and Brainstorming's example question 'Problem solved?' (asks the user, example only). MODE_Task_Management's own example takes 'Implement auth system' straight to Phase 1-4.

2. **MODE_Task_Management reinforces A3 instead of remedying it.** 'Orient to the current position (load context, identify the phase, resume) before acting', 'resume from the last checkpoint' and the bound 'never ... work outside the task list once one exists' tell the model to re-enter a prior plan without checking whether evidence has invalidated it. This is the one mode that governs re-entry after a session break and it has no re-plan trigger. Rewrite State-Aware as: re-read the goal, list evidence gathered since the plan, decide whether the plan survives, then resume.

3. **Post-compaction re-entry rule is missing where it belongs.** MODE_Token_Efficiency <compaction> defines the trigger (60 %) and the preserve list but says nothing about what the model does on the first turn after /compact. A3 fixtures need: restate purpose and criterion from the preserved summary, re-validate the open plan against current file state. Zero bytes exist for this.

4. **MODE_Token_Efficiency example works against R3.** Row three of <examples>: 'Listing all six options considered before the recommendation → The recommendation, and the one option that was close.' Under --uc this instructs exactly the compression the R3 fixture measured ('Decision: No' with the conditional buried). Replace with: keep every live option and its condition; drop the narration of how they were found.

5. **MODE_Introspection is 2.3 KB of exhortation in the one mode that should own A3.** Every section is D: 'State assumptions, then verify', 'Check against superclaude standards' (repo leak), emoji markers. Either delete the mode or rebuild it as the self-anchor remedy: a mandatory 'what would make my current plan wrong, and have I seen it' check with a re-plan rule.

6. **Largest A/D deletions (approx. 21 KB).** MODE_DeepResearch <example quoting-retrieved-sources> 1.1 KB (paraphrase policy, unrelated to research); MODE_Verbalized_Sampling paper provenance + research gotchas ~1.4 KB; quality.md Writing guidance 1.8 KB + Audit checklist 0.7 KB + provenance 1.4 KB; format-xml 'When tags help' 0.4 KB (A); every <role><mission> and <thinking> block across the eight modes ~3.6 KB; RESEARCH_CONFIG <replanning> + execution gate 0.7 KB (verbatim duplicates of the mode); sc-prompt invocation table 0.9 KB; the five 'Project format and language' restatements of the isolation rule in sc-author references ~2.0 KB; modes/README.md 3.0 KB (not injected, but carries a repo path and pytest command).

7. **Real B mechanisms worth keeping (6.6 KB total).** DeepResearch Source-Verification (≥2 sources, A2) and Replan (A3); RESEARCH_CONFIG <reflection> (A3); Verbalized Sampling 'set, not a ranking ... the user picks' and label-after-text (R3/A3); sc-author preamble isolation of in-context rules and project docs (A2) plus evidence-before-removal; sc-prompt Embedded-anchor row (A1: own estimate and criterion first, prior afterwards as one input), Verifiability switch (criterion stated first), Context targets Reason/Quality bar (I0), 'never use a recalled value in place of a read' (A2); Orchestration Schema-vs-Evidence (A4). Note that the only R3 mechanics (VS, Business Panel) are opt-in overlays and never reach a default session.

8. **Exhortations that read as remedies but are D.** Business Panel 'Assumption Surfacing: Make implicit assumptions explicit before concluding' (stated twice, no gate); DeepResearch <thinking> 'question each source and look for bias'; Introspection 'Hypothesis-Testing: State assumptions, then verify'; Orchestration 'Verification-First ... never assume correctness'; Brainstorming 'Discover constraints > assume them'; Business Panel 'skipping context gathering' in <never>. None changes ordering or what information reaches whom.

9. **sc-author has the success-criterion step in the wrong place.** Step 7 produces 'one or two [prompts] that should trigger the document and one similar that should not' — that is a success criterion for the document, generated after it is written. Moving it to Step 1 (before Resolve settles path/format) gives the skill an I0 gate: what behavior should this document change, and which prompt would show it. Also missing from Step 1: the purpose of the document, as opposed to its type.

10. **Five-fold and two-fold duplication of the few B rules.** VS post-hoc-label rule appears in <thinking>, <behaviors>, <output_format>, <gotchas> and <bounds>; Replan appears in MODE_DeepResearch and twice in RESEARCH_CONFIG; the sc-author isolation rule appears in the preamble, Step 3, format-xml and four type references. Keep one copy each at the point of use (the behaviors/steps), drop the rest: ~3 KB.

## 6. Not read

- ~/.claude/, the repo's .claude/, docs/, CHANGELOG.md, README.md (root), tests/, core/, agents/, commands/, mcp/, output-styles/ — excluded by the isolation rule.
- src/superclaude/ARCHITECTURE.md and scripts/context_loader.py — grepped only for mode delivery (on-demand whole-file injection, README skipped, RESEARCH_CONFIG not injected); not classified.
- core/rules/RULES_DELEGATION.md, core/FLAGS.md, commands/sc/save.md — pointed to by Orchestration/Token-Efficiency/Research sections; out of scope, so the duplicate/pointer judgments assume the SSOT exists there as stated.
- skills/sc-author/references/fields.yaml `tool_names` list and per-type field lists were not verified against Claude Code docs (web search forbidden); classified C on the assumption they are accurate.
