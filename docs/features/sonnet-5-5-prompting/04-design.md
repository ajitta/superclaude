---
status: complete
revised: 2026-09-30
---

# 04 — Application proposals

Sonnet 5.5 needs no kernel change. `core/RULES.md` already asks for the behavior that the guide's G2, G3, G5 and G11 prompt for ([03-analysis.md](./03-analysis.md) §1), and on the one probe that could separate the arms the kernel supplied a check the bare model skipped ([03a](./03a-analysis-probes.md) P-C). The work is in `/sc:prompt`, which today rewrites every Sonnet session's prompts as Opus prompts and inverts the verification edit ([03](./03-analysis.md) §3), plus a few text copies that name only Opus 5.5.

Each proposal passed the [R18] test "is the system broken without this?". §3 lists the ideas that failed it, with the reason, so they are not re-proposed.

## 1. Proposals

Ordered by what is broken today, then by cost.

### Q1 — Add Opus 5.5 and Sonnet 5.5 anchors; retire the interim text (S8, S9) · ready now

**Broken today (for users who update the skill):** upstream `model-migration.md` at `8a1541c` has `## Migrating to Claude Opus 5.5` and `## Migrating to Claude Sonnet 5.5`. The hook still points an `opus55` rewrite at the Opus 5 range. The command then applies `interim` text that its own rule says is valid "only while the reference has no Opus 5.5 section". This is the prior feature's P4, whose trigger has now fired (02-research §5).

**Change:**

1. `scripts/context_loader.py` `_MIGRATION_REF_ANCHORS`: add `("claude-opus-5-5", "## Migrating to Claude Opus 5.5")` and `("claude-sonnet-5-5", "## Migrating to Claude Sonnet 5.5")`, in file order, copied verbatim from the reference. The whole-line match needs no change (03 §4).
2. `tests/unit/test_context_loader.py:774-875`: add both headings to the fixture, and assert that `claude-opus-5` still resolves to its own range and not the 5.5 one (a prefix-collision guard, the same trap the reference's "Verify the Migration" section warns about for model IDs).
3. `commands/prompt.md`: keep the `interim (Opus 5.5 prompting guide)` text, but condition it the other way. It applies only when the Grep for the target's own heading finds none, which is the rule `<fact_sourcing>` already states. This keeps machines on an older skill copy working. Delete the interim text outright in a later release, once the skill copy on a fresh install is known to carry the section.

**Verify:** `uv run pytest tests/unit/test_context_loader.py`. Run `migration_reference_ranges()` on a current reference and confirm it returns four keys, including `claude-sonnet-5-5 L2195-2225` (line numbers move with each upstream release; check the keys, not the numbers). Canary: `/sc:prompt --model opus55` on a machine with the updated skill reports that it read the Opus 5.5 section, not the fallback.

### Q2 — Give `/sc:prompt` a Sonnet 5.5 target (S1–S7, S16) · ready now; needs Q1 for the reference path

**Broken today:** a Sonnet 5.5 session has no target. Probes A2–A5 assumed `claude-opus-5-5` 4/4, deleted a verification requirement under the Opus rule 2/2, and told the user "Opus self-verifies unprompted". No flag lets the user name Sonnet.

**Change** (`src/superclaude/commands/prompt.md`):

1. **Flag and inference.** Add `sonnet55` → `claude-sonnet-5-5`. Flow step 2: a Sonnet 5.5 session resolves to that ID. Any other Sonnet or Haiku session keeps today's rule (ask, or state the assumption), because the reference's Sonnet 5 and Haiku sections are not in the command's scope.
2. **Mirror column.** Add a `'claude-sonnet-5-5'` column. It holds direction only and defers to the reference's Sonnet 5.5 section when that section is on the machine, the same contract as the other columns (`prompt.md:26`). Rows, each sourced from 02-research §3:

   | Axis | `'claude-sonnet-5-5'` |
   |---|---|
   | Verification instructions | Replace self-check slogans with the guide's real-check paragraph (run a check that exercises the change; syntax-only does not count; say which check did not run). Most needed at `low` effort (G11) |
   | Subagent delegation † | No 5.5-specific direction below `xhigh`. At `xhigh`/`max`, add the stop-and-report line that stops self-started reviewer subagents (G4) |
   | Tool-call batching | No documented delta |
   | Progress updates | Delete hold-for-final lines; a when-and-what line only if the interface shows text between calls (G8) |
   | Task completion † | At `low`/`medium` on agentic coding, add the guide's two-paragraph carry-through block; use only its second paragraph where scope is the concern (G2, G3) |
   | Prescriptiveness † | Scope line for unrequested tests, docs and files (G3); for open-ended requests, "ideas or a plan, then stop" (G5) |
   | Tool use | Delete tool-discouraging lines; where a search tool exists, add the guide's check-current-specifics line (G9) |
   | Native failure modes | Early check-in at `low`/`medium`, unrequested supporting files, self-started review at `xhigh`/`max`, answers from training knowledge, skipped checks at `low` |

3. **Removal rows.**
   - "Reasoning write-out" (`:50`): add `'claude-sonnet-5-5'` to the delete list, with the same `display: "summarized"` note (G14).
   - "Thinking incantations" (`:49`): add one exception. For `'claude-sonnet-5-5'`, when the prompt asks for a JSON answer to a multi-step task under adaptive thinking, replace the incantation with the guide's single line "Think the problem through before you answer." at the end of the system prompt. Keep deleting it everywhere else (G7).
   - "Self-check phrasing" (`:52`): for `'claude-sonnet-5-5'`, replace rather than delete. Swap the slogan for the real-check paragraph. Update the `opus5-verify-inversion` gotcha (`:114`) to say that the inversion is Opus-only and that Sonnet 5.5 runs in the opposite direction.
   - "Narration suppression" (`:55`): add `'claude-sonnet-5-5'` (G8).
   - New row "Tool discouragement": signals `only use tools when strictly necessary`, `minimize tool calls`, `avoid unnecessary tool calls`. Action: delete for `'claude-sonnet-5-5'`, which follows them literally (G9). For the other targets, delete only when the line contradicts a stated task that needs tools, which is what A3–A5 did by judgment.
4. **Request configuration** for `'claude-sonnet-5-5'` on `--target api`: effort `medium` for agentic coding and multistep tools, `low` for chat, classification and extraction, and `high` when unstated (the API default), with `xhigh`/`max` only where a gain was measured. Thinking-off routes send `between_tools` at `high` or below; the reference prefers adaptive thinking at `low` effort first. `tool_choice` `any`/`tool` returns 400. `display: "updates"` for progress UIs. `max_tokens` 128,000 for agentic coding (the prompting guide; the reference says 64,000 is "a reasonable starting point" for `between_tools` routes, so cite whichever section was read). Treat `stop_reason: "max_tokens"` as failed for structured JSON (G7).
5. **Summaries** (`help.md:54`, `sc.md:54`, `commands/README.md:80`, root `README.md:684`): "Opus 5.5 / Sonnet 5.5 / Fable 5.1".

**Verify:**

- `uv run pytest`: markdown and doc-structure tests, plus the `grep-longline-blindspot` caution for `prompt.md:2`.
- Canaries on `--model sonnet`, in two unrelated domains, one English and one Korean:
  - `./agent.md --target api` (the A4 prompt). Expect `sonnet55` inferred and named. Expect the double-check line replaced by the real-check paragraph, not deleted. Expect the tool line deleted under its row. Expect `effort: medium`.
  - A chat prompt with a JSON-output multi-step task and `think step by step`. Expect the incantation replaced by the single think-first line.
  - The same `agent.md` with `--model opus55`. Expect today's Opus behavior, unchanged.
  - Write each canary's criteria before reading its output, as the prior feature's 08 §3 did.

### Q3 — Name Sonnet 5.5 in the inline-refusal warning (S10) · trivial

**Broken today:** root `README.md:684` warns only Opus 5.5 users to pass reasoning-requesting prompts as a file path. Probe A1: Sonnet 5.5 refused the same input inline (`[reasoning_extraction]`), and the turn was billed.

**Change:** "On an Opus 5.5 or Sonnet 5.5 session, pass a prompt that asks for written-out reasoning as a file path: pasted inline, it can be declined before the command runs." Add the same sentence as a `<gotchas>` line in `prompt.md`, where a Sonnet user reads it at invocation. It cannot prevent the refusal (the refusal happens on the user turn, 03a P-A), but it tells the user the cause.

**Verify:** `uv run pytest`; `grep -n "Sonnet 5.5" README.md src/superclaude/commands/prompt.md` shows both.

### Q4 — Refusal docstring (S11) · trivial

Change `utils/__init__.py:313-317` and the pinned copy in `evals/run_eval.py` to name Sonnet 5.5 with Fable 5.x, Opus 5.5 and Opus 5. Scope the no-retry fact for `reasoning_extraction` to Opus 5.5 and Sonnet 5.5. Note that Sonnet 5.5's server-side fallback retries only `cyber` and `frontier_llm`, on Sonnet 5. The auto-improve mutator runs on `sonnet` by default, so this is the classifier set it actually meets.

**Verify:** `uv run pytest tests/unit`; edit both copies in one commit (prior feature 04 P5 records that nothing catches them drifting apart).

### Q5 — Sonnet 5.5 in Model Routing (S14) · optional

**Not broken:** delegation already leaves the model to the user (S15). What is missing is the user-facing guidance. `agents/README.md` Model Routing documents Fable as the opt-in upward path and says nothing about the downward one.

**Change:** one paragraph, "When Sonnet 5.5". Quote the official split: Sonnet 5.5 for "well-scoped everyday tasks, fixing bugs", Opus 5.5 for "complex work requiring careful judgment", and "For the hardest long-horizon work, an Opus model is the better choice". Give the prices: half of Opus 5.5 on input and output, the same $0.20 cache read. Name the paths and how long each lasts (`claude --model sonnet` for one session; `/model sonnet` is saved). State one Sonnet-specific cost: neither 5.5 model reads the other's thinking blocks, so switching mid-session runs later turns without the earlier reasoning.

**Necessity:** weak. Recommended because the section already carries the Fable equivalent, and a user reading it for "which model" gets half the answer.

## 2. Decisions for the user

- **D1 — Sonnet column in the mirror vs reference-only.** (a) Full column, as in Q2 (recommended): this VM, like any machine without the `claude-api` skill, got its whole rewrite from the mirror table (03 §4), so a reference-only target would give those users nothing. (b) Flag and inference only, with every Sonnet delta read from the reference: less to maintain, but blind where the skill is absent.
- **D2 — Q2 canary effort level.** (a) Claude Code default `medium` only (recommended): it is what an installed user runs, and 03a used it. (b) Add `low` runs, where the guide's G2/G11 failures are strongest: more cost, and the command's output does not depend on the session's effort.
- **D3 — Q5 in or out.** Recommendation: in, as one paragraph.

## 3. Considered and rejected

| Idea | Why not |
|---|---|
| Add the guide's verification paragraph to `core/RULES.md` | `<verification_before_completion>` (`RULES.md:19`) already says the same, and P-C showed it working (2/2 vs 0/2). A second copy in an always-loaded file costs tokens every session and adds nothing |
| Add the G2 carry-through paragraph to the kernel | Its second half duplicates `<scope_discipline>`. Its first half ("keep working ... only stop to ask when you can't go on") conflicts with `[R12]`/`[R13]`, which ask for confirmation on ambiguous, irreversible work, and the guide itself says it "doesn't replace your own rules about risky or irreversible actions". Claude Code also injects its own task-completion text |
| Pin `effort` or `model` for agents or commands on Sonnet 5.5 | Reverses the de-pin decisions (`agents/README.md:88`, commit `8edd05d`). Effort is Claude Code native |
| Switch the auto-improve mutator away from `sonnet` | The alias now resolves to a model the announcement calls faster and cheaper per task. Nothing measured says the mutator regressed |
| Rewrite `--introspect` / `--vs cot` for `reasoning_extraction` | Not declined on Sonnet 5.5 (03a P-B), matching Opus 5.5 |
| Turn-scoped reminder after five silent steps (G8) | SuperClaude runs inside Claude Code and does not build the `messages` array. The reminder is a harness feature |
| Tolerant tool-name handling (G12), crop/zoom tools (G13) | Harness-side. Claude Code owns tool dispatch, and SuperClaude ships no visual-input tooling |
| Move `test_runner_hook` output from `systemMessage` to fewer, rarer messages because of G10 | No misread observed (2/2, 03a P-D). The hook's real defect is the false "Tests FAILED" (S12), which is model-agnostic and belongs to its own fix |
| A search-first line for `deep-researcher` / `/sc:research` (G9) | Those surfaces already route to web search first (`RESEARCH_CONFIG.md`, `commands/research.md:33-35`). The guide's line is for products whose prompts don't already require searching |

## 4. Deferred, with the event that would reopen them

- **`test_runner_hook` false failure (S12).** *Resolved in 4.17.2 on `fix/test-runner-missing-pytest`: a runner that cannot start (pytest missing, no npm test script, no make test target) now reports "Tests not run" instead of "Tests FAILED".* When `pyproject.toml` declares no pytest, the hook reports "Tests FAILED" on correct code, and in 2/2 probes the model spent a turn on it. Model-agnostic, so out of this feature's scope. Reopen as its own `fix/` branch: skip the run (or report "no test runner available") when `uv run python -c "import pytest"` fails.
- **G2 early check-in on long tasks.** Not reproduced by the short fixture. Reopen if a `low`/`medium` Sonnet session is seen stopping mid-task to ask something it could answer itself. The candidate fix is the guide's first paragraph in a mode such as `--task-manage`, not in the kernel.
- **G10 mid-turn user messages.** Only headless runs were probed. Reopen if an interactive Sonnet 5.5 session is seen treating a typed message as an injection while SuperClaude hooks are active.
- **Deleting the interim Opus 5.5 text entirely (Q1 item 3).** Reopen once a fresh `claude-api` skill install is confirmed to carry the Opus 5.5 section.

## 5. Change set and verification summary

| Proposal | Files | Size | Gate |
|---|---|---|---|
| Q1 | `scripts/context_loader.py`, `tests/unit/test_context_loader.py`, `commands/prompt.md` | 2 tuples + fixture + 1 clause | pytest; ranges on a current reference |
| Q2 | `commands/prompt.md`, `help.md`, `sc.md`, `commands/README.md`, root `README.md` | ~35 lines | pytest; Sonnet and Opus canaries in 2 domains and 2 languages |
| Q3 | root `README.md`, `commands/prompt.md` | 2 lines | pytest; grep |
| Q4 | `utils/__init__.py`, `evals/run_eval.py` | docstring ×2 | pytest |
| Q5 | `agents/README.md` | 1 paragraph | D3; pytest |

No `.py` file is added or removed, so the component count in `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` does not move. Q1–Q4 can land on one `fix/sonnet-5-5-prompting` branch, with a minor version bump (4.17.0+ajitta), since `/sc:prompt` gains a target.
