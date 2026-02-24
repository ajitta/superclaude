# Session: v2.1.20-v2.1.33 Alignment

**Date**: 2026-02-06
**Commit**: `d174e60` (pushed to `origin/master`)
**Duration**: ~30 min active
**Type**: Documentation alignment (zero Python changes)

## What Was Done
- Full alignment of SuperClaude docs with Claude Code v2.1.20–v2.1.33
- 26 files changed (167+/17-), 225/225 tests pass
- FLAGS.md bumped to 2.1.33+, hooks.json schema to 2.1.33
- All 19 agents got `memory: user` frontmatter
- 3 new hook events: Setup, TeammateIdle, TaskCompleted
- 15 new cc_features entries in FLAGS.md
- Task(agent_type) allowlist pattern documented
- Skills README updated with --add-dir discovery + 2% budget

## Key Decisions (User)
- Scope: Full v2.1.20-v2.1.33 catchup (not just v2.1.33)
- Agent memory: `memory: user` on ALL 19 agents
- Agent model: Omit (inherit is default)
- Agent tools: Omit (no restrictions, only pm-agent would benefit from Task(x))
- Experimental: Document TeammateIdle/TaskCompleted with [experimental] tag
- v2.0.x: No backfill (v2.1.x only)

## Open Items
1. hooks.json TeammateIdle/TaskCompleted use echo placeholder commands
2. Remove [experimental] tags when agent teams reaches GA
3. CLAUDE.md may need sync (references "21 agent definitions")
4. Consider more frequent alignment (~every 5 versions)

## Process Notes
- Brainstorm→Spec→Implement pipeline worked well
- Parallel Explore + deep-research agents saved discovery time
- Batch editing 19 agents was efficient with the pattern approach
- All edits were read-first, pattern-confirmed
