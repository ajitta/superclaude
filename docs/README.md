# docs/

Working artifacts for SuperClaude development. **Not** user-facing product docs.

User-facing documentation is the framework content itself — its SSOT lives in `src/superclaude/`:

- Commands — `src/superclaude/commands/README.md`
- Agents — `src/superclaude/agents/README.md`
- Modes / Skills / MCP / Core — `src/superclaude/{modes,skills,mcp}/` and `src/superclaude/core/`
- Architecture — `src/superclaude/ARCHITECTURE.md`
- Dev setup, test, make targets — repo-root `CLAUDE.md`

## Layout

| Dir | Holds |
|---|---|
| `specs/` | Discovery + design docs for in-flight work |
| `plans/` | Implementation plans for in-flight work |
| `research/` | External research, evidence gathering |
| `analysis/` | Codebase analysis, retrospectives |
| `reports/` | Living reference docs (`UPPER_SNAKE`, no date) |
| `guides/` | Standalone how-to guides |
| `experiments/` | A/B harness outputs |
| `troubleshooting/` | Active install/runtime troubleshooting |
| `archive/` | Terminal-status docs + legacy upstream user-docs — see `archive/README.md` |

## Why no user guide here

`docs/user-guide/`, `docs/reference/`, `docs/getting-started/`, `docs/developer-guide/` were inherited from upstream SuperClaude. The fork diverged far enough that the prose contradicted the live SSOT (wrong command counts, retired flags, dead install paths). Archived 2026-05-15 to `docs/archive/legacy-userdocs/` rather than maintained — duplicating SSOT prose only recreates the divergence trap.
