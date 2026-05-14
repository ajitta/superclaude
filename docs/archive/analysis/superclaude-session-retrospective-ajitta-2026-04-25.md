---
status: complete
revised: 2026-04-25
session: skill-authoring-consistency
purpose: Retrospective on problems, improvements, and tool-usage gaps observed during the skill-authoring consistency overhaul session
---

# SuperClaude Session Retrospective — 2026-04-25

> Session: brainstorm → discovery spec → 4-PR plan → execution → push/merge to master.
> Total commits: 10 + 1 merge. Tests: 1,628 → 1,767 passing (no regressions). Files touched: ~23.
> Spec: `docs/specs/skill-authoring-consistency-discovery-ajitta-2026-04-25.md`.

This doc tracks every friction point, internal bug, tooling gap, and workflow shortcoming surfaced *during* this session — not just the issues that became the session's primary work product. Severity: 🔴 blocker · 🟡 friction · 🟢 nice-to-fix.

---

## 1. SuperClaude internal bugs found AND fixed this session

These were the session's primary work, but worth cataloging as part of the gap inventory.

### 1.1 🔴 `when-to-use` (hyphen) silently dropped by CC parser
- **Observed:** All 5 shipped skills used `when-to-use:` for ~14+ days. CC parser reads `frontmatter.when_to_use` (snake_case, dot-notation) — JS dot-notation can't read hyphenated keys, so the field was silently ignored.
- **Impact:** Trigger keywords for every shipped skill were invisible to auto-invocation. Effective coverage = `description` only.
- **Source of error:** Memory entry `reference_cc-native-fields.md:37` (dated 2026-04-02) listed `when-to-use` as valid. The memory was stale and contradicted upstream truth.
- **Fix:** PR1 — remove field, fold triggers into `description` (Anthropic's canonical pattern; `when_to_use` itself is deprecated per `skill-reviewer.md:57`).

### 1.2 🟡 4-way `<bounds>` rule drift across authoring files
- skill-authoring: `should + avoid` required.
- agent-authoring: `should + avoid + fallback` required.
- command-authoring: rule said 2-attr, example used 3 (internally inconsistent).
- mode-authoring: 3-attr required.
- **Fix:** PR3 — unified rule (`should + avoid` required; `fallback` recommended for agent/mode, optional for skill/command).

### 1.3 🟡 Hook regex substring-match false positives
Three places used substring-matching where `-f` substring-matches `-force-with-lease` (the SAFER alternative, blocked by mistake):
- `ship/SKILL.md` PreToolUse hook
- `finishing-a-development-branch/SKILL.md` PreToolUse hook
- `hooks/hooks.json` Bash safety hook
- **Fix:** Negative-character-class word-boundary fakes (`-f([^a-zA-Z]|$)`).

### 1.4 🟡 Bare "VS" in verbalized-sampling description → false-positive auto-invoke
- "Postgres vs DynamoDB" comparisons would trigger the skill.
- **Fix:** Removed bare "VS"; added explicit "X vs Y is NOT a trigger" exclusion.

### 1.5 🟡 Stale figures in skill-authoring.md
- `SLASH_COMMAND_TOOL_CHAR_BUDGET ~15,000 chars` (was a 2% formula); current: 1% / fallback ~8K.
- `description ≤1,536 chars` framed as per-`description`; actually combined with `when_to_use` (now moot post-PR1).
- `allowed-tools` documented as comma-separated; Anthropic canonical = space-separated.
- **Fix:** PR2 — corrected with citations.

### 1.6 🟡 `effort: high` example with no policy guidance
- skill-authoring.md showed `effort: high` as a routine example.
- agent-authoring.md (since 2026-04-18) has extensive "omit by default — inherit from parent" policy.
- 0/5 shipped skills set `effort:`. Doc bias inflated apparent usage.
- **Fix:** PR2/PR3 — added "omit by default" comment.

### 1.7 🟡 Korean YAML inline comments in skill-authoring (peers all English)
- Memory entry from 2026-03-29 already flagged this as a known incomplete fix.
- **Fix:** PR4 — translated YAML inline comments and example values to English.

### 1.8 🟢 Field reference advertises 8/13 fields with zero shipped-skill usage
- Equal visual weight to rare and common fields misled readers.
- **Fix:** PR3 — annotated each field with shipped-skill usage count (`# 0/5 shipped use this`).

### 1.9 🟢 Install-path scope variance not documented
- `install_components.py` has 2 rewrite targets (user vs project/local), not the single target shown in the doc.
- **Fix:** PR2 — corrected (and self-review caught my v1 spec's mistaken "3 targets" claim).

### 1.10 🟢 Missing fields the project might reach for
- `paths:` (used in authoring rules but not documented as a skill option).
- `${CLAUDE_SKILL_DIR}` (Anthropic-portable; relevant if SuperClaude skills ship via plugin marketplace where `{{SKILLS_PATH}}` substitution doesn't fire).
- **Fix:** PR2 — added with brief annotations; `arguments:`, `shell:`, inline `` !`<cmd>` `` deferred (zero current usage).

### 1.11 🟢 Plugin-distribution path skips `{{SKILLS_PATH}}` substitution (latent)
- `_resolve_skill_templates` fires only for `superclaude install` (bulk + single-skill). No `/plugin install` hook invokes it.
- **Impact:** Currently latent (0/5 skills use the placeholder). Active bug if SuperClaude skills ship via marketplace.
- **Fix:** Documented in PR2 commit body; `${CLAUDE_SKILL_DIR}` recommended for redistributable skills.

---

## 2. Tool harness friction (CC + uv + Windows)

### 2.1 🟡 Read tool dedup hook over-aggressively returns only line 1
- Hook decides "file already observed" and returns 1 line + a memory timeline summary.
- Triggered every time I re-Read a file I'd seen in this session OR in a prior session.
- **Workarounds I had to use:** `Bash cat <file>` (~3-4 times), or run `Read` and accept 1-line return + use Bash for content.
- **Side-effect:** Edit tool requires a prior Read for "file registration", but Bash-cat doesn't satisfy that. Caused a chain where I'd Bash-cat (got content), try Edit (failed: "File not read yet"), then Read (returned dedup'd 1 line, but registered the file), then Edit succeeded.
- **Suggested fix:** Either (a) add a `--force-fresh` flag to Read, (b) hook should track *change* in mtime/size since last read and bypass dedup if changed, or (c) Edit should accept a Bash-cat'd file as registered.
- **Severity:** 🟡 — workable with workarounds, but added ~10 redundant tool calls in a single session.

### 2.2 🟡 `uv run pytest` script-canonicalization Windows bug
- `uv run pytest` returned "Failed to canonicalize script path" with exit 0 and no test output.
- `uv run python -m pytest` works fine — same env, same tests.
- **Impact:** Project's PostToolUse `make test` hook ran via `uv run pytest` and reported false test failures after every SKILL.md edit. Spammed the conversation with bogus "Tests FAILED" reminders ~6 times.
- **Suggested fix:** Update `make test` to `uv run python -m pytest` until uv fixes the script-path bug.

### 2.3 🟡 PostToolUse `make test` hook fires on out-of-scope files
- The hook ran when I wrote `.claude/_insight_append.py` (a temp script unrelated to source code).
- **Suggested fix:** Hook matcher should scope to `src/` and `tests/` only, not blanket Edit/Write.

### 2.4 🟡 Slash commands mangled when piped to `claude -p` via Git Bash
- `claude -p "/simplicity-coach daybook"` had the `/` interpreted by Git Bash as a path prefix.
- **Workaround:** Quote differently or run from cmd.exe.
- **Severity:** Minor — limited to canary-probe-style automation.

### 2.5 🟢 TaskCreate/TaskUpdate reminder spam
- "The task tools haven't been used recently..." appeared 5+ times this session.
- The reminder fires even when I have a clean task list and the work doesn't fit task tracking.
- **Suggested fix:** Suppress reminder if (a) all current tasks are completed, OR (b) recent commits indicate progress, OR (c) the user just said "proceed all" and the work is now mid-execution.

---

## 3. SuperClaude command friction

### 3.1 🟡 `/sc:plan` 15KB cap forces phase-file splits
- The 4-PR plan needed splitting into 4 files (each ~5-10KB) to stay under the cap.
- **Fine in principle**, but the splits had to be authored by hand. No `/sc:plan --phases 4` automation.
- **Suggested fix:** When the plan would exceed cap, `/sc:plan` could auto-emit a parent index file + N phase files with cross-links, instead of leaving it to the model.

### 3.2 🟡 `/sc:insight` shell-quoting fragile with backticks/special chars
- The first `python -c "..."` attempt failed because backticks in the insight text triggered shell command substitution; the Bash hook noise from `uv run pytest` then injected mid-string and produced a syntax error.
- **Workaround:** Wrote a temp `.claude/_insight_append.py` via Write tool, ran it, deleted.
- **Suggested fix:** `/sc:insight` skill body should always use the temp-file pattern, not `python -c`. Or: provide a small `.claude/insight-append.py` helper that reads JSON from stdin.

### 3.3 🟡 `/sc:brainstorm` auto-mode user-approval gate ambiguity
- The brainstorm flow has 3+ "wait for user" pauses (after discovery spec, after plan, after review). In auto mode, I had to interpret which pauses to honor and which to fast-track.
- The user said "proceed all" mid-stream, which collapsed the remaining gates. But the rules of when a "decision" gate is real vs ceremonial were unclear.
- **Suggested fix:** Document an auto-mode decision matrix in `/sc:brainstorm` body (e.g., "in auto mode, only Q1-Q5 user-input pauses are real; structural gates auto-approve").

### 3.4 🟡 `/sc:plan` doesn't catch "this isn't testable from automation"
- PR1's canary probe (D3 acceptance gate) requires a fresh interactive CC session. The plan had no field for "if you can't run this step, here's the alternative."
- I improvised by deferring the canary to the user, then later figured out `claude -p --output-format json` could substitute.
- **Suggested fix:** Plan template could include a `<verification mode="auto|interactive|deferred">` field per task, with explicit fallback paths for automation-blocked steps.

### 3.5 🟢 `/sc:review` self-review surfaced 3 critical errors AFTER user approval
- v1 spec was user-approved with my recommendations baked in.
- Self-review caught: (1) `when_to_use` is deprecated (the keystone reversal), (2) install-path "3 targets" is wrong, (3) D2 rationale was sunk-cost reasoning.
- **Implication:** The post-design self-review gate is **load-bearing**, not optional. It should be required after `/sc:brainstorm` decisions are baked, before `/sc:plan` handoff.
- **Suggested fix:** `/sc:brainstorm` flow should emit a "Recommended: run /sc:review on this spec before /sc:plan" at the end of its discovery output. Currently it just lists `/sc:plan` as the next step.

---

## 4. Tool integration gaps

### 4.1 🟡 `make deploy` ≠ skill deploy
- CLAUDE.md says "Editable install via `make deploy` (`uv tool install --editable .`) — `src/` changes reflect immediately."
- **Reality:** This installs only the CLI. Skills/agents/commands require separate `superclaude install --force` to propagate to `~/.claude/`.
- **Impact:** First canary probe attempt found old `when-to-use:` content still in `~/.claude/skills/confidence-check/SKILL.md` even after `make deploy`.
- **Suggested fix:** Either (a) `make deploy` triggers `superclaude install --force` as a step, OR (b) CLAUDE.md is updated to clarify the two-step requirement.

### 4.2 🟡 No programmatic skill-invoke testing fixture
- The canary probe was hand-rolled: 11 `claude -p` calls + manual response inspection.
- This is now a known-good pattern (see insight 17:35:03), but there's no `tests/integration/test_skill_canary.py` that exercises it.
- **Suggested fix:** Add a generic skill-canary fixture: input a (skill_name, trigger_phrase, expected_pattern) tuple, runs `claude -p`, asserts pattern in result.

### 4.3 🟡 Memory file `reference_cc-native-fields.md` was stale and contradicted upstream
- Memory entry (dated 2026-04-02) listed `when-to-use` as a valid field. Upstream truth (verified 2026-04-25): deprecated.
- No staleness warning fired; nothing checks memory entries against current Anthropic docs.
- **Suggested fix:** Memory entries with `verified DATE` claims could be auto-stale-flagged after N days when referenced. Or: a quarterly memory-curation skill that re-verifies time-sensitive claims.

### 4.4 🟢 Worktree mirror inflates repo-wide greps
- `.claude/worktrees/lucid-kalam/` shadow-mirrors src/, doubling counts in greps like "200 occurrences of `<component`".
- **Suggested fix:** Default greps should exclude `.claude/worktrees/`. Currently has to be done by hand each time.

### 4.5 🟢 No "where does this trigger come from?" introspection
- Several skills had trigger overlaps (e.g., `simplicity-coach` skill vs `simplicity-guide` agent).
- No single tool answered: "given user input X, which skill/agent/mode would activate?"
- **Suggested fix:** A `/sc:trace --input "X"` command that simulates which trigger paths would fire.

---

## 5. Workflow gaps

### 5.1 🟡 4-PR plan executed as 4 sequential commits on 1 branch (PR framing was aspirational)
- The plan documents call them "PR1", "PR2", etc. I executed them as 4 commits on a single feature branch, then merged to master.
- This worked, but the "PR" framing implied separate review cycles that didn't happen.
- **Suggested fix:** Either (a) `/sc:plan` should emit "phase" instead of "PR" for sequential work in auto mode, OR (b) when the user says "proceed all" the plan should auto-collapse PR boundaries into phase commits with a note in the merge commit.

### 5.2 🟡 No "decision-trail" audit for /sc:brainstorm spec changes
- v1 spec had decisions D1-D7 baked in. Self-review reversed D1, upgraded D2, added D8-D12.
- The diff between v1 and v2 was material but not captured in commit history (both versions were the same uncommitted file).
- **Workaround:** I added a "Review iteration log" table at the bottom of v2.
- **Suggested fix:** `/sc:review` could auto-emit a v1→v2 delta table when it modifies a draft spec.

### 5.3 🟢 Auto mode + brainstorm flow + decision-delegation produced subtly fragile decisions
- User delegated D2/D5/Q4/Q5 to me ("너의 추천을 존중하겠다"). My v1 picks were partially wrong (caught by self-review).
- This isn't a bug — self-review caught it. But it confirms: delegated decisions should ALWAYS go through self-review, not just user-approved decisions.
- **Suggested fix:** `/sc:brainstorm` should auto-trigger `/sc:review` on any decision tagged "delegated to model".

---

## 6. Doc / convention gaps

### 6.1 🟢 `doc_output_convention` frontmatter `status:` field has no enum
- I used `status: draft`, `status: ready-for-plan`, `status: revised-after-self-review`, `status: approved-for-plan`, `status: complete`. None of these are documented as valid.
- **Suggested fix:** Add a `status:` enum to RULES.md `<doc_output_convention>` (e.g., `draft|review|approved|implementing|complete|deprecated`).

### 6.2 🟢 No "deferred-decision" marker convention
- Spec had several "explicitly deferred" items (XML→Markdown migration, YAML schema sidecar). These are documented in prose but not greppable.
- **Suggested fix:** Convention like `<deferred until="condition" reason="...">` so future grep can find unblocked deferred items.

---

## 7. What worked well (worth amplifying)

- **Self-review as a load-bearing gate.** Three critical errors caught after user approval. This pattern should be required, not optional.
- **Two-agent parallel research.** External (Anthropic + leaked source) + internal (shipped-skill audit) caught different classes of issues. Neither alone would have surfaced the silent bug + the install-path drift simultaneously.
- **Headless `claude -p --output-format json` for canary probes.** Replaced "user must run interactive test" with "I run 11 scenarios in parallel and parse JSON". Massive speed win.
- **Memory observations (`get_observations`) for prior context.** The Apr-18 note on `effort: high` being kept "intentionally for skills" was load-bearing context that prevented me from naively scrubbing it.
- **The phase-plan structure (PR1→PR4 with `depends-on:` frontmatter).** Each phase was self-contained and re-runnable.
- **`--delegate auto` on review.** The self-review subagent's independent audit was the keystone correction mechanism.

---

## 8. Top 5 actionable follow-ups

Ranked by leverage:

1. **🔴 Fix `make test` hook to use `python -m pytest`** instead of `uv run pytest` — eliminates the persistent "Tests FAILED ... canonicalize script path" noise.
2. **🟡 Update CLAUDE.md `make deploy` description** to note the two-step deploy: `make deploy` (CLI) → `superclaude install --force` (content). Or merge them into one step.
3. **🟡 Make self-review a required gate after `/sc:brainstorm` decisions are baked in.** Add a `<handoff next="/sc:review"/>` to brainstorm before `/sc:plan`.
4. **🟡 Add a generic skill-canary fixture** (`tests/integration/test_skill_canary.py`) that takes (skill, trigger, expected) tuples and runs `claude -p` programmatically.
5. **🟢 Document the `status:` frontmatter enum** in RULES.md `<doc_output_convention>` so future docs use a consistent value set.

---

## 9. Numbers

| Metric | Value |
|--------|-------|
| Session duration | ~3 hours |
| Commits on `fix/skill-authoring-consistency` | 10 + 1 merge |
| Files modified | 17 |
| Lines added / removed | +1,206 / -79 |
| Tests pre-session | 1,628 passing |
| Tests post-session | 1,767 passing (24 skipped) |
| Insights captured | 7 |
| Self-review findings | 3 critical, 9 important, 6 suggestions |
| Tool friction events (Read dedup, uv pytest, hook noise) | ~12 |
| User decision gates honored | 5 (Q1, Q2, P0 pivot, push, merge) |
| User decision gates auto-resolved | ~3 (D8, D9, D10 — programmatic findings) |
