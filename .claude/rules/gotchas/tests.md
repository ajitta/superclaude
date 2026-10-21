---
paths: ["tests/**"]
---

# Project Gotchas — Tests
# Last reviewed: 2026-10-21
# Traps in writing tests: sandboxes, env anchors, isolation from the developer's machine.

- test-anchor-env: Resolver tests must `monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))` — `project_root()` reads the env first, so `chdir` alone writes into the real repo or `~/.claude`. For `claude_base()` also `mkdir <tmp>/.claude/superclaude`, else it falls back to the developer's home.
- sandbox-escapes-home: A test that fakes `$HOME` puts the project inside it (`home / "project"`). The install walk stops at `$HOME`; a project beside the fake home climbs out to the developer's real `~/.claude` (Windows pytest temp is under the profile). Hit 2026-10-21, c05[user]
