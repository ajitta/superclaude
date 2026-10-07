# Brief template

Lead with one plain line before the brief: the verdict and the next step. Fill every section from the user's answers only, and translate the section headers into the user's language. In chat, print the brief as plain Markdown, not inside a code block (code blocks scroll sideways on phones); the block below only shows the structure. Keep an empty section with "none" rather than dropping it, so the reader knows it was considered.

```markdown
# Brief: <short name>  ·  <YYYY-MM-DD>

**Verdict:** sharpened | open | refuted  ·  mode: develop|stress  ·  probes: <n>

## Thesis
- Before: <user's first statement, paraphrased>
- After: <refined thesis; any live risky assumption written in as a condition, e.g. "…, piloted for one month first">

## Decisions
- <decision> (confirmed | delegated)

## Assumptions
- <assumption> (validated | unvalidated | risky)

## Open questions
- <what must be answered before or while proceeding>

## Options considered
1. <option> (user's | mine): <one line on how it fared against the criteria>

## Criteria
- <the user's 2-3 criteria, their words>

## Parking lot
- <tangent worth keeping>

## Not tested this session
- <e.g. "no counterexample pressure", "no outside viewpoint">

## Next step
<one concrete action the user takes; one, not a list>
```

Rules:

- `refuted` requires both colliding statements quoted verbatim under Open questions or Thesis, plus the user's attempted reconciliation. Without that, it is `open`.
- `risky` means load-bearing *and* doubtful. Address risky assumptions first in the next step.
- More than one delegated decision: add "Recheck the delegated decisions before building" to the next step.
- In a repository that uses SuperClaude, a suitable next step is `/sc:design` or `/sc:review` on the brief. Suggest it; don't run it.
