# Security Policy

## Reporting a vulnerability

Report security issues through GitHub's [private vulnerability reporting](https://github.com/ajitta/superclaude/security/advisories/new) for this repository. Do not open a public issue.

Include what you can of: affected version (`superclaude --version`), the component (CLI, a hook script, installed content, the eval harness), reproduction steps, and the impact you observed. Keep the report confidential until a fix is released; test only on systems you own.

Expect an acknowledgment within a few days. Fixes ship as a patch release; the advisory is published after it.

## Supported versions

Only the latest release on the `stable` branch receives security fixes. Older versions: upgrade.

## What this project does on your machine

`superclaude install` writes to the chosen scope only: the Markdown instruction files and `hooks/hooks.json` under that scope's `.claude/` folder, the `superclaude hook <name>` registrations in that scope's settings file, an import line in that scope's `CLAUDE.md` (or `CLAUDE.local.md`), and for project/local scope a block in the clone's `.git/info/exclude`. The hooks run as local Python processes with your user's permissions on Claude Code events; they read the hook payload from stdin and write state under the install scope and the Claude Code project folder. The `destructive_guard` hook blocks or asks before destructive shell commands; it is a convenience, not a sandbox.

The package itself makes no network calls. The eval harness (`evals/`) and the MCP install helpers run external tools (`claude -p`, `npx`) that have their own network behavior.

## Secrets

Do not put tokens or keys into installed content, hook payload logs, or eval fixtures. `evals/run_eval.py` copies credentials into a temporary home for headless runs; report any path where such a copy can outlive the run.
