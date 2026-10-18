# Phase 2 analysis 03b — modes/ and skills sc-author, sc-prompt — part 2 of 3

> Continuation of [part 1](./03b-analysis-modes-skills-1.md) (split by size; content unchanged).

## 2. Classification table (continued)

| File | Section | Class | Reason | Failure (B) | Mechanism or exhortation (B) | Quote | ~Bytes |
|---|---|:-:|---|---|---|---|---:|
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
