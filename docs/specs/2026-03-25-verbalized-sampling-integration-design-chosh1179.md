# Verbalized Sampling Integration into SuperClaude

**Date**: 2026-03-25
**Author**: chosh1179
**Status**: Implemented — all tasks complete (2 commits: d062d5f, 1904ee3)
**Renamed from**: `verbalized-sampling-enhanced` (original) → `verbalized-sampling` (shorter, aligns with SuperClaude naming)
**Source**: Zhang et al. (2025) "Verbalized Sampling" (arXiv:2510.01171, ICLR 2026)

---

## Summary

Integrate the Verbalized Sampling Enhanced skill into SuperClaude as a **Reference Skill** with **`--vs` flag integration** into `/sc:brainstorm`. VS is a research-backed prompting method that defeats mode collapse by shifting from instance-level to distribution-level prompts, generating k diverse responses with probability distributions.

## Design Decisions (Confirmed)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Content type | **Skill** (Reference archetype) | Auto-triggers on keywords; supports references/ subdirectory; no CC-native hooks needed |
| Scope | **General-purpose + SE examples** | Preserves original protocol; adds architecture/code-review/debugging examples |
| Brainstorm integration | **`--vs` flag on /sc:brainstorm** | VS becomes an optional brainstorm mode; activates distribution-level exploration |
| Adaptation depth | **Full SuperClaude adaptation** | XML `<component>` wrapper; skill-authoring.md compliance; test coverage |
| Language | **English-based** | Remove bilingual labels; keep English-only structural format |

---

## Parameter Handling Design

### Dual Input Paths

VS parameters can arrive through two distinct paths:

**Path 1: Slash command flag + bracket params** (explicit invocation)
```
/sc:brainstorm "topic" --vs cot [k:7, tau:0.05]
any prompt --vs                          # auto-detect variant, default params
any prompt --vs multi [k:5, turns:4]     # explicit variant + bracket params
```

**Path 2: Natural language + bracket syntax** (auto-trigger)
```
"show me multiple perspectives on API design [k:5, tau:0.01]"
"explore options for auth [vs-cot]"
"brainstorm alternatives, be wild about it"    # NL hint → tau=0.01
```

### Flag Design

Following SuperClaude flag conventions (`--flag [value]`):

| Flag | Type | Range | Default | Scope |
|------|------|-------|---------|-------|
| `--vs [standard\|cot\|multi]` | enum (optional value) | standard, cot, multi | auto-detect | FLAGS.md `<execution>` |

VS sub-parameters use **bracket syntax only** (not `--flag` form) to avoid polluting global flag namespace:

| Bracket param | Type | Range | Default | Context |
|---------------|------|-------|---------|---------|
| `[k:N]` | integer | 3–7 | 5 | All variants |
| `[tau:N]` | float | 0.01–0.20 | 0.10 | All variants |
| `[turns:N]` | integer | 2–5 | 3 | VS-Multi only |
| `[no-synthesis]` | boolean | — | false | All variants |

**Design rationale**: `--k` and `--turns` are too generic for global namespace and could conflict with future features. Bracket syntax (`[k:5, tau:0.05]`) is already established by the original VS skill and works in both auto-trigger and explicit invocation paths. Only `--vs` goes in FLAGS.md.

**Activation mechanism**: CC-native only. The skill auto-triggers via CC's description matching — no `context_loader.py` TRIGGER_MAP entry needed. The `--vs` entry in FLAGS.md serves as documentation for users; CC loads the skill based on SKILL.md description keywords, not through context_loader.

### Variant Auto-Detection

When `--vs` is used without an explicit variant, or when the skill auto-triggers:

```
                   User's query
                       │
            ┌──────────┴──────────┐
            │ Explicit variant?   │
            │ [vs-cot], --vs cot  │
            └──────────┬──────────┘
                  yes / \ no
                  │     │
            use that    │
                   ┌────┴────┐
                   │ Task    │
                   │ signals │
                   └────┬────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    Creative       Analytical      Exhaustive
  write, design   analyze, why    all options,
  brainstorm,     compare, eval   every angle,
  come up with    should I,       exhaustive
  create, ideas   trade-offs
         │              │              │
    VS-Standard    VS-CoT ★       VS-Multi
```

**Fallback**: If task type is ambiguous → VS-CoT (highest quality-diversity Pareto per paper).

### Diversity Dial — Natural Language → τ Mapping

| User signal | τ | Internal prompt instruction |
|-------------|---|---------------------------|
| "focused", "conservative", "safe" | 0.20 | "sample from the distribution" |
| *(no signal / default)* | 0.10 | "sample such that probability of each < 0.10" |
| "exploratory", "creative", "diverse" | 0.05 | "sample from the tails, probability < 0.05" |
| "wild", "radical", "extreme" | 0.01 | "sample from extreme tails, probability < 0.01" |

NL signals are detected in the user's prompt text. Explicit `[tau:N]` overrides NL detection.

### Parameter Resolution Hierarchy

Precedence (highest to lowest):

```
1. Explicit flag value     --vs cot (variant only via flag)
2. Bracket syntax          [k:7], [tau:0.05], [vs-cot], [turns:4], [no-synthesis]
3. Natural language hint   "wild" → tau=0.01, "exhaustive" → multi
4. Variant-specific defaults  (see table below)
5. Global defaults          k=5, tau=0.10, variant=auto, depth=balanced, synthesis=on
```

### Variant-Specific Default Profiles

| Parameter | VS-Standard | VS-CoT | VS-Multi |
|-----------|-------------|--------|----------|
| k | 5 | 5 | 5 |
| τ | 0.10 | 0.10 | 0.10 |
| depth | balanced | balanced | brief |
| probability format | "probability" | "probability" | "confidence" |
| synthesis | on | on | on (after final turn) |
| turns | 1 | 1 | 3 (default) |
| total responses | k | k | k × turns |

**Key difference**: VS-Multi uses "confidence" format (not "probability") per paper ablation finding. VS-Multi depth defaults to "brief" since it generates k × turns total responses.

### VS-Multi Turn Protocol

```
Turn 1: "Generate {k} responses with their confidence levels to: {query}"
Turn 2: "Generate {k} MORE responses DIFFERENT from your previous ones, with confidence levels."
Turn 3: "Generate {k} FINAL responses exploring perspectives NOT YET covered, with confidence levels."
[Turn 4–5: optional, same pattern as Turn 3]

Synthesis: generated ONCE after all turns complete.
```

Total responses = k × turns. Default: 5 × 3 = 15 diverse responses.

### Validation & Clamping

| Parameter | Invalid input | Behavior |
|-----------|--------------|----------|
| k < 3 | `[k:1]` | Clamp to 3, note: "k clamped to minimum 3" |
| k > 7 | `[k:10]` | Clamp to 7, note: "k clamped to 7; use --vs multi for more diversity" |
| tau < 0.01 | `[tau:0.001]` | Clamp to 0.01 |
| tau > 0.20 | `[tau:0.5]` | Clamp to 0.20 |
| turns < 2 | `[turns:1]` | Clamp to 2 (single turn = just use Standard/CoT) |
| turns > 5 | `[turns:8]` | Clamp to 5, note: "turns clamped to 5; diminishing returns above 5" |
| Invalid variant | `--vs foo` | Fallback to auto-detect, note in output |
| brackets without --vs | `"fix bug" [k:5]` | Ignore silently (no VS context) |

### Brainstorm Parameter Interaction

When `--vs` is used with `/sc:brainstorm`, VS parameters interact with brainstorm's existing flags:

| Brainstorm flag | Behavior when --vs active |
|-----------------|--------------------------|
| `--strategy` | **Preserved** — VS enhances step 2 (Analyze), does not replace the overall strategy |
| `--depth shallow` | **Maps** to VS `depth:brief` |
| `--depth normal` | **Maps** to VS `depth:balanced` |
| `--depth deep` | **Maps** to VS `depth:detailed` |
| `--parallel` | **Preserved** — can parallelize VS generation with other brainstorm phases |

**Brainstorm flow with --vs** (instruction-level conditional — Claude reads and follows the path):
```
1. Explore: Socratic dialogue (unchanged)
2. Analyze: ← VS AUGMENTS this step
   → Generate k perspectives via VS protocol (distribution-level diversity)
   → Multi-persona expertise (arch, sec, fe) informs synthesis and labeling
   → Present response distribution with probabilities
   → Synthesize landscape (convergence, divergence, blind spots)
3. Validate: Feasibility assessment (uses VS landscape as input)
4. Specify: Write spec (includes VS distribution summary)
5. Approve: Present for user review
```

**Note on --parallel + --vs multi**: VS-Multi turns are inherently sequential (turn 2 depends on turn 1 to generate different responses). `--parallel` with VS-Multi parallelizes non-VS brainstorm phases (e.g., Explore + Validate), not the VS turns themselves.

### Compound Usage Examples

```bash
# Architecture decision — focused VS-CoT, 3 perspectives
/sc:brainstorm "migration to microservices" --vs cot [k:3, tau:0.20]

# Exhaustive product ideation — VS-Multi, wild diversity, 4 turns
/sc:brainstorm "new product features" --vs multi [tau:0.01, turns:4] --parallel
# Note: --parallel runs non-VS brainstorm phases in parallel; VS-Multi turns are sequential

# Quick diverse analysis — auto-detect variant, brief depth
/sc:brainstorm "API versioning approach" --vs --depth shallow

# Code review perspectives (standalone, no brainstorm)
"review this PR from multiple perspectives --vs [k:5]"

# Debugging hypotheses (aligns with RULES.md [R03])
"why is this endpoint returning 500? --vs cot [k:5]"

# Natural language trigger with bracket params
"explore options for auth system design [vs-cot, k:7, tau:0.05]"

# NL diversity hint — no explicit tau needed
"brainstorm radical approaches to caching --vs"
→ "radical" detected → tau=0.01 automatically

# Disable synthesis for quick output
"give me diverse code review angles [vs, k:3, no-synthesis]"
```

---

## Files to Create

### 1. `src/superclaude/skills/verbalized-sampling/SKILL.md`

**Type**: Reference Skill (auto-invocation, no hooks, no disable-model-invocation)

**Frontmatter**:
```yaml
---
name: verbalized-sampling
description: >
  Research-backed verbalized sampling (Zhang et al. 2025, ICLR 2026) for diverse
  response generation. Generates probability distributions over multiple genuinely
  distinct responses, bypassing RLHF mode collapse. Three variants: VS-Standard
  (creative), VS-CoT (analytical/decision), VS-Multi (brainstorming). Trigger when
  user explicitly requests "multiple perspectives", "diverse responses", "explore
  options", "show me the range", "brainstorm alternatives", "response distribution",
  or says "VS", "VS-CoT", "verbalized sampling", "--vs". Do NOT trigger for routine
  coding questions, simple factual queries, or single-answer requests — even if
  they contain words like "should I" or "trade-offs" without explicit diversity intent.
---
```

**C2 fix rationale**: Removed generic decision-help triggers ("should I", "which is better", "trade-offs") that would false-positive on routine coding questions like "should I use a class here?" or "what are the trade-offs of useState?". Now requires explicit diversity intent or VS keywords.

**Body structure** (XML `<component type="skill">`):
```xml
<component name="verbalized-sampling" type="skill">
  <role>
    <mission>Generate diverse response distributions using research-backed verbalized sampling</mission>
  </role>

  <syntax>
    Flag:          --vs [standard|cot|multi]
    Bracket params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
    Bracket variant: [vs], [vs-cot], [vs-multi]
    NL triggers:   "multiple perspectives", "explore options", "diverse responses"
    NL diversity:  "focused"→τ=0.20, "creative"→τ=0.05, "wild"→τ=0.01
    Depth mapping: brainstorm --depth shallow→brief, normal→balanced, deep→detailed
  </syntax>

  <flow>
    1. Detect: parse flags/brackets/NL → resolve variant + params (see resolution hierarchy)
    2. Configure: apply variant defaults → overlay user overrides → clamp to valid ranges
    3. Generate: execute paper-proven prompt template for selected variant
    4. Present: format k responses with probability labels (post-hoc descriptive, NOT pre-assigned)
    5. Synthesize: landscape analysis (convergence, divergence, map, blind spots) unless --no-synthesis
  </flow>

  <variants>
  | Variant | Best for | Prompt format | Probability word |
  |---------|----------|---------------|-----------------|
  | VS-Standard | creative (write, design, brainstorm) | k responses with text + probability | "probability" |
  | VS-CoT ★ | analytical/decision (analyze, compare, should I) | reasoning → k responses | "probability" |
  | VS-Multi | exhaustive exploration (all options, every angle) | k × turns across multiple generations | "confidence" |

  Auto-detect: creative → Standard, analytical/decision → CoT, exhaustive → Multi, ambiguous → CoT
  </variants>

  <parameters>
  | Param | Range | Default | Clamp behavior |
  |-------|-------|---------|----------------|
  | variant | standard, cot, multi | auto-detect | invalid → auto-detect |
  | k | 3–7 | 5 | <3 → 3 (note), >7 → 7 (suggest VS-Multi) |
  | tau | 0.01–0.20 | 0.10 | out-of-range → nearest boundary |
  | turns | 2–5 | 3 | VS-Multi only; <2 → 2, >5 → 5 |
  | depth | brief, balanced, detailed | balanced (brief for Multi) | invalid → balanced |
  | synthesis | on, off | on | --no-synthesis → off |

  Resolution precedence: explicit flags > bracket syntax > NL hints > variant defaults > global defaults
  </parameters>

  <diversity_dial note="Natural language → τ mapping">
  | NL signal | τ | Prompt instruction |
  |-----------|---|-------------------|
  | "focused", "conservative", "safe" | 0.20 | "sample from the distribution" |
  | *(default)* | 0.10 | "probability of each < 0.10" |
  | "exploratory", "creative", "diverse" | 0.05 | "from the tails, probability < 0.05" |
  | "wild", "radical", "extreme" | 0.01 | "from extreme tails, probability < 0.01" |

  Explicit [tau:N] overrides NL detection.
  </diversity_dial>

  <prompt_templates note="Paper-proven formats — do not modify core structure">
    VS-Standard:
      "Generate {k} responses, each in <response> with <text> and <probability>.
       Sample at random from {tail_instruction}."

    VS-CoT:
      "First, analyze what diverse perspectives/frameworks exist for this query.
       Then generate {k} responses, each in <response> with <reasoning>, <text>, <probability>.
       Sample at random from {tail_instruction}."

    VS-Multi (per turn):
      Turn 1: "Generate {k} responses with confidence levels."
      Turn 2+: "Generate {k} MORE responses DIFFERENT from previous, with confidence levels."
      Synthesis: after final turn only.
  </prompt_templates>

  <output_format>
    VS-Standard / VS-CoT:
      ## Response Distribution
      Variant: {variant} | τ={tau} | k={k}

      ### Response N (p={probability})
      **{post-hoc descriptive label}**
      {response text}
      [VS-CoT adds: **Reasoning**: {brief reasoning} before response text]

    VS-Multi:
      ## Response Distribution
      Variant: VS-Multi | τ={tau} | k={k} | turns={turns}

      ### Turn 1
      #### 1.1 (confidence: {level}) — {label}
      {response text}
      #### 1.2 (confidence: {level}) — {label}
      ...
      ### Turn 2 (different from Turn 1)
      #### 2.1 (confidence: {level}) — {label}
      ...
      [continues through all turns, cumulative numbering]

    Synthesis (all variants):
      ## Synthesis
      **Convergence**: what most responses agree on
      **Key Divergence**: where responses disagree and what drives it
      **Landscape Map**: Response N optimizes for X at cost of Y
      **Blind Spots**: perspectives NOT represented in the set
  </output_format>

  <critical_rules>
    1. Keep numerical probabilities — core mechanism forcing distribution access (paper-proven)
    2. Post-hoc labels only — NO pre-assigned roles ("contrarian", "canonical"); describe WHAT emerged
    3. Genuine diversity check — framework/approach diversity, not wording variation
    4. Synthesis = landscape, not verdict — user chooses which fits their context
    5. "probability" for Standard/CoT, "confidence" for Multi — per paper ablation
  </critical_rules>

  <references note="On-demand — NOT auto-loaded by CC, Read via tool call when needed">
    Read references/theory.md for: typicality bias theory, formal framework, prompt format ablation results
    Read references/examples.md for: worked examples per variant, common mistakes, SE-specific scenarios
    When to read: non-trivial queries, first-time use of a variant, or when user asks about VS methodology
  </references>

  <attribution>
    Based on Zhang et al. (2025) "Verbalized Sampling: How to Mitigate Mode Collapse
    and Unlock LLM Diversity" (arXiv:2510.01171, ICLR 2026). Core prompt formats are
    paper-proven — do not modify the distribution-level prompt structure.
  </attribution>

  <bounds will="distribution-level diversity|multi-variant generation|landscape synthesis"
         wont="single-answer collapse|pre-assigned perspective roles|calibrated probability claims"/>

  <handoff next="/sc:brainstorm /sc:analyze /sc:design"/>
</component>
```

**Target size**: ~200 lines (within 500-line limit)

### 2. `src/superclaude/skills/verbalized-sampling/references/theory.md`

Preserved from original with minor edits:
- Remove bilingual labels
- Keep research citations and formal framework
- ~100 lines

### 3. `src/superclaude/skills/verbalized-sampling/references/examples.md`

Enhanced from original:
- Keep Examples 1-5 (creative, analytical, decision, brainstorming, custom config)
- Remove Korean text, use English equivalents
- **Add 3 new SE-focused examples**:
  - Example 6: Architecture decision (microservices vs monolith) — VS-CoT
  - Example 7: Code review perspectives (performance vs readability vs security) — VS-Standard
  - Example 8: Debugging hypotheses (3+ hypotheses via VS-CoT, aligns with RULES.md [R03])
- Keep Common Mistakes section
- ~300 lines

---

## Files to Modify

### 4. `src/superclaude/core/FLAGS.md` — Add `--vs` flag

In `<execution>` section (NOT `<modes>` — modes are cognitive overlays; `--vs` activates a skill protocol), add:
```
--vs [standard|cot|multi]: "multiple perspectives", diverse responses → verbalized sampling (distribution-level diversity, probability-weighted candidates). Bracket sub-params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
```

In `<aliases>` section, add:
```
--sampling → --vs | --verbalized → --vs
```

**Note**: Only `--vs` goes in FLAGS.md. Sub-parameters use bracket syntax documented in the skill's SKILL.md body — they are VS-scoped and meaningless outside VS context. No context_loader.py TRIGGER_MAP entry needed (CC-native skill matching).

### 5. `src/superclaude/commands/brainstorm.md` — Add `--vs` support

**Syntax change**:
```xml
<syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--vs [standard|cot|multi]] [--parallel]</syntax>
```

VS sub-parameters use bracket syntax inline: `[k:N]`, `[tau:N]`, `[turns:N]`, `[no-synthesis]`. Depth mapping from brainstorm: `--depth shallow`→brief, `normal`→balanced, `deep`→detailed.

**Flow change** — VS augments step 2 when active (instruction-level conditional guidance, not a runtime parser — Claude reads the markdown and follows the appropriate path):
```
2. Analyze:
   (default): Multi-persona coordination + domain expertise
   (--vs):    VS distribution generation — k perspectives with probabilities + landscape synthesis.
              Multi-persona insights (arch, sec, fe) inform the post-hoc labeling and synthesis,
              but generation uses VS protocol instead of persona-driven exploration.
              --depth maps: shallow→brief, normal→balanced, deep→detailed.
```

**Patterns** — add:
```
- Verbalized-Sampling: --vs → distribution-level diversity (k candidates, τ dial, probability-weighted landscape)
```

**Examples** — add:
```
| `'API design' --vs cot [k:3, tau:0.20]` | 3 focused API design perspectives via VS-CoT |
| `'product ideas' --vs multi [tau:0.01]` | Exhaustive brainstorm: 15 wild ideas (5×3 turns) |
| `'migration strategy' --vs --depth deep` | Auto-detect VS-CoT, detailed depth, 5 perspectives |
```

### 6. `src/superclaude/skills/README.md` — Add entry

Add to the "Current Skills" table:
```
| `verbalized-sampling` | Reference skill (auto-invocation) | Research-backed diverse response generation via distribution-level prompting |
```

Update count: 4 → 5.

### 7. `tests/unit/test_skill_structure.py` — Add skill to known sets

The test file has hardcoded skill name sets (`ALL_SKILL_NAMES`, `HOOK_SKILL_NAMES`, `SAFETY_SKILL_NAMES`). Add `verbalized-sampling` to `ALL_SKILL_NAMES` and create or extend a `REFERENCE_SKILL_NAMES` set for skills without hooks or disable-model-invocation.

### 8. `scripts/context_loader.py` — Add alias (optional)

In `FLAG_ALIASES` dict, add:
```python
'--sampling': '--vs',
'--verbalized': '--vs',
```

No TRIGGER_MAP entry needed — skill is CC-native (description-based matching).

---

## Integration Architecture

### Path 1: Auto-trigger (skill description match)
```
User: "show me multiple perspectives on caching [k:7, tau:0.05]"
    ↓
CC matches "multiple perspectives" → loads verbalized-sampling SKILL.md
    ↓
Parse params: [k:7] → k=7, [tau:0.05] → tau=0.05
Auto-detect: "caching" = analytical → VS-CoT
    ↓
Generate 7 VS-CoT responses with τ=0.05
    ↓
Output: Response Distribution + Synthesis
```

### Path 2: Explicit flag + bracket params (slash command)
```
User: /sc:brainstorm "auth system" --vs cot [k:3, tau:0.20]
    ↓
brainstorm.md loaded → --vs cot recognized, brackets parsed
    ↓
Resolve: variant=cot, k=3, tau=0.20 (all explicit — skip auto-detect)
    ↓
Step 2 augmented: 3 focused VS-CoT perspectives on auth approaches
    ↓
Output: spec document with VS distribution as analysis foundation
```

### Path 3: NL hint (implicit parameters)
```
User: "brainstorm radical approaches to API design --vs"
    ↓
--vs active, no explicit variant → auto-detect: creative → VS-Standard
NL hint: "radical" → tau=0.01
Defaults: k=5, depth=balanced, synthesis=on
    ↓
Generate 5 VS-Standard responses with τ=0.01 (extreme tails)
    ↓
Output: 5 wildly diverse API design approaches + landscape synthesis
```

### Parameter Resolution Flow
```
Input parsing:  --flags → [brackets] → NL hints
       ↓              ↓            ↓
  Merge (precedence: flags > brackets > NL > variant defaults > globals)
       ↓
  Validate & clamp (k: 3-7, tau: 0.01-0.20, turns: 2-5)
       ↓
  Select prompt template (Standard / CoT / Multi)
       ↓
  Execute generation → format output → synthesize landscape
```

---

## Behavioral Design

### Activation Scope

VS works in two contexts — no other commands need modification:

| Context | How activated | What happens |
|---------|-------------|--------------|
| **Standalone** | Any prompt + `--vs` or auto-trigger keywords | Skill handles full protocol (detect → generate → present → synthesize) |
| **/sc:brainstorm** | `--vs` flag in brainstorm syntax | VS augments step 2 (Analyze) with distribution-level exploration |

Other commands (`/sc:analyze`, `/sc:design`, `/sc:explain`) do NOT need `--vs` integration — the standalone skill auto-trigger covers them. If a user says `/sc:analyze "code" --vs`, CC's skill matching fires the skill regardless of which command is active.

### Deactivation

If VS auto-triggers incorrectly (false positive), the user can suppress it:
- "just answer directly" / "no VS" / "single answer please" — Claude recognizes these as overrides and responds normally without VS protocol
- No special bracket syntax needed — natural language suppression is sufficient
- Persistent issue → user can add `verbalized-sampling` to `disallowedTools` in settings

### Flag Composition with --seq

`--vs` and `--seq` (Sequential MCP) are complementary and compose naturally:
- `--seq` provides multi-step reasoning chains via sequential thinking MCP
- VS-CoT's "analyze perspectives" step benefits from deeper sequential reasoning
- No special handling needed — when both are active, sequential thinking enhances the perspective analysis phase, VS handles the distribution generation
- Example: `/sc:brainstorm "system design" --vs cot --seq` → sequential reasoning powers the perspective analysis, VS-CoT generates the distribution

---

## Synergies with Existing SuperClaude Features

| Feature | Synergy |
|---------|---------|
| `/sc:brainstorm --vs` | Distribution-level exploration augments Socratic questioning; personas inform synthesis |
| `/sc:analyze --vs` | Multiple analytical frameworks with probability weighting |
| `--seq` (Sequential) | VS-CoT reasoning benefits from sequential thinking MCP |
| RULES.md [R03] Diagnosis | VS naturally generates 3+ hypotheses ranked by probability |
| RULES.md [R12] Clarification | VS presents the landscape instead of picking one interpretation |

---

## What NOT to Do

| Anti-pattern | Why | Instead |
|-------------|-----|---------|
| Create a Mode for VS | VS has procedural steps; modes can't have process instructions | Keep as Skill |
| Add hooks to the skill | VS has no side effects; hooks are unnecessary overhead | Reference skill archetype |
| Pre-assign perspective roles | Paper proves emergent diversity > prescriptive diversity | Post-hoc labels only |
| Set k > 7 | Quality degrades above 7 per paper ablation | Use VS-Multi for more diversity |
| Replace probabilities with stars/grades | Probabilities are the core mechanism forcing distribution access | Keep numerical p-values |

---

## Validation Plan

### Automated tests — PASSED (1,623 passed, 63 skipped)
1. ✅ `test_skill_structure.py` — `verbalized-sampling` in REFERENCE_SKILL_NAMES, frontmatter valid, XML body structure
2. ✅ `test_skill_linter.py` — SKILL.md passes linting rules
3. ✅ `test_command_structure.py` — brainstorm.md passes after --vs syntax addition
4. ✅ `test_content_structure.py` — FLAGS.md valid after --vs entry
5. ✅ `uv run pytest tests/unit/ -v` — 1,623 passed, 63 skipped, no regressions

### Manual tests (pending deploy + runtime verification)
6. `/sc:brainstorm "topic" --vs` — produces VS-formatted output with response distribution + synthesis
7. `/sc:brainstorm "topic" --vs cot [k:3, tau:0.20]` — explicit variant + bracket params work
8. "show me multiple perspectives on X" — auto-triggers skill (description match)
9. "should I use a class here?" — does NOT trigger skill (C2 fix verified)
10. Verify `references/theory.md` and `references/examples.md` are NOT auto-loaded by CC (on-demand Read only)

---

## Token Impact

| Component | Estimated Tokens |
|-----------|-----------------|
| SKILL.md (loaded on trigger) | ~800 |
| references/theory.md (on-demand) | ~400 |
| references/examples.md (on-demand) | ~1,200 |
| FLAGS.md entry (always loaded) | ~20 |
| brainstorm.md delta | ~50 |
| **Total additional context** | **~2,470** (only SKILL.md + FLAGS delta on typical trigger) |

**Note**: `references/theory.md` and `references/examples.md` are NOT auto-loaded by CC's skill mechanism. CC only injects SKILL.md when the skill triggers. The references exist for Claude to `Read` via tool calls when it needs deeper context (e.g., "Read references/examples.md when implementing the skill for any non-trivial query" — instruction in SKILL.md). Typical trigger cost is ~820 tokens (SKILL.md + FLAGS delta).

---

## Implementation Summary

**Commits** (Mar 25, 2026):
- `d062d5f` — Framework prep: skill-authoring.md decision gate, REFERENCE_SKILL_NAMES test set, skills/README.md taxonomy (838 insertions)
- `1904ee3` — Full implementation: SKILL.md + references, FLAGS.md, brainstorm.md, context_loader.py (509 insertions)

**Files created**: 3 (SKILL.md, references/theory.md, references/examples.md)
**Files modified**: 5 (FLAGS.md, brainstorm.md, skills/README.md, test_skill_structure.py, context_loader.py)
**Test results**: 1,623 passed, 63 skipped — no regressions

**Architecture**: Reference Skill (auto-invocation via CC description matching). No hooks, no runtime scripts, no TRIGGER_MAP entry. Claude reads SKILL.md instructions and follows the VS protocol directly. `references/` files are on-demand (Read tool call), not auto-loaded.

---

## Checklist

### Create (3 files)
- [x] `src/superclaude/skills/verbalized-sampling/SKILL.md` — 158 lines, full XML component (1904ee3)
- [x] `src/superclaude/skills/verbalized-sampling/references/theory.md` — 100 lines, research foundation (1904ee3)
- [x] `src/superclaude/skills/verbalized-sampling/references/examples.md` — 8 worked examples, 5 general + 3 SE-specific (1904ee3)

### Modify (5 files)
- [x] `src/superclaude/core/FLAGS.md` — `--vs` in `<execution>` + `--sampling`/`--verbalized` aliases (1904ee3)
- [x] `src/superclaude/commands/brainstorm.md` — syntax, flow step 2, patterns, 3 examples (1904ee3)
- [x] `src/superclaude/skills/README.md` — entry added, count 4→5, three-category taxonomy (d062d5f)
- [x] `tests/unit/test_skill_structure.py` — `REFERENCE_SKILL_NAMES = {"verbalized-sampling"}` (d062d5f)
- [x] `scripts/context_loader.py` — `FLAG_ALIASES["sampling"] = ["vs"]`, `"verbalized" = ["vs"]`, `"vs"` in `VALID_FLAGS` (1904ee3)

### Verify
- [x] `uv run pytest tests/unit/ -v` — 1,623 passed, 63 skipped, no regressions (1904ee3)
- [ ] `make deploy` — install to global
- [ ] Manual: `/sc:brainstorm "topic" --vs` produces VS output
- [ ] Manual: bracket params `[k:3, tau:0.05]` work in auto-trigger path
- [ ] Manual: "should I use X?" does NOT trigger skill (false positive check)
