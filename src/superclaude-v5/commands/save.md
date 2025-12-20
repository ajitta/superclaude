---
name: save
type: command
priority: medium
triggers: [save, snapshot, remember]
---

<document type="command" name="save">

# /sc:save

## Purpose
Save session context or notes.

## Syntax
```
/sc:save [name]
```

## Examples

<example>
  <input>/sc:save auth-debug</input>
  <output>Stores session context</output>
</example>

<example>
  <input>/sc:save architecture-notes</input>
  <output>Creates a named snapshot</output>
</example>

<example>
  <input>/sc:save</input>
  <output>Prompts for a name</output>
</example>

</document>
