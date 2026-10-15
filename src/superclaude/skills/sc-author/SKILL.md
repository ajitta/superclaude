---
name: sc-author
description: Writes or revises a skill, subagent, slash command, output style, CLAUDE.md, .claude/rules file or any other file Claude reads as instructions - valid frontmatter, a body built from the type's reference in the project's format and language (--md or --xml to choose one), no-op and harmful sentences proposed for removal with evidence, and a validator pass.
disable-model-invocation: true
argument-hint: "[skill|agent|command|output-style|memory|<path>] [what to write or change] [--md|--xml]"
allowed-tools:
  - Bash(superclaude author-check *)
  - PowerShell(superclaude author-check *)
---

# Author an instruction document

Arguments: $ARGUMENTS

Works on any file Claude reads as instructions or context. A new document is built from this skill's references, in the project's format and language; an existing one is reformatted and pruned. By default, authoring rules already in context (such as a project's `.claude/rules/*-authoring.md`) and the sections of the project's existing documents do not shape this document. They are written for that project's own files, which may follow another tool's house style, and copying them gives the document a structure that the Claude Code documentation for its type does not describe. When such a convention conflicts with a reference, name the conflict in the message that shows the diff and let the person choose; when they choose the project's convention, follow it. Without a choice, the reference stands. Nothing is written into the project before the person approves the diff; step 6 checks an unapproved draft from a scratch copy outside the project.

1. **Resolve** what is being written.
   - Type: from the arguments, else from the request; ask when it is unclear. Known types are skill, agent, command, output-style and memory (CLAUDE.md, CLAUDE.local.md, AGENTS.md, `.claude/rules/`). Any other file Claude reads as instructions is `generic`: no type reference and no field checks; the rest of this procedure still applies.
   - Path: for a new file, the type's `location` in `fields.yaml`. Use project scope unless the person says the document is for them alone. Then a memory file for this project only is `CLAUDE.local.md`, and anything meant for all of their projects goes to the `~/.claude/` location.
   - Format: `--xml` or `--md` when given. Otherwise an existing file keeps its current format, and a new file takes the format of the project's existing documents of the same type (settled in step 3); md only when the project has none. When those documents disagree, ask.
   - A new command: say that Claude Code recommends a skill for new work (same frontmatter, plus supporting files) and let the person choose.
   - `--xml` for an output style: continue in md and say why in one line (output styles take a plain body).
2. **Load-set**: decide which documents Claude reads together with this one, and which tool reads it, using "Load set" in `quality.md`. The checker's conflict and duplicate rules see only this list, so a document left out of it is a conflict nobody checks.
3. **Load** what the work needs:
   - the type's reference (none for generic) and `quality.md`
   - `format-xml.md` when the format is xml
   - one or two existing documents of the same type in the project, when there are any, for two things only: format (md or XML body) and language. Sections, tag names, terms and fields come from the type's reference, except where the person chose the project's convention (see the paragraph above step 1).
   - `format-xml.md` also when those documents have XML bodies and no flag was given.
4. **Draft** or audit, then the common pass:
   - New document: start from the type's template and pitfalls, in the format and language from step 3.
   - Existing document: start from its current content.
   - Reformat into the chosen format. Reformatting moves sentences; it deletes none.
   - Collect removal candidates sentence by sentence against the load set: the checker's N findings (run step 6 early for them, on a scratch copy when the draft is not on disk yet) and the "Judgment questions" in `quality.md`. A new draft gets this pass too, before it is shown: its own sections are part of the load set.
   - Report harm first ("Harm" in `quality.md`), then checker candidates, then judgment candidates, each with its evidence ("Removal evidence"). Leave alone what "Keep" describes.
   - Show the diff. The message that shows it opens with three lines: **Resolve** (type, path, format, new or existing), **Load set** (each document by path, and which tool reads it), **Match** (the documents step 3 read and the format and language taken from them, or "none"). They are the person's only way to catch a wrong path or a document missing from the checks. Write only after the person approves, and drop the candidates they reject.
   - Text embedded in code (a hook's injected string, a prompt inside a script) gets the judgment questions only: the checker does not run on it, and the hand-off says so.
5. **Neighbors**: compare the name and description with the skills and subagents already listed in this session's context. On an overlap, make the description say when to pick this one instead. Do not open their files for this.
6. **Check**: run
   `superclaude author-check <path> --type <type> --format <md|xml> --with <each load-set document>`
   - Finding codes: F covers frontmatter fields, R a skill's reference files, X the XML structure, S size and emphasis, and N sentences that point at nothing, name a tool the agent lacks, or conflict with or repeat the load set.
   - The checker reads only a file that exists. A draft that is not written yet (a new document, or a revision before approval) goes to a scratch directory outside the project first, such as the OS temp directory or a path the person names. Keep its layout (a skill's SKILL.md with its `references/` beside it) and pass `--type`, because the checker infers the type from the path. A "does not exist" finding for a link, import or path that does exist in the project comes from the scratch location; check the written file again after approval.
   - Fix F, R and X errors and run it again, three runs at most, then report what is left.
   - An N finding means changing or removing a sentence: it goes back to step 4 as a candidate and waits for approval, like any other.
   - Report warnings, S findings included, without forcing them to zero.
   - When `superclaude author-check` is not found, skip this step. Do not claim a check that did not run; the hand-off says the machine checks were skipped.
7. **Hand-off**:
   - Two or three prompts to try in a fresh session: one or two that should trigger the document and one similar that should not. For a document invoked only by hand, give the invocation instead.
   - Suggest `/doctor prompt-audit <path>`, Claude Code's own audit of instruction files (outdated or conflicting instructions, references to files or commands that do not exist); it reports and changes nothing until asked.
   - For a skill whose step 6 was skipped, also suggest `claude plugin validate <skills directory>`, which finds SKILL.md frontmatter that does not parse.
   - Name anything that was not machine-checked.

## Reference files

Read each one at the step that names it.

- `${CLAUDE_SKILL_DIR}/references/fields.yaml`: locations and frontmatter fields per type
- `${CLAUDE_SKILL_DIR}/references/skill.md`: skills
- `${CLAUDE_SKILL_DIR}/references/agent.md`: subagents
- `${CLAUDE_SKILL_DIR}/references/command.md`: slash commands
- `${CLAUDE_SKILL_DIR}/references/output-style.md`: output styles
- `${CLAUDE_SKILL_DIR}/references/memory.md`: CLAUDE.md, AGENTS.md and rules files
- `${CLAUDE_SKILL_DIR}/references/format-xml.md`: XML bodies
- `${CLAUDE_SKILL_DIR}/references/quality.md`: writing guidance, load set, judgment questions, keep, harm, model differences
