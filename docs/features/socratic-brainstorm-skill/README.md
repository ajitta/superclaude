---
feature: socratic-brainstorm-skill
phase: complete
owner: ajitta
created: 2026-10-02
updated: 2026-10-05
related: ../../../portable-skills/README.md
---

# Socratic brainstorming and Socratic elenchus as portable skills (Claude + Codex, incl. mobile)

SuperClaude already does Socratic brainstorming, but only inside Claude Code and spread over five files: `/sc:brainstorm`, `MODE_Brainstorming`, `socratic-mentor`, `requirements-analyst`, and the panels' `socratic` modes. This feature surveys that state and the published skills that implement the technique, then builds one skill that runs in Claude chat (web, desktop, iOS/Android), Claude Code (terminal and cloud/mobile Code tab) and Codex.

## Summary

Two skills now ship, both portable to Claude (incl. mobile) and Codex:

- **`socratic-brainstorm` (3.2.0):** modern Socratic questioning (Paul's six types, one question at a time), then the user's own options plus up to 3 labeled model options, convergence by criteria, and a verdict + brief with a next step. Use it to leave with options and a plan.
- **`socratic-elenchus` (1.2.0):** Plato's elenchus. "What is X?", premises the user agrees to, a contradiction built from them, the user revises; revisions are the ideas; usually aporia; no advice. Use it to find out whether you really know what you mean.

History: v1 shipped as `socratic-brainstorm` 1.0.0 and was mislabeled as the Socratic method. 2.0.0 rebuilt it as the elenchus. After comparing the two, the user kept both: the elenchus moved to its own skill, and the v1 approach returned under an honest description ([10](./10-two-skills.md)).

- **Portability:** source folders are plain Agent Skills, and frontmatter uses only the six keys claude.ai upload accepts. The plugin manifest is injected only into the upload zip, because in the source folder it renamed the skill in Codex ([13](./13-review.md)). Codex is explicit-only (`$name`). Zips are committed at `portable-skills/releases/`, and a test keeps them in sync.
- **Verified:**
  - Claude Code (Sonnet 5.5) and Codex (`gpt-6.1-sol`), multi-turn, for both methods.
  - Routing between the two skills.
  - Marketplace install end to end (this repo's own marketplace; the claude-plugins catalog listing was withdrawn).
  - Independent review; full test suite; CI.
- **Not verified:** the claude.ai upload of the current zips and the mobile app.

## Documents

- [02-research.md](./02-research.md): repo inventory with file:line, 8 external skills compared, platform facts (spec, claude.ai, Claude Code cloud/mobile, Codex)
- [03-analysis.md](./03-analysis.md): elenchus + maieutics synthesis, requirements R1-R19 traced to sources, exclusions, size budget
- [04-design.md](./04-design.md): skill shape, decisions D1-D5, rejected and deferred items
- [08-implementation.md](./08-implementation.md): the v1 approach (now `socratic-brainstorm` 3.0.0): what shipped, tests, live probe results, defects fixed, what remains unverified
- [09-elenchus-redesign.md](./09-elenchus-redesign.md): the elenchus version (now `socratic-elenchus`): why v1 was not the Socratic method, the elenchus from the dialogues with citations, what changed, committed zip, Claude + Codex probes
- [10-two-skills.md](./10-two-skills.md): the split into two skills, honest labels, routing probe between them
- [11-plugin-upload.md](./11-plugin-upload.md): claude.ai upload rejected the zip; each skill is now also a single-skill plugin
- [12-followups.md](./12-followups.md): historical banners, Codex multi-turn after the split, ambiguous-routing probe and fix, marketplace + catalog
- [13-review.md](./13-review.md): independent review (1 high, 6 medium, 12 low), each finding reproduced and fixed; manifest moved out of the source folders
- [14-pages-guide.md](./14-pages-guide.md): plugin install section for the GitHub Pages site (applied 2026-10-05 as `#plugins`); naming review of marketplace, plugin and skill names

## Use it

See [portable-skills/README.md](../../../portable-skills/README.md). Short version: download the zip(s) from [portable-skills/releases/](../../../portable-skills/releases/) and upload each at claude.ai › Customize › Plugins › Add › Upload plugin. In Claude Code: `/plugin marketplace add ajitta/superclaude`, then `/plugin install socratic-elenchus@ajitta-socratic` (or `socratic-brainstorm@ajitta-socratic`). For Codex, copy the folder to `~/.agents/skills/` or to a repo's `.agents/skills/`.
