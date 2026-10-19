# docs/

Working artifacts for superclaude development. **Not** user-facing product docs.

User-facing documentation is the framework content itself — its SSOT lives in `src/superclaude/`:

- Commands — `src/superclaude/commands/README.md`
- Agents — `src/superclaude/agents/README.md`
- Modes / Skills / MCP / Core — `src/superclaude/{modes,skills,mcp}/` and `src/superclaude/core/`
- Architecture — `src/superclaude/ARCHITECTURE.md`
- Dev setup, test — repo-root `AGENTS.md` (imported by `CLAUDE.md`); make targets — `make help`

## Layout

| Dir | Holds |
|---|---|
| `adr/` | Architecture decision records |
| `agents/` | Conventions for coding agents: issue tracker, triage labels, domain docs |
| `features/` | Phased feature folders (README + numbered phase docs), the default for multi-doc work |
| `plans/` | Implementation plans for in-flight work |
| `research/` | External research, evidence gathering |
| `analysis/` | Codebase analysis, retrospectives |
| `reports/` | Living reference docs (`UPPER_SNAKE`, no date) |
| `experiments/` | A/B harness outputs |
| `codex/` | Working guides for improving and verifying `src/superclaude/` (the component inventory lives there) |
| `archive/` | Finished or no-longer-valid docs + legacy upstream user-docs — see `archive/README.md` |

A `specs/` directory is created by the first standalone discovery or design doc (`RULES_DOCS.md` slug resolution) and is absent until then.

## Why no user guide here

`docs/user-guide/`, `docs/reference/`, `docs/getting-started/`, `docs/developer-guide/` were inherited from upstream SuperClaude. The fork diverged far enough that the prose contradicted the live SSOT (wrong command counts, retired flags, dead install paths). Archived 2026-05-15 to `docs/archive/legacy-userdocs/` rather than maintained — duplicating SSOT prose only recreates the divergence trap.
