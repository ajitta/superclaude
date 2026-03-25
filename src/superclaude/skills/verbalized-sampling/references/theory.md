# Verbalized Sampling: Theoretical Foundation

## Typicality Bias

### What It Is
When human annotators rate LLM responses during RLHF, they systematically prefer text that
is familiar, easy to read, and predictable. This is a well-established cognitive psychology
finding — people gravitate toward "typical" exemplars of categories.

### How It Causes Mode Collapse
The typicality bias in preference data trains the reward model to assign higher scores to
conventional responses. The LLM then optimizes for this reward, compressing its output
distribution toward a narrow set of "safe" responses. The diverse knowledge from pretraining
still exists in the weights — it's just suppressed by the alignment layer.

### Empirical Verification
Zhang et al. analyzed 6,874 response pairs from the HelpSteer dataset. They found that
human raters consistently preferred the responses that the base model ranked as most likely,
regardless of whether those were actually higher quality.

### Key Implication
Mode collapse is a DATA problem (biased preferences), not purely an algorithmic problem
(RLHF mechanics). This means it can be addressed at inference time by changing prompt
semantics, without retraining.

---

## Why Distribution-Level Prompts Work

### The Mode-Shifting Mechanism
Different prompts collapse to different modes. For an instance-level prompt ("tell me a joke"),
the mode is the single most typical response. For a distribution-level prompt ("generate 5
jokes with their probabilities"), the mode is a DISTRIBUTION that approximates what the model
learned in pretraining.

### Formal Intuition
When you ask for a single response: the model outputs argmax of its compressed post-RLHF
distribution — mode collapse.

When you ask for a distribution of responses with probabilities: the model needs to represent
MULTIPLE modes simultaneously — accesses the broader pretraining distribution.

### Evidence
On the US states enumeration task, VS with Claude produced a distribution with
KL divergence of only 0.12 from the pretraining corpus (RedPajama) distribution. Direct
prompting collapsed into repeatedly outputting California and Texas.

---

## Prompt Format Ablation Results

The paper tested different ways to request the distribution:

| Format | What You Ask For | Best For |
|--------|-----------------|----------|
| "probability" | Numeric probability values | VS-Standard, VS-CoT |
| "confidence" | Confidence level | VS-Multi |
| "percentage" | Percentage values | Works, slightly worse |

**Finding**: All formats improve diversity over direct prompting. "Probability" performs
best for single-call variants. "Confidence" performs best for multi-turn variants.

### Number of Candidates (k)
- k=3: Minimum useful diversity. Good for quick queries.
- k=5: Optimal quality-diversity tradeoff. Paper default.
- k=7: More diversity but quality starts to degrade.
- k>7: Diminishing returns, noticeable quality degradation.

---

## Combining VS with Other Techniques

### Temperature
VS and temperature are orthogonal — they improve diversity through different mechanisms.
VS changes WHAT the model generates (distribution-level semantics). Temperature changes
HOW it generates (softmax scaling). Combining them yields further improvements.

### Chain-of-Thought
VS-CoT explicitly adds reasoning before generation. This pushes the Pareto front — achieving
the highest diversity while maintaining the highest quality simultaneously. This is the
recommended variant for any task where reasoning quality matters.

### Multi-Turn
VS-Multi accumulates diversity across multiple conversation turns. Each turn is instructed
to generate responses DIFFERENT from previous turns. This achieves the highest absolute
diversity but at higher token cost.

### Key Results
- 1.6-2.1x diversity improvement in creative writing
- 25.7% improvement in human evaluation
- 66.8% recovery of base model diversity
- Larger models benefit more
- Safety and accuracy preserved
