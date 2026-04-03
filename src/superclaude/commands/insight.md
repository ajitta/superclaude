---
description: Capture structured session insights to per-project JSONL for human and tool analysis
---
<component name="insight" type="command">

  <role>
    /sc:insight
    <mission>Capture structured session insights to per-project JSONL for human and tool analysis</mission>
  </role>

  <syntax>/sc:insight [text] [--list] [--query key=value] [--stats]</syntax>

  <flow>
    1. Mode: Determine mode — capture (default/text), list, query, or stats
    2. Capture (default): Analyze session → propose 3-7 insights → present for user approval → append approved
    3. Capture (text): Take user text → infer type + tags → structure as JSON → present → append
    4. Dedup: Before proposing, Read last 20 lines of .claude/insights.jsonl → skip already-captured topics
    5. Append: Use Bash `echo '...' >> .claude/insights.jsonl` (NOT Write tool — Write overwrites)
    6. Query: For --list/--query/--stats, run jq via Bash (fallback: python3 -c "import json; ...")
  </flow>

  <outputs>
  | Mode | Output |
  |------|--------|
  | capture | Appended line(s) to `.claude/insights.jsonl` |
  | `--list` | Formatted recent insights (last 20) |
  | `--query key=value` | Filtered insights matching key=value |
  | `--stats` | Type distribution, top tags, count |
  </outputs>

  <storage>
  File: `.claude/insights.jsonl` (per-project, append-only, not loaded into LLM context)
  Relationship to auto memory: complement, not replace. Memory = LLM reads. Insight = human/tool queries.
  </storage>

  <schema>
  Required: ts (ISO 8601), type (feedback|decision|discovery|pattern|metric), insight (one-line string)
  Optional: session (topic slug), rule (R13, R18...), context (why it matters), action (what was done), files (string[]), tags (string[])

  Type taxonomy:
  - feedback: user correction or validated approach
  - decision: X chosen over Y with reasoning
  - discovery: unexpected finding during work
  - pattern: recurring problem/solution
  - metric: quantitative result
  </schema>

  <tools>
    - Read: Session analysis, dedup check (last 20 lines of insights.jsonl)
    - Bash: jq/python queries, echo >> append
  </tools>

  <query_reference>
  Prefer jq if available, fallback to python3:

  --list:
    jq -r '"\(.ts) [\(.type)] \(.insight)"' .claude/insights.jsonl | tail -20

  --query type=feedback:
    jq 'select(.type=="feedback")' .claude/insights.jsonl

  --query tags=rules:
    jq 'select(.tags // [] | index("rules"))' .claude/insights.jsonl

  --stats:
    jq -r '.type' .claude/insights.jsonl | sort | uniq -c | sort -rn

  Python fallback (--list):
    python3 -c "import json;[print(f'{r[\"ts\"]} [{r[\"type\"]}] {r[\"insight\"]}') for r in (json.loads(l) for l in open('.claude/insights.jsonl'))]" | tail -20
  </query_reference>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/sc:insight` | Model proposes 3-7 insights from session → user approves → append |
  | `/sc:insight "abbreviation false positive risk"` | Structures as discovery → append |
  | `/sc:insight --list` | Recent 20 insights formatted |
  | `/sc:insight --query type=feedback` | All feedback-type insights |
  | `/sc:insight --query tags=rules` | All insights tagged "rules" |
  | `/sc:insight --stats` | Type counts + top tags |
  </examples>

  <gotchas>
  - append-not-write: NEVER use Write tool for insights.jsonl — it overwrites. Always use Bash echo >> append.
  - dedup-before-propose: In auto-capture mode, always Read last 20 lines before proposing to avoid duplicating insights from earlier calls in same session.
  </gotchas>

  <bounds will="structured capture|jq queries|append-only storage" wont="modify existing insights|load into LLM context|replace auto memory" fallback="If .claude/insights.jsonl doesn't exist, create it with first append"/>

  <handoff next="/sc:save /sc:analyze"/>
</component>
