# Code Style & Conventions

## Python
- Python ≥ 3.10
- ruff (line-length 88, ignores E501)
- Run `make format` before committing
- Type hints used in public interfaces
- Minimal comments — only when WHY is non-obvious

## Content Files (Markdown)
- Component bodies use XML prose format (defined in `.claude/rules/xml-prose-format.md`)
- Single root XML wrapper tag per component
- Section tags: `snake_case`
- Max nesting depth: 3 levels
- No markdown headers (`#`) in component bodies (only in `<example>` when showing real artifacts)
- Declarative third-person voice ("Claude does X") — never hedging ("should", "might")
- Compact table separators: `|---|---|` (no padding)
- `<does>`/`<never>`/`<fallback>` for bounds sub-tags (not `<should>`/`<avoid>`)

## Commit Conventions
- Prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Branch: `master` ← `integration` ← `feature/*`, `fix/*`, `docs/*`

## File Organization
- `src/superclaude/agents/` — agent .md files
- `src/superclaude/commands/` — command .md files
- `src/superclaude/modes/` — mode .md files
- `src/superclaude/skills/` — skill directories
- `src/superclaude/mcp/` — MCP server docs
- `src/superclaude/core/` — FLAGS.md, PRINCIPLES.md, RULES.md
- `src/superclaude/hooks/` — hook Python scripts
- Authoring rules: `.claude/rules/` (agent, command, skill, mode — auto-loaded by CC)
