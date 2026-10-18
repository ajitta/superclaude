# superclaude Modes

Mindset overlays — situational cognitive frameworks that modify Claude's thinking, communication, and priorities.

## Content Delivery

Modes are activated on demand by `context_loader.py` via flag/keyword detection. They are **not** managed by Claude Code's native content system — no frontmatter needed.

> Tables below list each mode's **primary flag**. Full trigger patterns (aliases like `--bs`, keyword forms like `systematic investigation`, slash commands like `/sc:research`) live in `scripts/context_loader.py` TRIGGER_MAP — SSOT.

## Available Modes

| Mode | Flag | Mission |
|------|------|---------|
| Brainstorming | `--brainstorm` | Collaborative discovery for requirements exploration |
| Business Panel | `--business-panel` | Multi-expert business analysis with adaptive interaction |
| Deep Research | `--research` | Research mindset for systematic investigation |
| Introspection | `--introspect` | Meta-cognitive analysis and reasoning optimization |
| Token Efficiency | `--token-efficient` / `--uc` | Selective omission for fewer output tokens without loss of clarity |
| Verbalized Sampling | `--vs` | Distribution-level answering — k candidates with post-hoc probabilities |

### Supporting Configuration

| File | Type | Purpose |
|------|------|---------|
| RESEARCH_CONFIG.md | `config` | Deep research operational parameters — planning strategies, depth profiles, source-count gates, credibility tiers, replan triggers, tool routing |

**Note:** RESEARCH_CONFIG.md is **not** a mode and is never injected by `context_loader.py`; `/sc:research` points to its installed copy, and the research mode states the source-count and replan rules it needs inline. It is excluded from mode structure validation and uses `type="config"`, not `type="mode"`.

## 4-Axis Structure

Every mode defines four axes:

| Axis | Tag | What It Controls |
|------|-----|------------------|
| Thinking | `<thinking>` | Cognitive principles — how to reason |
| Communication | `<communication>` | Expression style — how to present |
| Priorities | `<priorities>` | Trade-off guidance — what to optimize |
| Behaviors | `<behaviors>` | Action patterns — what to do differently |

Modes combine (e.g., `--research --uc`: Deep Research sets what gets investigated, Token Efficiency sets how the report is worded).

## Authoring Rules

See `.claude/rules/mode-authoring.md` for full authoring spec.

Validation: `uv run pytest tests/unit/test_mode_structure.py -v`

## Related

- `core/FLAGS.md` — Flag defs + auto-detect triggers
- `agents/` — Domain expert agents (modes shape mindset, agents shape expertise)
- `commands/` — Slash commands may activate modes
- `scripts/context_loader.py` — On-demand delivery mechanism
