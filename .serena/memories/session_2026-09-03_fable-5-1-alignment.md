# Session 2026-09-03/04 — Fable 5.1 alignment of src/superclaude

## Goal
`/goal`: the Obsidian vault `fable-5-1-obsidian-notes` (10 notes + a 2026-09-02 verification report) describes the Claude Fable 5.1 release; produce an improvement plan for `src/superclaude`. The user then approved the plan ("draft 상태에서 수정 진행이 곤란" = go ahead) and said "남은 것 진행" / "계속 진행" until nothing was left. Goal status: done — merged to master `fa01784`, follow-ups through `387f1af`, pushed, user install synced, no open items.

## What the analysis found
- Fable 5.1 is a small delta for a content framework. The Claude Code system prompt in a Fable 5.1 session already carries the prompting guide's autonomy block, batching nudge, and progress-update line verbatim, and the scope block in substance. So the plan's rule was: add nothing the harness says, contradict nothing, fill only the gaps. Sweeps for narration suppression, anti-formatting rules, compile-check phrasing: zero hits.
- Primary sources: the docs site serves clean markdown when `.md` is appended to a platform.claude.com URL (54 KB vs 860 KB HTML); this also bypasses the WebFetch interception.
- Claude Code facts (checked against code.claude.com docs and the 2.1.258 binary): a `PreCompact` hook cannot inject compaction-summary instructions (its `systemMessage`/`continue` are discarded); `claude --model fable` selects Fable 5.1; `claude -p` refusal fields are undocumented, but the result message has top-level `stop_reason` and no `stop_details`, while the assistant message has both (stream-json only).
- Docs: `docs/features/fable-5-1-alignment/{README,03-analysis,05-plan}.md`. Analysis was adversarially verified by an independent agent (every primary-source claim held; a line number, an overstated "verbatim", and a mis-cited gotcha were corrected).

## Change sets applied (all on master)
- CS-A `6dda706`: `commands/prompt.md` targets Fable 5.1 (`--model opus5|fable51`, `fable5` legacy alias); the "proactivity boosters → delete" row now distinguishes slogans (delete) from the documented autonomy block (add on `--target api` only, since CC injects it on cc); narration-suppression and anti-formatting removal rows; listings and one loader comment; `agent-authoring.md` gains the `fable` alias.
- CS-B `d24bc69`: `RULES_DELEGATION.md` run-alongside + SendMessage reuse line; `save.md` compaction Preserve list = the guide's six items (SSOT); `MODE_Token_Efficiency.md` points at it.
- CS-C `196d3e0` (+ `c110e8f`, `5ea27cb`): refusal classification in parallel_ab (`exit_status: refusal`, `refusal_category`, now reads stream-json), auto_improve mutator (`refused` flag; loop stops after 3 consecutive refusals), evals (`REFUSED` cell, Refusals section; result-level refusal never downgrades the assistant category). Reviewed by a 75-agent workflow; its one high-severity finding (category clobbered to "unknown") was real and fixed.
- CS-D `fbff547`: one sentence in `RULES_DOCS.md` for long documents at xhigh. Measured on plan-routing at `--effort xhigh`, n=2/arm: mean duration -11%, output tokens -18%, checks identical, ranges overlap. Shipped on the approved gate; evidence is weak and recorded as such.
- Harness: `d8d1610` `--effort` passthrough; `e8caf0e` refuse runs under `~/.claude`, count PowerShell in transcript gates, stash-aware `file_preserved_glob`; `ca3fd52` plan-routing accepts both convention locations, max-turns runs keep usage and checks, fixture no longer installs into the real dev tree; `9f88fc0` install walk-up stops at `$HOME`; `8b32859` every `mutation_error` rolls back and rollback no longer wipes the untracked `results.tsv`; detector deduped into `superclaude.utils.detect_refusal`.

## Canary results (claude-fable-5-1, 14 tasks)
- First run from inside the CC session: 9/14, 1 gate failure — invalid. Cause: TEMP sits under `~/.claude/tmp`, where CC denies every Edit/Write in headless mode; PowerShell git commands invisible to Bash-only transcript checks; a `git stash` scored as destruction. All harness defects, fixed.
- Master baseline vs branch, outside `~/.claude`: identical on all 14 tasks, 13/14 fully passing, 7/7 gates, 0 refusals, $8.59 vs $8.94. No regression. The shared miss was `plan-routing`, which the task definition caused (fixed on the task side afterwards; offline score 3/3 on real output).
- Total eval spend ≈ $37.

## Problems hit and resolved
- Bash heredocs with long multi-line bodies were mangled by the shell hook twice; writing scratch files and `cat >>` worked.
- `uv run pytest` was red on a clean tree from inside a session (two scope tests). Root cause was code, not temp location: the walk-up passed the faked `$HOME` into the real user profile. Fixed in `find_install_root`.
- A test fixture installed into the repo's dev-tree `.claude/` before its chdir and raced the post-edit test hook; stray call removed.
- Rollback data loss in auto_improve reproduced on a throwaway repo (one header-less row left after one regressed cycle); fixed with `git clean -fd -e results.tsv`.
- prettier hook raised a one-off permission error; manual run exit 0; not reproduced.

## Approaches set aside
- PreCompact hook carrying the six-item compaction list: impossible per CC docs.
- Effort table in FLAGS.md: the model cannot set its own effort in CC (August decision stands).
- Changing `RULES_DOCS.md`'s `[f]` default for `/sc:plan` to fix plan-routing: the task was wrong, not the convention.
- Verifier-subagent exception in the delegation rule: omitted, no multi-hour autonomous builds run here.

## Next session
Nothing pending from this feature. Optional: a third CS-D measurement pair (~$4) to firm up the weak gate; raising plan-routing's `max_turns` (12) since Fable 5.1 used 13 once. Run evals with `--runs-dir C:/tmp/...` from inside a session; run pytest with the default temp root (now green).
