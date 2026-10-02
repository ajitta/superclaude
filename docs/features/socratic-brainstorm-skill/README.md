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

- **Repo state.** The technique is there, but bound to Claude Code commands, hooks and subagents. The repo ships no skills: they were deliberately removed in `910eabd`. Nothing reaches chat, mobile or Codex.
- **Prior art.** Of 8 published skills read in full, grammy-jiang/socratic-method has the most rigorous elenchus (six question types, verbatim contradiction surfacing, aporia as a verdict), and obra/superpowers sets the one-question-per-message norm. None combines testing the idea with drawing the user's own options out. That combination is this skill's slot.
- **Portability constraint.** claude.ai upload rejects any frontmatter key outside `name, description, license, compatibility, metadata, allowed-tools`. So no `disable-model-invocation`; Codex gets explicit-only behavior through `agents/openai.yaml`. A claude.ai upload is the one install that reaches mobile chat, the mobile Code tab and the terminal.
- **Result.** `portable-skills/socratic-brainstorm/` (109-line SKILL.md + 2 references + Codex sidecar), a validator/packager, and 6 tests. Live probes on Sonnet 5.5 showed one ask per turn, verbatim contradiction surfacing, an aporia verdict on a stop signal, and user-first divergence. Three defects found by probing were fixed. Codex (`gpt-6.1-sol`) ran the same scenario to the same verdict; it needs the `$socratic-brainstorm` mention. The claude.ai upload and the mobile app were not run (see 08 §2).

## Documents

- [02-research.md](./02-research.md): repo inventory with file:line, 8 external skills compared, platform facts (spec, claude.ai, Claude Code cloud/mobile, Codex)
- [03-analysis.md](./03-analysis.md): elenchus + maieutics synthesis, requirements R1-R19 traced to sources, exclusions, size budget
- [04-design.md](./04-design.md): skill shape, decisions D1-D5, rejected and deferred items
- [08-implementation.md](./08-implementation.md): what shipped, tests, live probe results, defects fixed, what remains unverified

## Use it

See [portable-skills/README.md](../../../portable-skills/README.md). Short version: run `python3 portable-skills/package.py`, then upload `dist/portable-skills/socratic-brainstorm.zip` at claude.ai › Customize › Skills. For Codex, copy the folder to `~/.agents/skills/` or to a repo's `.agents/skills/`.
