# Claude Code Selection UX — Design Spec

**Date:** 2026-03-20
**Status:** Track 1 implemented, Track 2-3 documented for future

## Problem Statement

When Claude Code presents choices during conversations (brainstorming options, implementation strategies, architecture decisions), the user must type free-text responses to select from presented options. This creates unnecessary friction — typing "I'd like to go with option A, the Agent SDK approach" when a simple "1" would suffice.

### Pain Points

| Scenario | Current UX | Desired UX |
|----------|-----------|------------|
| Brainstorm option selection | Type description or reference option | Type "1" |
| Multi-option selection | Type each option name | Type "1,3" |
| Hierarchical choice | Re-explain context | Type "1" → then "1a" |
| Reject all options | Explain alternative | Type free text naturally |

## Research Findings

### Claude Code Architecture

| Finding | Source |
|---------|--------|
| Built with React + Ink framework for terminal rendering | [How Claude Code is built](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built) |
| Yoga (Meta) layout engine for terminal sizing | [Claude Code Internals: Terminal UI](https://kotrotsos.medium.com/claude-code-internals-part-11-terminal-ui-542fe17db016) |
| Closed source — no custom UI component injection | Confirmed via research |
| Hooks are non-interactive (stdin is JSON, no TTY access) | [Hooks reference](https://code.claude.com/docs/en/hooks) |
| Interactive TTY support already requested | [GitHub Issue #26353](https://github.com/anthropics/claude-code/issues/26353) |

### Feasibility Analysis

| Approach | Feasibility | Windows | UX Quality | Effort |
|----------|------------|---------|------------|--------|
| **Claude Code internal modification** | Impossible (closed source) | N/A | N/A | N/A |
| **Hook + /dev/tty hack** | Fragile, conflicts with Ink rendering | No (/dev/tty unavailable) | Low | 2-3 days |
| **Hook + gum/fzf external selector** | Limited — hooks are non-interactive | Partial (gum Windows support limited) | Medium | 1-2 days |
| **Agent SDK + Custom Ink TUI** | Viable — full programmatic control | Yes (Node.js) | High | 2-4 weeks |
| **Prompt optimization (selection protocol)** | Immediate — works within current system | Yes | Medium | 1 hour |
| **Anthropic feature request** | Best long-term, no direct control | Yes | Highest | Wait |

### Key Constraint: Windows 11 Environment

The user's environment is Windows 11 with bash shell. This eliminates `/dev/tty`-based approaches and limits `gum`/`fzf` interop options.

## Solution: 3-Track Strategy

### Track 1: Selection Protocol in core/RULES.md (Implemented)

Added a `<selection_protocol>` section to `core/RULES.md` that applies to ALL SuperClaude commands and agents. This is a prompt-engineering solution that standardizes how Claude presents options.

#### Protocol Rules (9 lines, ~100 tokens)

```xml
<selection_protocol note="Structured choice presentation — all commands">
Identify: assign unique selectors — [N] flat, [Na] hierarchical, [y/n] binary
Format: "#### [N] Label" with details as sub-list; keep each option scannable
Recommend: mark suggested option with ★ when one is clearly superior for context
Guide: end with input method — "select: N", "select: N,N", "[y/n]"
Accept: bare numbers (1), comma lists (1,3), y/n, and free text — all valid
Escape: always append free-input path — "or type your own" at end of guide
Depth: sub-choices → present parent first, drill down next turn (Progressive)
  Exception: ≤3 sub-options per parent → show inline as [Na] [Nb] [Nc]
Limit: max 7 options per selection; split into categories if more
Compare: add trade-off row when options have clear differentiators
</selection_protocol>
```

#### Selection Types Covered

| Type | Identifier | Input | Example |
|------|-----------|-------|---------|
| Single select | [N] | `1` | Pick one approach |
| Multi select | [N] | `1,3` | Select multiple test types |
| Binary | [y/n] | `y` | Confirm/deny |
| Hierarchical (parent) | [N] | `1` | Pick category first |
| Hierarchical (child) | [Na] | `1a` | Pick sub-option |
| Scale | [N] | `3` | Depth: 1=quick ~ 4=deep |
| Confirmation | [y/n/e] | `e` | Approve/reject/edit plan |
| Free text escape | any text | typed | Reject all, propose alternative |

#### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Placed in `core/RULES.md`, not `brainstorm.md` | Applies to all commands, not just brainstorming |
| 9-line compressed format | Matches RULES.md density; ~100 token cost per session |
| No `<details>` HTML tags | Terminal rendering not guaranteed |
| No `?N` custom syntax | Keep it simple; markdown headings for detail visibility |
| Markdown `####` headers for options | Guaranteed rendering in all terminals |
| Accept scrolling over collapsing | Reliable > clever |
| Progressive hierarchy (parent → child next turn) | Reduces cognitive load per selection |
| ≤3 sub-options inline exception | Avoids unnecessary turn for trivial choices |

#### Example Output (After Protocol)

```markdown
#### [1] ★ Agent SDK + Custom TUI
- Full visual selection UI, Windows compatible
- 3-4 weeks investment
- Tech: @anthropic-ai/claude-agent-sdk + Ink

#### [2] Hook + gum Hybrid
- Quick prototype, limited UX
- 2-3 days
- Windows support limited

#### [3] Feature Request
- Best possible UX (native)
- Timeline unknown, zero effort

---
compare: [1] high-invest/max-flex vs [2] low-invest/limited vs [3] zero/wait

select: 1, or type your own
```

### Track 2: `claude-brainstorm` Dedicated TUI (Future)

A standalone CLI tool using Agent SDK + Ink for brainstorming-specific interactions with visual selection UI.

#### Architecture Concept

```
[claude-brainstorm CLI]  ←→  [Agent SDK]  ←→  [Claude API]
        ↓
  ┌──────────┬─────────────┐
  │ Options  │  Preview    │
  │ > Opt 1  │  details    │
  │   Opt 2  │  here       │
  ├──────────┴─────────────┤
  │ [Chat] [Files] [Plan]  │  ← tab switching
  ├────────────────────────┤
  │ > input...              │
  └────────────────────────┘
```

#### Technical Stack

- `@anthropic-ai/claude-agent-sdk` — Claude conversation engine
- `ink` + `ink-select-input` — Terminal React components
- `ink-text-input` — Input fields
- `fuse.js` — Fuzzy search for option filtering

#### Option Detection Protocol

Claude instructed to emit structured markers when presenting options:

```
<!--OPTIONS
{
  "type": "single_select",
  "question": "Which approach?",
  "options": [
    {"id": 1, "label": "Agent SDK", "description": "Full control"},
    {"id": 2, "label": "Hook hybrid", "description": "Quick prototype"}
  ]
}
OPTIONS-->
```

TUI parses markers and renders visual selection components.

#### Scope

- Brainstorming conversations only (not general coding)
- No tool permission handling needed
- No file editing UI needed
- Core: chat rendering + selection UI + SDK integration

### Track 3: Anthropic Feature Request (Future)

- Reference: [GitHub Issue #26353](https://github.com/anthropics/claude-code/issues/26353) — Interactive TTY mode
- Claude Code is Ink-based (React), so structured selection components are technically feasible
- Submit concrete UX mockups with this spec as evidence of demand

## Files Changed

| File | Change | Status |
|------|--------|--------|
| `src/superclaude/core/RULES.md` | Added `<selection_protocol>` section (9 lines) | Implemented |
| `src/superclaude/commands/brainstorm.md` | Removed verbose selection_protocol (restored to original) | Implemented |

## Verification

- 21/21 structure tests passing (brainstorm command + content)
- Deployed via `make deploy`
- Protocol loads on every session via `CLAUDE_SC.md` → `core/RULES.md`

## References

- [How Claude Code is built — Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built)
- [Claude Code Internals: Terminal UI](https://kotrotsos.medium.com/claude-code-internals-part-11-terminal-ui-542fe17db016)
- [Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Run Claude Code programmatically](https://code.claude.com/docs/en/headless)
- [Interactive TTY Feature Request #26353](https://github.com/anthropics/claude-code/issues/26353)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [awesome-tuis](https://github.com/rothgar/awesome-tuis)
- [Agent SDK demos](https://github.com/anthropics/claude-agent-sdk-demos)
