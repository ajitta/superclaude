---
status: complete
revised: 2026-08-31
---

# Verbalized Sampling Re-verification — Evidence Base for MODE_Verbalized_Sampling.md

Re-verification of the research claims behind the `--vs` mode, run 2026-08-31 against primary
sources (all post-date the original mode authoring, Mar 2026). Method: 5 parallel verification
agents fetched the sources directly (arXiv v1/v3/v4 HTML, arXiv export API, ICML virtual site,
GitHub repo README, HN Algolia API, reddit .json) and returned per-claim verdicts with quotes;
a cross-check agent compared findings against the mode file's claims. This is literature/method
verification, not an experimental re-run.

## Sources

- Zhang et al., "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity",
  arXiv:2510.01171 v4 (revised 2026-07-15), ICML 2026 poster #60489. Repo: github.com/CHATS-lab/verbalized-sampling
- Jang, Lee, Kim (KAIST), "Instruction-Tuned Language Models Cannot Sample from Distributions
  They Can Describe", arXiv:2607.25292
- Özkan, "Distribution-First Population Simulation", arXiv:2607.18310
- "DIVERGE: Diversity-Enhanced RAG for Open-Ended Information Seeking", arXiv:2602.00238 v2
- Community: HN 46665183; r/MachineLearning 1uv1xb3 (ICML thread), 1o7ifvy (author Q&A);
  r/AIDungeon 1qpb05t; r/WritingWithAI 1ug1kh3

## What holds

- Diversity gains are real and independently replicated: 1.6–2.1x on creative writing (paper,
  10 models / ~6 families); ~4x semantic diversity over independent sampling (DIVERGE); fidelity
  +6.8–10.1 points (100·(1−TVD)) on survey distributions (Özkan); one-call distribution
  elicitation halves TV distance vs repeated sampling, 0.21–0.22 vs 0.46 (Jang·Lee·Kim).
- The paper's 25.7% human-eval gain is DIVERSITY, not quality preference; quality win-rates vs
  direct are near-ties on creative tasks (poem 0.52, story 0.46, joke 0.55, Table 14).
- VS-CoT is the paper's quality-diversity Pareto winner (§5.1); VS-Standard is the cost pick
  (G.2: 1.12x cost / 1.23x latency vs CoT 1.51x/1.66x, Multi 1.59x/2.81x — one poem condition).
- tau is a real diversity dial (F.5 sweep p ∈ 1.0→0.001, lower = more diverse); k trades
  diversity against per-candidate quality gradually (F.2, k=1–20, no threshold); k=5 is the paper's
  working default and the repo default; tau=0.10 is the repo default (the paper sweeps the threshold, F.5).
- Safety roughly unchanged: StrongReject 353×6 models, refusal 97.45–97.91% (VS) vs 98.22% (direct).
- Collapse cause is post-training generally, not RLHF specifically: Jang·Lee·Kim reproduce it
  across RLHF, SFT-only, and DPO pipelines; internal logits stay collapsed (top-two gaps reaching >14 nats on some targets)
  while verbalized distributions do not — verbalized probabilities are not a logit readout.

## What does not hold (or is bounded)

- "Diversity without quality loss" is creative-task-only: DIVERGE measures −0.12 to −0.98 on a
  5-point quality scale on information-seeking QA across all 8 model×dataset combos, worst on
  weaker models (GPT-5.1 −0.1 vs GPT-5-mini −0.98).
- Population simulation overdisperses structurally: SD-ratio 0.40–0.56 → 1.26–1.37 across 3
  model families (Özkan); paper's fix is a mean-preserving KL tilt, and subgroup/individual-level
  claims stay contaminated. VS weights are not frequency estimates.
- Mechanism is unresolved: no published control with arbitrary decorative numbers/labels instead
  of probabilities (HN critique; v4 added structure-matched Sequence-CoT/Multi and input-seeding
  controls, not that one). Wording barely matters: F.4 7-way probability-wording ablation found
  "no significant overall advantage"; an independently-worded describe prompt is statistically
  indistinguishable from VS (Wilcoxon p=0.14). The validated core is the elicitation pattern —
  k candidates + verbalized probability + tail constraint, in one call.
- Long-form is untested per the authors (Q&A): use VS at idea/outline level, select, then expand
  chapter-by-chapter; practitioners report most candidates are weak ("brainstorming seeds").

## Mode-file errors this pass found (beyond the source report)

1. Template provenance: the "sample at random from the tails of the distribution…" literal is the
   GitHub repo quickstart — it appears nowhere in the v4 paper (0 grep hits). The paper's
   benchmarked VS-Standard prompt is JSON-shaped ("probability from 0.0 to 1.0 … relative to the
   full distribution"). The old note "core structure is paper-proven, do not modify" misattributed it.
2. "Probability word … per paper ablation" overstated a null result (tendency only).
3. "k > 7 degrades quality" stated a threshold the paper never gives (gradual trade-off, k=1–20).
4. "Post-hoc labeling … this is the paper's core claim" misattributed a house rule — the paper
   generates text + probability jointly.

## Changes applied (same date)

`src/superclaude/modes/MODE_Verbalized_Sampling.md`: fixed the four misattributions; widened
RLHF → post-training in thinking; added task-fit, population-sim, and long-form gotchas; added a
factual-single-answer branch to the Route line; extended bounds (never reuse probabilities as
population-frequency/fact-confidence estimates) and fallback (factual queries route out unless
`--vs` is explicit — then state the trade-off and proceed; expansion of a picked candidate runs
single-answer); added the
provenance paragraph and cost note to templates. `core/FLAGS.md`: `--vs` line gained
"ideation/landscape queries, not factual QA". Left alone as verified: tau dial + literal tail
strings (deployed repo recipe), k/tau defaults, synthesis-on default, variant routing (creative/analytical/exhaustive), output format.
