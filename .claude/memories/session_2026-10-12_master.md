branch: master @2f3e6754

# Session 2026-10-12 — master

## Where it stands
- master @2f3e6754 pushed to origin; no CI run for the last two commits (a push alone runs none)
  - c5818d25 fix(agents): verifier frontmatter valid YAML
  - 2f3e6754 fix(loader): skip harness-inserted turns in context_loader
- Local suite before commit: 3000 passed / 1 skipped, `make lint` clean, `tests/unit/scripts` 149 passed
- v4.26.0 released earlier today (stable 20e3e108); merged branches deleted; open lines: feature/authoring-skill (worktree), fix/plain-language-structure (held)
- Earlier today: serena-removal merged @bef88d5b; branch-side detail in `session_2026-10-12_feature-serena-removal.md`

## Decided (earlier today)
- /sc:save + /sc:load across worktrees and branches (Phase G, `docs/features/serena-removal/05g-plan-branch-records.md`): one add-only record `session_[date]_[branch-slug].md`; `pm_context.md` the only fixed name; auto memory is one folder shared by all worktrees → name the branch in entries, Edit single MEMORY.md lines

## verifier agent never loaded (fixed c5818d25)
- `src/superclaude/agents/verifier.md:3` unquoted `description:` held `gate: test` → invalid YAML → Claude Code silently dropped the agent (absent from the session agent list since 3362816e, 2026-10-07)
- Only shipped file of 62 with frontmatter that fails `yaml.safe_load`
- Tests missed it: `tests/unit/md_helpers.py::parse_frontmatter` splits lines on `:`, never parses YAML

## Harness turns triggered the loader (fixed 2f3e6754)
- CC 2.1.296 fires UserPromptSubmit for sub-agent hand-backs, task notifications and the /goal activation notice; `prompt` holds that text, so filenames/flag names in a report injected modes, RULES modules and directives (root-cause-analyst investigation, transcript L240-242 of session f0e7af4b)
- The hook prompt for a hand-back starts with `<agent-message `; transcript display text "Another Claude session sent a message:" is not what the hook receives
- Fix: `_is_harness_turn` → empty prompt when `source == "system"` (in CC schema, not sent by 2.1.296) or prompt starts with `<agent-message `, `<task-notification>`, `A session-scoped Stop hook is now active`
- /goal notice quotes the condition without its slash, so `sc:implement --plan <file>` read as the global --plan (wait-for-approval) directive
- Verified live for the hand-back (probe report with 3 trigger words → nothing injected, none in the dedup cache); /goal prefix tested only by unit/subprocess tests, not live
- Left open by decision (cannot stall work): Stop-hook feedback turns, auto-continuation ("Goal set: …"), backtick-quoted mode/RULES triggers (`check_triggers` scans the raw prompt, `context_loader.py:~1121`)
- Accepted risk: prefixes are undocumented CC strings; a format change silently re-opens the leak

## --verbose-context assessment (no decision yet)
- Reaches only 4 files today: Tier 0 Playwright/DevTools/BUSINESS_SYMBOLS, Tier 1 Tavily; modes and RULES_* are always full
- Duplicates env `CLAUDE_CONTEXT_USE_INSTRUCTIONS=0`
- Dedup is keyed by file path, not tier → works only on the prompt that first triggers a file; mid-session it is a no-op
- Injected text persists for the session (until /clear or compaction), so the cost is once per session — valid use: front-load full docs at session start
- Options offered: (1) drop only the FLAGS.md line, keep code; (2) keep and reword FLAGS.md to "full .md for MCP docs triggered in the same prompt; persists for the session"; full removal conflicts with `fork-unknown-users`

## Next actions
- [ ] `make sync-local` so the installed `.claude/agents/verifier.md` gets the fix; confirm `verifier` in a new session's agent list
- [ ] Optional CI: `gh workflow run Tests --ref master`
- [ ] Decide --verbose-context (options above)
- [ ] Optional: regression test running `yaml.safe_load` over every shipped frontmatter block (proposed, not asked)
- [ ] Stale local install file `.claude/superclaude/mcp/MCP_Serena.md` (left after serena removal)
- [ ] Global uv tool `superclaude v4.25.0` predates the loader fix; a session whose PATH finds it first runs the old loader
- [ ] Switch the harness check to `source == "system"` only once CC sends the field
- [x] CHANGELOG lines from serena-removal "Release note" — shipped in 4.26.0
- [x] Delete local `feature/serena-removal` — done after the 4.26.0 release
- [ ] authoring-skill: /sc:plan for the sc-author skill (worktree has an untracked `.serena/memories/session_2026-10-10_authoring-skill-design.md`)
- [ ] structured-output-style issue 01: needs name/scope/notation decisions
