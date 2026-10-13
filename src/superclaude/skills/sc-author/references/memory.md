---
sources:
  - {url: "https://code.claude.com/docs/en/memory", retrieved: 2026-10-13}
---

# CLAUDE.md, AGENTS.md and rules files

## When to use this type

CLAUDE.md holds what Claude should know in every session of the project: build and test commands, conventions, structure. Instructions that matter only for part of the codebase go into a rules file in `.claude/rules/` with `paths`, which loads only when Claude works on matching files.

CLAUDE.md is context, not enforced configuration. To block an action whatever Claude decides, use a hook.

## How these files load

- CLAUDE.md files and rules without `paths` load at session start. Rules with `paths` load when Claude works on a matching file.
- AGENTS.md is read only when there is no CLAUDE.md or CLAUDE.local.md in the working directory or above it. To use both, import it from CLAUDE.md with an `@AGENTS.md` line; a sentence asking Claude to read it is not an import.
- `@path` imports resolve relative to the importing file and nest at most four hops.
- User-level rules load before project rules; neither overrides the other.
- Auto memory: the first 200 lines or 25KB of MEMORY.md load each session; topic files load only when opened.

## Match the project first

Read the project's CLAUDE.md and one or two rules files and match their language, heading layout, bullet style and how they group instructions. A new instruction goes where similar ones already are. With no CLAUDE.md, start from the template below.

## Fallback template (md)

```markdown
# <Project>

## Commands

- Build: `<command>`
- Test: `<command>`

## Conventions

- <A specific, checkable instruction, for example "Use 2-space indentation in YAML">
```

Rules file:

```markdown
---
paths: ["src/api/**/*.ts"]
---

- <An instruction that applies only to these files>
```

## Pitfalls

- Target under 200 lines per CLAUDE.md file; longer files take more context and reduce adherence. Move file-specific parts into path-scoped rules.
- Specific instructions are followed more consistently: "Use 2-space indentation", not "Format code properly".
- Two instructions that contradict each other, in one file or across files, leave Claude to pick one arbitrarily.
- In a rules file, `paths` is the only frontmatter field Claude Code reads. YAML that does not parse makes the rule load as if it had no `paths`.
