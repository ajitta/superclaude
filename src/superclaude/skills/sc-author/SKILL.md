---
name: sc-author
description: Writes or revises a skill, subagent, slash command, output style, CLAUDE.md, .claude/rules file or any other file Claude reads as instructions - valid frontmatter, a body in the project's own conventions and format (--md or --xml to choose one), no-op and harmful sentences proposed for removal with evidence, and a validator pass.
disable-model-invocation: true
argument-hint: "[skill|agent|command|output-style|memory|<path>] [what to write or change] [--md|--xml]"
allowed-tools:
  - Bash(superclaude author-check *)
  - PowerShell(superclaude author-check *)
---

# Author an instruction document

Arguments: $ARGUMENTS

Works on any file Claude reads as instructions or context. A new document follows the project's existing conventions; an existing one is reformatted and pruned. Nothing is written before the person approves the diff.

1. **Resolve** what is being written.
   - Type: from the arguments, else from the request; ask when it is unclear. Known types are skill, agent, command, output-style and memory (CLAUDE.md, CLAUDE.local.md, AGENTS.md, `.claude/rules/`). Any other file Claude reads as instructions is `generic`: no type reference and no field checks; the rest of this procedure still applies.
   - Path: for a new file, the type's `location` in `fields.yaml`. Project scope, unless the person says the document is for them alone (then the `~/.claude/` location).
   - Format: `--xml` or `--md` when given. Otherwise an existing file keeps its current format, and a new file takes the format of the project's existing documents of the same type (settled in step 3); md only when the project has none. When those documents disagree, ask.
   - A new command: say that Claude Code recommends a skill for new work (same frontmatter, plus supporting files) and let the person choose.
   - `--xml` for an output style: continue in md and say why in one line (output styles take a plain body).
2. **Load-set**: decide which documents Claude reads together with this one, and which tool reads it, using "Load set" in `quality.md`. Show the list in one line. The checker's conflict and duplicate rules see only this list, so a document left out of it is a conflict nobody checks.
3. **Load** what the work needs:
   - the type's reference (none for generic) and `quality.md`
   - `format-xml.md` when the format is xml
   - one or two existing documents of the same type in the project, when there are any. Show in one line what will be matched: format (md or XML body), language, terminology, heading or tag shape, section layout, the frontmatter fields actually used.
   - `format-xml.md` also when those documents have XML bodies and no flag was given.
4. **Draft** or audit, then the common pass:
   - New document: write it in the project's conventions from step 3. Use the type's fallback template only when the project has no document of that type.
   - Existing document: start from its current content.
   - Reformat into the chosen format. Reformatting moves sentences; it deletes none.
   - Collect removal candidates sentence by sentence against the load set: the checker's N findings (run step 6 early for them) and the "Judgment questions" in `quality.md`. A new draft gets this pass too, before it is shown: its own sections are part of the load set.
   - Report harm first ("Harm" in `quality.md`), then checker candidates, then judgment candidates, each with its evidence ("Removal evidence"). Leave alone what "Keep" describes.
   - Show the diff. Write only after the person approves, and drop the candidates they reject.
   - Text embedded in code (a hook's injected string, a prompt inside a script) gets the judgment questions only: the checker does not run on it, and the hand-off says so.
5. **Neighbors**: compare the name and description with the skills and subagents already listed in this session's context. On an overlap, make the description say when to pick this one instead. Do not open their files for this.
6. **Check**: run
   `superclaude author-check <path> --type <type> --format <md|xml> --with <each load-set document>`
   - Fix F, R and X errors (fields, references, XML structure) and run it again, three runs at most, then report what is left.
   - An N finding means changing or removing a sentence: it goes back to step 4 as a candidate and waits for approval, like any other.
   - Report warnings without forcing them to zero.
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
