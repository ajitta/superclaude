---
status: complete
revised: 2026-10-02
---

# 11 — claude.ai upload needs a plugin manifest

> **Superseded in part by [13](./13-review.md) §2.** The manifest no longer sits in the skill folder. It lives in `portable-skills/plugin-manifests/` and is injected only into the zip, because in the source folder it renamed the skill in Codex. The "Side effects" claim below that Codex ignores `.claude-plugin/` was wrong.

## Problem

The user uploaded the zip to claude.ai and got an error. The upload wanted a zip manifest: a top-level file declaring the plugin's components.

02-research §3 had taken the install path from the Help Center article "Use skills in Claude" (Customize › Skills › upload a ZIP of the skill folder). The upload the user reached runs through **plugins**. claude.com/docs/plugins/build says to zip the plugin folder and use Customize › Plugins › Add › Upload plugin. It also says the upload fails unless `.claude-plugin/plugin.json` sits at the zip root or inside a single top-level directory. Our zips held only `<skill>/SKILL.md`, so there was no manifest.

## Fix

- Each skill folder gets `.claude-plugin/plugin.json` with `name`, `displayName`, `version`, `description`, `author`, `license` and `homepage`, following the manifest example in claude.com/docs/plugins/build. Per the Claude Code plugins reference, a plugin with `SKILL.md` at its root and no `skills/` directory loads as a single skill, so the folder layout stays the same.
- `package.py` fails when the manifest is missing, is invalid JSON, or has a `name`/`version` that disagrees with `SKILL.md`. Mutation check: setting `version` to 9.9.9 → `ERROR socratic-elenchus: plugin.json version '9.9.9' != SKILL.md metadata.version '1.0.0'`.
- New tests: the zip contains `<skill>/.claude-plugin/plugin.json` and `<skill>/SKILL.md` under exactly one top-level folder, and the validator rejects a folder without a manifest.

## Verification

- `claude plugin validate portable-skills/<skill>`: ✔ Validation passed for both.
- The committed zip was unzipped into a scratch dir and loaded with `claude -p --plugin-dir` (both plugins) in an empty repo. Both registered as `socratic-elenchus:socratic-elenchus` and `socratic-brainstorm:socratic-brainstorm`. "소크라테스 대화법으로 따져줘: 사내 점심 메뉴 추천 앱" loaded the elenchus skill and opened with "좋은 추천이란 무엇인가요?".
- **Not verified:** the claude.ai upload itself, which needs the account UI. The user re-uploads to confirm.

## Side effects

- When installed as a plugin, the Claude Code slash command becomes `/socratic-elenchus:socratic-elenchus` (plugin namespace). Natural-language invocation is unchanged. README updated.
- Codex ignores `.claude-plugin/`, and `.claude/skills/` copies ignore it too.
