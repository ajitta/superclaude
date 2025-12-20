---
name: load
type: command
priority: medium
triggers: [load, restore, resume]
---

<document type="command" name="load">

# /sc:load

## Purpose
Load a saved session or note set.

## Syntax
```
/sc:load [name]
```

## Examples

<example>
  <input>/sc:load auth-debug</input>
  <output>Restores context</output>
</example>

<example>
  <input>/sc:load architecture-notes</input>
  <output>Loads saved notes</output>
</example>

<example>
  <input>/sc:load</input>
  <output>Lists available saves</output>
</example>

## Success Criteria
- Context restored accurately
- Missing saves reported

## Boundaries

| Will | Won't |
|---|---|
| Restore saved context | Override current work |
| List available saves | Auto-merge conflicts |

</document>
