---
feature: socratic-brainstorm-skill
phase: complete
owner: ajitta
created: 2026-10-02
updated: 2026-10-02
related: ../../portable-skills/README.md
---

# Socratic brainstorming as a portable skill (Claude + Codex, incl. mobile)


SuperClaude already does Socratic brainstorming, but only inside Claude Code and spread over five files: `/sc:brainstorm`, `MODE_Brainstorming`, `socratic-mentor`, `requirements-analyst`, and the panels' `socratic` modes. This feature surveys that state and the published skills that implement the technique, then builds one skill that runs in Claude chat (web, desktop, iOS/Android), Claude Code (terminal and cloud/mobile Code tab) and Codex.

## Summary

- **v2 (current, 2.0.0)** runs the elenchus of Plato's early dialogues. It finds the concept an idea stands on and asks "what is X?". It collects premises the user agrees to, one short question at a time, and lays out where they contradict the definition. The user revises the definition, and each revision is a new idea. The usual ending is aporia. The model gives no ideas or advice during the dialogue. See [09](./09-elenchus-redesign.md).
- **v1 (1.0.0)** was modern "Socratic questioning" (Paul's six types) plus Osborn-style diverge/converge. The user pointed out it was not the Socratic method; [02](./02-research.md), [03](./03-analysis.md), [04](./04-design.md) and [08](./08-implementation.md) document that version and its research, kept for the record.
- **Portability** is unchanged: frontmatter uses only the six keys claude.ai upload accepts. Codex is explicit-only (`$socratic-brainstorm`). The upload zip is committed at `portable-skills/releases/` and a test keeps it in sync with the source.
- **Verified:** Claude Code (Sonnet 5.5) and Codex (`gpt-6.1-sol`) on two dialogues each; full test suite; CI. **Not verified:** the claude.ai upload and the mobile app.

## Documents

- [02-research.md](./02-research.md): repo inventory with file:line, 8 external skills compared, platform facts (spec, claude.ai, Claude Code cloud/mobile, Codex)
- [03-analysis.md](./03-analysis.md): elenchus + maieutics synthesis, requirements R1-R19 traced to sources, exclusions, size budget
- [04-design.md](./04-design.md): skill shape, decisions D1-D5, rejected and deferred items
- [08-implementation.md](./08-implementation.md): v1 (1.0.0): what shipped, tests, live probe results, defects fixed, what remains unverified
- [09-elenchus-redesign.md](./09-elenchus-redesign.md): v2 (2.0.0): why v1 was not the Socratic method, the elenchus from the dialogues with citations, what changed, committed zip, Claude + Codex probes

## Use it

See [portable-skills/README.md](../../../portable-skills/README.md). Short version: download [portable-skills/releases/socratic-brainstorm.zip](../../../portable-skills/releases/socratic-brainstorm.zip) and upload it at claude.ai › Customize › Skills. For Codex, copy the folder to `~/.agents/skills/` or to a repo's `.agents/skills/`.
