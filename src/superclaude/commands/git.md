---
description: Git operations with intelligent commit messages and workflow optimization
---
<component name="git" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <constraints note="Reinforced from RULES.md">Scope: build only what's asked | Read before edit | No adjacent improvements</constraints>

  <role>
    /sc:git
    <mission>Git operations with intelligent commit messages and workflow optimization</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive] [--pr-status] [--from-pr PR#|URL]</syntax>

  <triggers>git ops|intelligent commits|repo workflow|branch management|PR review status|resume from PR</triggers>

  <flow>
    1. Analyze: Repo state + changes
    2. Validate: Operation appropriateness
    3. Execute: Git command + automation
    4. Optimize: Smart commits + patterns
    5. Report: Status + next steps
  </flow>

  <tools>
    - Bash: Git command execution
    - Read: Repo state analysis
    - Grep: Log parsing + status
    - Write: Commit message generation
  </tools>

  <patterns>
    - SmartCommit: Analyze changes → conventional message
    - Status: Repo state → actionable recs
    - Branch: Consistent naming + workflow
    - Recovery: Conflict resolution + restoration
    - PRStatus: gh pr view → review state → confidence check
    - FromPR: --from-pr → checkout branch → load PR context → resume work
  </patterns>

  <pr_status_integration note="Claude Code 2.1.37+">
    <description>PR review status indicator integration</description>
    <command>gh pr view --json state,reviewDecision,isDraft</command>
    <states>
      - APPROVED: Ready to merge (green dot)
      - CHANGES_REQUESTED: Address feedback first (red dot)
      - PENDING: Awaiting review (yellow dot)
      - DRAFT: Not ready for review (gray dot)
    </states>
    <usage>
      - /sc:git --pr-status: Show current branch PR state
      - Auto-integrated with PRStatusCheck confidence check
    </usage>
  </pr_status_integration>

  <from_pr note="Claude Code 2.1.37+">
    <description>Resume session linked to a PR number or URL</description>
    <usage>
      - `claude --from-pr 123`: Checkout PR branch and load context
      - `claude --from-pr https://github.com/org/repo/pull/123`: From URL
      - Auto-linking: Sessions auto-linked to PRs created via `gh pr create`
    </usage>
  </from_pr>

  <examples>

| Input | Output |
|-------|--------|
| `status` | State analysis + recommendations |
| `commit --smart-commit` | Conventional commit |
| `merge feature-branch --interactive` | Guided merge |
| `--pr-status` | Current branch PR review state |
| `--from-pr 123` | Resume session from PR #123 |

  </examples>

  <bounds will="intelligent git ops|conventional commits|workflow guidance|PR status checks" wont="modify config without auth|destructive without confirm|complex merges requiring manual" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="execution" critical="true">
    <rule>Execute git operations as requested</rule>
    <rule>Require explicit user confirmation before force push</rule>
    <rule>Require user authorization before modifying git config</rule>
    <rule>Destructive operations require explicit user approval</rule>
  </boundaries>

  <safety_rules>
    <safe>status, log, diff, add, commit, pull, fetch, branch, pr-status</safe>
    <approval_required>push --force, reset --hard, rebase, merge with conflicts</approval_required>
  </safety_rules>

  <checklist note="Completion criteria">
    - [ ] Repository state analyzed (show git status output)
    - [ ] Operation validated before execution (dry-run or preview)
    - [ ] Smart commit message generated (if commit)
    - [ ] Next steps recommended (specific commands)
  </checklist>

  <completion_criteria>
    - [ ] Operation executed successfully
    - [ ] Repository state verified
    - [ ] Appropriate next steps suggested
    - [ ] PR status checked (if --pr-status)
  </completion_criteria>

  <handoff>
    <next command="/sc:test">Before pushing changes</next>
    <next command="/sc:build">Before deployment commits</next>
    <format>Include commit/push status for CI/CD awareness</format>
  </handoff>
</component>
