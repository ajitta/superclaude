---
name: ship
description: Ship changes with git add, conventional commit, push, and optional PR creation. This skill should be used when the user says 'ship', 'commit and push', 'create PR', or wants to deploy changes to remote.
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git push (--force([^-]|$)|-f([^a-zA-Z]|$))' && echo 'BLOCKED: Force push detected. Use regular push (--force-with-lease is allowed).' >&2 && exit 2 || exit 0"
---
<component name="ship" type="skill">

  <role>
    <mission>Auto delivery flow: stage → commit → push → PR. Safety checks + conventional commits.</mission>
  </role>

  $ARGUMENTS given → ship changes tied to that issue/context.

  <syntax>/ship [--pr] [--title "..."] [--base branch] [--exclude pattern] [--dry-run]</syntax>

  <flow>
  1. Status: run `git status` + `git diff --stat`, assess changes
  2. Validate: check branch naming (see references/conventions.md), warn if master/main
  3. Stage: `git add` relevant files, honor --exclude + default excludes
  4. Commit: build conventional commit msg from diff, show for approval
  5. Push: `git push -u origin <branch>` (confirm if first push to remote)
  6. PR (if --pr): `gh pr create`, summary from commits
  </flow>

  <references>
  - `references/conventions.md` — branch naming, commit format, PR template, default excludes. Read when need detail
  </references>

  <tools>
  - Bash: git, gh CLI
  - Grep: scan staged files for secrets
  </tools>

  <gotchas>
  - force-push: --force caught by hook, blocked hard. Regular push only
  - secrets: .env, credentials.json excluded by default. --include bypasses → must warn
  - staged-scan: scan staged files for API keys, tokens, passwords pre-commit
  - main-direct: push direct to master/main → suggest feature branch first
  </gotchas>

  <examples>
| Input | Output |
|---|---|
| `/ship` | Stage + commit + push current changes |
| `/ship --pr` | Stage + commit + push + create PR |
| `/ship --pr --title "Add auth" --base main` | Full delivery with custom PR |
| `/ship --exclude "*.test.*"` | Ship without test files |
| `/ship --dry-run` | Preview staging, commit message, push target |
  </examples>

  <bounds>
    <does>safe delivery auto, conventional commits, PR creation.</does>
    <never>force push, commit secrets, push main no confirm, skip user approval.</never>
  </bounds>

  <handoff next="/sc:test /sc:build"/>
</component>