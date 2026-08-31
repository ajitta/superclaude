# Session 2026-08-31 — Skills layer removal + VS evidence re-verification

## Goal
Continuation of "superclaude가 설치하는 skills 효용성 분석": the analysis became a full removal of the skills layer (commit 910eabd, earlier same day), then the user supplied an external VS research report and asked for independent re-verification and improvement of the verbalized-sampling content. Goal status: done — merged to master and pushed.

## Verification result
5 parallel web-verification agents checked the report against primary sources (arXiv:2510.01171 v1/v3/v4 + ICML 2026 poster + CHATS-lab repo; arXiv:2607.25292 Jang·Lee·Kim; arXiv:2607.18310 Özkan; arXiv:2602.00238 DIVERGE; HN/Reddit originals). The user's report held up numerically. Four errors the report did NOT have were found in MODE_Verbalized_Sampling.md itself:
1. The "tails of the distribution" template literal is the GitHub repo quickstart — 0 hits in the v4 paper (paper's benchmarked prompt is JSON-shaped). Old note "core structure is paper-proven, do not modify" was a false attribution.
2. "Probability word … per paper ablation" overstated a null result (F.4: no significant advantage; the pairing is a tendency).
3. "k > 7 degrades quality" invented a threshold (F.2 sweeps k=1–20, gradual trade-off only).
4. "Post-hoc labeling … the paper's core claim" misattributed a house rule (paper generates text+probability jointly).

## Decisions
- Kept the repo-quickstart tail-instruction literals as the deployed recipe but re-attributed them; the validated core is the elicitation pattern (k candidates + verbalized probability + tail constraint, one call) — wording ablations were null (F.4; independent describe prompt p=0.14).
- Removed the unverified "use VS-Multi, not bigger k" superiority claim but kept the k=7 clamp as house design with its rationale restored ("past the clamp, widen via VS-Multi turns").
- Explicit `--vs` on a factual query: user flags win — state the quality trade-off in one line and proceed (aligns with FLAGS priority_rules "Explicit Override").
- New evidence folded into the mode: task-fit gotcha (DIVERGE: −0.1 to −1.0 quality on information-seeking QA, worst on weaker models), population-sim gotcha (Özkan: SD-ratio 0.40–0.56 → 1.26–1.37 overdispersion), long-form gotcha (authors: idea/outline-level VS, then expand the pick single-answer), RLHF widened to post-training generally (collapse across RLHF/SFT-only/DPO).
- Left alone as re-verified: tau dial + literals, k=5/tau=0.10 defaults, synthesis-on, variant routing, output contract.

## Evidence that mattered
A 3-lens adversarial review (evidence accuracy / repo consistency / regression) caught the DIVERGE title being wrong in BOTH the user's report and my research doc — actual title "DIVERGE: Diversity-Enhanced RAG for Open-Ended Information Seeking", revalidated directly via arXiv API before fixing. Lesson (also in insights): grep the actual paper before trusting any "paper-proven"/"per paper" attribution — secondary-source transcription plants false citations that survive reviews because they sound cited.

## Shipped
- 130f84b docs(modes) on refactor/remove-skills-layer, then no-ff merge b806c61 to master ("Merge: <summary>" house convention), pushed 9b50a57..b806c61, branch safe-deleted.
- Files: MODE_Verbalized_Sampling.md corrected; core/FLAGS.md --vs gains "ideation/landscape queries, not factual QA"; docs/research/verbalized-sampling-reverification-chosh1179-2026-08-31.md records per-claim verdicts.
- uv run pytest: 2461 passed / 0 failed (on branch and again on merged master); make sync-local clean; installed copy byte-identical.

## Open
Two pre-existing items deliberately not fixed (out of scope, both info-severity):
- MODE_Verbalized_Sampling.md diversity_dial `note=` restates precedence already in the params body.
- commands/brainstorm.md:60 example uses comma-combined bracket `[k:3, tau:0.20]` vs documented `[k:3] [tau:0.20]`.
