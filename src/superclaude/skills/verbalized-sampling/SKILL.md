---
name: verbalized-sampling
description: Research-backed verbalized sampling for diverse response generation with three variants.
when-to-use: >
  When user explicitly requests "multiple perspectives", "diverse responses", "explore options",
  "brainstorm alternatives", or says "VS", "VS-CoT", "verbalized sampling", "--vs".
  Do NOT trigger for routine coding questions, simple factual queries, or single-answer requests.
---
<component name="verbalized-sampling" type="skill">

  <role>
    <mission>Generate diverse response distributions using research-backed verbalized sampling</mission>
  </role>

  <syntax>
    Flag:           --vs [standard|cot|multi]
    Bracket params: [k:3-7], [tau:0.01-0.20], [turns:2-5], [no-synthesis]
    Bracket variant: [vs], [vs-cot], [vs-multi]
    NL triggers:    "multiple perspectives", "explore options", "diverse responses"
    NL diversity:   "focused" → tau=0.20 | "creative" → tau=0.05 | "wild" → tau=0.01
    Depth mapping:  brainstorm --depth shallow→brief, normal→balanced, deep→detailed
  </syntax>

  <flow>
    1. Detect: parse flags/brackets/NL → resolve variant + params
    2. Configure: apply variant defaults → overlay user overrides → clamp to valid ranges
    3. Generate: execute paper-proven prompt template for selected variant
    4. Present: format k responses with probability labels (post-hoc descriptive, NOT pre-assigned)
    5. Synthesize: landscape analysis (convergence, divergence, map, blind spots) unless [no-synthesis]
  </flow>

  <variants>
  | Variant | Best for | Prompt format | Probability word |
  |---------|----------|---------------|-----------------|
  | VS-Standard | creative (write, design, brainstorm) | k responses with text + probability | "probability" |
  | VS-CoT | analytical/decision (analyze, compare, evaluate) | reasoning → k responses | "probability" |
  | VS-Multi | exhaustive exploration (all options, every angle) | k × turns across multiple generations | "confidence" |

  Auto-detect: creative → Standard | analytical/decision → CoT | exhaustive → Multi | ambiguous → CoT
  VS-CoT is the recommended default — highest quality-diversity Pareto front per paper.
  </variants>

  <references note="Load on demand — NOT auto-loaded by CC, Read via tool call when needed">
  - `references/paper-methodology.md` — parameters, diversity dial, prompt templates, output format. Read before generating VS responses for the first time in a session
  - `references/theory.md` — typicality bias theory, formal framework, ablation results
  - `references/examples.md` — worked examples per variant, common mistakes, SE-specific scenarios
  </references>

  <essential_rules note="Inline minimums — do not depend solely on references/ for these">
  - Numerical probabilities are mandatory in every response (core mechanism)
  - Labels are post-hoc descriptive only — never pre-assign roles before generation
  - Prompt template structure from paper-methodology.md must be followed exactly
  </essential_rules>

  <gotchas>
  - pre-assign: Do not pre-assign probabilities. Post-hoc labeling only after response generation (paper core)
  - role-label: Do not pre-assign roles like "contrarian" or "canonical". Describe what emerged post-hoc
  - k-limit: k > 7 degrades quality. For more diversity, use VS-Multi (multiple turns) instead
  - word-diversity: Responses differing only in wording are not diverse. Require framework/approach-level differences
  - synthesis-verdict: Synthesis is a landscape map, not a verdict. User chooses
  - prob-word: Use "probability" for Standard/CoT, "confidence" for Multi — per paper ablation finding
  </gotchas>

  <attribution>
    Based on Zhang et al. (2025) "Verbalized Sampling: How to Mitigate Mode Collapse
    and Unlock LLM Diversity" (arXiv:2510.01171, ICLR 2026). Core prompt formats are
    paper-proven — do not modify the distribution-level prompt structure.
  </attribution>

  <bounds should="distribution-level diversity|multi-variant generation|landscape synthesis"
         avoid="single-answer collapse|pre-assigned perspective roles|calibrated probability claims"/>

  <handoff next="/sc:brainstorm /sc:analyze /sc:design"/>
</component>
