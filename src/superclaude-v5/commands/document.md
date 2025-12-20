---
name: document
type: command
priority: medium
triggers: [document, docs, write, guide]
---

<document type="command" name="document">

# /sc:document

## Purpose
Create or update documentation.

## Syntax
```
/sc:document [target] [--type readme|api|guide]
```

## Workflow
1. Identify audience
2. Draft outline
3. Write and edit
4. Validate examples

## Examples

<example>
  <input>/sc:document README --type=readme</input>
  <output>Updated README sections</output>
</example>

<example>
  <input>/sc:document auth API --type=api</input>
  <output>Endpoint docs with examples</output>
</example>

<example>
  <input>/sc:document onboarding guide</input>
  <output>Step-by-step guide</output>
</example>

## Success Criteria
- Audience-appropriate content
- Examples validated
- Consistent formatting

## Boundaries

| Will | Won't |
|---|---|
| Draft documentation | Publish without review |
| Validate examples | Invent features |
| Follow templates | Override style guides |

</document>
