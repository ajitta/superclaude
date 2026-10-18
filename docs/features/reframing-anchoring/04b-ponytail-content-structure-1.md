---
feature: reframing-anchoring
phase: analysis
doc: 04b-ponytail-content-structure
status: draft
revised: 2026-10-17
---

# 04b — Ponytail lean criteria applied to the content structure (ADAPTATION)

> Split by size into 2 files (part 1 of 2): [part 2](./04b-ponytail-content-structure-2.md). Section boundaries and content unchanged.

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
