---
name: finishing-a-development-branch
description: |
  Complete development work with structured options for merge, PR, or cleanup.
  Use when implementation is complete and all tests pass. Presents options and
  guides branch completion. Involves git operations.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

## Purpose

Guide branch completion by verifying tests, presenting options, executing the chosen path, and cleaning up.

## Workflow

1. **Run the test suite.** Tests should pass before presenting options. If they fail, report failures and pause.
2. **Detect the base branch.** Check whether the repo uses `main` or `master`, and confirm with the user before proceeding.
3. **Present four options:**
   - Merge locally into base branch
   - Push and create a PR
   - Keep the branch as-is for later
   - Discard the branch (requires typed "discard" confirmation)
4. **Execute the chosen option.** For merges, re-run tests after merging. For PRs, use `gh pr create` and report the URL. For discard, wait for explicit confirmation before deleting.
5. **Clean up worktree if applicable.** Remove worktrees for merge and discard options; preserve them for PR and keep-as-is options.

## Constraints

- Do not proceed past step 1 with failing tests.
- Do not skip typed confirmation for the discard option.
- Do not force-push without an explicit user request.
- Do not auto-merge a PR — the review process is separate.

## Completion

The chosen option has been executed, any associated worktree has been handled, and the user has been informed of the result.

## Next

Pairs with **using-git-worktrees** for worktree cleanup. Use `/sc:ship` to streamline merge and cleanup.
