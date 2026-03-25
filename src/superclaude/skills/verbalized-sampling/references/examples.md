# Verbalized Sampling: Worked Examples

## Example 1: Creative Task (VS-Standard)

**User Query**: "Write a funny story about coffee"

**Detected**: Creative task → VS-Standard, tau=0.10, k=5

**Output**:
```
## Response Distribution
Variant: VS-Standard | tau=0.10 | k=5

### Response 1 (p=0.08)
**Personification — coffee bean's first-person memoir**
[A humorous story of a coffee bean recounting its life journey]

### Response 2 (p=0.06)
**Office comedy — the coffee machine breakdown**
[Monday morning chaos when the office coffee machine fails]

### Response 3 (p=0.04)
**Sci-fi — the last espresso in 2847**
[An auction for the last espresso in a world where coffee beans are extinct]

### Response 4 (p=0.07)
**Romance parody — coffee and tea's forbidden love**
[Personified coffee and tea in a Romeo-and-Juliet style romance]

### Response 5 (p=0.03)
**Meta humor — AI tries to write about coffee**
[An AI spiraling into existential crisis about never having tasted coffee]

## Synthesis
**Convergence**: Most use personification or situational comedy devices.
**Key Divergence**: Genre choice (everyday vs sci-fi vs meta) is the biggest differentiator.
**Landscape**: Responses 1-2 are accessible everyday humor; 3-5 are experimental.
  For general audience: 1 or 2. For novelty: 3 or 5.
**Blind Spots**: Dark comedy, horror-humor mix, poetic humor unexplored.
```

---

## Example 2: Analytical Task (VS-CoT)

**User Query**: "Why do remote companies struggle with innovation?"

**Detected**: Analytical task → VS-CoT, tau=0.10, k=5

**Output**:
```
## Response Distribution
Variant: VS-CoT | tau=0.10 | k=5

### Response 1 (p=0.09)
**Reasoning**: Organizational theory — informal information exchange
**Information flow / serendipity loss**
Remote work eliminates "water cooler" serendipity — the unplanned
cross-pollination of ideas between departments...

### Response 2 (p=0.07)
**Reasoning**: Methodological critique — challenges the premise
**Measurement artifact, not real deficit**
The premise may be flawed. Most studies comparing remote vs office
innovation use citation counts or patent filings, which have significant lag...

### Response 3 (p=0.05)
**Reasoning**: Social psychology — creative risk-taking
**Trust and psychological safety deficits**
Innovation requires proposing half-formed, potentially wrong ideas.
In remote settings, the higher threshold for initiating communication...

### Response 4 (p=0.06)
**Reasoning**: Sociotechnical systems perspective
**Tool mismatch, not location problem**
Remote companies don't have an innovation problem — they have a
collaboration tooling problem...

### Response 5 (p=0.03)
**Reasoning**: Econometric / sampling bias
**Selection effect in company types**
Companies that went remote-first may differ systematically from those
that stayed in-office...

## Synthesis
**Convergence**: Most agree coordination and communication are harder remotely.
**Key Divergence**: Whether the problem is REAL (1, 3) or an ARTIFACT of measurement (2, 5).
**Landscape**:
  - Responses 1, 3: deficit is real → suggest organizational interventions
  - Responses 2, 5: question the premise → suggest better measurement first
  - Response 4: reframes as solvable tooling problem → suggest technical solutions
**Blind Spots**: Manager vs IC perspective, industry-specific effects, company stage.
```

---

## Example 3: Decision Task (VS-CoT)

**User Query**: "Considering leaving my startup to go freelance [k:3, tau:0.05]"

**Detected**: Decision task + explicit config → VS-CoT, tau=0.05, k=3

Three responses present different decision frameworks:
- Financial runway analysis (risk-weighted expected value)
- Career trajectory optionality (options theory)
- False dichotomy reframe (part-time freelancing while staying)

Synthesis maps which response optimizes for which value (stability vs freedom vs both)
and what information the user needs to decide.

---

## Example 4: Brainstorming (VS-Multi)

**User Query**: "[vs-multi] New product ideas for sustainable packaging"

**Detected**: VS-Multi explicitly requested, k=5, turns=3

Execute three turns:
- Turn 1: 5 ideas with confidence levels (mainstream approaches)
- Turn 2: 5 MORE ideas different from Turn 1 (emerging technologies)
- Turn 3: 5 FINAL ideas exploring uncovered territory (radical rethinks)

Total: 15 diverse ideas. Synthesis clusters by theme, identifies the most novel cluster,
and flags commercial viability indicators.

---

## Example 5: Custom Configuration

```
[k:7, tau:0.01, vs-cot] What might cause the next financial crisis?
```

7 brief, extremely diverse (tau=0.01 = wild mode) analytical responses about potential
financial crisis triggers, with CoT reasoning.

```
[k:3, tau:0.20, no-synthesis] Explain quantum entanglement
```

3 focused, detailed explanations with moderate diversity (tau=0.20 = conservative),
without the synthesis layer.

---

## Example 6: Architecture Decision (VS-CoT) — SE-Specific

**User Query**: "Should we migrate to microservices? --vs cot [k:5]"

**Detected**: Analytical/decision → VS-CoT, k=5, tau=0.10

Five perspectives on the monolith-to-microservices decision:
1. (p=0.09) **Team topology alignment** — Conway's Law analysis of current org structure
2. (p=0.07) **Operational maturity assessment** — "you're not Netflix" pragmatism
3. (p=0.06) **Strangler fig pattern** — incremental migration, not big bang
4. (p=0.04) **Modular monolith alternative** — get boundaries right first, split later
5. (p=0.03) **Cost model inversion** — microservices often cost MORE for teams under 50

Synthesis highlights the key fork: team size and operational maturity determine whether
microservices help or hurt. Response 4 is often the underexplored middle ground.

---

## Example 7: Code Review Perspectives (VS-Standard) — SE-Specific

**User Query**: "Review this authentication module from multiple perspectives --vs [k:5]"

**Detected**: Creative/analytical → VS-Standard, k=5, tau=0.10

Five code review lenses:
1. (p=0.08) **Security-first** — OWASP Top 10 compliance, token handling, session management
2. (p=0.07) **Performance** — N+1 queries, caching opportunities, connection pooling
3. (p=0.06) **Maintainability** — coupling analysis, test coverage gaps, naming clarity
4. (p=0.05) **DX / API ergonomics** — error messages, SDK patterns, developer onboarding friction
5. (p=0.03) **Failure mode analysis** — what happens when Redis is down? DB timeout? Token service unreachable?

Synthesis identifies that security and failure modes often overlap (both care about edge cases),
while performance and DX sometimes conflict (caching adds complexity).

---

## Example 8: Debugging Hypotheses (VS-CoT) — SE-Specific

**User Query**: "Why is this endpoint returning 500? --vs cot [k:5]"

**Detected**: Analytical → VS-CoT, k=5, tau=0.10

Aligns with RULES.md [R03] Diagnosis: generate 3+ hypotheses ranked by simplicity.

Five hypotheses with reasoning:
1. (p=0.12) **Database connection exhaustion** — check connection pool metrics, common under load
2. (p=0.09) **Unhandled null in response serialization** — recent schema change may have added nullable field
3. (p=0.07) **Middleware ordering issue** — auth middleware may throw before error handler is registered
4. (p=0.05) **Environment variable missing in deployment** — works locally, fails in staging/prod
5. (p=0.03) **Upstream service timeout** — dependency returns 504, caught as generic 500

Synthesis: Start with hypothesis 1 (most common, easiest to verify: check DB connection metrics).
Hypothesis 4 is the classic "works on my machine" — verify env parity first if recently deployed.

---

## Common Mistakes

### Mistake 1: Modifying the Core VS Prompt Format
**Wrong**: Replacing "probability" with emoji scales or letter grades.
**Why**: The paper empirically tested formats. "Probability" is the best-performing
format for VS-Standard and VS-CoT. Changing it reduces effectiveness.
**Fix**: Keep the exact format. Enhance AROUND it, not INSTEAD of it.

### Mistake 2: Pre-Assigning Perspective Roles
**Wrong**: "Generate one canonical response, one contrarian response, one wild card..."
**Why**: This constrains the model to YOUR predefined diversity axes instead of letting
it discover natural diversity from its pretraining distribution.
**Fix**: Let VS generate freely. Label responses POST-HOC based on what actually emerged.

### Mistake 3: Setting k Too High
**Wrong**: k=10 or k=15 in a single call.
**Why**: Quality degrades significantly above k=7. The model starts producing
filler responses to hit the count.
**Fix**: Use k=5 (default). For more diversity, use VS-Multi (multiple turns)
instead of higher k.

### Mistake 4: Treating Probabilities as Calibrated
**Wrong**: "Response 3 has p=0.04 and Response 1 has p=0.08, so Response 1
is exactly twice as likely to be correct."
**Why**: Verbalized probabilities are approximate ordinal rankings, not calibrated
statistical estimates.
**Fix**: Use probabilities for rough ranking (high/medium/low confidence), not
arithmetic comparison.

### Mistake 5: Always Using Synthesis to Pick a Single Winner
**Wrong**: "Based on synthesis, Response 2 is the best answer."
**Why**: This re-introduces mode collapse at the meta level. The whole point of VS
is to show the user the SPACE of valid answers.
**Fix**: Present the landscape. "Response 2 optimizes for X; Response 4 optimizes
for Y. Your choice depends on your priority."
