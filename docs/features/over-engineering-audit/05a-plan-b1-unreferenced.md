---
status: draft
revised: 2026-10-03
---

# B1: Unreferenced files and test-only cleanup

Item specs for batch B1. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b1). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F04: tests/manual tier probe

`delete` · verdict **confirmed** · ~377 lines · owner decision: no

tests/manual/test_context_loader_tiers.py (377 lines) contains 0 `def test_` functions, so pytest collects 0 items from it, and it is a hand-run probe (`uv run python tests/manual/...`). It is also partly stale: it calls ~/.claude/superclaude/scripts/context_reset.py (no script copies exist there since the console-entry change), and asserts a 'skills installed' banner for a deleted skills layer. tests/unit/test_context_loader.py already asserts TIER_0_MAP / INSTRUCTION_MAP / _get_injection_tier and session dedup. The one thing only the manual script offers is an end-to-end per-tier token-size table.

**Changes**

- `tests/manual/test_context_loader_tiers.py` (delete): 377 lines. tests/manual/ is then empty; remove the directory (and the untracked tests/manual/__pycache__).

**Tests**

- Delete the file itself. No other test imports it. tests/unit/test_context_loader.py needs no change.

**Doc references**

- None (no doc mentions tests/manual).

**Collateral**

- pyproject testpaths=['tests'] and python_files='test_*.py' import the module at collection time (it runs hook_state_dir() at import); deleting removes that import-time side effect
- No src change; module-count trap (a) not triggered; make test-scripts unaffected

**Verify**

```bash
test ! -e tests/manual && git grep -n 'tests/manual\|test_context_loader_tiers' -- . ':!.claude/insights.jsonl*' (expect no output) && uv run pytest (exit 0, collected count unchanged) && uv run ruff check src/ tests/
```

<details><summary>Evidence</summary>

- grep -c 'def test_' tests/manual/test_context_loader_tiers.py = 0; `uv run pytest tests/manual --collect-only -q -p no:cacheprovider` -> 'collected 0 items'
- File header: 'Manual test ... Run: uv run python tests/manual/test_context_loader_tiers.py'; main() at line ~294, __main__ guard at ~376
- tests/manual/test_context_loader_tiers.py:~209 RESET = Path.home()/'.claude'/'superclaude'/'scripts'/'context_reset.py' (stale per gotcha hook-console-entry); lines 197-231 assert 'skills installed'
- tests/unit/test_context_loader.py:216-298 (tier assertions on TIER_0_MAP/INSTRUCTION_MAP/_get_injection_tier), :398, :433-444 (subprocess run of the loader), :456-527 (per-session dedup)
- Only inbound references: the file's own docstring, and two .claude/insights.jsonl(.bak) metric entries (session 'context-loader-3-tier-audit')
- Default suite collects 2719 tests on this branch (measured); the file contributes 0

</details>

## F08: todo-app/ sample output

`delete` · verdict **confirmed** · ~316 lines · owner decision: no

todo-app/ (4 files, 316 lines: app.js 107, index.html 41, storage.js 21, styles.css 147) is sample output from an empirical command test, committed in 1e67947 ('chore(examples): /sc:design and /sc:implement command output samples'). Nothing in the build, tests, installer or docs points at it; only two docs/analysis narratives mention it, and one of them calls it a side effect ('rm -rf if wrong location').

**Changes**

- `todo-app/` (delete): git rm -r todo-app (4 files).

**Tests**

- None.

**Doc references**

- docs/analysis/karpathy-*-2026-05-08.md mention it as history; leave unchanged (dated analysis records).

**Collateral**

- No Python, hook, README-count or pyproject impact. Not part of the wheel or sdist.

**Verify**

```bash
test ! -d todo-app && git grep -n 'todo-app' -- . ':!docs/analysis' ':!docs/archive' (expect no output) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- git log -- todo-app -> single commit 1e67947 (2026-05-08); same commit added docs/specs/simple-note-api-design-ajitta-2026-05-08.md, now under docs/archive/specs
- grep -rIn -i 'todo-app|todo_app|todoapp' (excluding todo-app/, caches, .git): docs/analysis/karpathy-command-impact-ajitta-2026-05-08.md:231 and docs/analysis/karpathy-empirical-test-ajitta-2026-05-08.md:231-246,282,327 only
- karpathy-empirical-test:243 'todo-app/ dropped at framework root (rm -rf if wrong location)'; :327 'Side effects landed in repo ... todo-app/ directory. Both reversible (rm)'
- No hit in tests/, evals/, Makefile, pyproject.toml, .github/, src/

</details>

## F16: .pre-commit-config.yaml

`delete` · verdict **confirmed** · ~93 lines · owner decision: no

.pre-commit-config.yaml (93 lines, added 882a0d8 on upstream history) names `.secrets.baseline`, which does not exist; pre-commit is not in the dev extra, no workflow runs it, .git/hooks holds only samples, and the string '.pre-commit-config' appears in no file anywhere (archive included). It would fail on its first detect-secrets run even if installed.

**Changes**

- `.pre-commit-config.yaml` (delete): 93 lines.

**Tests**

- None.

**Doc references**

- None.

**Collateral**

- None. CLAUDE.md's only commit-time rule is the manual `make format`; shellcheck/markdownlint/yamllint it listed were never wired.

**Verify**

```bash
test ! -e .pre-commit-config.yaml && git grep -n 'pre-commit-config' (expect no output) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- .pre-commit-config.yaml:~30 args ['--baseline', '.secrets.baseline']; `ls .secrets.baseline` -> not found
- pyproject.toml [project.optional-dependencies].dev = pytest-cov, pytest-benchmark, pytest-asyncio, scipy, black, ruff, mypy (no pre-commit)
- grep -rIn -i 'pre-commit|precommit|secrets.baseline|detect-secrets' (excluding the file itself, uv.lock, caches) -> only prose in src/superclaude/agents/python-expert.md:33 (+ .claude copy), docs/research/*, .serena memory; none reference the config
- .github/workflows/{test,quick-check}.yml run pytest + `ruff check src/ tests/` + `ruff format --check`; no pre-commit job
- ls .git/hooks (excluding *.sample) -> empty; Makefile has no pre-commit target

</details>

## F28: MANIFEST.in and setup.py

`delete` · verdict **modified** · ~44 lines · owner decision: no

Both files are inert under the hatchling backend, but MANIFEST.in is worse than claimed: 15 of its 30 path entries point at missing paths, not 5 (VERSION, CHANGELOG.md, CONTRIBUTING.md, src/superclaude/examples, plugins/superclaude, plus ten plugins/superclaude/{commands,agents,modes,mcp,mcp/configs,core,examples,hooks,scripts,skills} entries). setup.py is an 11-line `from setuptools import setup; setup()` shim and setuptools is not in build-system.requires. Sdist content is controlled by [tool.hatch.build.targets.sdist] include = src/, tests/, README.md, LICENSE, pyproject.toml.

**Changes**

- `MANIFEST.in` (delete): 33 lines.
- `setup.py` (delete): 11 lines.

**Tests**

- None reference either. test_runner_hook.py:155 keeps its own 'setup.py' string; do not touch.

**Doc references**

- None.

**Collateral**

- Build output must not change: compare `uv build` sdist and wheel file lists before and after (hatchling ignores both files)
- pip install -e . and uv tool install use the PEP 517 backend, never setup.py

**Verify**

```bash
git stash-free check: uv build --out-dir <scratchpad>/before then after the deletion and diff `tar tzf` / `unzip -l` file lists (expect identical); git grep -n 'MANIFEST.in' (expect no output); uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- pyproject.toml:2-3 requires=['hatchling'], build-backend='hatchling.build'; :73-90 [tool.hatch.build.targets.wheel/sdist]
- python read of MANIFEST.in: 30 include/recursive-include path entries, 15 do not exist (listed above)
- setup.py (11 lines) imports setuptools only
- Only references: MANIFEST.in/setup.py themselves; src/superclaude/scripts/test_runner_hook.py:155 uses the string 'setup.py' as a project-root marker for the user's projects (unrelated, keep); .gitignore:29 'MANIFEST' is a different name
- git log: both files predate the hatchling move (last touched fd8c67f 2025-11-14 and earlier)

</details>

## F35f: FUNDING.yml and .agent placeholder

`delete` · verdict **confirmed** · ~22 lines · owner decision: yes (see README)

Both files are removable. .github/FUNDING.yml (15 lines) sets `github: NomenAK`, the upstream author's sponsorship, so the fork's GitHub page shows a Sponsor button for someone else; the remaining lines are template comments. .agent/rules/claude-mem-context.md (7 lines) is a placeholder committed by the owner (b62312c, 2026-04-11). The installed claude-mem 13.29.0 does not write a project-level .agent/rules path: its Antigravity target is ~/.agents/rules/claude-mem-context.md in HOME (which holds the same placeholder text and is rewritten, mtime 2 Oct), so deleting the repo copy is not futile.

**Batch note:** B1 takes the FUNDING.yml half. The `.agent/` placeholder half waits for the owner decision in B7.

**Decision:** The .agent placeholder was committed on purpose ('Adds cross-session memory context configuration'). Google Antigravity reads workspace .agent/rules; if the owner uses Antigravity in this repo, keep or regenerate it. FUNDING.yml needs no decision.

**Changes**

- `.github/FUNDING.yml` (delete): 15 lines.
- `.agent/rules/claude-mem-context.md` (delete): 7 lines; .agent/ then becomes empty and disappears.

**Tests**

- None reference either.

**Doc references**

- None.

**Collateral**

- If a newer claude-mem or Antigravity recreates .agent/, it shows up as untracked; adding `.agent/` to .gitignore is optional and not part of this cut.

**Verify**

```bash
test ! -e .github/FUNDING.yml && test ! -e .agent && git grep -n -E 'FUNDING|claude-mem-context' -- . ':!docs/archive' ':!.serena' (expect no output) && uv run pytest (exit 0)
```

<details><summary>Evidence</summary>

- cat .github/FUNDING.yml -> 'github: NomenAK', all other keys empty template comments; git log -> c946fbd 2025-08-07 NomenAK 'Create FUNDING.yml'
- cat .agent/rules/claude-mem-context.md -> '&lt;claude-mem-context> ... No context yet. Complete your first session and context will appear here.'; tracked (git ls-files .agent); single commit b62312c by ajitta
- ~/.claude/plugins/cache/thedotmack/claude-mem/13.29.0/scripts/worker-service.cjs: grep for a project '.agent' path join and `contextPath` entries finds .github/copilot-instructions.md, .roo/rules/claude-mem-context.md, WARP.md and (HOME) ~/.agents/rules/claude-mem-context.md; no workspace '.agent/rules' target
- ~/.agents/rules/claude-mem-context.md exists with identical placeholder text
- .gitignore:112-113 ignore '.agents/' and 'agent/' but not '.agent/'

</details>

## F22: duplicated test helpers

`shrink` · verdict **confirmed** · ~54 lines · owner decision: no

The helper copies are byte-identical (hashed function bodies): parse_frontmatter x3 (test_agent_structure, test_command_structure, test_cross_references) and extract_xml_attr x4 and extract_xml_content x4 (test_agent_structure, test_command_structure, test_content_structure, test_mode_structure). They can move into one shared module imported the way tests/unit/prose_guard.py is. The different src/superclaude/hooks/inline_hooks.py:22 parse_frontmatter is a separate implementation and must not be merged.

**Changes**

- `tests/unit/md_helpers.py` (edit): CREATE this file (new, ~35 lines; name is a suggestion). Docstring in prose_guard.py's style (not a test module; single definition site for the content-test parsers). `import re`, then verbatim parse_frontmatter(text: str) -> dict[str, str], extract_xml_attr(text, tag, attr) -> str | None, extract_xml_content(text, tag) -> str | None, copied from test_agent_structure.py:65-89.
- `tests/unit/test_agent_structure.py` (edit): Delete lines 65-89 plus the two trailing blank lines (the three helpers). Add `from tests.unit.md_helpers import extract_xml_attr, extract_xml_content, parse_frontmatter` after the third-party imports (import pytest / import yaml block), as its own first-party block; keep `import re` and `import yaml`.
- `tests/unit/test_command_structure.py` (edit): Delete lines 57-81 plus trailing blank lines; add the same three-name import.
- `tests/unit/test_cross_references.py` (edit): Delete lines 48-58 plus trailing blank lines; add `from tests.unit.md_helpers import parse_frontmatter`.
- `tests/unit/test_content_structure.py` (edit): Delete lines 24-35 plus trailing blank lines; add `from tests.unit.md_helpers import extract_xml_attr, extract_xml_content`.
- `tests/unit/test_mode_structure.py` (edit): Delete lines 20-31 plus trailing blank lines; add the same two-name import.

**Tests**

- No test is deleted. Parametrized collection must be unchanged: tests/unit/test_agent_structure.py, test_command_structure.py, test_cross_references.py, test_content_structure.py and test_mode_structure.py should collect exactly the same number of items as before. Record `pytest --collect-only -q <5 files> | tail -1` before the edit and compare.

**Doc references**

- None. grep for parse_frontmatter, extract_xml_attr and extract_xml_content in *.md, yml, toml and json finds nothing.

**Collateral**

- New file is under tests/, not src/superclaude/, so test_codex_component_map.py's `_PKG.rglob('*.py')` module count is unchanged.
- ruff isort ('I' rule): `tests` is first-party; run `uv run ruff check --fix tests/unit` and `uv run ruff format tests/unit` so the import blocks are ordered.
- Net size: ~95 lines removed from the five files, ~6 import lines and ~35 new-file lines added, net about -54.
- Do not touch src/superclaude/hooks/inline_hooks.py:22 or src/superclaude/scripts/token_estimator.py:47 (different behaviour, tested by test_hooks.py).

**Verify**

```bash
uv run pytest tests/unit/test_agent_structure.py tests/unit/test_command_structure.py tests/unit/test_cross_references.py tests/unit/test_content_structure.py tests/unit/test_mode_structure.py -q   # same count as before and exit 0, then uv run pytest   # exits 0. grep -nE '^def (parse_frontmatter|extract_xml_attr|extract_xml_content)' tests/unit/*.py shows only tests/unit/md_helpers.py. uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/   # exit 0.
```

<details><summary>Evidence</summary>

- Hash of each function body, normalised: parse_frontmatter 32be5595 in all 3 files; extract_xml_attr b79b7387 in all 4; extract_xml_content 6b396226 in all 4.
- Definitions: test_agent_structure.py:65-75, 78-82, 85-89; test_command_structure.py:57-67, 70-74, 77-81; test_cross_references.py:48-58 (parse_frontmatter only); test_content_structure.py:24-28, 31-35 (xml only); test_mode_structure.py:20-24, 27-31 (xml only).
- Usage counts (including the def) are: agent 3/3/10, command 2/3/4, cross_references 2/0/0, content 0/3/5, mode 0/3/8, in the order parse_frontmatter / extract_xml_attr / extract_xml_content. Content and mode files do not use parse_frontmatter, so they import only the xml helpers.
- grep for `from tests.unit.test_` or `import test_(agent|command|cross|content|mode)` finds no other module importing these helpers. grep -rE 'def \w*(frontmatter|xml_attr|xml_content)' in tests/ finds only these copies plus unrelated test names in test_hooks.py.
- Import mechanism has precedent: tests/__init__.py and tests/unit/__init__.py exist and test_cli_context.py:31 does `from tests.unit.prose_guard import prose_units`. prose_guard.py is not collected because python_files is test_*.py.
- `re` is still used elsewhere in all five files after the helpers go (20/16/4/12/7 other `re.` uses).

</details>

## F35j: rules_schemas fixture

`delete` · verdict **confirmed** · ~16 lines · owner decision: no

The rules_schemas fixture in tests/conftest.py has one consumer: test_conftest_fixture_rules_schemas_loads in tests/unit/test_rules_schemas.py, which only checks that the fixture itself loads. Every other module that needs .claude/rules/schemas.yaml loads it directly. Delete the fixture, the test and the two imports that become unused.

**Changes**

- `tests/conftest.py` (edit): Delete lines 11-18 (the `@pytest.fixture(scope="session") def rules_schemas()` block plus its trailing blank), and the now-unused `from pathlib import Path` (5, with its blank) and `import yaml` (8). Keep `import pytest` and sandbox_home (19-57).
- `tests/unit/test_rules_schemas.py` (edit): Delete lines 49-53 (the blank before it and `test_conftest_fixture_rules_schemas_loads`). `Path` and `yaml` imports stay; they are used by SCHEMAS_PATH and _load().

**Tests**

- tests/unit/test_rules_schemas.py::test_conftest_fixture_rules_schemas_loads: delete. Suite goes from 2719 to 2718 collected tests; no doc pins the count (test_docs_do_not_hardcode_a_pass_count).

**Doc references**

- None. docs/codex/prompting_session_raw/05_quality_gate_catalog.md:50 runs `pytest tests/unit/test_rules_schemas.py -v`, which still works.

**Collateral**

- No .py under src/ added or removed; module-count and README-count traps do not fire.
- The sandbox_home autouse fixture in conftest.py is unrelated and untouched.

**Verify**

```bash
grep -rn rules_schemas tests   # no output (the file name test_rules_schemas.py will not match because the grep is for the exact word within code; only conftest-fixture hits matter). uv run ruff check src/ tests/   # exit 0, no F401 in conftest.py. uv run pytest tests/unit/test_rules_schemas.py tests/unit/test_agent_structure.py tests/unit/test_command_structure.py -q   # green. uv run pytest   # exits 0, 2718 collected.
```

<details><summary>Evidence</summary>

- grep -rn rules_schemas over py, md, toml, yml and json: tests/conftest.py:12 (definition), tests/unit/test_rules_schemas.py:50-53 (the only use), and docs/codex/prompting_session_raw/05_quality_gate_catalog.md:50 which names the file test_rules_schemas.py, not the fixture.
- tests/unit/test_rules_schemas.py:7-9 and 21-23 already define SCHEMAS_PATH and _load() and the other three tests (26-47) use them; the removed test asserts the same three top-level keys that test_schemas_yaml_exists_and_parses (30-31) already checks.
- Other consumers load the file themselves: tests/unit/test_agent_structure.py:26-31 (_SCHEMAS_PATH, agent_colors, effort_values) and tests/unit/test_command_structure.py:17-21 (forbidden_command_fields). No test requests the fixture by name.
- In tests/conftest.py, `Path` (line 5) and `yaml` (line 8) are used only inside the fixture; `pytest` stays for the sandbox_home fixture (line 19).

</details>
