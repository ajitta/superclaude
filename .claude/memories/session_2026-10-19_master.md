branch: master @9f4f1ca4 (== origin/master == stable == v4.30.2); worktree clean (untracked .hermes/, .ignore belong to other sessions; `/.hermes/` gitignored)

# Session 2026-10-19 — master (hygiene rounds, a release review, two purpose rounds, the install/upgrade audit, eight releases)

## Where it stands
- Morning (Windows session): five hygiene rounds closed — context-budget-restore, author-check-multiline, repo-hygiene, test-exclusion-lift, plus v4.29.2 and v4.29.3
- Afternoon (Hermes on the OCI VM, `superclaude` profile): review of v4.29.3 → v4.29.4; mypy clean + CI gate → v4.29.5; axis A purpose-generalization; purpose-opus → v4.29.6; Dependabot PR #23 (checkout v7, setup-python v7); axis C install-upgrade-audit → v4.30.0
- Default `uv run pytest`: 4485 passed / 3 skipped; ruff and `mypy src` clean (CI runs all three); `tests/unit/test_install_upgrade_scenarios.py` builds old installs from `tests/fixtures/legacy_installs/` (no network)
- Evidence on `purpose_before_action` (core/RULES.md), sc-full vs sc-ablate: sonnet D3a (5/12 vs 2/12), opus D5 ceiling (12/12 vs 8/12); purpose-opus D3a positive, under-powered (13/20 vs 8/20, p = 0.103); over-inference none detected (0/12, 0/10). No shipped content changed
- Axis C (`docs/features/install-upgrade-audit/`): 99-scenario matrix over fork-era installs (run 1: 21 PASS / 78 FAIL → 21 confirmed findings; run 2: 89 / 10, the 10 = S3); 17 S1/S2 + verifier V-1–V-5 fixed red-first; verifier round 1 PASS WITH FIXES (V-1 High: retired agents deleted by name — introduced in this round, caught before merge), round 2 PASS
- Owner rulings: sonnet dropped; opus follow-up round and rule-wording trial on hold; axis C Q1–Q16 all recommended; C-06 = (b); the four P5 calls kept as they are (BOM exclude refused, old Tavily kept, C-06 update pass, C-18 one-directional); C-16/C-17 held; the two C-20/C-21 residuals accepted
- Windows CI: dispatched scenario job on master 4.30.1 failed (W-2, fixture-only: mixed-separator token paths); fixed; master 9f4f1ca4 run 39218794149 green incl. Windows
- Windows install still needs `make sync-*` to 4.30.2; this VM has no content install in any scope

## What changed (merges on master, oldest first, this part)
- d56826ae review-v4.29.3 fixes → 49599e01 v4.29.4 (canary-gates 7/7)
- b50a1820 mypy-clean (`make typecheck` = `uv run mypy src`, CI gate)
- 64af5fe2 purpose-generalization → caaead0d v4.29.5
- d8167084 purpose-opus (N2, N5, N7, K3 kept as probes) → e7298b3a v4.29.6
- 136c9f64 Dependabot PR #23
- a5a3e4e6 install-upgrade-audit: input preflight (UTF-8, no BOM, JSON object) before any write; anchored CLAUDE.md import removal; `--remove-mcp` keeps foreign servers; `update` refuses an empty or other-scope base; advice carries `--scope`; retired agents/skills/hook registrations removed on shipped content only (full-history digests via `scripts/gen_shipped_names.py`); doctor advisory tier; verify-drift ignores user files; dispatch-only Windows scenario job (`gh workflow run Tests --ref <b> -f windows=true`) → eb118ae0 v4.30.0 (minor: behavior contract changes, six upgrade notes)
- W-1: a retired skill dir loses only files whose path + digest superclaude shipped (`cli/retired_skill_files.py`, generated); `gen_shipped_names.py` walks `--full-history` (merge second parents: +5 skill digests, a branch-only hook id); verifier PASS WITH FIXES, X-1–X-5 applied → fcc3bd31 v4.30.1
- 88fe9344 install-file-fidelity (Fable 5.1 high, interactive): W-2 fixture fix; C-20 CLAUDE file kept byte-for-byte (own line ending, uninstall removes only its lines); C-21 settings keep mode/indent/EOL/final newline, read-only settings/CLAUDE/`info/exclude` refused in preflight, symlinked settings written through; advice unified on `update --scope`; doctor verify-drift ~0.1–0.2 s at 42k skill files; verifier 06c PASS WITH FIXES, Y-1–Y-6 applied → 9f4f1ca4 v4.30.2

## Decisions
- Independent verification per round: separate `claude -p --model opus --effort high` runs, never self-review; reports committed under `docs/features/<slug>/`
- Install audits run only in a sandbox (HOME, CLAUDE_CONFIG_DIR, UV_CACHE_DIR, PATH redirected, stub `claude`, real-HOME guard); the real `~/.claude` is snapshotted before and compared after each stage
- A deletion in a shared dir (`agents/`, `skills/`, `output-styles/`) needs a content gate (shipped digest), never a name match
- No canary for 4.29.5 / 4.29.6 / 4.30.0 / 4.30.1 / 4.30.2 (core and hooks.json unchanged)
- Implementation rounds may run on Fable 5.1 high only in an interactive Claude Code session (tmux), never headless `claude -p` (bills usage credits); verifier stays headless opus high

## Problems hit
- gh default repo on this clone = upstream → `GH_REPO`; use `-R ajitta/superclaude` for ad-hoc gh
- The Windows job's first run failed 16 tests Linux passed: machine-path tokens substituted into JSON fixtures unescaped (`C:\…`) → JSON-escape for `.json` targets
- Status reports full of labels lost the owner mid-round — open each with one plain sentence of what is tested and which step

## Next actions
- [ ] Windows: `make sync-*` to 4.30.2 (`superclaude doctor --scope <s>` first); `scripts/install-audit-windows.ps1`; `04a-handoff.md` §1
- [ ] S3 backlog on hold: C-16, C-17 (`04a-handoff.md` §2); C-15 waits for W7
- [ ] Unpicked axes: D docs ↔ SSOT consistency (recommended next), B model-generation re-audit (at the next model)
- [ ] On hold: opus follow-up round on N2/N5; "open the file a reference points to" wording trial; `origin/fix/plain-language-structure` (unmerged WIP, kept)
- [ ] If a Windows `0xC0000409` abort ever recurs: `git revert 3e64dc82`, bisect parallel_ab under concurrent load
