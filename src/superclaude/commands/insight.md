---
description: Capture structured session insights to per-project JSONL for human + tool analysis. Use when user types `/sc:insight` (with optional --list/--query/--stats/--review) or explicitly asks to record an insight ("record this insight", "capture this as an insight"). NO auto-trigger on "let me note this" or general observation — insights = deliberate capture, no auto-snapshot.
---
<component name="insight" type="command">

  <role command="/sc:insight">
    <mission>Capture structured session insights to per-project JSONL for human + tool analysis</mission>
  </role>

  <syntax>/sc:insight [text] [--list] [--query key=value] [--stats] [--review]</syntax>

  <flow>
  1. Mode: pick mode — capture (default/text), list, query, stats, or review (process pending harvested markers)
  2. Capture (default): scan session → propose 3-7 insights → show user for approval → append approved
  3. Capture (text): take user text → infer type + tags → shape as JSON → show → append
  4. Dedup: before propose, run `insight_writer.py list --limit 20` to check recent entries → skip already-captured topics. For annotations, also check existing ref_ts.
  5. Append: ALWAYS via `python3 {{SCRIPTS_PATH}}/insight_writer.py append --json '<json>'` — NEVER hand-write to insights.jsonl. Script enforce schema, escaping, annotation ref check. (`{{SCRIPTS_PATH}}` here and below resolves to `~/.claude/superclaude/scripts/` — substitute real path when running; command bodies ship the literal template unresolved.)
  6. Read modes: `--list`, `--query`, `--stats` shell to jq via same script. If jq missing, script print install hint + exit 1 — relay message to user.
  7. Review mode: `--review` call `insight_writer.py review` to list pending markers harvested by SessionEnd/PreCompact hooks. For each wanted entry, propose structured promote (type + tags) + call `insight_writer.py promote --index N --type TYPE [--tags a,b]`.
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
  Files (per-project, append-only, no load into LLM context):
  - `.claude/insights.jsonl` — promoted, structured insights
  - `.claude/insights.pending.jsonl` — raw `INSIGHT:` markers harvested from transcripts (made on demand, gone when empty)

  Auto-harvest: `SessionEnd` + `PreCompact` hooks scan active transcript for user messages with `INSIGHT:` + append unique entries to pending. `SessionStart` (clear|compact|startup) print one-line notice if pending non-empty.

  Link to auto memory: complement, no replace. Memory = LLM read. Insight = human/tool query.
  </storage>

  <schema>
  Required: ts (ISO 8601), type (feedback|decision|discovery|pattern|metric|annotation), insight (one-line string)
  Optional: author (git username, always emit), session (topic slug), rule (R13, R18...), context (why matter), action (what done), files (string[]), tags (string[]), ref_ts (ISO 8601, annotation target)

  Author: `git config user.name` (lowercase, no spaces) — script auto-fill if missing.
  Timestamp format: second precision, colon offset (YYYY-MM-DDTHH:MM:SS+HH:MM) — script auto-fill if missing.

  Type taxonomy:
  - feedback: user correction or validated approach
  - decision: X chosen over Y with reason
  - discovery: surprise finding during work
  - pattern: recurring problem/solution
  - metric: quantitative result
  - annotation: relevance link to existing insight (need ref_ts targeting non-annotation entry; script enforce)
  </schema>

  <tools>
  - Bash: call `insight_writer.py` (append/list/query/stats/review/promote). All file I/O on insights.jsonl go through this script.
  </tools>

  <script_reference>
  Append one entry:
    python3 {{SCRIPTS_PATH}}/insight_writer.py append --json '{"type":"feedback","insight":"...","tags":["..."]}'

  Append many (batch):
    python3 {{SCRIPTS_PATH}}/insight_writer.py append --json '[{...},{...}]'

  Read paths (need jq):
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
  | `/sc:insight` | Model propose 3-7 insights from session → user approve → script append |
  | `/sc:insight "abbreviation false positive risk"` | Shape as discovery → script append |
  | `/sc:insight --list` | Recent 20 insights formatted |
  | `/sc:insight --query type=feedback` | All feedback-type insights |
  | `/sc:insight --query tags=rules` | All insights tagged "rules" |
  | `/sc:insight --stats` | Type counts |
  | `/sc:insight --review` | List pending markers; propose structured promote for each |
  </examples>

  <auto_harvest_behavior>
  When user message hold literal `INSIGHT:` marker (line-start or inline), SessionEnd / PreCompact hooks scan active transcript + append unique entries to `.claude/insights.pending.jsonl`. On next SessionStart (clear|compact|startup), one-line notice ("🟡 N pending insight(s) — run /sc:insight --review") inject. User invoke `/sc:insight --review` to classify + promote each pending entry.
  </auto_harvest_behavior>

  <gotchas>
  - script-only-writes: NEVER Write/echo on insights.jsonl. ALWAYS go through `insight_writer.py append`. Script handle JSON escaping, schema check, annotation ref existence checks that hand-written code miss often.
  - jq-required: `--list`, `--query`, `--stats` need jq on PATH. If absent, script exit 1 with install URL — surface to user, no inline Python fallback.
  - dedup-before-propose: In auto-capture mode, run `insight_writer.py list --limit 20` first to dodge dup entries from same session.
  - review-requires-classification: Pending entries = raw text; must propose `--type` (feedback|decision|discovery|...) + optional tags before call promote. Never promote without show user what classification you plan.
  </gotchas>

  <bounds>
    <does>structured capture via script, jq queries, pending review/promote, append-only storage.</does>
    <never>modify existing insights, load to LLM context, replace auto memory, hand-edit insights.jsonl.</never>
    <fallback>If insights.jsonl missing, script make it on first append.</fallback>
  </bounds>

  <handoff next="/sc:save /sc:analyze"/>
</component>