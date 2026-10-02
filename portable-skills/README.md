# Portable skills

Skills here follow the [Agent Skills spec](https://agentskills.io/specification) subset that **every** target accepts, so one folder runs in Claude (chat, desktop, mobile, Claude Code, cloud sessions) and in Codex. They are separate from the SuperClaude framework: `superclaude install` does not install them, and nothing in `src/superclaude` depends on them.

| Skill | What it does | Pick it when | Upload zip |
|---|---|---|---|
| [socratic-brainstorm](./socratic-brainstorm/SKILL.md) | Modern Socratic questioning (six question types, one at a time) tests your idea. Then you list your options, it adds up to 3 labeled ones, you converge by criteria. Ends with a verdict (sharpened / open / refuted) and a brief with a next step. | You want to leave with options and a plan. | [socratic-brainstorm.zip](./releases/socratic-brainstorm.zip) |
| [socratic-elenchus](./socratic-elenchus/SKILL.md) | The elenchus of Plato's Socratic dialogues: "what is X?", premises you agree to one at a time, a contradiction built from them, you revise the definition. Your revisions are the new ideas. Usually ends in aporia. No advice at all. | You want to find out whether you really know what you mean. | [socratic-elenchus.zip](./releases/socratic-elenchus.zip) |

They work well in sequence: run `socratic-elenchus` to settle what the key word means, then `socratic-brainstorm` on the sharpened idea. Installing both is fine. Each description names the other, and explicit phrasings route correctly. A bare "소크라테스식으로" can land in either; the skill then says which style it is and how to ask for the other.

## Layout: plain skills in the source, plugins in the zip

```
portable-skills/
├── socratic-brainstorm/        plain Agent Skill (SKILL.md, references/, agents/openai.yaml)
├── socratic-elenchus/          plain Agent Skill
├── plugin-manifests/<skill>.json   plugin manifest, injected only into the zip
└── releases/<skill>.zip        <skill>/ + <skill>/.claude-plugin/plugin.json
```

Why the manifest is not in the skill folder:

- claude.ai uploads through Customize › Plugins, which rejects a zip without `.claude-plugin/plugin.json` (the error asks for a top-level manifest declaring the plugin's components). So the **zip** must carry one. A plugin with `SKILL.md` at its root and no `skills/` directory loads as a single skill (Claude Code plugins reference).
- In the **source folder**, a manifest changes how the folder loads elsewhere:
  - Codex 0.160 registers such a folder as `<skill>:<skill>`, so `$<skill>` stops resolving.
  - Claude Code loads it from `.claude/skills/` as a `<skill>@skills-dir` plugin after workspace trust, not as a plain skill.

`package.py` refuses a `.claude-plugin/`, `skills/` or `bin/` directory in a source folder. It also refuses a missing manifest, and a manifest whose `name`/`version` disagrees with `SKILL.md`.

## Validate and package

```bash
python3 portable-skills/package.py          # validate + write portable-skills/releases/<name>.zip
python3 portable-skills/package.py --check  # validate only
```

The zips are committed so they can be downloaded from GitHub directly. The build is byte-reproducible on Linux, macOS and Windows: fixed timestamps, modes and `create_system`, with LF line endings for text files. `tests/unit/test_portable_skills.py` fails if a committed zip lags its source. The same file runs the validator in CI, and it rejects Claude Code-only frontmatter keys (`disable-model-invocation`, `argument-hint`, `when_to_use`, …) because claude.ai upload fails hard on them.

## Install

Replace `<skill>` with `socratic-brainstorm` or `socratic-elenchus`.

| Where you want it | How | Reaches mobile? |
|---|---|---|
| **Claude, everywhere** (recommended) | Download `releases/<skill>.zip`, then claude.ai › Customize › **Plugins** › Add › Upload plugin. Not Customize › Skills: that screen rejects this zip ("a skill cannot contain a plugin manifest"). The upload screen is not in the mobile app; use a desktop or mobile browser once. | Yes: chat in the iOS/Android app, the app's Code tab (cloud sessions), and Claude Code in the terminal via account sync (v2.1.273+). |
| Claude Code, as a plugin | `/plugin marketplace add ajitta/superclaude`, then `/plugin install <skill>@ajitta-socratic`. Also listed in the [ajitta/claude-plugins](https://github.com/ajitta/claude-plugins) catalog as `<skill>@ajitta` | No. Plugins from user settings don't load in cloud sessions. |
| Claude Code, one machine | `cp -r portable-skills/<skill> ~/.claude/skills/` | No. Cloud sessions don't read `~/.claude/skills`. |
| Claude Code, one repo (incl. cloud sessions on that repo) | Commit the folder to `<repo>/.claude/skills/<skill>/` | Yes, for sessions on that repo. In the mobile harness `/<skill>` may not register (anthropics/claude-code#48696); ask for it in words instead. |
| Codex CLI / IDE / ChatGPT desktop | `cp -r portable-skills/<skill> ~/.agents/skills/` | No. |
| Codex cloud tasks on one repo (web, ChatGPT mobile) | Commit the folder to `<repo>/.agents/skills/<skill>/` | Probably, for tasks on that repo. Inferred from Codex scanning `.agents/skills` up to the repo root; not tested. |

## Invoke

| | socratic-brainstorm | socratic-elenchus |
|---|---|---|
| Claude Code, folder copied into `.claude/skills/` | `/socratic-brainstorm <idea>` | `/socratic-elenchus <idea>` |
| Claude Code, installed as a plugin | `/socratic-brainstorm:socratic-brainstorm <idea>` | `/socratic-elenchus:socratic-elenchus <idea>` |
| Claude Code, after a claude.ai upload (synced) | listed under `claude.ai sync`; the full name may carry an `anthropic-skills:` prefix | same |
| Codex (`$` required; implicit invocation is off) | `$socratic-brainstorm <idea>` | `$socratic-elenchus <idea>` |
| Claude in words (any surface) | "소크라테스식 브레인스토밍 해줘", "질문으로 아이디어 다듬어줘", "이 계획 반박해줘" | "소크라테스 대화법으로 따져줘", "엘렌코스로 검증해줘", "'X'가 뭔지부터 정의로 따져줘" |

Asking in words works on every surface, so it is the safe default on mobile.

Design notes and probe results: [docs/features/socratic-brainstorm-skill](../docs/features/socratic-brainstorm-skill/README.md).
