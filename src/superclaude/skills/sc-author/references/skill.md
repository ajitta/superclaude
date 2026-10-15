---
sources:
  - {url: "https://code.claude.com/docs/en/skills", retrieved: 2026-10-14}
  - {url: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices", retrieved: 2026-10-13}
---

# Skill

## When to use this type

A skill holds the instructions for one kind of task. Claude loads its body only when someone invokes it or its description matches the task, so it suits a procedure or reference material that is needed sometimes. What every session should know belongs in CLAUDE.md; what must happen every time belongs in a hook.

## Project format and language

Read one or two existing skills in the project (`.claude/skills/*/SKILL.md`) for their format and language only. Steps, supporting-file layout and fields come from this file unless the person chose the project's convention for a conflict; a field the project uses that `fields.yaml` does not list for skills is reported as a candidate, not copied.

## Template (md)

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

- Third person: "Processes Excel files and generates reports", not "I can help you…" or "You can use this…". The description is injected into the system prompt, so keep one point of view there; the skill best practices guide warns that an inconsistent one can hurt discovery.
- Say what it does and when to use it, with the terms a matching request would contain. Vague descriptions ("Helps with documents") do not select the skill.
- The skill listing cuts `description` plus `when_to_use` at 1,536 characters, so the main use case goes first.

## Pitfalls

- `name`: lowercase letters, digits and hyphens, at most 64 characters, without the words "anthropic" or "claude". It defaults to the directory name.
- Keep the body under 500 lines. Move detail into reference files linked directly from SKILL.md, one level deep: Claude may read a file reached through another reference only partially.
- A reference file over 100 lines gets a table of contents at the top, so Claude sees what the file covers, and where, without reading all of it.
- Paths use forward slashes, also on Windows.
- Say whether a bundled script is to be run ("Run `scripts/<name>.py`") or read ("See `scripts/<name>.py` for the algorithm").
- A step that runs a command-line program (a search CLI the person set up, a build or test runner) names the command in the body. `allowed-tools` does not limit which tools the skill can use; it only skips the permission prompt for what it lists, during the turn that invokes the skill. Pre-approve that command narrowly (`Bash(<command> *)`), not all of `Bash`. `disallowed-tools` removes tools, so it must not list one a step needs. With `context: fork` the skill runs as the subagent named in `agent`, with that subagent's tools: a read-only one such as `Explore` cannot run the command.
- `disable-model-invocation: true` stops Claude from loading the skill on its own. For a skill that deploys, commits or sends something, that leaves the timing to the person.
