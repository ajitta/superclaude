---
status: draft
revised: 2026-09-30
---

# 03a — Probes on Sonnet 5.5 (headless)

Every probe ran as `claude -p --model sonnet` on Claude Code 2.1.284, on an aarch64 Linux VM. The `sonnet` alias resolved to `claude-sonnet-5-5` with `contextWindow: 1000000` (single `ok` probe, $0.057). Effort was the Claude Code default (`medium`).

SuperClaude arms ran in a scratch git repo after `superclaude install --scope project --force` from this checkout (4.16.0+ajitta, 84 components). Bare arms ran in an identical repo with nothing installed. The fixture is a 2-function Python package (`src/calc/ops.py`, `tests/test_ops.py`, `pyproject.toml` with `pythonpath = ["src"]`, no pytest dependency), committed once. Raw stream-json outputs stayed in the session scratchpad and are not committed.

Sample sizes are 1–2 per cell. Read every row as "this happened", not as a rate.

## P-A. `/sc:prompt` on a Sonnet 5.5 session

| Run | Input | Result |
|---|---|---|
| A1 | Inline: `/sc:prompt "You are a support bot. Think step by step and write out your reasoning before answering. Only use tools when strictly necessary."` | **Refused before the command ran.** `stop_reason: refusal`, `Details: [reasoning_extraction]`. The CLI printed "Sonnet 5.5's safeguards flagged this message". Billed $0.272 |
| A2 | Same text in `./support.md`, passed as a path (plus "Answer in under 100 words") | Ran. It **assumed `claude-opus-5-5`** ("this session runs Sonnet 5.5, which gives no target"). It deleted the think-step-by-step and write-out lines under the Opus rows and emitted the interim Opus 5.5 request config (`effort: medium`) |
| A3 | Inline, no reasoning request: `"... Be thorough and do not be lazy. Only use tools when strictly necessary."` | Ran. It assumed `claude-opus-5-5`. It deleted the boosters and rewrote the tool line as a when-to-look-up rule, as a judgment call (no detector row matched) |
| A4, A5 | `./agent.md --target api`: an unattended coding agent with "double-check your changes: re-verify by running the project's tests and the build" and "Only use tools when strictly necessary" | 2/2 assumed `claude-opus-5-5`. 2/2 **deleted the double-check line as "self-check phrasing: Opus self-verifies unprompted"**, then kept "tests and build pass" as a done-criterion. 2/2 deleted the tool-discouraging line as a judgment call. 2/2 emitted `effort: medium` and `max_tokens` 128,000 |

Each of A2–A5 reported: "no `claude-api` model-migration reference on this machine". This VM has no claude-api skill installed, so every run fell back to the mirror table. The context_loader note behaved as designed.

Readings:

- **The inference gap is live.** `prompt.md` flow step 2 says a session "on any other model infers no target: ask for `--model`, or state the target assumed and why". 4/4 stated an assumption, and 4/4 picked Opus 5.5. None asked. Nothing in the command lets a user name Sonnet 5.5, because `--model` accepts only `opus55|opus5|fable51`.
- **Verification direction.** A4/A5 removed the self-check wording under the Opus rule. They survived only because the model kept the underlying test-and-build requirement as a done-criterion. On Sonnet 5.5 the guide's direction is to keep or add a real-check requirement (02-research G11), and the rewrite's reported reason ("self-verifies unprompted") is not a Sonnet 5.5 fact.
- **The tool-discouraging line** was removed 3/3, but as judgment. For Sonnet 5.5 the guide makes it a documented removal (G9: "it follows these literally").
- **A1 extends a known Opus 5.5 finding to Sonnet 5.5.** The root README already warns that on an Opus 5.5 session a prompt asking for written-out reasoning must be passed as a file path. Sonnet 5.5 refused the same input inline. The refusal happens on the user turn, so no text inside `prompt.md` can prevent it.

## P-B. Reasoning-exposure modes (`--introspect`, `--vs cot`)

| Run | Prompt | Result |
|---|---|---|
| B1 | `We chose SQLite over Postgres for a single-user desktop notes app. Reflect on the choice. --introspect` | `end_turn`, a normal 🎯/📊 answer |
| B2 | `Suggest names for a CLI tool that syncs dotfiles. --vs cot` | `end_turn`, `Variant: cot` with a **Reasoning** line per candidate |

Neither was declined. This matches the Opus 5.5 result (opus-5-5-default-model 03-analysis §3b): both modes ask for decisions and rationale, not a transcript of internal thinking. n=1 each.

## P-C. Scope and verification: SuperClaude kernel vs bare

Two tasks, with 2 SuperClaude runs and 2 bare runs each, `--permission-mode bypassPermissions`.

**Task 1**: "Add a mul(a, b) function to src/calc/ops.py that returns the product."

| Arm | Change | Check run before reporting done | Unrequested files | Cost (each) |
|---|---|---|---|---|
| Bare ×2 | `mul` added | **None** ("I haven't run it or any tests", 2/2) | none | $0.121, $0.119 |
| SC ×2 | `mul` added | Import-and-call (`python3 -c "... mul(3, 4)"` → `12`), 2/2 | none | $0.162, $0.162 |

**Task 2**: "Add mul(a, b) and div(a, b) ... (div raises ValueError when b is 0), and add a CLI in src/calc/__main__.py ..."

| Arm | Tests added to `tests/test_ops.py` (not requested) | pytest run | CLI exercised | Cost (each) |
|---|---|---|---|---|
| Bare ×2 | 2/2 | 2/2 (5 passed) | 2/2 | $0.142, $0.141 |
| SC ×2 | 1/2 | 1/2 (5 passed) | 2/2 | $0.175, $0.190 |

Readings:

- **On a one-line change, the kernel supplied the check the bare model skipped.** This is the G11 failure the guide describes for `low`, observed here at `medium` in the bare arm (2/2). The SC arm's check exercised the change ("the changed command itself" in the guide's paragraph). It was not a syntax-only check.
- **On the larger task both arms verified by running the code.** The bare arm also wrote unrequested tests 2/2, as G3 predicts ("adds tests ... even when you don't ask for them"). The SC arm did so 1/2 under `[R06 Scope]` "0 unsolicited files". n=2 cannot separate the kernel's effect from noise.
- **Cost:** the SC arm cost 25–35% more per run. Most of that is the Stop hook's extra turn (the insight request, below) and the larger system context, not extra tool calls.

## P-D. Harness text after tool results (hooks)

Task: "Using the Edit tool (not Bash) for every file change, make three separate edits ... Then run the tests." Two SuperClaude runs, so that `test_runner_hook` (PostToolUse on Edit/Write, `async: true`) fired after each edit.

- The hook ran `uv run python -m pytest --tb=short -q` (`detect_test_command`: a `pyproject.toml` with no Makefile). pytest is not a declared dependency of the fixture, so each run's async `systemMessage` reported **"Tests FAILED"** after the edits, although the code was correct.
- 2/2 runs read those messages as hook output, not as injected instructions ("The hook's test runs are failing because pytest isn't installed"). Both then ran the tests themselves, with `uv pip install pytest` in one run and `uv run --with pytest` in the other: 5 passed, 2/2.
- The Stop hook's `[sc-insight-request]` arrived as user-turn text after the final answer, 2/2. The model answered it, never treated it as an injection, and the stream showed Claude Code's `Stop hook error occurred` notice each time.

Readings:

- **G10 did not fire.** Per-edit harness text did not make Sonnet 5.5 suspect an injection in 2/2 runs with 4 hook messages each. These are headless runs with no mid-turn user input, which is the case the guide describes as most sensitive. Interactive typing mid-turn was not probed.
- **A false "Tests FAILED" signal costs a detour.** Both runs spent a turn diagnosing the hook. This is a `test_runner_hook` defect (it assumes pytest is available whenever `pyproject.toml` exists), not a model-specific one. It is recorded in 03-analysis S12.

## Not probed

- `low`, `high`, `xhigh` and `max` effort: every run used the Claude Code default `medium`.
- The G2 early check-in on long multi-part tasks: the fixture tasks were too short to reach it.
- Mid-turn user messages in an interactive session (G10).
- `--target api` output of a `/sc:prompt` that has a Sonnet column: it does not exist yet (04-design P1).
