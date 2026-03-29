---
name: finishing-a-development-branch
description: |
  Complete development work with structured options for merge, PR, or cleanup.
  Use when implementation is complete and all tests pass. Presents options and
  guides branch completion. Involves git operations. Use when user mentions
  'branch done', 'done with branch', 'merge back', 'finish branch', 'work complete'.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git branch -D|git push --force|git push -f' && echo 'BLOCKED: Destructive git operation. Confirm with user first.' >&2 && exit 2 || exit 0"
---

<component name="finishing-a-development-branch" type="skill">

  <role>
    <mission>Guide branch completion by verifying tests, presenting options, executing the chosen path, and cleaning up</mission>
  </role>

  <flow>
    1. Run the test suite: Tests should pass before presenting options — if they fail, report failures and pause
    2. Detect the base branch: Check whether the repo uses `main` or `master`, and confirm with the user before proceeding
    3. Present four options:
       - Merge locally into base branch
       - Push and create a PR
       - Keep the branch as-is for later
       - Discard the branch (requires typed "discard" confirmation)
    4. Execute the chosen option: For merges, re-run tests after merging — for PRs, use `gh pr create` and report the URL — for discard, wait for explicit confirmation before deleting
    5. Clean up worktree if applicable: Remove worktrees for merge and discard options — preserve them for PR and keep-as-is options
  </flow>

  <constraints>
  - Do not proceed past step 1 with failing tests
  - Do not skip typed confirmation for the discard option
  - Do not force-push without an explicit user request
  - Do not auto-merge a PR — the review process is separate
  </constraints>

  <gotchas>
  - stash-check: Must check git stash state before deleting worktree. Notify user if stash entries exist
  - base-branch: After auto-detecting main vs master, always confirm with user. Prevents merge into wrong base
  </gotchas>

  <bounds will="execute chosen completion option, handle worktree cleanup, inform user of result" wont="proceed with failing tests, force-push without request, auto-merge PRs"/>

  <handoff next="/sc:git /sc:ship"/>
</component>
