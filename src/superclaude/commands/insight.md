---
description: Capture structured session insights to per-project JSONL for human and tool analysis
---
<component name="insight" type="command">

  <role command="/sc:insight">
    <mission>Capture structured session insights to per-project JSONL for human and tool analysis</mission>
  </role>

  <syntax>/sc:insight [text] [--list] [--query key=value] [--stats] [--review]</syntax>

  <flow>
  1. Mode: Determine mode — capture (default/text), list, query, stats, or review (process pending harvested markers)
  2. Capture (default): Analyze session → propose 3-7 insights → present for user approval → append approved
  3. Capture (text): Take user text → infer type + tags → structure as JSON → present → append
  4. Dedup: Before proposing, run `insight_writer.py list --limit 20` to check recent entries → skip already-captured topics. For annotations, also check existing ref_ts.
  5. Append: ALWAYS via `python3 {{SCRIPTS_PATH}}/insight_writer.py append --json '<json>'` — NEVER hand-write to insights.jsonl. The script enforces schema, escaping, and annotation ref validation.
  6. Read modes: `--list`, `--query`, `--stats` shell out to jq via the same script. If jq is missing the script prints an install hint and exits 1 — relay the message to the user.
  7. Review mode: `--review` calls `insight_writer.py review` to list pending markers harvested by the SessionEnd/PreCompact hooks. For each desired entry, propose a structured promote (type + tags) and call `insight_writer.py promote --index N --type TYPE [--tags a,b]`.
  </flow>

  <outputs>
  | Mode | Output |
  |---|---|
  | capture | Appended line(s) to `.claude/insights.jsonl` |
  | `--list` | Formatted recent insights (last 20) |
  | `--query key=value` | Filtered insights matching key=value |
  | `--stats` | Type distribution, top tags, count |
  | `--review` | Pending harvested markers + promote flow |
  </outputs>

  <storage>
  Files (per-project, append-only, not loaded into LLM context):
  - `.claude/insights.jsonl` — promoted, structured insights
  - `.claude/insights.pending.jsonl` — raw `INSIGHT:` markers harvested from transcripts (created on demand, removed when empty)

  Auto-harvest: `SessionEnd` and `PreCompact` hooks scan the active transcript for user messages containing `INSIGHT:` and append unique entries to pending. `SessionStart` (clear|compact|startup) prints a one-line notice if pending is non-empty.

  Relationship to auto memory: complement, not replace. Memory = LLM reads. Insight = human/tool queries.
  </storage>

  <schema>
  Required: ts (ISO 8601), type (feedback|decision|discovery|pattern|metric|annotation), insight (one-line string)
  Optional: author (git username, always emitted), session (topic slug), rule (R13, R18...), context (why it matters), action (what was done), files (string[]), tags (string[]), ref_ts (ISO 8601, annotation target)

  Author: `git config user.name` (lowercase, no spaces) — script auto-fills if missing.
  Timestamp format: second precision, colon offset (YYYY-MM-DDTHH:MM:SS+HH:MM) — script auto-fills if missing.

  Type taxonomy:
  - feedback: user correction or validated approach
  - decision: X chosen over Y with reasoning
  - discovery: unexpected finding during work
  - pattern: recurring problem/solution
  - metric: quantitative result
  - annotation: relevance link to existing insight (requires ref_ts targeting a non-annotation entry; script enforces)
  </schema>

  <tools>
  - Bash: invoke `insight_writer.py` (append/list/query/stats/review/promote). All file I/O on insights.jsonl goes through this script.
  </tools>

  <script_reference>
  Append a single entry:
    python3 {{SCRIPTS_PATH}}/insight_writer.py append --json '{"type":"feedback","insight":"...","tags":["..."]}'

  Append multiple (batch):
    python3 {{SCRIPTS_PATH}}/insight_writer.py append --json '[{...},{...}]'

  Read paths (require jq):
    python3 {{SCRIPTS_PATH}}/insight_writer.py list [--limit 20]
    python3 {{SCRIPTS_PATH}}/insight_writer.py query type=feedback
    python3 {{SCRIPTS_PATH}}/insight_writer.py query tags=rules
    python3 {{SCRIPTS_PATH}}/insight_writer.py stats [--all]

  Pending review/promote:
    python3 {{SCRIPTS_PATH}}/insight_writer.py review
    python3 {{SCRIPTS_PATH}}/insight_writer.py promote --index 0 --type discovery --tags harvest,a,b
    python3 {{SCRIPTS_PATH}}/insight_writer.py promote --index 0 --type pattern --insight "rewritten one-liner"
  </script_reference>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:insight` | Model proposes 3-7 insights from session → user approves → script appends |
  | `/sc:insight "abbreviation false positive risk"` | Structures as discovery → script appends |
  | `/sc:insight --list` | Recent 20 insights formatted |
  | `/sc:insight --query type=feedback` | All feedback-type insights |
  | `/sc:insight --query tags=rules` | All insights tagged "rules" |
  | `/sc:insight --stats` | Type counts |
  | `/sc:insight --review` | Lists pending markers; proposes structured promote for each |
  </examples>

  <auto_harvest_behavior>
  When a user message contains the literal `INSIGHT:` marker (line-start or inline), the SessionEnd / PreCompact hooks scan the active transcript and append unique entries to `.claude/insights.pending.jsonl`. On the next SessionStart (clear|compact|startup), a one-line notice ("🟡 N pending insight(s) — run /sc:insight --review") is injected. The user invokes `/sc:insight --review` to classify and promote each pending entry.
  </auto_harvest_behavior>

  <gotchas>
  - script-only-writes: NEVER use Write/echo on insights.jsonl. ALWAYS go through `insight_writer.py append`. The script handles JSON escaping, schema validation, and annotation ref existence checks that hand-written code routinely misses.
  - jq-required: `--list`, `--query`, `--stats` need jq on PATH. If absent, the script exits 1 with an install URL — surface that to the user, do not implement an inline Python fallback.
  - dedup-before-propose: In auto-capture mode, run `insight_writer.py list --limit 20` first to avoid duplicating earlier entries from the same session.
  - review-requires-classification: Pending entries are raw text; you must propose a `--type` (feedback|decision|discovery|...) and optional tags before calling promote. Never promote without showing the user what classification you intend.
  </gotchas>

  <bounds>
    <does>structured capture via script, jq queries, pending review/promote, and append-only storage.</does>
    <never>modify existing insights, load into LLM context, replace auto memory, and hand-edit insights.jsonl.</never>
    <fallback>If insights.jsonl doesn't exist, the script creates it on first append.</fallback>
  </bounds>

  <handoff next="/sc:save /sc:analyze"/>
</component>
