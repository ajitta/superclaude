# Record template

Lead with one plain line: the result, and the question the user takes away. Translate the headers into the user's language. Print plain Markdown, not a code block (code blocks scroll sideways on phones). Use only what the user said or agreed to. Keep an empty section as "none" rather than dropping it.

```markdown
# 문답 기록: <the idea>  ·  <YYYY-MM-DD>

**Result:** aporia | holding (provisional) | stopped before testing  ·  examined: <X>  ·  definitions tried: <n>

## How the definition changed
1. "<definition 1>": fell on ② + ③ (or: user withdrew premise ②)
2. "<definition 2>": fell on …
3. "<current definition, or none>"

## Agreed premises
② <premise>
③ <premise>
(withdrawn: <premise>, if any)

## Ideas born
- <old> → <new>: <one line on what this opens>

## What we now know we don't know
- <the part of X the user could not define>

## Not examined
- <sides of the definition never tested, e.g. "too-narrow side never tried">

## Question to take away
<one question the user can keep working on alone>
```

Rules:

- **aporia**: at least one definition fell, and the user has no surviving definition, or the current one is admittedly unclear.
- **holding**: the current definition passed at least one real breadth test and one goal or consequence test.
- **stopped before testing**: the user stopped while the current definition was still untested. Name which definitions fell before that.
- Quote definitions verbatim when the user stated them in one message. Otherwise paraphrase without quotation marks.
- If an empirical fact would settle part of X (counts, costs, who actually comes), you may add one line under "To check": the fact, not a plan.
- In a repository that uses SuperClaude, a later `/sc:brainstorm` or `/sc:design` can start from the ideas born. Mention it only if the user asks what's next.
