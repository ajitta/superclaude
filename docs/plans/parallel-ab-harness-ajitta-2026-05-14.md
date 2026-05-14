---
status: implementing
revised: 2026-05-15
---

# Parallel A/B Harness — Implementation Plan

**Goal:** Ship a parallel sub-agent harness that runs N variants of a prompt/skill against one scenario, captures structured observations, and aggregates into a side-by-side decision matrix without polluting main-thread context.

**Architecture:** Five-module Python sub-package under `src/superclaude/scripts/parallel_ab/`, mirroring the `auto_improve/` pattern. Orchestrator launches N async subprocess runners (each invokes `claude -p` per variant), each runner writes an observation JSON to `docs/experiments/<topic>/obs-<id>.json`, aggregator merges into `matrix.md` + `decision.md`. Main thread reads only the two `.md` files.

**Tech Stack:** Python 3.10+, asyncio (subprocess pool), PyYAML (spec parsing), stdlib `json` + `subprocess`. No new external deps. Tests via `pytest` + `pytest-asyncio` (already available — `auto_improve` uses async patterns).

**Spec source:** `docs/specs/parallel-ab-harness-design-ajitta-2026-05-14.md`

## Decisions Locked from Spec Open Questions

| Question | Decision | Rationale |
|---|---|---|
| `Task` tool vs `claude -p` | `claude -p` only for v1 | Spec workflow assumes true fork; `Task` integration deferred to a follow-up plan. |
| `--bare` auth fallback | Conditional retry without `--bare` when exit code matches auth-fail pattern | Implements `oauth_fallback: true` from variant spec. |
| Cost ceiling | Env vars `AB_MAX_PARALLEL` (default 8), `AB_TIMEOUT_S` (default 120). No dollar accounting in v1 | Cost is bounded by N × timeout; dollar tracking is a separate observability concern. |
| Karpathy 3-grade scoring | Pass-through descriptive strings only in v1 | Spec axes are free-form text; rubric-based scoring deferred until human-tagged corpus exists. |

## File Map

| File | Job | Phase |
|---|---|---|
| `src/superclaude/scripts/parallel_ab/__init__.py` | Package marker | 1 |
| `src/superclaude/scripts/parallel_ab/spec_loader.py` | Parse + validate `variants.yaml` → dataclass | 1 |
| `src/superclaude/scripts/parallel_ab/observation.py` | Observation JSON schema + `emit()` + `validate()` helpers | 2 |
| `src/superclaude/scripts/parallel_ab/runner.py` | Single-variant subprocess wrap of `claude -p`, captures stdout/timing/exit, writes obs JSON | 3 |
| `src/superclaude/scripts/parallel_ab/aggregator.py` | Read N obs JSON → emit `matrix.md` + `decision.md` | 4 |
| `src/superclaude/scripts/parallel_ab/orchestrator.py` | Async parallel pool, cost guards, calls runner + aggregator | 5 |
| `src/superclaude/scripts/parallel_ab/cli.py` | `python -m superclaude.scripts.parallel_ab <variants.yaml>` entry | 5 |
| `tests/unit/scripts/parallel_ab/__init__.py` | Test package marker | 1 |
| `tests/unit/scripts/parallel_ab/test_spec_loader.py` | Spec parser tests | 1 |
| `tests/unit/scripts/parallel_ab/test_observation.py` | Schema round-trip + validation tests | 2 |
| `tests/unit/scripts/parallel_ab/test_runner.py` | Runner tests w/ mock subprocess | 3 |
| `tests/unit/scripts/parallel_ab/test_aggregator.py` | Aggregator tests w/ fixture obs files | 4 |
| `tests/unit/scripts/parallel_ab/test_orchestrator.py` | Orchestrator tests w/ stub runner | 5 |
| `tests/integration/test_parallel_ab_e2e.py` | E2E gated on `AB_E2E=1`, hits real `claude -p` | 6 |
| `tests/unit/scripts/parallel_ab/fixtures/variants_min.yaml` | Minimal valid spec | 1 |
| `tests/unit/scripts/parallel_ab/fixtures/obs_*.json` | Observation fixtures | 4 |
| `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml` | E2E scenario spec | 6 |

No edits to existing files except: append to `src/superclaude/scripts/README.md` listing the new sub-package (Phase 5).

## Success Criteria (overall)

- Phase 1-5: `uv run pytest tests/unit/scripts/parallel_ab/ -v` → all pass.
- Phase 6: `AB_E2E=1 uv run pytest tests/integration/test_parallel_ab_e2e.py -v` → 1 pass, generates `matrix.md` + `decision.md` under `docs/experiments/brainstorm-ab-2026-05-14/`.
- Full suite baseline: `uv run pytest` ≥ 1904 pass (current baseline) + Phase-1..5 unit tests added (~25 estimated; **56 actual**).
- No regressions in unrelated tests.

---

### Task 1: Spec Loader

**Files:** Create: `src/superclaude/scripts/parallel_ab/__init__.py`, `src/superclaude/scripts/parallel_ab/spec_loader.py`, `tests/unit/scripts/parallel_ab/__init__.py`, `tests/unit/scripts/parallel_ab/test_spec_loader.py`, `tests/unit/scripts/parallel_ab/fixtures/variants_min.yaml`

**Behavior:** `load_spec(path: Path) -> ABSpec` returns a frozen dataclass `ABSpec(scenario, variants, runner)`. Required fields per spec section "Variant spec (YAML)". Raises `SpecError` on missing required keys, unknown runner CLI, or duplicate variant IDs.

- [x] Step 1: Write `test_spec_loader.py` covering: valid min spec loads; missing `scenario.input` raises `SpecError`; duplicate variant ids raise `SpecError`; unknown runner.cli raises `SpecError`; default runner.timeout_seconds = 60 when omitted; `bare` and `oauth_fallback` default to `True` and `True` respectively.
- [x] Step 2: Run `uv run pytest tests/unit/scripts/parallel_ab/test_spec_loader.py -v` → expect failures (module missing).
- [x] Step 3: Implement `spec_loader.py` w/ `@dataclass(frozen=True)` types and `load_spec()`.
- [x] Step 4: Run pytest → all pass. **11/11 passed.**
- [x] Step 5: Commit `feat(parallel-ab): add variants.yaml spec loader` — `32c7e6d`.

### Task 2: Observation Schema

**Files:** Create: `src/superclaude/scripts/parallel_ab/observation.py`, `tests/unit/scripts/parallel_ab/test_observation.py`

**Behavior:** `Observation` dataclass matches spec JSON schema. `emit(obs, path)` writes pretty-JSON; `validate(dict) -> Observation` round-trips. Unknown keys logged as warning, not error (forward-compat). Missing required keys → `ObservationError`.

- [x] Step 1: Write tests: schema round-trip; missing `variant_id` raises; unknown key warns but loads; `final_output_sha256` computed via `compute_sha256(text)` helper; axes is a `dict[str, str]`.
- [x] Step 2: Run pytest → fail.
- [x] Step 3: Implement `observation.py`. Use `dataclasses.asdict` + `json.dumps(indent=2)`.
- [x] Step 4: Run pytest → pass. **12/12 passed.**
- [x] Step 5: Commit `feat(parallel-ab): add observation schema + emit/validate helpers` — `51b4ef6`.

### Task 3: Single-Variant Runner

**Files:** Create: `src/superclaude/scripts/parallel_ab/runner.py`, `tests/unit/scripts/parallel_ab/test_runner.py`

**Behavior:** `async def run_variant(variant, scenario, runner_cfg, out_dir) -> Observation`. Constructs `claude -p <input> <flag> --model <m>` command, launches via `asyncio.create_subprocess_exec`, captures stdout/stderr/exit, times wall-seconds, parses token counts from `--output-format json` if available (else 0/0), computes sha256 of final output, writes `out_dir/obs-<id>.json`. On non-zero exit when `bare=True` and `oauth_fallback=True`, retries once without `--bare`.

- [x] Step 1: Write tests with `spawner` dependency injection (cleaner than `unittest.mock.patch` — see Execution Log): ok path → obs file written; non-zero exit + `bare+oauth_fallback` → retries without `--bare`; timeout → exit_status="timeout"; tool_calls counted from JSON output. Use `tmp_path` for `out_dir`.
- [x] Step 2: Run pytest → fail.
- [x] Step 3: Implement `runner.py`. Subprocess args as list (no shell); auth-fail detection via stderr keyword regex.
- [x] Step 4: Run pytest → pass. **14/14 passed.**
- [x] Step 5: Commit `feat(parallel-ab): add single-variant runner with claude -p subprocess wrap` — `94e887f`.

### Task 4: Aggregator

**Files:** Create: `src/superclaude/scripts/parallel_ab/aggregator.py`, `tests/unit/scripts/parallel_ab/test_aggregator.py`, `tests/unit/scripts/parallel_ab/fixtures/obs_a.json`, `obs_b.json`

**Behavior:** `aggregate(obs_dir: Path) -> tuple[Path, Path]` reads all `obs-*.json` in dir, sorts by `variant_id`, emits `matrix.md` (markdown table: id | exit | wall_s | input_tok | output_tok | tool_calls_summary | sha256_short | axes columns) and `decision.md` (1-paragraph: cheapest-passing variant by `(exit_status=ok, min wall_seconds, min output_tokens)` tuple, or "no clear winner" if all fail). Pure tabulation — no LLM call.

- [x] Step 1: Write tests using fixture obs JSONs: 2 variants → matrix has 2 rows; sort by id; all-fail case emits "no clear winner"; mixed pass/fail picks cheapest passing; sha256 truncated to 8 chars; axes columns dynamically derived from union of all observation `axes` keys.
- [x] Step 2: Run pytest → fail.
- [x] Step 3: Implement `aggregator.py`. Use plain f-strings for markdown — no template engine.
- [x] Step 4: Run pytest → pass. **10/10 passed.**
- [x] Step 5: Commit `feat(parallel-ab): aggregator emitting matrix.md + decision.md` — `e9027d9`.

### Task 5: Orchestrator + CLI

**Files:** Create: `src/superclaude/scripts/parallel_ab/orchestrator.py`, `src/superclaude/scripts/parallel_ab/cli.py`, `tests/unit/scripts/parallel_ab/test_orchestrator.py`. Modify: `src/superclaude/scripts/README.md` (append entry under existing list).

**Behavior:** `async def orchestrate(spec_path: Path) -> Path` loads spec, enforces `AB_MAX_PARALLEL` (default 8) — refuses if `len(variants) > limit`, applies `AB_TIMEOUT_S` to each runner via `asyncio.wait_for`, fans out runners via `asyncio.gather(return_exceptions=True)`, calls aggregator, returns `decision.md` path. Failed runners produce `obs-<id>.json` with `exit_status="error"` so aggregator handles uniformly. `cli.py` exposes `python -m superclaude.scripts.parallel_ab <variants.yaml>` w/ `--out-dir` override.

- [x] Step 1: Write tests: stub `run_variant` w/ fake coroutine returning canned observations; orchestrate emits matrix.md + decision.md; > AB_MAX_PARALLEL raises; per-variant exception produces error obs not aborts batch; CLI `--help` exits 0.
- [x] Step 2: Run pytest → fail.
- [x] Step 3: Implement `orchestrator.py` + `cli.py` + `__main__.py` (added — needed for `python -m` entry). Append README entry.
- [x] Step 4: Run pytest → pass. **9/9 passed.** Full suite: **1960 passed, 24 skipped** (baseline 1904 + 56 new). Zero regressions.
- [x] Step 5: Commit `feat(parallel-ab): orchestrator + CLI; AB_MAX_PARALLEL + AB_TIMEOUT_S envs` — `1c5efca`.

### Task 6: End-to-End Validation

**Files:** Create: `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml`, `tests/integration/test_parallel_ab_e2e.py`

**Behavior:** Author 4-variant spec for `/sc:brainstorm rate limiter for a markdown framework` (variants A/B/C/D as in design spec). E2E test gated on `AB_E2E=1` env (default skip — CI does not have `claude -p` auth), invokes `orchestrate(spec_path)`, asserts `matrix.md` + `decision.md` exist and contain 4 rows. Run manually once locally; commit generated `matrix.md` + `decision.md` for reviewers as evidence.

- [ ] Step 1: Author `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml` per spec example.
- [ ] Step 2: Write `test_parallel_ab_e2e.py` with `pytest.mark.skipif(not os.getenv("AB_E2E"), reason=...)`. Assert: 4 obs files written, matrix.md has 4 rows, decision.md non-empty.
- [ ] Step 3: Run `AB_E2E=1 uv run pytest tests/integration/test_parallel_ab_e2e.py -v` locally. Cite wall-seconds, total tokens, decision.
- [ ] Step 4: Inspect `matrix.md` manually — verify columns sane, axes populated, no malformed rows.
- [ ] Step 5: Commit `feat(parallel-ab): e2e validation against /sc:brainstorm; add experiment artifacts`. Push branch. Open PR.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Windows `claude -p` subprocess path resolution | `shutil.which("claude")` at runner init; fail loud if missing. Document in Phase 3 commit. |
| `claude -p` JSON output format unstable | Wrap parse in try/except; default token counts to 0 on parse failure (don't crash run). |
| Cost overrun in unattended runs | `AB_MAX_PARALLEL=8` hard cap; per-variant timeout via `asyncio.wait_for`. No autonomous-loop integration in v1. |
| Aggregator schema drift when axes evolve | Dynamic axes columns (union over all obs); stale axes appear as empty cells, not crash. |
| `--bare` auth fallback masks real auth bug | Log every fallback to stderr w/ variant id so user notices repeated fallbacks. |
| Test flake from real subprocess | All Phase 1-5 tests mock `asyncio.create_subprocess_exec`; only Phase 6 hits real CLI and is opt-in via env. |

## Verification Commands

```
# Per phase
uv run pytest tests/unit/scripts/parallel_ab/test_spec_loader.py -v        # P1
uv run pytest tests/unit/scripts/parallel_ab/test_observation.py -v        # P2
uv run pytest tests/unit/scripts/parallel_ab/test_runner.py -v             # P3
uv run pytest tests/unit/scripts/parallel_ab/test_aggregator.py -v         # P4
uv run pytest tests/unit/scripts/parallel_ab/test_orchestrator.py -v       # P5

# Phase 5 gate — no regressions in baseline
uv run pytest

# Phase 6 — manual, opt-in
AB_E2E=1 uv run pytest tests/integration/test_parallel_ab_e2e.py -v
```

## Out of Scope (per spec)

- Live skill mutation between iterations (separate `sc-tdd-loop-design`).
- Statistical significance — N=4..8 too small.
- UI/dashboard — markdown only.
- `Task` tool integration — `claude -p` only in v1.
- Dollar-cost accounting — bounded by parallel/timeout caps in v1.

## Execution Log

**2026-05-15 — Phases 1-5 complete** on branch `feature/parallel-ab-harness` (5 commits `32c7e6d`..`1c5efca`, not yet pushed).

| Phase | Commit | Tests |
|---|---|---|
| 1 Spec loader | `32c7e6d` | 11 |
| 2 Observation schema | `51b4ef6` | 12 |
| 3 Runner | `94e887f` | 14 |
| 4 Aggregator | `e9027d9` | 10 |
| 5 Orchestrator + CLI | `1c5efca` | 9 |
| **Total** | **5 commits** | **56** |

Full suite after Phase 5: **1960 passed, 24 skipped** (baseline 1904 + 56 new). Zero regressions.

**Deviations from plan (all simplifications, no scope expansion):**
- Task 3: used `spawner` dependency-injection parameter instead of `unittest.mock.patch` on `asyncio.create_subprocess_exec`. Cleaner test isolation, no global patching. Default `spawner=_default_spawn` preserves production path.
- Task 5: added `__main__.py` (not in original File Map) — required so `python -m superclaude.scripts.parallel_ab` resolves to `cli.main()`.
- Test count 56 vs ~25 estimated — TDD surfaced more edge cases (pure-helper tests for `_build_cmd`, `_parse_output`, `_looks_like_auth_fail`).

**Phase 6 remaining (manual — needs real `claude -p` auth, out of scope for autonomous run):**
1. Author `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml` (4 variants A/B/C/D).
2. Write `tests/integration/test_parallel_ab_e2e.py` gated on `AB_E2E=1`.
3. Run `AB_E2E=1 uv run python -m superclaude.scripts.parallel_ab docs/experiments/brainstorm-ab-2026-05-14/variants.yaml`.
4. Inspect generated `matrix.md` + `decision.md`.
5. Commit experiment artifacts. Push branch. Open PR.

## Handoff

Branch `feature/parallel-ab-harness` holds Phases 1-5, **not pushed**. Phase 6 is manual (real `claude -p`). Once Phase 6 evidence is captured, push branch + open single PR. Karpathy axes verified after each phase: every changed line traces to spec; no scope creep into `auto_improve/` or `ab_test_workflows.py`; only existing file touched is `scripts/README.md` (1-row append).
