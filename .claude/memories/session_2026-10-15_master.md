branch: master @001ce668

# Session 2026-10-14/15 — master (rule citations, v4.27.1 release)

## Where it stands
- Released v4.27.1: `stable` → 001ce668, Tests run 38585174723 green, Pages deployed. master == origin/master, clean
- Feature `docs/features/rule-citation-consistency/` complete (05-plan.md `status: complete`, Phases 0–4 all ticked, Deviations recorded)
- Local scope re-synced (`make sync-local`: 86 installed, `verify-drift` no drift); new rule text applies from the next Claude Code session
- claude-mem work_state `release` closed

## What changed (merges 0025c03a, 9961e620, 001ce668)
- Rule citations: shipped content and `.claude/rules/` cite rules as `[RNN Name]` only. Bare ID allowed only in `core/rules/RULES_QUALITY.md`, a range (`R01–R21`), or `_BARE_ID_ALLOWED` in `tests/unit/test_cross_references.py` (insight.md `rule` field example, gotcha `rule-tag-vs-concept`, `§ P-R21` anchor). Convention row in `.claude/rules/xml-prose-format.md` Quoting table
- `RULES_QUALITY.md` R06/R15/R18/R19/R20 shortened to "kernel `<section>` + what the kernel lacks" (12,832 → 12,534 bytes, ~75 tokens; estimate was 0.5–1KB). `test_quality_kernel_pointers_resolve` checks the named sections exist in `core/RULES.md`
- `file_size_guard`: message uses decimal KB (`size // 1000`) and "at or over the safe Read threshold (30KB)"; docs say "≥30KB". `test_threshold_described_as_inclusive` scans `src/superclaude` + README (pattern spans line breaks); `test_code_file_at_threshold` checks the real message
- `docs/` citations checked, NOT rewritten: no wrong citation outside `docs/archive/`; archive cites retired rules (R04 Planning etc.) that existed when written — dated records
- Gotcha `generated-regex-escapes` added to `.claude/rules/gotchas/general.md`

## Decisions
- Citation form `[RNN Name]` over bare IDs (bare saves <1KB total, loses meaning where RULES_QUALITY is not loaded, e.g. always-loaded PRINCIPLES.md) and over dropping IDs (breaks R14 `violated_rule`, insights `rule`, `/sc:analyze --focus rules`)
- Kernel dedupe option A (shrink RULES_QUALITY) over B (move into kernel: grows every session)
- Version 4.27.1 = patch (fixes + rule wording, no feature)

## Problems hit
- Writing Python test code through a non-raw string turned `\b` into backspace, `\n` into newline — twice. First time the test passed checking nothing. Caught by planted violations → gotcha
- First inclusive-wording pattern missed a message split across two source lines → widened pattern + runtime-output assertion
- `git checkout -- <file>` to undo a planted violation also reverted that file's real edit → restore from a temp copy instead (plan Step 3 corrected)
- Gotcha entry over 320 chars after adding a full tag → reworded only the edited phrase

## Canary
- `make canary-gates`: 7/7 hard gates, destructive-elicitation 2/2 (failed at 4.26.0 and 4.27.0; fixed by 5c7b8ca1), $1.07
- Runs dirs copy `~/.claude/.credentials.json` into `<runs-dir>/config/<arm>/` — real OAuth token. All `C:/tmp/sc-evals/` deleted this session (user-approved), folder removed

## Next actions
- [ ] None from this session
- [ ] Open elsewhere: claude-mem `structured-output-style` (needs name/scope/notation decisions); stale `superclaude/authoring-skill` work_state entry (released in v4.27.0; close from that worktree scope or ignore)
- [ ] Old local branches untouched: docs/sc-prompt-description, feature/portable-authoring-skill, fix/plain-language-structure (kept unmerged on purpose), fix/retired-workflow-bundled-ref, refactor/command-descriptions, refactor/sc-prompt-skill, test/sc-prompt-trigger
- [ ] Out of scope, noted: insights.jsonl `rule` (bare ID) vs R14 `violated_rule` (`[RNN Name]`) format differ; one stored insight cites undefined `R10`
