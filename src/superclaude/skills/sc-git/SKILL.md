---
name: sc-git
description: >-
  This skill should be used when the user asks to
  "commit my changes with a conventional message",
  "check PR review status",
  "push changes to remote",
  "create a feature branch",
  "resume work from a PR",
  "smart commit",
  "git workflow operations",
  "branch naming conventions",
  "recover from git conflicts".
version: 1.0.0
metadata:
  context: inline
  agent: general-purpose
  mcp: seq
  allowed-tools:
    - Bash
    - Read
    - Grep
    - Glob
  hooks:
    PreToolUse:
      - matcher: "Bash"
        hooks:
          - type: command
            command: "python3 {{SKILLS_PATH}}/sc-git/scripts/validate_git_safety.py"
            timeout: 5
---
<component name="sc-git" type="skill">

  <role>
    <mission>Git operations with intelligent commit messages and workflow optimization</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive] [--pr-status] [--from-pr PR#|URL]</syntax>

  <flow>
    1. Analyze: Run `git status` + `git diff --stat` to assess repo state and changes
    2. Validate: Check operation appropriateness (branch naming, destructive op guards)
    3. Execute: Perform git command with automation (smart commits, branch conventions)
    4. Optimize: Apply conventional commit patterns, suggest workflow improvements
    5. Report: Summarize results, recommend next steps, show handoff options
  </flow>

  <patterns>
    - SmartCommit: Analyze `git diff --cached` content, generate conventional commit message (feat/fix/docs/refactor/test/chore), present for user approval
    - Status: Parse `git status` + `git log --oneline -5`, produce actionable recommendations
    - Branch: Enforce naming conventions (feature/*, fix/*, docs/*, refactor/*, chore/*), warn on master/main direct work
    - Recovery: Guide conflict resolution with `git diff --name-only --diff-filter=U`, assist with `git stash` workflows
    - PRStatus: Run `gh pr view --json state,reviewDecision,isDraft`, map to status indicators (APPROVED/CHANGES_REQUESTED/PENDING/DRAFT)
    - FromPR: Accept PR number or URL, checkout branch via `gh pr checkout`, load PR description as session context
  </patterns>

  <safety>
    <safe>status, log, diff, add, commit, pull, fetch, branch, stash, pr-status, tag</safe>
    <approval_required>push --force, reset --hard, rebase, merge with conflicts, checkout -- (destructive), clean -f, branch -D</approval_required>
    <blocked>push --force to main/master (always blocked, no override)</blocked>
  </safety>

  <boundary_with_ship note="sc:ship vs sc:git">
    sc:ship = opinionated delivery workflow: stage + commit + push + optional PR (focused automation)
    sc:git = broad git operations toolkit: status, branching, recovery, PR status, smart commit, from-PR
    Overlap: both generate conventional commits. Distinction: sc:ship is "ship it now", sc:git is "git operations".
    Handoff: sc:git delegates to sc:ship when user intent is clearly "deliver these changes".
  </boundary_with_ship>

  <examples>
| Input | Output |
|-------|--------|
| `status` | State analysis + actionable recommendations |
| `commit --smart-commit` | Analyze diff, generate conventional commit, present for approval |
| `merge feature-branch --interactive` | Guided merge with conflict resolution |
| `--pr-status` | Current branch PR review state with color indicators |
| `--from-pr 123` | Checkout PR branch, load context, resume session |
| (auto-trigger) "commit my changes" | Skill activates, runs SmartCommit pattern |
| (auto-trigger) "what's the PR status" | Skill activates, runs PRStatus pattern |

  <example name="force-push-main" type="error-path">
    <input>/sc:git push --force origin main</input>
    <why_wrong>Force-pushing to main/master destroys team members' work and is irreversible.</why_wrong>
    <correct>Create a feature branch, push there, then open a PR for main.</correct>
  </example>
  </examples>

  <bounds will="intelligent git ops|conventional commits|workflow guidance|PR status checks|branch management|conflict recovery" wont="modify git config without auth|force push without confirm|complex merges requiring manual resolution|source code edits (use Edit tool)" fallback="Ask user for guidance when operation is ambiguous or destructive"/>

  <handoff next="/sc:test /sc:build /sc:ship"/>
</component>
