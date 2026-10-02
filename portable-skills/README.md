# Portable skills

Skills here follow the [Agent Skills spec](https://agentskills.io/specification) subset that **every** target accepts, so one folder runs in Claude (chat, desktop, mobile, Claude Code, cloud sessions) and in Codex. They are separate from the SuperClaude framework: `superclaude install` does not install them, and nothing in `src/superclaude` depends on them.

| Skill | What it does |
|---|---|
| [socratic-brainstorm](./socratic-brainstorm/SKILL.md) | Questions your idea one question at a time, draws out your own options before adding any, ends with an honest verdict and a short brief. |

## Validate and package

```bash
python3 portable-skills/package.py          # validate + write dist/portable-skills/<name>.zip
python3 portable-skills/package.py --check  # validate only
```

`tests/unit/test_portable_skills.py` runs the same validator in CI. It rejects Claude Code-only frontmatter keys (`disable-model-invocation`, `argument-hint`, `when_to_use`, …) because claude.ai upload fails hard on them.

## Install

| Where you want it | How | Reaches mobile? |
|---|---|---|
| **Claude, everywhere** (recommended) | Upload `dist/portable-skills/socratic-brainstorm.zip` at claude.ai › Customize › Skills (needs Settings › Capabilities › Code execution on). The upload screen is not in the mobile app; use a desktop or mobile browser once. | Yes: chat in the iOS/Android app, the app's Code tab (cloud sessions), and Claude Code in the terminal via account sync (v2.1.273+). |
| Claude Code, one machine | `cp -r portable-skills/socratic-brainstorm ~/.claude/skills/` | No. Cloud sessions don't read `~/.claude/skills`. |
| Claude Code, one repo (incl. cloud sessions on that repo) | Commit the folder to `<repo>/.claude/skills/socratic-brainstorm/` | Yes, for sessions on that repo. In the mobile harness `/socratic-brainstorm` may not register (anthropics/claude-code#48696); say "socratic-brainstorm 스킬로 …" in words instead. |
| Codex CLI / IDE / ChatGPT desktop | `cp -r portable-skills/socratic-brainstorm ~/.agents/skills/` | No. |
| Codex cloud tasks on one repo (web, ChatGPT mobile) | Commit the folder to `<repo>/.agents/skills/socratic-brainstorm/` | Yes, for tasks on that repo. |

## Invoke

- Claude Code: `/socratic-brainstorm <idea>`
- Codex: `$socratic-brainstorm <idea>`
- Claude (chat, mobile, Code), in words: "소크라테스식으로 브레인스토밍 해줘: <idea>", "question me about <idea>", "poke holes in this plan". Add "세게"/`stress` to stress-test, "가볍게"/`quick` for a short pass.
- Codex needs the `$socratic-brainstorm` mention: implicit invocation is off, so plain wording does not load the skill there.

The skill doesn't parse flags; it reads mode and depth from your wording. Codex won't fire it implicitly (`agents/openai.yaml`). On Claude, the description is written to fire only on explicit requests, which includes asking for it in words.

Design notes and probe results: [docs/features/socratic-brainstorm-skill](../docs/features/socratic-brainstorm-skill/README.md).
