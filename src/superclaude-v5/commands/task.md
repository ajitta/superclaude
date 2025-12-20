---
name: task
type: command
priority: low
triggers: [task, todo, checklist]
---

<document type="command" name="task">

# /sc:task

## Purpose
Task management: create, track, and summarize tasks.

## Syntax
```
/sc:task [add|list|done] [item]
```

## Examples

<example>
  <input>/sc:task add "write migration guide"</input>
  <output>Task added</output>
</example>

<example>
  <input>/sc:task list</input>
  <output>Current task list</output>
</example>

<example>
  <input>/sc:task done 2</input>
  <output>Marks task 2 complete</output>
</example>

</document>
