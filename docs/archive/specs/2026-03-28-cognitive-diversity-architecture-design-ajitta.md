# Cognitive Diversity Architecture (CDA) Design Specification

> **Status**: Research Archive (reclassified 2026-03-28)
> **Date**: 2026-03-28
> **Author**: ajitta
> **Origin**: Harness Engineering research synthesis (OpenAI, Anthropic, LangChain instantiations)
> **Philosophy**: Anthropic — "Harness = f(model limits)"
> **Related**: [Core Always-Loaded Analysis](../research/2026-03-28-core-always-loaded-harness-analysis-ajitta.md) | [Comprehensive Harness Research](../research/2026-03-28-harness-engineering-comprehensive-research-ajitta.md)
>
> **Reclassification Note**: This document was originally a design spec with implementation phases. After Socratic review, simplicity audit, and Anthropic source verification by three independent agents, it was reclassified as a Research Archive. Key findings:
> - The problem (agent bias reinforcement) is theoretical — no measured failures in SuperClaude's review pipeline
> - The proposed 3-phase architecture violates the project's own anti_over_engineering rules (RULES.md R06)
> - Anthropic's actual pattern (collaborative evaluator with sprint contracts) differs from the spec's interpretation (reasoning isolation)
> - The 80% solution is a 1-line mindset change to `self-review.md` — implemented separately
>
> **What was implemented instead**: Skeptical evaluator mindset (`self-review.md`) + challenge questions in `/sc:review` flow. Evidence-driven: measure first, build infrastructure only if needed.
>
> **This document retains value as**: Research synthesis on harness engineering, agent bias patterns, and evaluation architecture. Reference it when evidence of review quality problems emerges.

---

## 1. Problem Statement

### 1.1 Core Problem

SuperClaude's agents share the same model, the same core context (RULES.md, PRINCIPLES.md, FLAGS.md), and the same pipeline context. This creates **structural bias reinforcement** — agents converge on the same conclusions not because they're correct, but because they share identical blindspots.

### 1.2 Three Sub-Problems

| Problem | Cause | Effect |
|---------|-------|--------|
| **Shared Model Blindspots** | All agents = same Claude model = same training biases | Persona role-play produces shallow diversity, not genuine perspective differences |
| **Context Echo Chamber** | All agents read same core context (RULES, PRINCIPLES, FLAGS — ~500 lines always-loaded via CLAUDE_SC.md @import) | Same rules shape all agents' thinking identically, suppressing legitimate contrarian views. See [Core Analysis](../research/2026-03-28-core-always-loaded-harness-analysis-ajitta.md) |
| **Confirmation Cascade** | A→B→C pipeline where A's output feeds B's input | A's blindspots propagate through plan→implement→review unchallenged |

### 1.3 Evidence

- **Anthropic (2026)**: "Out of the box, Claude is a poor QA agent" — agents tend to "confidently praise the work, even when the quality is obviously mediocre." "Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work."
- **INDIBATOR (2026)**: Abstract personas < grounded individuality. Agents anchored in real research trajectories outperform prompt-based role-play.
- **Tool-MAD (2026)**: Heterogeneous evidence sources reduce shared blindspots. Homogeneous tools → overlapping content → limited argument diversity.
- **Cognitive Standardization (Sourati et al., 2026)**: LLMs "risk standardizing language and reasoning" — same AI tools → homogenized thinking patterns across users.
- **Heterogeneous Multi-Agent Debate (Heter-MAD, 2025; A-HMAD, 2025)**: Model heterogeneity improves debate quality by 6-8% — diverse evidence sources and perspectives outperform homogeneous configurations.

---

## 2. Design Principle

> **"Genuine diversity comes from information asymmetry, not persona role-play."**

Telling an agent "think like a security expert" is shallow diversity. Giving that agent different information, different tools, and different evaluation criteria produces genuine diversity — even when using the same underlying model.

### 2.1 Three Axes of Diversity

```
                    ┌──────────────────────┐
                    │   SAME MODEL (Claude) │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼──────────┐ ┌──▼──────────┐ ┌───▼────────────────┐
    │ Axis 1:            │ │ Axis 2:     │ │ Axis 3:            │
    │ INFORMATION        │ │ TOOL        │ │ EVALUATION         │
    │ ASYMMETRY          │ │ HETEROGENE- │ │ FRAME              │
    │                    │ │ ITY         │ │                    │
    │ What agents SEE    │ │ What agents │ │ How agents JUDGE   │
    │ differs            │ │ VERIFY with │ │ differs            │
    │                    │ │ differs     │ │                    │
    │ context: fork      │ │ Different   │ │ Multi-lens rubric  │
    │ Minimal handoff    │ │ MCP servers │ │ Independent scoring │
    │ No reasoning trail │ │ per role    │ │ per criterion      │
    └────────────────────┘ └─────────────┘ └────────────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  GENUINE DIVERSITY    │
                    │  despite same model   │
                    └──────────────────────┘
```

### 2.2 Anti-Principle: What This Is NOT

- NOT about using different models (Claude Code only supports Claude family)
- NOT about more elaborate persona prompts (research shows diminishing returns)
- NOT about adding debate rounds for every task (cost management matters)
- NOT about removing shared context entirely (some consistency is needed)

---

## 3. Architecture

### 3.0 Constitutional Layer Decision (Option C)

**Decision**: SuperClaude's `core/` always-loaded structure (FLAGS.md + PRINCIPLES.md + RULES.md, ~500 lines via CLAUDE_SC.md @import) remains **unchanged**. Both generator and evaluator agents load core/.

**What context: fork actually isolates:**

| Isolated by context: fork | NOT isolated (reloaded independently) |
|---|---|
| Generator's reasoning trail (why they chose an approach) | core/ (FLAGS, PRINCIPLES, RULES) — via CLAUDE.md @import |
| Conversation history (all prior turns) | .claude/rules/ (rescanned) |
| Previous tool call results | MCP server connections |
| Files the generator read | Tool definitions |

**Critical correction**: An earlier draft of this spec claimed evaluators would operate with "NO core context." This was incorrect. `context: fork` creates a subprocess in the same working directory, so CLAUDE.md → @import → core/ is **reloaded**. The evaluator has full access to FLAGS-based MCP routing, tool calling, and skill processing — this is necessary and correct.

**Process-Output Separation** — the actual mechanism:

```
GENERATOR:  core/ ✓ + conversation ✓ + reasoning ✓ + tool results ✓
                       ↓ artifacts only ↓
EVALUATOR:  core/ ✓ + artifacts only (criteria + diff + rubric)
            (NO conversation, NO reasoning trail, NO trial-and-error)
```

This aligns precisely with Anthropic's original pattern:
- *"Separating the agent doing the work from the agent judging it"*
- Evaluator sees the **output** (code diff, acceptance criteria), not the **process** (reasoning, alternatives considered)
- Both agents understand the framework rules (FLAGS/RULES) — ensuring MCP tools, skills, and tool calling work correctly
- The diversity comes from: different evidence (Axis 2), different evaluation frame (Axis 3), and no anchoring to generator's reasoning (Axis 1)

**Rationale** (evidence-driven, Anthropic-aligned):

1. **FLAGS must be available** to evaluator — MCP routing, tool calling, and skill processing depend on it
2. **Prompt caching preserved** — core/ cached after turn 1, cost ≈ 0
3. **"Guardrails that can be crowded out are suggestions, not invariants"** (Jeremy Daly) — core/ must stay always-loaded for all agents
4. **No measured evidence** that shared core/ rules cause evaluation homogenization (theoretical only)
5. **Reasoning isolation is sufficient** — Anthropic's research shows the key lever is separating the agent doing work from the one judging, not giving them different rules
6. **Residual echo chamber risk** from shared core/ rules is mitigated by Axis 2 (different tools → different evidence) and Axis 3 (5-lens rubric → different evaluation frames)

**Escalation to Option A (file split)** when ANY observed:
- Evaluator consistently produces identical assessments as generator despite CDA isolation
- Specific core/ rules demonstrably suppress valid criticisms in evaluator output
- Context compaction dropping core/ content in long sessions

See: [Full Core Always-Loaded Analysis](../research/2026-03-28-core-always-loaded-harness-analysis-ajitta.md)

### 3.1 Axis 1: Context Fork Protocol (Information Asymmetry)

**Mechanism**: Evaluator agents run in `context: fork` with minimal input — receiving only artifacts (code diff, acceptance criteria), not the generator's reasoning process.

**Why it works**: When a reviewer sees *why* the implementer made a choice, anchoring bias kicks in. The reasoning sounds plausible, so the reviewer agrees. When the reviewer sees only the *result*, they judge it independently.

**Current state**: SuperClaude's `context: fork` exists in skill infrastructure but is not used for bias reduction.

**Design**:

```
GENERATOR CONTEXT                    EVALUATOR CONTEXT (forked)
┌─────────────────────┐              ┌──────────────────────┐
│ Full conversation    │              │ Core (auto-reload):  │
│ Core context:        │              │  FLAGS.md  ✓         │
│  FLAGS.md            │   handoff    │  PRINCIPLES.md ✓     │
│  PRINCIPLES.md       │ ──────────> │  RULES.md  ✓         │
│  RULES.md            │  artifacts   │ Global rules ✓       │
│ MCP tools (Serena)   │    only      │ acceptance_criteria  │
│ Global + path rules  │              │ code diff (git diff) │
│ Reasoning history    │              │ evaluation_rubric    │
│ Trial-and-error      │              │ MCP tools (Playwright│
│ User conversation    │              │  + Tavily) ✓         │
│                      │              │                      │
│                      │              │ (NO reasoning trail) │
│                      │              │ (NO conversation)    │
│                      │              │ (NO trial-and-error) │
│                      │              │ (NO path-scoped rules│
└─────────────────────┘              └──────────────────────┘
Note: context: fork reloads CLAUDE.md @imports and global .claude/rules/
      but does NOT inherit path-specific scoped rules or conversation.
```

**Handoff protocol** (Option C — Process-Output Separation):
- Pass: `acceptance_criteria.md` + `git diff` (or file list) + `evaluation_rubric.md`
- Evaluator independently loads: core/ (via CLAUDE.md @import), its own MCP tools
- Do NOT pass: generator's reasoning, conversation history, trial-and-error
- Rationale: evaluator forms independent judgment without anchoring to generator's logic, while maintaining full access to framework rules and MCP/tool infrastructure

**Implementation path**:
- `/sc:review` enhanced with `--isolated` flag (or default for complex tasks)
- Evaluator runs as a skill with `context: fork` + `agent: quality-engineer`
- Handoff managed by orchestrator that strips reasoning and passes artifacts only

### 3.2 Axis 2: Tool Heterogeneity (Evidence Source Diversity)

**Mechanism**: Generator and Evaluator access different MCP servers, producing different evidence bases.

**Why it works**: Tool-MAD (2026) demonstrated that agents with heterogeneous evidence sources "explore distinct perspectives, reducing shared blind spots and producing more reliable conclusions." Homogeneous tool access → overlapping evidence → convergent conclusions.

**Design**:

| Role | MCP Tools | Purpose |
|------|-----------|---------|
| **Generator** | Serena, Context7 | Build: code structure understanding + official documentation |
| **Evaluator** | Playwright, Tavily | Break: live interaction testing + external failure case search |
| **Devil's Advocate** | Tavily, WebSearch | Challenge: external counter-evidence only |
| **Planner** | Sequential, Context7 | Reason: structured multi-step analysis + framework docs |

**Key insight from Anthropic**: *"The evaluator needs tools to actually interact with the output (navigate a UI, run tests, read files)"* — not the same tools used to create it.

**Adversarial search pattern**: When the Evaluator receives the implementation approach, it searches for counter-evidence:
```
Tavily query: "why [chosen approach] fails" OR "[approach] common pitfalls"
→ External failure cases injected into evaluation
→ Breaks echo chamber with information the Generator never saw
```

**Implementation path**:
- Update agent definitions: evaluator-role agents get `<mcp servers="play|tavily"/>` instead of `<mcp servers="serena|c7"/>`
- New `--adversarial` flag on `/sc:review`: triggers mandatory Tavily counter-evidence search
- Tool allocation documented in agent frontmatter comments explaining diversity rationale

### 3.3 Axis 3: Multi-Lens Evaluation (Evaluation Frame Diversity)

**Mechanism**: Instead of a single "is this good?" question, evaluation uses 5 independent lenses, each forcing a different cognitive frame.

**Why it works**: A single evaluation question activates the model's general preference (clean, readable, well-structured). Multiple orthogonal lenses force the model to examine different dimensions — some of which may contradict its general preference.

**The 5-Lens Rubric**:

| Lens | Question | Scoring | Bias Mitigation |
|------|----------|---------|-----------------|
| **Correctness** | Does each acceptance criterion pass? | Checklist (pass/fail per item) | Checklist removes subjectivity |
| **Security** | Any OWASP Top 10 applicable vulnerabilities? | Checklist (per OWASP category) | External framework overrides model preference |
| **Maintainability** | Can a junior dev unfamiliar with this codebase modify it in 3 years? | Score 0-5 with justification | Perspective shift forces different viewpoint |
| **AI Slop Detection** | Does this follow generic "AI-generated" patterns? | Score 0-3 (0=distinctive, 3=generic) | Meta-awareness of model's own tendencies |
| **Blindspot Scan** | What edge cases, user scenarios, or failure modes are missing? | List (quantity matters) | Negative question expands search space |

**Scoring rules**:
- Each lens scored independently — no aggregate score
- Fail on ANY lens → iteration required on that specific dimension
- Lens weights adjustable per task type (security-critical tasks weight Security higher)
- AI Slop lens inspired by Anthropic's evaluator rubric approach: weight criteria more heavily where the model consistently underperforms (e.g., originality, avoiding generic patterns)

**Implementation path**:
- Evaluation rubric template stored in `skills/` or `commands/` as reference
- `/sc:review` command updated to output per-lens scores
- `--focus` flag already exists — extend to map to rubric lens weighting

---

## 4. Pipeline Integration: Adversarial Checkpoints

### 4.1 The Cascade Problem

```
brainstorm → plan → implement → review
    A's blindspot propagates → → → → unchallenged at every stage
```

### 4.2 Checkpoint Architecture

Insert adversarial checkpoints between pipeline stages for complex tasks:

```
brainstorm
    ↓ [result]
    ├─────────────────────────────────────┐
    │ ADVERSARIAL CHECKPOINT              │
    │ (context: fork, Tavily only)        │
    │                                     │
    │ Input: brainstorm result only       │
    │ Task: "Find 3 reasons this          │
    │        direction could fail,        │
    │        with external evidence"      │
    │ Output: risk_assessment.md          │
    └─────────────────┬───────────────────┘
                      ↓
plan (receives: brainstorm result + risk_assessment)
    ↓ [plan.md + acceptance_criteria.md]
    │
implement (receives: plan + criteria)
    ↓ [code changes]
    ├─────────────────────────────────────┐
    │ SKEPTICAL REVIEW                    │
    │ (context: fork)                     │
    │                                     │
    │ Input: acceptance_criteria + diff   │
    │ Tools: Playwright + Tavily          │
    │ Frame: 5-lens rubric               │
    │ Output: evaluation.md (per-lens)   │
    └─────────────────┬───────────────────┘
                      ↓
    [pass] → done
    [fail on lens N] → iterate on dimension N only
```

### 4.3 Complexity Threshold

Not every task needs adversarial checkpoints. Cost management:

| Task Complexity | Checkpoint Level | Trigger |
|----------------|-----------------|---------|
| **Simple** (1 file, explicit path) | None | Direct edit, skip all checkpoints |
| **Medium** (feature addition, 3-10 files) | Skeptical Review only | `/sc:review` with 5-lens rubric |
| **Complex** (architecture, security, multi-system) | Full: Adversarial Checkpoint + Skeptical Review | `/sc:implement --thorough` or auto-detected |

Auto-detection heuristics for "complex":
- Touches >10 files
- Involves security, auth, payment, data migration keywords
- Architecture-level changes (new services, API contracts, database schemas)
- User explicitly requests `--thorough` or `--adversarial`

---

## 5. Comparison: Before and After

### 5.1 Current Flow (Bias Vulnerable)

```
User: "/sc:implement auth system"
→ system-architect plans
    (sees: full context, all rules, user conversation)
→ backend-architect implements
    (sees: architect's reasoning + all rules + conversation)
→ quality-engineer reviews
    (sees: architect's reasoning + implementer's reasoning + all rules)
→ quality-engineer: "LGTM, well-structured"
    (same blindspots shared, confirmation cascade complete)
```

### 5.2 CDA Flow (Bias Resistant)

```
User: "/sc:implement auth system --thorough"

[GENERATION]
→ system-architect plans (Serena + Context7)
  Output: plan.md + acceptance_criteria.md

[ADVERSARIAL CHECKPOINT] (context: fork, Tavily only)
  Input: plan.md (no architect reasoning)
  Action: Tavily "auth system common failure patterns 2025 2026"
  Output: risk_assessment.md (3 external failure cases with sources)

[IMPLEMENTATION]
→ backend-architect implements (plan + risk_assessment → risk-aware)
  Output: code changes (git diff)

[SKEPTICAL REVIEW] (context: fork, Playwright + Tavily)
  Input: acceptance_criteria.md + git diff (no implementer reasoning)
  Action:
    - Playwright: test actual auth flow end-to-end
    - Tavily: "why [chosen auth approach] fails"
    - 5-lens rubric: independent scoring
  Output: evaluation.md
    ├── Correctness: 4/5 criteria pass, 1 edge case missing
    ├── Security: OWASP A01 Broken Access Control — role check gap found
    ├── Maintainability: 4/5 — clear structure, needs 2 inline comments
    ├── AI Slop: 1/3 — distinctive approach, not generic template
    └── Blindspot: missing password reset flow, no rate limiting on login

[ITERATION]
→ backend-architect fixes Security + Blindspot items only
→ Re-review on those 2 lenses only (efficient)
```

---

## 6. Implementation Roadmap

> **Guiding principle**: core/ structure unchanged (Decision: Option C). All isolation happens at the CDA layer through `context: fork`.

### Phase 1: Quick Wins (1-2 days, content changes only)

| Item | Change | Files |
|------|--------|-------|
| **5-Lens Rubric** | Add evaluation rubric to /sc:review command | `commands/review.md` |
| **Evaluator Tool Reallocation** | Change evaluator agents' MCP allocation from build-tools to break-tools | `agents/self-review.md`, `agents/quality-engineer.md` |
| **Skeptical Default** | Strengthen evaluator agent mindset: "assume flaws exist until proven otherwise" | `agents/self-review.md` |
| **Adversarial Flag** | Add `--adversarial` flag documentation to /sc:review | `commands/review.md`, `core/FLAGS.md` |

**Explicit non-change**: core/ files (FLAGS.md, PRINCIPLES.md, RULES.md) are NOT modified in Phase 1.

### Phase 2: Process-Output Separation (3-5 days, infrastructure)

| Item | Change | Files |
|------|--------|-------|
| **Skeptical Review Skill** | Create skill with `context: fork` — evaluator runs with reasoning isolation (no generator process/conversation; core/ reloads independently) | `skills/skeptical-review/SKILL.md` |
| **Artifact Handoff** | Define protocol: pass acceptance_criteria + git diff + rubric as task prompt; generator's reasoning trail excluded by context: fork mechanism | Skill body + orchestration logic |
| **Adversarial Checkpoint** | Create checkpoint skill: `context: fork` + Tavily-only counter-evidence search | `skills/adversarial-checkpoint/SKILL.md` |
| **Complexity Threshold** | Auto-detect complex tasks (>10 files, security keywords, architecture scope) | `scripts/` or command logic |

**Key architectural point**: `context: fork` in Claude Code creates a subprocess that does NOT inherit the parent's conversation context (reasoning, history, tool results). However, the subprocess runs in the same working directory and **independently reloads** CLAUDE.md → @import → core/. This means:
- core/ (FLAGS, PRINCIPLES, RULES) are available → MCP routing, tool calling, skill processing work correctly
- Generator's reasoning trail is absent → evaluator judges output without anchoring bias
- The diversity mechanism is **Process-Output Separation**, not constitutional exclusion

### Phase 3: Grounded Individuality (1 week, content redesign)

| Item | Change | Files |
|------|--------|-------|
| **Agent Mindset Upgrade** | Move from abstract personas to grounded reference frames (INDIBATOR pattern) | All 22 agent .md files |
| **Pipeline VS** | Extend --vs to pipeline level (3 independent brainstorm runs) | `commands/brainstorm.md` |
| **Model Dependency Tagging** | Tag CDA components with `adaptive` (model-dependent) | New `MODEL_LIMITS.md` |
| **Escalation Monitoring** | Track evaluator/generator agreement rates to detect echo chamber | Observation, not code |

---

## 7. Model Dependency Analysis

Per Anthropic's philosophy: every harness intervention should declare its model limitation and removal condition.

| CDA Component | Model Limitation | Remove When | Tag |
|---------------|-----------------|-------------|-----|
| Process-Output Separation (context: fork) | Generator's reasoning anchors evaluator's judgment toward the same conclusion (anchoring bias) | Model performs robust independent evaluation even with full visibility into generator's reasoning | adaptive |
| Tool Heterogeneity | Same evidence → same conclusions | Model actively seeks disconfirming evidence without tool forcing | adaptive |
| 5-Lens Rubric | Single evaluation question → general preference convergence | Model spontaneously evaluates multiple orthogonal dimensions | adaptive |
| Adversarial Checkpoint | Pipeline stages inherit blindspots | Model metacognitively identifies and compensates for its own blindspots | adaptive |
| AI Slop Detection Lens | Model defaults to generic patterns | Model produces distinctive, non-generic outputs by default | adaptive |

**Overall model-dependency tag**: `adaptive`
**Review cadence**: Re-evaluate at each major model release (Opus 5, etc.)
**Expected trajectory**: Components should become simpler over time as models improve. If they don't, the limitation is deeper than assumed.

### 7.1 Core Context — Harness Component Classification

The always-loaded core/ serves as the harness's **Constitutional Layer**, mapping to three of seven universal harness components:

| Core File | Harness Component | Bitter Lesson Tag |
|-----------|------------------|-------------------|
| FLAGS.md (routing) | Repository Knowledge System | **adaptive** — models improving at auto-tool-selection |
| PRINCIPLES.md (philosophy) | Architecture Constraints | **durable** — meta-cognitive guidance, hardest to internalize |
| RULES.md (behavioral) | Architecture Constraints + Validation | **durable** — corrects model's fundamental over-engineering tendency |

**Option C implication**: All core/ components stay always-loaded for **both** generators and evaluators. The evaluator has full access to FLAGS-based MCP routing and RULES-based quality standards. The diversity mechanism is not core/ exclusion but **reasoning isolation** (evaluator doesn't see generator's thought process) combined with **tool heterogeneity** (different MCP tools) and **evaluation frame diversity** (5-lens rubric).

Full analysis: [Core Always-Loaded Harness Analysis](../research/2026-03-28-core-always-loaded-harness-analysis-ajitta.md)

---

## 8. Cost-Benefit Analysis

### 8.1 Costs

| Cost Type | Simple Task | Medium Task | Complex Task |
|-----------|-------------|-------------|--------------|
| Additional tokens (checkpoints) | 0 | +2K-5K (review) | +10K-20K (checkpoint + review) |
| Additional latency | 0 | +30-60s | +2-5min |
| Implementation effort | - | - | Phase 1: 1-2d, Phase 2: 3-5d |

### 8.2 Benefits

| Benefit | Mechanism | Evidence |
|---------|-----------|---------|
| Catch blindspots before production | External counter-evidence via Tavily | Tool-MAD: up to +35.5%p over standard MAD from heterogeneous tool sources |
| Reduce "LGTM" rubber-stamping | Context isolation prevents anchoring | Anthropic: "tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work" |
| Catch security issues | OWASP lens in rubric | Structured checklist > general review |
| Avoid "AI slop" | Dedicated detection lens | Anthropic: "weight criteria based on model capabilities" — penalize more heavily where model underperforms |
| Reduce iteration cycles | Per-lens feedback → targeted fixes | Fix only failed dimensions, not full rework |

### 8.3 ROI Threshold

CDA is justified when the cost of a missed blindspot exceeds the cost of the checkpoint:
- **Security features**: Always justify full CDA (cost of vulnerability >> checkpoint cost)
- **Architecture decisions**: Always justify (cost of wrong direction >> checkpoint cost)
- **Single-file bug fixes**: Never justify (low risk, high relative overhead)
- **Feature additions**: Judgment call — use `--thorough` flag when uncertain

---

## 9. Relation to Existing SuperClaude Patterns

| Existing Pattern | CDA Enhancement | Compatibility |
|-----------------|-----------------|---------------|
| `--vs` (Verbalized Sampling) | VS generates diversity within a single turn; CDA generates diversity across pipeline stages | Complementary — use VS within brainstorm, CDA across pipeline |
| `--validate` (Confidence Check) | Confidence check is self-assessment; CDA adds external assessment | CDA subsumes confidence-check for complex tasks |
| `/sc:review` command | Currently general review; CDA adds isolation + rubric + adversarial search | Direct enhancement — CDA is the next evolution of /sc:review |
| `context: fork` in skills | Currently used for execution isolation; CDA uses it for cognitive isolation | New use of existing mechanism |
| Agent `<mcp servers="">` | Currently for tool access; CDA uses it for evidence diversity | Reframing of existing pattern |
| Workflow gates (brainstorm→plan→implement→test) | CDA adds adversarial checkpoints between gates | Extension of existing flow |

---

## 10. Research References

| Source | Key Finding | Applied In |
|--------|------------|------------|
| Anthropic Harness Design (2026.03) | "Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work" | Axis 1: Context Fork |
| Anthropic Harness Design (2026.03) | "The evaluator needs tools to interact with the output" — Playwright MCP for live page testing | Axis 2: Tool Heterogeneity |
| Anthropic Harness Design (2026.03) | "Make subjective qualities gradable" + "Weight criteria based on model capabilities" | Axis 3: Multi-Lens Rubric |
| Tool-MAD (2026.01) | "Heterogeneous evidence sources reduce shared blind spots" | Axis 2: Tool Heterogeneity |
| INDIBATOR (2026.02) | Abstract personas < grounded individuality based on real trajectories | Phase 3: Agent Mindset Upgrade |
| Heter-MAD / A-HMAD (2025) | Model heterogeneity improves debate 6-8%; since Claude Code = single model family, diversify on tool/evidence/frame axes | Design constraint: same model, so diversify on other axes |
| Cognitive Standardization (Sourati et al., 2026) | Same AI tools → homogenized thinking patterns | Core motivation for CDA |
| Phil Schmid (2026.01) | "Model = CPU, Harness = OS" + Bitter Lesson warning | Model Dependency Analysis (Section 7) |

---

## 11. Open Questions

1. ~~**Context isolation granularity**: Should the evaluator see ANY core context (RULES.md), or should complete isolation produce better independent judgment?~~
   **RESOLVED (Option C)**: Evaluator runs in `context: fork` with **reasoning isolation** — generator's conversation history and thought process are excluded, but core/ (FLAGS, PRINCIPLES, RULES) reloads independently via CLAUDE.md @import. This preserves MCP/tool/skill functionality while preventing anchoring bias. Diversity is achieved through Process-Output Separation (Axis 1) + Tool Heterogeneity (Axis 2) + Multi-Lens Rubric (Axis 3).

2. **Adversarial checkpoint quality**: Does Tavily reliably find relevant failure cases for technical approaches? May need curated failure-case databases for common patterns.

3. **5-Lens rubric calibration**: How should lens weights be set for different task types? Initial weights should be equal; calibrate based on which lenses catch real issues.

4. **Pipeline VS cost**: Running brainstorm 3x independently triples cost. Is the diversity gain worth it? May be justified only for architecture-level decisions.

5. **Evaluator gaming**: If the evaluator rubric is static, could the generator learn to "game" the rubric? Rotate or evolve rubric criteria periodically.

6. **Process-Output Separation validation**: Does the evaluator produce genuinely different assessments when running with reasoning isolation (context: fork) but shared core/ rules? Need to compare CDA evaluator outputs vs standard /sc:review outputs on identical code. If divergence is low despite reasoning isolation, Axis 2 (tool heterogeneity) and Axis 3 (5-lens rubric) are carrying the diversity load — which may be sufficient.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **Anchoring Bias** | Cognitive bias where exposure to prior reasoning anchors subsequent judgment toward the same conclusion |
| **AI Slop** | Generic, template-like patterns that mark output as "obviously AI-generated" |
| **Confirmation Cascade** | Blindspot propagation through a pipeline where each stage inherits and reinforces previous stage's biases |
| **Context Fork** | Claude Code mechanism (`context: fork`) that runs a skill/agent in an isolated subprocess without parent conversation context |
| **Grounded Individuality** | INDIBATOR pattern: agents anchored in concrete reference frames rather than abstract persona descriptions |
| **Constitutional Layer** | Harness component providing always-loaded constraints — SuperClaude's core/ (FLAGS, PRINCIPLES, RULES). Loaded by all agents including evaluators. |
| **Information Asymmetry** | Deliberate difference in what each agent can access, forcing independent evidence gathering |
| **Option C** | Decision to keep core/ structure unchanged; solve bias through reasoning isolation (context: fork), tool heterogeneity, and multi-lens evaluation — NOT through core/ exclusion |
| **Priority Saturation** | Phenomenon where too many always-loaded instructions cause the model to deprioritize all of them equally |
| **Multi-Lens Evaluation** | CDA Axis 3: evaluation using 5 independent lenses (correctness, security, maintainability, AI slop, blindspot) instead of a single "is this good?" question |
| **Process-Output Separation** | CDA mechanism where evaluator sees the generator's output (artifacts) but not its process (reasoning, conversation, trial-and-error). Both share core/ rules. |
| **Skeptical Review** | CDA evaluation mode where the evaluator's default posture is "assume flaws exist until proven otherwise" |
| **Tool Heterogeneity** | CDA Axis 2: generator and evaluator access different MCP servers, producing different evidence bases |

## Appendix B: CDA Flag Reference

| Flag | Effect | Default |
|------|--------|---------|
| `--adversarial` | Enable Tavily counter-evidence search in review | Off |
| `--isolated` | Run review in context: fork with artifact-only handoff (Process-Output Separation) | Off (Phase 2: On for complex) |
| `--thorough` | Enable full CDA: adversarial checkpoint + isolated review + 5-lens rubric | Off |
| `--lens [name]` | Run only specific evaluation lens (correctness, security, maintainability, slop, blindspot) | All lenses |

## Appendix C: Decision Record — Option C

### Decision

**Option C: Status Quo + CDA Isolation** — core/ always-loaded structure unchanged; evaluator diversity achieved through `context: fork`.

### Options Considered

| Option | Description | Pros | Cons |
|--------|------------|------|------|
| **A: File Split** | Split FLAGS/RULES into CORE + REF, CLAUDE_SC.md imports CORE only | Structural resolution; reduced attention dilution | Over-engineering without evidence; breaks prompt caching; partial echo chamber remains |
| **B: Scoped Rules** | Keep core/, duplicate operational parts as .claude/rules/ scoped rules | Low effort; scoped loading | Duplication; maintenance burden; doesn't solve echo chamber |
| **C: Status Quo + CDA** ★ | No core/ changes; CDA evaluator uses context: fork for reasoning isolation | Zero structural risk; prompt caching preserved; MCP/tool/skill routing intact; reasoning isolation as sufficient lever | Residual echo chamber from shared core/ rules in non-CDA workflows |

### Why Option C

1. **FLAGS must be available**: MCP routing, tool calling, and skill processing depend on FLAGS.md — evaluator cannot function without it
2. **context: fork preserves core/**: Claude Code's fork mechanism reloads CLAUDE.md @imports independently — core/ exclusion is not technically feasible without separate working directory
3. **Reasoning isolation is the real lever**: Anthropic's research shows "separating the agent doing the work from the agent judging it" — not giving them different rules
4. **Three axes compensate for shared rules**: Tool heterogeneity (Axis 2) and multi-lens rubric (Axis 3) provide diversity even when core/ rules are shared
5. **Bitter Lesson**: don't restructure working infrastructure preemptively
6. **Reversible**: can escalate to Option A anytime if shared rules demonstrably suppress valid criticism

### Escalation Criteria (Move to Option A When...)

| Signal | Measurement | Threshold |
|--------|------------|-----------|
| Evaluator-generator convergence | Compare CDA evaluator outputs vs standard review outputs on same code | <20% divergence = shared rules suppress criticism |
| Specific rule interference | Evaluator consistently fails to criticize over-engineering due to shared anti_over_engineering | Qualitative pattern (3+ instances) |
| Context compaction loss | Monitor whether core/ content survives compaction in 50+ turn sessions | core/ content dropped in >30% of long sessions |

### Monitoring Plan

- Phase 2: Add logging to skeptical-review skill to capture evaluator output divergence
- Phase 3: Quarterly review of escalation signals
- Model releases: Re-evaluate entire CDA at each Claude major version
