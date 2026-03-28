# Core Always-Loaded Context: Harness Engineering Analysis

> **Date**: 2026-03-28
> **Author**: ajitta
> **Scope**: Relationship between SuperClaude's core/ always-loaded mechanism and harness engineering patterns
> **Sources**: Harness research synthesis, Martin Fowler/Böckeler, Anthropic official, HumanLayer, Morphllm, Jeremy Daly, HN discussions, OpenHands SDK, AgentSkills spec

---

## 1. Mechanism Under Analysis

SuperClaude's `CLAUDE_SC.md` imports three files at every session start:

```
@core/FLAGS.md       (~93 lines)  ← Routing table + flag system
@core/PRINCIPLES.md  (~49 lines)  ← Engineering philosophy + decisions
@core/RULES.md       (~68 lines)  ← Operational rules R01-R17 + anti-over-engineering
                     ───────────
                     ~210 lines raw (~500 lines with XML)
```

This content is injected into every session, every agent, and every sub-agent via Claude Code's CLAUDE.md → @import chain. Architecture taxonomy calls this "Framework DNA" / "Constitution" with "Always loaded" delivery.

---

## 2. Harness Component Mapping

### 2.1 Per-File Mapping

| Core File | Harness Component(s) | Role Analogy |
|-----------|---------------------|--------------|
| **FLAGS.md** | Repository Knowledge System + Middleware Architecture | OpenAI's AGENTS.md INDEX — "what exists and when to use it" |
| **PRINCIPLES.md** | Architecture Constraints | Decision-making constitution — "how to judge" |
| **RULES.md** | Architecture Constraints + Validation & Guardrails | Behavioral rules + quality gates — "what to enforce" |

### 2.2 Combined Role

core/ always-loaded = **Constitutional Layer** of the harness, spanning 3 of 7 universal components:
1. Architecture Constraints (PRINCIPLES + RULES)
2. Repository Knowledge System (FLAGS — index/routing)
3. Validation & Guardrails (RULES — R01-R17)

This is the component rated "most model-independent and durable" across all three instantiations.

---

## 3. Industry Context Loading Patterns

Three patterns identified across all harness frameworks:

| Pattern | Mechanism | Examples | Token Cost |
|---------|-----------|----------|------------|
| **Always-loaded** | Permanent context at session start | CLAUDE.md, AGENTS.md, system prompt | ~50-5000 tokens, cached after turn 1 |
| **Trigger-loaded** | On-demand by keyword/file scope | Skills, scoped rules, context_loader | Variable, per-activation |
| **Progressive disclosure** | Name+description at startup, body on invocation | SKILL.md frontmatter → body → references/ | ~50 tokens at startup, full on need |

SuperClaude core/ = Pattern 1. Industry-wide most common AND most debated pattern.

### 3.1 Key Industry Findings

| Source | Finding |
|--------|---------|
| Martin Fowler/Böckeler (2026) | "CLAUDE.md: always loaded. For most frequently repeated general conventions." |
| HumanLayer (2025) | "CLAUDE.md goes into every session. Highest leverage point of the harness — for better or worse." |
| codewithmukesh (2026) | "System prompt cached after first turn, essentially free for subsequent turns." Keep CLAUDE.md under 200 lines. |
| Rick Hightower (2026) | "When everything is high priority, nothing is. Priority saturation." |
| Anthropic official (2026) | "Strive for the minimal set of information that fully outlines expected behavior." |
| Morphllm (2026) | "More tokens makes agents worse" — context pollution reduces performance. |
| Jeremy Daly (2026) | "What you exclude from context is becoming as important as what you include." "If guardrails can be crowded out, they are suggestions, not invariants." |
| HN discussion (2026) | "Items loaded at just the right time... attention layer does a better job during that part of the task." But: "Progressive disclosure reduces benefit of token caching. Might be a toss-up." |
| OpenHands SDK | Explicit 3-tier: always-loaded / trigger-loaded / progressive disclosure |

---

## 4. Three-Instantiation Comparison

### 4.1 Always-Loaded Strategies

| | OpenAI | Anthropic | LangChain | **SuperClaude** |
|---|---|---|---|---|
| Always-loaded | ~100-line INDEX | Minimal essential set | Middleware routing info | **~500 lines (FLAGS+PRINCIPLES+RULES)** |
| Detail layer | docs/ (reference) | Sprint contract (per-task) | Skill body (on-activation) | modes/ + mcp/ (context_loader) |
| Principle | Index only, reference on-demand | Minimal but complete | Routing only, execution on-demand | Constitution + operational mixed |

### 4.2 Per-Instantiation Analysis

**OpenAI lens (Progressive Disclosure)**:
- FLAGS.md = INDEX ✓ (routing table — what tools/modes exist)
- PRINCIPLES.md = acceptable ✓ (compact, universally applicable)
- RULES.md = mixed — core rules (R01-R07) are universal, but selection_protocol, doc_output_convention are situational
- Verdict: Split RULES into "core rules" (always) vs "operational guides" (on-demand)

**Anthropic lens (Model Limits)**:
- FLAGS.md routing: compensates for model's inability to auto-select tools → **adaptive** (models improving)
- RULES behavioral correction (YAGNI, scope): compensates for model's over-engineering tendency → **durable** (fundamental tendency)
- PRINCIPLES philosophy: meta-cognitive guidance → **durable** (hardest for models to internalize)
- Verdict: Durable content stays always-loaded; adaptive content can become on-demand

**LangChain lens (Middleware)**:
- FLAGS.md = routing middleware → always-active ✓
- PRINCIPLES.md = filter middleware → always-active ✓
- RULES.md = mixed middleware — R01-R10 always-active, selection_protocol/doc_convention conditional
- Verdict: Separate always-active from conditional middleware

**All three lenses converge**: core/ mixes "invariant constraints" with "operational guidelines." The former must be always-loaded; the latter could be on-demand.

---

## 5. Benefits-Costs Analysis

### 5.1 Benefits (Why Always-Load Is Correct)

| Benefit | Harness Principle | Evidence |
|---------|------------------|----------|
| **Behavioral Consistency** | "Guardrails that can be crowded out are suggestions, not invariants" (Daly) | Rules not loaded = rules not followed |
| **Prompt Caching** | Cached after turn 1, cost ≈ 0 (codewithmukesh) | Dynamic loading causes cache misses |
| **Identity Preservation** | "Golden principles embedded in repo" (OpenAI) | core/ without = SuperClaude without |
| **Sub-agent Inheritance** | Parent CLAUDE.md inherited by sub-agents | Consistent harness across delegation chain |
| **Entropy Prevention** | Prevents behavioral drift across sessions | Always-loaded = entropy management frontline |

### 5.2 Costs (Why Always-Load Has Risks)

| Cost | Harness Principle | Evidence |
|------|------------------|----------|
| **Context Echo Chamber** | Same instructions → homogenized thinking (CDA analysis) | All agents read same rules → same blindspots |
| **Priority Saturation** | "When everything is high priority, nothing is" (Hightower) | ~500 lines all "always apply" → which to prioritize? |
| **Attention Dilution** | "Items loaded at right time get better attention" (HN) | Irrelevant rules dilute attention on relevant ones |
| **Rigidity** | Cannot temporarily disable rules per-task | anti_over_engineering may suppress creativity in brainstorming |

### 5.3 Key Tension

> **"Always-load ensures guardrails are invariants"** vs **"Always-load creates echo chamber + attention dilution"**

Not a false dichotomy — both are real. Resolution requires layered design, not binary choice.

---

## 6. Proposed: Layered Constitutional Model

Three layers separating invariant constraints from operational guidelines:

```
Layer 1: INVARIANTS (~100-150 lines, always loaded)
  "Without this, it's not SuperClaude"
  ├── R01-R06, R13, R15 (core workflow rules)
  ├── anti_over_engineering core principle (no detailed examples)
  ├── PRINCIPLES core (Task-First, Evidence-Based, Restraint-First)
  └── FLAGS routing core (modes/MCP/execution flag list)

Layer 2: DEFAULTS (~200 lines, loaded by default, overridable)
  "Needed in most sessions, can be contextually deactivated"
  ├── R07-R12, R14, R16, R17
  ├── selection_protocol, doc_output_convention
  ├── anti_over_engineering detailed examples/tables
  └── FLAGS aliases, persona_index, mcp_auto_mode

Layer 3: SITUATIONAL (~150 lines, on-demand only)
  "Relevant only in specific tasks/modes"
  ├── workflow_gates detail (plan/implement transitions)
  ├── dynamic_context meta-description (debugging)
  ├── BUSINESS_SYMBOLS (already on-demand ✓)
  └── FLAGS detailed priority rules
```

### 6.1 How This Resolves Each Tension

| Tension | Resolution |
|---------|-----------|
| Guardrails = invariants | Layer 1 always loaded → core rules never absent |
| Echo chamber | CDA evaluator gets Layer 1 only → minimal sharing, max independence |
| Attention dilution | Task-irrelevant Layer 2/3 inactive → attention focused |
| Prompt caching | Layer 1 cached → cost optimization maintained |
| Rigidity | Layer 2 overridable → brainstorming can relax anti_over_engineering |

---

## 7. Bitter Lesson Classification

| Core Content | Model Dependency | Rationale |
|-------------|-----------------|-----------|
| FLAGS routing (which tool when) | **adaptive** | Models improving at auto-tool-selection |
| RULES behavioral correction (YAGNI, scope) | **durable** | Model's over-engineering tendency is fundamental (training data bias) |
| PRINCIPLES philosophy | **durable** | Meta-cognitive level — hardest for models to internalize |
| selection_protocol, doc_convention | **adaptive** | Format rules — unnecessary when model learns user preferences |

---

## 8. Decision: Option C (Status Quo + CDA Isolation)

### 8.1 Three Options Evaluated

| Option | Effort | Anthropic Alignment | Description |
|--------|--------|-------------------|-------------|
| **A: File Split** | Medium | High | Physically split FLAGS/RULES into CORE + REF, CLAUDE_SC.md imports CORE only |
| **B: Scoped Rules** | Low | Medium | Keep core/, duplicate operational parts as .claude/rules/ scoped rules |
| **C: Status Quo + CDA** | Minimal | **High** | No core/ changes; CDA evaluator uses context: fork to exclude core/ |

### 8.2 Why Option C

1. **No measured evidence** of echo chamber or priority saturation (theoretical derivation only)
2. **Bitter Lesson compliance**: don't restructure what's working without empirical evidence of a problem
3. **CDA's context: fork** already solves evaluator isolation — the biggest echo chamber risk
4. **Prompt caching preserved** — no architectural disruption
5. **Upgrade path clear**: if real problems observed → Option A (evidence-driven)

### 8.3 Escalation Criteria to Option A

Move to Option A (file split) when ANY of these are observed:
- [ ] Rules consistently ignored in specific task types (measurable adherence drop)
- [ ] Evaluator agents producing identical assessments as generators despite CDA isolation
- [ ] Context compaction dropping core/ content in long sessions
- [ ] User feedback that specific rules interfere with specific tasks

---

## 9. Relationship to CDA

The core/ always-loaded pattern directly connects to the Cognitive Diversity Architecture:

```
GENERATOR agent: Full core/ (Layer 1 + 2 + 3)
  → All rules applied, consistent behavior

EVALUATOR agent: context: fork (Layer 1 only, or none)
  → anti_over_engineering absent → bold criticism possible
  → selection_protocol absent → free-form evaluation
  → doc_convention absent → result-focused judgment
  → Independent judgment from different information base
```

This is the concrete implementation of CDA's Axis 1 (Information Asymmetry): evaluator and generator operate under different constitutional context, producing genuine cognitive diversity despite the same underlying model.

---

## 10. References

| Source | Key Finding | Applied To |
|--------|-------------|-----------|
| Martin Fowler/Böckeler (2026) | Always-loaded for universal conventions | Validates core/ as always-loaded |
| Jeremy Daly (2026) | "Guardrails crowded out = suggestions" | Justifies always-load for invariants |
| Jeremy Daly (2026) | "Exclusion as important as inclusion" | Justifies layered model |
| Rick Hightower (2026) | Priority saturation in large CLAUDE.md | Identifies risk in current ~500 lines |
| codewithmukesh (2026) | Prompt caching nullifies cost argument | Resolves token budget concern |
| HN discussion (2026) | On-demand gets better attention weight | Supports situational offloading |
| Anthropic official (2026) | "Minimal set that fully outlines behavior" | Validates Layer 1 concept |
| OpenHands SDK (2026) | Explicit 3-tier loading model | Validates layered architecture |
| Morphllm (2026) | "More tokens makes agents worse" | Warns against context pollution |
| AgentSkills spec (2026) | Progressive disclosure standard | Industry-standard loading pattern |
