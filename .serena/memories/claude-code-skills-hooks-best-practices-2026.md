# Claude Code Skills, Hooks & Plugins Best Practices (Feb 2026)

## Research Date: 2026-02-04

## 1. Skills System Best Practices

### context: fork vs inline
- `context: fork` runs skill in isolated subagent context - results return summarized
- Use fork when: skill reads many files, generates verbose output, does investigation
- Use inline (default) when: skill provides background knowledge/guidelines
- Fork only makes sense with explicit task instructions; guidelines-only skills should stay inline
- Fork prevents context pollution from large outputs

### agent field
- Only meaningful when `context: fork` is set
- Values: `Explore`, `Plan`, `Bash`, or custom agent names
- Explore = read-only investigation; Plan = architectural planning
- Custom agents defined in `.claude/agents/` directory

### allowed-tools patterns
- Wildcard patterns: `Bash(git *)`, `Bash(npm *)`, `Bash(python:)`
- Read-only: `Read, Grep, Glob`
- MCP tools: `ServerName:tool_name` format (e.g., `GitHub:create_issue`)
- Start restrictive, add tools as needed

### Progressive Disclosure
- SKILL.md: 1,500-2,000 words max (core concepts)
- references/: Detailed docs (loaded on demand)
- examples/: Working examples (loaded on demand)
- scripts/: Utility scripts (executed, output only)
- Only SKILL.md name+description loaded at startup (~30-50 tokens each)

## 2. Hooks System Best Practices

### Event Priority
1. UserPromptSubmit - validate/enrich before processing
2. PreToolUse - prevent dangerous operations
3. PostToolUse - validate results, format, lint
4. Stop - ensure task completion
5. SessionStart - environment setup, context loading

### Key Patterns (2026)
- "Block-at-Submit" > "Block-at-Write" - let agent complete plan, validate at end
- Input modification > blocking - use `updatedInput` to correct silently
- `once: true` - performance optimization, run only once per event
- Prompt-based hooks for complex logic, command hooks for deterministic checks

### Exit Codes
- 0: Success, continue
- 2: Block operation (PreToolUse/PermissionRequest only)
- Other: Non-blocking warning

### Environment Variables
- `$CLAUDE_PROJECT_DIR` - Project root
- `$CLAUDE_PLUGIN_ROOT` - Plugin directory (portability)
- `$CLAUDE_ENV_FILE` - SessionStart env persistence

### Hook Formats
- Plugin: `hooks/hooks.json` with wrapper
- Settings: Direct format in `.claude/settings.json`
- Frontmatter: Inline in skills/agents (PreToolUse, PostToolUse, Stop only)

## 3. Plugin System
- Bundles commands + skills + agents + hooks + MCP
- Plugin hooks merge with user hooks, run in parallel
- Use `${CLAUDE_PLUGIN_ROOT}` for portable paths
- Auto-discovery for commands/agents/skills

## 4. Token Efficiency
1. Move specialized instructions from CLAUDE.md to skills
2. Keep CLAUDE.md under ~500 lines
3. Use `context: fork` for investigation tasks
4. Delegate verbose operations to subagents
5. Use hooks to preprocess/filter data
6. Progressive disclosure in skills
7. /compact regularly
8. Commit, clear, repeat workflow

## 5. MCP Integration in Skills
- MCP provides connection; skill teaches how to use it
- Reference MCP tools with `ServerName:tool_name` format
- Skills can include step-by-step MCP workflows

## Sources
- code.claude.com/docs/en/skills
- code.claude.com/docs/en/hooks
- code.claude.com/docs/en/costs
- github.com/anthropics/claude-code (plugin-dev skills)
- github.com/disler/claude-code-hooks-mastery
- platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
