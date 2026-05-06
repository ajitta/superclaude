# Methodology Lessons — Agent Naming Experiment

How not to repeat the analysis errors made in the original 2-way `-expert` vs `-engineer` study. Three rules drawn from concrete mistakes that took two follow-up commits to correct.

## Lesson 1: Classify trial quality BEFORE computing aggregate metrics

**Mistake**: Computed mean output length across 15 trials without checking whether each trial was a real engagement with the task. Two of B's task-4 trials were broken (78-char empty-input hallucination; 2356-char preexisting-file hallucination). Their values dragged the aggregate mean — one too low, one too high — masking the true effect size.

**Cost of mistake**: The "B is shorter" gap was reported as 341 chars when the broken-trial-excluded gap is 436 chars (28% larger than reported).

**Rule**: Run a quality classifier (regex patterns + manual spot-check) before any `statistics.fmean()` call. Even a coarse classifier (`<50 chars` → suspect; `the file already exists` → halluc) catches the most damaging outliers.

**Heuristics that work**:
- Length floor: `<50 chars` for a non-trivial prompt → likely empty/refusal
- Pattern match on context-fabrication: `the file already exists`, `already (has|contains|on disk)`, `(corrected|fixed) the`, `all \d+ tests? (now )?(pass|passing)`
- Length ceiling on top of mean ± 3σ: outliers worth manual inspection
- Manual sanity-read of 2-3 outputs per condition before trusting any aggregate

## Lesson 2: Read all trials before drawing trial-level qualitative conclusions

**Mistake**: Cited B trial 1's narrative ("Here's the test file — one bug was corrected (`'a,a'` is a palindrome)") as evidence that "B caught an edge case A missed". Did not read A's trials before drawing this conclusion. A had actually handled the same edge case correctly in 2 of 3 trials, just without meta-narration.

**Cost of mistake**: Wrote a confidence-toned conclusion ("B caught what A missed → engineer is more critical-observation") that was the opposite of what the data showed. Required two follow-up commits to retract.

**Rule**: Before any qualitative claim about variant differences, read **every trial of every variant for the relevant task**. Narrative richness ≠ correctness. A silent correct answer beats a verbose narrated one.

**Practical loop**:
1. List trials matching the comparison.
2. Read each `result` field in full (not just first 200 chars).
3. Categorize what each variant actually did, not just what it talked about doing.
4. Then write the comparison.

## Lesson 3: Distinguish "narrates self-correction" from "catches what other missed"

**Mistake**: Treated "B trial 1 says it corrected a bug" as equivalent to "B has insight A lacks". The narrative is about B's writing process, not B's analytical depth.

**Cost of mistake**: Same as Lesson 2 — confused process verbosity for product correctness.

**Rule**: When a model meta-narrates its own work ("I noticed", "one bug was corrected", "the fix replaced X with Y"), that is a **style** signal — about how the model frames its output — not a **capability** signal. Capability is measured by the artifact (code that runs, tests that pass, types that check), not by the prose around it.

**Specific watchouts**:
- "I corrected" / "the fix" → sounds insightful, but check whether anything was actually corrected vs whether the model just produced the right answer in one shot.
- "I noticed that" → sounds like it caught a subtle issue, but the issue may have been in the model's own intermediate scratch, not in the input.
- Hallucinated context-fix narratives (e.g., the recursive-edit hallucination in this experiment) **look like reasoning steps** but are pure confabulation.

## Bonus: Pre-register predictions before reading new data

When extending an experiment (Phase 3 in this case), write down predictions and confidence levels **before** running the analyzer. The predictions in the Phase 3 writeup ended up 3-hit / 1-partial / 3-miss; the misses were the most informative results (expert-most-minimal-on-constrained-task; senior-task-6-clean) because they pointed at structure the prior model lacked.

Without pre-registration, the same data would have arrived as "see, the experiment confirms our intuition" — a textbook hindsight bias.

**How to pre-register cheaply**: write a 5-line table with `Question | Prediction | Confidence` before clicking run. Compare after results land. Calibration improves from this alone.
