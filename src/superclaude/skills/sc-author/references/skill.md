---
sources:
  - {url: "https://code.claude.com/docs/en/skills", retrieved: 2026-10-13}
  - {url: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices", retrieved: 2026-10-13}
---

# Skill

## When to use this type

A skill holds the instructions for one kind of task. Claude loads its body only when someone invokes it or its description matches the task, so it suits a procedure or reference material that is needed sometimes. What every session should know belongs in CLAUDE.md; what must happen every time belongs in a hook.

## Match the project first

Read one or two existing skills in the project (`.claude/skills/*/SKILL.md`) and match them:

- language and terminology
- how steps are written (numbered list, headed sections, checklist)
- how supporting files are named, placed and linked
- the frontmatter fields they actually use

A field the project uses that `fields.yaml` does not list for skills is not copied; report it as a candidate instead. With no skill in the project, start from the template below.

## Fallback template (md)

```markdown
---
name: <lowercase-hyphenated-name>
description: <What it does, in a few words>. Use when <the requests, file types or situations that call for it>.
---

# <Title>

1. <First action Claude takes>
2. <Next action>
3. <The check that shows it worked: a command to run or a result to compare>

## Reference files

- `${CLAUDE_SKILL_DIR}/references/<topic>.md`: read when <condition>
```

## Description

- Third person: "Processes Excel files and generates reports", not "I can help you…" or "You can use this…". The description is injected into the system prompt, and a shifting point of view hurts discovery.
- Say what it does and when to use it, with the terms a matching request would contain. Vague descriptions ("Helps with documents") do not select the skill.
- The skill listing cuts `description` plus `when_to_use` at 1,536 characters, so the main use case goes first.

## Pitfalls

- `name`: lowercase letters, digits and hyphens, at most 64 characters, without the words "anthropic" or "claude". It defaults to the directory name.
- Keep the body under 500 lines. Move detail into reference files linked directly from SKILL.md, one level deep: Claude may read a file reached through another reference only partially.
- A reference file over 100 lines gets a table of contents at the top.
- Paths use forward slashes, also on Windows.
- Say whether a bundled script is to be run ("Run `scripts/<name>.py`") or read ("See `scripts/<name>.py` for the algorithm").
- `disable-model-invocation: true` stops Claude from loading the skill on its own. For a skill that deploys, commits or sends something, that leaves the timing to the person.
