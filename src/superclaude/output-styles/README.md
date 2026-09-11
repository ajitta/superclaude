# SuperClaude Output Styles

Claude Code output styles — Markdown files with YAML frontmatter that replace the tone and format instructions in Claude Code's system prompt for every response. Read natively by Claude Code, not by SuperClaude's own loaders.

## Content Delivery

Installed to `<scope>/output-styles/` (`~/.claude/output-styles/` for user scope, `./.claude/output-styles/` for project and local scope), the directory Claude Code scans. The directory is shared with the user's own styles: install writes only the shipped files, uninstall removes only those filenames (so a user file that happens to share a shipped name is removed too), and a local-scope install git-excludes them file by file.

Installing a style does not activate it. The user picks it once via `/config` → **Output style**, which writes `"outputStyle": "<name>"` to `.claude/settings.local.json`, or sets that key in any settings file. Claude Code reads style files at startup — restart after install.

## Available Styles

| Style | `name` | Purpose |
|---|---|---|
| plain-language.md | Plain Language | Direct, specific prose in the user's language, without AI mannerisms or decorative structure |

## Authoring Rules

See `.claude/rules/output-style-authoring.md`.

Validation: `uv run pytest tests/unit/test_output_style_structure.py -v`

## Related

- Claude Code docs: https://code.claude.com/docs/en/output-styles
- `modes/` — mindset overlays injected on demand; a style applies to every response instead
