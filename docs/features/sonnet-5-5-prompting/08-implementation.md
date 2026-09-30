---
status: complete
revised: 2026-09-30
---

# 08 — Implementation record

Branch `fix/sonnet-5-5-prompting` implements Q1–Q5 of [04-design.md](./04-design.md), with D1–D3 settled on its recommendations: D1 full Sonnet column, D2 canaries at `medium` only, D3 Q5 in. Version 4.16.0+ajitta → 4.17.0+ajitta, because `/sc:prompt` gains a target.

## 1. What shipped

| Proposal | Files | Change |
|---|---|---|
| Q1 | `scripts/context_loader.py`, `tests/unit/test_context_loader.py` | Anchors `## Migrating to Claude Opus 5.5` and `## Migrating to Claude Sonnet 5.5` added. Three tests: both 5.5 ranges located; `claude-opus-5` keeps only its own range (prefix guard); an older reference copy yields no 5.5 keys |
| Q1 | `commands/prompt.md` | The interim Opus 5.5 text now applies only on a reference copy with no Opus 5.5 section, not unconditionally "until upstream adds one" (superseded in 4.18.0: interim text retired, see 09-followups §1) |
| Q2 | `commands/prompt.md` | `sonnet55` flag → `claude-sonnet-5-5`; Sonnet 5.5 sessions infer it; other models never default to the Opus column. New `'claude-sonnet-5-5'` column on all ten axes plus a new Tool use axis. Sonnet request configuration. Removal rows: Thinking incantations (Sonnet JSON exception), Reasoning write-out, Self-check phrasing (replace, not delete), Narration suppression, new Tool discouragement row. Example row, `opus5-verify-inversion` gotcha, and the fallback in `<fact_sourcing>` and `<bounds>` |
| Q2 | `commands/help.md`, `commands/sc.md`, `commands/README.md`, root `README.md` | "Opus 5.5 / Sonnet 5.5 / Fable 5.1" |
| Q3 | root `README.md`, `commands/prompt.md` | The inline-reasoning refusal warning names Sonnet 5.5; new `inline-reasoning-refusal` gotcha |
| Q4 | `utils/__init__.py`, `evals/run_eval.py` | Both refusal docstrings name Sonnet 5.5, scope the no-retry fact to Opus 5.5 and Sonnet 5.5, and give Sonnet 5.5's retry set |
| Q5 | `agents/README.md` | "When Sonnet 5.5" paragraph: official routing split, prices, session paths, and the thinking-block loss on a mid-session switch |

No `.py` file was added or removed, so the component count in `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` is unchanged.

## 2. Departures from 04-design

| Where | 04-design said | Shipped | Why |
|---|---|---|---|
| Q1 item 3 | Keep the interim text, conditioned on the Grep | Same. In addition, `claude-sonnet-5-5` gets no nearest-earlier-section fallback: on a copy without its section, the Sonnet column carries the rewrite | The reference says its Sonnet 5.5 section replaces "all of [Sonnet 5's] effort advice", so reading the Sonnet 5 section in its place would apply retired effort guidance |
| Q2 Tool discouragement, other targets | Delete only when the line contradicts a task that needs tools | Same, plus keep a concrete restriction (no network, a named tool) as a boundary | A3–A5 showed users may mean a real restriction; the row now keeps it rather than dropping it |
| Q2 Verbosity cell | Not listed | "Carried from Sonnet 5: length tracks task complexity" | The 5.5 guide defers to the Sonnet 5 guide on axes it does not cover |

## 3. Verification

- `uv run pytest`: 2638 passed, 26 skipped, 1 failed. The failure is `test_cli_reporting_scope::test_is_healthy_on_a_correct_install` ("superclaude on PATH"), which fails identically on unmodified `master` on this VM (environment, not this change). Before the change: 2635 passed; the 3 new tests account for the difference.
- `prompt.md` mirror table: 13 rows × 4 columns, checked by counting cell separators on every row.

### Canaries (`--model sonnet` → `claude-sonnet-5-5`, Claude Code 2.1.284, `--permission-mode plan`, default effort)

Each ran in a fresh scratch repo with `superclaude install --scope project` from this branch. Criteria were written before the runs.

| Run | Input | Criteria | Result |
|---|---|---|---|
| C1 | `./agent.md --target api` (the 03a A4 prompt), no reference | Infers `claude-sonnet-5-5`; replaces, not deletes, the double-check line; deletes the tool line under its row; `effort: medium` | **Pass**. "The session model is Sonnet 5.5, so I used the Sonnet column". Double-check line → real-check requirement keeping tests and build. Tool line deleted as "Tool discouragement". Keep-working and scope lines added |
| C2 | Korean JSON-calculation prompt with `Think step by step.`, no reference | Incantation replaced by the single think-first line at the end | **Pass**. Replaced with `Think the problem through before you answer.`, placed last, citing the Sonnet 5.5 exception; `max_tokens` 128,000 correctly not carried over to a non-agentic workload |
| C3 | `./agent.md --model opus55 --target api`, no reference | Unchanged Opus behavior | **Pass**. Opus column; double-check deleted as Opus self-check phrasing with tests and build kept as done-criteria; unattended-run slot as before |
| C4 | `./agent.md --target api`, reference `8a1541c` in `.claude/skills/claude-api/shared/` | Reads the Sonnet 5.5 section | **Pass**. Read `## Migrating to Claude Sonnet 5.5` L2195-2225 and quoted the verification paragraph verbatim from it |

Costs: $0.23–0.25 per run. Raw outputs stayed in the session scratchpad.

## 4. Observed, not acted on

- C1 and C4 paraphrased or slotted the guide's keep-working and no-unrequested-additions paragraphs, because those sit in the prompting guide, not in the reference's behavioral-shifts range. Correct under the command's no-invention rule; a later reference release may carry them.
- In the no-reference runs the model ran `find /` for the reference and found pytest fixture copies and sibling scratch copies; it rejected them as sources (2/2 explicitly). The command's glob guidance does not scope the search; left as is, since the rejection held.

## 5. Independent review and fixes (4.17.1)

An independent `claude -p --model opus --effort high` reviewer (resolved `claude-opus-5-5`, 53 turns, $3.60) checked the change in a disposable copy. The copy held the diff, 04-design and the four official sources, but not this record or the author's verdict. It found no high-severity defects. Each finding below was re-checked against the cited lines before it was acted on.

| # | Finding | Severity | Resolution |
|---|---|---|---|
| D1 | The prefix-guard test passed with prefix matching restored: `next()` takes only the first match, so the fixture could not fail | medium | The fixture now holds only the 5.5 section and asserts `claude-opus-5` is absent. Mutation-checked: with `startswith(anchor)` the test fails |
| D2 | The Sonnet column told the rewrite to add three guide paragraphs that are not on the machine, with no sourcing rule. Runs paraphrased them | medium | Each is now a `[FILL: …]` slot naming the guide URL, as the Opus 5.5 precedent does. Canary C5 emitted both slots |
| D3 | The `<fact_sourcing>` closing sentence and the `facts-not-memory` gotcha omitted the new Sonnet-column exception | medium | Both now name it |
| D4 | The `opus55` example still said the Opus 5 section is read in place of the Opus 5.5 one | medium | It now names the Opus 5.5 section, or the Opus 5 section on an older copy |
| D5 | The spec's 64,000 citation from the reference was missing | low-medium | Added, with "cite whichever section was read" |
| D6 | The interim Opus 5.5 condition excluded machines with no reference at all | low | The condition now covers "no copy, or a copy without the section" |
| D7 | The Narration row gave a causal claim ("go quiet behind it") that the sources do not make | low | The row now cites the guide's instruction to remove such lines |
| D8 | The positioning quotes were attributed loosely | low | The row now credits the announcement and the prompting guide separately |
| D9 | The docstrings said "Sonnet 5.5 retries"; it is server-side fallback that retries. The two copies had drifted | low | Both copies now say server-side fallback and match each other |
| D11 | The feature README summary still read as pre-fix | low | Updated |
| D13 | The real-check cell was unscoped, and `display` had no adaptive-thinking condition | low | Scoped to prompts that change code; `display` is now conditioned on adaptive thinking (and `between_tools` rejects it) |
| D10 | "Never default to the Opus column" goes beyond Q2.1 | low | **Kept, as a recorded departure.** 03a probes A2–A5 showed that the Opus default inverts the verification edit. On a non-5.5 session, asking or naming a non-Opus assumption is the safe branch |
| D12 | `okf/` copies still say "Opus 5 or Fable 5" | low | **Out of scope.** Stale since 2026-08-31, before this change |
| D13c | "near-miss tool-name casing" is listed as a native failure mode although the harness fix was rejected | low | **Kept.** Listing a failure mode is description, not a harness change |

After the fixes: `uv run pytest` gives 2638 passed and 1 failed. The failure is the pre-existing doctor PATH check; the reviewer traced it to the check excluding the venv's own `bin`. ruff check and format are clean, and the mirror table is still 13 rows × 4 columns.
