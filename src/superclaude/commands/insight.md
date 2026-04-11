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
    4. Dedup: Before proposing, Read last 20 lines of .claude/insights.jsonl → skip already-captured topics. For annotations, also check existing ref_ts to avoid duplicates.
    5. Append: Batch via Python — `python3 -c "import json; entries=[...]; f=open('.claude/insights.jsonl','a'); [f.write(json.dumps(e)+'\n') for e in entries]; f.close()"` (NOT Write tool — Write overwrites, NOT echo — escaping risk)
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
  Required: ts (ISO 8601), type (feedback|decision|discovery|pattern|metric|annotation), insight (one-line string)
  Optional: author (git username, always emitted), session (topic slug), rule (R13, R18...), context (why it matters), action (what was done), files (string[]), tags (string[]), ref_ts (ISO 8601, annotation target)

  Author: `git config user.name` (lowercase, no spaces) — always populated, not enforced for backward compat.
  Timestamp format: second precision, colon offset (YYYY-MM-DDTHH:MM:SS+HH:MM).

  Type taxonomy:
  - feedback: user correction or validated approach
  - decision: X chosen over Y with reasoning
  - discovery: unexpected finding during work
  - pattern: recurring problem/solution
  - metric: quantitative result
  - annotation: relevance link to existing insight (requires ref_ts targeting a non-annotation entry)

  Annotation rules:
  - ref_ts must target an existing non-annotation entry's ts (no annotation chains)
  - author on annotations = git user who invoked the agent, not the agent itself
  - Agent must verify ref_ts target exists before appending
  - Agent must check for existing annotations with same ref_ts to avoid duplicates
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

  --stats (excludes annotations):
    jq -r 'select(.type != "annotation") | .type' .claude/insights.jsonl | sort | uniq -c | sort -rn

  --stats --all (includes annotations):
    jq -r '.type' .claude/insights.jsonl | sort | uniq -c | sort -rn

  --query author=chosh1179:
    jq 'select(.author=="chosh1179")' .claude/insights.jsonl

  --query type=annotation:
    jq 'select(.type=="annotation")' .claude/insights.jsonl

  Annotations for a specific insight:
    jq 'select(.ref_ts=="2026-04-03T18:00:00+09:00")' .claude/insights.jsonl

  Python fallback (--list):
    python3 -c "import json;[print(f'{r[\"ts\"]} [{r.get(\"author\",\"unknown\")}] [{r[\"type\"]}] {r[\"insight\"]}') for r in (json.loads(l) for l in open('.claude/insights.jsonl'))]" | tail -20
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
  | `/sc:insight --query type=annotation` | All annotation entries |
  </examples>

  <gotchas>
  - append-not-write: NEVER use Write tool for insights.jsonl — it overwrites. Use Python `json.dumps()` batch append (handles escaping safely). Avoid bare `echo >>` — quotes/special chars in insight text cause silent corruption.
  - dedup-before-propose: In auto-capture mode, always Read last 20 lines before proposing to avoid duplicating insights from earlier calls in same session.
  </gotchas>

  <bounds should="structured capture|jq queries|append-only storage" avoid="modify existing insights|load into LLM context|replace auto memory" fallback="If .claude/insights.jsonl doesn't exist, create it with first append"/>

  <handoff next="/sc:save /sc:analyze"/>
</component>
