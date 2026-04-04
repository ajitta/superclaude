---
status: superseded
revised: 2026-04-04
---

# Frontend-Design Plugin x SuperClaude: Coexistence Design

> **SUPERSEDED:** Post-review analysis (self-review + simplicity-guide + fact-check) determined Tier 0 is sufficient. All 3 proposed Tier 1 changes fail R18 necessity test. The sub-agent context gap has a native CC solution (`skills:` frontmatter field) — no SC framework changes needed. See updated discovery spec.
>
> **Key finding from review:** CC's `skills:` frontmatter field in agent definitions already supports preloading plugin skills into sub-agents ([source: code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)). Users can add `skills: [frontend-design:frontend-design]` to `frontend-architect.md` if they want aesthetic guidance in delegated work. This is a user config choice, not an SC framework change.

**Discovery:** `frontend-design-plugin-coexistence-discovery-ajitta-2026-04-04.md`

## Design Summary (original — superseded)

3 micro-edits to 1 file (`frontend-architect.md`). No new files, no install-time changes, no new skills. Total cost: ~52 tokens.

## Architecture: Layer Separation

```
┌─────────────────────────────────────────────────┐
│  User Prompt: "build a dashboard"               │
├─────────────────────────────────────────────────┤
│  System Prompt Layer                            │
│  ┌──────────────────┐  ┌─────────────────────┐  │
│  │ SC Core Framework │  │ frontend-design     │  │
│  │ (FLAGS, RULES,    │  │ plugin skill        │  │
│  │  PRINCIPLES)      │  │ (auto-injected)     │  │
│  └──────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Main Conversation ← both active                │
│  ┌──────────────────────────────────────────┐   │
│  │ Direct response: aesthetic + engineered   │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Sub-Agent Delegation ← only SC active          │
│  ┌──────────────────────────────────────────┐   │
│  │ frontend-architect: engineered            │   │
│  │ (plugin skill NOT inherited)              │   │
│  │ Tier 1: +aesthetic awareness in agent     │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Tier 1 Changes (implement now)

### R18 Necessity Test

| Change | Broken without? | Evidence | Verdict |
|--------|----------------|----------|---------|
| Mindset: +aesthetic awareness | Sub-agent produces generic UI | User-facing visual quality gap | **PASS** |
| Focus: +design quality item | Agent has no aesthetic principle | Plugin-absent users get no design guidance | **PASS** |
| Gotcha: plugin coexistence | Agent unaware of plugin role separation | Potential instruction confusion | **PASS** |
| New skill (Tier 2) | System works, just sub-optimal | No user reports yet | **FAIL — defer** |
| Install detection | No install conflict exists | N/A | **FAIL — unnecessary** |

### Change 1: Mindset Update

**File:** `src/superclaude/agents/frontend-architect.md` line 11

```diff
- <mindset>User-first in every decision. Accessibility as fundamental, not afterthought. Optimize for real-world constraints.</mindset>
+ <mindset>User-first in every decision. Accessibility as fundamental, not afterthought. Distinctive design over generic output. Optimize for real-world constraints.</mindset>
```

**Rationale:** 5-word addition. Establishes aesthetic principle without diluting a11y focus. Works with or without plugin.

### Change 2: Focus Addition

**File:** `src/superclaude/agents/frontend-architect.md` after line 19 (after Frameworks item)

```diff
  - Frameworks: React, Vue, Angular best practices + optimization
+ - Design Quality: intentional aesthetic choices, contextual visual identity, avoid generic patterns
```

**Rationale:** Bridges the aesthetic gap for plugin-absent users. Principle-level (WHAT to care about), not implementation-level (HOW to do it — that's the plugin's domain). Complements rather than competes.

### Change 3: Gotcha Addition

**File:** `src/superclaude/agents/frontend-architect.md` in `<gotchas>` section after line 71

```diff
  - rich-only: SC's only frontend dependency is Rich (terminal UI). Do not recommend React/Vue/browser frameworks for SC itself
+ - plugin-coexistence: If frontend-design plugin provides aesthetic direction in parent context, focus on engineering guardrails (a11y, perf, responsive). If absent, also consider visual distinctiveness and contextual design
```

**Rationale:** Project-specific (not generic advice). Informs agent about role separation. Adaptive — behavior adjusts to plugin presence.

## Tier 2 Design (deferred)

**Decision gate:** 3+ user reports of generic-looking SC-delegated frontend output.

### If triggered: SC Reference Skill

```
src/superclaude/skills/frontend-aesthetics/
└── SKILL.md
```

```yaml
---
name: frontend-aesthetics
description: Design quality principles for distinctive, contextual frontend interfaces.
when-to-use: >
  When building web components, pages, or applications.
  Complements engineering focus with aesthetic awareness.
user-invocable: false
---
```

- Content: SC's own design-quality principles (~800 tokens)
- NOT a copy of the plugin — SC's perspective on accessible, performant beauty
- Agent integration: `skills: [frontend-aesthetics]` in frontend-architect frontmatter
- Coexists with plugin (additive, not competing)

### CC Feature Watch

If CC adds plugin skill inheritance for sub-agents (`skills:` frontmatter inheriting parent plugins), Tier 2 becomes unnecessary. Monitor CC changelog.

## Broader Plugin Ecosystem

Official plugins in `anthropics/claude-plugins-official` (count unverified — likely 50+). Potentially overlapping with SC:

| Plugin | SC Overlap | Conflict Level |
|--------|-----------|----------------|
| `code-review` | self-review agent | Low — different depth |
| `code-simplifier` | simplicity-guide agent | Low — different approach |
| `feature-dev` | /sc:implement command | Medium — workflow overlap |
| `security-guidance` | security-engineer agent | Low — complementary |
| `frontend-design` | frontend-architect agent | **None** — different dimensions |

**Pattern:** Official plugins tend to be lightweight skills (~2K tokens). SC provides deeper, structured frameworks. They complement more than compete. No general coexistence mechanism needed now.

## Validation Plan

1. Run `uv run pytest tests/unit/test_agent_structure.py -v` — verify agent structure valid
2. Install plugin (`/plugin` → enable frontend-design → `/reload-plugins`)
3. Test direct prompt: "build a dashboard" — verify plugin aesthetic guidance applies
4. Test SC delegation: `/sc:implement "build a dashboard"` — verify agent has aesthetic awareness
5. Test plugin-absent: remove plugin, verify agent still has design quality focus

## Constraints

| Constraint | Value |
|------------|-------|
| Token budget for changes | ~52 tokens |
| Files modified | 1 (`frontend-architect.md`) |
| New files | 0 |
| Install logic changes | 0 |
| Test impact | None (structure unchanged) |

## Next Steps

- `/sc:implement` — apply the 3 changes to `frontend-architect.md`
- `uv run pytest tests/unit/test_agent_structure.py -v` — validate
