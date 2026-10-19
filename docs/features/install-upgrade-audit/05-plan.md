---
feature: install-upgrade-audit
status: implementing
revised: 2026-10-19
---

# Axis C: install / upgrade path audit, plan v2

## Owner summary

- **Question:** does a real user's upgrade (old install, then the current CLI) and a later uninstall end in the state code and README promise, at every scope, without touching user content?
- **Seen already:** stale content reported "healthy" (T1). `update` creating another scope (T4). Uninstall claiming success with 14 hooks left (T5). A UTF-16 settings.json makes uninstall delete all content and then crash (T6). Retired skills, agents and hook registrations kept forever (R1).
- **Fixtures:** about 10 era states, captured once from real old installs. Exact bytes for agents, SKILL.md, settings, CLAUDE and exclude files; sha256 stubs for the rest. No network or git history in CI. A shipped-names history built from full `git log` guards the next retirement.
- **Phases:** P0 harness, P1 inventory, P2 matrix, P3 review, P4 triage, P5 fixes, P6 rerun, P7 verify, P8 Windows (owner), P9 release. About 20–27 h. **Headless sessions: 1**, the P7 opus diff verifier (2 if it blocks once). Everything else: 0.
- **Decide:** Q3 doctor advisory, Q4 `update` refuses at an empty scope, Q11 uninstall leftovers, Q13 retired hooks, Q15 `CLAUDE_CONFIG_DIR`, Q16 encoding preflight, Q2 manual Windows job. The other Qs confirm v1.

Base: `master` @ 1dd9622c (v4.29.6). Planning only; no tracked file edited. Sandbox runs are under `$PLAN_DIR/sandbox/`, with `HOME`, `CLAUDE_CONFIG_DIR`, `UV_CACHE_DIR` and `PATH` set on every command [v2: P-10]. The axes are correctness axes; the over-engineering audit covered deletability.

**Grounding (sandbox, 0.6–3 s per run):**

| Trial | Source | Result with the current CLI |
|---|---|---|
| T1 | `v4.20.1` user + customizations | Non-force install: 5 pruned, **76 stale, doctor "healthy"**. `update` clean, but `my-agent.md: EXTRA` → verify-drift exits 1 for good. Uninstall leaves empty `agent-memory/`. |
| T2 | `19575ac4^` local | 14 legacy commands rewritten, `scripts/` kept with a notice; doctor "healthy" with 75 stale; uninstall leaves `agent-memory-local/`, drops its exclude |
| T3 | cp949 `~/.claude/CLAUDE.md` | install → `UnicodeDecodeError` (install_settings.py:597) after content and hooks were written |
| T4 | local only, then `update` | **Full user-scope install created in `~/.claude`** |
| T5 | settings.json with trailing commas | `uninstall -y`: "✅ No hooks", exit 0; **14 hooks remain** |
| T6 [v2: P-6] | user install, settings.json → UTF-16 | doctor, update, uninstall: traceback, exit 1. **Uninstall had already deleted all content**, leaving `CLAUDE.md` with a dangling import, `agent-memory/`, 14 hooks. Reviewer: install tracebacks after 82 files; UTF-8-BOM → "82 installed, 1 failed". |
| R1 [v2: P-1, P-7] | reviewer, `b933fd65^` user | Non-force keeps 11 process skills, `pm-agent.md`, `deep-research-agent.md` and the jq blocker beside `destructive_guard`; `skills 14/14 OK`, doctor "healthy". After uninstall, `using-superclaude` and both agents remain. |

All are hypotheses until §4 verification.

**Split for the size target** (`RULES_DOCS.md` Size), as §5 prescribes: §1–§3 in [05a-plan-matrix.md](./05a-plan-matrix.md), §4–§5 in [05b-plan-review-fixes.md](./05b-plan-review-fixes.md); §6–§8 and the review dispositions stay here. Text is plan v2 verbatim; owner decisions: [00-intent.md](./00-intent.md).

## Progress

- [x] P0 Harness — [02-scenarios.md](./02-scenarios.md) §1
- [x] P1 Inventory — [01-inventory.md](./01-inventory.md), [01a-inventory-history.md](./01a-inventory-history.md)
- [x] P2 Matrix 1 — [02-scenarios.md](./02-scenarios.md), [02a-scenarios-edge.md](./02a-scenarios-edge.md)
- [x] P3 Review — [03a-findings-review.md](./03a-findings-review.md)
- [x] P4 Triage — [03-findings.md](./03-findings.md)
- [ ] P5 Fixes
- [ ] P6 Matrix 2
- [ ] P7 Verify
- [ ] P8 Windows (owner)
- [ ] P9 Release

## 6. Phases

| Phase | Work | Effort | Headless |
|---|---|---|---|
| P0 Harness | `old-install.sh` (extract, scope check), `seed-C.sh`, `snap.py`, `run-matrix.sh`, `$SB/bin`, real-HOME guard, stub `claude` | 2 h | 0 |
| P1 Inventory | finish §1; c8e64bac era; generator source dirs; Q1 upstream check | 1.5 h | 0 |
| P2 Matrix 1 | run §3, record, capture fixtures | 2 h | 0 |
| P3 Review | A1–A6; optional 3 read-only in-session subagents (A1+A5, A2+A3, A4+A6); every cited line re-read (`context-leak`) | 3–4 h | 0 |
| P4 Triage | `03-findings.md`; owner checkpoint on a new S1 needing a decision | 0.5 h | 0 |
| P5 Fixes | fixture → red → fix → green; expect 12–16 findings | 9–13 h | 0 |
| P6 Matrix 2 | rerun; explain each changed expectation | 0.5 h | 0 |
| P7 Verify | full suite, lint, format, typecheck; then `claude -p --model opus --effort high` on `git diff master...` with plan and findings as spec, run outside the repo (`probe-observer-effect`); answer every point | 1 h | **1** (2 on rerun) |
| P8 Windows | owner: W1–W7, the PowerShell script, the Q2 job once | owner 45 min | 0 |
| P9 Release | one-command merge (`merge-without-uv-run`) → master green → bump → `make release` | 0.5 h | 0 |

Total ≈ 20–27 h. [v2: P-8] The P7 verifier is the owner's stated practice (round brief). Fallback without a billed run: the in-session read-only `independent-reviewer` subagent.

## 7. Decisions for the owner

1. **Q1 Source versions.** (a) Fork era: v4.29.5, v4.20.1, the untagged boundaries in §3, and v4.1.9 as root (checked only for "deletes nothing foreign"); (b) plus upstream `setup/` migration; (c) tags only. **Recommended: (a)**: the legacy paths live in untagged eras (T2, R1, U11) [v2: P-11].
2. **Q2 Windows.** (a) Synthetic inputs (E4–E6) + owner checklist; (b) Linux only; (c) a Windows job on every PR; (d) (a) plus a `workflow_dispatch`-only `windows-latest` job running only the scenario module. **Recommended: (d)** [v2: P-8]: the repo is public (minutes are free), and the module has no network or asyncio. It catches locale encodings and path forms.
3. **Q3 Stale content after non-force install** (T1). (a) Keep skip semantics; install prints "N files differ from this release — `update --scope X` refreshes them, overwriting edits"; doctor gets a new **advisory** tier ("healthy, 1 advisory", exit 0); (b) doctor fails on any drift; (c) document only. **Recommended: (a)** [v2: P-8]: deliberate edits read as drift, so (b) keeps editors red forever. Doctor is binary today (doctor.py:77).
4. **Q4 Commands that create a scope** (T4). (a) `update` refuses (exit 1) at a scope with no install and names the one found; `install --force` creating a scope prints "⚠️ no existing <scope> install — creating <path>"; remediation lines carry `--scope`; (b) warnings only; (c) status quo. **Recommended: (a)** [v2: P-8]: the recorded incident was `install --force --scope user`, which must still create, so it gets the warning; `update` never creates.
5. **Q5 Fix in round?** (a) S1/S2 now, S3 to backlog; (b) findings only; (c) all. **Recommended: (a)**: T6 is an S1, an uninstall that deletes content and leaves 14 hooks active.
6. **Q6 CI.** (a) Fixture tests in the default run; (b) plus a job building real refs; (c) none. **Recommended: (a)**: network-free; runs on every PR and at release [v2: self].
7. **Q7 Branch.** (a) `fix/install-upgrade-audit`; (b) `feature/…`; (c) `docs/…`. **Recommended: (a)**, or (c) if Q5 = (b).
8. **Q8 Release.** (a) One at round end; (b) per fix; (c) none. **Recommended: (a)**: one upgrade note, one recipe run.
9. **Q9 verify-drift EXTRA.** (a) `agents/`, `output-styles/`: EXTRA only for ever-shipped names; `skills/`: retired SC dirs reported `RETIRED` (exit 1), foreign dirs ignored; (b) foreign files informational, exit 0. **Recommended: (a)** [v2: P-8]: ends T1's permanent exit 1 and makes R1's stale skills visible.
10. **Q10 Retirement guard.** (a) Full-history names, hook ids and events, plus a test (§5); (b) a checklist item; (c) nothing. **Recommended: (a)**: agents, skills and hooks have each leaked already.
11. **Q11 Uninstall leftovers.** (a) Keep all; (b) remove a memory dir if empty, and warn when a non-empty `agent-memory-local/` loses its exclude; remove `~/.claude/CLAUDE.md` only if it holds nothing but SC's heading; keep and document `insights.pending.jsonl`; (c) remove always. **Recommended: (b)** [v2: P-7]: no user byte lost, nothing SC-made left.
12. **Q12 `--remove-mcp` vs a user's same-name server.** (a) Remove only if the command matches `MCP_SERVERS`; (b) status quo, documented. **Recommended: (a)** if I3 confirms the collision: the marker principle hooks already use.
13. **Q13 Retired SC hook registrations** [v2: P-1, P-8]. (a) A committed retired-identity list (fed by Q10); install (force or not), `update` and uninstall remove matching SC inner hooks; the two `[experimental]` echoes match by exact command; `superclaude/scripts/` untouched; (b) only `--force`/`update` remove them, and non-force lists them; (c) status quo. **Recommended: (a)**: `hook-upgrade-live-session` forbids deleting scripts a registration names; removing the registration leaves nothing dangling. Exact identities keep the no-pattern rule.
14. **Q14 The `19091b37` `.claude/hooks/x.py` era** [v2: P-3]. (a) Recognise `.claude/hooks/<sc-script>.py` by exact name; (b) unsupported, with an upgrade note naming the 3 commands to delete. **Recommended: (b)** unless P1 finds users on it: it lasted one day, and its relative path likely never resolved at user scope.
15. **Q15 `CLAUDE_CONFIG_DIR`** [v2: P-7]. (a) Honour it in `get_base_path` and the hook resolvers; (b) install and doctor warn, naming both paths, when it is set and differs; (c) document. **Recommended: (b)** now, (a) as an ADR: honouring it moves existing installs and `claude_base()`. W7 confirms Claude Code's side.
16. **Q16 Settings encoding** [v2: P-6]. (a) Preflight: every command validates settings and CLAUDE files before its first write or delete, and refuses non-UTF-8 or BOM input (exit 1, nothing changed, encoding named); BOM acceptance waits for W6; (b) read `utf-8-sig` now. **Recommended: (a)**: it closes T3, T6 and I4's partial-install half in one place.

## 8. Risks and do-not-do

- **Never touch the real `~/.claude` / `~/.claude.json`.** The runner aborts unless `$HOME` is under `$PLAN_DIR/sandbox/`; the real-HOME guard runs per batch. Only the uv cache is written outside; `~/.local/bin` stays off PATH [v2: P-10]; no `uv cache clean`.
- **Never `make sync-*`, `make deploy`, `uv sync`.** Always an explicit `--scope … </dev/null` (`sync-scope-creates`; old CLIs open the wizard).
- **No real `claude` binary**; the stub only. Keep the CWD in `$SB/proj` and diff all of `$SB` (old installers write CWD-relative paths).
- **No network or history in CI tests**; the generator needs a full clone [v2: P-4].
- **No pattern deletion** in shared dirs or settings: explicit lists, each with a foreign-neighbour test. Never delete `superclaude/scripts/`.
- Blocking claims are checked with `echo '{}' | <command>; echo $?` in the sandbox, never in a session. Windows inferred on Linux stays "synthetic".
- No re-litigating D11/D12, no ponytail deletion, no reading `*.output` files. Python-writing generators use Edit/Write or a quoted heredoc plus a planted violation (`generated-regex-escapes`). Trials stay uncommitted under `$PLAN_DIR/sandbox/`.

## Review dispositions

| P-n | Disposition | Reason (re-checked) |
|---|---|---|
| P-1 | applied | `git log -S` confirms all three; echoes match no marker (utils:304-319) |
| P-2 | applied | Gitlink in all 3 refs; `77b5821c` has no `local`; archive build verified on `ec6fa7e2^` (0.7 s) |
| P-3 | applied | hooks.json says `./scripts/`, but the installer wrote `.claude/hooks/` (reviewer's sandbox); Q14 (b) |
| P-4 | applied, corrected | Full history adopted; tags v4.1.9–v4.3.0 *do* hold the two agents, no fork-era tag does |
| P-5 | applied | Readers confirmed (install_components.py:96-99, verify_drift.py:89-91) |
| P-6 | applied, extended | Re-run: doctor, update and uninstall traceback; uninstall deletes content first (T6, S1) |
| P-7 | applied | `get_base_path`, CC docs, insight_writer.py:64, 52b5517e confirmed |
| P-8 | partly | Q2–Q4, Q9, Q13–Q16 adopted; verifier not reopened: the brief prescribes it |
| P-9 | applied | v1 was 30,058 bytes; the committed copy is split; this file stays under the guard |
| P-10 | applied | The probe walks PATH (install_paths.py:330); uv/uvx links needed (a first try failed without them) |
| P-11 | applied | v4.1.9 is an ancestor, v4.2.0/v4.3.0 are not; install_paths.py:18 and 910eabdd confirmed |
| self | applied | `test.yml` has no push trigger; v1 Q6 was wrong |
