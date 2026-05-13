# Ship Conventions Reference

## Branch Validation

- master/main: WARN — suggest make feature branch first
- feature/*|fix/*|docs/*|refactor/*|chore/*: OK
- Other: WARN — suggest conventional branch name

## Conventional Commit Format

- feat: new feature
- fix: bug fix
- docs: docs only
- refactor: code restructure
- test: add/update tests
- chore: maintenance, deps, config

Auto-detect from diff; user approve final message.

## PR Template

```markdown
## Summary
{1-3 bullet points from commit messages}

## Changes
{file list with change type indicators}

## Test plan
- [ ] {auto-generated from change types}
```

## Default Exclusions (never staged)

- .env, .env.* (secrets)
- credentials.json, *secret*, *token* (creds)
- *.log, *.tmp (transient)
- node_modules/, __pycache__/, .venv/ (generated)
- User --exclude patterns (glob syntax)