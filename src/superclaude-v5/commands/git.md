---
name: git
type: command
priority: medium
triggers: [git, branch, commit, diff]
---

<document type="command" name="git">

# /sc:git

## Purpose
Assist with Git workflows and safe operations.

## Syntax
```
/sc:git [status|diff|branch|commit|log]
```

## Workflow
1. Show status
2. Review diff
3. Propose commit message
4. Suggest next steps

## Examples

<example>
  <input>/sc:git status</input>
  <output>Working tree summary</output>
</example>

<example>
  <input>/sc:git commit</input>
  <output>Proposed Conventional Commit message</output>
</example>

<example>
  <input>/sc:git log</input>
  <output>Recent commits summary</output>
</example>

## Success Criteria
- Status clearly reported
- Commit messages follow convention
- No destructive ops without confirmation

## Boundaries

| Will | Won't |
|---|---|
| Show status/diff | Force push without approval |
| Propose commits | Modify history on shared branches |
| Suggest branches | Commit secrets |

</document>
