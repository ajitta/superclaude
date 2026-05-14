---
status: implemented
revised: 2026-04-03
---

# Insight Schema + Agent — Discovery Spec

**Purpose**: Two complementary enhancements to the insight system:
1. Add `author` field to schema for multi-user attribution
2. Create `insight-analyst` agent for contextual insight retrieval + annotation

**Prerequisite**: `/sc:insight` command (implemented 2026-04-03)

---

## 1. Schema Enhancement: `author` Field

### Current Schema
```
Required: ts, type, insight
Optional: session, rule, context, action, files[], tags[]
```

### Proposed Schema
```
Required: ts, type, insight
Optional: author, session, rule, context, action, files[], tags[], ref_ts
```

| New Field | Required | Type | Description |
|-----------|----------|------|-------------|
| `author` | no (always emitted) | string | `git config user.name` (lowercase, no spaces). Fallback: system username. Always populated by model convention, but not enforced — old entries without it are valid. |
| `ref_ts` | no | ISO 8601 | References another non-annotation insight's `ts`. Format: second precision, colon offset (e.g., `+09:00` not `+0900`). |

### New Type: `annotation`

Type taxonomy expands from 5 to 6:

| type | When | Example |
|------|------|---------|
| `feedback` | User correction or validated approach | "gate timing > existence" |
| `decision` | X chosen over Y with reasoning | "R19 rejected" |
| `discovery` | Unexpected finding during work | "persona_index is dead ref" |
| `pattern` | Recurring problem/solution | "decorative attrs accumulate" |
| `metric` | Quantitative result | "41 attrs removed" |
| **`annotation`** | **Relevance link to existing insight** | **"auth refactor 시 참고"** |

**Annotation rules:**
- `ref_ts` must point to an existing non-annotation entry (no annotation-of-annotation chains)
- `author` on annotations is always the git user who invoked the agent, not the agent itself
- Agent must verify `ref_ts` target exists before appending
- Agent must check for existing annotations with same `ref_ts` to avoid duplicates

### Timestamp Format

All `ts` and `ref_ts` values use: second precision, colon in timezone offset.
```
Format: YYYY-MM-DDTHH:MM:SS+HH:MM
Example: 2026-04-03T18:00:00+09:00
```

### Example: Before and After

**Before** (no attribution):
```jsonl
{"ts":"2026-04-03T18:00:00+09:00","type":"feedback","insight":"gate timing > existence","tags":["rules"]}
```

**After** (with `author`):
```jsonl
{"ts":"2026-04-03T18:00:00+09:00","author":"chosh1179","type":"feedback","insight":"gate timing > existence","tags":["rules"]}
```

**Annotation** (agent-created, links to original):
```jsonl
{"ts":"2026-04-03T19:30:00+09:00","author":"chosh1179","type":"annotation","insight":"auth refactor 시 이 결정 참고 필요","ref_ts":"2026-04-03T18:00:00+09:00","tags":["auth"]}
```

### Author Population

Source: `git config user.name` → lowercase, no spaces (matching `doc_output_convention` in RULES.md).

Backward compatibility: existing entries without `author` are tolerated. Queries use `// "unknown"` fallback:
```bash
jq -r '"\(.ts) [\(.author // "unknown")] \(.insight)"' .claude/insights.jsonl
```

### New Queries Enabled

```bash
# My insights only
jq 'select(.author=="chosh1179")' .claude/insights.jsonl

# Annotations linked to a specific insight
jq 'select(.ref_ts=="2026-04-03T18:00:00+09:00")' .claude/insights.jsonl

# All annotations
jq 'select(.type=="annotation")' .claude/insights.jsonl
```

### Stats Behavior

`--stats` excludes annotations by default (annotations are metadata about insights, not insights themselves):
```bash
# Default --stats: exclude annotations
jq -r 'select(.type != "annotation") | .type' .claude/insights.jsonl | sort | uniq -c | sort -rn

# Include annotations explicitly
jq -r '.type' .claude/insights.jsonl | sort | uniq -c | sort -rn
```

---

## 2. `insight-analyst` Agent

### Purpose

Find and present relevant past insights based on current work context. Optionally annotate insights with relevance links.

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent vs Skill | Agent | Conversational, auto-delegated, persona-driven |
| Model tier | sonnet | Retrieval + bounded judgment = execution tier |
| Auto-trigger | Manual only | Token cost of auto-session-start too high |
| Write capability | Append-only annotations | `ref_ts` links, no modification of existing entries |
| Scope | Per-project | `.claude/insights.jsonl` is already per-project |
| Frontmatter style | Minimal (match existing 22 agents) | No `tools`, `effort`, `maxTurns` — behavioral control via `<bounds>` |

### Agent Frontmatter

```yaml
---
name: insight-analyst
description: Find and present relevant project insights with contextual analysis (triggers - find insights, past insights, what did we learn, insight history, search insights)
model: sonnet
permissionMode: default
memory: project
disallowedTools: NotebookEdit
color: purple
---
```

### Agent XML Body (key sections)

**`<tool_guidance>`:**
- Proceed: jq queries on insights.jsonl, semantic relevance matching, formatting results
- Ask First: appending annotation entries (user must confirm relevance link)
- Never: modify or delete existing insight entries, search across projects

**`<memory_guide>`:**
- Query-Patterns: effective jq filters and search strategies for this project's insights
  `<refs agents="root-cause-analyst,quality-engineer"/>`
- Insight-Gaps: topics with sparse insights where more capture would be valuable
  `<refs agents="deep-researcher,requirements-analyst"/>`
- Cross-References: recurring insight relationships and annotation patterns found
  `<refs agents="system-architect,refactoring-expert"/>`

**`<checklist>`:**
- [ ] Relevant insights found and presented with context
- [ ] Results grouped by type/date/author
- [ ] Annotations (if created) have valid ref_ts targeting existing entries
- [ ] No duplicate annotations for same ref_ts

**`<gotchas>`:**
- orphaned-ref-ts: Always verify ref_ts target exists before appending annotation
- stats-inflation: Annotations count as JSONL entries; remind user that --stats excludes them by default
- tz-mismatch: ref_ts string match is exact — inconsistent timezone formats break links

**`<bounds>`:**
- will: semantic insight search, contextual relevance matching, append-only annotations
- wont: modify existing insights, delete insights.jsonl, auto-trigger on session start, cross-project search
- fallback: if insights.jsonl doesn't exist, inform user to capture insights first via /sc:insight

### Agent Behavior Flow

1. Understand: Parse user query — topic, timeframe, author filter, type filter
2. Pre-filter: Run jq on `.claude/insights.jsonl` to narrow candidate set
3. Match: Apply LLM judgment for semantic relevance (beyond keyword matching)
4. Present: Format results grouped by type/date/author
5. Annotate (optional): If user confirms, append `annotation` entries linking relevant insights to current context. Check for existing annotations with same `ref_ts` first (dedup).

### Differentiation from `/sc:insight --query`

| Capability | `--query` (command) | `insight-analyst` (agent) |
|-----------|---------------------|--------------------------|
| Exact field match | `type=feedback` | yes |
| Semantic relevance | no | **yes** — LLM judgment |
| Context-aware | no | **yes** — understands current task |
| Multi-field correlation | no | **yes** — "auth decisions by chosh" |
| Annotation | no | **yes** — appends `annotation` entries |
| Token cost | ~0 (jq only) | medium (agent session) |

---

## Implementation Scope

| Item | Type | Effort |
|------|------|--------|
| `commands/insight.md` schema section | Update | Low — add `author`, `ref_ts`, `annotation` type, stats filter |
| `commands/insight.md` flow/examples | Update | Low — author population, annotation examples, dedup |
| `agents/insight-analyst.md` | New file | Medium — full agent with memory_guide, checklist, gotchas |
| `agents/README.md` | Update | Low — add to agent table (sonnet count 10→11) |
| `core/FLAGS.md` model_routing | Update | Low — add insight-analyst to sonnet list |
| This spec | Update | Low — status: implemented |
| `make deploy` | Run | 0 |

**No Python code needed.** Both changes are markdown-only.

### Test Impact
- `test_agent_structure.py` auto-detects new agent — validates frontmatter + XML
- `test_command_structure.py` re-validates insight.md after schema update
- No new tests needed

---

## Open Items (deferred)

- Cross-project insight search: not in scope, revisit if multi-repo workflow emerges
- Auto-session-start retrieval: deferred — high token cost, manual trigger sufficient
- `--find` subcommand: deferred — `--query` + agent covers current needs
- Haiku model tier: evaluated, sonnet preferred for semantic matching quality

---

## Approval

Approve this spec to proceed to `/sc:plan` for implementation?

[y/n]
