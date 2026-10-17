---
feature: reframing-anchoring
phase: analysis
doc: 04b-ponytail-content-structure
status: draft
revised: 2026-10-17
---

# 04b — Ponytail lean criteria applied to the content structure (ADAPTATION)

**This is an adaptation.** The ponytail lean criteria (delete / reuse-merge / yagni / split / stdlib-native) were written for code. Here the "codebase" is the superclaude content tree — 37 commands, 25 agents, 10 mode files, the `core/` kernel + `core/rules/` modules, `mcp/` docs, `skills/` — plus the one piece of code that routes it, `scripts/context_loader.py` `TRIGGER_MAP`. Mapping used:

| Ponytail criterion | Content reading |
|---|---|
| delete (dead code) | content never loaded: no trigger, no `description` route, no `<handoff>`, no command names it, flag nobody can discover |
| reuse / merge | two files that must change together (same roster, same `gh` command, same gate) but are never co-loaded |
| yagni | an abstraction with one implementation: a mode/agent/command trio where only one of the three is ever in context |
| split | one file carrying unrelated jobs |
| stdlib / native | Claude Code already does it (slash-command dispatch, agent memory instructions, subagent return semantics) |

Evidence rules followed: before calling anything dead or unrouted, the whole `src/superclaude` tree, `TRIGGER_MAP`, every frontmatter `description`, and every `<handoff next=…>` were grepped. Isolation: only `src/superclaude/**`, `src/superclaude/ARCHITECTURE.md`, `scripts/context_loader.py`. No `~/.claude`, repo `.claude/`, `docs/`, README/CHANGELOG, no web. Byte counts are `wc -c` on LF files.

---

## 1. Size table

### Per directory (installed content only; `README.md` files are not installed and are excluded from the lean count)

| Directory | Files | Bytes | Note |
|---|---|---|---|
| commands/ | 37 | 160,391 | incl. commands/README.md 3,277 |
| agents/ | 25 | 153,064 | incl. agents/README.md 9,973 |
| modes/ | 10 | 37,799 | 8 modes + RESEARCH_CONFIG 3,749 + README 2,951 |
| core/ (top) | 5 | 17,005 | FLAGS 5,172 · PRINCIPLES 2,169 · RULES 4,838 · BUSINESS_SYMBOLS 2,488 · README 2,338 |
| core/rules/ | 4 | 33,709 | QUALITY 13,594 · DOCS 10,220 · DELEGATION 8,757 · INTERACTION 1,138 |
| mcp/ | 4 | 17,473 | Playwright 4,759 · Chrome-DevTools 3,214 · Tavily 2,730 · README 6,770 |
| skills/ | 14 | 68,914 | sc-prompt 30,612 · sc-author 38,302 |
| output-styles/ | 2 | 5,578 | |
| templates/ | 4 | 4,795 | docs-scaffold, used by /sc:init task [i] |
| **Total content** | 105 | **498,728** | |
| ARCHITECTURE.md | 1 | 12,782 | |
| scripts/context_loader.py | 1 | 48,435 | |

### Always-loaded chain (`CLAUDE_SC.md` → `@core/FLAGS.md @core/PRINCIPLES.md @core/RULES.md`)

| File | Bytes | chars/4 tokens |
|---|---|---|
| CLAUDE_SC.md | 50 | — |
| core/FLAGS.md | 5,172 | 1,278 |
| core/PRINCIPLES.md | 2,169 | 539 |
| core/RULES.md | 4,838 | 1,202 |
| **Chain** | **12,229** | **~3,020** |

### What one `/sc:` prompt actually injects (loader, 8,000-token budget, chars/4)

| Prompt | Injected | Tokens |
|---|---|---|
| `/sc:analyze` | RULES_QUALITY + RULES_DOCS + RULES_INTERACTION | 6,174 |
| `/sc:task` | RULES_QUALITY + RULES_DELEGATION + RULES_INTERACTION | 5,820 |
| `/sc:analyze --delegate` | QUALITY + DELEGATION + DOCS = **8,072 > 8,000** → RULES_DOCS skipped, INTERACTION fits | 5,820 |
| `/sc:research` | Tavily Tier-1 string + MODE_DeepResearch + RULES_DOCS + RULES_INTERACTION | ~4,100 |
| `/sc:business-panel` | MODE_Business_Panel + RULES_INTERACTION | 1,280 |
| `/sc:brainstorm` | RULES_DOCS + RULES_INTERACTION (**not** MODE_Brainstorming) | 2,816 |

### Largest single files

skills/sc-prompt/SKILL.md 16,344 · core/rules/RULES_QUALITY.md 13,594 · skills/sc-author/references/quality.md 10,837 · core/rules/RULES_DOCS.md 10,220 · agents/project-initializer.md 9,595 · modes/MODE_Verbalized_Sampling.md 8,860 · core/rules/RULES_DELEGATION.md 8,757 · agents/verifier.md 8,578 · commands/insight.md 8,202.

### Section-level totals (what the bytes are spent on)

| Commands (36) | Bytes | Agents (24) | Bytes |
|---|---|---|---|
| `<flow>` | 28,238 | `<tool_guidance>` | 22,688 |
| `<examples>` | 23,452 | `<actions>` | 12,767 |
| `<gotchas>` | 15,879 | `<memory_guide>` | 12,287 |
| `<flags>` | 13,409 | `<gotchas>` | 11,358 |
| `<bounds>` | 10,318 | `<examples>` | 10,808 |
| `<role>` | 5,412 | `<focus>` | 10,543 |
| `<syntax>` | 3,848 | `<bounds>` | 10,529 |
| | | `<checklist>` | 8,447 |

---

## 2. Answers to the six questions

### (1) `TRIGGER_MAP` — what maps where, what cannot fire, what fires too broadly

All 16 entries map to files that exist (checked: `mcp/MCP_{Tavily,Playwright,Chrome-DevTools}.md`, `core/BUSINESS_SYMBOLS.md`, 8 `modes/MODE_*.md`, 4 `core/rules/RULES_*.md`). `modes/RESEARCH_CONFIG.md` has no trigger, by design (ARCHITECTURE.md §modes).

**Alternatives that cannot realistically fire** (the phrase is documented nowhere in the content tree, so no user is told to type it):

| Regex alternative | Target | Evidence |
|---|---|---|
| `vs-(cot\|multi\|standard)` | MODE_Verbalized_Sampling | FLAGS.md and brainstorm.md spell the syntax `--vs cot` / `--vs [standard\|cot\|multi]` (space). The hyphenated form appears only as the mode's own section labels "VS-CoT"/"VS-Multi"; `--vs\b` in the same regex already covers every documented form. |
| `business.?symbol\|strategic.?symbol\|business.?example\|panel.?example` | core/BUSINESS_SYMBOLS | 0 hits for any of these phrases outside the loader. The only documented path is `/sc:business-panel --structured` (business-panel.md `--structured` flag), which is the fifth alternative. |
| `analyze reasoning` | MODE_Introspection | 0 hits anywhere in content. `self.?analysis` has exactly 1 hit (FLAGS.md `--introspect: self-analysis, …`). |
| `fact.?check` | MCP_Tavily | 1 hit, in MCP_Tavily.md itself (a file that is only injected as a Tier-1 string). Fires only if the user independently says "fact-check". Harmless but undocumented. |

**Fires for prompts it should not** (cross-domain):

| Regex alternative | Target | Concrete misfire |
|---|---|---|
| `multi.?expert` | MODE_Business_Panel (3,992 B) | spec-panel.md's description, mission and flow say "multi-expert" 13 times across 6 files. A user asking for "a multi-expert spec critique" (the exact wording of spec-panel's description) gets the **business** panel mode injected — its `<experts>` table is Porter/Christensen/Drucker, not Osmani/Hickey/Beck. |
| `strategic.?analysis` | MODE_Business_Panel | 1 hit in content (business-panel-experts.md mindset). Any prompt containing "strategic analysis" of code/architecture loads the business roster. |
| `tool.?select` | MODE_Orchestration (4,196 B) | "tool selection" is ordinary English; 8 hits across 5 files including FLAGS.md's own mission line. |
| `worktree`, `sub.?agent` | RULES_DELEGATION (8,757 B) | 100 and 129 hits across the tree — these words appear in ordinary status reports ("the subagent returned…"). Harness turns are filtered (`_HARNESS_TURN_PREFIXES`), but a user quoting one is not: `check_triggers()` receives the raw prompt, **not** `scannable_prompt()` (main(): `trigger_prompt = strip_unresolved_commands(prompt, …)`; `check_triggers(trigger_prompt)`), so a flag or keyword inside a fenced block, inline code or blockquote fires every TRIGGER_MAP entry even though the same text is blanked for flag resolution and execution directives. Five modes carry a prose `<fallback>` sentence ("Revert to default behavior when … a flag or keyword that appeared only in quoted, pasted or code text …", 1,590 B total) that exists to paper over this one missing call. |
| `/sc:\w+` | RULES_INTERACTION | Fires on every `/sc:` prompt; 1,138 B, P2, deliberate. Acceptable. |

**Budget interaction (correctness, not size):** RULES_QUALITY (3,358 tok) + RULES_DELEGATION (2,180) + RULES_DOCS (2,534) = **8,072 tokens**, 72 over `MAX_TOKENS_ESTIMATE`. `/sc:analyze --delegate`, `/sc:task … implementation plan`, `/sc:implement --delegate --plan …` all trigger the three at once on a fresh session. `check_triggers()` calls `mark_as_loaded()` for every matched file **before** `output_inject_mode()` applies the budget, so the skipped RULES_DOCS is recorded as loaded and is never injected again until `/clear`. analyze.md step 5 and the whole `doc_output_convention` then run from memory.

**Dead flag plumbing:** `VALID_FLAGS` lists `scope`, `focus`, `plan`, `validate`, `safe-mode`, `verbose-context` with no TRIGGER_MAP or directive except `--plan` (directive) and `--safe-mode` (→ MODE_Token_Efficiency); they are documented in FLAGS.md so they are not dead, only prose-only. `--task-manage`, `--introspect`, `--orchestrate` are typed by nobody the content tree knows about: **no command or agent file mentions any of them** (rg across commands/ and agents/: 0 hits); they exist only in FLAGS.md's one-line list and the loader.

### (2) Naming Trinity — does each of mode / agent / command carry distinct content?

ARCHITECTURE.md §Naming Trinity names two domains (Research, Business) and asserts "These are not redundant". Checked per axis; quotes are verbatim.

**Research** — MODE_DeepResearch (4,162) · agents/deep-researcher (7,353) · commands/research (3,922) · plus modes/RESEARCH_CONFIG (3,749), which the mode and the command both point to.

| Content | Copies | Where |
|---|---|---|
| "each load-bearing claim needs ≥2 independent sources, except a claim settled by one primary source (the official documentation, specification, or primary record of the thing itself); label a claim with only one source as single-source" | **8** | MODE `<behaviors>` Source-Verification **and** Replan; research.md `<gotchas>` single-source; deep-researcher `<focus>` Evidence, `<actions>` 4, `<evidence>`, `<checklist>`; RESEARCH_CONFIG `<gates>` **and** `<replanning>` |
| Credibility tier 1–4 table (academic/gov → forums/blogs) | 2 | RESEARCH_CONFIG `<credibility>`; deep-researcher `<evidence>` (inline) |
| Hop patterns entity/temporal/conceptual/causal | 2 | RESEARCH_CONFIG `<hop_config>`; deep-researcher `<hop_patterns>` |
| Depth profiles quick/standard/deep/exhaustive | 3 | RESEARCH_CONFIG `<depth_profiles>`; research.md `<depth>`; deep-researcher `<depth_behavior>` |
| Strategy planning/intent/unified | 2 | RESEARCH_CONFIG `<strategies>`; research.md `--strategy` flag text |
| Tool routing tavily/playwright/context7 → fallback | 2 | RESEARCH_CONFIG `<tool_routing>`; deep-researcher `<tools>` |

What is distinct: the mode's `<thinking>/<communication>/<priorities>` (4 lines + the quoting example), the agent's `<outputs>` shape and `<tool_guidance>`, the command's doc-output path and the two flags. RESEARCH_CONFIG carries nothing the agent does not restate except the numeric sources/hops/iter table (`10/1/1 … 50+/5/5`), `<output_formats>` and `<errors>`; it is never injected and never Read by a flow step (research.md only cites it in two `note=` attributes). Its `<memory case_based="true" pattern_learning="true" cross_session="true"/>` is an empty element.

**Business** — MODE_Business_Panel (3,992) · agents/business-panel-experts (6,212) · commands/business-panel (3,333) · core/BUSINESS_SYMBOLS (2,488).

| Content | Copies | Where |
|---|---|---|
| The nine-expert roster | **4** | MODE `<experts>` table (585 B); agent `<focus>` (one line per expert); command `<experts>` ("frameworks per agents/business-panel-experts.md `<focus>` (SSOT)" — the command already declares the agent SSOT); BUSINESS_SYMBOLS "Expert (Framework)" list + `<expert_selection>` (406 B) |
| Discussion / Debate / Socratic and which domain picks which | 4 | MODE `<interaction_modes>` + `<domain_routing>` (763 B); agent `<modes>`; command `<modes>`; BUSINESS_SYMBOLS `<templates>` (306 B) |
| "2-3 lenses/frameworks" | 4 | MODE behaviors Multi-Lens; agent `<modes>` + `<checklist>`; command flow 2; BUSINESS_SYMBOLS `<config_defaults>` ("experts: 2-3 by default") |
| "Label which framework drives each" / "never present opinions as consensus/facts" | 3 | MODE `<communication>` + `<never>`; command gotcha opinion-as-fact; agent tool_guidance Never |
| lens-not-impersonation | 3 | MODE `<never>` "impersonating an expert persona"; agent gotcha; spec-panel.md gotcha (same sentence, different panel) |

What is distinct: the mode's `<thinking>` (4 bullets), the agent's `<outputs>` (Panel-Report / Trade-Off-Map / Next-Steps) and the subagent-vs-main-session Socratic note, the command's 6 flags, BUSINESS_SYMBOLS's emoji symbols and abbreviations. Loading reality: `/sc:business-panel` injects MODE + command; the agent is reached only by CC auto-delegation (no command names it except the SSOT pointer); BUSINESS_SYMBOLS only with `--structured`. So in the common path the mode and the command are co-loaded and the roster/mode-routing appear twice in context; the agent's copy — the declared SSOT — is the one not loaded.

**Trios the ARCHITECTURE does not list but that exist:**

| Domain | Mode | Agent | Command(s) | Finding |
|---|---|---|---|---|
| Brainstorm | MODE_Brainstorming (2,197) | requirements-analyst (4,971) | brainstorm (6,197) | `/sc:brainstorm` does **not** load the mode (trigger is `--brainstorm\|--bs` only). brainstorm.md step 1 "Socratic dialogue + systematic questioning" and its `<never>` "overrides the user's vision" restate the mode's Socratic / Non-Presumptive / "User vision > best practice". requirements-analyst is named by pm.md only. |
| Orchestration | MODE_Orchestration (4,196) | project-manager (6,974) | select-tool (3,895), pm, agent, task | The mode's `<behaviors>` Tool-Task Matching = FLAGS.md `<mcp>` (always loaded) + select-tool `<decision_matrix>`; its `<fan_out_execution>` (1,700 B) = RULES_DELEGATION `<workflow_delegation>` (Write-Return, Schema, Cap, Packet — same bullets). No command names the mode's flag `--orchestrate`. |
| Task | MODE_Task_Management (2,388) | project-manager | task (4,285) | Mode: "Plan -> Phase -> Task -> Todo"; command: "Epic → Story → Task → Subtask" — two hierarchies for one feature, never co-loaded (`/sc:task` does not trigger the mode). The mode's trigger `--task-manage` appears in no command/agent. |
| Git | — | git-workflow (6,192) | git (4,115) | see Q4/Q5 — same `gh pr view --json state,reviewDecision,isDraft`, same four PR states, same from-pr procedure, same new-commit gotcha; agent named by no file. |
| Init | — | project-initializer (9,595) | init (6,923) | Same task list (agent `<tasks>` 7 items / command `<menu>` 9 items a–i), same dependency graph; init.md never names the agent; the agent is named only by repo-index.md's `Not for`. |

### (3) Commands grouped by flow skeleton

| Skeleton | Commands | What differs beyond domain words |
|---|---|---|
| **A. analyze → delegate → track → deliver** | agent, pm, task | agent: Phase 1 Clarify gate (no impl until scope + criteria confirmed), fixed services `@deep-researcher`/`@repo-index`, no flags. pm: `--strategy brainstorm\|direct\|wave`, direct-work-first gotcha, PDCA log, no approval gate. task: Epic→Story→Task via TaskCreate, `--strategy sequential\|parallel\|adaptive`, **>3-file approval checkpoint**, `--cleanup --dry-run`, evidence-note completion rule. Handoffs: agent→implement/research; pm→implement/task/research; task→test/implement. Skeleton overlap is by authoring spec; the gates differ, so none is a pure duplicate. agent.md's `<startup>` ("Remind: 💡 Use /context to confirm token budget", "Report: Core services: deep research, repo index") and `<token_discipline>` are persona leftovers not tied to any step. |
| **B. gather → draft → approve → save (doc_output_convention)** | intent, brainstorm, design, plan, roadmap, research, analyze `--format report`, document, index, index-repo, promote-feature | The sentence "slug resolution (zero-match default `[f]`/`[s]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`" is copied into 6 flow steps (analyze, brainstorm, design, plan, research, roadmap) + intent. Gates: brainstorm (Approve + hard review gate), intent (Approve), plan (stop on `status: draft` spec, ask on open concerns), design (none — Concerns listed), roadmap (**none** — writes the same `05-plan.md` path as plan without plan's review gate). |
| **C. analyze → plan → execute → validate → report** | implement, improve, cleanup, build, git, test, troubleshoot | implement: `--plan` deviations protocol, >3-file checkpoint, Phase Gate. improve: thinnest (2,313 B), 5 generic steps, `--safe/--interactive`. cleanup: `--type docs` validator + `--apply` gate, auto_fix_threshold. troubleshoot: failing-test-first + commit rule, 3-hypothesis cap. test: thresholds, verifier dispatch. git: safety_rules tiers, PR status. build: `--clean` scope rule. |
| **D. assemble panel → analyze → collaborate → synthesize** | business-panel, spec-panel, (review) | business-panel: 9 experts, 4 modes, `--structured`. spec-panel: 6 experts, 3 modes, `--iterations` escalation gotcha. review: 9-step incl. Challenge, Spec gate (**sets `status: approved-for-plan`**), `--audit-delegated`. spec-panel and `review --scope spec` both review a spec; only review changes status. |
| **E. parse → classify → map → recommend (read-only)** | recommend, select-tool, help, sc, explain, estimate, reflect | help and sc both carry a 36-line command catalogue (`<commands>`, ~1.2 KB each), differing only in capitalisation ("Session controller + workflow orchestration" vs "session control + workflow orchestration"); recommend carries a third mapping (`<keyword_map>`). sc.md's flow is "invoke the matching /sc:<name> command via the Skill tool" — which is what Claude Code does natively when the user types `/sc:<name>`; its `<syntax>` `/sc:[command]` is not a command a user can type. |
| **F. load/persist session state** | load, save, insight, init | Four stores: `.claude/memories/` (save/load), auto memory (save/load), `.claude/insights.jsonl` (insight), `.claude/rules/gotchas/` (RULES kernel, init [h], reflect). A fifth, `docs/memory/patterns/` + `docs/memory/mistakes/`, exists only in agents/project-manager.md (`rg docs/memory` → 1 file). |
| **G. autonomous** | auto-improve | standalone; its `never-bare-python` gotcha duplicates insight.md's. |

**Merge candidates with the axes that would be lost**

| Merge | Axes lost if merged (must be carried over) | Bytes freed |
|---|---|---|
| sc.md → delete (help.md keeps the list) | `<meta>` version line (SSOT is pyproject.toml, the line itself says so); unknown-name suggestion (the loader already does this: `resolve_command_name()` emits "Did you mean"). | 3,799 |
| roadmap → `plan --from <prd> --granularity phase` | roadmap's `--strategy systematic\|agile\|enterprise` (text identical to brainstorm's), `--delegate` consult step, unchecked-box + `Evidence:` line rule. Gained: the spec review gate that roadmap currently bypasses on the same output path. | ~2,500 of 4,214 |
| index-repo → `index --type repo` | mode=create\|update\|quick, the 5 KB cap + measured-byte-size report, PROJECT_INDEX.json. | ~1,500 of 2,617 |
| agent → pm `--strategy direct` | Phase 1 Clarify gate, repo-before-web guidance, `<startup>` git check. Skeleton overlap is by design; only the `<startup>`/`<token_discipline>` sections are cut-safe without a merge. | 700 (sections only) |

### (4) Agents — overlapping `description` fields and unreachable agents

Each `description` ends with a `Not for X — other-agent` pointer, so most pairs are distinguishable *by the pointer*. Overlaps that remain, by trigger wording:

| Pair | Trigger text that collides |
|---|---|
| self-review ↔ `/sc:review` (command) | agent: "Use when the user explicitly asks for an independent second pass on a finished work product (/sc:review, …)"; command: "Use when asked for a second opinion or an independent review". Same trigger, two routes; review.md's `<tools>` Agent entry dispatches "isolated reviewer subagent" **without naming self-review**, and its `<focus_agent_mapping>` names security/performance/quality/system-architect only. |
| git-workflow ↔ `/sc:git` | "smart commits, PR flow and safety enforcement … draft conventional commits, review PR status" vs "Git operations with smart commit messages and workflow guidance … --pr-status". git.md never names the agent; it runs git with Bash. |
| project-initializer ↔ `/sc:init` | "set up a repository for Claude Code, or CLAUDE.md and memory scaffolding are missing" vs "Interactive project setup … first-session onboarding". init.md never names the agent. |
| project-manager ↔ insight-analyst ↔ `/sc:insight` | pm: "record a pattern after an implementation or a root cause after a mistake"; insight-analyst: "what was learned before"; /sc:insight: "Capture structured session insights". Three agents/commands for "write/read a lesson", writing to three different stores. |
| learning-guide ↔ socratic-mentor ↔ `/sc:explain` | "wants to learn a concept" / "asks to be questioned toward a concept" / "structured walkthrough tailored to an audience". Distinct in letter; explain.md does not name either agent. |
| backend-architect ↔ system-architect ↔ devops-architect | mutually cross-pointed; distinguishable. |
| refactoring-expert ↔ simplicity-guide | cross-pointed (existing vs not-yet-written code); distinguishable. |

**Agents named by no command, no `<handoff>`, no core rule** (reachable only through CC auto-delegation on their `description`, or `claude --agent`): **devops-architect, git-workflow, insight-analyst, learning-guide, project-initializer, python-expert, refactoring-expert, root-cause-analyst, simplicity-guide, socratic-mentor, technical-writer, self-review** (12 of 24; self-review's only mentions are the generic word in RULES_DOCS/DELEGATION and brainstorm's step name). Of these, the ones whose trigger is *also* claimed by a command (git-workflow, project-initializer, self-review) have no distinct trigger. The other nine have distinct descriptions and are legitimately CC-native.

`<handoff>` fields on agents point only at `/sc:` commands; no agent hands off to another agent, so agent→agent routing is entirely inside `<fallback>` prose ("escalate to requirements-analyst …").

### (5) Gotchas and bounds repeated across files

Exact-sentence scan (≥60 chars, XML stripped) found **15,827 redundant bytes** in verbatim copies; the paraphrased families below add more.

| Sentence (verbatim or near) | Copies | Files | Bytes |
|---|---|---|---|
| "As a delegated subagent Claude cannot ask mid-task: wherever this file says to ask the user or get the user's confirmation, it stops before that step and returns the proposed action and the question in its report. The task text counts as confirmation only for a reversible action it names with its target; a destructive or irreversible one needs the user's own approval quoted in the task." | 24 | every agent `<tool_guidance>` Ask First | 389 × 24 = **9,336** |
| "MEMORY.md = prior lessons; verify against current state before acting on them. After task: save a lesson only if a future run would act differently, in the file layout Claude Code's memory instructions give." | 24 | every agent `<memory_guide>` | 209 × 24 = **5,016** |
| "Symbolic-First: with a symbol-aware tool connected (LSP or code index), query overview → definition → references before whole-file Read" / "…prefer symbol-aware queries (when connected) or targeted Grep over whole-file Read…" | 19 (+ explain.md symbolic-first gotcha, + MODE_Orchestration priorities, + select-tool matrix row) | 11 + 4 + 2 agents in three wordings | ~2,900 |
| ≥2-independent-sources / single-source rule | 8 | see Q2 Research | ~1,800 |
| "slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`" | 7 | analyze, brainstorm, design, plan, research, roadmap, intent | ~900 |
| "Coverage beats filtering: Claude reports every finding, including low-severity…" + "Each finding carries `severity: … confidence: …`" + "When the user explicitly limits the scope…" (the whole `<finding_policy>` block) | 3 | quality-engineer, security-engineer, self-review | ~1,400 |
| evidence-fabrication: "Do not construct hypothetical failure scenarios to justify a pre-existing recommendation. Evidence (code, config, measurements) must precede proposals." | 3 | analyze, brainstorm, troubleshoot gotchas | ~480 |
| analysis-loop: "If reasoning reaches the same conclusion twice on the same question, end that line…" | 4 | analyze, brainstorm, troubleshoot, spec-panel (iteration-escalation cites it) | ~500 |
| workflow-fanout / Write-Return: "fan-out subagents RETURN … — subprocess writes discarded; main loop performs the Write" | 5 | design, plan, implement gotchas; task gotcha (workflow-task-state); MODE_Orchestration; RULES_DELEGATION (the declared "full rule") | ~1,100 |
| ">3 files → numbered plan → wait for approval" | 9 | RULES_QUALITY ×3, RULES_INTERACTION, RULES_DELEGATION, PRINCIPLES, FLAGS, implement ×2, task ×2 | ~900 |
| "Apply [R18 Necessity Test] …" | 6 files | RULES, RULES_QUALITY, RULES_DOCS, design, improve, spec-panel | ~400 |
| "Revert to default behavior when this mode was loaded by a keyword match … or by a flag or keyword that appeared only in quoted, pasted or code text …" | 7 | every mode `<fallback>` | 1,590 |
| "…unrelated to the global --focus / --scope / --safe-mode / --validate / --plan" | 9 | cleanup, business-panel, auto-improve, reflect, improve, review, implement, spec-panel | ~600 |
| `--strategy systematic\|agile\|enterprise: systematic works through every requirement area in order; agile splits…; enterprise adds compliance…` | 2 | brainstorm, roadmap (identical) | 290 |
| existing-check / existing-plan / existing-spec / check-existing / already-done ("check if X already exists before creating") | 5 | design, plan, spec-panel, init, task | ~350 |
| stale-list / phantom-command ("command list may go stale; verify against commands/sc/") | 3 | help ×1, sc ×2 | ~250 |
| "new-commit: never amend unless asked" | 2 | git.md, git-workflow.md | 160 |
| never-bare-python | 2 | insight, auto-improve | ~600 |
| lens-not-impersonation | 2 (+ MODE never) | business-panel-experts, spec-panel | ~350 |
| intent-confirm / scope-anchoring | 3 each | project-manager, root-cause-analyst, business-panel-experts | ~500 |

### (6) XML sections that carry no instruction

| Section | Where | Why it carries nothing |
|---|---|---|
| `<role command="/sc:x"><mission>…</mission></role>` | all 36 commands (5,412 B) | The mission is the first clause of the frontmatter `description` (analyze: description "Code analysis across quality, security, performance, architecture domains, with severity-rated findings…" / mission "Code analysis across quality, security, performance, architecture domains"; help: identical strings; 34 of 36 are prefix-copies). The `command=` attribute restates the filename. |
| `<bounds><does>` in commands | 36 (part of 10,318 B) | Restates the mission/flow as a noun list: explain `<does>clear explanations, agent expertise, framework integration.</does>`; design `<does>comprehensive specs, multi-format output, validation.</does>`; sc `<does>command dispatch, feature routing, context-aware help.</does>`; pm `<does>orchestration, auto-delegation, self-documenting.</does>`. |
| `<bounds><never>` tautologies | ~20 commands | explain `<never>explains without analysis, overrides standards, or reveals sensitive information.</never>`; index `<never>override manual docs, generate without analysis, bypass standards.</never>`; roadmap `<never>… generates without analysis</never>`; estimate `<never>… estimates without analysis</never>`; pm `<never>bypasses documentation.</never>`. "X without analysis" is the flow's step 1; "overrides standards" is the RULES kernel's project_rules_priority. The `<never>` lines that **do** carry a rule (build: "modifies build config, installs dependencies, deploys"; cleanup: "deletes files only after the user confirms the listed paths"; test: "generates test cases outside an explicit --tdd request") are the ones to keep. |
| `<memory case_based="true" pattern_learning="true" cross_session="true"/>` | RESEARCH_CONFIG | empty element, attributes name no action. |
| `<checklist>` items that restate `<actions>` | agents, 8,447 B | business-panel-experts action 3 "Run each lens's questions, collect insights and list assumptions" ↔ checklist "2-3 relevant lenses applied"; socratic-mentor action 4 "Reveal the concept name only after the learner articulates the idea" ↔ checklist "Principle named only after the learner articulates the idea". ~half of checklist lines are the actions list in past tense. |
| `<meta>` | sc.md | "version: 4.27.2 (SSOT: pyproject.toml — answer version queries via `superclaude --version`)" — tells the reader not to use the value it carries. |
| `<startup>` Report / Remind lines | agent.md | "Report: Core services: deep research, repo index" and "Remind: 💡 Use /context to confirm token budget" — status-line text, no decision. |
| `<description>` sub-elements | git.md `<pr_status_integration>`, task.md `<task_cleanup>` | "PR review status indicator", "Task cleanup via TaskUpdate delete" — a title repeated as an element. |
| `<tools>` lists of native tools | 25 commands | "Read: examine file content and context", "Grep: search patterns across changed files", "Bash: run git and gh commands" — names tools Claude Code already exposes with their own descriptions; only the `Agent:` lines (review, test, implement) carry an instruction. |

---

## 3. Findings

### Must fix

**1. RULES module trio overruns the budget by 72 tokens and the skipped module is marked loaded** (core/rules/RULES_QUALITY.md, RULES_DELEGATION.md, RULES_DOCS.md; scripts/context_loader.py)
- What this is: the three P1 rule modules sum to 8,072 estimated tokens against an 8,000 budget.
- Problem: `/sc:analyze --delegate` (QUALITY via `/sc:analyze`, DELEGATION via `--delegate`, DOCS via `/sc:analyze`) on a fresh session drops RULES_DOCS with a `⚠️ Budget exceeded` comment, and `check_triggers()` has already written it to the dedup cache, so no later prompt re-injects it. analyze.md step 5 then writes the report path from memory.
- Fix: cut ≥300 chars from RULES_QUALITY (the `>3 files` rule is stated three times inside it, lines 12, 13, 32) **or** move `mark_as_loaded` after the budget pass. Both are small.
- If we skip it: every delegated analysis/implement that also produces a doc runs without the doc convention for the whole session.

**2. git-workflow agent and /sc:git are one feature written twice** (agents/git-workflow.md, commands/git.md)
- What this is: same `gh pr view --json state,reviewDecision,isDraft`, same four PR states, same `--from-pr` procedure, same new-commit gotcha. The agent is named by no file in the tree; the command's description says to run git in the main session; the agent's says the same ("Not for one routine commit — the main session commits directly").
- Problem: must change together (a PR state or `gh` flag change hits both), never co-loaded. Two of the agent's gotchas (staged-secret-scan, default-branch-warn) are real rules that the command — the path actually taken — does not carry.
- Fix: delete git-workflow.md; move staged-secret-scan and default-branch-warn into git.md `<gotchas>` (~400 B).
- If we skip it: the secret-scan rule stays on the path nobody routes to. −5,800 B.

**3. /sc:sc duplicates Claude Code's own slash dispatch and the help list** (commands/sc.md)
- What this is: a command whose flow is "invoke the matching /sc:<name> command via the Skill tool", with a 36-entry catalogue copied from help.md and a `<meta>` block that disclaims its own version number.
- Problem: `/sc:[command]` is the native invocation; the unknown-name suggestion is already produced by the loader's `resolve_command_name()`; the catalogue is a second stale-list (its own gotcha says so).
- Fix: delete sc.md. help.md keeps the one list.
- If we skip it: three copies of the command catalogue (sc, help, recommend) to update on every command add. −3,799 B.

**4. The delegated-subagent paragraph is pasted into all 24 agents** (agents/*.md `<tool_guidance>`)
- What this is: 389 characters × 24 = 9,336 B of the identical sentence "As a delegated subagent Claude cannot ask mid-task …".
- Problem: a rule about how *any* subagent returns a question lives in every leaf instead of the one place the caller already assembles — RULES_DELEGATION `<delegate_packet>`, whose `active_mode_directives` field exists precisely because "sub-agents never receive context_loader injections, so … context that must govern the sub-agent travels only if copied".
- Fix: add one `return_rule` line to `<delegate_packet>` (the caller sends it); in each agent keep only the per-agent Ask-First list. Verifier/self-review that run under `claude --agent` as main session are unaffected (the sentence is conditional on delegation anyway).
- If we skip it: a wording fix is a 24-file edit; the sentence also lands in every `claude --agent X` main-session prompt where it does not apply. −8,900 B.

**5. Research domain states its one rule eight times and ships a config file nothing loads** (modes/RESEARCH_CONFIG.md, modes/MODE_DeepResearch.md, agents/deep-researcher.md, commands/research.md)
- What this is: the ≥2-sources/single-source rule in 8 places (4 inside deep-researcher alone); credibility tiers, hop patterns, depth profiles and tool routing each in 2–3; RESEARCH_CONFIG never injected and never Read by a flow step (cited only in two `note=` attributes).
- Problem: four copies of a threshold that must change together; the file that holds the "full profiles" is the one not in context.
- Fix: delete RESEARCH_CONFIG; move its only unique rows (sources/hops/iter numbers, `<errors>`) into deep-researcher `<depth_behavior>`/`<tools>` (~500 B); in deep-researcher keep the rule once in `<evidence>` and reference it from focus/actions/checklist; drop the mode's Replan restatement.
- If we skip it: the next edit to the single-source exception is an 8-site change. −4,600 B.

### Should fix

**6. MODE_Orchestration restates FLAGS `<mcp>` and RULES_DELEGATION `<workflow_delegation>`** (modes/MODE_Orchestration.md)
- What this is: `<behaviors>` Tool-Task Matching points at FLAGS.md (always loaded) for "full routing"; `<fan_out_execution>` (1,700 B) repeats Write-Return / Schema-vs-Evidence / Cap-Aware / Packet-Prompt from RULES_DELEGATION, which the same prompts (`--delegate`, "sub-agent", `/sc:pm|agent|task`) already inject. Trigger `tool.?select` fires on ordinary English; `--orchestrate` is typed by no command.
- Fix: delete the mode; move its two bullets not in RULES_DELEGATION (Pipeline-Default, Context-Carry) there (~350 B); keep select-tool.md as the one tool-routing surface.
- If we skip it: three copies of tool routing (FLAGS, mode, select-tool matrix) plus RESEARCH_CONFIG's fourth. −3,800 B.

**7. mcp/ doc bodies load only under `--verbose-context`** (mcp/MCP_Playwright.md, MCP_Chrome-DevTools.md, MCP_Tavily.md)
- What this is: Playwright and Chrome-DevTools are Tier 0 (one-line `TIER_0_MAP` hint), Tavily is Tier 1 (the `INSTRUCTION_MAP` string); the .md bodies (10,703 B) are read only when `--verbose-context` is typed or `CLAUDE_CONTEXT_USE_INSTRUCTIONS=0`. No command, agent or rule references any of the three files (rg: only mcp/README.md).
- Fix: shrink each file to its hint/instruction string plus the one section README says is the long form (`<cli_vs_mcp>` for Playwright); the loader's "backing file not installed" check then still works.
- If we skip it: 10.7 KB of tool docs that drift unseen because they are never in context. −8,000 B.

**8. Keyword triggers that cannot fire or fire across domains** (scripts/context_loader.py TRIGGER_MAP)
- What this is: `vs-(cot|multi|standard)`, `business.?symbol|strategic.?symbol|business.?example|panel.?example`, `analyze reasoning` are documented nowhere (Q1); `multi.?expert` loads the business mode for spec-panel's own wording; `check_triggers()` ignores `scannable_prompt()`, which seven mode `<fallback>` sentences (1,590 B) compensate for in prose.
- Fix: delete the undocumented alternatives and `multi.?expert`; pass `scannable_prompt(trigger_prompt)` to `check_triggers()`; delete the seven fallback sentences.
- If we skip it: "multi-expert spec critique" keeps loading Porter and Christensen. −1,600 B content.

**9. Agent `<memory_guide>` header is CC-native behaviour pasted 24 times** (agents/*.md)
- What this is: "MEMORY.md = prior lessons; verify against current state … After task: save a lesson only if a future run would act differently, in the file layout Claude Code's memory instructions give." 209 × 24 = 5,016 B. Every agent declares `memory: project`, the Claude Code feature whose own instructions the sentence defers to ("in the file layout Claude Code's memory instructions give").
- Fix: keep the per-agent category bullets, drop the two header lines. (Not verified against Claude Code docs here — isolation rule; the sentence's own wording is the evidence that the native instructions exist.)
- If we skip it: nothing breaks; 5 KB of restated native behaviour. −5,000 B.

**10. Business roster and mode-routing in four files** (modes/MODE_Business_Panel.md, core/BUSINESS_SYMBOLS.md, commands/business-panel.md)
- What this is: Q2 Business table — the nine experts and the Discussion/Debate/Socratic routing in mode, agent, command and BUSINESS_SYMBOLS; the command already names the agent `<focus>` as SSOT.
- Fix: delete the mode's `<experts>` table and BUSINESS_SYMBOLS `<expert_selection>`/`<config_defaults>` (the mode's `<domain_routing>` already carries domain→experts); keep the agent as SSOT.
- If we skip it: adding an expert is a 4-file edit. −1,300 B.

**11. /sc:init and project-initializer carry the same task list without routing to each other** (commands/init.md, agents/project-initializer.md)
- What this is: the command's `<menu>` a–i and the agent's `<tasks>`/`<execution_plan>`/`<task_details>` (3,721 B) describe the same tasks and dependency graph; init.md never names the agent; only repo-index.md's `Not for` does.
- Fix: either init.md step 5 dispatches the agent (then the agent is the task SSOT and the command's `<task_outputs>`/`<dependency_graph>` go), or the agent's three task sections go and it keeps the per-task idempotency rules the command lacks. Smallest: the second.
- If we skip it: the menu gains task [i] (docs scaffold) that the agent's list does not know. −3,000 B.

**12. project-manager writes to a memory store nothing else reads** (agents/project-manager.md)
- What this is: `docs/memory/patterns/` and `docs/memory/mistakes/` appear in one file in the tree. /sc:save, /sc:load, /sc:insight, /sc:reflect and the RULES kernel use `.claude/memories/`, auto memory, `.claude/insights.jsonl`, `.claude/rules/gotchas/`.
- Fix: point the agent's Patterns/Mistakes outputs at `.claude/memories/learnings_<topic>.md` (what /sc:save writes) or `.claude/rules/gotchas/` (what the kernel proposes).
- If we skip it: lessons the agent records are never loaded by /sc:load. 0 B, split fix.

**13. /sc:roadmap writes plan's output path without plan's gate** (commands/roadmap.md, commands/plan.md)
- What this is: both write `docs/features/<slug>/05-plan.md` (roadmap takes `05<letter>-plan-workflow.md` when a plan exists); plan stops on a `status: draft` spec, roadmap does not; roadmap's `--strategy`/`--depth` text is byte-identical to brainstorm's.
- Fix: fold roadmap into plan as `--from <prd>` + `--granularity phase` (lost axes in Q3 table), or add the draft-spec stop to roadmap's Analyze step. Smallest: the latter (+120 B).
- If we skip it: a PRD-derived plan can be written from an unreviewed discovery doc. −2,500 B if folded.

### Nice to have

**14. Command `<role>` wrapper and `<bounds><does>` restate the description** (commands/*.md) — Q6 rows 1–3. Keep `<mission>` text only where it is not a prefix of the description (2 of 36); drop `<does>` lines that are noun lists of the flow; keep the `<never>` lines that carry a rule. −~5,000 B.

**15. MODE_Task_Management is a flag-only mode with a second task hierarchy** (modes/MODE_Task_Management.md) — `--task-manage` appears in no command or agent; FLAGS.md's one line already describes it; task.md carries Epic→Story→Task while the mode carries Plan→Phase→Task→Todo. Delete the mode, or make `/sc:task` trigger it and make the hierarchies agree. −2,388 B.

**16. MODE_Brainstorming is not loaded by /sc:brainstorm** (modes/MODE_Brainstorming.md, scripts/context_loader.py) — trigger is `--brainstorm|--bs` only, unlike research/business-panel/select-tool whose commands trigger their modes. Either add `/sc:brainstorm` to the trigger, or accept that brainstorm.md step 1 and its `<never>` already restate the mode and leave it flag-only. 0 B, consistency.

**17. Three copies of the `<finding_policy>` block** (agents/quality-engineer.md, security-engineer.md, self-review.md) — identical 3-sentence policy; belongs in RULES_QUALITY (already injected on `/sc:review|analyze|test`). −900 B.

**18. agent.md `<startup>`/`<token_discipline>`** (commands/agent.md) — status-line persona text ("Remind: 💡 Use /context"); `<token_discipline>` restates `--uc`. −700 B.

**19. `<tools>` sections naming native tools** (25 commands) — "Read: examine file content"; keep only the `Agent:` lines that say *which* agent and *what packet*. −~2,500 B.

**20. Commands' `<examples>` tables with one-word outputs** (e.g. business-panel: "`market-analysis.md --mode discussion --focus strategy` → Collaborative expert analysis"; sc.md: "`/sc:recommend` → Get suggestions") — 23,452 B across commands, of which the error-path `<example>` blocks carry the only decision content. Not measured line by line; flagged for 03e/03f cross-check.

---

## Verdict

The content tree is not bloated by many weak files; it is bloated by the same rule written into every file that might need it, because the delivery system co-loads almost nothing (command + rule module + sometimes mode) and the authors compensated by copying. The two declared trinities are real on the mindset/workflow axis but carry their domain tables 4–8 times; two undeclared pairs (git, init) are the same feature in two directories with no route between them; one command (`/sc:sc`) re-implements Claude Code's own dispatch. The loader has three undocumented trigger alternatives, one cross-domain misfire (`multi.?expert`), and a 72-token overrun that silently drops RULES_DOCS for the session.

**Lean: -52,000 bytes (~8 files) possible.** (sc.md, git-workflow.md, MODE_Orchestration.md, RESEARCH_CONFIG.md, MODE_Task_Management.md, and the three mcp/ bodies shrunk to their hints; the rest is section-level cuts across agents and commands. Of the 52 KB, ~14 KB is in-context bytes per delegated agent call — the two pasted paragraphs — and ~12 KB is the RULES/mode injection path; the remainder is on-disk only.)

## Not checked

- `skills/sc-author` and `skills/sc-prompt` bodies beyond the duplicate-sentence scan (3 verbatim shared sentences found, all source-citation lines) — user-invoked, out of the routing graph.
- `output-styles/`, `templates/docs-scaffold/` (4.8 KB, referenced by init task [i]).
- Whether Claude Code's agent-memory feature injects the instructions that finding 9 assumes (isolation rule: no docs lookup).
- Whether the `Workflow` tool, `EnterWorktree`, `SendMessage` named in MODE_Orchestration and RULES_DELEGATION exist in the current harness — if not, `<fan_out_execution>` and `<workflow_delegation>` are dead on arrival, which would move finding 6 to Must fix.
- `agents/README.md` (9,973 B), `commands/README.md`, `modes/README.md`, `core/README.md`, `mcp/README.md` — not installed; excluded from the lean count.
- Line-by-line quality of `<examples>` tables (finding 20) and of `<checklist>` vs `<actions>` overlap beyond the two quoted agents.
- Tests under `tests/unit/` that pin section presence (`test_command_structure.py`, `test_agent_structure.py`, `TestCoreLiteSplit`): several cuts above (role/bounds/tools sections, mode deletion, trigger removal) will need the corresponding structural test relaxed; not inspected.
