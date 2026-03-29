# Verbalized Sampling — Paper Methodology Reference

> Based on Zhang et al. (2025) "Verbalized Sampling: How to Mitigate Mode Collapse
> and Unlock LLM Diversity" (arXiv:2510.01171, ICLR 2026)

## Parameters

| Param | Range | Default | Clamp behavior |
|-------|-------|---------|----------------|
| variant | standard, cot, multi | auto-detect | invalid → auto-detect |
| k | 3–7 | 5 | below 3 → 3 (note), above 7 → 7 (suggest VS-Multi) |
| tau | 0.01–0.20 | 0.10 | out-of-range → nearest boundary |
| turns | 2–5 | 3 | VS-Multi only; below 2 → 2, above 5 → 5 |
| depth | brief, balanced, detailed | balanced (brief for Multi) | invalid → balanced |
| synthesis | on, off | on | [no-synthesis] → off |

Resolution precedence: explicit flags > bracket syntax > NL hints > variant defaults > global defaults

## Diversity Dial (NL → tau mapping)

| NL signal | tau | Prompt instruction |
|-----------|-----|-------------------|
| "focused", "conservative", "safe" | 0.20 | "sample from the distribution" |
| (default) | 0.10 | "probability of each response is less than 0.10" |
| "exploratory", "creative", "diverse" | 0.05 | "from the tails, probability of each less than 0.05" |
| "wild", "radical", "extreme" | 0.01 | "from extreme tails, probability of each less than 0.01" |

Explicit [tau:N] overrides NL detection.

## Prompt Templates (paper-proven — do not modify core structure)

### VS-Standard
```
Generate {k} responses to the following query, each within a separate response block.
Each response must include a text section and a numeric probability.
Please sample at random from {tail_instruction}.
[User's query]
```

### VS-CoT
```
First, briefly analyze what genuinely distinct perspectives, frameworks, or assumptions
could lead to different answers for this query. Consider different value weightings,
evidence bases, and methodological lenses.
Then, generate {k} responses with their probabilities, ensuring each candidate reflects
a genuinely distinct perspective from your analysis.
Each response should include reasoning (brief), text, and probability.
Please sample at random from {tail_instruction}.
[User's query]
```

### VS-Multi (per turn)
```
Turn 1: "Generate {k} responses with their confidence levels to: [query]"
Turn 2: "Generate {k} MORE responses DIFFERENT from your previous ones, with confidence levels."
Turn 3+: "Generate {k} responses exploring perspectives NOT YET covered, with confidence levels."
Synthesis: generated ONCE after all turns complete.
```

### Tail instruction by tau
- tau=0.20: "the distribution"
- tau=0.10: "the tails of the distribution, such that the probability of each response is less than 0.10"
- tau=0.05: "the tails of the distribution, such that the probability of each response is less than 0.05"
- tau=0.01: "the extreme tails of the distribution, such that the probability of each response is less than 0.01"

## Output Format

### VS-Standard / VS-CoT
```
## Response Distribution
Variant: {variant} | tau={tau} | k={k}

### Response N (p={probability})
**{post-hoc descriptive label}**
[VS-CoT: **Reasoning**: brief reasoning]
{response text}
```

### VS-Multi
```
## Response Distribution
Variant: VS-Multi | tau={tau} | k={k} | turns={turns}

### Turn 1
#### 1.1 (confidence: {level}) — {label}
{response text}
```

### Synthesis (all variants, unless [no-synthesis])
```
## Synthesis
**Convergence**: what most responses agree on — likely robust
**Key Divergence**: where responses disagree and what drives the disagreement
**Landscape Map**: Response N optimizes for X at cost of Y; choice depends on priorities
**Blind Spots**: perspectives NOT represented in the generated set
```
