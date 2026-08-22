---
status: approved-for-plan
revised: 2026-08-22
---

# Defect Remediation — Claude-side Verification of the `6d6f09b` Audit

An independent re-verification of [`docs/codex/runtime-behavior-audit-6d6f09b-verification/`](../../codex/runtime-behavior-audit-6d6f09b-verification/README.md),
plus the defects that verification did not cover, and the plan that fixes both.

**Source:** merge `6d6f09b` (23 files under `src/superclaude/**`). Implementation plan for the merge
itself is [05-plan.md](./05-plan.md); the root-cause diagnostics are [06-diagnostics.md](./06-diagnostics.md).

## Verdict

The Codex report is **accurate but incomplete**. All 13 of its claims were re-checked against the
real source rather than against the report's own line numbers: **12 CONFIRMED, 1 PARTLY TRUE, 0
wrong**. A blind-spot pass plus first-hand verification added **13 further findings**, three of them
P1. One of the new P1s outranks everything in the Codex report, because it breaks every user who
upgrades with the documented command.

| Severity | Codex | New | Total |
|---|---:|---:|---:|
| P1 | 4 (one demoted to P2) | 4 | 7 |
| P2 | 6 (one promoted from P3) | 5 | 11 |
| P3 | 3 | 4 (+1 doc) | 8 |
| **Total** | **13** | **13** | **26** |

This plan fixes the 7 P1 and 11 P2 items. The 8 P3 items are recorded at the end for a follow-up.

## Two constraints that shape every fix

**Runtime state must stay under `claude_base()`.** The Codex report's headline recommendation — put
rebuildable runtime state outside the worktree — conflicts with the project's own rule
(`.claude/rules/gotchas/hooks.md`, `hook-runtime-state-uninstall`): state outside `base_path` is
unreachable by `uninstall_all()` and invisible to `--list-all`. Local-scope installs would start
leaving footprints in `~/.claude`, which is what `hook_state_dir()` exists to prevent. The fix is
exclusion plus path filtering, not relocation.

**Description wording is a near-zero-throughput channel.** [06-diagnostics.md](./06-diagnostics.md)
measured 6 model-initiated `Skill` calls across 743 tool calls, none of them `sc:`. Fixes to command
`description` fields are correctness work, not activation work, and are ranked accordingly — which is
why the Codex report's `/sc:git` P1 is carried here as a P2.

---

## Adjudication of the 13 reported findings

| # | Claim | Verdict | What the re-check corrected |
|---|---|---|---|
| 1 | Mixed hook entry: force/uninstall deletes user inner hooks | CONFIRMED | The non-force path is safe — `install_settings.py:212` appends and never rewrites an existing entry, so loss is confined to `--force` and uninstall. Force also silently **reorders**: `user_hooks + new_hooks` hoists user entries ahead of SuperClaude ones, changing execution order even when nothing is lost. And `--dry-run` counts outer entries (`install_inventory.py:462-467`) while `_count_shipped_hooks` counts inner hooks, so the two disagree about what "N hooks" means. |
| 2 | `_hook_script_id()` ignores the subcommand | CONFIRMED, latent | No event+matcher in today's `hooks.json` ships one script twice, so the reported reproduction is real but unreachable on a clean install. The **live** consequence the report missed: subcommand drift never propagates without `--force`. Commit `d1b4784` renamed `pending-count` to `pending-count-from-hook`; an install predating it keeps running the old subcommand forever, because `_hook_script_id` calls both the same hook. |
| 3 | `--force` cannot sweep retired events | CONFIRMED | `uninstall_hooks_from_settings()` does **not** share the bug — it iterates the settings file (`install_settings.py:320`) rather than the shipped config. That asymmetry is exactly why the gap has no test: the uninstall-side test passes. |
| 4 | `hooks_registered` compares counts, not identity | CONFIRMED | Misreads in both directions. Besides `14/14 ✅` for 14 obsolete hooks, a user-added inner hook inside a SuperClaude entry pushes `installed` to 15 against 14 shipped and renders the *not-installed* icon. |
| 5 | bare `install` catches `click.Abort` → user-scope install | CONFIRMED | Not silent: it prints `💡 No input available…(scope: user)`, which is the wrong text for the Ctrl-C case rather than missing text. Scoped to bare `install` — `-i` re-raises (`main.py:131-132`). The comment at `main.py:119-121` asserts the exact invariant that is false ("a user who declines gets a return value, and a prompt that cannot be read raises"); Ctrl-C is a third case that raises with a human present. **Blocker the report missed:** `tests/unit/test_install_interactive.py:165-179` pins the current behavior as intended, so the fix must rewrite that test. |
| 6 | `ensure_agent_memory_dir()` failure reported as success | CONFIRMED | Wider than claimed. `install_components.py:509-533` prints ❌ for `install_claude_sc_md` and ⚠️ for the CLAUDE.md import update and git-exclude write without touching `total_failed`, so `overall_success` can be `True` with a visible ❌ on screen. Also, `None` is overloaded — it is the legitimate return for an unsupported scope — so a bare `if not directory` check at the call site cannot distinguish the two. |
| 7 | `session_init` labels a local install `project` | CONFIRMED | Four on-disk discriminators exist (`settings.local.json`, `agent-memory-local/`, `CLAUDE.local.md`, the `.git/info/exclude` marker block) but there is **no install manifest**, and the discriminators are not mutually exclusive — this repository currently carries both scopes' artifacts side by side. The fix needs precedence rules, not a single check. |
| 8 | `git.md` description "approves" destructive ops | **PARTLY TRUE** | "approves" is genuinely ambiguous, not a flat contradiction: the author's intent (commit `af0d7c2`) was "this is the command that routes these through an approval step". The hard contradiction is a line the report never cited — the description says "wrong fire cost a revert" while `git.md:64` says force-pushing main is "**irreversible**". Same file, direct conflict. Note also that the installed copy is still pre-`af0d7c2`, so live blast radius today is zero until a re-install. |
| 9 | Retired-flag fuzzy match fires on external CLI options | CONFIRMED, **under-ranked** | Thresholds are `difflib.get_close_matches(cutoff=0.6)`, not the "Levenshtein ≤ 2" the comments at `context_loader.py:280-281` and `:380` claim. Blast radius exceeds the retired table: `--force`→`--focus`, `--all`→`--all-mcp`, `--verbose`→`--verbose-context`, `--porcelain`→`--plan`, `--jobs`→`--bs`. The report called the output advisory; that holds only for the "did you mean" comments — see N3. |
| 10 | `resolve_command_name()` inspects only the first token | CONFIRMED | Inverse failure missed: `main()` at `context_loader.py:840-842` calls `_COMMAND_TOKEN_RE.sub("", prompt)` with no count, so one unresolvable first token strips **every** `/sc:` token from the trigger prompt, killing context for a valid command later in the same prompt. |
| 11 | `.superclaude_hooks` dirties the tree → Stop blocks read-only sessions | CONFIRMED | Understated. The exclude block is written **only for local scope** (`install_components.py:531-533`), so project scope gets no exclusion at all, and there are **three** dirtying paths rather than one (N5). This repository is immune only because `.gitignore:105,107` was hand-written, which is why the authors never saw it. Overstated in one direction: the per-session guard caps it at one block per session, and `SUPERCLAUDE_INSIGHT_PROMPT=0` opts out. |
| 12 | `_working_tree_changed()` + one-shot guard misjudge session change | CONFIRMED | The guard is keyed `(project, session)`, written immediately before the block, and never cleared. `tests/unit/test_insight_writer.py:996` monkeypatches `_working_tree_changed` in **every** Stop test, so the real `git status --porcelain` behavior — including its treatment of untracked files — is entirely untested. |
| 13 | Harvester scans all assistant records; dedup only from pending | CONFIRMED | Sub-agent transcripts (`isSidechain`) are scanned too. Re-harvest is reachable on the normal path, not just a contrived one: `PreCompact` and `SessionEnd` both rescan the same transcript, and `_find_transcript` falls back to the most recently modified `*.jsonl` when `session_id` is empty. Credit where due: `REQUEST_REASON` deliberately avoids a literal `INSIGHT:` so the request text cannot self-match even without the sentinel. |

---

## New findings

### P1

**N1 — A non-force upgrade wires the new `Stop` hook to the *old* script, producing a blocking Stop on every turn.**

`install_components.py:363-366` skips any script whose target already exists when `force` is false,
and `:405-407` skips `.claude/hooks/hooks.json` the same way. But `:423-427` always merges the
**package's** hooks.json into `settings.json`, and `_merge_hook_arrays` short-circuits to
`user_hooks + new_hooks` for any event with no existing SuperClaude hooks
(`install_settings.py:179-181`) — exactly the case for the brand-new `Stop` event.

Verified against the parent commit: `git show 6d6f09b^1:src/superclaude/scripts/insight_writer.py`
handles only `harvest-from-hook` and `pending-count-from-hook` at `:526`. `request-from-hook` falls
through to argparse and exits 2. On `Stop`, exit 2 is the blocking code and stderr is fed back to the
model as the reason, and `stop_hook_active` cannot help because the old script dies before reading
stdin.

Dogfooding never exposed it because `make sync-user` passes `--force`.

**N2 — None of the merge's script fixes reach an existing install on the documented upgrade command.**

Same root cause, opposite direction. Session-keyed context caching, runtime-state pruning and the new
`session_init` status line all stay unshipped on a plain `superclaude install`, while the Stop hook
registration lands. The wizard's force prompt defaults to no (`install_interactive.py:126`) and the
`click.Abort` fallback passes `force=False`.

**N3 — Any text containing a valid SuperClaude flag hijacks the context loader.**

`resolve_flags()` (`context_loader.py:346`), the `--verbose-context` check (`:636`) and
`_EXECUTION_DIRECTIVES` (`:715-761`) all match the entire `UserPromptSubmit` payload with no context
gate: no code-fence awareness, no `/sc:` scoping, no quoting rules. The Codex report ranked this P2
and described the output as advisory. That is true only of the "did you mean" comments. The
valid-flag branch injects **behavior**.

Reproduced live while writing this document: a sub-agent report that merely *quoted* flag names as
data caused the hook to emit, unrequested,

```
<sc-directive flag="--plan">Lightweight planning mode … wait for user approval …</sc-directive>
<!-- SuperClaude --verbose-context: forcing full .md injection for 9 file(s).
     Expect 5-10x token inflation vs default tiers. -->
```

A flag string in a pasted log, a file under review, a PR body, a web page or a sub-agent's output
silently changes execution mode and can force a 5–10× context expansion. This is a prompt-injection
and context-exhaustion surface, not a wording problem.

**N4 — `Stop` fires per *turn*, not per session, so the ask lands on the first edit turn.**

`hooks.json:140-151` registers `request-from-hook` on `Stop`, which runs at the end of every
assistant turn. The four gates at `insight_writer.py:533-548` are the opt-out env var,
`stop_hook_active`, the one-shot guard, and a dirty tree — none of them is "the session is ending".
`REQUEST_REASON` (`:484-491`) opens "Before finishing:" and asks for the session's lesson, so the
model is asked for a retrospective on work it has just started, and the guard is then consumed for
the rest of the session. Compounding it: `Stop` never harvests — only `PreCompact` and `SessionEnd`
do — so the answer is lost entirely if neither fires.

### P2

**N5 — Three tree-dirtying framework paths, not one.** The Codex remedy names only
`.claude/.superclaude_hooks/`. Also in-tree and unexcluded: `.claude/insights.pending.jsonl`
(`insight_writer.py:58`, written by `PreCompact` mid-session, so the subsystem primes its own
trigger) and `.claude/agent-memory/` (created for project scope by this very merge,
`install_components.py:468`). All three are invisible here only because `.gitignore:105,107` was
hand-written; downstream projects get none of that.

**N6 — Matcher drift produces a duplicate registration, not preservation.**
`install_settings.py:183-190` states that "a user's timeout or matcher edit survives". The timeout
does. The matcher does not: the Counter key is `(matcher, script)` (`:191-195`), so an edited matcher
reclassifies the shipped hook as missing and appends a second entry. `_dedup_hook_array` cannot
collapse them because `_hook_entry_signature` (`:77-91`) includes the matcher. On the `startup`
matcher that means `context_reset.py` and `pending-count-from-hook` each run twice per session start.

**N7 — Transcript discovery ignores the payload.** Claude Code hands the hook `transcript_path` on
stdin. `main()` (`insight_writer.py:632-654`) never reads it; `_find_transcript` (`:123-133`)
reconstructs the path from `cwd` and `session_id` and falls back to the most recently modified
`*.jsonl` in that directory. With two windows open on one repository, `SessionEnd` in window A can
harvest window B's live transcript. The merge edited this exact function without taking the one-line
fix.

**N8 — `_PRUNABLE_PREFIXES` owns a filename that does not exist.** `utils/__init__.py:118-124` lists
`"hook_tracker"`; the real file is `hook_executions.json` (`hook_tracker.py:32`), so the sweep never
touches it. Consequence today is cosmetic because the tracker bounds itself, but the constant is the
sweep's contract and `TestHookStatePruning` never exercises it.

**N9 — `sandbox_home` does not isolate import-time-resolved paths.** `tests/conftest.py:19-37`
redirects `HOME` in an autouse fixture, which fixes call-time resolvers such as
`loop_guard._state_file()`. It does not fix import-time constants: `mcp_fallback.py:27`,
`hook_tracker.py:31` and `context_loader.py:70` all resolve `hook_state_dir()` at module import,
which happens during pytest collection, before any fixture runs. `test_context_loader.py:12` imports
at module level, so collection alone runs `_CACHE_DIR.mkdir()` against the developer's real
`~/.claude`. `test_mcp_fallback.py` patches all three constants by hand, which is the tell.

**N10 — `session_init.reset_context_cache()` resets blind.** `session_init.py:63-70` calls
`context_reset.reset_context_cache()` with no session id, so `get_cache_file(None)` deletes the
project-only fallback cache and `prune_fallback_ledger(None)` prunes without knowing which session is
live — while `context_reset.main()` on the same `SessionStart` event does it correctly with the id
from the payload.

**N11 — Sentinel exclusion drops the whole record.** `insight_writer.py:347-350` does
`if REQUEST_SENTINEL in content: continue`, discarding the record rather than the sentinel span. A
reply that quotes the request while also emitting the real `INSIGHT:` line — the natural "you asked
for X, here it is" shape — is silently dropped. Commit `e99bd69` already fixed 13 noise entries in
this same regex surface; widening the scan to assistant records reopens it from the other side.

**N12 — `install_claude_sc_md` failure is not counted.** Same root as Codex 6, different instance;
detail in that row above.

**N13 — `troubleshoot.md` has the `git.md` shape.** `troubleshoot.md:2` asserts the command "writes a
failing test and applies the fix" unconditionally, while its `<bounds><never>` says "risky fixes
without confirm" and `--fix` is opt-in. The Codex report judged the nine rewritten descriptions as a
group and never checked description-against-bounds per file.

---

## Remediation

Ordering is forced by two shared decisions — one hook-identity function (Task 2) and one
state-location policy (Task 3). Task 1 comes first because until it lands, no other runtime fix
reaches an upgrading user at all.

### Task 1 — Framework-owned artifacts always update (N1, N2)

**Files:** Modify `src/superclaude/cli/install_components.py` | Test: `tests/unit/test_cli_install.py`

- [ ] Failing test first: write a stub `insight_writer.py` without `request-from-hook` into the
      target, run `install_all(force=False)`, assert the installed script carries the `request`
      subparser afterwards
- [ ] Drop the `exists() and not force → skip` guard for `scripts/*.py` (`:363-366`) and
      `.claude/hooks/hooks.json` (`:405-407`). These are SuperClaude-only build outputs, not
      user-editable content; `--force` keeps its meaning for settings, commands, agents and core
- [ ] Add a suite-level invariant: every `command` in `hooks.json` resolves to a subcommand the
      shipped script actually accepts — the regression that would have caught N1 at authoring time
- [ ] Verify: `uv run pytest tests/unit/ -k "install" -v`

### Task 2 — One hook identity for merge, force, uninstall and inventory (Codex 1, 2, 3, 4; N6)

**Files:** Modify `src/superclaude/cli/install_settings.py`, `src/superclaude/cli/install_inventory.py` | Test: `tests/unit/test_install_settings.py`, `tests/unit/test_cli_install.py`

Sub-steps land in this order; inventory before ownership would report "missing" for hooks the merge
logic still considers present.

- [ ] **Identity.** Extend `_hook_script_id()` to `(script filename, stable entrypoint/subcommand)`,
      normalising only genuinely mutable options. Ship the argument-normalisation rule in the same
      change: without one, every existing registration whose args drifted is reclassified as missing
      and gets a duplicate appended — N6, amplified
- [ ] **Ownership.** Move `_is_superclaude_hook()` from outer-entry to inner-hook granularity.
      `--force` replaces SuperClaude inner hooks in place, preserving order and any user inner hooks
      in the same entry. `uninstall_hooks_from_settings()` uses the same decomposition and drops an
      entry only when it ends up empty
- [ ] **Retired sweep.** Before a force merge, walk all existing event types rather than only those
      present in the new config, remove SuperClaude inner hooks, then clean empty entries and events
- [ ] **Inventory.** Compare normalized identity sets; report `matched / shipped` with separate
      `missing`, `obsolete` and `duplicate` counts. Fix `--dry-run` (`install_inventory.py:462-467`)
      to count inner hooks so it agrees with `_count_shipped_hooks`
- [ ] Regression tests: a user inner hook at head, middle and tail of a mixed entry under both force
      and uninstall; matcher drift yields one entry not two; a retired event is swept by force; 14
      obsolete hooks report `0/14` with `obsolete: 14`
- [ ] Verify: `uv run pytest tests/unit/ -k "settings or hooks or install" -v`

### Task 3 — State-location policy and the dirty-tree gate (Codex 11, 12; N5)

**Files:** Modify `src/superclaude/scripts/insight_writer.py`, `src/superclaude/cli/install_git_exclude.py` | Test: `tests/unit/test_insight_writer.py`, `tests/unit/test_install_git_exclude.py`

State stays under `claude_base()` — see the constraint at the top of this document.

- [ ] **Defensive filter.** `_working_tree_changed()` parses `git status --porcelain` paths instead
      of testing the output for non-emptiness, and ignores framework-owned paths
      (`.claude/.superclaude_hooks/`, `.claude/insights*.jsonl`, `.claude/agent-memory*/`). This
      holds in every scope, including project scope, which gets no exclude block at all
- [ ] **Exclusion.** Add the same three paths to `_collect_local_entries()`
- [ ] **Session baseline.** Record a `git status` fingerprint at `SessionStart` and diff at `Stop`,
      so "did this session change code" stops being a proxy for "is the tree dirty". The one-shot
      guard becomes "a qualifying change was asked about", not "the first dirty observation". The
      baseline file lives in `hook_state_dir()`, already covered by the filter above
- [ ] **Un-mock the test.** Add an end-to-end test on a fresh committed repository: install, run a
      read-only prompt through the loader, assert `git status --porcelain` is clean and the Stop hook
      emits nothing. The current Stop tests monkeypatch `_working_tree_changed` universally
      (`test_insight_writer.py:996`)
- [ ] Verify: `uv run pytest tests/unit/ -k "insight or git_exclude" -v`

**Residual, accepted.** The exclude block is a per-clone `.git/info/exclude` written only for local
scope, so a project-scope install still shows `.claude/.superclaude_hooks/` in the user's own
`git status`. The Stop gate no longer reads it, which is the defect; making the tree visually clean
for project scope would mean extending `install_git_exclude` beyond its stated local-only contract,
and that was declined. A project that wants a clean status adds the path to its own `.gitignore`.

### Task 4 — Stop-hook timing and the INSIGHT pipeline (N4, N7, N11; Codex 13)

**Files:** Modify `src/superclaude/scripts/insight_writer.py`, `src/superclaude/hooks/hooks.json`, `src/superclaude/commands/insight.md` | Test: `tests/unit/test_insight_writer.py`

- [ ] **Event/prompt mismatch (N4).** Either move the request off per-turn `Stop`, or rewrite
      `REQUEST_REASON` to ask for what a mid-session turn can actually answer. Pair the choice with
      harvesting on the same event — today the answer given at `Stop` is only collected by a later
      `PreCompact` or `SessionEnd`, and is lost if neither fires
- [ ] **Transcript path (N7).** Read `transcript_path` from the hook payload; keep `_find_transcript`
      as fallback only
- [ ] **Harvest scope (Codex 13).** Correlate markers to the request rather than scanning every
      assistant record, and skip `isSidechain` records
- [ ] **Sentinel (N11).** Strip the sentinel span, do not drop the record
- [ ] **Dedup (Codex 13).** Add a durable harvested-UUID ledger, shipped together with its storage
      justification and its pruning rule — under `hook_state_dir()` it needs a name the sweep
      protects, and it grows one line per marker forever otherwise
- [ ] Regression tests: an explanatory `INSIGHT:` inside a document is not harvested;
      harvest → promote → harvest of one transcript yields one entry; a reply quoting the sentinel
      while carrying a real marker is harvested
- [ ] Verify: `uv run pytest tests/unit/test_insight_writer.py -v`

### Task 5 — Context-loader input gating (N3; Codex 9, 10)

**Files:** Modify `src/superclaude/scripts/context_loader.py` | Test: `tests/unit/test_context_loader.py`

- [ ] **Context gate (N3).** Strip fenced code blocks and inline-code spans before any flag scanning,
      and apply the gate to all three consumers — `resolve_flags()` (`:346`), the `--verbose-context`
      check (`:636`) and `_EXECUTION_DIRECTIVES` (`:715-761`). Behavioral directives must never fire
      from quoted text
- [ ] **Fuzzy threshold (Codex 9).** Raise the retired-flag cutoff well above `0.6` and correct the
      comments at `:280-281` and `:380`, which claim Levenshtein ≤ 2 while the code uses `difflib`.
      Do **not** gate the notice on `/sc:` invocation: the evidence motivating the feature is 479
      `--think*` and 159 `--parallel` uses typed in bare prompts, so a `/sc:`-only gate would
      suppress it exactly where the data says it is needed. The fence exclusion is the gate that
      survives its own evidence
- [ ] **Command tokens (Codex 10).** Iterate every `/sc:` token, emit a per-token notice, and strip
      only unresolvable tokens — `_COMMAND_TOKEN_RE.sub("", prompt)` at `:840-842` currently removes
      valid ones too
- [ ] Negative tests: `cargo test --parallel`, `curl --link`, `pytest --no-parallel`,
      `tool --parallelism 4`, `git status --porcelain`, and a fenced block containing
      `--verbose-context` — all silent, no directive emitted
- [ ] Verify: `uv run pytest tests/unit/test_context_loader.py -v`

### Task 6 — Installer failure honesty and cancel semantics (Codex 5, 6; N12)

**Files:** Modify `src/superclaude/cli/main.py`, `src/superclaude/cli/install_components.py` | Test: `tests/unit/test_install_interactive.py`, `tests/unit/test_cli_install.py`

- [ ] **Cancel (Codex 5).** Decide unattended-ness before entering the wizard using a positive
      non-interactive signal, and route only that path to the default install. Deleting the `Abort`
      fallback outright would restore the defect this merge fixed (bare install completing nothing in
      CI or `claude -p`), so the detector has to be built, not just removed. Any `Abort` raised after
      a prompt has started stays a cancel
- [ ] Rewrite `test_install_interactive.py:165-179`, which currently pins the present behavior as
      intended
- [ ] New tests: bare stdin EOF; EOF after the first prompt; EOF after a local or project scope
      choice; `KeyboardInterrupt` at each step. No fallback install fires in any of them, and no run
      installs to a scope the user did not pick
- [ ] **Failure propagation (Codex 6, N12).** Give `ensure_agent_memory_dir()` a return that
      separates "no location by design" from "mkdir failed", count that failure, and count
      `install_claude_sc_md`, the CLAUDE.md import update and the git-exclude write in `total_failed`
      so `overall_success` cannot be `True` with a ❌ on screen. Tests: permission denied, a regular
      file at the memory path, a read-only parent
- [ ] Verify: `uv run pytest tests/unit/ -k "install" -v`

### Task 7 — Test isolation and state hygiene (N8, N9, N10)

**Files:** Modify `tests/conftest.py`, `src/superclaude/hooks/mcp_fallback.py`, `src/superclaude/hooks/hook_tracker.py`, `src/superclaude/scripts/context_loader.py`, `src/superclaude/utils/__init__.py`, `src/superclaude/scripts/session_init.py`

- [ ] Convert the three import-time `hook_state_dir()` constants to call-time resolvers or lazy
      accessors so `sandbox_home` actually holds
- [ ] Add the empirical regression: snapshot `~/.claude/.superclaude_hooks` before and after a full
      `uv run pytest` and assert no delta — the existing `loop_guard`-only probe does not prove it
- [ ] Fix `_PRUNABLE_PREFIXES`: `"hook_tracker"` → `"hook_executions"`, with a test that the sweep
      collects an aged tracker file
- [ ] Pass the `SessionStart` session id through `session_init.reset_context_cache()`
- [ ] Verify: `uv run pytest tests/unit/ -k "scope_paths or mcp_fallback or session_init" -v`

### Task 8 — Command description contracts (Codex 8; N13)

**Files:** Modify `src/superclaude/commands/git.md`, `src/superclaude/commands/troubleshoot.md` | Test: `tests/unit/test_command_structure.py`

- [ ] `git.md:2` — remove "approves history-rewriting ops"; state that invoking the command
      authorises the workflow only, and that each destructive sub-operation needs its own
      confirmation naming the operation and target. Delete "wrong fire cost a revert", which
      contradicts the same file's `git.md:64` ("Force-push main/master destroy team work +
      irreversible")
- [ ] `troubleshoot.md:2` — condition the "writes a failing test and applies the fix" claim on
      `--fix`, matching its `<bounds>`
- [ ] Add a structural lint asserting that no description claims an action its `<bounds><never>` or
      `<approval_required>` block gates. Today's lint (`NEGATIVE_TRIGGER_GATE`,
      `test_command_structure.py:36`) is lexical only, which is why both files passed
- [ ] Verify: `uv run pytest tests/unit/test_command_structure.py -v`

---

## Deferred to a follow-up (P3)

- Codex 7 — a local install is labeled `project`; needs precedence rules across four non-exclusive
  discriminators and no install manifest exists
- `_working_tree_changed()` returns `False` outside a git repository (`git status` exits 128), so the
  whole INSIGHT producer is silently inert for non-git projects and for anyone without `git` on PATH
- `mcp_fallbacks.json` now has two read-modify-write writers with no locking
  (`utils/__init__.py:196-230` and `mcp_fallback.py:57-95`); `os.replace` prevents corruption but not
  lost updates
- `session_init._count("agents")` globs all of `<base>/agents/*.md`, counting user- and team-authored
  agents as SuperClaude's
- `install_settings.py:265-273` compares `merged_array` against the **deduped** array, so "already
  registered" can print while the file was in fact rewritten
- `install_interactive.py` renders the `hooks_registered` row with an "N new, M kept" action label
  that is meaningless for a settings-registration count

## Verification

Per task: the named `uv run pytest` selection, written failing-first.

Global, after every task:

```
uv run pytest      # expect 2157 passed, 28 skipped, 4 deselected — any failure is a regression
make lint
```

End-to-end, after Tasks 1–4, in a scratch git repository **outside this tree** (per
`.claude/rules/gotchas/authoring.md`, `probe-observer-effect`: probing from inside the repository
contaminates the baseline):

1. Install the parent commit's content, then run `superclaude install` without `--force` from this
   branch. Assert the on-disk `insight_writer.py` accepts every subcommand `settings.json` registers,
   and that a `Stop` event exits 0. This is N1's proof.
2. Fresh committed repository, project-scope install, one read-only prompt: `git status --porcelain`
   is clean and the Stop hook emits nothing.
3. A prompt carrying `--verbose-context` and `--plan` inside a fenced code block emits no directive
   and no flag notice.
4. A `--force` install over a settings file holding a mixed entry (SuperClaude and user inner hooks)
   plus a hook on a retired event: the user inner hook survives in place, the retired hook is gone,
   and `--list-all` reports `matched / shipped` honestly.

Two items stay `human_needed` and are recorded rather than automated: whether Claude Code caps
repeated exit-2 responses from a `Stop` hook, and a real multi-session week confirming that INSIGHT
entries accumulate at useful moments.
