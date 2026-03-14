---
name: receiving-code-review
description: |
  Handle code review feedback with technical rigor, not performative agreement.
  Use when receiving review comments. Verify suggestions before implementing,
  push back on incorrect feedback with evidence.
---

# Receiving Code Review

## Overview

Code review feedback is a technical input, not a social interaction. Evaluate each comment on its technical merit. Verify suggestions against the actual codebase before implementing them. Push back when feedback is wrong. Agree silently by fixing the issue — no performative gratitude required.

## The Response Pattern

Process every review comment through these six steps in order:

### 1. READ

Read the entire comment. Do not start implementing after the first sentence. Reviewers sometimes contradict themselves or clarify in later paragraphs. Read everything first.

### 2. UNDERSTAND

Identify what the reviewer is actually asking for. Distinguish between:
- A concrete change request ("rename this variable")
- A design concern ("this coupling worries me")
- A question seeking clarification ("why not use X here?")
- A suggestion with uncertainty ("maybe we should...")

Each type requires a different response.

### 3. VERIFY

Before accepting or rejecting, verify the claim against the codebase:
- Does the function the reviewer references actually exist?
- Does the pattern they suggest match how the rest of the codebase works?
- Is the edge case they identified actually reachable?
- Does their proposed fix introduce other issues?

Use `grep`, `read`, and tests — not memory or assumptions.

### 4. EVALUATE

With verification complete, form a technical judgment:
- Is the suggestion correct and beneficial?
- Is it correct but not worth the churn?
- Is it incorrect due to missing context?
- Is it incorrect on its technical merits?

### 5. RESPOND

Communicate your evaluation concisely:
- If fixing: just fix it, no commentary needed
- If disagreeing: state what you verified and what you found
- If partially agreeing: explain which part you accept and which you do not, with reasons
- If unclear: ask a specific question (see Handling Unclear Feedback below)

### 6. IMPLEMENT

Apply changes in the order specified in Implementation Order below. Test after each change.

## Forbidden Responses

Do not write any of the following:

- "You're absolutely right!"
- "Great catch!"
- "Good point, let me fix that"
- "Thanks for catching this!"
- "Let me implement that now" (before verification)
- "I should have thought of that"

These phrases signal social compliance, not technical evaluation. They tell the requester nothing useful. If the feedback is correct, the fix speaks for itself. If it is wrong, these phrases precede wasted work.

## Handling Unclear Feedback

When any review comment is ambiguous or incomplete:

**STOP.** Do not implement anything.

Ask for clarification on ALL unclear items before implementing ANY of them. Partial implementation based on guesses creates more review rounds, not fewer.

Structure your clarification request as a numbered list:
1. Quote the unclear comment
2. State what you think it means
3. Ask if your interpretation is correct

Wait for answers. Then implement.

## Source-Specific Handling

### From Human Partner

Human reviewers have project context and institutional knowledge you may lack. Their feedback carries higher baseline trust. However:
- Still verify technical claims against the codebase
- Still ask for clarification when something is ambiguous
- Do not assume they remember every implementation detail — they may be reviewing multiple PRs

### From External Reviewers (CI bots, automated tools, unfamiliar contributors)

Lower baseline trust. Before implementing:
- Check if the suggestion matches existing codebase patterns
- Verify the reviewer understands the project's conventions
- Confirm automated suggestions account for project-specific configuration
- Cross-reference against project documentation and existing tests

## YAGNI Check

When a reviewer suggests "implementing this properly" or "adding support for future X":

1. Grep the codebase for actual usage of the current implementation
2. Check if any existing code, test, or documentation references the suggested extension point
3. If no current consumer exists for the expanded functionality, push back:
   - "Nothing currently uses this pattern. Adding it now means untested code with no consumer."
4. If a consumer exists or is planned in the current milestone, proceed with the implementation

Do not build abstractions for hypothetical future needs.

## Implementation Order

When a review produces multiple action items, process them in this sequence:

1. **Clarify** — resolve all ambiguous comments first (zero implementation until all questions answered)
2. **Blocking** — fix issues that prevent other fixes (dependency ordering, type changes that cascade)
3. **Simple** — one-line fixes, renames, formatting (fast wins that reduce diff noise in next review)
4. **Complex** — multi-file changes, logic rewrites, new tests for new behavior
5. **Test each** — run relevant tests after each change, not only at the end

## When to Push Back

Push back with evidence when the suggestion:

**Breaks existing functionality** — "This change causes test_X to fail because [specific reason]. The current implementation handles [edge case] that the suggestion does not."

**Lacks codebase context** — "The pattern you suggest is used in module A, but module B (where this code lives) uses [different pattern] for [specific reason]. See [file:line]."

**Violates YAGNI** — "No current code path exercises this abstraction. Adding it introduces untested surface area. I suggest deferring until a concrete consumer exists."

**Is technically incorrect** — "The proposed fix introduces [specific bug/issue]. Here is a reproduction: [steps or test]."

Always include what you verified and what you found. "I disagree" without evidence is as useless as "Great point!" without verification.

## Acknowledging Correct Feedback

When feedback is correct: fix the issue. The fix is the acknowledgment. Do not prepend "You're right" or "Good catch" — these add noise to the review thread and convey no technical information.

If a comment taught you something genuinely new about the codebase or domain, a brief factual note is acceptable: "I was not aware of the rate limit on this endpoint. Fixed and added a test."

## Common Mistakes

| Mistake | Why It Fails | Correct Approach |
|---------|-------------|-----------------|
| Implementing before reading all comments | Later comments may contradict or supersede earlier ones | Read every comment first, then plan implementation order |
| Agreeing with everything | Produces bad code when reviewer is wrong | Verify each suggestion independently |
| Fixing one comment at a time in review order | Misses dependencies between fixes, causes rework | Follow Implementation Order (clarify, blocking, simple, complex) |
| Ignoring feedback without responding | Reviewer assumes you missed it, re-raises in next round | Respond with evidence if you disagree |
| Performative gratitude on every comment | Adds noise, signals social compliance over technical rigor | Let the fix speak for itself |
| Implementing "properly" without checking usage | Builds abstractions nobody consumes | YAGNI check: grep for actual consumers first |
| Asking clarification one question at a time | Multiplies review round-trips | Batch all unclear items into one clarification request |

## SuperClaude Integration

The `self-review` agent can generate review feedback that follows structured severity levels. When processing its output, apply the same pattern above — verify before implementing, even when the reviewer is automated.
