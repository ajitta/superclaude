# SuperClaude — Project Index

> **Version**: 4.3.0+ajitta | **Python**: >=3.10 | **Build**: hatchling | **License**: MIT
> **Generated**: 2026-03-05 | **Latest commit**: 20adbfb

## What It Is

A **dual-purpose** project: (1) a pytest plugin + CLI tool providing PM Agent patterns (confidence checking, self-check, reflexion, parallel execution), and (2) a content framework of markdown files installed into `~/.claude/` to configure Claude Code behavior.

## Entry Points

| Entry | Path | Purpose |
|-------|------|---------|
| CLI | `src/superclaude/cli/main.py` | `superclaude` command (Click) |
| Pytest plugin | `src/superclaude/pytest_plugin.py` | Auto-loaded via `pytest11` entry point |
| Package init | `src/superclaude/__init__.py` | Exports: ConfidenceChecker, SelfCheckProtocol, ReflexionPattern |

## Source Layout (`src/superclaude/`)

| Directory | Files | Purpose |
|-----------|-------|---------|
| `cli/` | 9 | CLI commands: install, uninstall, update, mcp, doctor, agents, skills, version |
| `pm_agent/` | 5 | Core patterns: confidence, self_check, reflexion, token_budget, task_cleanup |
| `execution/` | 3 | Parallel exec, reflection, self-correction |
| `hooks/` | 3+json | Hook tracker, inline hooks (YAML frontmatter), MCP fallback |
| `scripts/` | 7 | Utilities: session_init, context_loader, token_estimator, skill_activator, etc. |
| `utils/` | 1 | Shared utilities (atomic_write_json) |
| `commands/` | 31 | Slash command markdown files (sc:analyze, sc:implement, etc.) |
| `agents/` | 20+README | Agent definitions (system-architect, python-expert, etc.) |
| `skills/` | 3 | Skills: confidence-check, simplicity-coach, ship (each has SKILL.md) |
| `modes/` | 7+README+cfg | Behavioral modes: Brainstorming, Business Panel, DeepResearch, etc. |
| `mcp/` | 7+README | MCP server docs: Context7, Sequential, Playwright, Tavily, Serena, etc. |
| `core/` | 4 | FLAGS.md, PRINCIPLES.md, RULES.md, BUSINESS_SYMBOLS.md |

## Key Modules

| Module | Class/Function | Purpose |
|--------|---------------|---------|
| `pm_agent/confidence.py` | `ConfidenceChecker` | Pre-execution gate (>=90% proceed, <70% stop) |
| `pm_agent/self_check.py` | `SelfCheckProtocol` | Post-implementation validation |
| `pm_agent/reflexion.py` | `ReflexionPattern` | Cross-session error learning (JSONL) |
| `pm_agent/token_budget.py` | `TokenBudgetManager` | Token allocation (simple/medium/complex) |
| `pm_agent/task_cleanup.py` | `TaskCleanupManager` | Stale task removal (24h threshold) |
| `execution/parallel.py` | `ParallelExecutor` | Wave-Checkpoint-Wave pattern |
| `hooks/inline_hooks.py` | — | YAML frontmatter parser for skills/agents |
| `hooks/hook_tracker.py` | — | once:true session tracking (24h TTL) |
| `cli/install_paths.py` | `COMPONENTS` | Content installation path mapping |
| `cli/install_settings.py` | — | Settings/hooks merge into settings.json |
| `scripts/context_loader.py` | `TRIGGER_MAP` | Context loading with flag detection, hybrid injection |

## Content Installation Map

```
commands/  →  ~/.claude/commands/sc/       (31 slash commands)
agents/    →  ~/.claude/agents/            (20 agent definitions)
skills/    →  ~/.claude/skills/            (3 skill implementations)
core/      →  ~/.claude/superclaude/core/  (FLAGS, PRINCIPLES, RULES)
modes/     →  ~/.claude/superclaude/modes/ (7 behavioral modes)
mcp/       →  ~/.claude/superclaude/mcp/   (7 MCP server docs)
```

## Slash Commands (31)

| Category | Commands |
|----------|----------|
| Core | sc, help, recommend |
| Analysis | analyze, explain, troubleshoot |
| Implementation | implement, improve, cleanup |
| Planning | brainstorm, design, estimate, workflow, spawn |
| Documentation | document, index, index-repo |
| Quality | test, build, reflect |
| Research | research, spec-panel, business-panel |
| Session | load, save, agent, task |
| Git | git |
| Tools | select-tool, pm |

## Agents (20)

| Category | Agents |
|----------|--------|
| Architecture | backend-architect, devops-architect, frontend-architect, system-architect |
| Quality | quality-engineer, security-engineer, performance-engineer |
| Development | python-expert, refactoring-expert, requirements-analyst |
| Analysis | root-cause-analyst, deep-research-agent |
| Education | learning-guide, socratic-mentor, technical-writer |
| Workflow | pm-agent, repo-index, self-review, business-panel-experts, simplicity-guide |

## Modes (7+2)

| Mode | Trigger | Purpose |
|------|---------|---------|
| Brainstorming | --brainstorm | Collaborative discovery |
| DeepResearch | --research | Evidence-based investigation |
| Orchestration | --orchestrate | Multi-tool optimization |
| TaskManagement | --task-manage | Delegation, progressive enhancement |
| TokenEfficiency | --uc | Symbol communication, 30-50% reduction |
| Introspection | --introspect | Meta-cognition, pattern detection |
| BusinessPanel | --business-panel | Multi-expert analysis |
| ResearchConfig | (internal) | Research hop/credibility settings |

## MCP Servers (7)

| Server | Flag | Purpose |
|--------|------|---------|
| Context7 | --c7 | Official docs lookup |
| Sequential | --seq | Extended thinking |
| Serena | --serena | Symbol ops, project memory |
| Tavily | --tavily | Web search |
| Morphllm | --morph | Bulk pattern edits |
| Magic | --magic | UI components (21st.dev) |
| Playwright | --play | Browser automation |
| Chrome-DevTools | --perf | Performance debug |

## Dependencies

**Runtime**: pytest>=7.0, click>=8.0, rich>=13.0, pyyaml>=6.0
**Dev**: pytest-cov, pytest-benchmark, pytest-asyncio, scipy, black, ruff, mypy

## Tests

| Directory | Files | Focus |
|-----------|-------|-------|
| `tests/unit/` | 16 | confidence, self_check, token_budget, parallel, hooks, CLI, agents, reflexion, mcp_fallback, context_loader, install_settings, skills, triggers |
| `tests/integration/` | 2 | pytest_plugin, cross_directory_refs |

**908 tests passing, 28 skipped** | **Markers**: unit, integration, confidence_check, self_check, reflexion, complexity, hallucination, performance

## Dev Commands

```bash
make install    # uv pip install -e ".[dev]"
make deploy     # uv tool install --editable (global)
make test       # uv run pytest
make lint       # ruff check
make format     # ruff format
make doctor     # Health check
make clean      # Remove artifacts
```

## Git

Branch model: `master` <- `integration` <- `feature/*`, `fix/*`, `docs/*`
Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

---
*Token cost: ~2.5K (vs ~58K full read) — 94% reduction*
