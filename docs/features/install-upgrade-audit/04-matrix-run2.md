---
feature: install-upgrade-audit
phase: matrix
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 04. Scenario matrix, run 2 (P6)

The run-1 harness ([02 §1](./02-scenarios.md)), run against `fix/install-upgrade-audit` @ 7a43ee06, which holds the three P5 fix commits 0054ef0b, e7e72cf4 and 7a43ee06. Linux, sandbox only. The real-HOME guard was clean before and after every batch, and `~/.claude/settings.json` still matches its P0 md5. Run 1 is in [02](./02-scenarios.md) and [02a](./02a-scenarios-edge.md); the findings are in [03](./03-findings.md).

## 1. Result

| | Records | PASS | FAIL |
|---|---|---|---|
| Run 1 (master @ 1dd9622c) | 99 | 21 | 78 |
| Run 2, run-1 harness unchanged | 99 | 84 | 15 |
| Run 2, after the 5 expectation changes in §2 | 99 | **89** | **10** |

- **No regression.** No record went from PASS to FAIL. No check that passed in run 1 fails in run 2, and none that passed after P5 group 3 fails now.
- **Every remaining FAIL is an S3 finding** (C-16, C-17, C-20, C-21), which Q5 (a) sends to the backlog. §4 maps each one.
- **No new finding.** §5 lists the two open items from the P5 reports that were probed: one does not reproduce, the other is an owner decision.

## 2. Expectation changes (harness only)

The harness lives outside the repo. Its run-1 copy is kept beside it as `harness-run1/`, so each change can be diffed. Five records needed new expectations. Each change follows a fix or a ruling; none of them loosens what the record proves.

| Record | Run-1 check | Run-2 check | Why |
|---|---|---|---|
| U2, D1-stale, D1-deleted | doctor output contains the lowercase word `advisory` | doctor exits 0, prints the `Advisories (these do not fail doctor):` header, and the advisory names `drifted` / `missing` (U2 also requires `update --scope user`) | C-10, Q3 (a). The advisory tier exists, but its header reads "Advisories", which the old literal match did not catch. Observed in U2: `ℹ️  76 installed file(s) differ from this release (76 drifted): run 'superclaude update --scope user' …`, then `✅ superclaude is healthy`, exit 0. D1-deleted: `9 missing`. |
| D1-scripts-gone | after the current install, doctor exits non-zero | (1) plant the broken state **before** upgrading: `66b37a7e^` install, then delete `superclaude/scripts/`; doctor must exit non-zero and say the scripts are `gone`. (2) after the current install, no legacy registration is left and doctor is healthy | C-09, Q13 (a): the install now rewrites every legacy registration (run 1 left `skill_activator.py` and `session_init.py`, each exiting 2). So the broken state exists only before the upgrade. C-10 deviation (p5-g3): a gone script now fails the hooks check instead of being an advisory. Observed: `❌ Hooks in settings.json`, then `legacy: []`, healthy. |
| U11-d174e600-project | install exit 0; no retired registration after install | install exits 1, the advice names `update --scope project` and never `--scope user`, and the refused install leaves the registrations byte-for-byte as they were. The `update` and `uninstall` checks are unchanged | C-06, owner ruling (b): the non-force refusal stays, and its advice stays in scope. Q16 (a): refuse before writing. `update --scope project` then leaves only the shipped set (the 9 old lines were retired or legacy forms), and uninstall leaves no registration. |
| I2-user / -project / -local | one check: after uninstall, the snapshot equals the one before install, minus keeps | four checks: (a) the snapshot is unchanged outside the settings and CLAUDE files; (b) the settings *content* equals the pre-install content plus the user's post-install hook; (c) the settings file mode is unchanged; (d) the CLAUDE file bytes are unchanged | The single check could not say which finding was left. The split shows (a) and (b) pass, and only (c) C-21 (mode 0664 → 0600) and (d) C-20 (blank-line run collapsed) fail. The post-seed `echo user-inside-sc-entry` hook belongs to the user, and uninstall correctly keeps it. |

## 3. Run 1 vs run 2, per record

"Raw" means run 2 with the run-1 harness unchanged; "final" means run 2 after §2.

| Records | Run 1 | Run 2 raw → final | Explained by |
|---|---|---|---|
| U1-user, -project, -local | FAIL | PASS | C-11, Q9 (a): the user's agent and style are no longer EXTRA |
| U2 | FAIL | FAIL → PASS | C-10, Q3 (a): install prints how many files differ; doctor advisory (§2) |
| U3 | FAIL | PASS | C-11, Q9 (a); C-12, Q11 (b): the empty memory dir is removed |
| U4 | FAIL | FAIL | The Q11 (b) exclude warning now passes (C-12). Still failing: `~/.claude/.superclaude_hooks` is not reported, **C-17 (S3)** |
| U5, U7 | PASS | PASS | — |
| U6-77b5821c, U6-ec6fa7e2p | FAIL | PASS | C-09, Q13 (a): the jq blocker is removed |
| U6-19091b37 | FAIL | FAIL | **C-16 (S3)**, Q14 (b): the upgrade note is in the CHANGELOG, not in install output; `session_init` still runs twice |
| U8 | FAIL | PASS | C-08, Q10 (a): 2 agents and the process skills removed, `my-skill/` kept; C-09 |
| U9-user, U9-local | FAIL | PASS | C-10: `update` states where agent memory moves |
| U10 | FAIL | FAIL | **C-20 (S3)**: uninstall collapses the user's blank-line run. Nothing foreign deleted (passes) |
| U11-66b37a7ep-user/-project, U11-d174e600-user | FAIL | PASS | C-09, Q13 (a), including the unmarked `[experimental]` echoes |
| U11-d174e600-project | FAIL | FAIL → PASS | C-06 ruling (b) (§2); C-09 via `update` |
| X1 | FAIL | PASS | C-04, Q4 (a): `update` refuses and names the local install; `~/.claude` untouched |
| X2 | FAIL | PASS | C-05, Q4 (a): the remediation carries `--scope local` |
| X3 ×3, X4, X5 | PASS | PASS | — |
| X6 | FAIL | PASS | C-18: the replaced worktree-local block is reported |
| X7 | FAIL | PASS | C-15, Q15 (b): install and doctor name both paths; `$SB/cc` untouched |
| I1 ×3 | PASS | PASS | — |
| I2-user, -project, -local | FAIL | FAIL | **C-20, C-21 (S3)** only (§2 split) |
| I2-user-noC | FAIL | PASS | C-12, Q11 (b): no heading-only `CLAUDE.md`, `{}` settings or empty `agent-memory/` left |
| I3-user, -project, -local | FAIL | PASS | C-13, Q12 (a): the user's own `playwright` is kept |
| I3-noclaude | FAIL | PASS | C-14: refused before anything is deleted, no traceback |
| I4 | FAIL | PASS | C-19 (doctor not healthy mid-way), C-12 (leftovers) |
| D1-stale, D1-deleted | FAIL | FAIL → PASS | C-10, Q3 (a) (§2) |
| D1-scripts-gone | FAIL | FAIL → PASS | C-09 and the C-10 hooks-check failure (§2) |
| D1-duplicate | PASS | PASS | — |
| E1 ×3 install, ×3 uninstall | FAIL | PASS | C-03, C-02, Q16 (a): refused before any write or delete |
| E2-ro-file, -ro-dir, -ro-base | PASS | PASS | — |
| E2-ro-settings | FAIL | FAIL | **C-21 (S3)**: a 0444 settings file is replaced, exit 0, mode 0600 |
| E3 ×4, E3-exclude | FAIL | PASS | C-03, C-19, Q16 (a): no traceback, nothing written |
| E4-user, -project, -local | FAIL | FAIL | **C-20 (S3)**: CRLF → LF on install and uninstall |
| E5 | PASS | PASS | — |
| E6 ×36 (UTF-16, UTF-8-BOM, cp949 × install, update, uninstall, doctor × U/P/L) | 6 PASS / 30 FAIL | 36 PASS | C-01, C-02, C-03, Q16 (a): exit 1, nothing written or deleted, encoding named |

## 4. Remaining FAILs

| Record(s) | Failing check | Finding | Status |
|---|---|---|---|
| U6-19091b37 | install output does not name the `.claude/hooks/x.py` commands | C-16 (S3) | Q14 (b): CHANGELOG upgrade note only (p5-g3); backlog |
| U4 | local uninstall does not report `~/.claude/.superclaude_hooks/` | C-17 (S3) | backlog |
| U10, E4 ×3, I2 ×3 (d) | CLAUDE file normalised: CRLF → LF, blank-line runs collapsed | C-20 (S3) | fixed after v4.30.1 (`fix/install-file-fidelity`); these records should PASS at the next run |
| E2-ro-settings, I2 ×3 (c) | settings writes leave mode 0600 and replace a 0444 file with exit 0 | C-21 (S3) | fixed after v4.30.1 (same branch); E2-ro-settings now expects exit 1, nothing written, mode 0444 kept |

## 5. Open items probed

| Item (source) | Probe (sandbox) | Outcome |
|---|---|---|
| Non-UTF-8 user agents could traceback (p5-g1 §7) | A cp949 `agents/my-agent.md` at U, P and L, then `install`, `update`, `doctor`, `verify-drift`, `uninstall -y`. Then a cp949 line appended to a shipped agent at U | **Not reproduced.** No traceback, and the user's file was kept at every scope. The edited shipped agent reads as `1 drifted` in install, verify-drift and doctor. The memory scans read only shipped agent names, and both catch `UnicodeDecodeError` (install_components.py:139-143, :228-234). Closed. |
| A BOM in `info/exclude` is refused, though git accepts it (p5-g1 §1) | `printf '\xef\xbb\xbfscratch/\n' > .git/info/exclude`, then `git check-ignore -v scratch/x` (git 2.43) and `install --scope local` | **Confirmed as designed.** Git honours the BOM'd pattern line (`.git/info/exclude:1:scratch/`). Install exits 1, changes nothing and names the BOM. This is an owner decision ([04a](./04a-handoff.md)), not a defect against Q16 (a). |

## 6. Reproduce

From the audit's scratch directory:

- Full matrix: `PLAN_DIR=$PWD harness/run-matrix.sh`
- The §2 records only: `harness/run-matrix.sh U2 U11 D1 I2`

Logs are under `sandbox/p2/`:

| What | Path |
|---|---|
| Run 2 log | `p6-full-run.log` |
| §2 rerun log | `p6-adjusted-run.log` |
| Run 1 results | `results-run1/` |
| Run 2 raw results | `results-run2-raw/` |
| Run 2 final results | `results/` |
| State after P5 group 3 | `results-p5g3/` |
