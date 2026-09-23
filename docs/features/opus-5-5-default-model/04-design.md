---
status: implementing
revised: 2026-09-23
---

# 04 — Improvement proposals

Claude Code already makes Opus 5.5 the default for almost every installed user, so SuperClaude must not set a model. The default holds unless something overrides it: a `model` saved in user settings (which `/model` writes), a `model` value in project or managed settings, `ANTHROPIC_MODEL` (which "returns to that variable's model on the next launch, whatever you saved with `/model`"), `ANTHROPIC_DEFAULT_MODEL`, an organization default model, or a resumed session (model-config). The work is to stop the framework from contradicting that default and to give Fable 5.1 a clear opt-in path the user controls. Evidence is in [02-research.md](./02-research.md) (external) and [03-analysis.md](./03-analysis.md) (repository, surfaces S1–S13).

Every proposal below passed the [R18] question "is the system broken without this?". The ones that failed it are listed in §3 with the reason, so they are not re-proposed later.

## 1. Proposals

Ordered by what breaks today, then by cost.

### P1 — Fix the agent model-routing section (S6) · ready now

**Broken today:** `agents/README.md:90` states the subagent resolution order Claude Code dropped in v2.1.251, and `:92` tells readers to pin with `model:` frontmatter, which the project convention forbids.

**Change** (`src/superclaude/agents/README.md`, "Model Routing"):

- `:90` → `Resolution order: per-invocation \`model\` parameter > frontmatter \`model:\` > \`CLAUDE_CODE_SUBAGENT_MODEL\` > main conversation model (Claude Code v2.1.251+).`
- `:92` → replace the frontmatter override with the user-controlled paths, each with how long it lasts: `claude --model fable` for one session only; `/model fable`, which Claude Code saves to user settings so later sessions also start on Fable ("Choosing one with `/model` saves it as the selected model in your user settings, so later sessions start on it", model-config), undone with `/model default`; the `/model` picker with `s` on a row, which switches "for this session only and leave[s] your default unchanged", the only interactive mid-session path that leaves the saved default alone; a request to run one delegation on Fable, which becomes the Agent tool's per-invocation `model: "fable"`; `CLAUDE_CODE_SUBAGENT_MODEL` for every subagent. Recommend `--model fable` as the "when needed" path, because it cannot leave a user on Fable by accident.
- Add one paragraph, "When Fable 5.1", quoting the official criterion: "Most workloads start with Claude Opus 5.5". Move to Fable 5.1 when work at `xhigh`/`max` still falls short on demanding reasoning or long-horizon agentic tasks; its fit is "tasks larger than a single sitting". Name the cost (2.5× Opus 5.5 at list input and output, $10/$50 against $4/$20 per MTok; cache reads $0.25 against $0.20, 1.25×, and the announcement says cache reads "make up the majority of agentic and coding work costs") and the billing note: when a plan bills Fable to usage credits, `-p` mode and the Agent SDK bill it without the consent prompt interactive sessions show.

**Verify:** `uv run pytest` (markdown lint and doc-structure tests); `grep -n 'per-invocation `model` parameter > frontmatter' src/superclaude/agents/README.md` returns one line (the old line does not match it).

### P2 — Keep delegation from escalating to Fable unasked (S7) · ready now, small

**Broken today:** the Agent tool accepts `model: "fable"` per invocation, and nothing in the framework says who decides that. A model-initiated escalation costs 2.5× at list input/output price (1.25× on cache reads), and where the plan bills Fable to usage credits, `-p` mode and the Agent SDK bill it with no consent prompt (Claude Code model-config docs). The official move-to-Fable criterion is the user's own evaluation showing a shortfall at `xhigh`/`max`, a signal the framework does not have.

**Change** (`src/superclaude/core/rules/RULES_DELEGATION.md`, `<sub_agent_decision>`, one sentence after "Spawn discipline"):

> Model: omit the Agent tool's `model` parameter so the delegate falls through to its own frontmatter model, `CLAUDE_CODE_SUBAGENT_MODEL`, or the session model, in that order; pass a model only when the user asked for it for that work. Fable is the case that matters: it is priced above Opus 5.5, and headless runs can bill it to usage credits without a consent prompt.

(Amended in implementation review: the first draft said "2.5× Opus 5.5 at list price", which leaves out the 1.25× cache-read ratio; the rule now states no ratio, and `agents/README.md` carries the prices.)

This extends the existing agent-level rule (no `model:` pins, `agents/README.md:86-88`) to the per-invocation level. It adds a stated reason, not a new mechanism.

**Verify:** `uv run pytest`; the loader-injection tests for `RULES_DELEGATION.md` still pass. Behavioral check (optional): one headless delegation prompt on `--model claude-opus-5-5` with `--output-format stream-json`, confirming that the Agent call carries no `model` field; and a second prompt in which the user asks for Fable on that delegation, confirming the call carries `model: "fable"`.

### P3 — Give `/sc:prompt` an Opus 5.5 target (S1, S2, S5) · ready now

**Broken today:** the command's targets are `claude-opus-5` and `claude-fable-5-1`, while the default session is `claude-opus-5-5`. The `model-required` gotcha exists because an unresolved target yields opposite edits. On an Opus 5.5 session the command currently survives only through the model's own judgment (03-analysis §3, n=1).

**Change** (`src/superclaude/commands/prompt.md`):

1. **Target set: flags resolve to model IDs, one rule on IDs.** Add flag `opus55`. Every flag first resolves to a model ID: `opus5` → `claude-opus-5`, `opus55` → `claude-opus-5-5`, `fable51` and the legacy `fable5` → `claude-fable-5-1` (`prompt.md:15` already maps `fable5` this way, because Fable 5 prompts run unchanged on 5.1). One rule then applies to IDs only: read the ID's own reference section, or, when it has none, the nearest earlier section of the same family. So `claude-opus-5` reads Opus 5, `claude-opus-5-5` reads Opus 5 until upstream adds its own section, and `claude-fable-5-1` reads its two Fable 5.1 sections as today. No flag carries an exception. The mirror table keeps one column per family (Opus, Fable), and request configuration follows the ID, so `claude-opus-5` gets `high` and `claude-opus-5-5` gets `medium` (item 3 settles how). Update the description (`:2`), mission (`:8`), syntax (`:11`), flow step 2 (`:15`), table header (`:28`), the `opus5-verify-inversion` gotcha (`:109`) and example rows (`:100-102`).
2. **Session inference made explicit** (flow step 2): an Opus-family session resolves to the Opus column, a Fable-family session to the Fable column, and the one-line assumption names the column used. This writes down what the probe showed the model already doing.
3. **Missing reference section** (`<fact_sourcing>` and `<bounds><fallback>`): write the item-1 fallback into the command, and require the report to state that the target had no section and which section was read instead. Today the rule covers only a reference missing from the machine, and 03-analysis §4 shows the reference present with no 5.5 section.

   This makes the mirror table a source for the Opus 5.5 rows below, which `prompt.md:26` ("This table is a mirror, not a source") and the `facts-not-memory` gotcha (`:112`) currently forbid, and 03-analysis §4 names the same conflict. The change therefore amends both places explicitly instead of working around them: rows marked `interim (Opus 5.5 prompting guide)` are allowed as a source only while the reference has no Opus 5.5 section, and they are deleted in the P4 change that adds the anchor. The `interim` mark applies only to `<model_delta>` rows and request-config values, never to `<removal_targets>` rows, which `prompt.md:43` calls "the command's own, not a mirror". Precedence for `claude-opus-5-5` while it reads the Opus 5 section: on an axis an interim row names, the interim row wins over the fallback section; on every other axis the fallback section wins over the mirror, as `prompt.md:26` says today. Without this, the Opus 5 section's `high` default and its thinking-disabled guidance would override the 5.5 facts. The Opus column's existing rows are Opus 5 facts: the guide says existing Opus 5 prompts "should perform well without changes", which is about prompts continuing to work, not about every Opus 5 delta holding on 5.5. The column header therefore reads `Opus (5 verified; 5.5 carried from 5 unless marked)` until P4, not `claude-opus-5-5`.
4. **Changes drawn from the Opus 5.5 prompting guide.** Two kinds, handled differently.

   Permanent detector rows in `<removal_targets>` (the command's own table, kept through P4). Each row's action names the targets it applies to:
   - "Thinking incantations": add `think carefully` to the signal. The row's existing action ("Delete — redundant on thinking models") already covers every target; the guide adds "consider removing them for Claude Opus 5.5".
   - New row "Reasoning write-out": signals `write out your reasoning`, `show your reasoning in the response`, `explain your chain of thought`. Action: delete for `claude-opus-5-5` and `claude-fable-5-1`, whose classifiers carry the `reasoning_extraction` category (guide line 83; `utils/__init__.py:313-316` lists it for Fable 5.x), and on `--target api` set `thinking.display: "summarized"` to read the reasoning instead (guide line 83). Server-side fallback does not retry that category. Leave it for `claude-opus-5`, where the category does not exist and a write-out can stand in for disabled thinking.
   - New row "No-thinking rule": signals `do not think`, `respond without thinking`, `skip reasoning, just answer`. Action: delete for every target. `claude-opus-5-5` and `claude-fable-5-1` cannot turn thinking off (model-config: "You can't turn thinking off on Opus 5.5 or the Fable models"; guide line 54: "remove the no-thinking rule either way"); for `claude-opus-5` the migration reference says "Delete any instruction telling the model not to think or not to reason. That kind of rule *increases* tag leakage rather than suppressing it" (`model-migration.md:972`). For `claude-opus-5-5` only, keep "Answer directly without deliberating." when it sits beside `effort: low`: the guide offers that line for latency after lowering effort, provided quality is measured when it is added (line 52). On `--target api`, move a deleted rule's intent to `effort: low` in the request config, overriding the target's default effort (guide line 44: lowering effort reduces thinking "more reliably than prompt instructions do"). (Amended in implementation: the first draft kept the rule for `claude-opus-5`, which the reference contradicts, and left the keep clause unscoped.)

   Interim rows (mirror and request-config, deleted by P4), each citing the prompting-guide URL:
   - Delta row "Task completion †": for Opus 5.5 on fully unattended `--target api` runs, add the guide's unattended-run paragraph, present from the session's first request, as a `[FILL: …]` slot naming its URL, because the command has no tool that can read the guide; leave it out of human-in-the-loop prompts (the guide's own condition).
   - Not carried as interim rows: the guide's additive, conditional lines ("explore broadly with tool calls" for multi-app agents, "treat that answer as done" for chat, the `<pasted_content>` note, elapsed-time signals). They add text rather than change an edit's direction, and each applies only to one kind of harness, so writing them in now would widen the mirror-as-source exception that item 3 limits. They wait for the P4 upstream section.
   - Request-config (`--target api`, `opus55`): effort defaults to `medium`, and `xhigh`/`max` only where "you've measured a quality gain"; thinking cannot be disabled; `tool_choice` `any`/`tool` returns 400; text between tool calls now arrives in `thinking` blocks whose text is empty at the default display, so a harness that shows progress sets `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`); changing the top-level `effort` between requests invalidates the prompt cache, and a per-message effort change (beta) keeps it; `max_tokens` 128,000 for long agentic turns. Sources: What's new in Opus 5.5 (thinking cannot be disabled, forced `tool_choice` errors, text between tool calls "until it sets a `display` value that returns the text"); the prompting guide (`medium` default and the `xhigh`/`max` line, lines 38-43; `max_tokens`, line 42; cache invalidation, line 46; `display: "updates"`, lines 71 and 91). The first draft also carried a `"summarized"` note; the reference states it for Fable 5.1 only (`model-migration.md:1730`), so it is not an Opus 5.5 interim fact and was dropped.
5. **Summaries** (`commands/help.md:54`, `commands/sc.md:54`, `commands/README.md:80`): "Opus 5 / Fable 5.1" → "Opus 5.5 / Fable 5.1".

**Verify:**
- `uv run pytest`.
- Canary probes per the `/sc:prompt` probe method: run on Opus (`--model claude-opus-5-5`), with prompts from two unrelated domains, one Korean and one English. Include one prompt that carries `think carefully`, a reasoning write-out line and a no-thinking rule, run with `--model opus55` (expect all three removed, each tied to its row) and again with `--model opus5` (expect `think carefully` and the no-thinking rule removed, the write-out kept); pass the Korean one as a file path, because pasted inline it is declined by the session's `reasoning_extraction` classifier before the command runs ([08-implementation.md](./08-implementation.md) §4); one prompt with "Answer directly without deliberating." next to an `effort: low` note (expect it kept); and one clean prompt (expect "clean", no diff).
- `grep -n 'opus55' src/superclaude/commands/prompt.md` returns the syntax line, flow step 2 and at least one example row; `grep -n 'legacy alias' src/superclaude/commands/prompt.md` returns only the `fable5` mapping.

### P4 — Add the Opus 5.5 anchor when upstream publishes it (S3, S4) · gated on upstream

**Broken later, not today:** `context_loader.py:966` anchors on `## Migrating to Claude Opus 5`. Once the `claude-api` skill adds an Opus 5.5 section, the hook will keep pointing `/sc:prompt` at the Opus 5 range.

**Change**, when the section exists: add `("claude-opus-5-5", "<exact heading>")` to `_MIGRATION_REF_ANCHORS`, copying the heading verbatim from the file rather than guessing it now, and extend the fixture in `tests/unit/test_context_loader.py:774-820`. If upstream publishes both a migration section and a delta-only "from Claude Opus 5" section, as it did for Fable 5.1, add both headings as `claude-opus-5-5` tuples, the same way `context_loader.py:967-968` carries two Fable tuples. The same change deletes the P3 rows marked `interim` (model delta and request-config only; the P3 detector rows stay), restores the "mirror, not a source" wording at `prompt.md:26`, and renames the Opus column header to `claude-opus-5-5` if the new section confirms the carried rows.

**Trigger:** `grep -n '^## .*Opus 5\.5' ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/claude-api/shared/model-migration.md` returns a heading (anchored so table rows mentioning Opus 5.5 do not match). Until then the anchor would be a guess, and the existing "anchors have moved" note already covers a heading that changes.

### P5 — Correct the refusal docstring (S9) · trivial

Two copies carry the same sentence: `utils/__init__.py:313` ("Claude Fable 5.x safety classifiers") and `evals/run_eval.py:289` ("Fable 5.x safety classifiers"). Change both to "Safety classifiers on Fable 5.x, Opus 5.5 and Opus 5". Add that the `reasoning_extraction` category is not retried by server-side fallback, so a caller that sees it should change the prompt rather than retry. This is a docstring change only.

**Verify:** `uv run pytest tests/unit`. The evals copy is pinned to this function behaviorally (`tests/unit/test_eval_harness.py:522-542` compares return values), so a docstring edit cannot break the pin, and equally nothing catches the two docstrings drifting apart; edit both in the same commit. `grep -rn "Fable 5.x safety" src evals` returns nothing afterwards.

### P6 — Report the Claude Code version in `superclaude doctor` (S13) · optional

The goal fails silently in two cases: Claude Code older than 2.1.280 (default Sonnet 5 or Opus 5), and, more likely, a `model` key saved in user settings, which `/model` writes and which then outranks the default in every later session. A doctor section that reports every source that can replace the default (a `model` key in user, project, local or managed settings, `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_MODEL`, and an organization default when visible) is the more useful check; the `claude --version` warning below 2.1.280 is secondary. It must warn, never fail: SuperClaude works on older versions, and the check is informational.

**Necessity:** weak. Nothing in SuperClaude breaks, only the user's expectation, and Claude Code's own startup line names the model. Recommended only if doctor is meant to cover "am I getting the intended model".

### P7 — Name Opus 5.5's frontend defaults in `frontend-architect` · after a two-path probe

**Broken today:** `agents/frontend-architect.md:38` fights older model defaults by name ("Inter/Roboto/Arial/system fonts, purple gradients on white or dark") and describes one house style ("cream off-white, serif, terracotta") as never to auto-apply. The prompting guide says Opus 5.5 "falls back on a few default styles" when asked for frontend work "without design direction", and its example instruction names five patterns to avoid: "a cream or off-white background, italic accent words in headlines, numbered "01/02/03" section labels, monospace labels, or pill-shaped buttons" (lines 161-164). The file covers only the cream background. The guide also says a general instruction "mostly swaps one default for another", which is what the file's last item, "cookie-cutter layouts without context-specific character", is.

**Change** (`src/superclaude/agents/frontend-architect.md`, `<aesthetics>`, one sentence rewritten):

- Extend the house-style clause to the patterns the probe below actually observes from the guide's list (italic accent words in headlines, numbered section labels, monospace labels, pill-shaped buttons). They stay under the existing "Never auto-apply" stance, because the agent treats defaults as "starting points, not policy": they are fine when the brief asks for them.
- Delete "cookie-cutter layouts without context-specific character". It names no pattern, and by the guide's finding it changes which default appears, not whether one does.

**Verify:** the agent already supplies its own design direction on an ambiguous brief: it "proposes 4 distinct visual directions (bg hex, accent hex, typeface, one-line rationale) before building" (`frontend-architect.md:38`). The guide's fallback styles apply only where no direction exists, so one ambiguous-brief probe may never reach them, and in a headless run it may stop at the four proposals without building a page. Probe both paths on `--model claude-opus-5-5`, delegating to `frontend-architect` with a brief such as "a landing page for a small accounting firm":
- Path A, direction proposal: record whether the four proposed directions themselves lean on the guide's five patterns (for example, cream backgrounds or monospace type across several of them).
- Path B, direct build: pick one proposed direction and ask for the page, then record which of the five patterns appear in elements the chosen direction did not specify (section labels, button shape, headline emphasis).
- Name only patterns observed in either path, as the guide advises: "check which styles the first result used instead, and extend the list if needed." After editing, rerun both paths and confirm the named patterns are absent and no new house style replaced them wholesale.
- `uv run pytest` (agent frontmatter and content tests).

**Necessity:** unproven until the probe runs. The four-direction step already counters default styles on ambiguous briefs, so the gap is at most the elements a chosen direction leaves unspecified, plus the direction proposals themselves. If neither path shows a guide pattern, P7 reduces to deleting the general item.

(Probe outcome, [08-implementation.md](./08-implementation.md) §3: in delegated headless runs the four-direction step never fired, because the delegating session told the agent to pick defaults, so the named-pattern clause carries more weight than this paragraph assumed.)

## 2. Decisions for the user

- **D1 — auto-improve mutator default** (`scripts/auto_improve/mutator.py:19`, `coordinator.py:54`, `cli.py:80`; S8). It is `sonnet` by design ("pick cheap for volume"). Prices per MTok (Fable 5.1 overview): Sonnet 5 $2 input / $10 output / $0.20 cache read (10% of input); Opus 5.5 $4 / $20 / $0.20 (5% of input). Input and output are half; cache reads are equal, and the announcement says cache reads "make up the majority of agentic and coding work costs". The mutator is an agentic `claude -p` loop, and Opus 5.5 defaults to `medium` effort against Sonnet 5's `high`, so the real per-cycle gap is well under 2× and unmeasured. Sonnet 5.5 is announced for "the coming weeks". Recommendation: keep `sonnet` as an unmeasured cost choice, and revisit with one measured run of each model on the same eval before Sonnet 5.5 ships or the default is questioned. If it changes to `opus`, the unattended-run early-stop behavior in 02-research §2 applies to the mutator's `claude -p` loop and needs its own check.
- **D2 — P6 in or out.**
- **D3 — billing note on the Fable example.** `commands/auto-improve.md:48` shows `--mutator-model fable` for a one-hour headless loop, the exact case where Claude Code bills Fable to usage credits without a consent prompt. Recommendation: add that note to the example row or to the `mutator-model-freeform` gotcha (`:40`).

## 3. Considered and rejected

| Idea | Why not |
|---|---|
| Installer writes a `model` key (`opus`, `opus[1m]` or a full ID) | Claude Code already defaults to Opus 5.5 with the 1M window on every first-party plan, so the key adds nothing there. It would override the choice of every user and team the framework serves, including Foundry and organization defaults, and it would freeze a choice Claude Code updates on its own ("Aliases … update over time"). The window is not a reason either way: `opus` and `opus[1m]` both run with 1M (03-analysis §1) |
| Installer writes an `effortLevel` | A top-level user-settings `effortLevel` is ignored for Opus 5.5, and a project-level one applies to every model, Fable included. Effort is Claude Code native (`context_loader.py:407`) |
| Re-add agent `model:` pins (e.g. `fable` for deep-researcher) | Reverses the 2026-08-25 de-pin, which was made because a pin overrides the user's cost-vs-quality choice and misroutes after the next release. The official Fable criterion is a measured shortfall, not an agent type |
| Recommend `opusplan` | It executes on `sonnet`, which contradicts "default Opus 5.5" |
| Rewrite `--introspect` / `--vs cot` for `reasoning_extraction` | Probed on Opus 5.5 with no decline (03-analysis §3b); both ask for decisions and rationale, not a thinking transcript |
| Adjust visual-input scaffolding for Opus 5.5 (guide "Tools for complex visual inputs") | Not applicable: `src/superclaude` ships no image-cropping, resolution or visual-input scaffolding to re-test |
| Change `--uc` / `--safe-mode` thresholds for the 1M window | They are percentages of the window, so nothing to change |
| Retune Spawn discipline for Opus 5.5 | No official statement on 5.5 spawn frequency; the "delegates far more effectively" line is a customer quote |

## 4. Deferred, with the event that would reopen them

- **Elapsed-time signals in Workflow fan-out.** The prompting guide reports faster multi-agent work when the lead sees a time budget. Reopen once a Workflow run is measured with and without the signal.
- **Unattended early-stop paragraph for headless runners** (auto-improve, parallel-A/B). Reopen if D1 moves the mutator to Opus, or if a parallel-A/B run on Opus 5.5 shows `end_turn` before the task is done.
- **Dev-tree stale copies outside `src/`:** `.claude/rules/agent-authoring.md:33` shows `model: sonnet` as the example value, and `evals/README.md:72` uses a Fable canary example. Both are out of the requested scope and worth a separate docs pass.

## 5. Change set and verification summary

| Proposal | Files | Size | Gate |
|---|---|---|---|
| P1 | `agents/README.md` | ~8 lines | pytest |
| P2 | `core/rules/RULES_DELEGATION.md` | 1 sentence | pytest; optional stream-json probe |
| P3 | `commands/prompt.md`, `help.md`, `sc.md`, `commands/README.md` | ~30 lines | pytest; Opus canaries in 2 domains / 2 languages |
| P4 | `scripts/context_loader.py`, `tests/unit/test_context_loader.py` | 1 tuple + fixture | upstream heading exists; pytest |
| P5 | `utils/__init__.py`, `evals/run_eval.py` | docstring ×2 | pytest; grep shows no old sentence |
| P6 | `cli/doctor.py` + test | ~30 lines | user decision; pytest |
| P7 | `agents/frontend-architect.md` | 1 sentence | two-path probe before and after; pytest |
| D3 | `commands/auto-improve.md` | 1 line | user decision; pytest |

No `.py` file is added or removed, so the component count in `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` does not move. P1–P3, P5 and P7 are content or docstring changes (P5 also touches `evals/`, outside `src/`) that can land on one `docs/` or `fix/` branch off `integration`. P4 waits for upstream.
