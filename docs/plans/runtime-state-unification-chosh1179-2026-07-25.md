---
status: complete
revised: 2026-07-25
---

# Runtime State Unification

Unify where SuperClaude writes files and directories while it is running, so every
runtime path resolves through one rule instead of five ad-hoc mechanisms.

## Current state

Five different resolution mechanisms are in use for runtime paths.

| Writer | Path written | How it resolves | Reachable by uninstall |
|---|---|---|---|
| `context_loader.py:64,66` | `<claude_base>/.superclaude_hooks/claude_context_<id>.txt` | `hook_state_dir()`, id = `md5(os.getcwd())[:8]` | yes (`install_inventory.py:404`) |
| `context_reset.py:23,27` | same file | `hook_state_dir()`, id = `md5(os.getcwd())[:8]` | yes |
| `hook_tracker.py:31-33` | `<claude_base>/.superclaude_hooks/{hook_executions.json,current_session.txt}` | `hook_state_dir()` | yes |
| `mcp_fallback.py:27` | `<claude_base>/.superclaude_hooks/mcp_fallbacks.json` | `hook_state_dir()` | yes |
| `loop_guard.py:28-30` | `<project>/.claude/loop_guard_state.json` | inline `CLAUDE_PROJECT_DIR or os.getcwd()` | **no** — see D1 |
| `insight_writer.py:38-39` | `.claude/insights.jsonl`, `.claude/insights.pending.jsonl` | **CWD-relative literal** | no (correct — user data) |
| `insight_writer.py:281,445` | same two files | `Path(cwd)` from hook payload | no |
| `session_init.py:161` | (reads only) `Path.cwd()/packages,apps,libs,services` | `Path.cwd()` | n/a |

`superclaude/utils/__init__.py` already exposes the canonical resolvers —
`project_root()`, `claude_base()`, `hook_state_dir()` — but only four of the eight
call sites use them.

## Defects this causes

**D1 — loop_guard state escapes its install scope and survives uninstall.**
`loop_guard.py` always writes to `<project>/.claude/loop_guard_state.json`, but
`install_inventory.py:387` removes `base_path/"loop_guard_state.json"`. Under a
user-scope install `base_path` is `~/.claude`, so the cleanup targets a file that
never exists while the real one sits in whichever repo the user was working in.
Two consequences: a user-scope install leaves a footprint in every project it
touches, and uninstall never removes any of them.

**D2 — the context dedup cache is keyed by CWD, not by project.**
Both `context_loader.py:63` and `context_reset.py:27` compute the cache key as
`md5(os.getcwd())[:8]`. Hook CWD is not guaranteed to be the project root
(documented in `.claude/rules/gotchas/hooks.md`, `hook-path-scope`). A hook firing
from a subdirectory reads and writes a different cache file, so dedup silently
fails and contexts re-inject. This is the same failure class as the already-fixed
skills-count bug (9 skills reported instead of 22).

**D3 — `insights.jsonl` has two different resolutions in one module.**
The module constants at `insight_writer.py:38-39` are CWD-relative literals; the
hook entry points at `:281` and `:445` rebuild the same paths from the hook
payload's `cwd`. Running `insight_writer.py append` from a subdirectory (the Bash
tool's CWD persists across calls and is not pinned to the project root) creates a
second `insights.jsonl` under that subdirectory, splitting the user's insight
history with no error.

**D4 — no stated rule, so each new hook re-decides.**
Nothing in the codebase says where a new hook should put its state. The result is
the table above: four call sites right, four wrong, and a hardcoded uninstall
special case papering over one of them.

## Design

Runtime output splits into two classes with opposite lifetimes. Collapsing both
into one directory would be wrong — deleting `insights.jsonl` on uninstall is data
loss. So unify the **rule**, not the directory.

| Class | Owner | Location | On uninstall |
|---|---|---|---|
| Ephemeral machine state (regenerable) | SuperClaude | `hook_state_dir()` = `<claude_base>/.superclaude_hooks/` | removed wholesale |
| Durable project data (user's) | user | `project_root()/.claude/` | preserved |

**The rule:** every runtime path resolves through `superclaude.utils`. No
`os.getcwd()`, no `Path.cwd()`, no CWD-relative literals in `hooks/` or `scripts/`.

Class assignment:

- Ephemeral: context dedup cache, context reset, hook tracker, MCP fallback log,
  **loop_guard state** (15-minute sliding window circuit-breaker — regenerable by
  definition).
- Durable: `insights.jsonl`, `insights.pending.jsonl`.

Moving loop_guard state into `hook_state_dir()` introduces one problem: under a
user-scope install that directory is shared across projects, and loop_guard's
state (`{"entries": [...]}`) carries no project key, so two concurrent projects
would cross-contaminate each other's error counters. The fix is the same key that
D2 needs, so one helper covers both.

## Changes

### C1 — add `project_key()` to `superclaude/utils/__init__.py`

```python
def project_key() -> str:
    """Stable short id for the active project, for per-project state filenames."""
    return hashlib.md5(str(project_root()).encode()).hexdigest()[:8]
```

Replaces three ad-hoc `md5(os.getcwd())[:8]` computations and re-anchors them from
CWD to project root. Not speculative: two consumers, three call sites, all in this
change set.

**Verify:** new unit test — `project_key()` is identical when CWD is a
subdirectory but `CLAUDE_PROJECT_DIR` is unchanged, and differs across projects.

### C2 — fix the context cache key (D2)

- `context_loader.py:63` — `SESSION_ID = project_key()`
- `context_reset.py:27` — `session_id = project_key()`

**Verify:** `uv run pytest tests/manual/test_context_loader_tiers.py tests/unit/ -k context`
plus a new test asserting `get_cache_file()` returns the same path from a
subdirectory CWD.

### C3 — move loop_guard state into hook state dir (D1)

- `loop_guard.py:28-30` — `hook_state_dir() / f"loop_guard_{project_key()}.json"`,
  drop the inline `CLAUDE_PROJECT_DIR or os.getcwd()` duplication; update the
  module docstring (`:11-12`) which states the old path.

Git safety is already covered: `.gitignore:105` ignores `.claude/.superclaude_hooks/`.

**Verify:** `tests/unit/test_loop_guard.py` (3 assertions at `:216,:233,:253`),
`tests/unit/test_safety_hooks.py:193`, and
`tests/unit/test_eval_harness.py:95` — that last one regex-scrapes
`Path(root) / "x" / "y"` out of `loop_guard.py` source and will break; rewrite it
to assert against the new resolver. `evals/run_eval.py:57` `WS_GITIGNORE` must drop
`.claude/loop_guard_state.json` in favor of `.claude/.superclaude_hooks/`.

### C4 — delete the uninstall special case (D1)

`install_inventory.py:386-398` — remove the `loop_guard_state.json` loop entirely.
Step 5b's `shutil.rmtree` of `.superclaude_hooks` at `:404` now covers it.

**Verify:** `uv run pytest tests/unit/test_scope_paths.py tests/unit/test_hooks.py`
plus a dry-run uninstall showing the state dir removed and no dangling entry.

### C5 — single resolution for insights files (D3)

`insight_writer.py` — module constants become
`project_root() / ".claude" / "insights.jsonl"` (and `.pending.jsonl`); the inline
rebuilds at `:281` and `:445` use the same constants. `project_root()` wins over
the hook payload's `cwd` because it is the project anchor; payload `cwd` is the
session's working directory and can be a subdirectory.

**Verify:** `uv run pytest tests/unit/test_insight_writer.py`; new test asserting
`append` from a subdirectory CWD writes to the project-root file.

### C6 — anchor the multi-dir scan (low severity)

`session_init.py:161` — `Path.cwd()` → `project_root()`. Affects only a banner
count, but it is the exact pattern D2 fixes elsewhere, and leaving one instance
behind is what produced D4.

**Verify:** existing session_init tests.

### C7 — write the rule down

- `superclaude/utils/__init__.py` module docstring: state the two-class table.
- `.claude/rules/gotchas/hooks.md`: add
  `runtime-path-single-resolver: all runtime paths via superclaude.utils
  (project_root/claude_base/hook_state_dir/project_key) — never os.getcwd(),
  Path.cwd(), or CWD-relative literals in hooks/ or scripts/. Ephemeral state
  under hook_state_dir() (uninstall removes it); durable user data under
  project_root()/.claude (uninstall preserves it).`
- `src/superclaude/ARCHITECTURE.md`: runtime-state section pointing at the table.

**Verify:** `uv run pytest` full suite; markdown-only, no test risk.

## Out of scope

- `scripts/auto_improve/` (`<repo>/.worktrees/auto-improve-<ts>/results.tsv`,
  `auto_improve.pid`) and `scripts/parallel_ab/` (output defaults to the spec
  file's parent, overridable with `--out-dir`). These are developer tools invoked
  explicitly, not hook runtime — nothing is broken and no user-visible footprint
  leaks. Bringing them under the same rule is a separate, optional change.
- `.claude/scheduled_tasks.lock` and `.claude/agent-memory*/` — written by Claude
  Code itself, not SuperClaude.
- Content-output conventions (`docs/reports/`, `docs/plans/`, `docs/specs/`,
  `.scratch/<feature>/`, `PROJECT_INDEX.md`) — already unified in
  `core/rules/RULES_DOCS.md`; a different problem from runtime state.

## Risks

- **Orphaned state after C3.** Existing `<project>/.claude/loop_guard_state.json`
  files are not migrated. Impact is nil — the state is a 15-minute sliding window
  and self-heals on the next tool call — but the stale files stay on disk. Adding a
  one-shot cleanup would fail the necessity test; note it in the changelog instead.
- **Cache invalidation on C2.** Changing the key orphans every existing
  `claude_context_<old-id>.txt`. First prompt after upgrade re-injects contexts
  once, then dedup resumes. Acceptable.
- **`project_root()` falls back to CWD** when `CLAUDE_PROJECT_DIR` is unset (CLI
  invocations outside a Claude Code session). Behavior there is unchanged from
  today; C5 and C6 do not make it worse.

- **Accepted: loop_guard state now outlives its project.** Before C3 the state
  file sat inside the project and died with the repo. Under a user-scope install
  it now sits in the shared `~/.claude/.superclaude_hooks/` as
  `loop_guard_<project_key>.json`, one per project, with no TTL —
  `cleanup_old_sessions()` (`hook_tracker.py:161`) prunes entries inside
  `hook_executions.json`, not files in the directory. Deleting a repo leaves its
  state file behind until `superclaude uninstall`.

  Accepted rather than fixed. The files are 100–400 bytes holding a 15-minute
  sliding window, so the cost is a slow trickle of dead bytes, not a failure —
  and `claude_context_<key>.txt` already had exactly this shape before this
  change, so a sweeper would be new machinery for a problem neither family has
  actually caused. Revisit if the directory ever holds enough files to matter;
  the fix then is one TTL sweep over `hook_state_dir()` covering both families,
  not a per-writer cleanup.

  Rejected alongside it: stamping a `"project": "<path>"` field into the state
  JSON to make the hashes traceable. The files are disposable by design, so the
  worst case for a confused reader is deleting all of them and losing nothing.

## Verification for the whole change set

Baseline is 2075 passed / 28 skipped / 4 deselected / 0 failures. Any failure not
in the six files named above is a regression. Final gate:

```bash
uv run pytest                       # expect >= 2075 passing, 0 failures
make lint                           # ruff clean
superclaude uninstall --dry-run --scope user    # no loop_guard_state.json entry, .superclaude_hooks listed
```

## Outcome

All of C1–C7 applied. `uv run pytest` → 2075 passed / 28 skipped / 4 deselected /
0 failures, exactly the baseline. `make lint` clean. `uninstall --dry-run` reports
a single `.superclaude_hooks` removal under both user and project scope, with no
dangling `loop_guard_state.json` entry and no insights entry.

## Post-review corrections

A `/sc:review` pass on the diff found the plan's three specified verification
tests had not been written — test count was unchanged at 2075, so the
subdirectory-anchoring behavior the whole change exists to fix had nothing
proving it. Added `TestProjectKey` (stability from a subdirectory, difference
across projects, filename safety) and `TestContextCacheKeying` (cache filename
stable across CWD, distinct across projects) to `tests/unit/test_scope_paths.py`.
Baseline moves 2075 → 2080; `CLAUDE.md`, `AGENTS.md`, `README.md` updated.

Writing those tests surfaced one thing the plan had wrong: `context_reset.py`
resolves `hook_state_dir()` once at module import, so the cache *directory*
cannot follow monkeypatched env within a test session — only the filename can.
That is correct for a one-shot hook subprocess (the env is set before Python
starts) and is left alone; the test asserts the filename and says why.

Also from the review: `pending-count --cwd` had become a flag that silently did
nothing once the pending file moved to `project_root()`, so it was removed from
the parser and from `main()`'s hook dispatch. And `project_key()` now passes
`usedforsecurity=False` to `hashlib.md5`, which bare `md5()` needs to survive a
FIPS-enforcing Python build.

## Follow-up: a ninth call site the table missed

Post-merge verification found `memory_staleness.py:88` resolving
`HOME_PROJECTS / encode_project_path(os.getcwd())`. The audit table above lists
eight call sites; there were nine. It is a live SessionStart hook
(`hooks.json:17`), and it fails in exactly the D2 shape — measured from
`src/superclaude`:

| CWD | resolved | exists |
|---|---|---|
| project root | `~/.claude/projects/-Users-chosh-Repos-ajitta-superclaude/memory` | yes |
| `src/superclaude` | `…-superclaude-src-superclaude/memory` | no |

A missing directory makes `scan_stale_entries()` return `[]`, so the staleness
warning silently never fires. Fixed by anchoring on `project_root()`.
`HOME_PROJECTS` keeps `Path.home()` deliberately — that directory belongs to
Claude Code, which writes auto-memory under `~/.claude/projects/` regardless of
SuperClaude's install scope; only the project anchor was ours to fix.

Verified: new `test_memory_dir_anchored_on_project_root_not_cwd` fails on the old
resolver and passes on the new one, and the installed hook run from `src/deep` of
a synthetic project found its stale fixture. Baseline 2080 → 2081.

That the site was missed is D4 itself — the audit enumerated writers of
`.claude/` paths, and this one writes under `~/.claude/projects/`, so it fell
outside the grep. The search surface for this rule is every script reachable from
`hooks.json`, not every script touching `.claude/`.

## Deviations from the plan

- **C5 needed functions, not re-anchored constants.** `INSIGHT_FILE` /
  `PENDING_FILE` became `_insight_file()` / `_pending_file()`. Module constants
  evaluated at import time would freeze the anchor before any test could set it,
  and `_read_pending(path=PENDING_FILE)` had the same problem in a default
  argument.
- **C5 changed a contract the tests encoded.** `cmd_harvest` and
  `cmd_pending_count` previously anchored the pending file on the hook stdin
  payload's `cwd`; they now use `project_root()` like every other writer.
  Otherwise harvest writes one file and promote reads another — the D3 split.
  `args.cwd` still anchors *transcript* lookup, since Claude Code encodes the
  session cwd into the transcript directory name.
  `test_reads_cwd_from_stdin_payload` was rewritten as
  `test_project_root_wins_over_stdin_cwd`, with a decoy pending file in a
  subdirectory.
- **Test fixtures had to pin the anchor, and the cost of not doing so was
  measured.** `monkeypatch.chdir(tmp_path)` alone no longer isolates anything —
  `project_root()` reads `CLAUDE_PROJECT_DIR` first, and `claude_base()` falls
  back to the real `~/.claude` without a `<tmp>/.claude/superclaude` marker.
  Before the fixtures were pinned, test runs left 19 stray `loop_guard_*.json`
  in the real `~/.claude/.superclaude_hooks/` and appended 33 fixture lines to
  the repo's real `.claude/insights.jsonl`. Both cleaned up; captured as the
  `test-anchor-env` gotcha.
- **The eval-harness drift guard was rewritten, not just re-pointed.** It used to
  regex-scrape a `Path(root) / "x" / "y"` literal out of `loop_guard.py`, which
  the change deleted. It now calls the real `_state_path()` against a
  project-scope tmp layout, so it cannot go stale the same way again.
- **Two dead entries removed as orphans of this change**: `.gitignore`'s
  `.claude/loop_guard_state.json` (already covered by `.claude/.superclaude_hooks/`
  one line above) and the untracked `.claude/loop_guard_state.json` this repo had
  from the old path.
- **`tests/unit/test_safety_hooks.py:193` deliberately left alone.** It passes an
  explicit path literal to `_save_state()` and never touches `_state_path()`, so
  it still tests what it claims to. Renaming the literal would be scope creep.
