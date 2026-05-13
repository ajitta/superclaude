# Verbalized Sampling: Theoretical Foundation

## Typicality Bias

### What It Is
Human raters in RLHF prefer familiar, easy-read, predictable text. Well-known cog-psych finding — people pick "typical" exemplars.

### How It Causes Mode Collapse
Biased preferences train reward model to score conventional responses higher. LLM optimizes, squashes output distribution to narrow "safe" set. Pretraining diversity still in weights — alignment layer suppress it.

### Empirical Verification
Zhang et al. checked 6,874 HelpSteer response pairs. Raters consistently picked responses base model ranked most likely — quality irrelevant.

### Key Implication
Mode collapse = DATA problem (biased prefs), not pure algorithm problem (RLHF mechanics). Fix at inference via prompt semantics — no retrain needed.

---

## Why Distribution-Level Prompts Work

### The Mode-Shifting Mechanism
Different prompts → different modes. Instance prompt ("tell me a joke") → mode = single most typical response. Distribution prompt ("generate 5 jokes with probabilities") → mode = DISTRIBUTION approximating pretraining.

### Formal Intuition
Ask single response → model outputs argmax of compressed post-RLHF distribution → mode collapse.

Ask distribution with probabilities → model represent MULTIPLE modes at once → access broader pretraining distribution.

### Evidence
US states enum task: VS with Claude gave distribution with KL divergence 0.12 from RedPajama pretraining. Direct prompting collapsed to California and Texas only.

---

## Prompt Format Ablation Results

Paper tested formats for requesting distribution:

| Format | What You Ask For | Best For |
|--------|-----------------|----------|
| "probability" | Numeric probability values | VS-Standard, VS-CoT |
| "confidence" | Confidence level | VS-Multi |
| "percentage" | Percentage values | Works, slightly worse |

**Finding**: All formats beat direct prompting on diversity. "Probability" wins single-call. "Confidence" wins multi-turn.

### Number of Candidates (k)
- k=3: Min useful diversity. Good for quick queries.
- k=5: Best quality-diversity tradeoff. Paper default.
- k=7: More diversity, quality drops.
- k>7: Diminishing returns, noticeable quality drop.

---

## Combining VS with Other Techniques

### Temperature
VS and temperature orthogonal — different mechanisms. VS changes WHAT model generates (distribution semantics). Temperature changes HOW (softmax scaling). Combine = more gains.

### Chain-of-Thought
VS-CoT adds reasoning before generation. Pushes Pareto front — top diversity AND top quality together. Recommended when reasoning quality matters.

### Multi-Turn
VS-Multi stacks diversity across turns. Each turn told to differ from prior turns. Highest absolute diversity, higher token cost.

### Key Results
- 1.6-2.1x diversity gain in creative writing
- 25.7% gain in human eval
- 66.8% recovery of base model diversity
- Bigger models benefit more
- Safety and accuracy preserved