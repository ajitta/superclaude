---
name: ship
description: Ship changes with git add, conventional commit, push, and optional PR creation.
when-to-use: >
  When user wants to ship, commit and push, create PR, or deploy changes to remote.
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git push --force|git push -f' && echo 'BLOCKED: Force push detected. Use regular push.' >&2 && exit 2 || exit 0"
---
<component name="ship" type="skill">

  <role>
    <mission>Automate the delivery workflow: stage → commit → push → PR with safety checks and conventional commits</mission>
  </role>

  When $ARGUMENTS is provided, ship changes related to that issue or context.

  <syntax>/ship [--pr] [--title "..."] [--base branch] [--exclude pattern] [--dry-run]</syntax>

  <flow>
    1. Status: Run `git status` + `git diff --stat` to assess changes
    2. Validate: Check branch naming conventions (see references/conventions.md), warn on master/main
    3. Stage: `git add` relevant files, respecting --exclude patterns and default exclusions
    4. Commit: Generate conventional commit message from diff analysis, present for approval
    5. Push: `git push -u origin <branch>` (confirm if first push to remote)
    6. PR (if --pr): Create PR via `gh pr create` with summary from commits
  </flow>

  <references>
  - `references/conventions.md` — branch naming, commit format, PR template, default exclusions. Read when detailed rules needed
  </references>

  <tools>
  - Bash: git commands, gh CLI
  - Grep: Scan for secrets in staged files
  </tools>

  <gotchas>
  - force-push: --force detected by hook and physically blocked. Only regular push allowed
  - secrets: .env, credentials.json are default exclusions but --include can bypass — warn required
  - staged-scan: Scan staged files for API keys, tokens, passwords patterns before commit
  - main-direct: When pushing directly to master/main, suggest creating feature branch first
  </gotchas>

  <examples>
| Input | Output |
|-------|--------|
| `/ship` | Stage + commit + push current changes |
| `/ship --pr` | Stage + commit + push + create PR |
| `/ship --pr --title "Add auth" --base main` | Full delivery with custom PR |
| `/ship --exclude "*.test.*"` | Ship without test files |
| `/ship --dry-run` | Preview staging, commit message, push target |
  </examples>

  <bounds will="safe delivery automation|conventional commits|PR creation" wont="force push|commit secrets|push to main without confirmation|skip user approval"/>

  <handoff next="/sc:test /sc:build"/>
</component>
