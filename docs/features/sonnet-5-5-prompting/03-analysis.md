---
status: draft
revised: 2026-09-30
---

# 03 — Repository analysis: `src/superclaude` against the Sonnet 5.5 deltas

This document checks each Sonnet 5.5 delta in [02-research.md](./02-research.md) (G1–G14) against the surface in `src/superclaude` that it touches. Each surface is marked **blocking**, **drifted**, **gap** or **aligned**. Probe evidence is in [03a-analysis-probes.md](./03a-analysis-probes.md). Proposals are in [04-design.md](./04-design.md).

Baseline: branch `master` at `ca38dc1`, version 4.16.0+ajitta. Surfaces were found by `grep -rniE "sonnet|opus|fable|haiku|effort|verif|tool" src/superclaude`, then by reading each file named below.

## 1. What already fits

Most of the Sonnet 5.5 guide describes behavior that SuperClaude's kernel already asks for. None of these needs a change:

| Delta | Where SuperClaude already says it | Evidence |
|---|---|---|
| G2 second paragraph, G3 (no unrequested features, tests, files) | `core/RULES.md:15` `<scope_discipline>` ("Build only what is asked ... Notice unrelated issues → mention, never fix unasked"); `core/rules/RULES_QUALITY.md:11` `[R06 Scope]` ("0 unsolicited files") | P-C task 2: the SC arm added unrequested tests 1/2, the bare arm 2/2 (n=2, not separable from noise) |
| G5 (ideas requested → stop before building) | `core/RULES.md:15`: "When the user describes a problem, asks a question, or thinks out loud rather than requesting a change, the deliverable is the assessment: report findings and stop" | Not probed |
| G11 (run a real check before reporting done) | `core/RULES.md:19` `<verification_before_completion>` ("Never claim work complete without running the verification that proves it ... If verification was skipped, say which check and why"); `RULES_QUALITY.md:82-92` `<verification_ladder>` | P-C task 1: the SC arm ran an exercising check 2/2, the bare arm 0/2 |
| G4 (no self-started reviewer subagents) | `core/rules/RULES_DELEGATION.md:12` "Never spawn a sub-agent to verify or double-check work the main loop already did" | Not probed (needs `xhigh`/`max`) |
| G6, G14 (no "don't think" rules; no reasoning write-out) | `core/PRINCIPLES.md:27` names restating chain-of-thought as an anti-pattern. No shipped mode asks for a thinking transcript | P-B: `--introspect` and `--vs cot` not declined, 2/2 |
| G1 (effort is the lever, not prompts) | `scripts/context_loader.py:406-422` routes the removed `--effort` flag to Claude Code's native control. No agent or command pins `effort` (`agents/README.md:88`, commit `8edd05d`) | — |
| Model choice left to the user | `agents/README.md:86-90` (no `model:` pins); `RULES_DELEGATION.md:13` (pass a model only when the user asked) | — |

INFERRED: the kernel was written against Opus-family over-reach, and it happens to cover the Sonnet 5.5 guide's G2/G3/G11 in the same words. The one kernel rule that points the wrong way for Sonnet 5.5 lives in `/sc:prompt` (S1–S3), not in the kernel.

## 2. Surface inventory

| # | Surface | file:line | What depends on the model | Status |
|---|---|---|---|---|
| S1 | `/sc:prompt` target set | `commands/prompt.md:2,8,11,15`; table header `:28` | Targets are `opus55`, `opus5` and `fable51`. A Sonnet session "infers no target" (`:15`). Probes A2–A5 assumed `claude-opus-5-5` 4/4 and never asked | **Blocking**: the second 5.5 model has no target, and the fallback lands on the family whose verification direction is opposite |
| S2 | Self-check row and gotcha | `commands/prompt.md:52` (Self-check phrasing → delete for Opus), `:114` (`opus5-verify-inversion`) | Correct for Opus. For Sonnet 5.5 the guide adds a real-check paragraph at `low` effort (G11). Probes A4/A5 deleted "double-check ... re-verify by running the tests and the build" citing "Opus self-verifies unprompted" | **Blocking** once S1 adds Sonnet: the row needs a Sonnet action, or the inversion carries over |
| S3 | Thinking-incantations row | `commands/prompt.md:49` ("Delete — redundant on thinking models") | G7: for JSON answers to multi-step tasks under adaptive thinking, "Think the problem through before you answer." at the end of the system prompt raises accuracy (at `high`, close to `xhigh`) | **Drifted** for Sonnet 5.5, in one task class |
| S4 | Reasoning write-out row | `commands/prompt.md:50` | Delete for `claude-opus-5-5` and `claude-fable-5-1`. Sonnet 5.5 has the same `reasoning_extraction` category and the same no-retry fallback (What's new) | **Gap**: Sonnet not named |
| S5 | No tool-discouragement row | `commands/prompt.md:45-66` `<removal_targets>` | G9 names `only use tools when strictly necessary` and `minimize tool calls`, and the reference says the model "follows these literally". A2–A5 removed the line 4/4, but by judgment, with no row to cite | **Gap** |
| S6 | Narration-suppression row | `commands/prompt.md:55` (delete for Fable only) | G8 says to remove "hold all findings for the final response" on Sonnet 5.5 as well | **Gap** |
| S7 | Request configuration | `commands/prompt.md:41` (Opus 5.5 only, marked interim) | Sonnet 5.5 differs from Opus 5.5 in its API default effort (`high` vs `medium`), its lowest thinking setting (`between_tools` vs none) and its effort starting points by workload (G1) | **Gap** |
| S8 | Migration-reference anchors | `scripts/context_loader.py:965-969` `_MIGRATION_REF_ANCHORS` | Holds Opus 5 and Fable 5.1 only. The upstream reference now has `## Migrating to Claude Opus 5.5` (L1867) and `## Migrating to Claude Sonnet 5.5` (L2072) (02-research §5). With the two anchors added, the shipped `migration_reference_ranges()` returns `claude-opus-5-5 L2044-2071` and `claude-sonnet-5-5 L2195-2225` | **Unblocked**: the prior feature's P4 can ship, and the `interim` text can go |
| S9 | Interim Opus 5.5 text | `commands/prompt.md:26,34,41`, the `<fact_sourcing>` fallback `:81`, `<bounds><fallback>` `:124` | Allowed "only while the reference has no Opus 5.5 section". Upstream now has one | **Drifted** as soon as a user updates the skill |
| S10 | Inline reasoning-request warning | root `README.md:684` | "On an Opus 5.5 session, pass a prompt that asks for written-out reasoning as a file path". Probe A1: Sonnet 5.5 refused the same input inline (`[reasoning_extraction]`, $0.27) | **Drifted**: Sonnet 5.5 not named |
| S11 | Refusal docstring | `utils/__init__.py:313-317`, and its pinned copy in `evals/run_eval.py` | Names Fable 5.x, Opus 5.5 and Opus 5, and the no-retry fact for Opus 5.5. The auto-improve mutator's own default model (`sonnet`, S13) now resolves to Sonnet 5.5, which has five categories and the same no-retry rule for `reasoning_extraction` | **Drifted** docstring. The code is model-agnostic |
| S12 | `test_runner_hook` | `scripts/test_runner_hook.py:75-95` (`detect_test_command`), `:152-165` | Runs `uv run python -m pytest` whenever a `pyproject.toml` has no Makefile, even if pytest is not a dependency. P-D: a false "Tests FAILED" after each edit, 2/2 runs, and each run spent a turn diagnosing it. The async `systemMessage` after each edit is the per-step harness text that G10 warns about; no misread was seen (2/2) | **Defect, model-agnostic**. Out of this feature's scope (04-design §4) |
| S13 | auto-improve mutator default | `scripts/auto_improve/mutator.py:19`, `coordinator.py:54`, `cli.py:80`, `commands/auto-improve.md:40` | `--mutator-model sonnet` now resolves to Sonnet 5.5 on Claude Code ≥ 2.1.284. Cost per task is lower, and effort in `-p` is `medium`. `DEFAULT_PROMPT` asks for "a one-paragraph rationale describing the change and your hypothesis", which is a report, not a thinking transcript | **Aligned**. The default follows the alias by design (opus-5-5 D1) |
| S14 | Model Routing section | `agents/README.md:84-102` | Documents Fable as the user's opt-in path. Says nothing about Sonnet 5.5 as a user-chosen, cheaper path for well-scoped work, or about the thinking loss when a session switches between Opus 5.5 and Sonnet 5.5 (neither reads the other's blocks) | **Gap**, optional |
| S15 | Delegation model line | `core/rules/RULES_DELEGATION.md:13` | "Pass a model only when the user asked for it". This already covers a model-initiated downgrade to `sonnet` for cost. The Fable sentence gives the reason for the expensive case only | **Aligned** |
| S16 | Command summaries | `commands/help.md:54`, `commands/sc.md:54`, `commands/README.md:80`, root `README.md:684` | "Rewrite a prompt for Opus 5.5 / Fable 5.1" | **Drifted**, follows S1 |

Outside `src/` (listed for completeness): `tests/unit/test_context_loader.py:774-875` pins the anchor fixtures and will need rows for any new anchor. `.claude/rules/agent-authoring.md` already says to omit `model`.

## 3. The verification inversion, stated once

The `/sc:prompt` model delta now has three directions, not two:

| Target | Verification instructions in a prompt | Source |
|---|---|---|
| `claude-opus-5` (and 5.5 as carried) | Delete: it self-verifies unprompted, and "double-check" causes over-verification | model-migration.md Opus 5 section; the Opus 5.5 section says to re-test these |
| `claude-fable-5-1` | Keep only claim-grounding; add a read-only verifier for long autonomous builds | `prompt.md:30` |
| `claude-sonnet-5-5` | At `low` (and in P-C, at `medium` in the bare arm) it can report a change done with no exercising check. Replace self-check slogans with the guide's real-check paragraph; don't delete the requirement | Prompting guide lines 144-152; P-C task 1 |

The target a rewrite assumes decides which of three opposite edits it makes. A1–A5 show that, today, a Sonnet session silently gets the first row.

## 4. Upstream fact source

- The reference now has a section for each 5.5 model. A machine that updates the `claude-api` skill gets `## Migrating to Claude Sonnet 5.5`, whose "Behavioral shifts (prompt-tunable)" subsection (L2195-2225) covers G9–G12, the workaround removal, and the settled-answers line.
- Anchor matching in `migration_reference_ranges()` compares whole lines (`line.rstrip() == anchor`), so `## Migrating to Claude Opus 5` does not match `## Migrating to Claude Opus 5.5`. Adding the two anchors needs no matcher change. Checked by running the function on the downloaded file (02-research §5).
- This VM has no copy of the skill (`find / -name model-migration.md` found only an unrelated Codex file). Every A-probe therefore ran on the mirror table alone. The mirror, not the reference, is what users without the skill get, which is the case for adding a Sonnet column (04-design D1).
