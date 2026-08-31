# UI Guide — `superclaude` CLI output

> This project has exactly one human-facing UI: the text the `superclaude`
> command prints in a terminal. There is no web, GUI, or TUI surface.
>
> The framework's *other* interface — markdown read by the model — is governed
> by `.claude/rules/xml-prose-format.md` and the per-type authoring rules; those
> are the SSOT and are not restated here.

## Design Tokens

The visual system is a glyph vocabulary plus fixed indentation. No color, no
ANSI styling, no rendering library: output is plain `click.echo`.

### Status glyphs

| Glyph | Means | Seen in |
|---|---|---|
| ✅ | present / succeeded / complete | `install --list-all`, `doctor` |
| ⬜ | absent, and that is a normal state | `--list`, `mcp --list` |
| ⏭️ | skipped — nothing to do, not a failure | uninstall + inventory reports |
| ⚠️ | degraded, continuing anyway | missing install, partial health |
| ❌ | failed or aborted; pairs with `sys.exit(1)` | install/skill/agent errors |
| 💡 | next step the user probably wants | after install, after `--list` |
| ℹ️ | note attached to the line above | `mcp` server notes |
| 🔑 | a secret is about to be requested | MCP API-key prompt |

### Command banners

One banner as the first line of a command, verb-shaped, with the scope in
parentheses: `📦 Installing SuperClaude components (scope: user)...`

| Glyph | Command family |
|---|---|
| 📦 | install (components, skills) |
| 🗑️ | uninstall |
| 🔄 | update |
| 🔌 | mcp |
| 🔍 | inspect — dry-run, drift check |
| 📋 | listing (components, commands, agents, skills) |
| 📊 | measurement (token estimates) |

Reuse this table. A new subcommand picks an existing glyph rather than
introducing a ninth one.

### Layout

- Item lines: 3-space indent.
- Detail under an item: 6 spaces then `└─ `.
- Alignment comes from f-string field widths, not a table library — 40 for
  component descriptions, 25 for agent/skill names, 20 for command names.
- Section rule inside a long list: `━━ <heading> ━━`.
- Box-drawing (`┌─┬─┐`) is reserved for the one real matrix, `mcp --list`.
- Totals go after a blank line: `Total: <n> available, <m> installed`.

## Component Conventions

**Output skeleton** — banner → blank line → body → summary/total → optional 💡
tip. `--list*` paths print and return before any mutation, so listing is always
safe to pipe.

**Prompts.**

- `click.confirm(..., default=...)` — the default is always explicit, and the
  safe answer is the default (`Overwrite already-installed files?` defaults to
  no; `Proceed with install?` defaults to yes only after a preview).
- Multi-step flows label progress as `Step N/5:` so an interrupted wizard is
  locatable.
- Secrets use `click.prompt(..., hide_input=True)` and are never echoed back;
  an already-set variable is reported by name only (`✅ Using TAVILY_API_KEY
  from environment`).
- **Never prompt where stdin cannot answer.** `_stdin_can_answer()` in
  `cli/main.py` gates this, and it is deliberately not `isatty()` alone —
  Windows `NUL` reports as a terminal.

**Failure.** Print one `❌` line saying what failed, then `sys.exit(1)`. Prefer
`err=True` for new error output so that listing output stays pipeable; today
this is inconsistent — `install_mcp.py` uses it, most of `main.py` does not.

## Accessibility Baseline

- **A glyph never carries meaning alone.** Always glyph + word: `✅ installed` /
  `⬜ not installed`. A console that drops emoji, a screen reader, or a legacy
  Windows code page must still leave the line readable — nothing in the CLI
  reconfigures stdout encoding, so the word is the real signal.
- **Non-TTY safe.** No spinners, progress bars, cursor control, or line
  rewriting; `superclaude install > install.log` must read exactly as the
  terminal did.
- **Headless safe.** Every interactive path is reachable only behind the stdin
  gate above; `claude -p` and CI runs must never block on a prompt.
- **Secrets stay hidden** on input and in echoes.

## Forbidden UI Patterns

| Pattern | Reason |
|---|---|
| Emoji-only status column | Breaks the moment the glyph does not render |
| ANSI color as the only signal | Lost in logs and pipes; the CLI has no color layer at all |
| Introducing `rich` rendering for one command | Two renderers on one surface; `rich` is currently declared but unused (see `docs/PRD.md` open questions) |
| Spinner / progress animation | Corrupts redirected output |
| A prompt without the stdin gate | Hangs headless sessions |
| Echoing a secret or a full environment value | Leaks into scrollback and logs |
| A new banner glyph per subcommand | The glyph table is the vocabulary |
| Raw traceback as the user-facing error | Print the failure, exit 1; the traceback belongs in a bug report |

## Example

`install --list-all` in `src/superclaude/cli/main.py:196` is the reference
implementation: banner with scope, glyph + width-aligned description + count,
`└─` detail line, and a second `└─` only when there is drift to report.

```text
📋 SuperClaude Components (scope: user):

   ✅ Slash commands                           [36/36]
      └─ ~/.claude/commands/sc
   ✅ Agent definitions                        [23/23]
      └─ ~/.claude/agents
   ⬜ Hooks registered in settings             [0/14]
      └─ ~/.claude/settings.json
      └─ 14 missing
```

Captured 2026-08-31, paths abbreviated, and the last row edited to show the
drift line. Counts move with the source tree — run
`uv run superclaude install --list-all` for current figures.
