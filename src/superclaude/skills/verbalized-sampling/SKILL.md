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

  <parameters>
  | Param | Range | Default | Clamp behavior |
  |-------|-------|---------|----------------|
  | variant | standard, cot, multi | auto-detect | invalid → auto-detect |
  | k | 3–7 | 5 | below 3 → 3 (note), above 7 → 7 (suggest VS-Multi) |
  | tau | 0.01–0.20 | 0.10 | out-of-range → nearest boundary |
  | turns | 2–5 | 3 | VS-Multi only; below 2 → 2, above 5 → 5 |
  | depth | brief, balanced, detailed | balanced (brief for Multi) | invalid → balanced |
  | synthesis | on, off | on | [no-synthesis] → off |

  Resolution precedence: explicit flags > bracket syntax > NL hints > variant defaults > global defaults
  </parameters>

  <diversity_dial note="Natural language → tau mapping">
  | NL signal | tau | Prompt instruction |
  |-----------|-----|-------------------|
  | "focused", "conservative", "safe" | 0.20 | "sample from the distribution" |
  | (default) | 0.10 | "probability of each response is less than 0.10" |
  | "exploratory", "creative", "diverse" | 0.05 | "from the tails, probability of each less than 0.05" |
  | "wild", "radical", "extreme" | 0.01 | "from extreme tails, probability of each less than 0.01" |

  Explicit [tau:N] overrides NL detection.
  </diversity_dial>

  <prompt_templates note="Paper-proven formats — do not modify core structure">
    VS-Standard:
      Generate {k} responses to the following query, each within a separate response block.
      Each response must include a text section and a numeric probability.
      Please sample at random from {tail_instruction}.
      [User's query]

    VS-CoT:
      First, briefly analyze what genuinely distinct perspectives, frameworks, or assumptions
      could lead to different answers for this query. Consider different value weightings,
      evidence bases, and methodological lenses.
      Then, generate {k} responses with their probabilities, ensuring each candidate reflects
      a genuinely distinct perspective from your analysis.
      Each response should include reasoning (brief), text, and probability.
      Please sample at random from {tail_instruction}.
      [User's query]

    VS-Multi (per turn):
      Turn 1: "Generate {k} responses with their confidence levels to: [query]"
      Turn 2: "Generate {k} MORE responses DIFFERENT from your previous ones, with confidence levels."
      Turn 3+: "Generate {k} responses exploring perspectives NOT YET covered, with confidence levels."
      Synthesis: generated ONCE after all turns complete.

    Tail instruction by tau:
      tau=0.20: "the distribution"
      tau=0.10: "the tails of the distribution, such that the probability of each response is less than 0.10"
      tau=0.05: "the tails of the distribution, such that the probability of each response is less than 0.05"
      tau=0.01: "the extreme tails of the distribution, such that the probability of each response is less than 0.01"
  </prompt_templates>

  <output_format>
    VS-Standard / VS-CoT:
      ## Response Distribution
      Variant: {variant} | tau={tau} | k={k}

      ### Response N (p={probability})
      **{post-hoc descriptive label}**
      [VS-CoT: **Reasoning**: brief reasoning]
      {response text}

    VS-Multi:
      ## Response Distribution
      Variant: VS-Multi | tau={tau} | k={k} | turns={turns}

      ### Turn 1
      #### 1.1 (confidence: {level}) — {label}
      {response text}
      #### 1.2 (confidence: {level}) — {label}
      ...
      ### Turn 2 (different from Turn 1)
      #### 2.1 (confidence: {level}) — {label}
      ...

    Synthesis (all variants, unless [no-synthesis]):
      ## Synthesis
      **Convergence**: what most responses agree on — likely robust
      **Key Divergence**: where responses disagree and what drives the disagreement
      **Landscape Map**: Response N optimizes for X at cost of Y; choice depends on priorities
      **Blind Spots**: perspectives NOT represented in the generated set
  </output_format>

  <critical_rules>
    1. Keep numerical probabilities — core mechanism forcing distribution access (paper-proven)
    2. Post-hoc labels only — NO pre-assigned roles ("contrarian", "canonical"); describe WHAT emerged
    3. Genuine diversity check — framework/approach diversity, not just wording variation
    4. Synthesis = landscape, not verdict — present the map of options, user chooses
    5. "probability" for Standard/CoT, "confidence" for Multi — per paper ablation finding
    6. k above 7 degrades quality — use VS-Multi (multiple turns) for more diversity instead
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
