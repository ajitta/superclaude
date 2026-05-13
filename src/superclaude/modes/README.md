# SuperClaude Modes

Mindset overlays — situational cog frameworks that modify Claude thinking, comms, priorities.

## Content Delivery

Modes activate on-demand by `context_loader.py` via flag/keyword detect (TRIGGER_MAP). **Not** managed by Claude Code native content sys — no frontmatter needed.

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
| RESEARCH_CONFIG.md | `config` | Deep research op params — depth profiles, confidence thresholds, tool routing |

**Note:** RESEARCH_CONFIG.md **not** a mode. Gives op settings for research mode, excluded from mode structure validation. Uses `type="config"`, not `type="mode"`.

## 4-Axis Structure

Every mode define four axes:

| Axis | Tag | What It Controls |
|------|-----|------------------|
| Thinking | `<thinking>` | Cognitive principles — how to reason |
| Communication | `<communication>` | Expression style — how to present |
| Priorities | `<priorities>` | Trade-off guidance — what to optimize |
| Behaviors | `<behaviors>` | Action patterns — what to do differently |

Modes combine (e.g., `--research --uc` for compressed research output).

## Authoring Rules

See `.claude/rules/mode-authoring.md` for full authoring spec.

Validation: `uv run python -m pytest tests/unit/test_mode_structure.py -v`

## Related

- `core/FLAGS.md` — Flag defs + auto-detect triggers
- `agents/` — Domain expert agents (modes shape mindset, agents shape expertise)
- `commands/` — Slash commands may activate modes
- `scripts/context_loader.py` — On-demand delivery mechanism