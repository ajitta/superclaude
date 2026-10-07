# Elenchus patterns

Shapes, not scripts. Each one serves the current definition. Ask in the user's language.

## Forcing a definition

| User gives | Ask |
|---|---|
| An example ("one that suggests ramen") | "That's one case. What makes all of them X?" |
| A list ("fast, tasty, cheap…") | "Does it need all three to be X, or is one enough?" |
| A synonym ("a good recommendation is a decent one") | "How would you tell that it's 'decent'?" |
| "Depends" / "it varies" | "Across those situations, is there anything they share that makes you call it X?" |
| A refusal ("we don't need a definition") | "Then how would you tell whether what you're building is X or not?" |

## Premise questions (one per message, yes/no friendly)

- **Too broad:** "By that definition [odd case] counts as X. Is it?"
- **Too narrow:** "[clear case of X] falls outside the definition. Is it not X, then?"
- **Goal check:** "Earlier you said you want [the user's stated goal]. Does this definition get you there?"
- **Consequence:** "If X really is that, do you also accept [what follows]?"
- **Hypothesis** (Meno 86e-87b), when "what is X" stalls: "Let's set aside what X is. If X were [condition], what would follow?"

Agreed premises are numbered silently. Use only those numbers in Step 4.

## Laying out a contradiction (≤ 4 lines)

```
① <definition> (definition)
② <agreed premise> (agreed)
③ <agreed premise, if needed> (agreed)
So ① and ② can't both stand. Where would you change it?
```

In chat, render it as plain lines or a quote block, not a code block. The code block above only shows the shape.

## When the user pushes back

- "That's not what ② meant" → "Then how would you restate ②?" Restate it, get a "yes", and re-check whether the conflict still holds.
- "That's a leap" → re-read the step. If they're right: "You're right, that step doesn't follow. I'll withdraw it." Then continue.
- "My definition is just right" → "What case would make you accept that the definition is wrong?" If nothing could, note that as a finding, not a strength.

## Noticing a birth

When a revision moves the concept, name the move in one line: "<old> → <new>". Moves usually go one of these ways:

- from a means to an end ("fast recommendations" → "less time spent deciding")
- from one person to another ("easy for me" → "easy for the team to pick together")
- from a feature to a condition ("free" → "you can come with nothing prepared")

These moves are the brainstorm's output. A rewording that changes nothing is not a birth; say so.

## Signs of aporia

- The user's last two definitions have each fallen, and they have no third.
- The user says "I don't know" or "I'll have to think about it" about X itself, not about a detail.
- Each new definition reintroduces a premise they already gave up.

Name it gently: "It seems we've found out that we don't know what X is." Then go to the record.
