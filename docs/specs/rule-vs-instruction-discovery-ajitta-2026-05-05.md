---
status: draft
revised: 2026-05-05
---

# Rule vs. Instruction — Authoring Guide Discovery

> Discovery spec exploring how SuperClaude authors should distinguish "rule" content (always-on behavioral invariants) from "instruction" content (task-triggered decision references) in the framework's content tree, and what authoring-meta-doc additions would help that distinction land consistently.

## 1. Origin

This discovery was triggered by a token-cost analysis of `src/superclaude/core/RULES.md` (commit `bc2a318`, 2026-05-05). The file is **174 lines / ~6.6K tokens**, of which:

- 35.7% is `<core_rules>` (R01–R20 rule definitions + 16-row examples table).
- ~28% is **decision-reference content** that fits a "task-triggered guidance" shape rather than a "behavioral invariant" shape: `<sub_agent_decision>` (10.7%), `<agent_routing>` (9.6%), `<doc_output_convention>` (7.7%).
- The remaining ~36% is examples tables, anti-pattern blocks, and smaller invariants.

RULES.md is part of the always-loaded `@superclaude/CLAUDE_SC.md` import chain (FLAGS 2.1K + PRINCIPLES 1K + RULES 6.5K = ~9.6K tokens injected on every conversation). The **observation that prompted this discovery**: not all of RULES.md needs to be always-loaded. Decision matrices and reference tables could ride the existing dynamic-injection mechanism (`TRIGGER_MAP` / `INSTRUCTION_MAP` in `src/superclaude/scripts/context_loader.py`) instead — but framework authors today have no written guidance on when to put behavioral content in the always-on chain vs. dynamic-injected reference files.

The output of this discovery is **authoring guidance**, not a refactor. Refactor planning is downstream.

## 2. Scope

In-scope:
- SuperClaude content tree under `src/superclaude/` (core, components, modes, mcp, scripts).
- The five `*-authoring.md` meta-docs in `.claude/rules/` plus `xml-prose-format.md`.
- Existing dynamic-injection mechanism: `TRIGGER_MAP`, `INSTRUCTION_MAP`, `TIER_0_MAP`, `COMPOSITE_FLAGS` in `context_loader.py`.

Out of scope:
- LLM-industry context-engineering theory (Karpathy, Anthropic public docs) — referenced only as background, not as deliverable.
- Refactor of RULES.md itself. That's a separate `/sc:plan` cycle that would consume this spec as input.
- Per-component body re-authoring. The authoring guide gives criteria; applying them to existing components is downstream.
- Hooks and other CC-native injection paths (system-reminders, PreToolUse) — they share the same conceptual axis but live outside the framework content tree.

## 3. Resolved Decisions

Captured from brainstorm dialogue 2026-05-05 §3:

| Q | Decision | Mode | Rationale |
|---|---|---|---|
| Q1: Origin of question | **1a — Diagnostic motivation, anchored in RULES.md 6.6K analysis** | confirmed | User typed literal option letter `1a`. |
| Q2: Output form | **2b — Authoring guide additions to `.claude/rules/*-authoring.md`** | confirmed | User typed literal option letter `2b`. |
| Q3: Scope | **3a — SuperClaude framework only** | confirmed | User typed literal option letter `3a`. |

All three decisions are `confirmed` mode. No delegated decisions present, so the `/sc:review` handoff in §10 carries no audit-mandate.

## 4. Question Framing

The practical question framework authors face today: **"I have a piece of behavioral content. Where does it go?"**

Today's choices, implicit and undocumented:
1. `core/RULES.md` (always-on, hand-curated, ~6.6K).
2. `core/FLAGS.md` / `core/PRINCIPLES.md` (always-on, role-specific).
3. `core/<DOMAIN>.md` (e.g., `BUSINESS_SYMBOLS.md`) — dynamic-loaded via `TRIGGER_MAP`.
4. Per-component XML body (`commands/*.md`, `agents/*.md`, `modes/*.md`, `skills/*/SKILL.md`, `mcp/*.md`).
5. Per-component examples / gotchas section (within the body).

Without authoring guidance, the historical drift has been: **everything that "feels framework-wide" lands in RULES.md**, even when it's a decision matrix that only fires for a specific verb (`<sub_agent_decision>` only matters when delegating; `<doc_output_convention>` only matters when running `/sc:plan`/`/sc:design`/`/sc:brainstorm`). This bloats the always-on cost without buying always-on benefit.

The discovery output: a **content classification** that distinguishes rule from instruction, plus a **decision tree** authors can apply, plus **anti-pattern examples** to make the distinction stick.

## 5. Working Taxonomy — 4 Axes

The brainstorm proposed 6 axes (Lifetime, Voice, Authority, Source, Compaction, Conflict). Convergence drops two as **derived** rather than independent: Compaction priority follows from Lifetime (always-on content survives compaction by placement); Conflict resolution follows from Authority (the priority hierarchy is itself a rule-shape).

The four load-bearing axes:

### Voice
- **Rule:** declarative, third-person, behavioral. *"Claude does X."* / *"Never Y."*
- **Instruction:** imperative or reference-shaped. *"When delegating, choose agent by … "* / *"Output to `docs/<type>/…`"*

This is the surface form. Opus 4.7 reads declarative voice as load-bearing and drops hedging. Reference-shaped tables are not load-bearing on their own — they're consulted when the relevant verb appears.

### Lifetime
- **Rule:** every conversation, every turn. Has no opt-out.
- **Instruction:** triggered by verb / scope / context. Safe to omit when the trigger doesn't fire.

A clean test: *"If a user has a 30-turn debugging session that never invokes /sc:brainstorm, is omitting this content harmful?"* If yes → rule. If no → instruction.

### Authority
- **Rule:** constrains the action space. Defines invariants that hold regardless of what the agent is trying to do.
- **Instruction:** directs a specific action within an already-bounded space. Tells the agent *how* to do something, not *whether* it's allowed.

R10 ("root cause analysis, always test") is rule-shaped — it constrains every implementation. The agent-routing matrix is instruction-shaped — it directs choice *within* the already-decided action of "delegate to a sub-agent".

### Source
- **Rule:** committed framework code under `src/superclaude/core/` + `src/superclaude/CLAUDE_SC.md` import chain. Authored by framework maintainers; never injected dynamically.
- **Instruction:** lives in dynamically-loaded reference files (`mcp/`, `modes/`, `core/BUSINESS_SYMBOLS.md`), per-component bodies, or hooks. May be authored by component authors, not just framework maintainers.

Source is the **operational** axis — it tells the author which file to write to. The other three axes determine the *kind* of content; Source determines the *location*.

## 6. Existing Mechanism (what's already there)

The framework already has the plumbing for instruction-shaped content. `src/superclaude/scripts/context_loader.py` defines a 3-tier injection model triggered by regex patterns over the user prompt:

| Tier | Mechanism | Token cost | Used for |
|---|---|---|---|
| Tier 0 | 1-line summary in `TIER_0_MAP` | ~10–25 tokens | Tool MCPs (Context7, Sequential, Playwright, DevTools), supplementary references |
| Tier 1 | Multi-paragraph instruction in `INSTRUCTION_MAP` | ~150–250 tokens | Behavioral MCPs (Serena, Tavily) — workflow patterns, decision rules |
| Tier 2 | Full `.md` body | ~500–2000 tokens | Modes (Brainstorming, Token-Efficiency, etc.) and behavioral MCPs needing pattern fidelity |

Plus `COMPOSITE_FLAGS` (`--frontend-verify`, `--all-mcp`) for one-shot multi-file injection.

What's missing: **core/ files other than `BUSINESS_SYMBOLS.md` are not in `TRIGGER_MAP`.** `RULES.md`/`FLAGS.md`/`PRINCIPLES.md` are statically `@`-imported via `CLAUDE_SC.md` and never tier-tagged. Decision-reference content that lives inside RULES.md today has no mechanism to ride Tier 0/1/2 even though shape-wise it fits.

## 7. Authoring Decision Tree

The proposed test for "where does this content go?" — written from the author's point of view:

1. **Is the content always-true behavioral invariant?** *(Voice: declarative; Lifetime: every conversation; Authority: constrains action space.)*
   - Yes → `core/RULES.md` (or `FLAGS.md`/`PRINCIPLES.md` by domain).
   - No → continue.

2. **Is it task-triggered decision reference?** *(Voice: reference / matrix; Lifetime: only when verb fires; Authority: directs choice within bounded action.)*
   - Used framework-wide across multiple components → `core/<DOMAIN>.md` + add a `TRIGGER_MAP` entry. Pick a tier:
     - Single-line lookup, no workflow → Tier 0.
     - Multi-paragraph workflow with decision rules → Tier 1.
     - Full body needed for pattern fidelity → Tier 2.
   - Used by exactly one component → keep in that component's XML body under appropriate section tag (`<flow>`, `<patterns>`, `<focus_agent_mapping>`, etc.).

3. **Is it ephemeral / per-turn?** (User message, hook injection, system-reminder.) → Outside the framework content tree. Not an authoring concern for SuperClaude.

A piece of content can fail step 1 and step 2 in different ways. Tag-level signal:

| Tag shape | Likely category | Default location |
|---|---|---|
| `<core_rules>` numbered list (R-rules) | Rule | `core/RULES.md` |
| `<priority_system>` / `<thresholds>` | Rule | `core/RULES.md` |
| Decision matrix with verb-keyed rows (e.g., `<agent_routing>`, `<sub_agent_decision>`) | Instruction | Dynamic-loaded core file (Tier 1 or 2) |
| Output-format / directory mapping | Instruction | Dynamic-loaded core file (Tier 0 or 1) keyed on the relevant verb |
| Examples table (`<examples>`) attached to a rule | Rule-adjacent — moves with its parent | Same file as the rule |
| Per-component flow / patterns / tools | Instruction (component-scoped) | Component XML body |

## 8. Mixed-Content Audit — RULES.md Offenders

Concrete instances in current `core/RULES.md` where rule and instruction content live together:

- **`<sub_agent_decision>` (lines 13–30, ~600 tokens).** Mixed: the *trigger heuristics* ("3+ independent parallel streams", "<3 steps") are rule-shaped — they constrain when sub-agents are appropriate. The *7-row examples matrix* is instruction-shaped reference. Verb trigger: any sub-agent-spawning intent (`--delegate`, `--p`, "audit", "research X + Y + Z"). Candidate split: keep a 2-line invariant in RULES (Direct vs Sub-agent vs Never), move the matrix to `core/AGENT_ROUTING.md` Tier 1.
- **`<agent_routing>` (lines 32–44, ~550 tokens).** Pure instruction-shape. Verb trigger: same as above, plus single-trigger ambiguity verbs (`optimize`, `refactor`, `test`, `teach`, `research`, `docs`). Should not be always-loaded. Candidate: same `core/AGENT_ROUTING.md` Tier 1 or 2.
- **`<doc_output_convention>` (lines 146–158, ~510 tokens).** Pure instruction-shape (directory/suffix/status mappings). Verb trigger: file-producing commands (`/sc:brainstorm`, `/sc:design`, `/sc:plan`, `/sc:workflow`, `/sc:analyze`, `/sc:research`, `/sc:document`). Should not be always-loaded. Candidate: `core/DOC_CONVENTIONS.md` Tier 1.
- **`<core_rules>` examples table (lines 64–83, ~990 tokens).** Rule-adjacent. Stays with R01–R20 by default. Could be split to a sibling `core/RULES_EXAMPLES.md` Tier 0/1 if the always-on rules block needs to slim, but this is lower priority — examples augment rules at the moment of disambiguation, and the 16 rows aggregate across all 20 rules so partial inject is awkward.
- **`<anti_over_engineering>` (lines 91–109, ~620 tokens).** Mixed: the prose rules ("Bug fix ≠ cleanup", "Earned > Premature") are rule-shaped; the 5-row examples table is rule-adjacent; the `<model_tendencies>` block is rule-shaped (describes invariant model behavior). Stays in RULES.

Estimated extraction (if downstream `/sc:plan` adopts the splits): ~1,660 tokens off the always-on chain (-25% of RULES.md). This is a **bound for the authoring-guide outcome**, not a commitment.

## 9. Proposed Authoring Guide Additions

The output of this discovery is content for two existing meta-docs, not new files. (One-file-per-concept hygiene; a separate `rule-vs-instruction.md` would orphan the topic.)

### 9.1 New section in `xml-prose-format.md`

Title: **Rule vs. Instruction Content**. Placement: after "Section Ordering" and before "Root Structure" — it's a content-classification rule, peer to other body-format rules.

Content (proposed shape, draft for design phase):
- The 4 axes from §5 as a compact table.
- The decision tree from §7 as numbered prose (1./2./3.).
- The tag-shape lookup from §7 as a table.
- One short example block: "Where does this content go?" walking a hypothetical author through `<sub_agent_decision>` and showing the rule-portion-stays / matrix-extracts split.

Estimated added size: ~80–110 lines / ~3K tokens. xml-prose-format.md is currently ~6.6K tokens; this would push it to ~9.5K. That's within the spec's own size guidance for non-component meta-docs (which are uncapped — the size targets in xml-prose-format apply to components, not the meta-doc itself).

### 9.2 Cross-reference block in each `*-authoring.md`

The five per-type meta-docs (`agent-`, `command-`, `mode-`, `skill-`, `mcp-authoring.md`) already inherit from `xml-prose-format.md` via an "Inherited from xml-prose-format.md" section. The discovery extends that inheritance with a one-line pointer:

> Rule vs. Instruction content classification — see xml-prose-format.md §"Rule vs. Instruction Content". When authoring a `<…>` section, decide whether its content is always-on rule shape or task-triggered instruction shape; instruction-shape content belongs in a dynamic-loaded core file or a per-component body, not in `core/RULES.md`.

Per-component authoring docs already echo cross-cutting xml-prose rules; this is the same pattern.

### 9.3 What this guide does NOT prescribe

- **No specific TRIGGER_MAP entries.** Authors propose, framework maintainers gate-keep new entries (`TRIGGER_MAP` is opinionated infrastructure).
- **No threshold for "framework-wide vs single-component"**. The decision is qualitative; the tree gives signal but doesn't force a numeric cutoff.
- **No retro-active enforcement.** Existing components and core files are not in violation. The guide is forward-looking; refactor of mixed content is a separate planning cycle.

## 10. Handoff

This spec must pass `/sc:review` before progressing to `/sc:plan` (per `/sc:brainstorm` flow step 5b — hard gate, not advisory).

**Run `/sc:review` on this spec before `/sc:plan`. Plan handoff is gated on review.**

(All decisions in §3 are `confirmed` mode; no audit-mandate phrase required.)

After review iteration logs are appended in §11 and status is bumped to `approved-for-plan`, the planning cycle should target:
- Drafting the `xml-prose-format.md` §"Rule vs. Instruction Content" section as concrete prose.
- Drafting the cross-reference block for each `*-authoring.md` (5 files).
- Adding tests if the structural test suite (`tests/structural/`) should validate that core/* files don't ship instruction-shape content (out-of-scope question for the planning phase, not committed here).

A *separate* downstream plan would consume this guide as input to refactor RULES.md (the §8 audit). That plan is **not** part of this discovery; it should be initiated only if/when this guide ships and proves useful.

## 11. Self-Review Iteration Log

*To be filled by `/sc:review`.*

| Round | Date | Reviewer | Summary | Resolved |
|---|---|---|---|---|
| _v1 baseline_ | 2026-05-05 | author | initial draft from brainstorm | n/a |

## 12. Non-Goals & Open Questions for Design Phase

Open questions deferred to `/sc:plan` (do not resolve here):

1. **Should `xml-prose-format.md` itself remain plain Markdown** (its current form, per its own §Scope note), or should the new §"Rule vs. Instruction" section adopt the XML body format it documents? The meta-doc is not a SuperClaude component, so plain Markdown is acceptable; consistency with the rest of the file is the simpler choice.
2. **Tier-0 vs Tier-1 cutoff for new core/* extractions** — `core/AGENT_ROUTING.md` could be Tier 1 (instruction-paragraph) or Tier 2 (full body); the answer depends on whether the 7-row matrix is faithfully representable in ~200 tokens. Belongs to the downstream refactor plan, not this guide.
3. **Should the structural test suite enforce the rule/instruction classification?** E.g., a test that flags decision-matrix tables in always-loaded core/* files. Surface as a candidate test in the design phase; not committed.
4. **Naming.** Is "Rule vs. Instruction" the best label, or does "Invariant vs. Reference" carry the distinction with less ambiguity? Voice-test (declarative vs imperative) suggests the rule/instruction split tracks Anthropic's own system-vs-user prompt convention better; reviewer call.
