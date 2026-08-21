---
status: complete
revised: 2026-08-21
---

# Analysis — SuperClaude runtime behavior from Claude Code logs

## Method

Three passes, all reproducible:

1. **Prompt history** — `~/.claude/history.jsonl`, 14,596 entries, 2025-10-15 → 2026-08-21.
   Parsed for `/sc:*` command tokens, `--flag` tokens, project path, timestamp. This measures
   what the user *asked for*, independent of whether the framework was present to answer.
2. **Session transcripts** — `~/.claude/projects/**/*.jsonl`, 1,331 files, 1.1 GB. Parsed for
   `tool_use` blocks: tool name, `subagent_type`, `Skill` name. Claude Code rotates these, so
   the window is 2026-07-22 → 2026-08-21 (30 days). Every transcript-derived claim below is
   bounded to that window and labelled.
3. **Live probes** — each of the 11 hook commands in `.claude/settings.local.json` executed
   with synthetic stdin; `context_loader.py` executed against five representative prompts with
   the state cache cleared between runs.

Two caveats on the evidence. Transcript greps for framework identifiers (`destructive_guard`,
`loop_guard`, …) are unusable inside this repository because the source text itself appears in
the transcripts; all such counts were discarded and replaced by structured `tool_use` parsing.
And the probe runs mutated this repository's own hook state (`mcp_fallbacks.json`,
`claude_context_f17f0cab.txt`) — both are self-healing caches, not durable data.

---

## A1 — Adoption collapse (critical)

`/sc:` share of typed prompts, by month:

| Month | Prompts | `/sc:` | Share | caveman | /goal | karpathy | /effort |
|---|---|---|---|---|---|---|---|
| 2025-10 | 672 | 204 | 30.4% | 0 | 0 | 0 | 0 |
| 2025-11 | 1,540 | 680 | 44.2% | 0 | 0 | 0 | 0 |
| 2025-12 | 1,391 | 658 | 47.3% | 0 | 0 | 0 | 0 |
| 2026-01 | 1,279 | 377 | 29.5% | 0 | 0 | 0 | 0 |
| 2026-02 | 1,599 | 510 | 31.9% | 0 | 0 | 0 | 0 |
| 2026-03 | 1,619 | 673 | 41.6% | 0 | 0 | 0 | 4 |
| 2026-04 | 1,747 | 181 | 10.4% | 0 | 0 | 14 | 2 |
| 2026-05 | 2,280 | **0** | 0.0% | 50 | 0 | 146 | 8 |
| 2026-06 | 1,232 | 0 | 0.0% | 17 | 30 | 83 | 55 |
| 2026-07 | 653 | 7 | 1.1% | 11 | 38 | 13 | 23 |
| 2026-08 | 584 | 2 | 0.3% | 41 | 71 | 37 | 31 |

The substitution is visible in the same table: the month `/sc:` reaches zero is the month the
karpathy skill plugin reaches 146 uses and caveman appears at 50. `/goal` and `/effort`
(native Claude Code) climb through the summer. The roles overlap almost one-for-one —
`--uc`/MODE_Token_Efficiency vs. caveman, `RULES`/`PRINCIPLES` vs. karpathy-guidelines,
`--task-manage` vs. `/goal`, thinking flags vs. `/effort`.

Total `/sc:` invocations since 2026-06-01: **9** (5 in oasis-nakama-dev, 4 in this repository).

## A2 — Distribution: no user-scope install, no plugin

- `superclaude install --list` reports `Total: 36 available, 0 installed`. Default scope is
  user, and `~/.claude/` contains no `superclaude/`, no `commands/`, no `agents/`.
- Only two project-local installs exist on this machine: this repository and
  `/Users/chosh/Repos/fitfuns/oasis/oasis-nakama-dev`.
- Three of the five heaviest historical consumers have `.claude/` but no SuperClaude content:
  `oasis_editor` (835 `/sc:` uses, last 2026-03-17), `playcanvas-editor-ts-template` (603, last
  2025-12-10), `smd-webgl` (574, last 2025-12-18). `oasis_editor/.claude/` still holds an orphan
  `agent-memory/` and `rules/` — the install was removed, not absent.
- The tooling that displaced it is user-scope plugin: `claude-mem@thedotmack`,
  `claude-md-management`, caveman, karpathy-skills — installed once, present in every repo.
- This repository has no `.claude-plugin/plugin.json` and no marketplace manifest. `plugins/`
  contains one unrelated skill (`tavily-response-filter`).

Per-project installation is the only distribution path, and it is the one path that does not
survive starting work in a new repository.

## A3 — Context cache is keyed by project, not session (defect, reproduced)

`src/superclaude/scripts/context_loader.py:64`:

```python
SESSION_ID = project_key()
CACHE_FILE = _CACHE_DIR / f"claude_context_{SESSION_ID}.txt"
```

`project_key()` is `md5(project_root())[:8]`. The name `SESSION_ID` is a misnomer — the cache
is per-project and shared by every concurrent Claude Code session in that project.

Reproduction (cache cleared first):

```
session_id "A", prompt "analyze this --seq"  →  861 bytes injected
session_id "B", same prompt                  →    0 bytes injected
```

The second session receives no framework context at all for anything the first session already
triggered. `SessionStart` runs `context_reset.py`, which clears the file project-wide, so the
failure is symmetric: opening a second window re-arms injection for the first one and it
re-injects contexts it already has.

The same file gets this right elsewhere — `check_mcp_fallbacks` keys its once-per-session dedup
on the real `session_id` parsed from hook stdin (`context_loader.py:673-686`). The mechanical
reason for the inconsistency is that `CACHE_FILE` is a module-level constant evaluated at import,
before stdin is read.

## A4 — Test suite writes into the user's real `~/.claude` (defect, reproduced)

`tests/unit/test_loop_guard.py:274`:

```python
def test_missing_claude_dir_auto_creates(self, tmp_path):
    result = run_guard(post_event("Bash", "foo", "err"), tmp_path)
```

`run_guard` sets `CLAUDE_PROJECT_DIR=tmp_path`. Because `tmp_path` has no `.claude/superclaude`,
`claude_base()` falls through to `Path.home() / ".claude"`, and the guard writes
`loop_guard_<md5(tmp_path)>.json` into the developer's real home state directory. `tmp_path`
differs on every run, so every `pytest` run leaves one new orphan file.

Evidence: `~/.claude/.superclaude_hooks/` holds **29** `loop_guard_*.json` files. Twenty-eight are
dated 2026-07-25; one is dated 2026-08-21 16:59 and contains the test fixture's own payload:

```json
{"entries": [{"signature": "Bash::foo", "ts": 1787299168.236928, "kind": "error"}]}
```

That timestamp matches the `uv run pytest` run from the preceding session. The test asserts the
fail-open behavior correctly; the isolation is what is missing.

## A5 — Insight pipeline has produced nothing since 2026-05-08

`.claude/insights.jsonl` holds 138 entries: 131 from 2026-04, 7 from 2026-05, none after
2026-05-08. No pending file exists in the state directory. The hooks themselves are healthy —
`insight_writer.py harvest-from-hook` on `SessionEnd`/`PreCompact` exits 0.

The mechanism is the problem: `cmd_harvest` scans the session transcript for `INSIGHT:` markers
(`insight_writer.py:57-62`), and nothing in the framework causes the model to emit them. The
manual entry point, `/sc:insight`, was typed 5 times in 10 months. The subsystem is 555 lines of
script plus three hook registrations returning zero output for three and a half months.

## A6 — The agent layer is not exercised (30-day window)

23 agents ship. Across all 1,331 transcripts in the window there are 44 `subagent_type`
occurrences and 18 delegating tool calls:

| subagent_type | Calls |
|---|---|
| Explore | 11 |
| general-purpose | 3 |
| self-review | 2 |
| caveman:cavecrew-reviewer | 1 |
| caveman:cavecrew-investigator | 1 |

`self-review` is the only SuperClaude agent invoked at all. The other 22 — `system-architect`,
`security-engineer`, `root-cause-analyst`, `python-expert`, `quality-engineer`,
`refactoring-expert`, `deep-researcher`, `simplicity-guide`, and the rest — have zero
invocations. `.claude/agent-memory/` contains only `.DS_Store` and has not changed since
2026-05-06, which is consistent: agents that never run accumulate no memory.

This corroborates the earlier zero-accumulation investigation with fresh data, and rules out the
remaining "maybe they run but don't write" hypothesis.

## A7 — Vocabulary drift: flags are handled, command names are not

The flag path is in better shape than the raw counts suggest, and the audit's first reading of it
was wrong. `context_loader.py` carries a fuzzy fallback in `resolve_flags` (Levenshtein ≤ 2) and it
works — verified live:

```
--instrospect  →  <!-- SuperClaude flag: --instrospect is not a recognized flag. Did you mean: --introspect? -->
--sequntial    →  <!-- ... Did you mean: --sequential? -->
```

So `--instrospect` (25 uses) is already covered. Three real gaps remain.

**(a) Vocabulary the user kept using after it was removed.** `--parellel` was typed **159** times.
Its target, `--parallel`, is not a valid flag either — it was deliberately deleted as a conceptual
alias for `--delegate` (`context_loader.py:250-255`: *"Conceptual aliases (e.g., --parallel for
--delegate) were removed to keep one canonical name per concept"*). With no valid flag within
distance 2, the fuzzy matcher stays silent. 159 typed uses is a measurement of that removal not
taking; `--architecture` (25) is the same shape.

**(b) Removed flags get no deprecation notice.** `--think` (175), `--think-hard` (145), and
`--effort` (307) were SuperClaude flags, retired in `0cdf20f` ("replace --think flags with --effort")
and `06d972b` ("remove --effort flag, keep ultrathink as native keyword"). Typing them today
produces nothing at all — verified. `--ultrathink` (774) is the one case working as designed: it was
kept deliberately as a native Claude Code keyword, so silence is correct there.

**(c) Command names get none of this treatment.** The 24 misspelled invocations —
`/sc:analayze` (6), `/sc:brainstorem` (4), `/sc:troubleshot` (4), `/sc:brainestorm` (2),
`/sc:imporve` (2), `/sc:trobuleshoot` (2), `/sc:implemnt` (2), `/sc:refesh` (1), `/sc:expain` (1) —
resolve to nothing, and neither does `/sc:workflow`, typed 25 times after
`src/superclaude/commands/workflow.md` was deleted on 2026-06-27 in `16b89c0` and renamed to
`roadmap`, with no alias left behind. Worse than silence: the loader still injects 1,469 bytes of
command context for `/sc:analayze` and `/sc:workflow`, so a nonexistent command looks to the model
exactly like a real one.

## A8 — Stale and unbounded runtime state

In `~/.claude/.superclaude_hooks/` (the legacy user-scope state directory, left behind by the
2026-07-25 runtime-path unification):

- `current_session.txt` — last written 2026-03-21.
- `mcp_fallbacks.json` — last written 2026-03-22, keyed by a 16-hex scheme no longer produced,
  and holding `magic` and `morphllm` entries for MCP servers that are no longer in
  `MCP_SERVERS` (current roster: sequential-thinking, context7, serena, tavily, playwright,
  chrome-devtools).
- 29 orphan `loop_guard_*.json` files (see A4).

In the live project state directory, `mcp_fallbacks.json` gains one top-level entry per session
and is never pruned; `claude_context_be04c4b3.txt` is an orphan from a project key that no longer
resolves. `loop_guard.py` prunes entries *inside* a state file but nothing prunes the files.

## A9 — Inventory drift between docs, memory, and repository

Actual counts: 23 agents, 36 commands, 5 skills, 8 modes, 6 MCP docs, 12 hook scripts.
The session memory index records "35 commands" and "9 MCP servers", and "Serena Memories
(20 total)" against the 5 files actually in `.serena/memories/`. Low severity on its own; it
matters because the index is what gets loaded into context at session start, so the drift is
read as fact every session.

## A10 — Session-start output is fixed boilerplate

`session_init.py:202-207` prints a five-line "Core Services Available" block with five hardcoded
checkmarks on every startup, regardless of whether any of those services are installed, reachable,
or relevant. It is roughly 40–60 tokens per session of text that cannot change and cannot inform
a decision.

---

## A11 — The one other install: `oasis-nakama-dev` (local scope)

Investigated separately because it is the only SuperClaude install outside this repository, and
the only one seeing real (if rare) use — 5 `/sc:` invocations since June 1, last 2026-08-15, with
hook state written as recently as 2026-08-21 17:19.

**What is healthy.** The install is correct and current. Content was synced 2026-08-21 16:24 and
is byte-identical to `src/superclaude/`: 36 commands (zero drift, zero orphans), core, modes, mcp
and the 11 hook scripts all identical. The 23 agents differ by exactly one line each —
`memory: project` → `memory: local` — which is the installer's documented local-scope rewrite, not
drift. The import chain is wired (`CLAUDE.local.md:4` → `@.claude/superclaude/CLAUDE_SC.md`).
Local-scope git hygiene is correct: a marked block in `.git/info/exclude` covers
`.claude/superclaude/`, `.claude/commands/sc/`, the 5 SC skills, `settings.local.json` and
`CLAUDE.local.md`; `git status --untracked-files=all` over the SC paths returns 0 entries.

**A11-a — a shipped hook that never arrives (defect, reproduced).** `prettier_hook.py` is installed
in `.claude/superclaude/scripts/` but is not registered in `settings.local.json`. Twelve SC hook
entries are present; this repository's own install has thirteen, and prettier is the only
difference. The cause is in `install_settings.py:merge_hooks_to_settings`:

```python
has_sc_hooks = any(_is_superclaude_hook(h) for h in existing_array)
if has_sc_hooks and not force:
    existing_hooks[hook_type] = existing_array
    skipped_any = True
    continue
```

The skip is per *event type*, not per hook. Once any SuperClaude hook exists under `PostToolUse`,
no newly-shipped `PostToolUse` hook can ever be added by a non-`--force` install. Reproduced
against the real function with a synthetic settings file:

```
no-force:  "Hooks already exist ... (use --force to update)"  ->  ['loop_guard.py']
force:     "Hooks merged"                                     ->  ['prettier_hook.py', 'loop_guard.py']
```

This is why the discrepancy is invisible: this repository syncs through `make sync-*`, which passes
`--force`, so it always has the full set. Any install updated without `--force` silently freezes its
hook set at whatever existed when it was first written, while its *content* keeps updating. There is
no drift report and no warning — the install looks current because the markdown is current.

**A11-b — `memory: local` points at a directory nothing creates.** Per
`.claude/rules/agent-authoring.md:128`, a local install's agents store memory at
`.claude/agent-memory-local/<agent>/`. That directory does not exist in `oasis-nakama-dev`, and
nothing in `src/superclaude/cli/` creates it. All 23 agents there declare a store that is not
there — consistent with A6, and a second independent reason agent memory stays empty.

**A11-c — same dead subsystems.** `.claude/insights.jsonl` holds 7 entries, all from 2026-04, last
2026-04-08 (A5 again, in a second repository). `mcp_fallbacks.json` has accumulated 4 session-keyed
entries and is never pruned (A8 again).

## A12 — Auto-trigger: the activation path is closed by design

If `/sc:` commands are no longer typed (A1), the remaining way they could run is model
invocation — Claude Code exposes commands with a `description` as model-callable skills. The
transcripts say that path is effectively closed.

Every model-issued `Skill` call in the 30-day window, all 36 of them:

| Skill | Calls |
|---|---|
| artifact-design | 22 |
| new-branch | 4 |
| claude-api / pr-dev / design-taste-frontend | 2 each |
| caveman:caveman / caveman:caveman-compress / artifact-capabilities | 1 each |
| **sc:reflect** | **1** |

The single `sc:` call was not autonomous. It is dispatcher routing: the user typed `/sc:sc` at
2026-07-25 08:34:57Z, typed `2` to pick a menu entry at 08:35:22Z, and the model called
`Skill sc:reflect` seven seconds later. A typed command with an extra hop, not a description match.

The five SuperClaude skills — `confidence-check`, `simplicity-coach`, `verbalized-sampling`,
`ship`, `finishing-a-development-branch` — recorded **zero** invocations. The only SuperClaude agent
to run, `self-review`, ran twice on 2026-07-24 inside a `/goal agent-memory 활용 방안 조사 분석`
session, and one of those two is labelled "Memory write smoke test" — a deliberate probe of the
memory protocol, not routing. At most one organic delegation in a month.

The cause is **not** blanket suppression — an earlier draft of this section claimed all 36
descriptions suppress model invocation, and that was a measurement error: `command-authoring.md`
requires a negative gate ("Do NOT auto-trigger on …") from *both* trigger tiers, so counting the
gate counted compliant auto-triggerable commands too. The actual split:

| Tier | Count | Description wording |
|---|---|---|
| A — auto-triggerable | 22 | "Use when user types `/sc:X`, asks 'Y', or …" + negative gate |
| B — explicit-only | 13 | "Use ONLY when user explicitly types `/sc:X`" + negative gate |
| Hard block | 1 | `auto-improve.md` sets `disable-model-invocation: true` |

Tier A: analyze, brainstorm, business-panel, design, document, estimate, explain, git, help,
improve, insight, plan, pm, prompt, recommend, reflect, research, review, roadmap, spec-panel,
task, troubleshoot.

That makes the finding sharper, not weaker. **Twenty-two commands already carry auto-triggerable
wording, and none of them fired once in thirty days.** The wording tier is not the blocker. Whatever
is stopping them sits further upstream — the descriptions do not win against the neighbouring skills
competing for the same conversational cues, or the model never gets close enough to consider them.

This narrows what P0 can achieve. Packaging as a plugin fixes availability — it puts the commands
in every repository — but it does not create an activation path. And it means the plan's tier task is not "unlock the commands" —
22 are already unlocked. The open question is why an unlocked, well-described command still never
gets picked, which needs a diagnostic before any description rewrite.

---

## Reading of the whole

A3, A4, A5, A7, and A8 are ordinary defects and each is individually cheap to fix. But fixing them
does not address A1. The framework stopped being used in May 2026, and the two structural reasons
visible in the data are (A2) it must be installed per repository while everything competing with
it is installed once per machine, and (A6, A5) large parts of its surface — 22 agents, the insight
pipeline — produce nothing even where it *is* installed.

That points at a scope question rather than a bug list: whether the next round of work is
distribution plus subtraction, or maintenance of the current surface. The plan document takes
that as its first decision.
