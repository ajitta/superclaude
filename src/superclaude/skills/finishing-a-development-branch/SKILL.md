---
name: finishing-a-development-branch
description: |
  Complete development work with structured options for merge, PR, or cleanup.
  Use when implementation is complete and all tests pass. Presents options and
  guides branch completion. Involves git operations.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# Finishing a Development Branch

## Overview

Guide branch completion by presenting clear options and handling the chosen workflow. The core principle is straightforward: verify tests pass, present the available options, execute the selected choice, and clean up afterward.

> I'm using the finishing-a-development-branch skill to complete this work.

## The Process

### Step 1: Verify Tests

Run the project's full test suite before anything else.

- **If tests fail**: Display the failures clearly and stop. Do not proceed with any branch finishing operation until all tests pass.
- **If tests pass**: Continue to the next step.

This gate is non-negotiable. A branch with failing tests is not ready to finish.

### Step 2: Determine Base Branch

Identify the target branch for merge or PR operations.

1. Check whether the repository uses `main` or `master` as the primary branch.
2. Inspect the current branch's upstream tracking configuration.
3. Confirm the base branch with the user before proceeding.

Do not assume the base branch. Always verify.

### Step 3: Present Options

Offer exactly four choices. Do not add alternatives or leave the question open-ended.

| Option | Description |
|--------|-------------|
| **1. Merge locally** | Merge the feature branch into base on the local machine |
| **2. Push and create PR** | Push the branch to remote and open a pull request |
| **3. Keep as-is** | Leave the branch untouched for continued work later |
| **4. Discard** | Delete the branch and all associated work |

Ask the user to pick one. Wait for their response.

### Step 4: Execute the Chosen Option

#### Option 1: Merge Locally

1. Switch to the base branch.
2. Pull the latest changes from remote.
3. Merge the feature branch into base.
4. Run the test suite again to confirm nothing broke during merge.
5. Delete the feature branch after successful verification.

If the merge produces conflicts, show them and let the user resolve before continuing.

#### Option 2: Push and Create PR

1. Push the feature branch to remote with the `-u` flag to set upstream tracking.
2. Create a pull request using `gh pr create` with a structured body:
   - Summary section describing what the branch accomplishes.
   - Test plan section outlining how changes were validated.
3. Report the PR URL back to the user.

Do not merge the PR automatically. The review process happens separately.

#### Option 3: Keep As-Is

1. Report the current branch name and its status.
2. Preserve the worktree if one exists.
3. Summarize what remains on the branch (uncommitted changes, unpushed commits).

No destructive actions. Simply inform and exit.

#### Option 4: Discard

This is a destructive operation requiring explicit confirmation.

1. Ask the user to type the word "discard" to confirm.
2. Do not proceed until the exact confirmation is received.
3. Once confirmed, delete the local branch.
4. If a remote tracking branch exists, delete it as well.

Never skip the confirmation step regardless of context.

### Step 5: Cleanup Worktree

Handle worktree state based on the selected option.

| Option | Worktree Action |
|--------|-----------------|
| 1 (Merge) | Remove the worktree after successful merge |
| 2 (PR) | Remove the worktree after push completes |
| 3 (Keep) | Preserve the worktree in place |
| 4 (Discard) | Remove the worktree after branch deletion |

If no worktree is associated with the branch, skip this step.

## Quick Reference

| Option | Merges | Pushes | Keeps Worktree | Cleans Up |
|--------|--------|--------|----------------|-----------|
| 1. Merge locally | Yes | No | No | Yes |
| 2. Push + PR | No | Yes | No | Yes |
| 3. Keep as-is | No | No | Yes | No |
| 4. Discard | No | No | No | Yes |

## Common Mistakes

- **Skipping test verification**: Always run tests first. A passing suite is the entry requirement.
- **Asking open-ended questions**: Present exactly four options. Do not ask "what would you like to do?" without structure.
- **Auto-cleaning worktrees**: Only clean up worktrees for options 1, 2, and 4. Option 3 explicitly preserves them.
- **Omitting discard confirmation**: The typed "discard" confirmation is mandatory. Never bypass it.

## Red Flags

Never take these actions under any circumstance:

- Proceed with any finishing operation when tests are failing.
- Merge a branch without running the post-merge verification suite.
- Delete a branch or worktree without explicit user confirmation.
- Force-push to any branch during the finishing workflow.

## SuperClaude Integration

Git operations are handled natively through standard CLI tooling. This is a terminal skill with no handoff to subsequent workflows.
