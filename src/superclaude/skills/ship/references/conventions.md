# Ship Conventions Reference

## Branch Validation

- master/main: WARN — suggest creating feature branch first
- feature/*|fix/*|docs/*|refactor/*|chore/*: OK
- Other: WARN — suggest conventional branch name

## Conventional Commit Format

- feat: new feature
- fix: bug fix
- docs: documentation only
- refactor: code restructuring
- test: adding/updating tests
- chore: maintenance, deps, config

Auto-detected from diff content; user approves final message.

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
- credentials.json, *secret*, *token* (credentials)
- *.log, *.tmp (transient)
- node_modules/, __pycache__/, .venv/ (generated)
- User-specified --exclude patterns (glob syntax)
