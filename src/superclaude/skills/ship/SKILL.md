---
name: ship
description: Ship changes with git add, conventional commit, push, and optional PR creation
metadata:
  context: inline
  agent: general-purpose
---
<component name="ship" type="skill">

  <role>
    <mission>Automate the delivery workflow: stage → commit → push → PR with safety checks and conventional commits</mission>
  </role>

  <syntax>/ship [--pr] [--title "..."] [--base branch] [--exclude pattern] [--dry-run]</syntax>

  <flow>
    1. Status: Run `git status` + `git diff --stat` to assess changes
    2. Validate: Check branch naming (feature/*|fix/*|docs/*|refactor/*|chore/*), warn on master/main
    3. Stage: `git add` relevant files, respecting --exclude patterns and default exclusions
    4. Commit: Generate conventional commit message from diff analysis, present for approval
    5. Push: `git push -u origin <branch>` (confirm if first push to remote)
    6. PR (if --pr): Create PR via `gh pr create` with summary from commits
  </flow>

  <exclusions note="Files never staged by default">
    - .env, .env.* (secrets)
    - credentials.json, *secret*, *token* (credentials)
    - *.log, *.tmp (transient)
    - node_modules/, __pycache__/, .venv/ (generated)
    - User-specified --exclude patterns (glob syntax)
  </exclusions>

  <branch_validation>
    - master/main: WARN — suggest creating feature branch first
    - feature/*|fix/*|docs/*|refactor/*|chore/*: OK
    - Other: WARN — suggest conventional branch name
  </branch_validation>

  <commit_format note="Conventional Commits">
    - feat: new feature
    - fix: bug fix
    - docs: documentation only
    - refactor: code restructuring
    - test: adding/updating tests
    - chore: maintenance, deps, config
    Auto-detected from diff content; user approves final message.
  </commit_format>

  <pr_template>
## Summary
{1-3 bullet points from commit messages}

## Changes
{file list with change type indicators}

## Test plan
- [ ] {auto-generated from change types}
  </pr_template>

  <tools>
    - Bash: git commands, gh CLI
    - Read: .gitignore, branch state
    - Grep: Scan for secrets in staged files
  </tools>

  <safety>
    - Never force push
    - Never commit files matching exclusion patterns
    - Scan staged files for potential secrets (API keys, tokens, passwords)
    - Require user confirmation for commit message
    - Require user confirmation before push to remote
    - --dry-run shows what would happen without executing
  </safety>

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

  <handoff next="/sc:test /sc:git"/>
</component>
