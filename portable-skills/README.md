# Portable skills

Skills here follow the [Agent Skills spec](https://agentskills.io/specification) subset that **every** target accepts, so one folder runs in Claude (chat, desktop, mobile, Claude Code, cloud sessions) and in Codex. They are separate from the SuperClaude framework: `superclaude install` does not install them, and nothing in `src/superclaude` depends on them.

| Skill | What it does |
|---|---|
| [socratic-brainstorm](./socratic-brainstorm/SKILL.md) | Plato's elenchus applied to an idea: "what is X?", premises you agree to one at a time, contradictions shown from your own statements, revisions as the new ideas, usually ending in aporia. Gives no advice. |

## Validate and package

```bash
python3 portable-skills/package.py          # validate + write portable-skills/releases/<name>.zip
python3 portable-skills/package.py --check  # validate only
```

The zip is committed so it can be downloaded from GitHub directly: [releases/socratic-brainstorm.zip](./releases/socratic-brainstorm.zip). The build is byte-reproducible, and `tests/unit/test_portable_skills.py` fails if the committed zip lags the source. The same test file runs the validator in CI. It rejects Claude Code-only frontmatter keys (`disable-model-invocation`, `argument-hint`, `when_to_use`, …) because claude.ai upload fails hard on them.

## Install

| Where you want it | How | Reaches mobile? |
|---|---|---|
| **Claude, everywhere** (recommended) | Download [releases/socratic-brainstorm.zip](./releases/socratic-brainstorm.zip) and upload it at claude.ai › Customize › Skills (needs Settings › Capabilities › Code execution on). The upload screen is not in the mobile app; use a desktop or mobile browser once. | Yes: chat in the iOS/Android app, the app's Code tab (cloud sessions), and Claude Code in the terminal via account sync (v2.1.273+). |
| Claude Code, one machine | `cp -r portable-skills/socratic-brainstorm ~/.claude/skills/` | No. Cloud sessions don't read `~/.claude/skills`. |
| Claude Code, one repo (incl. cloud sessions on that repo) | Commit the folder to `<repo>/.claude/skills/socratic-brainstorm/` | Yes, for sessions on that repo. In the mobile harness `/socratic-brainstorm` may not register (anthropics/claude-code#48696); say "socratic-brainstorm 스킬로 …" in words instead. |
| Codex CLI / IDE / ChatGPT desktop | `cp -r portable-skills/socratic-brainstorm ~/.agents/skills/` | No. |
| Codex cloud tasks on one repo (web, ChatGPT mobile) | Commit the folder to `<repo>/.agents/skills/socratic-brainstorm/` | Yes, for tasks on that repo. |

## Invoke

- Claude Code: `/socratic-brainstorm <idea>`
- Codex: `$socratic-brainstorm <idea>`
- Claude (chat, mobile, Code), in words: "소크라테스 대화법으로 따져줘: <idea>", "examine my idea Socratically: <idea>".
- Codex needs the `$socratic-brainstorm` mention: implicit invocation is off, so plain wording does not load the skill there.

Codex won't fire it implicitly (`agents/openai.yaml`). On Claude, the description is written to fire only on explicit requests, which includes asking for it in words.

Design notes and probe results: [docs/features/socratic-brainstorm-skill](../docs/features/socratic-brainstorm-skill/README.md).
