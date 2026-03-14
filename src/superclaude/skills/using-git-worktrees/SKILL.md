---
name: using-git-worktrees
description: |
  Create isolated git worktrees for feature work and plan execution. Use when
  starting work that needs isolation from current workspace. Sets up worktree
  with smart directory selection and safety verification.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# Using Git Worktrees

Announce: "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Overview

Git worktrees provide isolated workspaces that share the same repository history. This
skill handles systematic directory selection, safety verification, and workspace setup
so that feature work and plan execution happen in a clean, independent environment
without disrupting the current working tree.

Core responsibilities:
- Select or create a worktree directory following a strict priority order
- Verify the directory is gitignored before any worktree is created
- Set up the worktree with project dependencies and a passing test baseline

## Directory Selection Process

Follow this priority order exactly. Stop at the first match.

### Priority 1: Check for existing worktree directories

Look for these directories relative to the repository root:

```
.worktrees/       # local hidden directory (most common)
worktrees/        # local visible directory
```

If either exists and is already gitignored, use it.

### Priority 2: Check CLAUDE.md for a preference

Search the project's `CLAUDE.md` for a worktree directory preference. Look for
keys like `worktree-dir`, `worktrees-path`, or similar configuration. If found,
use the specified path.

### Priority 3: Ask the user

Present two options:

| Option | Path | When to use |
|--------|------|-------------|
| Local hidden | `.worktrees/` in repo root | Single-project work, keeps worktrees near code |
| Global shared | `~/.config/superpowers/worktrees/` | Multi-project work, central location |

Wait for the user to choose before proceeding.

## Safety Verification

**MUST verify the worktree directory is gitignored before creating any worktree.**

Steps:

1. Run `git check-ignore -q <worktree-dir>` to test if the directory is ignored
2. If the directory IS ignored: proceed to creation
3. If the directory is NOT ignored:
   a. Add the directory pattern to `.gitignore` (e.g., `.worktrees/`)
   b. Stage and commit the `.gitignore` change with message: `chore: gitignore worktree directory`
   c. Confirm the ignore rule is active with `git check-ignore -q` again
   d. Proceed to creation

Never skip this step. An unignored worktree directory will pollute `git status` with
thousands of untracked files.

## Creation Steps

Once the directory is selected and verified:

### 1. Detect project name

Derive the worktree name from the branch name or task identifier:

```bash
# Example: feature/add-auth → add-auth
BRANCH_NAME="feature/add-auth"
WORKTREE_NAME="${BRANCH_NAME##*/}"
```

### 2. Create the worktree

```bash
git worktree add <worktree-dir>/<worktree-name> -b <branch-name>
```

If the branch already exists, omit `-b`:

```bash
git worktree add <worktree-dir>/<worktree-name> <branch-name>
```

### 3. Run project setup

Auto-detect the project type and install dependencies:

| Indicator file | Setup command |
|---------------|---------------|
| `package-lock.json` | `npm ci` |
| `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
| `yarn.lock` | `yarn install --frozen-lockfile` |
| `pyproject.toml` | `uv sync` or `pip install -e .` |
| `Cargo.toml` | `cargo build` |
| `go.mod` | `go mod download` |
| `Gemfile.lock` | `bundle install` |

Run the matching command inside the new worktree directory.

### 4. Verify clean baseline

Run the project's test suite inside the worktree to confirm a passing state:

```bash
cd <worktree-path>
# Run tests appropriate to the project type
```

If tests fail, stop and report the failures. Do not proceed with feature work on a
broken baseline.

### 5. Report location

Print the worktree path and branch name so the caller knows where to work:

```
Worktree ready:
  Path:   <absolute-path-to-worktree>
  Branch: <branch-name>
  Status: Tests passing, dependencies installed
```

## Quick Reference

| Action | Command |
|--------|---------|
| List worktrees | `git worktree list` |
| Remove worktree | `git worktree remove <path>` |
| Prune stale entries | `git worktree prune` |
| Switch to worktree | `cd <worktree-path>` |

## Common Mistakes

- **Skipping ignore verification** — leads to thousands of untracked file warnings in the main tree
- **Assuming a worktree location** — always follow the priority order; never hardcode a path
- **Proceeding with failing tests** — a broken baseline means bugs will be invisible in the feature branch

## Red Flags

Never allow any of these situations:

- An unignored worktree directory in the repository
- Skipping the baseline test verification step
- Proceeding with feature work when baseline tests fail
- Creating a worktree on a branch that already has an active worktree

## Integration

- **Called by**: brainstorming, executing-plans (when isolation is needed for parallel work)
- **Pairs with**: finishing-a-development-branch (to merge and clean up the worktree after work is complete)
- **Complements**: dispatching-parallel-agents (each agent can work in its own worktree)
