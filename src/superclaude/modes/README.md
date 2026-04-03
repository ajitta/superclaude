# SuperClaude Modes

Mindset overlays — situational cognitive frameworks that modify Claude's thinking, communication, and priorities.

## Content Delivery

Modes are activated on-demand by `context_loader.py` via flag/keyword detection (TRIGGER_MAP). They are **not** managed by Claude Code's native content system — no frontmatter required.

## Available Modes

| Mode | Flag | Mission |
|------|------|---------|
| Brainstorming | `--brainstorm` | Collaborative discovery for requirements exploration |
| Business Panel | `--business-panel` | Multi-expert business analysis with adaptive interaction |
| Deep Research | `--research` | Research mindset for systematic investigation |
| Introspection | `--introspect` | Meta-cognitive analysis and reasoning optimization |
| Orchestration | `--orchestrate` | Intelligent tool selection and resource efficiency |
| Task Management | `--task-manage` | Hierarchical task organization with persistent memory |
| Token Efficiency | `--token-efficient` / `--uc` | Symbol-enhanced communication for compressed clarity |

### Supporting Configuration

| File | Type | Purpose |
|------|------|---------|
| RESEARCH_CONFIG.md | `config` | Deep research operational parameters — depth profiles, confidence thresholds, tool routing |

**Note:** RESEARCH_CONFIG.md is **not** a mode. It provides operational settings for the research mode and is excluded from mode structure validation. It uses `type="config"`, not `type="mode"`.

## 4-Axis Structure

Every mode defines four axes:

| Axis | Tag | What It Controls |
|------|-----|------------------|
| Thinking | `<thinking>` | Cognitive principles — how to reason |
| Communication | `<communication>` | Expression style — how to present |
| Priorities | `<priorities>` | Trade-off guidance — what to optimize |
| Behaviors | `<behaviors>` | Action patterns — what to do differently |

Modes can be combined (e.g., `--research --uc` for compressed research output).

## Authoring Rules

See `.claude/rules/mode-authoring.md` for the complete authoring specification.

Validation: `uv run python -m pytest tests/unit/test_mode_structure.py -v`

## Related

- `core/FLAGS.md` — Flag definitions and auto-detection triggers
- `agents/` — Domain expert agents (modes shape mindset, agents shape expertise)
- `commands/` — Slash commands that may activate modes
- `scripts/context_loader.py` — On-demand delivery mechanism
