# Portable skills

Skills here follow the [Agent Skills spec](https://agentskills.io/specification) subset that **every** target accepts, so one folder runs in Claude (chat, desktop, mobile, Claude Code, cloud sessions) and in Codex. They are separate from the SuperClaude framework: `superclaude install` does not install them, and nothing in `src/superclaude` depends on them.

| Skill | What it does | Pick it when | Upload zip |
|---|---|---|---|
| [socratic-brainstorm](./socratic-brainstorm/SKILL.md) | Modern Socratic questioning (six question types, one at a time) tests your idea. Then you list your options, it adds up to 3 labeled ones, you converge by criteria. Ends with a verdict (sharpened / open / refuted) and a brief with a next step. | You want to leave with options and a plan. | [socratic-brainstorm.zip](./releases/socratic-brainstorm.zip) |
| [socratic-elenchus](./socratic-elenchus/SKILL.md) | The method of Plato's early dialogues: "what is X?", premises you agree to one at a time, a contradiction built from them, you revise the definition. Your revisions are the new ideas. Usually ends in aporia. No advice at all. | You want to find out whether you really know what you mean. | [socratic-elenchus.zip](./releases/socratic-elenchus.zip) |

They work well in sequence: run `socratic-elenchus` to settle what the key word means, then `socratic-brainstorm` on the sharpened idea. Installing both is fine. Each description names the other, and explicit phrasings route correctly. A bare "소크라테스식으로" can land in either; the skill then says which style it is and how to ask for the other.

## Why each skill folder is also a plugin

claude.ai takes uploads through Customize › Plugins, which rejects a zip without `.claude-plugin/plugin.json` (the error asks for a top-level manifest declaring the plugin's components). Each skill folder therefore carries a minimal manifest. A plugin with `SKILL.md` at its root and no `skills/` directory loads as a single skill (Claude Code plugins reference). Codex and `.claude/skills/` copies ignore the `.claude-plugin/` folder. `package.py` fails if the manifest is missing or its `name`/`version` disagree with `SKILL.md`.

## Validate and package

```bash
python3 portable-skills/package.py          # validate + write portable-skills/releases/<name>.zip
python3 portable-skills/package.py --check  # validate only
```

The zips are committed so they can be downloaded from GitHub directly. The build is byte-reproducible, and `tests/unit/test_portable_skills.py` fails if a committed zip lags its source. The same test file runs the validator in CI. It rejects Claude Code-only frontmatter keys (`disable-model-invocation`, `argument-hint`, `when_to_use`, …) because claude.ai upload fails hard on them.

## Install

Replace `<skill>` with `socratic-brainstorm` or `socratic-elenchus`.

| Where you want it | How | Reaches mobile? |
|---|---|---|
| **Claude, everywhere** (recommended) | Download `releases/<skill>.zip`, then claude.ai › Customize › Plugins › Add › Upload plugin. The zip is a single-skill plugin (`.claude-plugin/plugin.json` + `SKILL.md`). The upload screen is not in the mobile app; use a desktop or mobile browser once. | Yes: chat in the iOS/Android app, the app's Code tab (cloud sessions), and Claude Code in the terminal via account sync (v2.1.273+). |
| Claude Code, as a plugin | `/plugin marketplace add ajitta/superclaude`, then `/plugin install <skill>@ajitta-socratic`. Also listed in the [ajitta/claude-plugins](https://github.com/ajitta/claude-plugins) catalog as `<skill>@ajitta` | No. Plugins from user settings don't load in cloud sessions. |
| Claude Code, one machine | `cp -r portable-skills/<skill> ~/.claude/skills/` | No. Cloud sessions don't read `~/.claude/skills`. |
| Claude Code, one repo (incl. cloud sessions on that repo) | Commit the folder to `<repo>/.claude/skills/<skill>/` | Yes, for sessions on that repo. In the mobile harness `/<skill>` may not register (anthropics/claude-code#48696); ask for it in words instead. |
| Codex CLI / IDE / ChatGPT desktop | `cp -r portable-skills/<skill> ~/.agents/skills/` | No. |
| Codex cloud tasks on one repo (web, ChatGPT mobile) | Commit the folder to `<repo>/.agents/skills/<skill>/` | Yes, for tasks on that repo. |

## Invoke

| | socratic-brainstorm | socratic-elenchus |
|---|---|---|
| Claude Code (copied into `.claude/skills/`) | `/socratic-brainstorm <idea>` | `/socratic-elenchus <idea>` |
| Claude Code (installed as a plugin) | `/socratic-brainstorm:socratic-brainstorm <idea>` | `/socratic-elenchus:socratic-elenchus <idea>` |
| Codex (`$` required; implicit invocation is off) | `$socratic-brainstorm <idea>` | `$socratic-elenchus <idea>` |
| Claude in words | "소크라테스식 브레인스토밍 해줘", "질문으로 아이디어 다듬어줘", "이 계획 반박해줘" | "소크라테스 대화법으로 따져줘", "엘렌코스로 검증해줘", "'X'가 뭔지부터 정의로 따져줘" |

Design notes and probe results: [docs/features/socratic-brainstorm-skill](../docs/features/socratic-brainstorm-skill/README.md).
