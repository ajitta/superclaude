---
paths: ["src/superclaude/skills/**", ".claude/rules/skill-authoring.md"]
---

# Skill Authoring Rules

Skills superclaude ships under `src/superclaude/skills/<name>/`, installed by the `skills` directory component into `<scope>/skills/<name>/`.

## Naming and invocation

- Directory and `name` start with `sc-` (`sc-author`): `.claude/skills/` is shared with the user's own skills and other tools, and the prefix keeps ours from colliding. Commands keep `/sc:*`; a skill name cannot contain `:`.
- A skill with a confirmed side effect (found in use or reported, `content-quality.md` §1 Trigger), or a meta skill that overlaps other authoring tools, sets `disable-model-invocation: true`.
- Claude Code-only frontmatter fields are allowed (no portability target).

## References

- References are written for the projects superclaude is installed into. Their source is the external documentation each file lists in `sources` (URL + retrieval date; a mirror of another skill's file gives that `file` and `section` instead of a URL), never this repository's rules: `content-quality.md`, `xml-prose-format.md` and the `*-authoring.md` files are conventions for superclaude's own content, so changing them does not change the references.
- No link to or import of any file outside `src/superclaude/` (gotcha `install-tree-boundary`).
- `tests/unit/test_sc_author_skill.py` keeps superclaude vocabulary out of them and the `quality.md` "Model differences" rows equal to the model IDs `/sc-prompt` resolves: adding a model there turns it red until the row is written from that model's prompting guide.
- `references/fields.yaml` is also checker data: after changing it, run `uv run pytest tests/unit/test_author_check.py`.

## Tests

- Skill structure and references: `tests/unit/test_sc_author_skill.py`, `tests/unit/test_sc_prompt_skill.py`
- Checker: `tests/unit/test_author_check.py`, `tests/unit/test_author_check_corpus.py`
- Install component: `tests/unit/test_install_skills_component.py`
