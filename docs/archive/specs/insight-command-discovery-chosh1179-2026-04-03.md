---
status: implemented
revised: 2026-04-03
---

# /sc:insight Command — Discovery Spec

**Purpose**: Structured session insight capture to per-project JSONL for human/tool analysis.
**Relationship to auto memory**: Complement, not replace. Memory = LLM reads next session. Insight = human/tool queries across sessions.

---

## Design

### Storage
- **File**: `.claude/insights.jsonl` (per-project, append-only)
- **Format**: One JSON object per line, UTF-8
- **Not loaded into LLM context** — zero token cost

### Schema
```jsonl
{"ts":"2026-04-03T18:00:00+09:00","type":"feedback","insight":"Gate timing > gate existence","session":"retrospective-improvements","rule":"R18","context":"7 issues, existing gates had wrong scope","action":"Expanded R18 scope","files":["RULES.md"],"tags":["rules","simplicity"]}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `ts` | yes | ISO 8601 | Timestamp |
| `type` | yes | enum | feedback, decision, discovery, pattern, metric |
| `insight` | yes | string | One-line insight text |
| `session` | no | string | Session identifier / topic |
| `rule` | no | string | Related rule (R13, R18, etc.) |
| `context` | no | string | Why this insight matters |
| `action` | no | string | What was done about it |
| `files` | no | string[] | Files involved |
| `tags` | no | string[] | Filterable tags |

### Type Taxonomy

| type | When | Example |
|------|------|---------|
| `feedback` | User corrects approach or validates non-obvious choice | "gate timing > existence" |
| `decision` | X chosen over Y with reasoning | "R19 rejected → absorbed into anti_misunderstanding" |
| `discovery` | Unexpected finding during work | "persona_index is dead reference since b02e4b1" |
| `pattern` | Recurring problem/solution across sessions | "decorative attrs accumulate via copy-paste" |
| `metric` | Quantitative result | "41 attrs removed → ~480 tokens/session saved" |

### Multi-call per session
- 한 세션에서 여러 번 호출 가능 (작업 단위마다 인사이트 캡처)
- 자동 분석 모드: 제안 전 insights.jsonl 마지막 20줄 Read → 이미 캡처된 주제 제외
- 직접 입력 모드: 항상 append (중복 체크 없음 — 사용자 판단)
- session 필드: 모델이 세션 주제에서 추론. 불명확하면 생략 (optional)

### Subcommands

```
/sc:insight                        # Model analyzes session → proposes insights → user approves → append
/sc:insight "direct text"          # User provides insight directly → model structures as JSON → append
/sc:insight --list                 # Show summary of all insights (jq)
/sc:insight --query type=feedback    # Filter insights
/sc:insight --stats                # Count by type, top tags, timeline
```

### Query Implementation
Prefer `jq` if available, fallback to `python -c "import json; ..."` (always present — SuperClaude dependency):

```bash
# --list (recent 20) — jq
jq -r '"\(.ts) [\(.type)] \(.insight)"' .claude/insights.jsonl | tail -20

# --list — python fallback
python3 -c "import json,sys;[print(f'{r[\"ts\"]} [{r[\"type\"]}] {r[\"insight\"]}') for r in (json.loads(l) for l in open('.claude/insights.jsonl'))]" | tail -20

# --query type=feedback
jq 'select(.type=="feedback")' .claude/insights.jsonl

# --query tags=rules
jq 'select(.tags // [] | index("rules"))' .claude/insights.jsonl

# --stats
jq -r '.type' .claude/insights.jsonl | sort | uniq -c | sort -rn
```

### Append Implementation
Use Bash `>>` redirect — NOT Write tool (Write overwrites):
```bash
echo '{"ts":"...","type":"feedback","insight":"..."}' >> .claude/insights.jsonl
```

---

## Command Spec (commands/insight.md)

```xml
<component name="insight" type="command">
  <role>
    /sc:insight
    <mission>Capture structured session insights to per-project JSONL for human and tool analysis</mission>
  </role>

  <syntax>/sc:insight [text] [--list] [--query "filter"] [--stats]</syntax>

  <flow>
    1. Mode: Determine mode — capture (default/text), list, query, or stats
    2. Capture: Model analyzes session or takes user text → structures as JSON → presents for approval
    3. Append: Bash echo >> .claude/insights.jsonl (one line per insight, NOT Write tool)
    4. Query: For --list/--query/--stats, run jq via Bash on .claude/insights.jsonl
  </flow>

  <outputs>
  | Mode | Output |
  |------|--------|
  | capture | Appended line(s) to .claude/insights.jsonl |
  | --list | Formatted recent insights |
  | --query | Filtered insights |
  | --stats | Type counts, top tags, timeline |
  </outputs>

  <tools>
    - Read: Session analysis, dedup check (last 20 lines of insights.jsonl)
    - Bash: jq/python queries, echo >> append
  </tools>

  <schema>
  Required: ts (ISO 8601), type (feedback|decision|discovery|pattern|metric), insight (string)
  Optional: session, rule, context, action, files[], tags[]
  </schema>

  <examples>
  | Input | Output |
  |-------|--------|
  | /sc:insight | Model proposes 3-5 insights from session → user approves → append |
  | /sc:insight "약어 false positive 위험" | Structures as discovery type → append |
  | /sc:insight --list | Recent 20 insights formatted |
  | /sc:insight --query type=feedback | All feedback-type insights |
  | /sc:insight --stats | Type distribution + top tags |
  </examples>

  <bounds will="structured capture|jq queries|append-only storage" wont="modify existing insights|load into LLM context|replace auto memory"/>
  <handoff next="/sc:save /sc:analyze"/>
</component>
```

---

## Implementation Scope

| Item | Type | Effort |
|------|------|--------|
| `src/superclaude/commands/insight.md` | New command file | Low (markdown only) |
| Test: command structure validation | Existing tests auto-detect | 0 |
| `make deploy` | Install to ~/.claude/commands/sc/ | 0 |

**No Python code needed.** Query is jq via Bash. Storage is Write tool. Schema is model-enforced via command docs.

---

## Decision Required

Approve this spec to proceed to implementation?

[y/n]
