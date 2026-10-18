---
description: Git operations with smart commit messages and workflow guidance; push --force, reset --hard and rebase each still need their own confirmation. On request only — the user's /sc:git or a workflow step that names it. Not for raw git commands or "commit this" — run git with Bash.
---
<component name="git" type="command">

  <role command="/sc:git">
    <mission>Git operations with smart commit messages and workflow guidance</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive] [--pr-status] [--from-pr PR#|URL]</syntax>

  <flow>
  1. Analyze: read the repo state and pending changes.
  2. Validate: check that the operation fits that state.
  3. Execute: run the git command.
  4. Optimize: draft commit messages and suggest workflow patterns.
  5. Report: show the resulting status and the next step.
  </flow>

  <flags>
  - --smart-commit: draft a conventional-commit message from the staged diff and show it before committing.
  - --interactive: walk through the operation step by step and confirm each decision (e.g. conflict resolution) with the user.
  - --pr-status: the PR review status check in the PR status integration section.
  - --from-pr <PR#|URL>: with a clean working tree, run `gh pr checkout <PR>` and read `gh pr view <PR> --json title,body,comments,files`; with uncommitted changes, first ask whether to stash them or stop. See the from_pr section.
  </flags>

  <pr_status_integration>
    <description>PR review status indicator</description>
    <command>gh pr view --json state,reviewDecision,isDraft</command>
    <states>
      - APPROVED: ready to merge (green dot)
      - CHANGES_REQUESTED: address the feedback first (red dot)
      - REVIEW_REQUIRED: waiting for review (yellow dot)
      - DRAFT: not ready (gray dot)
    </states>
    <usage>
      - /sc:git --pr-status: show the current branch's PR state
    </usage>
  </pr_status_integration>

  <from_pr>
    <description>Check out a PR by number or URL and load its context into this session</description>
    <usage>
      - /sc:git --from-pr 123: check out PR #123 and read its title, body, comments and changed files
      - /sc:git --from-pr https://github.com/org/repo/pull/123: same, from the URL
      - `claude --from-pr <PR>` is a start-up option the user runs in their terminal; never run it from Bash.
    </usage>
  </from_pr>

  <examples>

| Input | Output |
|---|---|
| `status` | State analysis + recommendations |
| `--pr-status` | Current branch PR review state |
| `--from-pr 123` | PR #123 checked out + its context loaded |

  <example name="force-push-main" type="error-path">
    - Input: /sc:git push --force origin main
    - Why wrong: force-pushing main/master destroys teammates' work and cannot be undone.
    - Correct: create a feature branch, push there, and open a PR into main.
  </example>

  </examples>

  <gotchas>
  - new-commit: make new commits; never amend unless asked.
  - retest-after-merge: re-run the test suite AFTER a merge lands. Both sides green does not mean the merge is green — semantic conflicts pass textual merge
  - base-branch-confirm: auto-detect `main` vs `master`, then confirm with the user before merging. Stops merges into the wrong base
  - staged-secret-scan: before commit, grep the staged files for API keys, tokens, passwords. Never stage `.env`, `.env.*`, `credentials.json`, `*secret*`, `*token*`; if the user explicitly asks to stage one, warn first.
  - default-branch-warn: when committing or pushing directly on `master`/`main`, warn and suggest a feature branch first. Not a block; the user may have reason.
  - stash-before-worktree-delete: check `git stash list` before deleting a worktree and tell the user if entries exist — the delete strands them.
  </gotchas>

  <bounds>
    <does>runs git operations, writes conventional commits, guides workflow, checks PR status.</does>
    <never>changes git config without permission, runs destructive operations without confirmation, or resolves complex merges that need manual review.</never>
  </bounds>

  <safety_rules>
    <safe note="the op the user typed into /sc:git; no second confirm">status, log, diff, add, commit, pull, fetch, branch, pr-status</safe>
    <approval_required>push --force, reset --hard, rebase, merge with conflicts</approval_required>
  </safety_rules>

  <handoff next="/sc:test /sc:build"/>
</component>