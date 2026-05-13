---
description: Git ops w/ smart commit msgs + workflow optim. Use when user type `/sc:git` or ask for smart commit msg draft, PR body, or guided git flow. NO auto-trigger on raw git cmds like "git status", "git log", "git diff", "git push" — invoke via Bash direct.
---
<component name="git" type="command">

  <role command="/sc:git">
    <mission>Git ops w/ smart commit msgs + workflow optim</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive] [--pr-status] [--from-pr PR#|URL]</syntax>

  <flow>
  1. Analyze: Repo state + changes
  2. Validate: Op fit
  3. Execute: Git cmd + auto
  4. Optimize: Smart commits + patterns
  5. Report: Status + next
  </flow>


  <tools>
  - Bash: Git cmd exec
  - Read: Repo state analysis
  - Grep: Log parse + status
  - Write: Commit msg gen
  </tools>

  <patterns>
    - SmartCommit: changes → conventional msg
    - Status: state → rec
    - Branch: naming + flow
    - Recovery: conflict fix + restore
    - PRStatus: gh pr view → review state → confidence
    - FromPR: --from-pr → checkout → load PR ctx → resume
  </patterns>

  <pr_status_integration note="Claude Code 2.1.37+">
    <description>PR review status indicator</description>
    <command>gh pr view --json state,reviewDecision,isDraft</command>
    <states>
      - APPROVED: Ready merge (green dot)
      - CHANGES_REQUESTED: Fix feedback first (red dot)
      - PENDING: Wait review (yellow dot)
      - DRAFT: Not ready (gray dot)
    </states>
    <usage>
      - /sc:git --pr-status: Show cur branch PR state
      - Auto w/ PRStatusCheck confidence check
    </usage>
  </pr_status_integration>

  <from_pr note="Claude Code 2.1.37+">
    <description>Resume session linked to PR # or URL</description>
    <usage>
      - `claude --from-pr 123`: Checkout PR branch + load ctx
      - `claude --from-pr https://github.com/org/repo/pull/123`: From URL
      - Auto-link: Sessions auto-linked to PRs made via `gh pr create`
    </usage>
  </from_pr>

  <examples>

| Input | Output |
|---|---|
| `status` | State analysis + recs |
| `commit --smart-commit` | Conventional commit |
| `merge feature-branch --interactive` | Guided merge |
| `--pr-status` | Cur branch PR review state |
| `--from-pr 123` | Resume from PR #123 |

  <example name="force-push-main" type="error-path">
    - Input: /sc:git push --force origin main
    - Why wrong: Force-push main/master destroy team work + irreversible.
    - Correct: Make feature branch, push there, open PR for main.
  </example>

  </examples>


  <gotchas>
  - new-commit: Make new commits, never amend unless asked
  </gotchas>

  <bounds>
    <does>smart git ops, conventional commits, flow guide, PR status check.</does>
    <never>change config w/o auth, destruct w/o confirm, complex merge needing manual.</never>
    <fallback>Ask user when unsure.</fallback>
  </bounds>

  <safety_rules>
    <safe>status, log, diff, add, commit, pull, fetch, branch, pr-status</safe>
    <approval_required>push --force, reset --hard, rebase, merge with conflicts</approval_required>
  </safety_rules>

  <handoff next="/sc:test /sc:build"/>
</component>